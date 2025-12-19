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


    def register(self, session: Session, data):


        if self.repo.get_user_by_email(session, data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        new_user = User(
            email=data.email,
            full_name=data.full_name,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role=UserRole.CUSTOMER,
        )

        return self.repo.create_user(session, new_user)


    def login(self, session: Session, email: str, password: str):

        user = self.repo.get_user_by_email(session, email)

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

        # Create tokens
        access_token = create_access_token(
            sub=str(user.id),
            role=user.role.value
        )
        refresh_token = create_refresh_token(
            sub=str(user.id)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "property_id": user.property_id
            }
        }


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


    def list_users(self, session: Session):

        return self.repo.list_users(session)


    def update_profile(self, session: Session, user: User, data):
        changed = False

        if data.full_name is not None:
            user.full_name = data.full_name
            changed = True

        if data.phone is not None:
            user.phone = data.phone
            changed = True

        if not changed:
            return user

        session.add(user)
        session.commit()
        session.refresh(user)
        return user


    def get_current_user_profile(self, session: Session, user_id: int):

        user = self.repo.get_user(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
