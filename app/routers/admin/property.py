from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyRead
from app.services.property_service import PropertyService
from app.core.database import get_session
from app.utils.dependencies import (
    require_super_admin,
    get_current_user,
)

router = APIRouter(prefix="/property", tags=["Property"])

service = PropertyService()

# ============================================================
# ✅ PUBLIC API — ai cũng xem được chi tiết của 1 property
# Mobile App sẽ dùng API này để hiển thị:
#   - Tên khách sạn
#   - Ảnh đại diện
#   - Địa chỉ + province
#   - Kinh độ / Vĩ độ
#   - Giờ checkin / checkout
#   - Room types sẽ lấy từ API khác
# ============================================================

@router.get("/{prop_id}", response_model=PropertyRead)
def get_property_public(
    prop_id: int,
    session: Session = Depends(get_session)
):
    prop = service.get_property(session, prop_id)
    return prop


# ============================================================
# ADMIN API — SUPER ADMIN ONLY
# prefix đặt /admin cho đúng chuẩn phân quyền
# ============================================================

admin_router = APIRouter(prefix="/admin/property", tags=["Admin Property"])


@admin_router.post("", response_model=PropertyRead)
def create_property(
    payload: PropertyCreate,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    return service.create_property(session, payload)


@admin_router.get("", response_model=list[PropertyRead])
def list_properties(
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    return service.list_properties(session)


@admin_router.get("/{prop_id}", response_model=PropertyRead)
def get_property_admin(
    prop_id: int,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    return service.get_property(session, prop_id)


@admin_router.patch("/{prop_id}", response_model=PropertyRead)
def update_property(
    prop_id: int,
    payload: PropertyUpdate,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    return service.update_property(session, prop_id, payload)


@admin_router.delete("/{prop_id}")
def delete_property(
    prop_id: int,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    service.delete_property(session, prop_id)
    return {"message": "Property deleted"}
