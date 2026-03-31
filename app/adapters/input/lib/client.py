from __future__ import annotations

from template.core.application.dtos.dto import ItemResponseDTO
from template.infrastructure.config.settings import Settings
from template.infrastructure.startup import bootstrap


class LibraryAdapter:
    def __init__(self, settings: Settings | None = None) -> None:
        self._facade = bootstrap(settings)

    def create_item(self, name: str, value: float) -> ItemResponseDTO:
        return self._facade.create_item(name, value)

    def get_item(self, item_id: str) -> ItemResponseDTO:
        return self._facade.get_item(item_id)

    def list_items(self) -> list[ItemResponseDTO]:
        return self._facade.list_items()

    def __enter__(self) -> "LibraryAdapter":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        return False
