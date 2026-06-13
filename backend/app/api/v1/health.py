import time
from typing import Any

from fastapi import APIRouter

from app.core.database import db_manager
from app.core.redis import redis_manager
from app.schemas.common import Envelope
from app.schemas.health import ComponentStatus, SystemHealthResponse

router = APIRouter()

@router.get("/health", response_model=Envelope[SystemHealthResponse])
async def check_system_health() -> Envelope[SystemHealthResponse]:
    """
    Pings MongoDB Atlas and Redis connections to verify overall backend status.
    """
    # 1. MongoDB check
    db_status = "unhealthy"
    db_latency = 0.0
    db_details = {}
    if db_manager.client:
        try:
            start_time = time.perf_counter()
            await db_manager.client.admin.command("ping")
            db_latency = (time.perf_counter() - start_time) * 1000
            db_status = "healthy"
        except Exception as exc:
            db_details["error"] = str(exc)

    # 2. Redis check
    redis_status = "unhealthy"
    redis_latency = 0.0
    redis_details = {}
    if redis_manager.client:
        try:
            start_time = time.perf_counter()
            await redis_manager.client.ping()
            redis_latency = (time.perf_counter() - start_time) * 1000
            redis_status = "healthy"
        except Exception as exc:
            redis_details["error"] = str(exc)

    system_status = "healthy" if (db_status == "healthy" and redis_status == "healthy") else "degraded"

    health_data = SystemHealthResponse(
        status=system_status,
        database=ComponentStatus(status=db_status, latency_ms=db_latency, details=db_details),
        redis=ComponentStatus(status=redis_status, latency_ms=redis_latency, details=redis_details)
    )

    return Envelope(
        success=True,
        message="System status verified successfully.",
        data=health_data
    )


@router.get("/readiness", response_model=Envelope[dict[str, Any]])
@router.get("/health/readiness", response_model=Envelope[dict[str, Any]], include_in_schema=False)
async def check_system_readiness() -> Any:
    """
    Readiness probe verifying MongoDB and Redis connections.
    Returns 503 if any key dependency is unhealthy.
    """

    from fastapi import status
    from fastapi.responses import JSONResponse

    db_ok = False
    redis_ok = False

    # 1. MongoDB check
    if db_manager.client:
        try:
            await db_manager.client.admin.command("ping")
            db_ok = True
        except Exception:
            pass

    # 2. Redis check
    if redis_manager.client:
        try:
            await redis_manager.client.ping()
            redis_ok = True
        except Exception:
            pass

    if not db_ok or not redis_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "message": "Service is unhealthy.",
                "data": {
                    "database": "healthy" if db_ok else "unhealthy",
                    "redis": "healthy" if redis_ok else "unhealthy",
                },
            },
        )

    return Envelope(
        success=True,
        message="Service is ready to accept traffic.",
        data={
            "database": "healthy",
            "redis": "healthy",
        },
    )
