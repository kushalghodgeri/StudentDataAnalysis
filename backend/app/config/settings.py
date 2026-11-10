"""Application configuration and environment settings using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application configuration."""

    # Database Configuration
    DB_HOST: str = Field(default="127.0.0.1", description="MySQL Host")
    DB_PORT: int = Field(default=3306, description="MySQL Port")
    DB_USER: str = Field(default="root", description="MySQL Username")
    DB_PASSWORD: str = Field(default="rootpassword", description="MySQL Password")
    DB_NAME: str = Field(default="student_analytics", description="MySQL Database Name")
    DB_POOL_NAME: str = Field(default="student_pool", description="Connection Pool Name")
    DB_POOL_SIZE: int = Field(default=10, description="Connection Pool Size")

    # Application Settings
    APP_ENV: str = Field(default="development", description="Environment mode")
    APP_PORT: int = Field(default=8000, description="Uvicorn server port")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173"],
        description="Allowed CORS origins"
    )
    LOG_LEVEL: str = Field(default="INFO", description="Application log level")
    LOG_FILE: str = Field(default="backend/app.log", description="Rotating log file path")

    # Storage Paths
    BASE_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
    )
    DATA_RAW_DIR: str = Field(default="backend/data/raw")
    DATA_PROCESSED_DIR: str = Field(default="backend/data/processed")
    OUTPUT_CHARTS_DIR: str = Field(default="backend/output/charts")
    OUTPUT_REPORTS_DIR: str = Field(default="backend/output/reports")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def raw_dir_path(self) -> Path:
        """Resolve absolute path to raw data directory."""
        path = self.BASE_DIR / "data" / "raw"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def processed_dir_path(self) -> Path:
        """Resolve absolute path to processed data directory."""
        path = self.BASE_DIR / "data" / "processed"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def charts_dir_path(self) -> Path:
        """Resolve absolute path to charts output directory."""
        path = self.BASE_DIR / "output" / "charts"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def reports_dir_path(self) -> Path:
        """Resolve absolute path to reports output directory."""
        path = self.BASE_DIR / "output" / "reports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def sqlalchemy_url(self) -> str:
        """Generate SQLAlchemy connection URL for pandas read_sql."""
        return (
            f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
