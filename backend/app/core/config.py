
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True
    )

    PROJECT_NAME: str = "Bharath Delight Foods"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days

    MONGODB_URI: str
    DATABASE_NAME: str = "mr_bharath_foods"

    REDIS_URL: str
    UPI_ID: str = "mrbharathfoods@upi"  # TODO: Update after new UPI ID is created

    # Production Hardening Configurations
    ENVIRONMENT: str = "development"
    MAX_PAGINATION_LIMIT: int = 250
    MAX_REQUEST_SIZE_BYTES: int = 16777216  # 16MB
    PROJECT_VERSION: str = "1.0.0"

    # Cloudflare R2 configurations
    R2_ENDPOINT_URL: str | None = None
    R2_ACCESS_KEY_ID: str | None = None
    R2_SECRET_ACCESS_KEY: str | None = None
    R2_BUCKET_NAME: str | None = None

    # Cloudinary configurations
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    # Brevo Email configurations
    BREVO_API_KEY: str | None = None
    BREVO_SENDER_EMAIL: str | None = None
    BREVO_SENDER_NAME: str = "Bharath Delight Foods"

    # Admin contact for notifications (e.g. contact form inquiries)
    ADMIN_EMAIL: str = "bharathdelightfoods@gmail.com"

settings = Settings()  # type: ignore[call-arg]
