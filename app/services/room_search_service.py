from sqlmodel import Session, select
from app.repositories.room_search_repo import RoomSearchRepository
from app.core.database import engine
from app.utils.redis_cache import make_key, cache_get, cache_set


class RoomSearchService:

    def __init__(self):
        self.repo = RoomSearchRepository()

    def search_available_rooms(self, data: dict):

        # 1️⃣ Check cache
        cache_key = make_key("room_search", data)
        cached = cache_get(cache_key)
        if cached:
            return cached

        property_id = data["property_id"]
        checkin = data["checkin"]
        checkout = data["checkout"]
        num_guests = data["num_guests"]

        with Session(engine) as session:

            # 2️⃣ Load RoomTypes của property
            room_types = self.repo.get_room_types(session, property_id)
            rt_ids = [rt.id for rt in room_types]

            # 3️⃣ Load rooms qua room_type_id (vì Room không có property_id)
            rooms = self.repo.get_rooms(session, property_id, rt_ids)

            # Map room → room_type_id
            room_map = {rt.id: [] for rt in room_types}
            for r in rooms:
                room_map[r.room_type_id].append(r)

            room_ids = [r.id for r in rooms]

            # 4️⃣ Check phòng bị trùng lịch
            overlaps = self.repo.get_overlapping_bookings(
                session, room_ids, checkin, checkout
            )
            booked_ids = {b.room_id for b in overlaps}

            result = []

            # 5️⃣ Build response
            for rt in room_types:

                if rt.max_occupancy < num_guests:
                    continue

                available_rooms = [
                    r for r in room_map[rt.id] if r.id not in booked_ids
                ]

                if not available_rooms:
                    continue

                result.append({
                    "id": rt.id,
                    "name": rt.name,
                    "price": rt.price,
                    "max_occupancy": rt.max_occupancy,
                    "room_count": len(available_rooms),
                    "available_rooms": [
                        {"room_id": r.id, "room_number": r.room_number}
                        for r in available_rooms
                    ]
                })

        # 6️⃣ Save cache
        cache_set(cache_key, result, expire_seconds=30)
        return result
