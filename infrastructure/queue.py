from __future__ import annotations

from asyncio import Queue
from typing import Generic, TypeVar


T = TypeVar("T")


class AsyncQueue(Generic[T]):
    def __init__(self, maxsize: int = 0) -> None:
        self._queue: Queue[T] = Queue(maxsize=maxsize)

    async def put(self, item: T) -> None:
        await self._queue.put(item)

    async def get(self) -> T:
        return await self._queue.get()

    @property
    def maxsize(self) -> int:
        return self._queue.maxsize

    def full(self) -> bool:
        return self._queue.full()

    def empty(self) -> bool:
        return self._queue.empty()
