from __future__ import annotations

from dataclasses import dataclass

from template.core.domain.entities.model import Item


@dataclass(slots=True)
class CreateItemDTO:
    name: str
    value: float


ApplicationDTO = CreateItemDTO


@dataclass(slots=True)
class ItemResponseDTO:
    id: str
    name: str
    value: float

    @classmethod
    def from_item(cls, item: Item) -> "ItemResponseDTO":
        return cls(id=item.id, name=item.name, value=item.value)
