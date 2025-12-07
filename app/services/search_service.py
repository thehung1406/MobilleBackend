from sqlmodel import Session
from app.repositories.search_repo import SearchRepository
from app.core.database import engine
from app.utils.redis_cache import make_key, cache_get, cache_set


class SearchService:

    def __init__(self):
        self.repo = SearchRepository()

    def search_available_rooms(self, data: dict):

        # ---------------------------------------
        # 1. Kiểm tra cache
        # ---------------------------------------
        cache_key = make_key("search", data)
        cached = cache_get(cache_key)
        if cached:
            return cached

        property_id = data["property_id"]
        checkin = data["checkin"]
        checkout = data["checkout"]
        num_guests = data["num_guests"]
        min_price = data.get("min_price")
        max_price = data.get("max_price")
        requested_amenities = set(data.get("amenities") or [])

        with Session(engine) as session:

            # ---------------------------------------
            # 2. Load dữ liệu trong DB
            # ---------------------------------------
            room_types = self.repo.get_room_types(session, property_id)
            rooms = self.repo.get_rooms_by_property(session, property_id)

            room_map = {rt.id: [] for rt in room_types}
            for r in rooms:
                room_map[r.room_type_id].append(r)

            room_ids = [r.id for r in rooms]

            overlaps = self.repo.get_overlapping_bookings(
                session, room_ids, checkin, checkout
            )
            booked_ids = {b.room_id for b in overlaps}

            property_amenities = self.repo.get_property_amenities(session, property_id)

            # ---------------------------------------
            # 3. Build response
            # ---------------------------------------
            result = []

            for rt in room_types:

                # --- Filter theo occupancy ---
                if rt.max_occupancy < num_guests:
                    continue

                # --- Filter theo giá ---
                if min_price and rt.price < min_price:
                    continue
                if max_price and rt.price > max_price:
                    continue

                # --- Filter theo amenities ---
                if requested_amenities:
                    if not requested_amenities.issubset(property_amenities):
                        continue

                # --- Lấy danh sách phòng còn trống ---
                available_rooms = [
                    r for r in room_map[rt.id] if r.id not in booked_ids
                ]
                room_count = len(available_rooms)

                if room_count == 0:
                    continue

                result.append({
                    "id": rt.id,
                    "name": rt.name,
                    "price": rt.price,
                    "max_occupancy": rt.max_occupancy,
                    "room_count": room_count,
                    "available_rooms": [
                        {"room_id": r.id, "room_number": r.room_number}
                        for r in available_rooms
                    ]
                })

        # ---------------------------------------
        # 4. Lưu cache
        # ---------------------------------------
        cache_set(cache_key, result, expire_seconds=30)

        return result
