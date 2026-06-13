
from pydantic import model_validator
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
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    MONGODB_URI: str
    DATABASE_NAME: str = "mr_bharath_foods"

    REDIS_URL: str
    UPI_ID: str = "mrbharathfoods@upi"  # TODO: Update after new UPI ID is created

    # Production Hardening Configurations
    ENVIRONMENT: str = "development"
    MAX_PAGINATION_LIMIT: int = 250
    MAX_REQUEST_SIZE_BYTES: int = 16777216  # 16MB
    PROJECT_VERSION: str = "1.0.0"

    FRONTEND_ORIGIN: str = "http://localhost:3000"
    CORS_ORIGINS: str = "http://localhost:3000"

    # Cloudflare R2 configurations
    R2_ENDPOINT_URL: str | None = None
    R2_ACCESS_KEY_ID: str | None = None
    R2_SECRET_ACCESS_KEY: str | None = None
    R2_BUCKET_NAME: str | None = None
    R2_PUBLIC_BASE_URL: str | None = None

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
    MEDIA_FOLDER_PREFIX: str = "bharath-delight-foods"

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production_config(self) -> 'Settings':
        if self.ENVIRONMENT.lower() == "production":
            # 1. SECRET_KEY Strength Check
            default_secret = "generate_a_secure_random_string_signature"
            if self.SECRET_KEY == default_secret:
                raise ValueError("Production configuration error: SECRET_KEY cannot be the default development value.")
            if len(self.SECRET_KEY) < 32:
                raise ValueError("Production configuration error: SECRET_KEY must be at least 32 characters long.")

            # 2. MONGODB_URI Check
            if "localhost" in self.MONGODB_URI or "127.0.0.1" in self.MONGODB_URI:
                raise ValueError("Production configuration error: MONGODB_URI cannot refer to localhost in production.")

            # 3. CORS_ORIGINS Check
            if not getattr(self, "CORS_ORIGINS", None) or self.CORS_ORIGINS.strip() == "":
                raise ValueError("Production configuration error: CORS_ORIGINS must be configured in production.")
            origins = self.cors_origins_list
            if not origins:
                raise ValueError("Production configuration error: CORS_ORIGINS must be configured in production.")
            if "*" in origins:
                raise ValueError("Production configuration error: CORS_ORIGINS cannot be wildcard in production.")

            # 4. FRONTEND_ORIGIN Check
            if not getattr(self, "FRONTEND_ORIGIN", None) or not self.FRONTEND_ORIGIN.startswith("https://"):
                raise ValueError("Production configuration error: FRONTEND_ORIGIN must be configured and start with https:// in production.")

            # 5. BREVO_API_KEY Check
            if not self.BREVO_API_KEY or "your_brevo_api_key_here" in self.BREVO_API_KEY or self.BREVO_API_KEY.strip() == "":
                raise ValueError("Production configuration error: BREVO_API_KEY must be configured in production.")

            # 6. Storage Credentials Check (Cloudinary or R2)
            has_r2 = all([
                self.R2_ENDPOINT_URL,
                self.R2_ACCESS_KEY_ID,
                self.R2_SECRET_ACCESS_KEY,
                self.R2_BUCKET_NAME,
                self.R2_ACCESS_KEY_ID != "r2_access_key",
                self.R2_SECRET_ACCESS_KEY != "r2_secret_key"
            ])
            has_cloudinary = all([
                self.CLOUDINARY_CLOUD_NAME,
                self.CLOUDINARY_API_KEY,
                self.CLOUDINARY_API_SECRET,
                self.CLOUDINARY_CLOUD_NAME != "cloudinary_cloud_name",
                self.CLOUDINARY_API_KEY != "cloudinary_api_key",
                self.CLOUDINARY_API_SECRET != "cloudinary_api_secret"
            ])
            if not has_r2 and not has_cloudinary:
                raise ValueError("Production configuration error: Either Cloudflare R2 or Cloudinary credentials must be fully configured in production.")

            # 7. UPI_ID Check
            if not self.UPI_ID or "mrbharathfoods@upi" in self.UPI_ID or "bharathdelightfoods@upi" in self.UPI_ID or self.UPI_ID.strip() == "":
                raise ValueError("Production configuration error: UPI_ID must be configured in production.")

        return self


settings = Settings()  # type: ignore[call-arg]
