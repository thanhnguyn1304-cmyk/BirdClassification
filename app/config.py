import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    database_path: str = "birds.db"
    storage_dir: str = "storage"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Resolve paths relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, settings.storage_dir)
DATABASE_PATH = os.path.join(BASE_DIR, settings.database_path)

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)
