from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./techkids.db"
    SECRET_KEY: str = "techkids-development-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    EMAIL_SENDER: str = "no-reply@techkids.local"
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 587
    POST_SCHEDULER_INTERVAL: int = 60
    FACEBOOK_API_TOKEN: str | None = None
    X_API_TOKEN: str | None = None
    INSTAGRAM_API_TOKEN: str | None = None
    POST_DISPATCH_MAX_ATTEMPTS: int = 3
    POST_DISPATCH_RETRY_BACKOFF: int = 300
    # If you have more config variables, add them here.

    # Pydantic 2.x style config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
