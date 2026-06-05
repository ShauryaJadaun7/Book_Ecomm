# 1. Add 'Text' (Capitalized) to your imports from sqlalchemy
from sqlalchemy import Column, String, DateTime, Text, text  
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from geoalchemy2 import Geometry
from src.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    auth_provider = Column(String(50), default="email")  
    oauth_id = Column(String(255), unique=True, nullable=True, index=True)
    
    area = Column(String(255), nullable=False)
    pincode = Column(String(20), nullable=False)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    
    # 2. Fix this line to use capital 'Text'
    bio = Column(Text, nullable=True)  
    favorite_genres = Column(ARRAY(String(100)), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))