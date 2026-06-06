from datetime import datetime
from typing import Any

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    target_user_id: str | None = None
    role_target: str | None = None
    type: str
    title: str
    message: str
    metadata: dict[str, Any]
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None
