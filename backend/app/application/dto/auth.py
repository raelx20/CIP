import uuid
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="citizen")
    phone: str | None = None
    constituency: str | None = None
    district: str | None = None
    state: str | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    phone: str | None = None
    constituency: str | None = None
    district: str | None = None
    state: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
