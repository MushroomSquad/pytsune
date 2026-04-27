from __future__ import annotations

from typing import Protocol

from template.core.application.dtos.dto import CreateItemDTO, ItemResponseDTO


class ItemInputPort(Protocol):
    def create_item(self, dto: CreateItemDTO) -> ItemResponseDTO: ...
    def get_item(self, item_id: str) -> ItemResponseDTO: ...
    def list_items(self) -> list[ItemResponseDTO]: ...
