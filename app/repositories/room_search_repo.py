from sqlmodel import Session, select
from app.models.room_type import RoomType
from app.models.room import Room
from app.models.booked_room import BookedRoom
from app.models.property_amenity import PropertyAmenity


class RoomSearchRepository:

    def get_room_types(self, session: Session, property_id: int):
        return session.exec(
            select(RoomType).where(RoomType.property_id == property_id)
        ).all()

    def get_rooms(self, session: Session, property_id: int, rt_ids: list):
        return session.exec(
            select(Room).where(Room.room_type_id.in_(rt_ids))
        ).all()

    def get_overlapping_bookings(self, session: Session, room_ids, checkin, checkout):
        return session.exec(
            select(BookedRoom)
            .where(BookedRoom.room_id.in_(room_ids))
            .where(BookedRoom.checkin < checkout)
            .where(BookedRoom.checkout > checkin)
        ).all()

    def get_property_amenities(self, session: Session, property_id: int):
        rows = session.exec(
            select(PropertyAmenity.amenity_id)
            .where(PropertyAmenity.property_id == property_id)
        ).all()
        return {r[0] for r in rows}

