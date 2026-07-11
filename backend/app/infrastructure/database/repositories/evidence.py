import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.evidence import ContextEvidence, EvidenceType
from app.infrastructure.database.repositories.base import BaseRepository


class EvidenceRepository(BaseRepository[ContextEvidence]):
    def __init__(self, session: AsyncSession):
        super().__init__(ContextEvidence, session)

    async def get_by_cluster(self, cluster_id: uuid.UUID) -> Sequence[ContextEvidence]:
        result = await self.session.execute(
            select(ContextEvidence)
            .where(ContextEvidence.cluster_id == cluster_id)
            .order_by(ContextEvidence.confidence.desc())
        )
        return result.scalars().all()

    async def get_by_type(
        self, cluster_id: uuid.UUID, evidence_type: EvidenceType
    ) -> Sequence[ContextEvidence]:
        result = await self.session.execute(
            select(ContextEvidence)
            .where(
                ContextEvidence.cluster_id == cluster_id,
                ContextEvidence.evidence_type == evidence_type,
            )
            .order_by(ContextEvidence.confidence.desc())
        )
        return result.scalars().all()

    async def get_supporting_evidence(self, cluster_id: uuid.UUID) -> Sequence[ContextEvidence]:
        from app.database.models.evidence import EvidenceRelationshipType
        result = await self.session.execute(
            select(ContextEvidence)
            .where(
                ContextEvidence.cluster_id == cluster_id,
                ContextEvidence.relationship_to_issue == EvidenceRelationshipType.SUPPORTING,
            )
            .order_by(ContextEvidence.confidence.desc())
        )
        return result.scalars().all()

    async def get_contradicting_evidence(self, cluster_id: uuid.UUID) -> Sequence[ContextEvidence]:
        from app.database.models.evidence import EvidenceRelationshipType
        result = await self.session.execute(
            select(ContextEvidence)
            .where(
                ContextEvidence.cluster_id == cluster_id,
                ContextEvidence.relationship_to_issue == EvidenceRelationshipType.CONTRADICTING,
            )
            .order_by(ContextEvidence.confidence.desc())
        )
        return result.scalars().all()

    async def get_recent_evidence(
        self, cluster_id: uuid.UUID, days: int = 30
    ) -> Sequence[ContextEvidence]:
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(ContextEvidence)
            .where(
                ContextEvidence.cluster_id == cluster_id,
                ContextEvidence.retrieval_timestamp >= cutoff,
            )
            .order_by(ContextEvidence.retrieval_timestamp.desc())
        )
        return result.scalars().all()
