from __future__ import annotations

from typing import Protocol

from template.core.domain.entities.model import Item


class ItemRepositoryPort(Protocol):
    def save(self, item: Item) -> Item: ...
    def get(self, item_id: str) -> Item | None: ...
    def list(self) -> list[Item]: ...
