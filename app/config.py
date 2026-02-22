from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    DATABASE_URL: str
    BASE_URL: str = "http://localhost:8000"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXP_MINUTES: int = 60
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    ASSETS_DIR: str = "assets"  # Directory for storing generated assets (QR codes, ID cards, photos)
    # Deprecated (no longer needed - using in-memory storage)
    REDIS_URL: str = ""
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
