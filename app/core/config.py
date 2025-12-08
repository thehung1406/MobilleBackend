from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    SECRET_KEY: str
    ALGORITHM: str

    DATABASE_URL: str
    REDIS_URL: str  # bạn vẫn giữ lại để dùng cho Celery nếu cần

    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    CORS_ORIGINS: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    FRONTEND_URL: str

    # ⭐ THÊM (bắt buộc cho Redis Cache)
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
