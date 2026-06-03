from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.modules.users import service
import redis
from src.core.config import settings

redis_store = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_current_user(session_id: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated: No session cookie")
        
    user_id = redis_store.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated: Session expired or invalid")
        
    user = await service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated: User not found")
        
    return user
