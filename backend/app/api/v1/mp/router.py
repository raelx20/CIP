import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.dto.dashboard import DashboardOverview, IssueCountByCategory
from app.application.dto.issue import IssueClusterResponse, IssueDetailResponse, IssueListResponse
from app.application.dto.priority import PriorityRankingResponse
from app.application.dto.copilot import CopilotQuery, CopilotResponse
from app.api.dependencies import require_mp

router = APIRouter()


@router.get("/dashboard", response_model=DashboardOverview)
async def get_mp_dashboard(
    constituency: str | None = None,
    current_user: dict = Depends(require_mp),
):
    """Get MP constituency-scoped dashboard overview."""
    from app.infrastructure.database.repositories.submission import SubmissionRepository
    from app.infrastructure.database.repositories.issue import IssueClusterRepository
    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        submission_repo = SubmissionRepository(session)
        issue_repo = IssueClusterRepository(session)

        total_submissions = await submission_repo.count()
        pending = await submission_repo.get_needing_review(limit=1000)
        active_clusters = await issue_repo.get_active_clusters(limit=1000)

        return DashboardOverview(
            total_submissions=total_submissions,
            pending_review=len(pending),
            active_clusters=len(active_clusters),
            high_priority=0,
            issues_by_category=[],
            recent_submissions=total_submissions,
            avg_priority_score=None,
        )


@router.get("/issues", response_model=IssueListResponse)
async def get_mp_issues(
    constituency: str | None = None,
    category: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(require_mp),
):
    """Get consolidated issue clusters for MP (ONE entry per unique problem)."""
    from app.infrastructure.database.repositories.issue import IssueClusterRepository
    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        repo = IssueClusterRepository(session)
        clusters = await repo.get_active_clusters(skip=skip, limit=limit)

        return IssueListResponse(
            issues=[
                IssueClusterResponse(
                    id=c.id,
                    title=c.title,
                    summary=c.summary,
                    category=c.category,
                    subcategory=c.subcategory,
                    latitude=c.latitude,
                    longitude=c.longitude,
                    formatted_address=c.formatted_address,
                    raw_submission_count=c.raw_submission_count,
                    trusted_demand=c.trusted_demand,
                    suspicious_demand=c.suspicious_demand,
                    affected_population=c.affected_population,
                    severity=c.severity,
                    urgency=c.urgency,
                    lifecycle_state=c.lifecycle_state.value,
                    confidence=c.confidence,
                    first_reported=c.first_reported,
                    latest_report=c.latest_report,
                    created_at=c.created_at,
                )
                for c in clusters
            ],
            total=len(clusters),
            skip=skip,
            limit=limit,
        )


@router.get("/issues/{issue_id}", response_model=IssueDetailResponse)
async def get_mp_issue_detail(
    issue_id: uuid.UUID,
    current_user: dict = Depends(require_mp),
):
    """Get detailed information about a specific consolidated issue."""
    from app.infrastructure.database.repositories.issue import IssueClusterRepository
    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        repo = IssueClusterRepository(session)
        cluster = await repo.get_by_id(issue_id)

        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found",
            )

        return IssueDetailResponse(
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
            administrative_areas=cluster.administrative_areas,
            demand_velocity=cluster.demand_velocity,
            persistence=cluster.persistence,
        )


@router.get("/priorities", response_model=PriorityRankingResponse)
async def get_mp_priorities(
    constituency: str | None = None,
    category: str | None = None,
    min_level: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(require_mp),
):
    """Get ranked priority list for MP constituency."""
    return PriorityRankingResponse(
        rankings=[],
        total=0,
        skip=skip,
        limit=limit,
        scoring_version="1.0",
    )


@router.get("/hotspots")
async def get_mp_hotspots(
    constituency: str | None = None,
    category: str | None = None,
    current_user: dict = Depends(require_mp),
):
    """Get geographic hotspots for MP constituency."""
    from app.infrastructure.database.repositories.issue import IssueClusterRepository
    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        repo = IssueClusterRepository(session)
        clusters = await repo.get_active_clusters(limit=1000)

        hotspots = []
        for c in clusters:
            if c.latitude and c.longitude:
                hotspots.append({
                    "latitude": c.latitude,
                    "longitude": c.longitude,
                    "cluster_id": str(c.id),
                    "title": c.title,
                    "category": c.category,
                    "submission_count": c.raw_submission_count,
                    "severity": c.severity,
                    "urgency": c.urgency,
                })

        return {"hotspots": hotspots}


@router.post("/copilot", response_model=CopilotResponse)
async def mp_copilot_query(
    query: CopilotQuery,
    current_user: dict = Depends(require_mp),
):
    """Query the grounded MP copilot."""
    from app.application.workflows.chat import ChatWorkflow

    workflow = ChatWorkflow()

    response = await workflow.process_admin_copilot_query(
        admin_id=uuid.uuid4(),
        query=query.query,
        constituency=query.constituency,
    )

    return CopilotResponse(
        answer=response["answer"],
        citations=response.get("citations", []),
        uncertainty=response.get("uncertainty"),
        sources_used=response.get("sources_used", []),
    )
