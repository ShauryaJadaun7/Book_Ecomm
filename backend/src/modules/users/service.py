from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User

# Pre-mapped Campus Location Coordinates to maintain high performance
CAMPUS_GEO_DICTIONARY: Dict[str, Dict[str, float]] = {
    "adani university": {"lon": 72.5714, "lat": 23.0225},
    "daiict": {"lon": 72.6835, "lat": 23.1878},
    "nirma university": {"lon": 72.5412, "lat": 23.1247}
}

def get_wkt_point_from_area(area: str) -> str:
    normalized_area = area.lower().strip()
    coords = CAMPUS_GEO_DICTIONARY.get(normalized_area, {"lon": 72.5714, "lat": 23.0225}) # Fallback to default campus coords
    return f"POINT({coords['lon']} {coords['lat']})"

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_new_user(db: AsyncSession, name: str, email: str, area: str, pincode: str, auth_provider: str = "email", oauth_id: Optional[str] = None) -> User:
    wkt_location = get_wkt_point_from_area(area)
    
    user = User(
        name=name,
        email=email,
        area=area,
        pincode=pincode,
        auth_provider=auth_provider,
        oauth_id=oauth_id,
        #location=wkt_location
    )
    db.add(user)
    await db.flush()
    return user