# app/repositories/auth_repo.py
from sqlmodel import Session, select
from app.models.user import User


class AuthRepository:


    def get_user_by_email(self, session: Session, email: str):
        stmt = select(User).where(User.email == email)
        return session.exec(stmt).first()

    def get_user(self, session: Session, user_id: int):
        return session.get(User, user_id)


    def create_user(self, session: Session, user: User):
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


    def list_users(self, session: Session):
        stmt = select(User)
        return session.exec(stmt).all()

    def list_staff(self, session: Session):
        stmt = select(User).where(User.role == "staff")
        return session.exec(stmt).all()

    def list_customers(self, session: Session):
        stmt = select(User).where(User.role == "customer")
        return session.exec(stmt).all()


    def update_user(self, session: Session, user: User):
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


    def delete_user(self, session: Session, user: User):
        session.delete(user)
        session.commit()


    def deactivate_user(self, session: Session, user: User):
        user.is_active = False
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
