from sqlalchemy import Column, Float, String, Text, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from src.core.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    genres = Column(ARRAY(String(100)), nullable=True)
    image_url = Column(String(500), nullable=True)  # Absolute storage system directory pointer
    price = Column(Float, nullable=False, default=0.0)  # column for peer pricing
    owner_note = Column(String(500), nullable=True)
    # Structural Ownership Links
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", backref="books")
    
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))