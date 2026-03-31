from __future__ import annotations

from template.app.adapters.input.cli.cli import CliAdapter
from template.infrastructure.startup import bootstrap


def run(argv: list[str] | None = None) -> int:
    facade = bootstrap()
    adapter = CliAdapter(facade)
    return adapter.run(argv)
