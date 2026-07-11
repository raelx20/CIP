from abc import ABC, abstractmethod
from typing import Any


class NewsProvider(ABC):
    @abstractmethod
    async def search_news(
        self,
        query: str,
        location: str | None = None,
        language: str = "en",
        max_results: int = 10,
        **kwargs,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_article(
        self,
        url: str,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
