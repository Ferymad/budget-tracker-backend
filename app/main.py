from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.database import init_db
from app.api import auth, users, categories, transactions, budgets
from app.utils.exceptions import (
    BudgetTrackerException,
    budget_tracker_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Budget Tracker API",
    description="A comprehensive personal finance management API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(BudgetTrackerException, budget_tracker_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # Don't fail startup - let health check handle it


@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint"""
    return {
        "message": "Budget Tracker API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - no rate limiting for Railway"""
    try:
        # Test database connection
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "environment": settings.environment,
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "environment": settings.environment,
            "database": "disconnected",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )