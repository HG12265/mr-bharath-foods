from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.config import settings


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_size_bytes: int | None = None):
        super().__init__(app)
        self.max_size_bytes = max_size_bytes or settings.MAX_REQUEST_SIZE_BYTES

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    if int(content_length) > self.max_size_bytes:
                        return JSONResponse(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            content={
                                "success": False,
                                "message": f"Request payload size exceeds the limit of {self.max_size_bytes} bytes.",
                                "data": None,
                            },
                        )
                except ValueError:
                    pass
        return await call_next(request)
