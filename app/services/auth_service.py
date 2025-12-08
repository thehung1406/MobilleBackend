from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.repositories.auth_repo import AuthRepository
from app.models.user import User
from app.utils.enums import UserRole
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)


class AuthService:

    def __init__(self):
        self.repo = AuthRepository()

    # REGISTER
    def register(self, session: Session, data):
        if self.repo.get_user_by_email(session, data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        user = User(
            email=data.email,
            full_name=data.full_name,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role=UserRole.CUSTOMER,
        )

        return self.repo.create_user(session, user)

    # LOGIN
    def login(self, session: Session, email: str, password: str):

        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not found"
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )

        access_token = create_access_token(sub=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(sub=str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
            }
        }

    # CREATE STAFF
    def create_staff(self, session: Session, data):
        if self.repo.get_user_by_email(session, data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        staff = User(
            email=data.email,
            full_name=data.full_name,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role=UserRole.STAFF,
            property_id=data.property_id
        )

        return self.repo.create_user(session, staff)

    # LIST USERS
    def list_users(self, session: Session):
        return self.repo.list_users(session)

    # UPDATE PROFILE
    def update_profile(self, session: Session, user: User, data):
        if data.full_name:
            user.full_name = data.full_name
        if data.phone:
            user.phone = data.phone

        session.add(user)
        session.commit()
        session.refresh(user)
        return user
