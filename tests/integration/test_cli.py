from __future__ import annotations

import pytest

pytest.importorskip("typer")

from typer.testing import CliRunner

from template.app.adapters.input.cli import app


runner = CliRunner()


def test_root_help_lists_autodiscovered_command_groups() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "items" in result.stdout
    assert "smoke" in result.stdout


def test_ctx_obj_injection_exposes_app_facade() -> None:
    result = runner.invoke(app, ["items", "list", "--debug-state"])

    assert result.exit_code == 0
    assert "AppFacade" in result.stdout


def test_autodiscovered_smoke_group_is_available_without_cli_changes() -> None:
    result = runner.invoke(app, ["smoke", "hello"])

    assert result.exit_code == 0
    assert "hello" in result.stdout


@pytest.mark.parametrize("group_name", ["items", "smoke"])
def test_each_autodiscovered_group_exposes_help(group_name: str) -> None:
    result = runner.invoke(app, [group_name, "--help"])

    assert result.exit_code == 0
    assert group_name in result.stdout
