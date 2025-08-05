from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database - Railway will provide this via DATABASE_URL env var
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/budget_tracker"
    
    # JWT Settings - Railway will provide this via SECRET_KEY env var
    secret_key: str = "dev-secret-key-railway-will-override"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS - includes localhost for dev + Railway domains
    cors_origins: list = [
        "http://localhost:3000", 
        "http://localhost:8080",
        "https://*.railway.app"  # Railway will provide exact domains
    ]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Security
    bcrypt_rounds: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()