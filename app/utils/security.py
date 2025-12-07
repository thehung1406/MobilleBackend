from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

from app.core.config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------------------------------------
# PASSWORD HASH / VERIFY
# -------------------------------------
def hash_password(password: str):
    return pwd.hash(password)


def verify_password(password: str, hashed: str):
    return pwd.verify(password, hashed)


# -------------------------------------
# TOKEN GENERATION
# -------------------------------------
def create_access_token(sub: str, role: str):
    now = datetime.utcnow()
    payload = {
        "sub": sub,
        "role": role,
        "scope": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(sub: str):
    now = datetime.utcnow()
    payload = {
        "sub": sub,
        "scope": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
