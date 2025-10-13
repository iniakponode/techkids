from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./aitechkids.db"
    SECRET_KEY: str = "techkids-development-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    EMAIL_SENDER: str = "no-reply@techkids.local"
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 587
    POST_SCHEDULER_INTERVAL: int = 15  # Check for posts every 15 seconds
    FACEBOOK_API_TOKEN: str | None = None
    X_API_TOKEN: str | None = None
    INSTAGRAM_API_TOKEN: str | None = None
    POST_DISPATCH_MAX_ATTEMPTS: int = 3
    POST_DISPATCH_RETRY_BACKOFF: int = 300
    
    # Paystack Configuration
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""
    PAYSTACK_BASE_URL: str = "https://api.paystack.co"
    PAYSTACK_CALLBACK_URL: str = ""
    
    # If you have more config variables, add them here.

    # Pydantic 2.x style config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
