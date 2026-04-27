from __future__ import annotations

from asyncio import Queue
from typing import Any, TypeVar, cast

from template.app.airflow.etl.stubs import StubConsumer, StubProducer
from template.app.adapters.output.db.repository import InMemoryItemRepository
from template.app.adapters.output.files.file import FileItemRepository
from template.app.facade import AppFacade
from template.core.application.ports.input.producer import IProducer
from template.core.application.ports.output.consumer import IConsumer
from template.core.application.ports.output.repository_port import ItemRepositoryPort
from template.core.application.services.service import ApplicationService
from template.core.application.use_cases.etl_use_case import ETLUseCase
from template.core.application.use_cases.use_case import (
    CreateItemUseCase,
    GetItemUseCase,
    ListItemsUseCase,
)
from template.infrastructure.config.settings import Settings
from template.infrastructure.queue import AsyncQueue


T = TypeVar("T")
_SINGLETONS: dict[type[object], object] = {}


class ContainerFactory:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def create_repository(self) -> ItemRepositoryPort:
        if self.settings.repository_type == "file":
            return FileItemRepository(self.settings.items_file_path)
        return InMemoryItemRepository()

    def resolve(self, dependency: type[T]) -> T:
        if dependency is Queue:
            if dependency not in _SINGLETONS:
                _SINGLETONS[dependency] = AsyncQueue[Any]()
            return cast(T, _SINGLETONS[dependency])
        raise KeyError(f"Unsupported dependency: {dependency!r}")

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

    def create_producer(self) -> IProducer:
        return StubProducer()

    def create_consumer(self) -> IConsumer:
        return StubConsumer()

    def create_etl_use_case(self) -> ETLUseCase:
        return ETLUseCase(
            producer=self.create_producer(),
            consumer=self.create_consumer(),
            queue=self.resolve(Queue),
        )

    def create_facade(self) -> AppFacade:
        return AppFacade(self.create_app_service())
