from __future__ import annotations

from typing import Any, Protocol


class IConsumer(Protocol):
    async def consume(self, item: Any) -> None: ...
