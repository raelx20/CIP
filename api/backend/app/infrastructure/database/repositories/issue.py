import uuid
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.issue import IssueCluster, ClusterLifecycleState
from app.infrastructure.database.repositories.base import BaseRepository


class IssueClusterRepository(BaseRepository[IssueCluster]):
    def __init__(self, session: AsyncSession):
        super().__init__(IssueCluster, session)

    async def get_by_category(
        self, category: str, skip: int = 0, limit: int = 100
    ) -> Sequence[IssueCluster]:
        result = await self.session.execute(
            select(IssueCluster)
            .where(IssueCluster.category == category)
            .order_by(IssueCluster.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_state(
        self, state: ClusterLifecycleState, skip: int = 0, limit: int = 100
    ) -> Sequence[IssueCluster]:
        result = await self.session.execute(
            select(IssueCluster)
            .where(IssueCluster.lifecycle_state == state)
            .order_by(IssueCluster.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_active_clusters(self, skip: int = 0, limit: int = 100) -> Sequence[IssueCluster]:
        result = await self.session.execute(
            select(IssueCluster)
            .where(
                IssueCluster.lifecycle_state.in_([
                    ClusterLifecycleState.NEW,
                    ClusterLifecycleState.GROWING,
                    ClusterLifecycleState.STABLE,
                ])
            )
            .order_by(IssueCluster.raw_submission_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_constituency(
        self, constituency: str, skip: int = 0, limit: int = 100
    ) -> Sequence[IssueCluster]:
        result = await self.session.execute(
            select(IssueCluster)
            .where(IssueCluster.administrative_areas.op('@>')(f'["{constituency}"]'))
            .order_by(IssueCluster.raw_submission_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_high_demand(self, min_submissions: int = 5, skip: int = 0, limit: int = 100) -> Sequence[IssueCluster]:
        result = await self.session.execute(
            select(IssueCluster)
            .where(IssueCluster.raw_submission_count >= min_submissions)
            .order_by(IssueCluster.raw_submission_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_by_category(self) -> list[dict]:
        result = await self.session.execute(
            select(
                IssueCluster.category,
                func.count(IssueCluster.id).label("count")
            )
            .group_by(IssueCluster.category)
            .order_by(func.count(IssueCluster.id).desc())
        )
        return [{"category": row[0], "count": row[1]} for row in result.all()]
