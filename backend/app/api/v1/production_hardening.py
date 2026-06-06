import time
from typing import Any

from fastapi import APIRouter, Depends

from app.core.database import db_manager
from app.core.dependencies import get_db, require_role
from app.core.redis import redis_manager
from app.core.roles import UserRole
from app.core.startup_checks import run_startup_checks
from app.schemas.auth import TokenData
from app.schemas.common import Envelope

router = APIRouter()


@router.get("/production-checklist", response_model=Envelope[dict[str, Any]])
async def get_production_checklist(
    current_user: TokenData = Depends(require_role(UserRole.ADMIN)),
    db: Any = Depends(get_db),
) -> Envelope[dict[str, Any]]:
    """
    Exposes a production readiness checklist for administrators.
    Checks environment configurations, db indexes, and connectivity status.
    """
    # 1. Run environment and config checks
    checklist = run_startup_checks()

    # 2. Database connectivity
    db_ok = False
    db_latency = 0.0
    if db_manager.client:
        try:
            start = time.perf_counter()
            await db_manager.client.admin.command("ping")
            db_latency = (time.perf_counter() - start) * 1000
            db_ok = True
        except Exception:
            pass

    checklist["database_connectivity"] = {  # type: ignore[assignment]
        "pass": db_ok,
        "details": f"Ping latency: {db_latency:.2f}ms" if db_ok else "Database connection is unhealthy.",
    }

    # 3. Redis connectivity
    redis_ok = False
    redis_latency = 0.0
    if redis_manager.client:
        try:
            start = time.perf_counter()
            await redis_manager.client.ping()
            redis_latency = (time.perf_counter() - start) * 1000
            redis_ok = True
        except Exception:
            pass

    checklist["redis_connectivity"] = {  # type: ignore[assignment]
        "pass": redis_ok,
        "details": f"Ping latency: {redis_latency:.2f}ms" if redis_ok else "Redis connection is unhealthy.",
    }

    # 4. Check settings initialization
    settings_ok = False
    try:
        from app.repositories.settings_repository import SettingsRepository
        settings_repo = SettingsRepository(db)
        settings_doc = await settings_repo.get_settings()
        if settings_doc:
            settings_ok = True
            details = "Settings initialized."
        else:
            details = "Default settings document is missing in DB."
    except Exception as exc:
        details = f"Error querying settings: {exc}"

    checklist["settings_initialized"] = {  # type: ignore[assignment]
        "pass": settings_ok,
        "details": details,
    }

    # Decide overall status
    all_pass = all(item["pass"] for item in checklist.values())

    return Envelope(
        success=True,
        message="Production readiness checks compiled.",
        data={
            "ready": all_pass,
            "checklist": checklist,
        },
    )
