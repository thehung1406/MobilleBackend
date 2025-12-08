from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.property_amenity import (
    PropertyAmenityCreate,
    PropertyAmenityRead,
)
from app.services.property_amenity_service import PropertyAmenityService
from app.utils.dependencies import (
    get_session,
    require_super_admin,
)

router = APIRouter(
    prefix="/admin/property-amenity",
    tags=["Admin Property Amenity"],
)

service = PropertyAmenityService()


# CREATE
@router.post("", response_model=PropertyAmenityRead)
def create_property_amenity(
    payload: PropertyAmenityCreate,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    return service.add(session, payload)


# LIST ALL OF A PROPERTY
@router.get("/property/{property_id}", response_model=list[PropertyAmenityRead])
def list_property_amenities(
    property_id: int,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    return service.list_by_property(session, property_id)


# DELETE
@router.delete("/{pa_id}")
def delete_property_amenity(
    pa_id: int,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    service.remove(session, pa_id)
    return {"message": "Property amenity deleted"}
