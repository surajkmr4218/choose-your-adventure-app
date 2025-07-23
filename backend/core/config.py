from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    API_PREFIX = "/api"
    DEBUG = False

    DATABASE_URL = None  

    ALLOWED_ORIGINS = ""
    OPENAI_API_KEY = None  

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v):
        return v.split(",") if v else []
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

