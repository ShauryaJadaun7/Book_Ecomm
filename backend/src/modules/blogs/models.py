from sqlalchemy import Column, String, Text, ForeignKey, DateTime, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.core.database import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author = relationship("User", backref="blogs")
    
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))


class BlogLike(Base):
    __tablename__ = "blog_likes"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    blog_id = Column(UUID(as_uuid=True), ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (UniqueConstraint("blog_id", "user_id", name="uq_blog_user_like"),)


class BlogComment(Base):
    __tablename__ = "blog_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    blog_id = Column(UUID(as_uuid=True), ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("User", backref="blog_comments")