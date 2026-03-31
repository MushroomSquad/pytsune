from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json

import typer

from template.app.facade import AppFacade


app = typer.Typer(help="Manage items.")


def _facade_from_ctx(ctx: typer.Context) -> AppFacade:
    facade = ctx.obj
    if not isinstance(facade, AppFacade):
        raise typer.BadParameter("CLI application state is not initialized.")
    return facade


def _to_json(payload: object) -> str:
    if isinstance(payload, list):
        return json.dumps(
            [asdict(item) if is_dataclass(item) else item for item in payload],
            ensure_ascii=True,
        )
    return json.dumps(asdict(payload) if is_dataclass(payload) else payload, ensure_ascii=True)


@app.command("create")
def create_item(
    ctx: typer.Context,
    name: str,
    value: float,
) -> None:
    """Create a new item."""
    print(_to_json(_facade_from_ctx(ctx).create_item(name, value)))


@app.command("get")
def get_item(
    ctx: typer.Context,
    item_id: str,
) -> None:
    """Fetch an item by id."""
    print(_to_json(_facade_from_ctx(ctx).get_item(item_id)))


@app.command("list")
def list_items(
    ctx: typer.Context,
    debug_state: bool = typer.Option(
        False,
        "--debug-state",
        hidden=True,
        help="Print the injected application state type.",
    ),
) -> None:
    """List all items."""
    if debug_state:
        print(type(ctx.obj).__name__)
        return
    print(_to_json(_facade_from_ctx(ctx).list_items()))
