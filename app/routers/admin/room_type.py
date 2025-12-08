from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.schemas.room_type import (
    RoomTypeCreate,
    RoomTypeUpdate,
    RoomTypeRead,
)
from app.services.room_type_service import RoomTypeService
from app.utils.dependencies import (
    require_super_admin,
    require_staff,
)
from app.core.database import get_session


router = APIRouter(prefix="/admin/room-type", tags=["RoomType"])
service = RoomTypeService()


# =====================================================
# SUPER ADMIN — CREATE ROOM TYPE
# =====================================================
@router.post("", response_model=RoomTypeRead)
def create_room_type(
    data: RoomTypeCreate,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    return service.create(session, data)


# =====================================================
# SUPER ADMIN — LIST ALL ROOM TYPES
# =====================================================
@router.get("", response_model=list[RoomTypeRead])
def list_all(
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    return service.list_all(session)


# =====================================================
# STAFF — LIST ROOM TYPES IN THEIR PROPERTY
# SUPER ADMIN ALSO ALLOWED
# =====================================================
@router.get("/property/{property_id}", response_model=list[RoomTypeRead])
def list_by_property(
    property_id: int,
    staff = Depends(require_staff),
    session: Session = Depends(get_session),
):
    # Staff chỉ xem room type thuộc property họ quản lý
    if staff.role == "staff" and staff.property_id != property_id:
        raise HTTPException(403, "Not allowed for this property")

    return service.list_by_property(session, property_id)


# =====================================================
# UPDATE ROOM TYPE
# Staff chỉ update RoomType thuộc property mình
# Admin update tất cả
# =====================================================
@router.patch("/{room_type_id}", response_model=RoomTypeRead)
def update_room_type(
    room_type_id: int,
    data: RoomTypeUpdate,
    user = Depends(require_staff),   # staff & super_admin
    session: Session = Depends(get_session),
):
    obj = service.get(session, room_type_id)
    if not obj:
        raise HTTPException(404, "Room type not found")

    # Staff chỉ sửa room type của property mình
    if user.role == "staff" and user.property_id != obj.property_id:
        raise HTTPException(403, "Not allowed for this property")

    return service.update(session, room_type_id, data)


# =====================================================
# DELETE ROOM TYPE — SUPER ADMIN ONLY
# =====================================================
@router.delete("/{room_type_id}")
def delete_room_type(
    room_type_id: int,
    admin = Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    service.delete(session, room_type_id)
    return {"message": "Room type deleted"}
