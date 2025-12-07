from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from app.core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(pw: str) -> str:
    return pwd_ctx.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return pwd_ctx.verify(pw, hashed)

def create_token(sub: str, scope: str, expires_delta: timedelta) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": sub,
        "scope": scope,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(sub: str, role: str) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": sub,
        "role": role,
        "scope": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(sub: str) -> str:
    return create_token(sub, "refresh", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
