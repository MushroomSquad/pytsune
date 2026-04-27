from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

try:
    from robyn import Request, Response, SubRouter
except ImportError:  # pragma: no cover - optional dependency
    class SubRouter:  # type: ignore[no-redef]
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def get(self, path: str) -> Any:
            def decorator(fn: Any) -> Any:
                return fn
            return decorator

        def post(self, path: str) -> Any:
            def decorator(fn: Any) -> Any:
                return fn
            return decorator

    class Request:  # type: ignore[no-redef]
        path_params: dict[str, str] = {}

        def json(self) -> dict[str, object]:
            return {}

    class Response:  # type: ignore[no-redef]
        def __init__(self, **kwargs: object) -> None:
            pass


from template.app.facade import AppFacade
from template.core.domain.exceptions.exception import ItemNotFoundError, ItemValidationError


class RobynController:
    def __init__(self, facade: AppFacade, router: SubRouter | None = None) -> None:
        self.facade = facade
        self.router = router or SubRouter(__file__, prefix="")

        @self.router.get("/items")
        def list_items_route(request: Request) -> list[dict[str, Any]]:
            return self._list_items()

        @self.router.get("/items/:item_id")
        def get_item_route(request: Request) -> object:
            return self._get_item(request.path_params["item_id"])

        @self.router.post("/items")
        def create_item_route(request: Request) -> object:
            return self._create_item(request)

    def _list_items(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.facade.list_items()]

    def _get_item(self, item_id: str) -> object:
        try:
            return asdict(self.facade.get_item(item_id))
        except ItemNotFoundError as exc:
            return Response(
                status_code=404,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"detail": str(exc)}),
            )

    def _create_item(self, request: Request) -> object:
        try:
            payload = request.json()
            item = self.facade.create_item(str(payload["name"]), float(payload["value"]))  # type: ignore[arg-type]
            return Response(
                status_code=201,
                headers={"Content-Type": "application/json"},
                description=json.dumps(asdict(item)),
            )
        except KeyError as exc:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"detail": f"Missing field: {exc.args[0]}"}),
            )
        except ValueError:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"detail": "Field 'value' must be a number."}),
            )
        except ItemValidationError as exc:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"detail": str(exc)}),
            )
