from __future__ import annotations

from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules

import typer

from template.app.adapters.input.cli.args import (
    DEFAULT_ENV,
    DEFAULT_VERBOSE,
    ENV_OPTION,
    VERBOSE_OPTION,
)
from template.app.facade import AppFacade
from template.infrastructure.config.settings import Settings
from template.infrastructure.container import ContainerFactory


COMMANDS_PACKAGE = "template.app.adapters.input.cli.commands"
COMMANDS_PATH = [str(Path(__file__).with_name("commands"))]

app = typer.Typer(help="Template CLI")


def build_facade(*, env: str = DEFAULT_ENV, verbose: bool = DEFAULT_VERBOSE) -> AppFacade:
    settings = Settings()
    if hasattr(settings, "environment"):
        settings.environment = env
    if verbose:
        settings.log_level = "DEBUG"
    return ContainerFactory(settings=settings).create_facade()


@app.callback()
def main(
    ctx: typer.Context,
    env: ENV_OPTION = DEFAULT_ENV,
    verbose: VERBOSE_OPTION = DEFAULT_VERBOSE,
) -> None:
    """Build application state for subcommands."""
    ctx.obj = build_facade(env=env, verbose=verbose)


def autodiscover(
    root_app: typer.Typer,
    *,
    package_name: str = COMMANDS_PACKAGE,
    package_path: list[str] | None = None,
) -> None:
    search_path = COMMANDS_PATH if package_path is None else package_path
    for module_info in iter_modules(search_path):
        module_name = f"{package_name}.{module_info.name}"
        try:
            module = import_module(module_name)
        except Exception:
            continue

        sub_app = getattr(module, "app", None)
        if isinstance(sub_app, typer.Typer):
            root_app.add_typer(sub_app, name=module_info.name.replace("_", "-"))


autodiscover(app)


def run(argv: list[str] | None = None) -> int:
    app(args=argv or [], prog_name="python -m template")
    return 0
