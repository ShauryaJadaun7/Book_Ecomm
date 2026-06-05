import uuid
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Performs a case-normalized database search for an active account profile."""
    if not email:
        return None
    result = await db.execute(select(User).filter(User.email == email.strip().lower()))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Retrieves an individual account entry matching the UUID primary identifier."""
    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        return None
    result = await db.execute(select(User).filter(User.id == user_uuid))
    return result.scalars().first()


async def create_new_user(
    db: AsyncSession, 
    name: str, 
    email: str, 
    auth_provider: str = "email", 
    password_hash: Optional[str] = None, 
    oauth_id: Optional[str] = None
) -> User:
    """
    GitHub-Style Onboarding Creator: Spawns a location-agnostic account shell profile.
    Initializes spatial geometries and onboarding metadata fields as null.
    """
    user = User(
        name=name.strip(),
        email=email.strip().lower(),
        auth_provider=auth_provider,
        password_hash=password_hash,
        oauth_id=oauth_id,
        area=None,          # Captured post-login via Profile
        pincode=None,       # Captured post-login via Profile
        location=None,      # Captured post-login via Profile (GPS)
        mobile_number=None, # Captured post-login via Profile
        bio=None,
        favorite_genres=None
    )
    db.add(user)
    await db.flush()  # Allocate user.id without terminating the transaction block
    return user


async def update_user(db: AsyncSession, user_id: str, **kwargs) -> Optional[User]:
    """
    Dynamic Profile Updater: Applies patches to active attributes.
    🎯 GPS METADATA INTEGRATION: If latitude and longitude are supplied, this hook 
    dynamically binds them into an explicit Extended WKT Point string for PostGIS tracking.
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
        
    # Intercept and map raw GPS tracking properties sent from the device
    latitude = kwargs.pop("latitude", None)
    longitude = kwargs.pop("longitude", None)
    
    if latitude is not None and longitude is not None:
        # Construct clean, standard PostGIS EWKT point representation (Format: POINT(longitude latitude))
        kwargs["location"] = f"SRID=4326;POINT({float(longitude)} {float(latitude)})"

    # Map remaining dynamic parameters onto the target user record instance
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
        
    await db.commit()
    await db.refresh(user)
    return user