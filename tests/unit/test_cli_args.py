from __future__ import annotations

import pytest

pytest.importorskip("typer")

import typer
from typer.testing import CliRunner
from template.app.adapters.input.cli.args import (
    DEFAULT_ENV,
    DEFAULT_VERBOSE,
    ENV_OPTION,
    VERBOSE_OPTION,
)


runner = CliRunner()


def test_env_option_constant_builds_typer_command() -> None:
    app = typer.Typer()

    @app.command()
    def command(env: ENV_OPTION = DEFAULT_ENV) -> None:
        print(env)

    result = runner.invoke(app, ["--env", "test"])

    assert result.exit_code == 0
    assert "test" in result.stdout


def test_verbose_option_constant_builds_typer_command() -> None:
    app = typer.Typer()

    @app.command()
    def command(verbose: VERBOSE_OPTION = DEFAULT_VERBOSE) -> None:
        print(verbose)

    result = runner.invoke(app, ["--verbose"])

    assert result.exit_code == 0
    assert "True" in result.stdout
