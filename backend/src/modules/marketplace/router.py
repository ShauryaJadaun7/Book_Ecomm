from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_session  # 🔐 Import your centralized dependency injection gate
from src.modules.users import service as users_service  # Resolve active PostgreSQL profiles
from . import service

router = APIRouter(prefix="/books", tags=["Books Exploration Catalog"])


@router.get("/book")
async def get_and_search_books(
    search: Optional[str] = Query(None, description="Search filters for matching title/author strings"),
    max_radius: Optional[float] = Query(None, alias="max_radius_km", description="Filter within distance radius"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    user_id: str = Depends(verify_session),  # 🎯 Verified automatically; throws immediate 401 downstream if missing/expired
    db: AsyncSession = Depends(get_db)
):
    """
    Exploration Feed: Fetches books dynamically. Passes the user object downstream 
    to toggle between PostGIS proximity tracking or chronological fallback layouts.
    """
    # 👤 Fetch the full user model to pass down to the catalog query compiler using injected user_id
    current_user = await users_service.get_user_by_id(db, user_id)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User workspace profile not found.")

    return await service.get_distance_sorted_catalog(
        db=db, 
        current_user=current_user, 
        search=search, 
        max_radius_km=max_radius, 
        page=page, 
        limit=limit
    )

# MERGE NOTE:
# bhai ye ek new route chaiye tha my books ke liye isliye add kiya
@router.get("/my-books")
async def get_my_inventory(
    user_id: str = Depends(verify_session),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves all books uploaded by the currently authenticated user.
    """
    current_user = await users_service.get_user_by_id(db, user_id)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found.")

    return await service.get_user_inventory(db, current_user_id=current_user.id)


@router.post("/scan")
async def scan_and_parse_book_cover(
    image: UploadFile = File(..., description="The binary photo capturing the book's front cover or spine detail"),
    user_id: str = Depends(verify_session)  # 🎯 Protected, rejects unauthorized calls before executing business logic
):
    """
    Performs high-speed OCR text extraction on image streams using AI Vision models.
    Returns structured parameters to pre-populate frontend form elements.
    """
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid format. Supply a clean JPEG, PNG, or WEBP image source.")

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
    user_id: str = Depends(verify_session),  # 🎯 Protected session extraction loop
    db: AsyncSession = Depends(get_db)
):
    """
    Marketplace Listing Gate: Enforces profile validation. Users cannot list 
    an item for exchange unless their core profile and GPS tracking layers are activated.
    """
    # 👤 Resolve account structure validation properties
    current_user = await users_service.get_user_by_id(db, user_id)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User workspace profile not found.")

    # 🛡️ DEFENSIVE GUARD: Block upload if location coordinates do not exist yet (GPS missing)
    if current_user.location is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile onboarding incomplete. Please provide your campus details and enable GPS location access before listing items on the marketplace."
        )

    import traceback
    try:
        return await service.create_new_book_listing(
            db=db,
            user_id=str(current_user.id),
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


@router.post("/{book_id}/click-interest", status_code=200)
async def log_and_generate_whatsapp_lead(
    book_id: str,
    user_id: str = Depends(verify_session),
    db: AsyncSession = Depends(get_db)
):
    """
    Lead Generator Analytics: Logs the expression of interest transaction event 
    into your ledger and returns sanitized click-to-chat redirection configuration elements.
    """
    # 1. Fetch book and assert existence
    book_data = await service.get_book_details_by_id(db, book_id)
    if not book_data:
        raise HTTPException(status_code=404, detail="Book listing not found.")
        
    # 2. Prevent users from expressing interest in their own listings
    if book_data["owner_id"] == user_id:
        raise HTTPException(status_code=400, detail="You cannot generate leads for your own catalog assets.")

    # 3. BACKEND DEV WORK: Async write this lead to an analytics or transaction table
    # This lets you measure traction: "Book X generated 14 potential buyer inquiries this week"

    # MERGE NOTE:
    # bhai isko connect krna he baad me , to uske liye abhi to koi function nahi he 
    # jo reflect kare database me bhi to isko comment hi rhne diya , to iska function bana le 
    # and database me bhi agar kuch alter karna hoto
    # await service.increment_book_lead_counter(db, book_id=book_id, buyer_id=user_id)
    
    # 4. Generate the auto-text messaging structure from the backend dynamically
    msg = f"Hi {book_data['owner_name']}! 👋 I am interested in your book '{book_data['title']}' listed on BookMyBook. Is it still available near {book_data['campus_name']}?"
    
    return {
        "status": "success",
        "target_mobile": book_data["owner_mobile"],
        "prefilled_text": msg  # Frontend just grabs this string and drops it into encodeURIComponent()
    }

# MERGE NOTE:
# Ek dynamic route chaiye tha kyuki button pr click krne k liye book_id chahiye tha

@router.get("/{book_id}")
async def get_book_detail(
    book_id: str,
    user_id: str = Depends(verify_session),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches the detailed information for a specific book listing.
    """
    book_data = await service.get_book_details_by_id(db, book_id)
    if not book_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book listing not found.")
    
    return book_data
