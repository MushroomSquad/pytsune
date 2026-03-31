from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ItemCreatedEvent:
    item_id: str
    name: str
    value: float
