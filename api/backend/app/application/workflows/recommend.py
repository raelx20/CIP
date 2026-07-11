import uuid
from datetime import datetime, timezone

from app.domain.department_router import DepartmentRouter
from app.domain.submission.value_objects import SubmissionStatus


class RecommendWorkflow:
    def __init__(self):
        self.router = DepartmentRouter()

    async def generate_recommendation(
        self,
        cluster_id: uuid.UUID,
        title: str,
        description: str,
        category: str,
        subcategory: str | None,
        priority_score: float,
        affected_population: int | None = None,
        location_context: dict | None = None,
    ) -> dict:
        routing = self.router.route(
            category=category,
            subcategory=subcategory,
            location_context=location_context,
        )

        recommendation = {
            "id": uuid.uuid4(),
            "cluster_id": cluster_id,
            "priority_assessment_id": None,
            "title": title,
            "recommended_action": description,
            "responsible_department_candidates": [
                routing["primary_department"],
                *routing["alternative_departments"],
            ],
            "rationale": f"Based on priority score {priority_score:.2f} and {category} category",
            "implementation_steps": [],
            "expected_outcomes": None,
            "expected_beneficiaries": affected_population,
            "supporting_evidence_refs": [],
            "contradictory_evidence": [],
            "dependencies": [],
            "risks": [],
            "uncertainties": [],
            "confidence": routing["confidence"],
            "alternative_actions": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        submission_update = {
            "status": SubmissionStatus.RECOMMENDED.value,
            "updated_at": datetime.now(timezone.utc),
        }

        return {
            "recommendation": recommendation,
            "routing": routing,
            "submission_update": submission_update,
        }
