from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.amenity import AmenityCreate, AmenityUpdate, AmenityRead
from app.services.amenity_service import AmenityService
from app.utils.dependencies import (
    require_super_admin,
    get_session,
)

service = AmenityService()

# ============================================================
# ✅ PUBLIC API — ai cũng xem được danh sách tiện ích
# Mobile App dùng để hiển thị checkbox filter (wifi, hồ bơi,...)
# ============================================================

public_router = APIRouter(prefix="/amenity", tags=["Amenity"])

@public_router.get("", response_model=list[AmenityRead])
def public_list_amenities(session: Session = Depends(get_session)):
    return service.list(session)


# ============================================================
# ADMIN API — SUPER ADMIN ONLY
# ============================================================

admin_router = APIRouter(prefix="/admin/amenity", tags=["Admin Amenity"])

@admin_router.post("", response_model=AmenityRead)
def create_amenity(
    payload: AmenityCreate,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    return service.create(session, payload)


@admin_router.get("", response_model=list[AmenityRead])
def list_admin_amenities(
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    return service.list(session)


@admin_router.patch("/{amenity_id}", response_model=AmenityRead)
def update_amenity(
    amenity_id: int,
    payload: AmenityUpdate,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    return service.update(session, amenity_id, payload)


@admin_router.delete("/{amenity_id}")
def delete_amenity(
    amenity_id: int,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    service.delete(session, amenity_id)
    return {"message": "Amenity deleted"}
