import os
import json
import uuid
from typing import List, Optional
import google.generativeai as genai
from fastapi import UploadFile, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from geoalchemy2.functions import ST_Distance

from src.modules.users.router import redis_store
from src.modules.users.models import User
from .models import Book

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🧠 Configure Gemini internally within the module framework
if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
else:
    print("[!] [AI WARNING] GEMINI_API_KEY is not defined or is a dummy value in your environment configs.")

# 🚨 Structured Output Definition for Gemini Flash
class AIBookExtractionSchema(BaseModel):
    title: str = Field(description="The primary official title of the book, clean and capitalized.")
    author: str = Field(description="The full name of the author or authors of the book.")
    description: str = Field(description="A high-quality, concise 2-3 sentence summary of what the book is about.")
    genres: List[str] = Field(description="An array of 2-4 highly relevant category tags (e.g., 'Engineering', 'Economics', 'Programming').")


async def parse_book_photo_with_vision_ai(image_file: UploadFile) -> dict:
    """
    Streams the raw uploaded image bytes directly to Gemini Flash Vision 
    and forces a strict JSON response fitting our Pydantic schema.
    """
    try:
        # Read file stream bytes
        image_bytes = await image_file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="The provided file stream is empty.")

        image_part = {
            "mime_type": image_file.content_type or "image/jpeg",
            "data": image_bytes
        }

        model = genai.GenerativeModel(model_name="gemini-2.5-flash")

        prompt = (
            "You are an expert OCR book cataloging assistant. Look closely at this book cover/spine photo. "
            "Extract the title, author, a high-quality concise description, and 2-4 category tags. "
            "If text is cutoff or unreadable, use your pre-trained domain knowledge to populate the fields accurately. "
            "You must return data matching the requested schema layout."
        )

        print("🧠 [AI VISION ACTIVE] Processing book cover frame with Gemini...")
        response = model.generate_content(
            [image_part, prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=AIBookExtractionSchema,
                temperature=0.1  # Low temperature makes output highly deterministic and accurate
            )
        )

        extracted_json = json.loads(response.text)
        print(f"✨ [AI PARSE SUCCESSFUL] Extracted: '{extracted_json.get('title')}'")
        
        return {
            "status": "success",
            "suggested_data": extracted_json
        }

    except Exception as error:
        print(f"❌ [AI VISION CRASH] Internal processing breakdown: {str(error)}")
        raise HTTPException(status_code=500, detail=f"AI cover analysis failed: {str(error)}")
    finally:
        # Crucial: Reset the file stream pointer so the file can be read again if needed
        await image_file.seek(0)


async def create_new_book_listing(
    db: AsyncSession,
    user_id: str,
    title: str,
    author: str,
    description: Optional[str],
    genres: Optional[str],
    price: float,
    owner_note: Optional[str],
    image: UploadFile
) -> dict:
    """
    Handles file saving, transforms text parameters into standard types,
    commits to Postgres, and flushes historical cache frames from Redis.
    """
    file_extension = os.path.splitext(image.filename)[1].lower()
    if file_extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Unsupported media extension. Submit JPG or PNG.")

    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_save_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        contents = await image.read()
        with open(file_save_path, "wb") as storage_file:
            storage_file.write(contents)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"File disk save execution failure: {str(error)}")
    finally:
        await image.close()

    genre_list = [g.strip() for g in genres.split(",")] if genres else []
    web_accessible_url = f"/static/uploads/{unique_filename}"
    
    new_book = Book(
        title=title.strip(),
        author=author.strip(),
        description=description.strip() if description else None,
        genres=genre_list,
        image_url=web_accessible_url,
        price=max(0.0, price),
        owner_note=owner_note.strip() if owner_note else None,
        owner_id=uuid.UUID(user_id)
    )
    
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)

    # Invalidate old redis search cache instances automatically
    try:
        cache_keys = redis_store.keys("books_catalog:*")
        if cache_keys:
            redis_store.delete(*cache_keys)
    except Exception as e:
        print(f"⚠️ Cache tracking warning: {str(e)}")

    # 🚀 Triggers your async Celery Wishlist match check immediately background process loop
    from src.modules.wishlist.tasks import check_wishlist_matches_task
    check_wishlist_matches_task.delay(
        book_id=str(new_book.id),
        book_title=new_book.title,
        uploader_id=str(new_book.owner_id)
    )

    return {
        "status": "success",
        "message": "Asset successfully published into campus catalog index.",
        "book_id": str(new_book.id),
        "title": new_book.title
    }


async def get_distance_sorted_catalog(
    db: AsyncSession,
    user_id: str,
    search: Optional[str],
    max_radius_km: Optional[float],
    page: int,
    limit: int
) -> dict:
    normalized_search = search.strip().lower() if search else "all"
    radius_tag = f"r:{max_radius_km}" if max_radius_km else "r:any"
    cache_key = f"books_catalog:{user_id}:q:{normalized_search}:{radius_tag}:p:{page}:l:{limit}"
    
    cached_page_data = redis_store.get(cache_key)
    if cached_page_data:
        return json.loads(cached_page_data)

    user_geo_cache = redis_store.get(f"user:location:{user_id}")
    if user_geo_cache:
        user_location_wkt = user_geo_cache
    else:
        user_record = await db.get(User, uuid.UUID(user_id))
        if not user_record:
            return {"page": page, "limit": limit, "books": []}
        user_location_wkt = await db.scalar(select(func.ST_AsText(user_record.location)))
        redis_store.setex(f"user:location:{user_id}", 3600, user_location_wkt)

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
            Book.price,
            Book.owner_note,
            User.name.label("owner_name"),
            User.area.label("campus_name"),
            distance_expression.label("distance_meters")
        )
        .join(User, Book.owner_id == User.id)
        .filter(Book.owner_id != uuid.UUID(user_id))
    )
    
    if max_radius_km:
        query = query.filter(distance_expression <= (max_radius_km * 1000.0))
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_pattern),
                Book.author.ilike(search_pattern),
                func.array_to_string(Book.genres, ",").ilike(search_pattern)
            )
        )
        
    query = query.order_by("distance_meters").offset(offset_value).limit(limit)
    result = await db.execute(query)
    rows = result.all()
    
    catalog_books = []
    for row in rows:
        distance_km = round(row.distance_meters / 1000.0, 2)
        catalog_books.append({
            "book_id": str(row.id),
            "title": row.title,
            "author": row.author,
            "description": row.description,
            "genres": row.genres or [],
            "price": row.price,
            "owner_note": row.owner_note,
            "image_url": f"http://localhost:8000{row.image_url}" if row.image_url else None,
            "owner_name": row.owner_name,
            "campus_name": row.campus_name,
            "distance_display": f"{distance_km} km away" if distance_km >= 0.1 else "On Campus"
        })
        
    response_payload = {
        "page": page,
        "limit": limit,
        "search_query": search,
        "max_radius_km": max_radius_km,
        "count": len(catalog_books),
        "books": catalog_books
    }
    
    redis_store.setex(cache_key, 120, json.dumps(response_payload))
    return response_payload