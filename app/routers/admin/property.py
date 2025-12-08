from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyRead
from app.services.property_service import PropertyService
from app.core.database import get_session
from app.utils.dependencies import (
    require_super_admin,
)

router = APIRouter(prefix="/property", tags=["Property"])

service = PropertyService()


# ============================================================
# PUBLIC API — khách, user, ai cũng xem được
# ============================================================
@router.get("", response_model=list[PropertyRead])
def list_public_properties(
    session: Session = Depends(get_session)
):
    """Public listing — hiển thị danh sách khách sạn trên app."""
    return service.list_properties(session)


@router.get("/{prop_id}", response_model=PropertyRead)
def get_property_public(
    prop_id: int,
    session: Session = Depends(get_session)
):
    """Public detail — xem thông tin chi tiết khách sạn."""
    prop = service.get_property(session, prop_id)
    return prop


# ============================================================
# ADMIN API — SUPER ADMIN ONLY
# ============================================================

@router.post("/admin", response_model=PropertyRead)
def create_property(
    payload: PropertyCreate,
    admin = Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    return service.create_property(session, payload)


@router.get("/admin", response_model=list[PropertyRead])
def list_properties_admin(
    admin = Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    return service.list_properties(session)


@router.get("/admin/{prop_id}", response_model=PropertyRead)
def get_property_admin(
    prop_id: int,
    admin = Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    return service.get_property(session, prop_id)


@router.patch("/admin/{prop_id}", response_model=PropertyRead)
def update_property(
    prop_id: int,
    payload: PropertyUpdate,
    admin = Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    return service.update_property(session, prop_id, payload)


@router.delete("/admin/{prop_id}")
def delete_property(
    prop_id: int,
    admin = Depends(require_super_admin),
    session: Session = Depends(get_session)
):
    service.delete_property(session, prop_id)
    return {"message": "Property deleted"}
