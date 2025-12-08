from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas.amenity import AmenityCreate, AmenityUpdate, AmenityRead
from app.services.amenity_service import AmenityService
from app.utils.dependencies import require_super_admin, get_session

router = APIRouter(prefix="/admin/amenity", tags=["Amenity"])

service = AmenityService()


@router.post("", response_model=AmenityRead)
def create(data: AmenityCreate, admin=Depends(require_super_admin), session: Session = Depends(get_session)):
    return service.create(session, data)


@router.get("", response_model=list[AmenityRead])
def list_all(admin=Depends(require_super_admin), session: Session = Depends(get_session)):
    return service.list(session)


@router.patch("/{amenity_id}", response_model=AmenityRead)
def update(
    amenity_id: int,
    data: AmenityUpdate,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    return service.update(session, amenity_id, data)


@router.delete("/{amenity_id}")
def delete(
    amenity_id: int,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    service.delete(session, amenity_id)
    return {"message": "Amenity deleted"}
