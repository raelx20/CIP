import uuid
from datetime import datetime, timezone

from app.domain.clarification_policy import ClarificationPolicy
from app.domain.submission.value_objects import SubmissionStatus


class ClarifyWorkflow:
    def __init__(self):
        self.policy = ClarificationPolicy()

    async def should_clarify(
        self,
        submission_id: uuid.UUID,
        missing_information: list[str],
        current_round: int,
        max_rounds: int,
    ) -> bool:
        return self.policy.should_clarify(
            missing_information=missing_information,
            current_round=current_round,
            max_rounds=max_rounds,
            submission_status="understood",
        )

    async def generate_clarification(
        self,
        submission_id: uuid.UUID,
        missing_information: list[str],
        already_answered: list[str],
        current_round: int,
    ) -> dict:
        questions = self.policy.generate_clarification_questions(
            missing_information=missing_information,
            already_answered=already_answered,
            current_round=current_round,
        )

        question_texts = [q.question for q in questions]

        session = {
            "id": uuid.uuid4(),
            "submission_id": submission_id,
            "citizen_id": None,
            "state": "active",
            "current_round": current_round + 1,
            "max_rounds": self.policy.MAX_ROUNDS,
            "language": None,
            "context": {
                "missing_information": missing_information,
                "questions_asked": [q.topic for q in questions],
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        submission_update = {
            "status": SubmissionStatus.NEEDS_CLARIFICATION.value,
            "updated_at": datetime.now(timezone.utc),
        }

        return {
            "session": session,
            "questions": question_texts,
            "submission_update": submission_update,
        }

    async def process_response(
        self,
        session_id: uuid.UUID,
        citizen_response: str,
        question_topics: list[str],
    ) -> dict:
        return {
            "answers": {
                topic: citizen_response for topic in question_topics
            },
            "session_update": {
                "state": "active",
                "updated_at": datetime.now(timezone.utc),
            },
        }
