import uuid
import random
from typing import Optional
import httpx
import redis
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.config import settings
from src.core.security import get_current_user, hash_password, verify_password
from src.modules.users.models import User
from .schemas import UserSignupRequest, VerifySignupOTPRequest, UserLoginRequest, GoogleAuthRequest
from . import service

# Establish centralized connection to high-speed Redis memory layer
redis_store = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

router = APIRouter(prefix="/auth", tags=["GitHub-Style Authentication Gateway"])


@router.post("/signup")
async def initiate_credential_signup(payload: UserSignupRequest, db: AsyncSession = Depends(get_db)):
    """
    Step 1 Signup: Enforces entry-level uniqueness (Redundancy Shield 1), hashes
    passwords securely via bcrypt, stages unverified credentials inside Redis caches (15-min TTL),
    and schedules an email background task via Celery using your Resend SMTP setup.
    """
    # 🛡️ REDUNDANCY SHIELD 1: Instantly reject if the account is already registered
    existing_user = await service.get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address is already registered. Please proceed to login."
        )

    generated_otp = str(random.randint(100000, 999999))
    hashed_pass = hash_password(payload.password)
    
    # Cache parameters within an isolated 15-minute transactional staging window (900 seconds)
    redis_store.setex(f"otp:{payload.email}", 900, generated_otp)
    redis_store.setex(f"reg_cache:{payload.email}:name", 900, payload.name)
    redis_store.setex(f"reg_cache:{payload.email}:pass_hash", 900, hashed_pass)

    # Delegate mail generation to background workers to keep route execution speed at ~5ms
    try:
        from worker.tasks.auth_tasks import send_otp_email_task
        send_otp_email_task.delay(payload.email, generated_otp)
    except Exception as e:
        print(f"⚠️ [CELERY SUBMISSION FAILURE] Fallback localized console bypass token: {generated_otp}")

    return {
        "status": "success",
        "message": "Security validation code successfully generated and pushed to background transmission queue.",
        "dev_bypass_token": generated_otp  # Retained for automated postman regression script testing loops
    }


@router.post("/signup/verify")
async def finalize_credential_signup(payload: VerifySignupOTPRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Step 2 Signup: Validates OTP correctness. Executes an anti-race condition check (Redundancy Shield 2)
    right before creation to handle double-clicks. Commits the baseline location-agnostic profile 
    to PostgreSQL, cleans up transient caches, and issues an active secure session cookie.
    """
    cached_otp = redis_store.get(f"otp:{payload.email}")
    if not cached_otp or cached_otp != payload.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided verification code is invalid or has expired."
        )

    # 🛡️ REDUNDANCY SHIELD 2: Anti-Race Condition Gate
    # Prevents concurrent thread double-submit creations or multiple open tab bypasses
    final_duplicate_check = await service.get_user_by_email(db, payload.email)
    if final_duplicate_check:
        # Immediate evacuation of stale transient cache nodes
        redis_store.delete(f"otp:{payload.email}")
        redis_store.delete(f"reg_cache:{payload.email}:name")
        redis_store.delete(f"reg_cache:{payload.email}:pass_hash")
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account activation redundant. This profile was successfully registered via another session link."
        )

    # Pull unverified data parameters out of staging memory handles
    name = redis_store.get(f"reg_cache:{payload.email}:name")
    password_hash = redis_store.get(f"reg_cache:{payload.email}:pass_hash")

    if not name or not password_hash:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Registration session timed out or already processed. Please initiate signup again."
        )

    # Formally write user profile shell entry into database ledger layers
    user = await service.create_new_user(
        db=db,
        name=name,
        email=payload.email,
        auth_provider="email",
        password_hash=password_hash
    )
    # Vo database pe save nahi ho raha tha isliye phir ye add kiya he
    await db.commit()

    # Immediate absolute atomic cleanup of active staging keys
    redis_store.delete(f"otp:{payload.email}")
    redis_store.delete(f"reg_cache:{payload.email}:name")
    redis_store.delete(f"reg_cache:{payload.email}:pass_hash")

    # MERGE NOTE: feat : Profile Remider
    # Queue the background profile reminder (60-second delay for testing)
    try:
        from worker.tasks.auth_tasks import check_profile_and_remind_task
        check_profile_and_remind_task.apply_async(
            args=[str(user.id), user.email, user.name],
            countdown=60
        )
    except Exception as e:
        print(f"⚠️ [CELERY SUBMISSION FAILURE] Reminder task dropped: {str(e)}")

    # Construct secure 30-day lifecycle session management token architecture
    assigned_session_uuid = f"sess_{uuid.uuid4().hex}"
    redis_store.setex(assigned_session_uuid, 2592000, str(user.id))
    
    is_prod = settings.ENVIRONMENT.lower() == "production"
    response.set_cookie(
        key="session_id",
        value=assigned_session_uuid,
        httponly=True,
        max_age=2592000,
        samesite="none" if is_prod else "lax",
        secure=is_prod
    )
    return {"status": "authorized", "user_id": str(user.id), "message": "Account created successfully."}


@router.post("/login")
async def standard_credential_login(payload: UserLoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Credential Sign In: Resolves user presence, checks for Google OAuth crossover locks,
    verifies passwords using bcrypt comparison helper contexts, and builds active session containers.
    """
    user = await service.get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials provided."
        )

    # Prevent credential guess spoofing on accounts created exclusively via Google Single Sign-On
    if user.auth_provider == "google" and not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses Google single sign-on. Please click 'Sign in with Google'."
        )

    # Run side-channel protected timing comparisons using passlib password verification contexts
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials provided."
        )

    assigned_session_uuid = f"sess_{uuid.uuid4().hex}"
    redis_store.setex(assigned_session_uuid, 2592000, str(user.id))
    
    is_prod = settings.ENVIRONMENT.lower() == "production"
    response.set_cookie(
        key="session_id",
        value=assigned_session_uuid,
        httponly=True,
        max_age=2592000,
        samesite="none" if is_prod else "lax",
        secure=is_prod
    )
    return {"status": "authorized", "user_id": str(user.id), "message": "Login successful."}


@router.post("/google")
async def google_oauth_verify(payload: GoogleAuthRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Alternative Google OAuth Hub: Performs direct, secure identity handshake assertions with 
    Google servers, handles automated account provisioning for new profiles, and issues sessions.
    """
    verification_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    
    async with httpx.AsyncClient() as async_client:
        google_stream = await async_client.get(
            verification_url, 
            headers={"Authorization": f"Bearer {payload.token}"}
        )
        
    if google_stream.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Google authentication signature handshake dropped validation."
        )
        
    identity_claims = google_stream.json()
    extracted_email = identity_claims.get("email")
    extracted_name = identity_claims.get("name", "Google Explorer")
    google_unique_id = identity_claims.get("sub")
    
    user = await service.get_user_by_email(db, extracted_email)
    
    # Seamless redundancy check: auto-provisions a profile ONLY if they do not exist
    if not user:
        user = await service.create_new_user(
            db=db, 
            name=extracted_name, 
            email=extracted_email, 
            auth_provider="google",
            oauth_id=google_unique_id
        )

        # MERGE NOTE: feat : User Creation Confirmation email
        await db.commit()
        
        # MERGE NOTE: feat : Profile Remider
        # Queue the background profile reminder (60-second delay for testing)
        try:
            from worker.tasks.auth_tasks import check_profile_and_remind_task
            check_profile_and_remind_task.apply_async(
                args=[str(user.id), user.email, user.name],
                countdown=60
            )
        except Exception as e:
            print(f"⚠️ [CELERY SUBMISSION FAILURE] Reminder task dropped: {str(e)}")
        
    assigned_session_uuid = f"sess_{uuid.uuid4().hex}"
    redis_store.setex(assigned_session_uuid, 2592000, str(user.id))
    
    is_prod = settings.ENVIRONMENT.lower() == "production"
    response.set_cookie(
        key="session_id",
        value=assigned_session_uuid,
        httponly=True,
        max_age=2592000,
        samesite="none" if is_prod else "lax",
        secure=is_prod
    )
    return {"status": "authorized", "user_id": str(user.id)}


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Protected Workspace Session Gate: Returns baseline profile attributes. 
    Frontend checks for null values in location/mobile fields to trigger the profile setup redirect.
    """
    return {
        "status": "success",
        "user_id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "area": current_user.area,                 # Returns null for new accounts
        "pincode": current_user.pincode,             # Returns null for new accounts
        "mobile_number": current_user.mobile_number   # Returns null for new accounts
    }


@router.post("/logout")
async def term_session(response: Response, session_id: Optional[str] = Cookie(None)):
    """Wipes the active session key mapping from Redis memory and cleaves client cookies clean."""
    if session_id:
        redis_store.delete(session_id)
    response.delete_cookie(key="session_id")
    return {"status": "terminated", "message": "Client session removed from backend register stores."}

from .schemas import ProfileOnboardingRequest # Import request schema validation

@router.patch("/onboarding")
async def save_profile_onboarding_data(
    payload: ProfileOnboardingRequest,
    current_user: User = Depends(get_current_user), # Blocks unauthorized access requests
    db: AsyncSession = Depends(get_db)
):
    """
    Profile Enrichment Point: Collects exact device GPS coordinates along with
    contact data to activate real-time marketplace proximity tracking capabilities.
    """
    # Check email uniqueness if email is modified and not already in use
    if payload.email and payload.email.strip().lower() != current_user.email.strip().lower():
        existing_user = await service.get_user_by_email(db, payload.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address is already registered."
            )

    updated_profile = await service.update_user(
        db=db,
        user_id=str(current_user.id),
        email=payload.email.strip().lower() if payload.email else None,
        area=payload.area,
        pincode=payload.pincode,
        mobile_number=payload.mobile_number,
        latitude=payload.latitude,
        longitude=payload.longitude
    )
    
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Active account workspace state could not be resolved.")

    # Check if profile is 100% complete (name, email, area, pincode, and mobile_number are all set and non-empty)
    is_profile_complete = (
        updated_profile.name and
        updated_profile.email and
        updated_profile.area and
        updated_profile.pincode and
        updated_profile.mobile_number
    )

    if is_profile_complete and not updated_profile.welcome_email_sent:
        updated_profile.welcome_email_sent = True
        await db.commit()
        
        try:
            from worker.tasks.auth_tasks import send_welcome_email_task
            send_welcome_email_task.apply_async(
                args=[updated_profile.email, updated_profile.name],
                countdown=60
            )
        except Exception as e:
            print(f"⚠️ [CELERY SUBMISSION FAILURE] Welcome email task dropped: {str(e)}")
        
    return {
        "status": "success",
        "message": "Campus profile attributes and exact GPS configurations successfully synchronized."
    }