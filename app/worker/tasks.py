from celery import shared_task
from sqlmodel import Session, select
from app.worker.celery_app import celery_app
from app.core.database import engine
from app.core.lock import RedisLock
from app.services.booking_service import BookingService
from app.services.mail_service import MailService
from app.core.logger import logger
from app.models.booking import Booking

booking_service = BookingService()
mail_service = MailService()


# ============================================================================
# TASK 1 — PROCESS BOOKING
# ============================================================================
@shared_task(bind=True, max_retries=3)
def process_booking_task(self, data: dict):

    room_ids = data["room_ids"]
    locks = [RedisLock(f"room:{room_id}") for room_id in room_ids]

    try:
        # -----------------------------
        # 1. ACQUIRE ALL LOCKS
        # -----------------------------
        for lock in locks:
            if not lock.acquire():
                logger.warning("[LOCK] Failed to acquire → retry")
                raise self.retry(countdown=1)

        # -----------------------------
        # 2. IDEMPOTENCY CHECK
        # -----------------------------
        with Session(engine) as session:
            stmt = select(Booking).where(
                Booking.user_id == data["user_id"],
                Booking.status == "pending"
            )
            existing = session.exec(stmt).first()

            if existing:
                logger.info(f"[Booking] Idempotent ✓ Existing #{existing.id}")
                return existing.id

        # -----------------------------
        # 3. MAIN BOOKING LOGIC
        # -----------------------------
        booking = booking_service.process_booking(data)

        # -----------------------------
        # 4. SEND EMAIL (ASYNC)
        # -----------------------------
        send_booking_email.delay(booking.id)

        logger.info(f"[Booking] Booking #{booking.id} created successfully")
        return booking.id

    except Exception as e:
        logger.error(f"[TaskError] {e}")
        raise

    finally:
        # -----------------------------
        # 5. RELEASE LOCKS
        # -----------------------------
        for lock in locks:
            lock.release()



# ============================================================================
# TASK 2 — AUTO EXPIRE PENDING BOOKINGS
# ============================================================================
@shared_task
def expire_pending_bookings():
    with Session(engine) as session:
        expired_count = booking_service.expire_pending_bookings(session)

    logger.info(f"[Expire] {expired_count} pending bookings expired")



# ============================================================================
# TASK 3 — SEND BOOKING EMAIL
# ============================================================================
@shared_task
def send_booking_email(booking_id: int):
    try:
        mail_service.send_booking_confirmation(booking_id)
        logger.info(f"[Mail] Email sent for booking #{booking_id}")
    except Exception as e:
        logger.error(f"[MailError] {e}")
