import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    citizen_id: uuid.UUID
    content: str = Field(..., min_length=1, max_length=10000)
    source_modality: str = Field(default="text")
    source_channel: str = Field(default="api")
    language: str | None = None
    gps_permission_granted: bool | None = None
    sender_latitude: float | None = None
    sender_longitude: float | None = None
    sender_gps_accuracy: float | None = None


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    status: str
    source_modality: str
    original_content: str
    normalized_content: str | None = None
    detected_language: str | None = None
    category: str | None = None
    subcategory: str | None = None
    severity: int | None = None
    urgency: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubmissionStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    progress: float = Field(ge=0, le=1)
    status_message: str
    created_at: datetime
    updated_at: datetime


class MediaUploadResponse(BaseModel):
    id: uuid.UUID
    media_type: str
    file_path: str
    original_filename: str | None = None
    extracted_text: str | None = None
    created_at: datetime
