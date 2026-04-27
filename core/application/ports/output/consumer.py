from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IConsumer(ABC):
    @abstractmethod
    async def consume(self, item: Any) -> None:
        raise NotImplementedError
