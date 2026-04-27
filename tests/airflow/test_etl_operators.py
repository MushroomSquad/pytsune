from __future__ import annotations

import asyncio
import unittest

from template.app.airflow.etl.stubs import StubConsumer, StubProducer
from template.core.application.ports.input.producer import IProducer
from template.core.application.ports.output.consumer import IConsumer
from template.core.application.use_cases.etl_use_case import ETLUseCase
from template.infrastructure.queue import AsyncQueue


class ETLContractsTestCase(unittest.TestCase):
    def test_stubs_match_ports(self) -> None:
        self.assertIsInstance(StubProducer(), IProducer)
        self.assertIsInstance(StubConsumer(), IConsumer)


class ETLUseCaseTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_run_transfers_all_items_and_drains_queue(self) -> None:
        producer = StubProducer(
            items=[
                {"id": "record-1", "payload": "alpha"},
                {"id": "record-2", "payload": "beta"},
            ]
        )
        consumer = StubConsumer()
        queue: asyncio.Queue[object] = asyncio.Queue()

        await ETLUseCase(producer=producer, consumer=consumer, queue=queue).run()

        self.assertEqual(
            consumer.items,
            [
                {"id": "record-1", "payload": "alpha"},
                {"id": "record-2", "payload": "beta"},
            ],
        )
        self.assertTrue(queue.empty())


class AsyncQueueTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_round_trip(self) -> None:
        queue = AsyncQueue[str](maxsize=1)

        await queue.put("demo")
        self.assertTrue(queue.full())

        item = await queue.get()
        self.assertEqual(item, "demo")
        self.assertTrue(queue.empty())
