from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings


def custom_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Enterprise API Core Gateway for Bharath Delight Foods digital platform.",
        routes=app.routes,
    )

    # Configure security scheme for JWT Bearer Tokens
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter access JWT directly to authenticate requests"
        }
    }

    # Require security constraints globally for routes (except public paths)
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

def configure_openapi(app: FastAPI) -> None:
    app.openapi = lambda: custom_openapi(app)  # type: ignore[method-assign]
