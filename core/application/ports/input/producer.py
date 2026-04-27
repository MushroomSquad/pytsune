from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any


class IProducer(ABC):
    @abstractmethod
    async def produce(self) -> AsyncIterator[Any]:
        raise NotImplementedError
