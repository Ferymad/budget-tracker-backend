from datetime import datetime, timedelta
from typing import Optional
import uuid
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.user import User
from app.models.refresh_token import RefreshToken

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token() -> str:
    """Create a secure refresh token"""
    return secrets.token_urlsafe(32)


async def create_refresh_token_db(db: AsyncSession, user_id: uuid.UUID) -> RefreshToken:
    """Create and store refresh token in database"""
    token = create_refresh_token()
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)
    return refresh_token


async def verify_refresh_token(db: AsyncSession, token: str) -> Optional[User]:
    """Verify refresh token and return associated user"""
    query = select(RefreshToken).where(
        RefreshToken.token == token,
        RefreshToken.expires_at > datetime.utcnow(),
        RefreshToken.is_revoked == False
    )
    result = await db.execute(query)
    refresh_token = result.scalar_one_or_none()
    
    if not refresh_token:
        return None
    
    # Get user
    user_query = select(User).where(User.id == refresh_token.user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    return user


async def revoke_refresh_token(db: AsyncSession, token: str):
    """Revoke a refresh token"""
    query = select(RefreshToken).where(RefreshToken.token == token)
    result = await db.execute(query)
    refresh_token = result.scalar_one_or_none()
    
    if refresh_token:
        refresh_token.is_revoked = True
        await db.commit()


async def revoke_all_user_tokens(db: AsyncSession, user_id: uuid.UUID):
    """Revoke all refresh tokens for a user"""
    query = select(RefreshToken).where(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    )
    result = await db.execute(query)
    tokens = result.scalars().all()
    
    for token in tokens:
        token.is_revoked = True
    
    await db.commit()


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user ID"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    
    return user