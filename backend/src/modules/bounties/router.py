import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult  # Inspects background states inside Redis memory arrays

from src.core.database import get_db
from src.core.security import get_current_user, enforce_contact_rate_limiting
from src.modules.users.models import User
from .schemas import BountyCreateRequest
from .models import BookBounty
from .tasks import search_and_match_bounty_task  # Import your task entry point handle

router = APIRouter(prefix="/bounties", tags=["Asynchronous Campus Bounty Architecture"])


@router.post(
    "/create", 
    status_code=status.HTTP_202_ACCEPTED,  # 🌟 202 Signifies long-running request processing initialization
    dependencies=[Depends(enforce_contact_rate_limiting)]
)
async def create_campus_book_bounty_async(
    payload: BountyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Non-Blocking Bounty Gate: Stages request configurations inside PostgreSQL registries 
    and instantly delegates spatial computing workloads to standalone background worker queues.
    """
    # 1. Instantly stage the structural record tracking anchor row item
    new_bounty = BookBounty(
        seeker_id=current_user.id,
        title=payload.title.strip(),
        genres=[g.strip() for g in payload.genres]
    )
    db.add(new_bounty)
    await db.commit()
    await db.refresh(new_bounty)

    # 2. Fire-and-Forget: Handover query computation tasks to your active Celery broker stack
    task = search_and_match_bounty_task.delay(
        bounty_id=str(new_bounty.id),
        seeker_id=str(current_user.id),
        title=new_bounty.title,
        genres=new_bounty.genres
    )

    # 3. Drop back a rapid transactional ticket signature. The client loop remains perfectly fluid.
    return {
        "status": "processing",
        "message": "Campus search tracking task pushed to processing background worker streams.",
        "task_id": task.id,
        "bounty_id": str(new_bounty.id)
    }


@router.get("/task/{task_id}", status_code=status.HTTP_200_OK)
async def get_bounty_matching_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)  # Locks polling route visualization down to authorized systems
):
    """
    Worker Results Polling Bridge: Extracts target memory segments straight from Celery's 
    Redis Results backend cache matrix to confirm lookup pipeline lifecycle progress values.
    """
    task_result = AsyncResult(task_id)

    if task_result.state == "PENDING":
        return {
            "task_id": task_id,
            "state": "PENDING",
            "message": "Task is waiting inside the worker routing ring queue lines..."
        }
    
    elif task_result.state == "STARTED":
        return {
            "task_id": task_id,
            "state": "STARTED",
            "message": "Worker is currently calculating coordinate parameters and text weights..."
        }

    elif task_result.state == "SUCCESS":
        # Celery successfully processed the job; pull the cached dictionary straight from Redis
        data = task_result.result
        return {
            "task_id": task_id,
            "state": "SUCCESS",
            "result": data
        }

    elif task_result.state == "FAILURE":
        return {
            "task_id": task_id,
            "state": "FAILURE",
            "error": str(task_result.info)  # Returns error context if a worker crashes
        }

    return {"task_id": task_id, "state": task_result.state}