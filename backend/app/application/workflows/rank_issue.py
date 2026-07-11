import uuid
from datetime import datetime, timezone

from app.domain.priority_engine import PriorityEngine
from app.domain.priority.value_objects import ThreatDimension
from app.domain.submission.value_objects import SubmissionStatus


class RankIssueWorkflow:
    def __init__(self):
        self.engine = PriorityEngine()

    async def rank(
        self,
        cluster_id: uuid.UUID,
        submission_count: int,
        urgency: int,
        severity: int,
        dimension_scores: dict[str, float] | None = None,
    ) -> dict:
        if not dimension_scores:
            dimension_scores = {dim.value: 0.5 for dim in ThreatDimension}

        threat_dimensions = {}
        for dim in ThreatDimension:
            threat_dimensions[dim.value] = dimension_scores.get(dim.value, 0.5)

        priority_score = self.engine.calculate_priority(
            dimension_scores=threat_dimensions,
            submission_count=submission_count,
            urgency=urgency,
            severity=severity,
        )

        assessment = {
            "id": uuid.uuid4(),
            "cluster_id": cluster_id,
            "final_score": priority_score.final_score,
            "priority_level": priority_score.priority_level.value,
            "rank": None,
            "scoring_version": priority_score.scoring_version,
            "weights": self.engine.weights.to_dict(),
            "bonuses": {},
            "penalties": {},
            "reasoning": self.engine.explain_score(priority_score),
            "uncertainties": [],
            "evidence_references": [],
            "calculation_timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        components = []
        for comp in priority_score.components:
            components.append({
                "id": uuid.uuid4(),
                "assessment_id": assessment["id"],
                "dimension": comp.dimension.value,
                "raw_value": comp.raw_value,
                "normalized_value": comp.normalized_value,
                "weight": comp.weight,
                "weighted_score": comp.weighted_score,
                "description": None,
                "evidence": None,
                "created_at": datetime.now(timezone.utc),
            })

        threat_analysis = {
            "cluster_id": cluster_id,
            "threat_dimensions": threat_dimensions,
            "overall_threat_score": priority_score.final_score,
            "highest_threat_dimension": max(
                threat_dimensions, key=threat_dimensions.get
            ),
            "threat_alerts": self._generate_alerts(threat_dimensions),
            "recommendations": [],
        }

        submission_update = {
            "status": SubmissionStatus.PRIORITIZED.value,
            "updated_at": datetime.now(timezone.utc),
        }

        return {
            "assessment": assessment,
            "components": components,
            "threat_analysis": threat_analysis,
            "submission_update": submission_update,
        }

    def _generate_alerts(self, dimensions: dict[str, float]) -> list[str]:
        alerts = []
        for dim, score in dimensions.items():
            if score >= 0.8:
                alerts.append(f"HIGH ALERT: {dim.replace('_', ' ').title()} is critically high ({score:.2f})")
            elif score >= 0.6:
                alerts.append(f"WARNING: {dim.replace('_', ' ').title()} is elevated ({score:.2f})")
        return alerts
