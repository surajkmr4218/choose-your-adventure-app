from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    
    # Railway automatically provides DATABASE_URL for PostgreSQL
    DATABASE_URL: str = "sqlite:///./database.db"  # Fallback for local dev
    ALLOWED_ORIGINS: str = "*"  # Default to allow all
    OPENAI_API_KEY: str = ""  # Will be set in Railway
    
    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        if not v:
            return ["*"]
        return [origin.strip() for origin in v.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()