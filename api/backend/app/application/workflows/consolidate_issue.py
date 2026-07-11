import uuid
from datetime import datetime, timezone

from app.domain.consolidation import IssueConsolidator
from app.domain.submission.value_objects import SubmissionStatus


class ConsolidateIssueWorkflow:
    def __init__(self):
        self.consolidator = IssueConsolidator()

    async def consolidate(
        self,
        submission_id: uuid.UUID,
        category: str,
        subcategory: str | None,
        latitude: float | None,
        longitude: float | None,
        existing_clusters: list[dict],
    ) -> dict:
        candidates = self.consolidator.find_matching_clusters(
            category=category,
            subcategory=subcategory,
            latitude=latitude,
            longitude=longitude,
            semantic_embedding=None,
            existing_clusters=existing_clusters,
        )

        should_create_new = self.consolidator.should_create_new_cluster(candidates)

        submission_update = {
            "status": SubmissionStatus.CLUSTERED.value,
            "updated_at": datetime.now(timezone.utc),
        }

        if should_create_new or not candidates:
            cluster = {
                "id": uuid.uuid4(),
                "title": f"{category}: New cluster",
                "summary": None,
                "category": category,
                "subcategory": subcategory,
                "latitude": latitude,
                "longitude": longitude,
                "raw_submission_count": 1,
                "trusted_demand": 0.0,
                "suspicious_demand": 0.0,
                "affected_population": None,
                "severity": None,
                "urgency": None,
                "lifecycle_state": "new",
                "confidence": 0.5,
                "first_reported": datetime.now(timezone.utc),
                "latest_report": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

            membership = {
                "id": uuid.uuid4(),
                "cluster_id": cluster["id"],
                "submission_id": submission_id,
                "similarity_score": 0.0,
                "is_primary": True,
                "created_at": datetime.now(timezone.utc),
            }

            return {
                "action": "created",
                "cluster": cluster,
                "membership": membership,
                "submission_update": submission_update,
            }
        else:
            best_match = candidates[0]

            membership = {
                "id": uuid.uuid4(),
                "cluster_id": best_match.cluster_id,
                "submission_id": submission_id,
                "similarity_score": best_match.similarity_score,
                "is_primary": False,
                "created_at": datetime.now(timezone.utc),
            }

            cluster_update = {
                "raw_submission_count": "+1",
                "latest_report": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

            return {
                "action": "merged",
                "cluster_id": best_match.cluster_id,
                "membership": membership,
                "cluster_update": cluster_update,
                "submission_update": submission_update,
            }
