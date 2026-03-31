from __future__ import annotations

from dataclasses import asdict

try:
    from fastapi import APIRouter, HTTPException
except ImportError:  # pragma: no cover - optional dependency
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str) -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class APIRouter:
        def __init__(self) -> None:
            self.routes: list[tuple[str, str, object]] = []

        def add_api_route(self, path: str, endpoint: object, methods: list[str]) -> None:
            self.routes.append((path, ",".join(methods), endpoint))


from template.app.facade import AppFacade
from template.core.domain.exceptions.exception import ItemNotFoundError, ItemValidationError


class RestController:
    def __init__(self, facade: AppFacade, router: APIRouter | None = None) -> None:
        self.facade = facade
        self.router = router or APIRouter()
        self.router.add_api_route("/items", self.list_items, methods=["GET"])
        self.router.add_api_route("/items/{item_id}", self.get_item, methods=["GET"])
        self.router.add_api_route("/items", self.create_item, methods=["POST"])

    def list_items(self) -> list[dict[str, object]]:
        return [asdict(item) for item in self.facade.list_items()]

    def get_item(self, item_id: str) -> dict[str, object]:
        try:
            return asdict(self.facade.get_item(item_id))
        except ItemNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    def create_item(self, payload: dict[str, object]) -> dict[str, object]:
        try:
            return asdict(self.facade.create_item(str(payload["name"]), float(payload["value"])))
        except ItemValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
