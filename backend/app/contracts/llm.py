from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def embed(
        self,
        text: str,
        **kwargs,
    ) -> list[float]:
        pass

    @abstractmethod
    async def embed_batch(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
