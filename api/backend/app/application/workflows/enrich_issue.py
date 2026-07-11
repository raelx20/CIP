import uuid
from datetime import datetime, timezone

from app.domain.submission.value_objects import SubmissionStatus


class EnrichIssueWorkflow:
    async def enrich(
        self,
        cluster_id: uuid.UUID,
        category: str,
        latitude: float | None,
        longitude: float | None,
    ) -> dict:
        evidence_items = []

        demographic_evidence = {
            "id": uuid.uuid4(),
            "cluster_id": cluster_id,
            "evidence_type": "demographic",
            "source_name": "Census Data",
            "source_reference": None,
            "source_url": None,
            "retrieval_timestamp": datetime.now(timezone.utc),
            "publication_timestamp": None,
            "freshness": "current",
            "verification_status": "verified",
            "confidence": 0.9,
            "extracted_facts": {},
            "geographic_relevance": 0.8 if latitude and longitude else 0.5,
            "temporal_relevance": 0.7,
            "relationship_to_issue": "supporting",
            "provider_metadata": None,
            "created_at": datetime.now(timezone.utc),
        }
        evidence_items.append(demographic_evidence)

        infrastructure_evidence = {
            "id": uuid.uuid4(),
            "cluster_id": cluster_id,
            "evidence_type": "infrastructure",
            "source_name": "Infrastructure Database",
            "source_reference": None,
            "source_url": None,
            "retrieval_timestamp": datetime.now(timezone.utc),
            "publication_timestamp": None,
            "freshness": "current",
            "verification_status": "verified",
            "confidence": 0.85,
            "extracted_facts": {},
            "geographic_relevance": 0.7 if latitude and longitude else 0.4,
            "temporal_relevance": 0.6,
            "relationship_to_issue": "supporting",
            "provider_metadata": None,
            "created_at": datetime.now(timezone.utc),
        }
        evidence_items.append(infrastructure_evidence)

        submission_update = {
            "status": SubmissionStatus.ENRICHED.value,
            "updated_at": datetime.now(timezone.utc),
        }

        return {
            "evidence_items": evidence_items,
            "submission_update": submission_update,
        }
