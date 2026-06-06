
from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repository: AuditRepository):
        self.repository = repository

    async def log_action(
        self,
        action: str,
        target_collection: str,
        user_id: str | None = None,
        target_id: str | None = None,
        ip_address: str | None = None
    ) -> AuditLog:
        """
        Persists a new structured audit log record in database.
        """
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            target_collection=target_collection,
            target_id=target_id,
            ip_address=ip_address
        )
        return await self.repository.insert(log_entry)

# Empty module init check placeholder
