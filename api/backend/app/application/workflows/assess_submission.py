import uuid
from datetime import datetime, timezone

from app.domain.submission.value_objects import SubmissionStatus


class AssessSubmissionWorkflow:
    async def assess(
        self,
        submission_id: uuid.UUID,
        original_content: str,
        detected_language: str | None = None,
    ) -> dict:
        assessment = {
            "id": uuid.uuid4(),
            "submission_id": submission_id,
            "primary_issue": None,
            "category": None,
            "subcategory": None,
            "description": original_content[:500] if original_content else None,
            "reported_cause": None,
            "affected_infrastructure": None,
            "candidate_departments": [],
            "issue_duration": None,
            "severity_indicators": {},
            "urgency_indicators": {},
            "people_affected": None,
            "households_affected": None,
            "vulnerable_groups": [],
            "health_impact": None,
            "safety_impact": None,
            "education_impact": None,
            "mobility_impact": None,
            "economic_impact": None,
            "environmental_impact": None,
            "service_disruption": None,
            "emergency_conditions": False,
            "alternatives_available": None,
            "requested_action": None,
            "missing_information": [],
            "contradictions": [],
            "ambiguity": [],
            "confidence": 0.0,
            "alternative_interpretations": [],
            "fact_inference_map": {},
            "extraction_metadata": {
                "detected_language": detected_language,
                "assessment_timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        updated_submission = {
            "status": SubmissionStatus.UNDERSTOOD.value,
            "updated_at": datetime.now(timezone.utc),
        }

        return {"assessment": assessment, "submission_update": updated_submission}
