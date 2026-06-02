import uuid
import random
from typing import Optional
import httpx
import redis
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.config import settings  # <-- Imports centralized settings
from .schemas import SendOTPRequest, VerifyOTPRequest, GoogleAuthRequest, UserProfileResponse
from . import service

# Connect dynamically using your .env configuration string
redis_store = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

router = APIRouter(prefix="/auth", tags=["Authentication Pipeline"])

@router.post("/send-otp")
async def send_otp(payload: SendOTPRequest):
    generated_otp = str(random.randint(100000, 999999))
    
    # Cache parameters safely inside transactional memory structures (5-minute TTL)
    redis_store.setex(f"otp:{payload.email}", 300, generated_otp)
    
    # Cache onboarding demographic parameters so they map cleanly upon verification pass
    redis_store.setex(f"signup_cache:{payload.email}:name", 300, payload.name)
    redis_store.setex(f"signup_cache:{payload.email}:area", 300, payload.area)
    redis_store.setex(f"signup_cache:{payload.email}:pincode", 300, payload.pincode)
    
    # Hand off execution thread over to Celery worker cluster immediately
    from worker.tasks.auth_tasks import send_otp_email_task
    send_otp_email_task.delay(payload.email, generated_otp)
    
    return {
        "status": "success",
        "message": "OTP challenge successfully generated and shifted to background queue.",
        "dev_bypass_token": generated_otp  # Extracted for straightforward Postman automation scripting
    }

@router.post("/verify-otp")
async def verify_otp(payload: VerifyOTPRequest, response: Response, db: AsyncSession = Depends(get_db)):
    cached_otp = redis_store.get(f"otp:{payload.email}")
    
    if not cached_otp or cached_otp != payload.otp:
        raise HTTPException(status_code=400, detail="Provided authorization token credentials mismatch or expired.")
        
    redis_store.delete(f"otp:{payload.email}")
    
    user = await service.get_user_by_email(db, payload.email)
    
    if not user:
        name = redis_store.get(f"signup_cache:{payload.email}:name") or "User"
        area = redis_store.get(f"signup_cache:{payload.email}:area") or "Adani University"
        pincode = redis_store.get(f"signup_cache:{payload.email}:pincode") or "382421"
        
        user = await service.create_new_user(db, name, payload.email, area, pincode, auth_provider="email")
        
        # Cleanup temporary signup cache keys
        redis_store.delete(f"signup_cache:{payload.email}:name")
        redis_store.delete(f"signup_cache:{payload.email}:area")
        redis_store.delete(f"signup_cache:{payload.email}:pincode")

    # Issue production-ready secure session token mapping block (30-day lifecycle window)
    assigned_session_uuid = f"sess_{uuid.uuid4().hex}"
    redis_store.setex(assigned_session_uuid, 2592000, str(user.id))
    
    response.set_cookie(
        key="session_id",
        value=assigned_session_uuid,
        httponly=True,
        max_age=2592000,
        samesite="lax",
        secure=False  # Switch setting to True inside live target production HTTPS pipelines
    )
    return {"status": "authorized", "user_id": str(user.id)}

@router.post("/google")
async def google_oauth_verify(payload: GoogleAuthRequest, response: Response, db: AsyncSession = Depends(get_db)):
    verification_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.token}"
    
    async with httpx.AsyncClient() as async_client:
        google_stream = await async_client.get(verification_url)
        
    if google_stream.status_code != 200:
        raise HTTPException(status_code=401, detail="Google authentication signature handshake dropped validation.")
        
    identity_claims = google_stream.json()
    extracted_email = identity_claims.get("email")
    extracted_name = identity_claims.get("name", "Google Explorer")
    google_unique_id = identity_claims.get("sub")
    
    user = await service.get_user_by_email(db, extracted_email)
    
    if not user:
        # Fixed the NameError bug here by changing google_id to google_unique_id
        user = await service.create_new_user(
            db, extracted_name, extracted_email, payload.area, payload.pincode, 
            auth_provider="google", oauth_id=google_unique_id
        )
        
    assigned_session_uuid = f"sess_{uuid.uuid4().hex}"
    redis_store.setex(assigned_session_uuid, 2592000, str(user.id))
    
    response.set_cookie(
        key="session_id",
        value=assigned_session_uuid,
        httponly=True,
        max_age=2592000,
        samesite="lax",
        secure=False
    )
    return {"status": "authorized", "user_id": str(user.id)}

@router.post("/logout")
async def term_session(response: Response, session_id: Optional[str] = Cookie(None)):
    if session_id:
        redis_store.delete(session_id)
    response.delete_cookie(key="session_id")
    return {"status": "terminated", "message": "Client session removed from backend register stores."}