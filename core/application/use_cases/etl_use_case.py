from __future__ import annotations

import asyncio
from asyncio import Queue
from typing import Any

from template.core.application.ports.input.producer import IProducer
from template.core.application.ports.output.consumer import IConsumer
from template.infrastructure.queue import AsyncQueue


_QUEUE_SENTINEL = object()


class ETLUseCase:
    def __init__(
        self,
        producer: IProducer,
        consumer: IConsumer,
        queue: Queue[Any] | AsyncQueue[Any],
    ) -> None:
        self._producer = producer
        self._consumer = consumer
        self._queue = queue

    async def _run_producer(self) -> None:
        async for item in self._producer.produce():
            await self._queue.put(item)

    async def _run_consumer(self) -> None:
        while not self._queue.empty():
            item = await self._queue.get()
            await self._consumer.consume(item)

    async def run(self) -> None:
        producer_task = asyncio.create_task(self._produce_with_signal())
        consumer_task = asyncio.create_task(self._consume_until_signal())
        await asyncio.gather(producer_task, consumer_task)

    async def _produce_with_signal(self) -> None:
        await self._run_producer()
        await self._queue.put(_QUEUE_SENTINEL)

    async def _consume_until_signal(self) -> None:
        while True:
            item = await self._queue.get()
            if item is _QUEUE_SENTINEL:
                break
            await self._consumer.consume(item)
