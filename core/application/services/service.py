from __future__ import annotations

from template.core.application.dtos.dto import CreateItemDTO, ItemResponseDTO
from template.core.application.use_cases.use_case import (
    CreateItemUseCase,
    GetItemUseCase,
    ListItemsUseCase,
)


class ApplicationService:
    def __init__(
        self,
        create_use_case: CreateItemUseCase,
        get_use_case: GetItemUseCase,
        list_use_case: ListItemsUseCase,
    ) -> None:
        self._create_use_case = create_use_case
        self._get_use_case = get_use_case
        self._list_use_case = list_use_case

    def create_item(self, dto: CreateItemDTO) -> ItemResponseDTO:
        return ItemResponseDTO.from_item(self._create_use_case.execute(dto))

    def get_item(self, item_id: str) -> ItemResponseDTO:
        return ItemResponseDTO.from_item(self._get_use_case.execute(item_id))

    def list_items(self) -> list[ItemResponseDTO]:
        return [ItemResponseDTO.from_item(item) for item in self._list_use_case.execute()]
