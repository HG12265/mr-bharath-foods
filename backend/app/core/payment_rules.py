from app.core.exceptions import BaseAppException

ALLOWED_FORMATS = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_payment_proof_file(content_type: str, file_size: int) -> None:
    """
    Validates content type format and size limit for payment proof screenshots.
    """
    if content_type.lower() not in ALLOWED_FORMATS:
        raise BaseAppException(
            message=f"Unsupported format '{content_type}'. Allowed types: jpg, jpeg, png, webp.",
            code="UNSUPPORTED_MEDIA_FORMAT",
            status_code=400,
        )
    if file_size > MAX_FILE_SIZE:
        raise BaseAppException(
            message=f"File size exceeds 5MB limit. Got {(file_size / (1024 * 1024)):.2f}MB.",
            code="FILE_TOO_LARGE",
            status_code=400,
        )
