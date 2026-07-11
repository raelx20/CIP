from abc import ABC, abstractmethod
from typing import Any


class ObjectStorage(ABC):
    @abstractmethod
    async def upload(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str | None = None,
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    async def download(
        self,
        bucket: str,
        key: str,
        **kwargs,
    ) -> bytes:
        pass

    @abstractmethod
    async def delete(
        self,
        bucket: str,
        key: str,
        **kwargs,
    ) -> bool:
        pass

    @abstractmethod
    async def get_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
