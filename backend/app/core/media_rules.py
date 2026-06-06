import os
from typing import TypedDict

from app.core.exceptions import BaseAppException


class MediaRule(TypedDict):
    allowed_types: set[str]
    allowed_extensions: set[str]
    max_size: int


MEDIA_RULES: dict[str, MediaRule] = {
    "product_image": {
        "allowed_types": {"image/jpeg", "image/png", "image/webp", "image/gif", "image/svg+xml"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"},
        "max_size": 5 * 1024 * 1024,  # 5MB
    },
    "blog_image": {
        "allowed_types": {"image/jpeg", "image/png", "image/webp", "image/gif"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".webp", ".gif"},
        "max_size": 5 * 1024 * 1024,  # 5MB
    },
    "certificate_pdf": {
        "allowed_types": {"application/pdf"},
        "allowed_extensions": {".pdf"},
        "max_size": 10 * 1024 * 1024,  # 10MB
    },
    "avatar": {
        "allowed_types": {"image/jpeg", "image/png", "image/webp"},
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".webp"},
        "max_size": 2 * 1024 * 1024,  # 2MB
    },
    "packaging_file": {
        "allowed_types": {
            "image/jpeg", "image/png", "image/webp", "application/pdf",
            "image/svg+xml", "application/zip", "application/x-zip-compressed"
        },
        "allowed_extensions": {".jpg", ".jpeg", ".png", ".webp", ".pdf", ".svg", ".zip"},
        "max_size": 20 * 1024 * 1024,  # 20MB
    },
    "video": {
        "allowed_types": {"video/mp4", "video/webm", "video/ogg", "video/quicktime"},
        "allowed_extensions": {".mp4", ".webm", ".ogg", ".mov"},
        "max_size": 100 * 1024 * 1024,  # 100MB
    }
}

def validate_media_file(filename: str, content_type: str, size: int, asset_type: str) -> None:
    """
    Validates that file properties (size, MIME type, and extension) align with target asset rules.
    """
    if asset_type not in MEDIA_RULES:
        raise BaseAppException(
            message=f"Unsupported asset type: {asset_type}.",
            code="UNSUPPORTED_ASSET_TYPE",
            status_code=400
        )

    rules = MEDIA_RULES[asset_type]

    # Validate file size
    if size <= 0:
        raise BaseAppException(
            message="File size must be greater than zero.",
            code="INVALID_FILE_SIZE",
            status_code=400
        )
    if size > rules["max_size"]:
        max_size_mb = rules["max_size"] / (1024 * 1024)
        raise BaseAppException(
            message=f"File size exceeds maximum limit of {max_size_mb:.1f}MB for asset type '{asset_type}'.",
            code="FILE_TOO_LARGE",
            status_code=400
        )

    # Validate MIME type
    if content_type not in rules["allowed_types"]:
        raise BaseAppException(
            message=f"MIME type '{content_type}' is not allowed for asset type '{asset_type}'.",
            code="INVALID_MIME_TYPE",
            status_code=400
        )

    # Validate extension
    _, ext = os.path.splitext(filename.lower())
    if ext not in rules["allowed_extensions"]:
        raise BaseAppException(
            message=f"File extension '{ext}' is not allowed for asset type '{asset_type}'.",
            code="INVALID_FILE_EXTENSION",
            status_code=400
        )
