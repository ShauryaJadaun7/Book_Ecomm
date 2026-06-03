from fastapi import APIRouter, Depends, HTTPException, Cookie, Form
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from src.core.database import get_db
from src.modules.users.router import redis_store
from .models import WishlistItem

router = APIRouter(prefix="/wishlist", tags=["Wishlist Management"])

@router.post("/")
async def add_item_to_wishlist(
    desired_title: str = Form(..., description="The name of the book the user is looking for"),
    session_id: str = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    if not session_id:
        raise HTTPException(status_code=401, detail="Session credentials missing.")
    user_id = redis_store.get(session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")

    new_wish = WishlistItem(
        user_id=uuid.UUID(user_id),
        desired_title=desired_title.strip()
    )
    db.add(new_wish)
    await db.commit()
    
    return {"status": "success", "message": f"'{desired_title}' successfully pinned to your campus alert watch."}