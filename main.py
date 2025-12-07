

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import init_db, engine
from app.core.logger import logger
from app.models.user import User
from app.utils.security import hash_password
from app.utils.enums import UserRole


import app.models

from app.routers import (
    auth,

)


def create_app() -> FastAPI:

    application = FastAPI(title=settings.PROJECT_NAME)


    cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    # Add development ports if not already included
    dev_origins = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:5173"]
    for origin in dev_origins:
        if origin not in cors_origins:
            cors_origins.append(origin)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )



    @application.on_event("startup")
    def on_startup() -> None:
        """Initialize the database and seed a default superuser on startup."""
        # Create database tables. `app.models` has been imported above so all
        # tables are registered with SQLModel's metadata.
        init_db()

        # Create a default superuser if one does not already exist. Using a
        # context-managed session ensures the connection is closed properly.
        with Session(engine) as session:
            existing_user = session.exec(
                select(User).where(User.email == settings.SUPERUSER_EMAIL)
            ).first()

            if not existing_user:
                admin_user = User(
                    email=settings.SUPERUSER_EMAIL,
                    password_hash=hash_password(settings.SUPERUSER_PASSWORD),
                    full_name="Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                    phone="0123456789",
                )
                session.add(admin_user)
                session.commit()
                logger.info(
                    f"✅ Created default superuser: {settings.SUPERUSER_EMAIL}"
                )
            else:
                logger.info("✅ Superuser already exists, skip seeding.")

        logger.info("✅ App started and DB initialized")

    return application


# Create the FastAPI app instance. This will be picked up by ASGI servers
# (e.g., Uvicorn, Gunicorn) when running the application.
app = create_app()