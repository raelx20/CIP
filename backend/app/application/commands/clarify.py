import uuid
from dataclasses import dataclass


@dataclass
class ClarifyCommand:
    session_id: uuid.UUID
    citizen_id: uuid.UUID
    response: str
    question_topics: list[str]
