from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import init_db, engine

# Utils
from app.utils.security import hash_password
from app.utils.enums import UserRole

# Models
from app.models.user import User

# ----------------------------
# PUBLIC ROUTERS
# ----------------------------
from app.routers.auth import router as auth_router
from app.routers.booking import router as booking_router
from app.routers.payment import router as payment_router
from app.routers.review import router as review_router
from app.routers.room_search import router as room_search_router
from app.routers.property_search import router as property_search_router
from app.routers.webhook_payment import router as webhook_payment_router

# ----------------------------
# ADMIN ROUTERS
# ----------------------------
from app.routers.admin.property import router as admin_property_router
from app.routers.admin.amenity import router as admin_amenity_router
from app.routers.admin.room import router as admin_room_router
from app.routers.admin.room_type import router as admin_room_type_router
from app.routers.admin.property_amenity import router as admin_property_amenity_router


# ================================================================
# CREATE FASTAPI APP
# ================================================================
def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    # ------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------
    cors_origins = [
        o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()
    ]

    dev_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:5173",
    ]

    for origin in dev_origins:
        if origin not in cors_origins:
            cors_origins.append(origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------
    # REGISTER PUBLIC ROUTES
    # ------------------------------------------------------------
    app.include_router(auth_router)
    app.include_router(booking_router)
    app.include_router(payment_router)
    app.include_router(review_router)
    app.include_router(room_search_router)
    app.include_router(property_search_router)
    app.include_router(webhook_payment_router)

    # ------------------------------------------------------------
    # REGISTER ADMIN ROUTES
    # ------------------------------------------------------------
    app.include_router(admin_property_router)
    app.include_router(admin_amenity_router)
    app.include_router(admin_room_router)
    app.include_router(admin_room_type_router)
    app.include_router(admin_property_amenity_router)

    # ------------------------------------------------------------
    # STARTUP: INIT DB + CREATE SUPER ADMIN
    # ------------------------------------------------------------
    @app.on_event("startup")
    def on_startup():
        print("🚀 Server starting…")
        init_db()

        super_email = settings.SUPERUSER_EMAIL

        with Session(engine) as session:
            existing = session.exec(
                select(User).where(User.email == super_email)
            ).first()

            if existing:
                print(f"✔ Super Admin already exists: {super_email}")
                return

            # Create new super admin
            super_admin = User(
                email=super_email,
                full_name="Super Admin",
                password_hash=hash_password(settings.SUPERUSER_PASSWORD),
                role=UserRole.SUPER_ADMIN,
                is_active=True,
            )

            session.add(super_admin)
            session.commit()
            print("🎉 Super Admin created successfully!")

    return app


# Entry point
app = create_app()
