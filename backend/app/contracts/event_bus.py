from abc import ABC, abstractmethod
from typing import Any, Callable


class EventBus(ABC):
    @abstractmethod
    async def publish(
        self,
        event_type: str,
        payload: dict[str, Any],
        **kwargs,
    ) -> None:
        pass

    @abstractmethod
    async def subscribe(
        self,
        event_type: str,
        handler: Callable,
        **kwargs,
    ) -> None:
        pass

    @abstractmethod
    async def unsubscribe(
        self,
        event_type: str,
        handler: Callable,
        **kwargs,
    ) -> None:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
