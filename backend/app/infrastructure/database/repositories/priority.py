import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.priority import PriorityAssessment, PriorityLevel
from app.infrastructure.database.repositories.base import BaseRepository


class PriorityRepository(BaseRepository[PriorityAssessment]):
    def __init__(self, session: AsyncSession):
        super().__init__(PriorityAssessment, session)

    async def get_by_cluster(self, cluster_id: uuid.UUID) -> PriorityAssessment | None:
        result = await self.session.execute(
            select(PriorityAssessment)
            .where(PriorityAssessment.cluster_id == cluster_id)
            .order_by(PriorityAssessment.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_ranked_priorities(
        self,
        constituency: str | None = None,
        category: str | None = None,
        min_level: PriorityLevel | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[PriorityAssessment]:
        query = select(PriorityAssessment).where(
            PriorityAssessment.rank.isnot(None)
        )

        if min_level:
            level_order = {
                PriorityLevel.CRITICAL: 0,
                PriorityLevel.HIGH: 1,
                PriorityLevel.MEDIUM: 2,
                PriorityLevel.LOW: 3,
                PriorityLevel.DEFERRED: 4,
            }
            min_rank = level_order.get(min_level, 4)
            query = query.where(
                PriorityAssessment.priority_level.in_(
                    [level for level, rank in level_order.items() if rank <= min_rank]
                )
            )

        query = query.order_by(PriorityAssessment.rank.asc()).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_latest_assessment(self, cluster_id: uuid.UUID) -> PriorityAssessment | None:
        result = await self.session.execute(
            select(PriorityAssessment)
            .where(PriorityAssessment.cluster_id == cluster_id)
            .order_by(PriorityAssessment.calculation_timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def recalculate_ranks(self) -> int:
        from sqlalchemy import update
        result = await self.session.execute(
            select(PriorityAssessment)
            .where(PriorityAssessment.rank.isnot(None))
            .order_by(PriorityAssessment.final_score.desc())
        )
        assessments = result.scalars().all()

        for i, assessment in enumerate(assessments, 1):
            assessment.rank = i

        await self.session.commit()
        return len(assessments)
