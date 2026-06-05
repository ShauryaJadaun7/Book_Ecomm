from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user
from src.modules.users.models import User
from . import service

router = APIRouter(prefix="/feed", tags=["Campus Feed & Interactions Platform"])


@router.get("")
async def read_feed_stream(
    cursor: Optional[str] = Query(None, description="The ISO timestamp of the last item from the previous batch"),
    limit: int = Query(10, ge=1, le=50, description="Number of blog posts to return in this batch"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a cursor-paginated timeline stream optimized for infinite scroll layouts.
    """
    return await service.get_paginated_blogs_feed(
        db=db, current_user_id=str(current_user.id), cursor=cursor, limit=limit
    )


@router.post("/{blog_id}/like")
async def toggle_like(
    blog_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle a like on a specific blog post.
    """
    return await service.toggle_blog_like(db=db, user_id=str(current_user.id), blog_id=blog_id)


@router.post("/{blog_id}/comment")
async def post_comment(
    blog_id: str,
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Post a new comment underneath a specific post.
    """
    if not content.strip():
        raise HTTPException(status_code=400, detail="Comment cannot be blank.")
    return await service.add_blog_comment(db=db, user_id=str(current_user.id), blog_id=blog_id, content=content)


@router.get("/{blog_id}/comments", response_model=List[dict])
async def read_comments(
    blog_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all comments for a specific post.
    """
    return await service.get_blog_comments(db=db, blog_id=blog_id)