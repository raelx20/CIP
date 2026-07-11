from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class JobQueue(ABC):
    @abstractmethod
    async def enqueue(
        self,
        task_name: str,
        payload: dict[str, Any],
        priority: int = 0,
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    async def dequeue(
        self,
        **kwargs,
    ) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def complete(
        self,
        job_id: str,
        result: Any = None,
        **kwargs,
    ) -> bool:
        pass

    @abstractmethod
    async def fail(
        self,
        job_id: str,
        error: str | None = None,
        **kwargs,
    ) -> bool:
        pass

    @abstractmethod
    async def get_status(
        self,
        job_id: str,
        **kwargs,
    ) -> JobStatus:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass
