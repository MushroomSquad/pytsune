from __future__ import annotations

from template.core.domain.entities.model import Item


class InMemoryItemRepository:
    def __init__(self) -> None:
        self._items: dict[str, Item] = {}

    def save(self, item: Item) -> Item:
        self._items[item.id] = item
        return item

    def get(self, item_id: str) -> Item | None:
        return self._items.get(item_id)

    def list(self) -> list[Item]:
        return list(self._items.values())
