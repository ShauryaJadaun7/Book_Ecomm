from celery import Celery
from src.core.config import settings  # <-- Import your centralized env configuration

celery_worker = Celery(
    "auth_tasks",
    broker=settings.REDIS_URL,       # <-- Dynamically loaded from .env
    backend=settings.REDIS_URL       # <-- Dynamically loaded from .env
)

celery_worker.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)