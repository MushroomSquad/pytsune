from __future__ import annotations

from template.app.adapters.input.cli.cli import run as run_cli


def run(argv: list[str] | None = None) -> int:
    return run_cli(argv)
