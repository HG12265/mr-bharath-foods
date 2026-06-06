from app.core.config import settings
from app.core.logging import logger


def run_startup_checks() -> dict[str, dict[str, object]]:
    """
    Executes production-hardening environment and security configuration validation checks.
    Logs warning messages on security vulnerabilities.
    Returns a dictionary mapping check names to status.
    """
    checks = {}
    is_production = settings.ENVIRONMENT.lower() in ("production", "staging")

    # 1. SECRET_KEY Strength Check
    secret_key_pass = True
    secret_key_reason = "Pass"
    default_secret = "generate_a_secure_random_string_signature"
    if settings.SECRET_KEY == default_secret:
        secret_key_pass = False
        secret_key_reason = "SECRET_KEY uses the default vulnerable string value."
        if is_production:
            logger.critical("SECURITY WARNING: DEFAULT SECRET_KEY DETECTED IN PRODUCTION!")
    elif len(settings.SECRET_KEY) < 32:
        secret_key_pass = False
        secret_key_reason = "SECRET_KEY length is insecure (less than 32 characters)."
        if is_production:
            logger.warning("SECURITY WARNING: SECRET_KEY IS SHORTER THAN 32 CHARACTERS!")

    checks["secret_key"] = {
        "pass": secret_key_pass,
        "details": secret_key_reason,
    }

    # 2. MongoDB URI Location Check
    mongodb_pass = True
    mongodb_reason = "Pass"
    if "localhost" in settings.MONGODB_URI or "127.0.0.1" in settings.MONGODB_URI:
        mongodb_reason = "Localhost MongoDB URI detected."
        if is_production:
            mongodb_pass = False
            logger.critical("SECURITY WARNING: LOCALHOST MONGODB URI DETECTED IN PRODUCTION ENVIRONMENT!")
    checks["mongodb_uri"] = {
        "pass": mongodb_pass,
        "details": mongodb_reason,
    }

    # 3. Redis URL Location Check
    redis_pass = True
    redis_reason = "Pass"
    if "localhost" in settings.REDIS_URL or "127.0.0.1" in settings.REDIS_URL:
        redis_reason = "Localhost Redis URL detected."
        if is_production:
            redis_pass = False
            logger.critical("SECURITY WARNING: LOCALHOST REDIS URL DETECTED IN PRODUCTION ENVIRONMENT!")
    checks["redis_url"] = {
        "pass": redis_pass,
        "details": redis_reason,
    }

    # 4. R2 Configuration Verification Check
    r2_pass = True
    r2_missing = []
    if not settings.R2_ENDPOINT_URL:
        r2_missing.append("R2_ENDPOINT_URL")
    if not settings.R2_ACCESS_KEY_ID or settings.R2_ACCESS_KEY_ID == "r2_access_key":
        r2_missing.append("R2_ACCESS_KEY_ID")
    if not settings.R2_SECRET_ACCESS_KEY or settings.R2_SECRET_ACCESS_KEY == "r2_secret_key":
        r2_missing.append("R2_SECRET_ACCESS_KEY")
    if not settings.R2_BUCKET_NAME or settings.R2_BUCKET_NAME == "mbf-media-bucket":
        r2_missing.append("R2_BUCKET_NAME")

    if r2_missing:
        r2_pass = False
        r2_reason = f"Missing or default Cloudflare R2 values: {', '.join(r2_missing)}"
        logger.warning(f"R2 Configuration incomplete: {r2_reason}")
    else:
        r2_reason = "R2 storage parameters are fully configured."

    checks["r2_configuration"] = {
        "pass": r2_pass,
        "details": r2_reason,
    }

    return checks
