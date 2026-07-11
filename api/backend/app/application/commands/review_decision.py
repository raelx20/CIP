import uuid
from dataclasses import dataclass


@dataclass
class ReviewDecisionCommand:
    submission_id: uuid.UUID
    officer_id: uuid.UUID
    decision: str
    reason: str | None = None
    corrections: dict | None = None
