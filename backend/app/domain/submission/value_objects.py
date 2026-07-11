import enum
import uuid
from dataclasses import dataclass


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


@dataclass(frozen=True)
class SubmissionID:
    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class MediaReference:
    file_path: str
    media_type: str
    mime_type: str | None = None
    file_size: int | None = None
