from sqlmodel import Session, select
from app.models.room import Room
from app.models.room_type import RoomType
from app.models.property_amenity import PropertyAmenity
from app.models.booked_room import BookedRoom


class SearchRepository:

    # ---------------- ROOM TYPES ----------------
    def get_room_types(self, session: Session, property_id: int):
        stmt = (
            select(RoomType)
            .where(RoomType.property_id == property_id)
            .where(RoomType.is_active == True)
        )
        return session.exec(stmt).all()

    # ---------------- ROOMS ----------------
    def get_rooms_by_property(self, session: Session, property_id: int):
        stmt = (
            select(Room)
            .where(Room.property_id == property_id)
            .where(Room.is_active == True)
        )
        return session.exec(stmt).all()

    # ---------------- BOOKED OVERLAP ----------------
    def get_overlapping_bookings(self, session: Session, room_ids, checkin, checkout):
        stmt = (
            select(BookedRoom)
            .where(BookedRoom.room_id.in_(room_ids))
            .where(BookedRoom.checkin < checkout)
            .where(BookedRoom.checkout > checkin)
        )
        return session.exec(stmt).all()

    # ---------------- AMENITIES ----------------
    def get_property_amenities(self, session: Session, property_id: int):
        stmt = (
            select(PropertyAmenity.amenity_id)
            .where(PropertyAmenity.property_id == property_id)
        )
        return {row[0] for row in session.exec(stmt).all()}  # return set
