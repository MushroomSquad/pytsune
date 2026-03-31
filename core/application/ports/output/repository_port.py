from __future__ import annotations

from abc import ABC, abstractmethod

from template.core.domain.entities.model import Item


class ItemRepositoryPort(ABC):
    @abstractmethod
    def save(self, item: Item) -> Item:
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: str) -> Item | None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Item]:
        raise NotImplementedError
