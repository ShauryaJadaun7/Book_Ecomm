import uuid
from worker.celery_app import celery_worker
from sqlalchemy import create_engine, func, or_
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.modules.users.models import User
from src.modules.marketplace.models import Book
from .models import BookBounty

# 🔌 Setup Synchronous Engine Pool for Celery Worker execution contexts
SYNC_DB_URL = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
sync_engine = create_engine(SYNC_DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=sync_engine)


@celery_worker.task(name="src.modules.bounties.tasks.search_and_match_bounty_task")
def search_and_match_bounty_task(bounty_id: str, seeker_id: str, title: str, genres: list) -> dict:
    """
    Location-Agnostic Bounty Task Engine: Scans the entire global catalog for matching 
    book titles or genre arrays, bypassing all geospatial and campus distance overheads.
    """
    # Use standard context manager to guarantee connection release
    with SessionLocal() as db:
        
        # 1. Base Query: Select only necessary details (No campus/area fields)
        query = db.query(
            Book.title.label("book_title"),
            User.id.label("owner_id"),
            User.name.label("owner_name"),
            User.mobile_number.label("owner_mobile")
        ).join(User, Book.owner_id == User.id).filter(User.id != uuid.UUID(seeker_id))

        # 2. Compile Search Filters (Case-Insensitive matching matching your setup)
        title_pattern = f"%{title.strip().lower()}%"
        genre_conditions = [func.array_to_string(Book.genres, ",").ilike(f"%{g.strip().lower()}%") for g in genres]

        # Apply Title or Genre matching logic
        query = query.filter(or_(Book.title.ilike(title_pattern), *genre_conditions))

        # 3. Order alphabetically by book title or owner name
        query = query.order_by(Book.title.asc())
        
        rows = query.all()

        # 4. Process matches and deduplicate owners
        processed_candidates = []
        seen_user_ids = set()

        for row in rows:
            # Deduplicate users to avoid sending the same owner multiple times
            if row.owner_id in seen_user_ids:
                continue
            seen_user_ids.add(row.owner_id)

            # Detect matching type strategy
            is_title_match = title.lower() in row.book_title.lower()
            match_vector = "Exact Title Match" if is_title_match else "Genre Expertise Match"

            # 📝 Updated message copy template (No location or campus mentions anymore)
            prefilled_msg = (
                f"Hi {row.owner_name}! 👋 I placed a campus bounty hunt for the book '{title.strip()}' "
                f"on LocalShelf. I saw that you have a matching copy or similar listings. "
                f"Is it available for barter or purchase?"
            )

            processed_candidates.append({
                "owner_name": row.owner_name,
                "owner_mobile": row.owner_mobile or "Unlinked Contact",
                "matched_via": match_vector,
                "prefilled_text": prefilled_msg
            })

        return {
            "bounty_id": bounty_id,
            "matches_found": len(processed_candidates),
            "candidates": processed_candidates
        }