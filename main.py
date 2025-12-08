from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db

# Routers
from app.routers.auth import router as auth_router
from app.routers.booking import router as booking_router
from app.routers.payment import router as payment_router
from app.routers.review import router as review_router
from app.routers.search import router as search_router
from app.routers.webhook_payment import router as webhook_router

# Admin Routers
from app.routers.admin.property import router as admin_property_router
from app.routers.admin.amenity import router as admin_amenity_router
from app.routers.admin.room import router as admin_room_router
from app.routers.admin.room_type import router as admin_room_type_router
from app.routers.admin.property_amenity import router as admin_property_amenity_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    # ---------------------------------------------------
    # CORS CONFIG
    # ---------------------------------------------------
    cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

    # Auto allowed dev URLs
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

    # ---------------------------------------------------
    # REGISTER ROUTERS
    # ---------------------------------------------------
    ## Public / Auth / Customer
    app.include_router(auth_router)
    app.include_router(booking_router)
    app.include_router(payment_router)
    app.include_router(review_router)
    app.include_router(search_router)
    app.include_router(webhook_router)

    ## Admin routes
    app.include_router(admin_property_router)
    app.include_router(admin_amenity_router)
    app.include_router(admin_room_router)
    app.include_router(admin_room_type_router)
    app.include_router(admin_property_amenity_router)

    # ---------------------------------------------------
    # DB INIT
    # ---------------------------------------------------
    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    return app


app = create_app()
