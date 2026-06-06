from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.config import settings


class APIVersionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, version: str | None = None):
        super().__init__(app)
        self.version = version or settings.PROJECT_VERSION

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-API-Version"] = self.version
        return response
