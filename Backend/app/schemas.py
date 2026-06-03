from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str | None = Field(None, max_length=255)

    @field_validator("password")
    @classmethod
    def password_not_only_whitespace(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Password must not be whitespace only")
        if len(v.encode("utf-8")) > 1024:
            # Prehash handles bcrypt's 72-byte limit, but reject absurdly long
            # passwords (> 1 KB) early to prevent DoS via hashing cost.
            raise ValueError("Password is too long")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: str
    username: str
    email: str
    display_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


# ---------------------------------------------------------------------------
# Sessions (conversation history sidebar)
# ---------------------------------------------------------------------------

class SessionSummary(BaseModel):
    session_id: str
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions: list[SessionSummary]


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Conversation session identifier")
    message: str = Field(..., min_length=1, max_length=5000, description="User message text")
    latitude: float | None = Field(None, description="User latitude for location-based help")
    longitude: float | None = Field(None, description="User longitude for location-based help")


class ChatResponse(BaseModel):
    response: str
    risk_level: str = "none"
    mood_score: float | None = None
    session_id: str


class SessionCreateResponse(BaseModel):
    session_id: str
    user_id: str


class ChatHistoryMessage(BaseModel):
    id: str | None = None
    role: str
    content: str
    created_at: datetime | None = None


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatHistoryMessage]


class DeleteSessionResponse(BaseModel):
    session_id: str
    message: str



class WSMessage(BaseModel):
    message: str
    latitude: float | None = None
    longitude: float | None = None


class WSEvent(BaseModel):
    type: str
    data: str



class MoodCreateRequest(BaseModel):
    mood_score: float = Field(..., ge=1, le=10)
    mood_label: str = Field(..., max_length=100)
    notes: str | None = None
    session_id: str | None = None


class MoodEntryResponse(BaseModel):
    id: str
    user_id: str
    session_id: str | None
    mood_score: float
    mood_label: str
    notes: str | None
    coping_strategies_offered: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MoodHistoryResponse(BaseModel):
    user_id: str
    entries: list[MoodEntryResponse]



class NearbyPlace(BaseModel):
    name: str
    address: str
    phone: str | None = None
    rating: float | None = None
    maps_link: str


class NearbyResponse(BaseModel):
    places: list[NearbyPlace]
    source: str = "mock"


class CrisisLine(BaseModel):
    name: str
    contact: str
    description: str
    available: str


class CrisisLinesResponse(BaseModel):
    crisis_lines: list[CrisisLine]
