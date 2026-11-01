from typing import Any

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repository: Any):
        if not isinstance(repository, AuditRepository):
            repository = AuditRepository(repository)
        self.repository = repository

    async def log_action(
        self,
        action: str,
        target_collection: str,
        user_id: str | None = None,
        target_id: str | None = None,
        ip_address: str | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> AuditLog:
        """
        Persists a new structured audit log record in database.
        Metadata can contain movement_type, quantity, before, after, reason, etc.
        """
        if metadata is None and "details" in kwargs:
            metadata = kwargs["details"]

        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            target_collection=target_collection,
            target_id=target_id,
            ip_address=ip_address,
            metadata=metadata or {},
        )
        return await self.repository.insert(log_entry)
