from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scaffold import (
    add_dependencies,
    ask,
    build_dependencies,
    scaffold_project,
    validate_project_name,
)


def test_build_dependencies_telegram_postgresql() -> None:
    result = build_dependencies("telegram", "postgresql", [])

    assert "aiogram" in result
    assert "asyncpg" in result
    assert "sqlalchemy[asyncio]" in result
    assert "pydantic-settings" in result


def test_build_dependencies_airflow_none() -> None:
    result = build_dependencies("airflow", "none", [])

    assert "apache-airflow" in result
    assert "pydantic-settings" in result
    assert "asyncpg" not in result
    assert "aiosqlite" not in result
    assert "motor" not in result
    assert "beanie" not in result


def test_build_dependencies_web_sqlite() -> None:
    result = build_dependencies("web", "sqlite", [])

    assert "fastapi" in result
    assert "uvicorn" in result
    assert "aiosqlite" in result
    assert "sqlalchemy[asyncio]" in result


def test_build_dependencies_lib_mongodb() -> None:
    result = build_dependencies("lib", "mongodb", [])

    assert "motor" in result
    assert "beanie" in result
    assert "pydantic-settings" in result
    assert "fastapi" not in result
    assert "uvicorn" not in result
    assert "aiogram" not in result
    assert "apache-airflow" not in result


def test_ask_valid_choice() -> None:
    with patch("builtins.input", side_effect=["wrong", "web"]):
        assert ask("Project type", ("cli", "web")) == "web"


def test_validate_project_name_accepts_valid() -> None:
    assert validate_project_name("my_project") is True


def test_validate_project_name_rejects_invalid() -> None:
    assert validate_project_name("MyProject") is False
    assert validate_project_name("my-project") is False
    assert validate_project_name("123foo") is False


@patch("scaffold.subprocess.run")
def test_scaffold_project_calls_uv_init(run_mock: Mock, tmp_path: Path) -> None:
    name = "demo_project"
    target_dir = tmp_path / name

    scaffold_project(name, "web", target_dir)

    run_mock.assert_called_once_with(
        ["uv", "init", "--name", name, "--python", "3.11", str(target_dir)],
        check=True,
    )


@patch("scaffold.subprocess.run")
def test_scaffold_project_aborts_if_dir_exists(run_mock: Mock, tmp_path: Path) -> None:
    target_dir = tmp_path / "demo_project"
    target_dir.mkdir()

    with pytest.raises(FileExistsError):
        scaffold_project("demo_project", "web", target_dir)

    run_mock.assert_not_called()


@patch("scaffold.subprocess.run")
def test_add_dependencies_calls_uv_add(run_mock: Mock, tmp_path: Path) -> None:
    deps = ["fastapi", "uvicorn"]

    add_dependencies(tmp_path, deps)

    run_mock.assert_called_once_with(["uv", "add", *deps], cwd=tmp_path, check=True)


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv is unavailable")
def test_scaffold_project_integration(tmp_path: Path) -> None:
    name = "demo_project"
    target_dir = tmp_path / name

    scaffold_project(name, "cli", target_dir)

    pyproject = target_dir / "pyproject.toml"
    assert pyproject.exists()
    assert name in pyproject.read_text(encoding="utf-8")
