from app.core.config import settings


def cap_pagination_limit(limit: int | None) -> int:
    """
    Ensures that pagination limit is capped at settings.MAX_PAGINATION_LIMIT.
    """
    if limit is None or limit <= 0:
        return settings.MAX_PAGINATION_LIMIT
    return min(limit, settings.MAX_PAGINATION_LIMIT)
