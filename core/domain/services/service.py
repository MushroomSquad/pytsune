from __future__ import annotations

from template.core.domain.entities.model import Item


class ItemDomainService:
    def create(self, name: str, value: float) -> Item:
        return Item(name=name, value=float(value)).validate()
