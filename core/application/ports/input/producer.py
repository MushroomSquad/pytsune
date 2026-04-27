from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Protocol


class IProducer(Protocol):
    async def produce(self) -> AsyncIterator[Any]: ...
