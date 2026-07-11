from abc import ABC, abstractmethod
from typing import Any


class CacheProvider(ABC):
    @abstractmethod
    async def get(
        self,
        key: str,
        **kwargs,
    ) -> Any | None:
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        **kwargs,
    ) -> bool:
        pass

    @abstractmethod
    async def delete(
        self,
        key: str,
        **kwargs,
    ) -> bool:
        pass

    @abstractmethod
    async def exists(
        self,
        key: str,
        **kwargs,
    ) -> bool:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
