from typing import Any

from pydantic import BaseModel


class ComponentStatus(BaseModel):
    status: str
    latency_ms: float
    details: dict[str, Any] = {}

class SystemHealthResponse(BaseModel):
    status: str
    database: ComponentStatus
    redis: ComponentStatus
