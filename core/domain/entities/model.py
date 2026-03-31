from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from uuid import uuid4

from template.core.domain.events.event import ItemCreatedEvent
from template.core.domain.exceptions.exception import ItemValidationError


@dataclass(slots=True)
class Item:
    name: str
    value: float
    id: str = field(default_factory=lambda: str(uuid4()))

    def validate(self) -> "Item":
        if not self.name or not self.name.strip():
            raise ItemValidationError("Item name must not be empty.")
        if not isinstance(self.value, int | float):
            raise ItemValidationError("Item value must be numeric.")
        if not isfinite(float(self.value)):
            raise ItemValidationError("Item value must be finite.")
        return self

    def to_event(self) -> ItemCreatedEvent:
        return ItemCreatedEvent(item_id=self.id, name=self.name, value=float(self.value))
