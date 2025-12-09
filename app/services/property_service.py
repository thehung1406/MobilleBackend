from sqlmodel import Session
from app.repositories.property_repo import PropertyRepository
from app.repositories.room_type_repo import RoomTypeRepository
from app.repositories.room_repo import RoomRepository
from app.schemas.property_detail import PropertyDetailRead, RoomTypeWithRoomsRead, RoomRead

from app.utils.redis_cache import make_key, cache_get, cache_set


class PropertyService:

    @staticmethod
    def get_detail(session: Session, property_id: int) -> PropertyDetailRead:

        cache_key = make_key("property_detail", {"id": property_id})
        cached = cache_get(cache_key)
        if cached:
            return PropertyDetailRead(**cached)

        property_obj = PropertyRepository.get_by_id(session, property_id)
        if not property_obj:
            return None

        room_types = RoomTypeRepository.get_by_property(session, property_id)

        room_type_list = []
        for rt in room_types:
            rooms = RoomRepository.get_by_room_type(session, rt.id)
            room_type_list.append(
                RoomTypeWithRoomsRead(
                    id=rt.id,
                    name=rt.name,
                    price=rt.price,
                    max_occupancy=rt.max_occupancy,
                    is_active=rt.is_active,
                    rooms=[RoomRead.from_orm(r) for r in rooms]
                )
            )

        result = PropertyDetailRead(
            id=property_obj.id,
            name=property_obj.name,
            description=property_obj.description,
            address=property_obj.address,
            latitude=property_obj.latitude,
            longitude=property_obj.longitude,
            image=property_obj.image,
            checkin=property_obj.checkin,
            checkout=property_obj.checkout,
            contact=property_obj.contact,
            room_types=room_type_list
        )

        cache_set(cache_key, result.dict(), expire_seconds=120)
        return result
