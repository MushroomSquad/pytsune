from __future__ import annotations

from template.app.adapters.output.db.repository import InMemoryItemRepository
from template.app.adapters.output.files.file import FileItemRepository
from template.app.facade import AppFacade
from template.core.application.ports.output.repository_port import ItemRepositoryPort
from template.core.application.services.service import ApplicationService
from template.core.application.use_cases.use_case import (
    CreateItemUseCase,
    GetItemUseCase,
    ListItemsUseCase,
)
from template.infrastructure.config.settings import Settings


class ContainerFactory:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def create_repository(self) -> ItemRepositoryPort:
        if self.settings.repository_type == "file":
            return FileItemRepository(self.settings.items_file_path)
        return InMemoryItemRepository()

    def create_use_cases(self) -> dict[str, object]:
        repository = self.create_repository()
        return {
            "create": CreateItemUseCase(repository),
            "get": GetItemUseCase(repository),
            "list": ListItemsUseCase(repository),
        }

    def create_app_service(self) -> ApplicationService:
        use_cases = self.create_use_cases()
        return ApplicationService(
            create_use_case=use_cases["create"],
            get_use_case=use_cases["get"],
            list_use_case=use_cases["list"],
        )

    def create_facade(self) -> AppFacade:
        return AppFacade(self.create_app_service())
