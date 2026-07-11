import asyncio
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class WorkerRunner:
    def __init__(self, max_concurrent: int = 4):
        self.max_concurrent = max_concurrent
        self.tasks: dict[str, Callable] = {}
        self.running = False
        self.semaphore = asyncio.Semaphore(max_concurrent)

    def register_task(self, task_name: str, handler: Callable):
        self.tasks[task_name] = handler
        logger.info(f"Registered task: {task_name}")

    async def start(self):
        self.running = True
        logger.info(f"Worker started with max_concurrent={self.max_concurrent}")

    async def stop(self):
        self.running = False
        logger.info("Worker stopped")

    async def execute_task(self, task_name: str, payload: dict[str, Any]) -> Any:
        if task_name not in self.tasks:
            raise ValueError(f"Unknown task: {task_name}")

        handler = self.tasks[task_name]

        async with self.semaphore:
            try:
                result = await handler(payload)
                logger.info(f"Task {task_name} completed")
                return result
            except Exception as e:
                logger.error(f"Task {task_name} failed: {e}")
                raise
