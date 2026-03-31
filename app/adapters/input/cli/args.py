from __future__ import annotations

from typing import Annotated

import typer

from template.infrastructure.config.settings import Settings


_DEFAULT_SETTINGS = Settings()
_DEFAULT_ENV = getattr(_DEFAULT_SETTINGS, "environment", "development")
_DEFAULT_VERBOSE = _DEFAULT_SETTINGS.log_level.upper() == "DEBUG"

ENV_OPTION = Annotated[
    str,
    typer.Option(
        "--env",
        help="Application environment label.",
        show_default=True,
    ),
]
VERBOSE_OPTION = Annotated[
    bool,
    typer.Option(
        "--verbose",
        "-v",
        help="Enable verbose logging.",
        show_default=True,
    ),
]

DEFAULT_ENV = _DEFAULT_ENV
DEFAULT_VERBOSE = _DEFAULT_VERBOSE
