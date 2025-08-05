from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database - Railway will provide this via DATABASE_URL env var
    database_url: str
    
    # JWT Settings - Railway will provide this via SECRET_KEY env var
    secret_key: str
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
    
    # Environment
    environment: str = "production"
    debug: bool = False
    
    # Security
    bcrypt_rounds: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()