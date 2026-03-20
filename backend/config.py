from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    jwt_secret: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
