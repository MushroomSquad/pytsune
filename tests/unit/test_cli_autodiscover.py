from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("typer")

import typer
from typer.testing import CliRunner

from template.app.adapters.input.cli.cli import autodiscover


runner = CliRunner()


def test_autodiscover_registers_only_valid_command_modules(
    tmp_path: Path,
    monkeypatch,
) -> None:
    package_root = tmp_path / "temp_commands"
    package_root.mkdir()
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "valid.py").write_text(
        "\n".join(
            [
                "import typer",
                "app = typer.Typer()",
                "@app.command()",
                "def ping() -> None:",
                '    print("pong")',
            ]
        ),
        encoding="utf-8",
    )
    (package_root / "no_app.py").write_text("VALUE = 1", encoding="utf-8")
    (package_root / "broken.py").write_text("raise RuntimeError('boom')", encoding="utf-8")

    monkeypatch.syspath_prepend(str(tmp_path))

    app = typer.Typer()
    autodiscover(
        app,
        package_name="temp_commands",
        package_path=[str(package_root)],
    )

    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "valid" in result.stdout
    assert "no-app" not in result.stdout
    assert "broken" not in result.stdout
