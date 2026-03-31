from __future__ import annotations

import json
from pathlib import Path

from template.core.application.ports.output.repository_port import ItemRepositoryPort
from template.core.domain.entities.model import Item


class FileItemRepository(ItemRepositoryPort):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def save(self, item: Item) -> Item:
        items = {stored.id: stored for stored in self.list()}
        items[item.id] = item
        self._write(list(items.values()))
        return item

    def get(self, item_id: str) -> Item | None:
        for item in self.list():
            if item.id == item_id:
                return item
        return None

    def list(self) -> list[Item]:
        if not self._path.exists():
            return []
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        return [Item(**item) for item in payload]

    def _write(self, items: list[Item]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        serialized = [item.__dict__ for item in items]
        self._path.write_text(json.dumps(serialized, ensure_ascii=True), encoding="utf-8")
