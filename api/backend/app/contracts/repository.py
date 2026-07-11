import uuid
from typing import Any, Protocol, Sequence, TypeVar

T = TypeVar("T")


class BaseRepositoryProtocol(Protocol[T]):
    async def get_by_id(self, id: uuid.UUID) -> T | None:
        pass

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        pass

    async def create(self, obj_in: dict[str, Any]) -> T:
        pass

    async def update(self, db_obj: T, obj_in: dict[str, Any]) -> T:
        pass

    async def delete(self, id: uuid.UUID) -> bool:
        pass

    async def count(self) -> int:
        pass
