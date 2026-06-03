from typing import Optional, List
from pydantic import BaseModel, EmailStr

class SendOTPRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    area: Optional[str] = None
    pincode: Optional[str] = None

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class GoogleAuthRequest(BaseModel):
    token: str
    area: Optional[str] = None
    pincode: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    area: str
    pincode: str
    
    class Config:
        from_attributes = True