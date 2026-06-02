import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from geoalchemy2.functions import ST_Distance

from src.core.database import get_db
from src.modules.users.router import redis_store
from src.modules.users.models import User
from .models import Book

router = APIRouter(prefix="/books", tags=["Books Exploration Catalog"])

@router.get("/book")
async def get_and_search_books(
    search: Optional[str] = Query(None, description="Search filters for matching title/author strings"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    session_id: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    # 1. Verification Gate against Identity Cluster Cache
    if not session_id:
        raise HTTPException(status_code=401, detail="Session credentials missing.")
        
    user_id = redis_store.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")

    # 2. Extract Data from Memory Tier using Normalization Tags
    normalized_search = search.strip().lower() if search else "all"
    cache_key = f"books_catalog:{user_id}:q:{normalized_search}:p:{page}:l:{limit}"
    
    cached_page_data = redis_store.get(cache_key)
    if cached_page_data:
        return json.loads(cached_page_data)

    # 3. Resolve Geographical Coordinates of the Target User Profile
    user_geo_cache = redis_store.get(f"user:location:{user_id}")
    if user_geo_cache:
        user_location_wkt = user_geo_cache
    else:
        user_record = await db.get(User, user_id)
        if not user_record:
            raise HTTPException(status_code=404, detail="User transaction state identity missing.")
        user_location_wkt = await db.scalar(select(func.ST_AsText(user_record.location)))
        redis_store.setex(f"user:location:{user_id}", 3600, user_location_wkt)

    # 4. Construct Spatial Math Computation Layout Parameters
    distance_expression = ST_Distance(User.location, func.ST_GeomFromText(user_location_wkt, 4326))
    offset_value = (page - 1) * limit
    
    query = (
        select(
            Book.id,
            Book.title,
            Book.author,
            Book.description,
            Book.genres,
            Book.image_url,
            User.name.label("owner_name"),
            User.area.label("campus_name"),
            distance_expression.label("distance_meters")
        )
        .join(User, Book.owner_id == User.id)
        .filter(Book.owner_id != user_id)  # Avoid returning a user's own listings back to them
    )
    
    # 5. Inject Full-Text Wildcard Filtering Constraints
    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
        )
        
    # Apply spatial sequence sorting, skipping page intervals, and slicing limits
    query = query.order_by("distance_meters").offset(offset_value).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    # 6. Restructure Response Rows cleanly for Client Render Processing
    catalog_books = []
    for row in rows:
        distance_km = round(row.distance_meters / 1000.0, 2)
        catalog_books.append({
            "book_id": str(row.id),
            "title": row.title,
            "author": row.author,
            "description": row.description,
            "genres": row.genres or [],
            "image_url": f"http://localhost:8000{row.image_url}" if row.image_url else None,
            "owner_name": row.owner_name,
            "campus_name": row.campus_name,
            "distance_display": f"{distance_km} km away" if distance_km >= 0.1 else "On Campus"
        })
        
    response_payload = {
        "page": page,
        "limit": limit,
        "search_query": search,
        "count": len(catalog_books),
        "books": catalog_books
    }
    
    # 7. Commit calculated response frame out to Redis with a short 2-minute expiration
    redis_store.setex(cache_key, 120, json.dumps(response_payload))
    
    return response_payload