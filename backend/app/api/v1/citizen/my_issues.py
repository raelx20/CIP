import uuid
from fastapi import APIRouter, HTTPException, status

from app.application.dto.issue import IssueClusterResponse

router = APIRouter()


@router.get("/my-issues")
async def get_my_issues(
    citizen_id: uuid.UUID,
):
    """Get consolidated issues the citizen contributed to, with 'X people reported this'."""
    from app.infrastructure.database.repositories.issue import IssueClusterRepository
    from app.infrastructure.database.repositories.submission import SubmissionRepository
    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        submission_repo = SubmissionRepository(session)
        issue_repo = IssueClusterRepository(session)

        submissions = await submission_repo.get_by_citizen(citizen_id, limit=1000)

        cluster_ids = set()
        for sub in submissions:
            memberships = await session.execute(
                __import__('sqlalchemy').select(
                    __import__('sqlalchemy').text('issue_cluster_memberships.cluster_id')
                ).where(
                    __import__('sqlalchemy').text(f"submission_id = '{sub.id}'")
                )
            )
            for row in memberships:
                cluster_ids.add(row[0])

        clusters = []
        for cid in cluster_ids:
            cluster = await issue_repo.get_by_id(cid)
            if cluster:
                clusters.append(
                    IssueClusterResponse(
                        id=cluster.id,
                        title=cluster.title,
                        summary=cluster.summary,
                        category=cluster.category,
                        subcategory=cluster.subcategory,
                        latitude=cluster.latitude,
                        longitude=cluster.longitude,
                        formatted_address=cluster.formatted_address,
                        raw_submission_count=cluster.raw_submission_count,
                        trusted_demand=cluster.trusted_demand,
                        suspicious_demand=cluster.suspicious_demand,
                        affected_population=cluster.affected_population,
                        severity=cluster.severity,
                        urgency=cluster.urgency,
                        lifecycle_state=cluster.lifecycle_state.value,
                        confidence=cluster.confidence,
                        first_reported=cluster.first_reported,
                        latest_report=cluster.latest_report,
                        created_at=cluster.created_at,
                    )
                )

        return {
            "issues": clusters,
            "total": len(clusters),
            "message": "These are the consolidated issues you contributed to. Multiple reports of the same problem are combined into one entry.",
        }


@router.get("/submissions/{submission_id}/status")
async def get_submission_status(submission_id: uuid.UUID):
    """Get detailed status of a citizen's submission."""
    from app.infrastructure.database.repositories.submission import SubmissionRepository
    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        repo = SubmissionRepository(session)
        submission = await repo.get_by_id(submission_id)

        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found",
            )

        status_progress = {
            "received": 0.1,
            "normalized": 0.15,
            "location_resolved": 0.2,
            "understood": 0.25,
            "needs_clarification": 0.3,
            "waiting_for_citizen": 0.35,
            "assessed": 0.4,
            "authenticity_scored": 0.5,
            "clustered": 0.6,
            "enriched": 0.7,
            "prioritized": 0.8,
            "recommended": 0.9,
            "ready_for_review": 0.95,
            "completed": 1.0,
        }

        progress = status_progress.get(submission.status.value, 0.0)

        status_messages = {
            "received": "Your complaint has been received and is being processed.",
            "normalized": "We are analyzing your complaint.",
            "location_resolved": "We have identified the location of your issue.",
            "understood": "Our AI has understood your complaint.",
            "needs_clarification": "We need a bit more information to help you better.",
            "waiting_for_citizen": "Waiting for your response to our questions.",
            "assessed": "Your complaint has been assessed.",
            "authenticity_scored": "We have verified the authenticity of your complaint.",
            "clustered": "Your complaint has been grouped with similar reports.",
            "enriched": "We have gathered additional context for your issue.",
            "prioritized": "Your complaint has been prioritized.",
            "recommended": "We have prepared recommendations for action.",
            "ready_for_review": "Your complaint is ready for officer review.",
            "completed": "Your complaint has been processed.",
        }

        return {
            "submission_id": str(submission.id),
            "status": submission.status.value,
            "progress": progress,
            "status_message": status_messages.get(submission.status.value, "Processing your complaint."),
            "created_at": submission.created_at.isoformat(),
            "updated_at": submission.updated_at.isoformat(),
        }
