from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class UserSignupRequest(BaseModel):
    """
    Validates entry-level signup credentials.
    Enforces minimum password length at the application gateway.
    """
    name: str = Field(..., min_length=2, max_length=100, description="The user's full display name")
    email: EmailStr = Field(..., description="Valid academic or personal email address")
    password: str = Field(..., min_length=6, description="Secure access password. Minimum 6 characters required.")


class VerifySignupOTPRequest(BaseModel):
    """
    Validates the 6-digit verification code payload string 
    required to finalize account provisioning.
    """
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit cryptographic challenge string")


class UserLoginRequest(BaseModel):
    """
    Validates email and password parameters during a standard login attempt.
    """
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """
    Validates incoming Google single sign-on requests.
    Decoupled from location constraints as they are handled post-login.
    """
    token: str = Field(..., description="OAuth credential token passed from the frontend client")


class UserProfileResponse(BaseModel):
    """
    Data Transfer Object (DTO) schema mapping active user profile metadata.
    Enables location and contact attributes to return as null/None for unonboarded accounts.
    """
    id: str
    name: str
    email: EmailStr
    area: Optional[str] = None
    pincode: Optional[str] = None
    mobile_number: Optional[str] = None

    class Config:
        from_attributes = True  # Allows Pydantic to cleanly serialize SQLAlchemy ORM instances natively

class ProfileOnboardingRequest(BaseModel):
    area: str = Field(..., min_length=2, max_length=255, description="Campus name selection string")
    pincode: str = Field(..., min_length=6, max_length=10, description="Regional zip code footprint")
    mobile_number: str = Field(..., min_length=10, max_length=15, description="Active user WhatsApp handle")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Device sensor latitude position decimal")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Device sensor longitude position decimal")
    email: Optional[EmailStr] = Field(None, description="Optional profile email override")
    # In your Profile/User Onboarding Schema
