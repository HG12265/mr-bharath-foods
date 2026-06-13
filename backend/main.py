from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.contact import router as contact_router
from app.api.v1.carts import router as carts_router
from app.api.v1.categories import router as categories_router
from app.api.v1.checkouts import router as checkouts_router
from app.api.v1.customers import router as customers_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.health import router as health_router
from app.api.v1.inventories import router as inventories_router
from app.api.v1.media import router as media_router
from app.api.v1.notifications import admin_router as notifications_admin_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.orders import admin_router as orders_admin_router
from app.api.v1.orders import router as orders_router
from app.api.v1.payments import admin_router as payments_admin_router
from app.api.v1.payments import router as payments_router
from app.api.v1.production_hardening import router as production_hardening_router
from app.api.v1.products import router as products_router
from app.api.v1.reviews import admin_router as reviews_admin_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.search import router as search_router
from app.api.v1.settings import admin_router as settings_admin_router
from app.api.v1.settings import router as settings_router
from app.api.v1.shipments import admin_router as shipments_admin_router
from app.api.v1.shipments import router as shipments_router
from app.api.v1.wishlists import router as wishlists_router
from app.core.config import settings
from app.core.database import db_manager
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger
from app.core.openapi import configure_openapi
from app.core.redis import redis_manager
from app.middleware.api_version import APIVersionMiddleware
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.request_size import RequestSizeLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # 1. Startup phase
    logger.info("Starting up application context lifecycle...")
    try:
        await db_manager.connect_to_database()
        await redis_manager.connect_to_redis()
        if db_manager.db is not None:
            from app.core.index_registry import initialize_indexes
            await initialize_indexes(db_manager.db)

        from app.core.startup_checks import run_startup_checks
        run_startup_checks()
        logger.info("Application context startup completed successfully.")
    except Exception as exc:
        logger.critical(f"Context initialization failed: {exc!s}")
        raise exc

    yield

    # 2. Shutdown phase
    logger.info("Shutting down application context lifecycle...")
    await db_manager.close_database_connection()
    await redis_manager.close_redis_connection()
    logger.info("Application context shutdown completed.")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        lifespan=lifespan,
    )

    # Register middlewares (execution starts from the last added middleware upwards)
    app.add_middleware(APIVersionMiddleware)
    app.add_middleware(RequestSizeLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict to configured origins in staging/production environment configs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount local static files directory for serving uploaded media
    import os

    from fastapi.staticfiles import StaticFiles
    os.makedirs("static", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Root route returning version metadata
    @app.get("/", tags=["Metadata"])
    async def root_metadata() -> dict[str, str]:
        return {
            "project_name": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "environment": settings.ENVIRONMENT,
            "status": "running",
        }

    # Register customized exception response interceptors
    register_exception_handlers(app)

    # Register customized OpenAPI Swagger security templates mapping
    configure_openapi(app)

    # Core Versioned API routing
    app.include_router(
        health_router,
        prefix=f"{settings.API_V1_STR}/health",
        tags=["Health Monitoring Checks"]
    )
    app.include_router(
        auth_router,
        prefix=f"{settings.API_V1_STR}/auth",
        tags=["Authentication Operations"]
    )
    app.include_router(
        customers_router,
        prefix=f"{settings.API_V1_STR}/customers",
        tags=["Customer Operations"]
    )
    app.include_router(
        media_router,
        prefix=f"{settings.API_V1_STR}/media",
        tags=["Media Assets Operations"]
    )
    app.include_router(
        categories_router,
        prefix=f"{settings.API_V1_STR}/categories",
        tags=["Category Taxonomy Operations"]
    )
    app.include_router(
        products_router,
        prefix=f"{settings.API_V1_STR}/products",
        tags=["Product Catalog Operations"]
    )
    app.include_router(
        search_router,
        prefix=f"{settings.API_V1_STR}/search",
        tags=["Search & Analytics Operations"]
    )
    app.include_router(
        wishlists_router,
        prefix=f"{settings.API_V1_STR}/wishlists",
        tags=["Wishlist Operations"]
    )
    app.include_router(
        carts_router,
        prefix=f"{settings.API_V1_STR}/carts",
        tags=["Cart Operations"]
    )
    app.include_router(
        inventories_router,
        prefix=f"{settings.API_V1_STR}/inventories",
        tags=["Inventory Operations"]
    )
    app.include_router(
        checkouts_router,
        prefix=f"{settings.API_V1_STR}/checkouts",
        tags=["Checkout Operations"]
    )
    app.include_router(
        orders_router,
        prefix=f"{settings.API_V1_STR}/orders",
        tags=["Order Operations"]
    )
    app.include_router(
        orders_admin_router,
        prefix=f"{settings.API_V1_STR}/admin/orders",
        tags=["Order Admin Operations"]
    )
    app.include_router(
        payments_router,
        prefix=f"{settings.API_V1_STR}/payments",
        tags=["Payment Operations"]
    )
    app.include_router(
        payments_admin_router,
        prefix=f"{settings.API_V1_STR}/admin/payments",
        tags=["Payment Admin Operations"]
    )
    app.include_router(
        shipments_router,
        prefix=f"{settings.API_V1_STR}/shipments",
        tags=["Shipment Operations"]
    )
    app.include_router(
        shipments_admin_router,
        prefix=f"{settings.API_V1_STR}/admin/shipments",
        tags=["Shipment Admin Operations"]
    )
    app.include_router(
        notifications_router,
        prefix=f"{settings.API_V1_STR}/notifications",
        tags=["Notification Operations"]
    )
    app.include_router(
        notifications_admin_router,
        prefix=f"{settings.API_V1_STR}/admin/notifications",
        tags=["Notification Admin Operations"]
    )
    app.include_router(
        reviews_router,
        prefix=f"{settings.API_V1_STR}/reviews",
        tags=["Review Operations"]
    )
    app.include_router(
        reviews_admin_router,
        prefix=f"{settings.API_V1_STR}/admin/reviews",
        tags=["Review Admin Operations"]
    )
    app.include_router(
        dashboard_router,
        prefix=f"{settings.API_V1_STR}/admin/dashboard",
        tags=["Dashboard Operations"]
    )
    app.include_router(
        settings_router,
        prefix=f"{settings.API_V1_STR}/settings",
        tags=["Settings Operations"]
    )
    app.include_router(
        settings_admin_router,
        prefix=f"{settings.API_V1_STR}/admin/settings",
        tags=["Settings Admin Operations"]
    )
    app.include_router(
        production_hardening_router,
        prefix=f"{settings.API_V1_STR}/admin",
        tags=["Production Hardening Operations"]
    )
    app.include_router(
        contact_router,
        prefix=f"{settings.API_V1_STR}",
        tags=["Contact Operations"]
    )

    return app

app = create_app()
