from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
from typing import Any

try:
    import typer
except ImportError:  # pragma: no cover - optional dependency
    typer = None

from template.app.facade import AppFacade
from template.core.domain.exceptions.exception import ItemNotFoundError, ItemValidationError


class CliAdapter:
    def __init__(self, facade: AppFacade) -> None:
        self._facade = facade
        self._app = self._build_typer_app() if typer else None

    def _build_typer_app(self) -> Any:
        app = typer.Typer(help="Template CLI")

        @app.command("create")
        def create(name: str, value: float) -> None:
            print(self._to_json(self._facade.create_item(name, value)))

        @app.command("get")
        def get(item_id: str) -> None:
            print(self._to_json(self._facade.get_item(item_id)))

        @app.command("list")
        def list_items() -> None:
            print(self._to_json(self._facade.list_items()))

        return app

    def app(self) -> Any:
        return self._app

    def run(self, argv: list[str] | None = None) -> int:
        args = list(argv or [])
        if self._app is not None:
            self._app(args=args, prog_name="python -m template cli")
            return 0

        if not args:
            print("Usage: python -m template cli [create|get|list] ...")
            return 1

        command = args.pop(0)
        try:
            if command == "create" and len(args) == 2:
                print(self._to_json(self._facade.create_item(args[0], float(args[1]))))
                return 0
            if command == "get" and len(args) == 1:
                print(self._to_json(self._facade.get_item(args[0])))
                return 0
            if command == "list" and not args:
                print(self._to_json(self._facade.list_items()))
                return 0
        except (ItemNotFoundError, ItemValidationError, ValueError) as exc:
            print(str(exc))
            return 1

        print("Usage: python -m template cli [create|get|list] ...")
        return 1

    @staticmethod
    def _to_json(payload: object) -> str:
        if isinstance(payload, list):
            return json.dumps([asdict(item) if is_dataclass(item) else item for item in payload], ensure_ascii=True)
        return json.dumps(asdict(payload) if is_dataclass(payload) else payload, ensure_ascii=True)
