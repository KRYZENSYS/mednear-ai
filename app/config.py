"""Application configuration using Pydantic Settings.

This module loads all environment variables and provides a centralized
configuration object for the entire application.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Telegram bot configuration settings."""

    token: str = Field(..., alias="BOT_TOKEN")
    username: str = Field(default="MedNearAIBot", alias="BOT_USERNAME")
    webhook_url: Optional[str] = Field(default=None, alias="BOT_WEBHOOK_URL")
    webhook_port: int = Field(default=8443, alias="BOT_WEBHOOK_PORT")
    admin_ids: str = Field(default="", alias="BOT_ADMIN_IDS")
    dev_id: Optional[int] = Field(default=None, alias="BOT_DEV_ID")
    debug: bool = Field(default=False, alias="BOT_DEBUG")

    @property
    def admin_id_list(self) -> List[int]:
        """Parse admin IDs from comma-separated string."""
        if not self.admin_ids:
            return []
        try:
            return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]
        except ValueError:
            return []

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration."""

    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=5432, alias="DB_PORT")
    name: str = Field(default="mednear_ai", alias="DB_NAME")
    user: str = Field(default="mednear_user", alias="DB_USER")
    password: str = Field(..., alias="DB_PASSWORD")
    pool_size: int = Field(default=20, alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, alias="DB_ECHO")

    @property
    def async_url(self) -> str:
        """Build async database URL for SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    def sync_url(self) -> str:
        """Build sync database URL for Alembic."""
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class RedisSettings(BaseSettings):
    """Redis cache configuration."""

    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    db: int = Field(default=0, alias="REDIS_DB")
    password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class AISettings(BaseSettings):
    """AI service API configuration."""

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=4096, alias="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, alias="OPENAI_TEMPERATURE")

    gemini_api_key: str = Field(..., alias="GOOGLE_GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")

    google_maps_api_key: str = Field(default="", alias="GOOGLE_MAPS_API_KEY")
    whisper_model: str = Field(default="whisper-1", alias="WHISPER_MODEL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class SecuritySettings(BaseSettings):
    """Security and authentication configuration."""

    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_expire_minutes: int = Field(default=1440, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_expire_days: int = Field(default=30, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    encryption_key: str = Field(..., alias="ENCRYPTION_KEY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class PaymentSettings(BaseSettings):
    """Payment system configuration."""

    provider_token: Optional[str] = Field(default=None, alias="PAYMENT_PROVIDER_TOKEN")
    premium_1_month: int = Field(default=25000, alias="PREMIUM_1_MONTH_PRICE")
    premium_3_month: int = Field(default=65000, alias="PREMIUM_3_MONTH_PRICE")
    premium_12_month: int = Field(default=200000, alias="PREMIUM_12_MONTH_PRICE")
    currency: str = Field(default="UZS", alias="CURRENCY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    level: str = Field(default="INFO", alias="LOG_LEVEL")
    file: str = Field(default="logs/bot.log", alias="LOG_FILE")
    max_bytes: int = Field(default=10485760, alias="LOG_MAX_BYTES")
    backup_count: int = Field(default=10, alias="LOG_BACKUP_COUNT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class AppSettings(BaseSettings):
    """General application settings."""

    name: str = Field(default="MedNear AI", alias="APP_NAME")
    version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="production", alias="APP_ENVIRONMENT")
    timezone: str = Field(default="Asia/Tashkent", alias="APP_TIMEZONE")
    default_language: str = Field(default="uz", alias="DEFAULT_LANGUAGE")
    supported_languages: str = Field(default="uz,ru,en", alias="SUPPORTED_LANGUAGES")

    @property
    def language_list(self) -> List[str]:
        """Parse supported languages."""
        return [x.strip() for x in self.supported_languages.split(",") if x.strip()]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings:
    """Main settings aggregator.

    Combines all configuration sections into a single accessible object.
    """

    def __init__(self) -> None:
        """Initialize all settings sections."""
        self.bot = BotSettings()
        self.db = DatabaseSettings()
        self.redis = RedisSettings()
        self.ai = AISettings()
        self.security = SecuritySettings()
        self.payment = PaymentSettings()
        self.logging = LoggingSettings()
        self.app = AppSettings()

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app.environment.lower() in ("development", "dev")

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in self.bot.admin_id_list

    def __repr__(self) -> str:
        """String representation (hiding secrets)."""
        return (
            f"Settings(app={self.app.name} v{self.app.version}, "
            f"env={self.app.environment}, db={self.db.host})"
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Cached application settings.
    """
    return Settings()


settings = get_settings()