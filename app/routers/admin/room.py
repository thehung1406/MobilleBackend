from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.models.room_type import RoomType
from app.schemas.room import RoomCreate, RoomUpdate, RoomRead
from app.services.room_service import RoomService
from app.utils.dependencies import (
    get_session,
    require_super_admin,
    require_staff
)

router = APIRouter(prefix="/admin/room", tags=["Admin Room"])

service = RoomService()


# ============================================================
# CREATE ROOM — SuperAdmin + Staff
# ============================================================
@router.post("", response_model=RoomRead)
def create_room(
    data: RoomCreate,
    user = Depends(require_staff),
    session: Session = Depends(get_session)
):
    """
    Staff chỉ được tạo room trong property họ quản lý
    nhưng Room không chứa property_id -> validate qua room_type.property_id
    """
    # Lấy property_id từ room_type
    room_type = session.get(RoomType, data.room_type_id)
    if not room_type:
        raise HTTPException(404, "RoomType not found")

    # Staff không được tạo room của property khác
    if user.role == "staff" and user.property_id != room_type.property_id:
        raise HTTPException(403, "Not allowed for this property")

    return service.create(session, data)


# ============================================================
# LIST ALL ROOMS — SuperAdmin Only
# ============================================================
@router.get("", response_model=list[RoomRead])
def list_all_rooms(
    admin = Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    return service.list_all(session)


# ============================================================
# LIST ROOMS BY PROPERTY — Staff only for their property
# ============================================================
@router.get("/property/{property_id}", response_model=list[RoomRead])
def list_by_property(
    property_id: int,
    user = Depends(require_staff),
    session: Session = Depends(get_session)
):
    # Staff chỉ được xem room của property họ quản lý
    if user.role == "staff" and user.property_id != property_id:
        raise HTTPException(403, "Not allowed")

    return service.list_by_property(session, property_id)


# ============================================================
# UPDATE ROOM — Staff only owns property
# ============================================================
@router.patch("/{room_id}", response_model=RoomRead)
def update_room(
    room_id: int,
    data: RoomUpdate,
    user = Depends(require_staff),
    session: Session = Depends(get_session)
):
    room = service.get(session, room_id)
    if not room:
        raise HTTPException(404, "Room not found")

    # Dùng room.room_type.property_id để kiểm tra quyền
    if user.role == "staff" and user.property_id != room.room_type.property_id:
        raise HTTPException(403, "Not allowed for this property")

    return service.update(session, room_id, data)


# ============================================================
# DELETE ROOM — SuperAdmin Only
# ============================================================
@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    admin = Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    service.delete(session, room_id)
    return {"message": "Room deleted"}
