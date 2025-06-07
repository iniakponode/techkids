import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: str
    ENVIRONMENT:str
    DATABASE_URL:str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    EMAIL_SENDER: str
    EMAIL_HOST: str
    EMAIL_PORT: int
    POST_SCHEDULER_INTERVAL: int = 60
    FACEBOOK_API_TOKEN: str | None = None
    X_API_TOKEN: str | None = None
    INSTAGRAM_API_TOKEN: str | None = None
    # If you have more config variables, add them here.

    # Pydantic 2.x style config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
