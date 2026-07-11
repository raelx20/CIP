import enum
from dataclasses import dataclass


class RecommendationStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"
    DEFERRED = "deferred"


@dataclass(frozen=True)
class ActionItem:
    step: int
    description: str
    responsible_department: str | None = None
    estimated_duration: str | None = None
    dependencies: list[str] | None = None
