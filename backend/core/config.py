"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    DATABASE_URL: str 

    ALLOWED_ORIGINS: str = ""

    OPENAI_API_KEY: str

    def __init__(self, **values):
        super().__init__(**values)
        if not self.DEBUG and not values.get("DATABASE_URL"):
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT")
            db_name = os.getenv("DB_NAME")
            self.DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os

# Debug: Print all environment variables that start with our expected names
print("=== DEBUG: Environment Variables ===")
for key, value in os.environ.items():
    if key in ['DATABASE_URL', 'OPENAI_API_KEY', 'API_PREFIX', 'DEBUG', 'ALLOWED_ORIGINS']:
        print(f"{key} = {'*' * len(value) if 'KEY' in key else value}")
print("=====================================")

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    DATABASE_URL: str = "temp_fallback"  # Add fallback to prevent crash
    ALLOWED_ORIGINS: str = ""
    OPENAI_API_KEY: str = "temp_fallback"  # Add fallback to prevent crash

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

# Debug: Print what actually got loaded
print("=== DEBUG: Loaded Settings ===")
print(f"API_PREFIX = {settings.API_PREFIX}")
print(f"DEBUG = {settings.DEBUG}")
print(f"DATABASE_URL = {'*' * 10 if settings.DATABASE_URL != 'temp_fallback' else 'temp_fallback'}")
print(f"ALLOWED_ORIGINS = {settings.ALLOWED_ORIGINS}")
print(f"OPENAI_API_KEY = {'*' * 10 if settings.OPENAI_API_KEY != 'temp_fallback' else 'temp_fallback'}")
print("===============================")