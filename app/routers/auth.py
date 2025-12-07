# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.schemas.auth import (
    SignupRequest, LoginRequest, StaffCreate, UserUpdate, UserRead
)
from app.services.auth_service import AuthService
from app.utils.dependencies import (
    get_current_user, require_super_admin, require_customer
)
from app.core.database import get_session

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()


@router.post("/register", response_model=UserRead)
def register(payload: SignupRequest, session: Session = Depends(get_session)):
    try:
        return auth_service.register(session, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    try:
        return auth_service.login(session, payload)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/create-staff", response_model=UserRead)
def create_staff(
    payload: StaffCreate,
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    return auth_service.create_staff(session, payload)


@router.get("/users", response_model=list[UserRead])
def list_users(
    admin=Depends(require_super_admin),
    session: Session = Depends(get_session),
):
    return auth_service.list_users(session)


@router.patch("/profile", response_model=UserRead)
def update_profile(
    data: UserUpdate,
    user=Depends(get_current_user),   # FIX
    session: Session = Depends(get_session),
):
    return auth_service.update_profile(session, user, data)

