import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from fastapi import APIRouter, Depends, HTTPException, Form, Query
from src.core.database import get_db
from src.core.security import get_current_user
from src.modules.users.models import User
from . import service

from src.modules.users.models import User
# 🧠 Direct Cross-Module Imports out of the Blog schema definitions:
from src.modules.blogs.models import Blog, BlogLike, BlogComment


router = APIRouter(prefix="/feed", tags=["Campus Feed & Interactions Platform"])


@router.get("/", response_model=List[dict])
async def read_feed_stream(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the chronological campus blog feed with embedded interaction metrics.
    """
    return await service.get_blogs_feed(db=db, current_user_id=str(current_user.id), page=page, limit=limit)


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


async def toggle_blog_like(db: AsyncSession, user_id: str, blog_id: str) -> dict:
    user_uuid = uuid.UUID(user_id)
    blog_uuid = uuid.UUID(blog_id)

    like_query = select(BlogLike).filter(and_(BlogLike.blog_id == blog_uuid, BlogLike.user_id == user_uuid))
    like_result = await db.execute(like_query)
    existing_like = like_result.scalars().first()

    if existing_like:
        await db.delete(existing_like)
        await db.commit()
        liked = False
    else:
        new_like = BlogLike(blog_id=blog_uuid, user_id=user_uuid)
        db.add(new_like)
        await db.commit()
        liked = True

    total_likes = await db.scalar(select(func.count(BlogLike.id)).filter(BlogLike.blog_id == blog_uuid))
    return {"status": "success", "liked": liked, "current_likes_count": total_likes}


async def add_blog_comment(db: AsyncSession, user_id: str, blog_id: str, content: str) -> dict:
    new_comment = BlogComment(
        blog_id=uuid.UUID(blog_id),
        user_id=uuid.UUID(user_id),
        content=content.strip()
    )
    db.add(new_comment)
    await db.commit()
    return {"status": "success", "comment_id": str(new_comment.id), "message": "Comment posted cleanly."}


async def get_blog_comments(db: AsyncSession, blog_id: str) -> List[dict]:
    query = (
        select(BlogComment.id, BlogComment.content, BlogComment.created_at, User.name.label("user_name"))
        .join(User, BlogComment.user_id == User.id)
        .filter(BlogComment.blog_id == uuid.UUID(blog_id))
        .order_by(BlogComment.created_at.asc())
    )
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "comment_id": str(row.id),
            "content": row.content,
            "created_at": row.created_at.isoformat(),
            "user_name": row.user_name
        }
        for row in rows
    ]