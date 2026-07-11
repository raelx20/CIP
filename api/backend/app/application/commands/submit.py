import uuid
from dataclasses import dataclass


@dataclass
class SubmitCommand:
    citizen_id: uuid.UUID
    content: str
    source_modality: str = "text"
    source_channel: str = "api"
    language: str | None = None
    gps_permission_granted: bool | None = None
    sender_latitude: float | None = None
    sender_longitude: float | None = None
    sender_gps_accuracy: float | None = None
