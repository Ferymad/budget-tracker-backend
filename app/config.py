from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database - Railway will provide DATABASE_URL, fallback for local dev
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/budget_tracker"
    
    # JWT Settings - Railway will provide SECRET_KEY, secure fallback 
    secret_key: str = "railway-deployment-will-override-this-secret-key-via-env-var"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS - includes localhost for dev + Railway domains
    cors_origins: list = [
        "http://localhost:3000", 
        "http://localhost:8080",
        "https://budget-tracker-frontend-production.up.railway.app",
        "*"  # Allow all origins for Railway deployment
    ]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Environment - Auto-detect Railway vs local
    environment: str = "production" if "RAILWAY_ENVIRONMENT" in __import__('os').environ else "development"
    debug: bool = "RAILWAY_ENVIRONMENT" not in __import__('os').environ
    
    # Security
    bcrypt_rounds: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()