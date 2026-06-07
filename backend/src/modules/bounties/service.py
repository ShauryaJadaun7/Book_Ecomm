import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import BookBounty

async def get_user_bounties(db: AsyncSession, user_id: str) -> List[BookBounty]:
    """Retrieves all active book bounties created by the specified user, ordered by creation time."""
    user_uuid = uuid.UUID(str(user_id))
    result = await db.execute(
        select(BookBounty)
        .filter(BookBounty.seeker_id == user_uuid)
        .order_by(BookBounty.created_at.desc())
    )
    return list(result.scalars().all())

async def delete_bounty(db: AsyncSession, bounty_id: str, user_id: str) -> bool:
    """Deletes a specific book bounty after verifying that it belongs to the requesting user."""
    bounty_uuid = uuid.UUID(str(bounty_id))
    user_uuid = uuid.UUID(str(user_id))
    
    result = await db.execute(
        select(BookBounty)
        .filter(BookBounty.id == bounty_uuid, BookBounty.seeker_id == user_uuid)
    )
    bounty = result.scalar_one_or_none()
    
    if not bounty:
        return False
        
    await db.delete(bounty)
    await db.commit()
    return True