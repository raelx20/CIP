import enum
import uuid
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SubmissionStatus(str, enum.Enum):
    RECEIVED = "received"
    NORMALIZED = "normalized"
    LOCATION_RESOLVED = "location_resolved"
    UNDERSTOOD = "understood"
    NEEDS_CLARIFICATION = "needs_clarification"
    WAITING_FOR_CITIZEN = "waiting_for_citizen"
    ASSESSED = "assessed"
    AUTHENTICITY_SCORED = "authenticity_scored"
    CLUSTERED = "clustered"
    ENRICHED = "enriched"
    PRIORITIZED = "prioritized"
    RECOMMENDED = "recommended"
    READY_FOR_REVIEW = "ready_for_review"
    COMPLETED = "completed"
    PROCESSING_FAILED = "processing_failed"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"
    ABANDONED = "abandoned"


class SourceModality(str, enum.Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    MESSAGING = "messaging"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    citizen_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus), nullable=False, default=SubmissionStatus.RECEIVED
    )
    source_modality: Mapped[SourceModality] = mapped_column(
        Enum(SourceModality), nullable=False
    )
    source_channel: Mapped[str] = mapped_column(String(50), nullable=False, default="api")
    original_content: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    response_language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    urgency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    affected_population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    affected_households: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extraction_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    processing_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    gps_permission_granted: Mapped[bool | None] = mapped_column(nullable=True)
    sender_latitude: Mapped[float | None] = mapped_column(nullable=True)
    sender_longitude: Mapped[float | None] = mapped_column(nullable=True)
    sender_gps_accuracy: Mapped[float | None] = mapped_column(nullable=True)
    sender_gps_timestamp: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    media: Mapped[list["SubmissionMedia"]] = relationship(back_populates="submission", cascade="all, delete-orphan")


class SubmissionMedia(Base):
    __tablename__ = "submission_media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False
    )
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    submission: Mapped["Submission"] = relationship(back_populates="media")
