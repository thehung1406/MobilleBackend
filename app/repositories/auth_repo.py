# app/repositories/auth_repo.py
from sqlmodel import Session, select
from app.models.user import User


class AuthRepository:

    def get_user_by_email(self, session: Session, email: str):
        stmt = select(User).where(User.email == email)
        return session.exec(stmt).first()

    def create_user(self, session: Session, user: User):
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def get_user(self, session: Session, user_id: int):
        return session.get(User, user_id)

    def list_users(self, session: Session):
        stmt = select(User)
        return session.exec(stmt).all()

    def delete_user(self, session: Session, user: User):
        session.delete(user)
        session.commit()
