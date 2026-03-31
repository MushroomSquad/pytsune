from __future__ import annotations

from template.app.facade import AppFacade


class MainPresenter:
    def __init__(self, facade: AppFacade) -> None:
        self._facade = facade
        self._view = None

    def bind(self, view: object) -> None:
        self._view = view

    def load_items(self) -> list[str]:
        return [f"{item.name}: {item.value}" for item in self._facade.list_items()]

    def create_item(self, name: str, value: float) -> str:
        item = self._facade.create_item(name, value)
        return f"{item.name}: {item.value}"
