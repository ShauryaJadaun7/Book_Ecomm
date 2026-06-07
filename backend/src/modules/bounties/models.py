import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, ARRAY as PG_ARRAY
from src.core.database import Base

class BookBounty(Base):
    __tablename__ = "book_bounties"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    seeker_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    genres = Column(PG_ARRAY(String), nullable=False, server_default="{}")
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))