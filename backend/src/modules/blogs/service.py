import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Blog

UPLOAD_DIR = "static/uploads/blogs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def create_new_blog(
    db: AsyncSession, author_id: str, title: str, content: str, image: Optional[UploadFile]
) -> dict:
    web_accessible_url = None
    
    if image:
        file_extension = os.path.splitext(image.filename)[1].lower()
        if file_extension not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise HTTPException(status_code=400, detail="Unsupported banner image format.")
            
        unique_filename = f"blog_{uuid.uuid4().hex}{file_extension}"
        file_save_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        try:
            contents = await image.read()
            with open(file_save_path, "wb") as storage_file:
                storage_file.write(contents)
            web_accessible_url = f"/static/uploads/blogs/{unique_filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Banner saving storage failure: {str(e)}")
        finally:
            await image.close()

    new_blog = Blog(
        title=title.strip(),
        content=content.strip(),
        image_url=web_accessible_url,
        author_id=uuid.UUID(author_id)
    )
    db.add(new_blog)
    await db.commit()
    await db.refresh(new_blog)
    
    return {
        "status": "success", 
        "message": "Blog post successfully published.",
        "blog_id": str(new_blog.id), 
        "title": new_blog.title
    }