from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

LOGGER = logging.getLogger(__name__)


class StubProducer:
    def __init__(self, items: list[dict[str, Any]] | None = None) -> None:
        self._items = items or [
            {"id": "record-1", "payload": "alpha"},
            {"id": "record-2", "payload": "beta"},
        ]

    async def produce(self) -> AsyncIterator[Any]:
        for item in self._items:
            yield item


class StubConsumer:
    def __init__(self) -> None:
        self.items: list[Any] = []

    async def consume(self, item: Any) -> None:
        self.items.append(item)
        LOGGER.info("Consumed item: %s", item)
