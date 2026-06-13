import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_config_validation_success() -> None:
    # A valid production config should not raise any validation error
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a_very_long_secure_production_secret_key_32_chars!",
        MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/db",
        REDIS_URL="redis://redis-server:6379/0",
        CORS_ORIGINS="https://bharathdelightfoods.in, https://admin.bharathdelightfoods.in",
        FRONTEND_ORIGIN="https://bharathdelightfoods.in",
        UPI_ID="realbusinessupi@upi",
        BREVO_API_KEY="xkeysib-real-api-key",
        BREVO_SENDER_EMAIL="sender@bharathdelightfoods.in",
        BREVO_SENDER_NAME="Bharath Delight Foods",
        CLOUDINARY_CLOUD_NAME="real_cloud",
        CLOUDINARY_API_KEY="real_key",
        CLOUDINARY_API_SECRET="real_secret"
    )
    assert settings.ENVIRONMENT == "production"
    assert settings.cors_origins_list == ["https://bharathdelightfoods.in", "https://admin.bharathdelightfoods.in"]


def test_production_config_default_secret_key() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="generate_a_secure_random_string_signature",
            MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/db",
            REDIS_URL="redis://redis-server:6379/0",
            CORS_ORIGINS="https://bharathdelightfoods.in",
            FRONTEND_ORIGIN="https://bharathdelightfoods.in",
            UPI_ID="realbusinessupi@upi",
            BREVO_API_KEY="xkeysib-real-api-key",
            CLOUDINARY_CLOUD_NAME="real_cloud",
            CLOUDINARY_API_KEY="real_key",
            CLOUDINARY_API_SECRET="real_secret"
        )
    assert "SECRET_KEY cannot be the default development value" in str(exc_info.value)


def test_production_config_short_secret_key() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="short-secret",
            MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/db",
            REDIS_URL="redis://redis-server:6379/0",
            CORS_ORIGINS="https://bharathdelightfoods.in",
            FRONTEND_ORIGIN="https://bharathdelightfoods.in",
            UPI_ID="realbusinessupi@upi",
            BREVO_API_KEY="xkeysib-real-api-key",
            CLOUDINARY_CLOUD_NAME="real_cloud",
            CLOUDINARY_API_KEY="real_key",
            CLOUDINARY_API_SECRET="real_secret"
        )
    assert "SECRET_KEY must be at least 32 characters long" in str(exc_info.value)


def test_production_config_localhost_mongodb() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a_very_long_secure_production_secret_key_32_chars!",
            MONGODB_URI="mongodb://localhost:27017/db",
            REDIS_URL="redis://redis-server:6379/0",
            CORS_ORIGINS="https://bharathdelightfoods.in",
            FRONTEND_ORIGIN="https://bharathdelightfoods.in",
            UPI_ID="realbusinessupi@upi",
            BREVO_API_KEY="xkeysib-real-api-key",
            CLOUDINARY_CLOUD_NAME="real_cloud",
            CLOUDINARY_API_KEY="real_key",
            CLOUDINARY_API_SECRET="real_secret"
        )
    assert "MONGODB_URI cannot refer to localhost in production" in str(exc_info.value)


def test_production_config_wildcard_cors() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a_very_long_secure_production_secret_key_32_chars!",
            MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/db",
            REDIS_URL="redis://redis-server:6379/0",
            CORS_ORIGINS="*",
            FRONTEND_ORIGIN="https://bharathdelightfoods.in",
            UPI_ID="realbusinessupi@upi",
            BREVO_API_KEY="xkeysib-real-api-key",
            CLOUDINARY_CLOUD_NAME="real_cloud",
            CLOUDINARY_API_KEY="real_key",
            CLOUDINARY_API_SECRET="real_secret"
        )
    assert "CORS_ORIGINS cannot be wildcard in production" in str(exc_info.value)


def test_production_config_http_frontend_origin() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a_very_long_secure_production_secret_key_32_chars!",
            MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/db",
            REDIS_URL="redis://redis-server:6379/0",
            CORS_ORIGINS="https://bharathdelightfoods.in",
            FRONTEND_ORIGIN="http://bharathdelightfoods.in",
            UPI_ID="realbusinessupi@upi",
            BREVO_API_KEY="xkeysib-real-api-key",
            CLOUDINARY_CLOUD_NAME="real_cloud",
            CLOUDINARY_API_KEY="real_key",
            CLOUDINARY_API_SECRET="real_secret"
        )
    assert "FRONTEND_ORIGIN must be configured and start with https://" in str(exc_info.value)


def test_production_config_missing_brevo_api_key() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a_very_long_secure_production_secret_key_32_chars!",
            MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/db",
            REDIS_URL="redis://redis-server:6379/0",
            CORS_ORIGINS="https://bharathdelightfoods.in",
            FRONTEND_ORIGIN="https://bharathdelightfoods.in",
            UPI_ID="realbusinessupi@upi",
            BREVO_API_KEY="",
            CLOUDINARY_CLOUD_NAME="real_cloud",
            CLOUDINARY_API_KEY="real_key",
            CLOUDINARY_API_SECRET="real_secret"
        )
    assert "BREVO_API_KEY must be configured in production" in str(exc_info.value)


def test_production_config_missing_storage_credentials() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a_very_long_secure_production_secret_key_32_chars!",
            MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/db",
            REDIS_URL="redis://redis-server:6379/0",
            CORS_ORIGINS="https://bharathdelightfoods.in",
            FRONTEND_ORIGIN="https://bharathdelightfoods.in",
            UPI_ID="realbusinessupi@upi",
            BREVO_API_KEY="xkeysib-real-api-key",
            CLOUDINARY_CLOUD_NAME="",
            CLOUDINARY_API_KEY="",
            CLOUDINARY_API_SECRET=""
        )
    assert "Either Cloudflare R2 or Cloudinary credentials must be fully configured in production" in str(exc_info.value)


def test_production_config_default_upi_id() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a_very_long_secure_production_secret_key_32_chars!",
            MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/db",
            REDIS_URL="redis://redis-server:6379/0",
            CORS_ORIGINS="https://bharathdelightfoods.in",
            FRONTEND_ORIGIN="https://bharathdelightfoods.in",
            UPI_ID="mrbharathfoods@upi",
            BREVO_API_KEY="xkeysib-real-api-key",
            CLOUDINARY_CLOUD_NAME="real_cloud",
            CLOUDINARY_API_KEY="real_key",
            CLOUDINARY_API_SECRET="real_secret"
        )
    assert "UPI_ID must be configured in production" in str(exc_info.value)
