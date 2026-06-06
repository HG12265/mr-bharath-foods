import time

from fastapi import APIRouter

from app.core.database import db_manager
from app.core.redis import redis_manager
from app.schemas.common import Envelope
from app.schemas.health import ComponentStatus, SystemHealthResponse

router = APIRouter()

@router.get("", response_model=Envelope[SystemHealthResponse])
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
