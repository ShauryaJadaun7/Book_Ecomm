from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user
from src.modules.users.models import User
from . import service

router = APIRouter(prefix="/blogs", tags=["Blog Creation Engine"])

@router.post("/", dependencies=[Depends(get_current_user)])
async def upload_new_blog_post(
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish endpoint: Accepts incoming form-data to spawn a new blog post.
    """
    return await service.create_new_blog(
        db=db, author_id=str(current_user.id), title=title, content=content, image=image
    )