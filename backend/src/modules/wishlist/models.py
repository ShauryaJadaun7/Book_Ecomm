from sqlalchemy import Column, String, ForeignKey, DateTime, text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.core.database import Base

class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    desired_title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    
    user = relationship("User", backref="wishlist")

# ⚡ Register the GIN Trigram Index directly into your persistent storage engine metadata
Index(
    "idx_wishlist_title_trgm",
    WishlistItem.desired_title,
    postgresql_using="gin",
    postgresql_ops={"desired_title": "gin_trgm_ops"}
)