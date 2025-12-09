from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import init_db, engine

# Security
from app.utils.security import hash_password
from app.utils.enums import UserRole

# =========================================================
# 🔥 IMPORT TẤT CẢ MODELS - QUAN TRỌNG!
# =========================================================
from app.models.user import User

# -----------------------------
from app.routers.auth import router as auth_router
from app.routers.booking import router as booking_router
from app.routers.payment import router as payment_router

# NEW routers
from app.routers.property_detail import router as property_detail_router
from app.routers.property_search import router as property_search_router
from app.routers.room import router as rooms_router   # check availability

# -----------------------------
# Import Routers (Admin)
# -----------------------------


# =========================================================
# CREATE FASTAPI APP
# =========================================================
def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    # -------------------------------------------------------
    # CORS CONFIG
    # -------------------------------------------------------
    cors_origins = [
        o.strip()
        for o in settings.CORS_ORIGINS.split(",")
        if o.strip()
    ]

    # Auto add local development URLs
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

    # -------------------------------------------------------
    # REGISTER ALL ROUTERS
    # -------------------------------------------------------

    # Public / Customer
    app.include_router(auth_router)
    app.include_router(booking_router)
    app.include_router(payment_router)
    app.include_router(property_search_router)
    app.include_router(property_detail_router)
    app.include_router(rooms_router)



    # -------------------------------------------------------
    # STARTUP EVENT → INIT DB + CREATE SUPER ADMIN
    # -------------------------------------------------------
    @app.on_event("startup")
    def on_startup() -> None:
        print("🚀 Backend starting...")

        # Create DB tables if not exist
        init_db()

        # --- Create super admin ---
        with Session(engine) as session:
            super_email = settings.SUPERUSER_EMAIL

            existing_user = session.exec(
                select(User).where(User.email == super_email)
            ).first()

            if existing_user:
                print(f"✔ Super admin already exists: {super_email}")
            else:
                print(f"🔥 Creating super admin: {super_email}")

                super_admin = User(
                    email=super_email,
                    password_hash=hash_password(settings.SUPERUSER_PASSWORD),
                    full_name="Super Admin",
                    role=UserRole.SUPER_ADMIN,
                    is_active=True,
                )

                session.add(super_admin)
                session.commit()
                print("🎉 Super admin created successfully!")

    return app


# -----------------------
# Final App Instance
# -----------------------
app = create_app()