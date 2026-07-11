import enum
from dataclasses import dataclass


class ConversationState(str, enum.Enum):
    ACTIVE = "active"
    WAITING_FOR_CITIZEN = "waiting_for_citizen"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    TIMED_OUT = "timed_out"


class MessageRole(str, enum.Enum):
    CITIZEN = "citizen"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class ClarificationRound:
    current: int
    max_rounds: int
    questions_asked: list[str]
    answers_received: dict[str, str]

    @property
    def is_complete(self) -> bool:
        return self.current >= self.max_rounds

    @property
    def remaining(self) -> int:
        return max(0, self.max_rounds - self.current)
