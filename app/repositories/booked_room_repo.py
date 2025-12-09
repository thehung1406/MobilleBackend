from sqlmodel import Session
from app.models.booked_room import BookedRoom


class BookedRoomRepository:

    @staticmethod
    def create(session: Session, booking_id: int, room_id: int, checkin, checkout):
        br = BookedRoom(
            booking_id=booking_id,
            room_id=room_id,
            checkin=checkin,
            checkout=checkout
        )
        session.add(br)
        session.commit()
        session.refresh(br)
        return br
