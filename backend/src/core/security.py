import uuid
import time  # 🌟 Ensured time is imported for timestamp generation
from typing import Optional
from fastapi import Cookie, HTTPException, Depends, status
import redis
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.config import settings
from src.core.database import get_db

# Initialize centralized connection to high-speed Redis session memory
redis_store = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# Secure bcrypt adaptive hashing context configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Transforms a plain text password into a secure cryptographic hash."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares raw input text against a stored hash to confirm identity matches."""
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


async def verify_session(session_id: Optional[str] = Cookie(None)) -> str:
    """
    Lightweight Security Gate: Validates cookie presence and returns the raw 
    string 'user_id' from Redis. Ideal for high-performance indexing features (Marketplace).
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session credentials missing. Please login."
        )
        
    user_id = redis_store.get(session_id)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session expired or invalid. Please re-authenticate."
        )
        
    return user_id


# 🛡️ NEW: SLIDING-WINDOW BOT SHIELD INTEGRATED AS A REUSABLE DEPENDENCY
async def enforce_contact_rate_limiting(user_id: str = Depends(verify_session)) -> str:
    """
    Sliding-Window Protection: Blocks bad actors from farming peer contact phone numbers.
    Caps inquiries to a maximum of 10 contact view requests per rolling 1-hour window.
    """
    current_timestamp = int(time.time())
    user_key = f"rate:contact_harvest:{user_id}"
    one_hour_ago = current_timestamp - 3600
    
    # 1. Evacuate historical expired records from the sorted set
    redis_store.zremrangebyscore(user_key, 0, one_hour_ago)
    
    # 2. Extract active running request density within the remaining tracking scope
    active_requests_count = redis_store.zcard(user_key)
    
    if active_requests_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED, 
            detail="Security Lock: Exceeded hourly peer contact visibility allowances. Slow down."
        )
        
    # 3. Log the validated current access instance stamp
    redis_store.zadd(user_key, {str(current_timestamp): current_timestamp})
    redis_store.expire(user_key, 3600)  # Clean memory space automatically after 1 hour of inactivity
    
    return user_id  # Returns the validated user_id downstream to your router endpoints


async def get_current_user(
    session_id: Optional[str] = Cookie(None), 
    db: AsyncSession = Depends(get_db)
):
    """
    Full Profile Security Gate: Validates session status and fetches the complete 
    active User ORM row from PostgreSQL. Ideal for identity checks and account updates.
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session credentials missing. Please login."
        )
        
    user_id = redis_store.get(session_id)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session expired or invalid. Please re-authenticate."
        )
    
    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Malformed session identity signature."
        )

    # Inline import completely avoids circular dependency locks with users/models.py
    from src.modules.users.models import User
    
    result = await db.execute(select(User).filter(User.id == user_uuid))
    current_user = result.scalars().first()
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User session points to a profile that no longer exists."
        )
        
    return current_user