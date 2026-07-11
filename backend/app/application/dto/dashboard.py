from pydantic import BaseModel, Field


class IssueCountByCategory(BaseModel):
    category: str
    count: int


class DashboardOverview(BaseModel):
    total_submissions: int
    pending_review: int
    active_clusters: int
    high_priority: int
    issues_by_category: list[IssueCountByCategory]
    recent_submissions: int
    avg_priority_score: float | None = None


class HotspotResponse(BaseModel):
    latitude: float
    longitude: float
    cluster_count: int
    total_submissions: int
    dominant_category: str
    average_severity: float
    average_urgency: float
