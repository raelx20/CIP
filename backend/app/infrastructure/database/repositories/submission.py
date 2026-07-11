import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.submission import Submission, SubmissionStatus
from app.infrastructure.database.repositories.base import BaseRepository


class SubmissionRepository(BaseRepository[Submission]):
    def __init__(self, session: AsyncSession):
        super().__init__(Submission, session)

    async def get_by_citizen(
        self, citizen_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[Submission]:
        result = await self.session.execute(
            select(Submission)
            .where(Submission.citizen_id == citizen_id)
            .order_by(Submission.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_status(
        self, status: SubmissionStatus, skip: int = 0, limit: int = 100
    ) -> Sequence[Submission]:
        result = await self.session.execute(
            select(Submission)
            .where(Submission.status == status)
            .order_by(Submission.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_with_media(self, submission_id: uuid.UUID) -> Submission | None:
        result = await self.session.execute(
            select(Submission)
            .options(selectinload(Submission.media))
            .where(Submission.id == submission_id)
        )
        return result.scalar_one_or_none()

    async def get_pending_processing(self, limit: int = 50) -> Sequence[Submission]:
        result = await self.session.execute(
            select(Submission)
            .where(
                Submission.status.in_([
                    SubmissionStatus.RECEIVED,
                    SubmissionStatus.NORMALIZED,
                ])
            )
            .order_by(Submission.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_needing_review(self, skip: int = 0, limit: int = 100) -> Sequence[Submission]:
        result = await self.session.execute(
            select(Submission)
            .where(
                Submission.status.in_([
                    SubmissionStatus.NEEDS_REVIEW,
                    SubmissionStatus.READY_FOR_REVIEW,
                ])
            )
            .order_by(Submission.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
