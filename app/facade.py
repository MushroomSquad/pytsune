from __future__ import annotations

from template.core.application.dtos.dto import ApplicationDTO, CreateItemDTO, ItemResponseDTO
from template.core.application.ports.input.input_port import ItemInputPort


class AppFacade:
    def __init__(self, service: ItemInputPort) -> None:
        self._service = service

    def __call__(self, dto: ApplicationDTO) -> ItemResponseDTO:
        return self._service.create_item(dto)

    def create_item(self, name: str, value: float) -> ItemResponseDTO:
        return self._service.create_item(CreateItemDTO(name=name, value=value))

    def get_item(self, item_id: str) -> ItemResponseDTO:
        return self._service.get_item(item_id)

    def list_items(self) -> list[ItemResponseDTO]:
        return self._service.list_items()
