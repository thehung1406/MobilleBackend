from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.amenity import AmenityCreate, AmenityUpdate, AmenityRead
from app.services.amenity_service import AmenityService
from app.utils.dependencies import (
    get_session,
    require_super_admin,
)

router = APIRouter(prefix="/amenities", tags=["Amenities"])

service = AmenityService()

# ==========================================================
# 1. PUBLIC — ANYONE can get amenities (customer, guest)
# ==========================================================
@router.get("", response_model=list[AmenityRead])
def list_public_amenities(session: Session = Depends(get_session)):
    """
    Public API — khách hàng xem danh sách tiện ích
    (WiFi, Hồ bơi, Gym...) để hiển thị UI hoặc filter search.
    """
    return service.list(session)


# ==========================================================
# 2. ADMIN — SUPER ADMIN ONLY
# ==========================================================

@router.post("", response_model=AmenityRead)
def create_amenity(
    data: AmenityCreate,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    """
    Tạo mới amenity — chỉ dành cho SUPER ADMIN.
    """
    return service.create(session, data)


@router.get("/admin", response_model=list[AmenityRead])
def list_admin_amenities(
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    """
    Admin listing (giống public nhưng thuộc /admin để quản lý).
    """
    return service.list(session)


@router.patch("/{amenity_id}", response_model=AmenityRead)
def update_amenity(
    amenity_id: int,
    data: AmenityUpdate,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    """
    Cập nhật amenity — SUPER ADMIN ONLY.
    """
    return service.update(session, amenity_id, data)


@router.delete("/{amenity_id}")
def delete_amenity(
    amenity_id: int,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    """
    Xoá amenity — SUPER ADMIN ONLY.
    """
    service.delete(session, amenity_id)
    return {"message": "Amenity deleted"}
