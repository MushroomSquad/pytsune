from __future__ import annotations

import typer

from template.app.facade import AppFacade


app = typer.Typer(help="Smoke-test commands.")


@app.command("hello")
def hello(ctx: typer.Context) -> None:
    """Confirm autodiscovery wiring is active."""
    facade = ctx.obj
    if not isinstance(facade, AppFacade):
        # TODO: revisit once the facade exposes a dedicated health-check API.
        raise typer.BadParameter("CLI application state is not initialized.")
    print("hello")
