from celery import Celery
from src.core.config import settings  # <-- Import your centralized env configuration

celery_worker = Celery(
    "auth_tasks",
    broker=settings.REDIS_URL,       # <-- Dynamically loaded from .env
    backend=settings.REDIS_URL,      # <-- Dynamically loaded from .env
    # 🚨 CRITICAL FIX: Tell the worker exactly where to look for your tasks on startup
    include=[
        "worker.tasks.auth_tasks",       # For your real-time OTP delivery emails
        "src.modules.wishlist.tasks"     # For your hyper-local campus wishlist matchers
    ]
)

celery_worker.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)