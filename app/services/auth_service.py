# app/services/auth_service.py
from sqlmodel import Session
from app.repositories.auth_repo import AuthRepository
from app.models.user import User
from app.utils.enums import UserRole
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token


class AuthService:

    def __init__(self):
        self.repo = AuthRepository()

    # REGISTER CUSTOMER
    def register(self, session: Session, data):
        if self.repo.get_user_by_email(session, data.email):
            raise ValueError("Email already exists")

        user = User(
            email=data.email,
            full_name=data.full_name,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role=UserRole.CUSTOMER,
        )

        return self.repo.create_user(session, user)

    # LOGIN
    def login(self, session: Session, data):
        user = self.repo.get_user_by_email(session, data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise ValueError("Invalid credentials")

        access = create_access_token(user.id, user.role.value)
        refresh = create_refresh_token(user.id)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "user": user,
        }

    # CREATE STAFF (SUPER ADMIN)
    def create_staff(self, session: Session, data):
        if self.repo.get_user_by_email(session, data.email):
            raise ValueError("Email already exists")

        staff = User(
            email=data.email,
            full_name=data.full_name,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role=UserRole.STAFF,
            property_id=data.property_id,
        )

        return self.repo.create_user(session, staff)

    # LIST ALL USERS (SUPER ADMIN)
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

    # DELETE USER
    def delete_user(self, session: Session, user_id):
        user = self.repo.get_user(session, user_id)
        if not user:
            raise ValueError("User not found")

        self.repo.delete_user(session, user)
