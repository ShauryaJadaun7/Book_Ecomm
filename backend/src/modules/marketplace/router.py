from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.users.router import redis_store
from . import service

router = APIRouter(prefix="/books", tags=["Books Exploration Catalog"])

@router.get("/book")
async def get_and_search_books(
    search: Optional[str] = Query(None, description="Search filters for matching title/author strings"),
    max_radius: Optional[float] = Query(None, alias="max_radius_km", description="Filter within distance radius"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    session_id: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    if not session_id:
        raise HTTPException(status_code=401, detail="Session credentials missing.")
    user_id = redis_store.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")

    return await service.get_distance_sorted_catalog(
        db=db, user_id=user_id, search=search, max_radius_km=max_radius, page=page, limit=limit
    )


@router.post("/scan")
async def scan_and_parse_book_cover(
    image: UploadFile = File(..., description="The binary photo capturing the book's front cover or spine detail"),
    session_id: Optional[str] = Cookie(None)
):
    """
    Performs high-speed OCR text extraction on image streams using AI Vision models.
    Returns structured parameters to pre-populate frontend form elements.
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Session credentials missing.")
    user_id = redis_store.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")

    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid format. Supply a clean JPEG, PNG, or WEBP image source.")

    return await service.parse_book_photo_with_vision_ai(image_file=image)


@router.post("/upload")
async def upload_new_book(
    title: str = Form(...),
    author: str = Form(...),
    description: Optional[str] = Form(None),
    genres: Optional[str] = Form(None),
    price: float = Form(..., ge=0.0),
    owner_note: Optional[str] = Form(None, description="Barter preferences or notes for peers"),
    image: UploadFile = File(...),
    session_id: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    if not session_id:
        raise HTTPException(status_code=401, detail="Session credentials missing.")
    user_id = redis_store.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")

    import traceback
    try:
        return await service.create_new_book_listing(
            db=db,
            user_id=user_id,
            title=title,
            author=author,
            description=description,
            genres=genres,
            price=price,
            owner_note=owner_note,
            image=image
        )
    except Exception as e:
        error_details = traceback.format_exc()
        print("INTERNAL CRASH:", error_details)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}\n{error_details}")