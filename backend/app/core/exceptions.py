from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.common import ErrorDetail, ErrorEnvelope


class BaseAppException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class NotFoundException(BaseAppException):
    def __init__(self, message: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(message, code, status.HTTP_404_NOT_FOUND)

class AuthenticationException(BaseAppException):
    def __init__(self, message: str = "Could not validate credentials", code: str = "UNAUTHORIZED"):
        super().__init__(message, code, status.HTTP_401_UNAUTHORIZED)

class PermissionDeniedException(BaseAppException):
    def __init__(self, message: str = "Access forbidden", code: str = "FORBIDDEN"):
        super().__init__(message, code, status.HTTP_403_FORBIDDEN)

class RateLimitException(BaseAppException):
    def __init__(self, message: str = "Rate limit exceeded", code: str = "RATE_LIMIT_EXCEEDED"):
        super().__init__(message, code, status.HTTP_429_TOO_MANY_REQUESTS)

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        envelope = ErrorEnvelope(
            message=exc.message,
            errors=[ErrorDetail(code=exc.code, message=exc.message)]
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=envelope.model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = []
        for error in exc.errors():
            field = ".".join(map(str, error.get("loc", [])))
            details.append(
                ErrorDetail(
                    code="VALIDATION_ERROR",
                    message=error.get("msg", "Invalid value"),
                    field=field
                )
            )
        envelope = ErrorEnvelope(
            message="Data validation constraints breached.",
            errors=details
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=envelope.model_dump()
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        envelope = ErrorEnvelope(
            message=str(exc.detail),
            errors=[ErrorDetail(code="HTTP_ERROR", message=str(exc.detail))]
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=envelope.model_dump()
        )
