import os
import json
import uuid
from typing import List, Optional
from google import genai  # 🌟 Upgraded to modern SDK framework
from google.genai import types
from fastapi import UploadFile, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from geoalchemy2.functions import ST_Distance

from src.core.config import settings  # Centralized Pydantic settings layer
from src.modules.users.router import redis_store
from src.modules.users.models import User
from .models import Book

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🧠 Securely initialize the modern GenAI Client using Pydantic settings context
try:
    ai_client = genai.Client(api_key=settings.gemini_api_key)
except Exception as e:
    print(f"⚠️ [AI WARNING] Gemini Client initialization bypassed: {str(e)}")

# Structured Output Definition for Gemini Flash
class AIBookExtractionSchema(BaseModel):
    title: str = Field(description="The primary official title of the book, clean and capitalized.")
    author: str = Field(description="The full name of the author or authors of the book.")
    description: str = Field(description="A high-quality, concise 2-3 sentence summary of what the book is about.")
    genres: List[str] = Field(description="An array of 2-4 highly relevant category tags.")


async def generate_whatsapp_lead_message(book_data: dict) -> str:
    """
    Injects dynamic row characteristics straight into the centralized string layout
    tracked within your core settings system matrix.
    """
    try:
        # .format() automatically binds the keys matching the brackets {owner_name}, {title}, {price}
        return settings.marketplace_message_template.format(
            owner_name=book_data["owner_name"],
            title=book_data["title"],
            price=book_data["price"]
        )
    except Exception as e:
        # Graceful fallback copy standard template string if format key mismatches occur
        print(f"⚠️ Template rendering warning: {str(e)}")
        return f"Hello! I am interested in your book '{book_data['title']}' listed on BookMyBook. Is it still available?"


async def parse_book_photo_with_vision_ai(image_file: UploadFile) -> dict:
    """
    Streams raw image bytes directly to the upgraded Gemini Client
    and enforces a structured JSON payload response matching your schema.
    """
    try:
        image_bytes = await image_file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="The provided file stream is empty.")

        # Re-structured using explicit typing models from the modern SDK
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=image_file.content_type or "image/jpeg",
        )

        prompt = (
            "You are an expert OCR book cataloging assistant. Look closely at this book cover/spine photo. "
            "Extract the title, author, a high-quality concise description, and 2-4 category tags. "
            "If text is cutoff or unreadable, use your pre-trained domain knowledge to populate the fields accurately. "
            "You must return data matching the requested schema layout."
        )

        print("🧠 [AI VISION ACTIVE] Analyzing book cover with upgraded Gemini Client...")
        response = ai_client.models.generate_content(
            # change the model to the stable version of gemini 2.5 flash 
            # (isko 1.5 mat karna)
            model='gemini-2.5-flash',
            contents=[image_part, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIBookExtractionSchema,
                temperature=0.1  # Highly deterministic results
            ),
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
        raise HTTPException(status_code=400, detail="Unsupported media extension. Submit JPG, PNG, or WEBP.")

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

    # Triggers your async Celery Wishlist match check background process loop
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
    current_user: User,  # 👤 Injected full user model context cleanly from router dependency
    search: Optional[str],
    max_radius_km: Optional[float],
    page: int,
    limit: int
) -> dict:
    """
    Adaptive Exploration Engine: Toggles dynamically between high-speed PostGIS proximity sorting 
    (if location permissions exist) or an elegant reverse-chronological layout fallback.
    """
    user_id = str(current_user.id)
    normalized_search = search.strip().lower() if search else "all"
    radius_tag = f"r:{max_radius_km}" if max_radius_km else "r:any"
    cache_key = f"books_catalog:{user_id}:q:{normalized_search}:{radius_tag}:p:{page}:l:{limit}"
    
    # 1. Attempt High-Speed Redis Page Extraction
    cached_page_data = redis_store.get(cache_key)
    if cached_page_data:
        return json.loads(cached_page_data)

    # 2. Process Adaptive Location Metrics
    has_location = current_user.location is not None
    user_location_wkt = None

    if has_location:
        user_geo_cache = redis_store.get(f"user:location:{user_id}")
        if user_geo_cache:
            user_location_wkt = user_geo_cache
        else:
            user_location_wkt = await db.scalar(select(func.ST_AsText(current_user.location)))
            if user_location_wkt:
                redis_store.setex(f"user:location:{user_id}", 3600, user_location_wkt)
            else:
                has_location = False  # Graceful safety fallback if DB geometry extraction encounters nulls

    offset_value = (page - 1) * limit
    
    # 3. Construct Dynamic Column Attribute Mapping Arrays
    selections = [
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
    ]

    # 4. Compile the Query Framework Branches Dynamically
    if has_location:
        # PostGIS Proximity Execution Pathway
        distance_expression = ST_Distance(User.location, func.ST_GeomFromText(user_location_wkt, 4326))
        selections.append(distance_expression.label("distance_meters"))
        
        query = select(*selections).join(User, Book.owner_id == User.id).filter(Book.owner_id != current_user.id)
        
        if max_radius_km:
            query = query.filter(distance_expression <= (max_radius_km * 1000.0))
            
        query = query.order_by("distance_meters")
    else:
        # Location-Agnostic Pathway: Fallback to simple reverse-chronological indexing order
        query = select(*selections).join(User, Book.owner_id == User.id).filter(Book.owner_id != current_user.id)
        query = query.order_by(Book.id.desc())

    # 5. Apply Search String Filters if Present
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_pattern),
                Book.author.ilike(search_pattern),
                func.array_to_string(Book.genres, ",").ilike(search_pattern)
            )
        )
        
    query = query.offset(offset_value).limit(limit)
    result = await db.execute(query)
    rows = result.all()
    
    # 6. Parse and Build Response Payload Data
    catalog_books = []
    for row in rows:
        if has_location:
            distance_km = round(row.distance_meters / 1000.0, 2)
            distance_display = f"{distance_km} km away" if distance_km >= 0.1 else "On Campus"
        else:
            distance_display = "Location Hidden"  # User placeholder string when GPS onboarding is pending

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
            "campus_name": row.campus_name or "Campus Member",
            "distance_display": distance_display
        })
        
    response_payload = {
        "page": page,
        "limit": limit,
        "search_query": search,
        "max_radius_km": max_radius_km if has_location else None,
        "count": len(catalog_books),
        "books": catalog_books
    }
    
    # Cache compilation results in Redis memory for 2 minutes to keep hot reloads lightning-fast
    redis_store.setex(cache_key, 120, json.dumps(response_payload))
    return response_payload


async def get_book_details_by_id(db: AsyncSession, book_id: str) -> Optional[dict]:
    """
    Exhaustive Detail Lookups: Queries specific primary record rows, running explicit inner 
    joins against peer profiles to extract critical communication hooks (WhatsApp metrics).
    """
    try:
        book_uuid = uuid.UUID(str(book_id))
    except ValueError:
        return None  # Rejects syntactically broken strings early

    # Construct explicit select join to link peer attributes
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
            # kuch owner id ka scene tha , kyuki isme uski key thi nahi , to router.py me error aa raha tha 
            # to isko add kiya he
            Book.owner_id,
            User.name.label("owner_name"),
            User.mobile_number.label("owner_mobile"),
            User.area.label("campus_name")
        )
        .join(User, Book.owner_id == User.id)
        .filter(Book.id == book_uuid)
    )

    result = await db.execute(query)
    row = result.first()
    if not row:
        return None

    # Base payload structure mapping
    base_data = {
        "book_id": str(row.id),
        "title": row.title,
        "author": row.author,
        "description": row.description,
        "genres": row.genres or [],
        "price": float(row.price),
        "owner_note": row.owner_note,
        "image_url": f"http://localhost:8000{row.image_url}" if row.image_url else None,
        #idhar bhi same reson se add kiya he
        "owner_id": str(row.owner_id),
        "owner_name": row.owner_name,
        "owner_mobile": row.owner_mobile,
        "campus_name": row.campus_name or "Campus Member"
    }

    # 🎯 AUTOMATED METADATA HOOK: Build pre-filled chat parameters dynamically using our helper
    base_data["prefilled_text"] = await generate_whatsapp_lead_message(base_data)

    return base_data

# MERGE NOTE:
# Ek mybooks page ke liye function chaiye tha , to isko bhi merge karlena
async def get_user_inventory(db: AsyncSession, current_user_id: uuid.UUID) -> list[dict]:
    """
    Inventory Query: Fetches all books belonging to a specific user.
    """
    selections = [
        Book.id,
        Book.title,
        Book.author,
        Book.description,
        Book.genres,
        Book.image_url,
        Book.price,
        Book.owner_note,
        Book.created_at
    ]
    query = select(*selections).filter(Book.owner_id == current_user_id).order_by(Book.created_at.desc())
    result = await db.execute(query)
    rows = result.all()

    catalog_books = []
    for row in rows:
        catalog_books.append({
            "id": str(row.id),
            "title": row.title,
            "author": row.author,
            "description": row.description,
            "genres": row.genres,
            "image_url": f"http://localhost:8000{row.image_url}" if row.image_url else None,
            "price": float(row.price),
            "owner_note": row.owner_note,
            "created_at": row.created_at.isoformat() + "Z" if row.created_at else None
        })
    return catalog_books