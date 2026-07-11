import enum
from dataclasses import dataclass


class ClusterLifecycleState(str, enum.Enum):
    NEW = "new"
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass(frozen=True)
class DemandVelocity:
    current_rate: float
    previous_rate: float
    acceleration: float
    trend: str  # "increasing", "stable", "decreasing"

    @property
    def is_accelerating(self) -> bool:
        return self.acceleration > 0.1
