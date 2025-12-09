from sqlmodel import Session, select
from datetime import datetime
from app.core.database import engine
from app.models.booking import Booking

from app.worker.celery_app import celery_app


@celery_app.task
def cleanup_expired_bookings():

    with Session(engine) as session:
        now = datetime.utcnow()

        stmt = select(Booking).where(
            (Booking.status == "pending") &
            (Booking.expires_at < now)
        )
        expired = session.exec(stmt).all()

        for b in expired:
            b.status = "cancelled"
            session.add(b)

        session.commit()

    return f"Cancelled {len(expired)} expired bookings"
