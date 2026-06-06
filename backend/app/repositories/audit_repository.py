from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_AUDIT_LOGS
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_AUDIT_LOGS, AuditLog)
