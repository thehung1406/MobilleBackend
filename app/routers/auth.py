from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.schemas.auth import SignupRequest
from app.schemas.user import StaffCreate, UserUpdate, UserRead
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user, require_super_admin
from app.core.database import get_session

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()


@router.post("/register", response_model=UserRead)
def register(payload: SignupRequest, session: Session = Depends(get_session)):
    return auth_service.register(session, payload)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    return auth_service.login(
        session=session,
        email=form_data.username,
        password=form_data.password
    )


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


@router.get("/me", response_model=UserRead)
def get_current_user_profile(
    user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    return auth_service.get_current_user_profile(session, user.id)


@router.patch("/profile", response_model=UserRead)
def update_profile(
    data: UserUpdate,
    user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return auth_service.update_profile(session, user, data)