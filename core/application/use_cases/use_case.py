from __future__ import annotations

from template.core.application.dtos.dto import CreateItemDTO
from template.core.application.ports.output.repository_port import ItemRepositoryPort
from template.core.domain.entities.model import Item
from template.core.domain.exceptions.exception import ItemNotFoundError
from template.core.domain.services.service import ItemDomainService


class CreateItemUseCase:
    def __init__(self, repository: ItemRepositoryPort, domain_service: ItemDomainService | None = None) -> None:
        self._repository = repository
        self._domain_service = domain_service or ItemDomainService()

    def execute(self, dto: CreateItemDTO) -> Item:
        item = self._domain_service.create(dto.name, dto.value)
        return self._repository.save(item)


class GetItemUseCase:
    def __init__(self, repository: ItemRepositoryPort) -> None:
        self._repository = repository

    def execute(self, item_id: str) -> Item:
        item = self._repository.get(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        return item


class ListItemsUseCase:
    def __init__(self, repository: ItemRepositoryPort) -> None:
        self._repository = repository

    def execute(self) -> list[Item]:
        return self._repository.list()
