from pydantic import BaseModel, Field
from typing import List

class BountyCreateRequest(BaseModel):
    """Validates bounty placement payloads coming from the frontend client."""
    title: str = Field(..., min_length=2, description="Title of the unavailable book being hunted")
    genres: List[str] = Field(..., min_length=1, description="Array of target genres to locate candidate match peers")


class MatchedOwnerResponse(BaseModel):
    """Represents a validated candidate match peer without location parameters."""
    owner_name: str
    owner_mobile: str
    matched_via: str  # Tracks 'Exact Title Match' or 'Genre Expertise Match'
    prefilled_text: str


class BountyCreationResponse(BaseModel):
    """The unified data structure returned following a successful bounty registration block."""
    status: str
    bounty_id: str
    message: str
    matches_found: int
    candidates: List[MatchedOwnerResponse]