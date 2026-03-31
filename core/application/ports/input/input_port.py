from __future__ import annotations

from abc import ABC, abstractmethod

from template.core.application.dtos.dto import CreateItemDTO, ItemResponseDTO


class ItemInputPort(ABC):
    @abstractmethod
    def create_item(self, dto: CreateItemDTO) -> ItemResponseDTO:
        raise NotImplementedError

    @abstractmethod
    def get_item(self, item_id: str) -> ItemResponseDTO:
        raise NotImplementedError

    @abstractmethod
    def list_items(self) -> list[ItemResponseDTO]:
        raise NotImplementedError
