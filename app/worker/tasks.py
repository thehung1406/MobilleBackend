from sqlmodel import Session, select
from datetime import datetime

from app.core.database import engine
from app.models.booking import Booking
from app.utils.lock import release_room_lock
from app.worker.celery_app import celery_app


@celery_app.task(name="cleanup_expired_bookings")
def cleanup_expired_bookings():
    with Session(engine) as session:
        now = datetime.utcnow()

        stmt = select(Booking).where(
            Booking.status == "pending",
            Booking.expires_at < now
        )

        expired_list = session.exec(stmt).all()

        for b in expired_list:
            # 🔑 FIX: selected_rooms có thể = None
            rooms = b.selected_rooms or []

            for rid in rooms:
                release_room_lock(rid, b.checkin, b.checkout)

            b.status = "cancelled"
            session.add(b)

        session.commit()

    return f"Cancelled {len(expired_list)} expired bookings"
