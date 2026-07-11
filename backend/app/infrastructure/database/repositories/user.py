import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User, UserRole
from app.infrastructure.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_role(self, role: UserRole) -> Sequence[User]:
        result = await self.session.execute(
            select(User).where(User.role == role)
        )
        return result.scalars().all()

    async def get_by_constituency(self, constituency: str) -> Sequence[User]:
        result = await self.session.execute(
            select(User).where(User.constituency == constituency)
        )
        return result.scalars().all()
