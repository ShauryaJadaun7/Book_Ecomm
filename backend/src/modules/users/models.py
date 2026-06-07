from sqlalchemy import Column, String, DateTime, Text, text, Boolean  
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from geoalchemy2 import Geometry
from src.core.database import Base

class User(Base):
    __tablename__ = "users"

    # Core Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # 🔐 Authentication Credentials (GitHub-Style Update)
    password_hash = Column(String(255), nullable=True) # Stored via safe bcrypt hashes
    auth_provider = Column(String(50), default="email")  # "email" or "google"
    oauth_id = Column(String(255), unique=True, nullable=True, index=True)
    
    # 📍 Profile Demographics (Made nullable=True to be gathered post-login)
    mobile_number = Column(String(20), nullable=True)
    area = Column(String(255), nullable=True)
    pincode = Column(String(20), nullable=True)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True) # Un-commented and safe for PostGIS lookups
    
    # Metadata and Preferences
    bio = Column(Text, nullable=True)  
    favorite_genres = Column(ARRAY(String(100)), nullable=True)
    
    welcome_email_sent = Column(Boolean, default=False, nullable=False, server_default=text("false"))
    
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))