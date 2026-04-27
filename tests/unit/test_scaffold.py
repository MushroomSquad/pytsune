from __future__ import annotations

import io
import tarfile
import tomllib
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scaffold import (
    _copy_template,
    _download_template,
    _should_include,
    _tty_input,
    _write_pyproject,
    ask,
    build_dependencies,
    main,
    validate_project_name,
)


@pytest.fixture(autouse=True)
def _mock_urlretrieve() -> None:
    with patch("scaffold.urllib.request.urlretrieve") as urlretrieve_mock:
        urlretrieve_mock.side_effect = AssertionError("unexpected network call")
        yield


def test_build_dependencies_telegram_postgresql() -> None:
    result = build_dependencies("telegram", "postgresql", [])

    assert "aiogram" in result
    assert "asyncpg" in result
    assert "sqlalchemy[asyncio]" in result
    assert "pydantic-settings" in result


def test_build_dependencies_airflow_none() -> None:
    result = build_dependencies("airflow", "none", [])

    assert "apache-airflow>=2.3" in result
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


def test_should_include_lib() -> None:
    assert _should_include("app/lib/main.py", "lib") is True
    assert _should_include("app/cli/main.py", "lib") is False


@pytest.mark.parametrize(
    ("project_type", "included", "excluded"),
    [
        ("cli", "app/adapters/input/cli/cli.py", "app/adapters/input/rest/controller.py"),
        ("web", "app/adapters/input/rest/controller.py", "app/adapters/input/cli/cli.py"),
        ("robyn", "app/adapters/input/rest/robyn_controller.py", "app/adapters/input/cli/cli.py"),
        ("telegram", "app/adapters/input/telegram/adapter.py", "app/adapters/input/lib/client.py"),
        ("airflow", "app/adapters/input/airflow/operators.py", "app/adapters/input/telegram/adapter.py"),
        ("lib", "app/adapters/input/lib/client.py", "app/adapters/input/rest/controller.py"),
    ],
)
def test_should_include_cli(project_type: str, included: str, excluded: str) -> None:
    assert _should_include(included, project_type) is True
    assert _should_include(excluded, project_type) is False


def test_build_dependencies_robyn_none() -> None:
    result = build_dependencies("robyn", "none", [])

    assert "robyn" in result
    assert "pydantic-settings" in result
    assert "fastapi" not in result
    assert "uvicorn" not in result


def test_build_dependencies_robyn_sqlite() -> None:
    result = build_dependencies("robyn", "sqlite", [])

    assert "robyn" in result
    assert "aiosqlite" in result
    assert "sqlalchemy[asyncio]" in result
    assert "fastapi" not in result


def test_should_include_robyn_entry() -> None:
    assert _should_include("app/robyn/main.py", "robyn") is True
    assert _should_include("app/robyn/main.py", "web") is False
    assert _should_include("app/web/main.py", "robyn") is False


def test_copy_template_creates_structure(tmp_path: Path) -> None:
    src_root = tmp_path / "src"
    dst_root = tmp_path / "dst"
    (src_root / "app/lib").mkdir(parents=True)
    (src_root / "app/adapters/input/lib").mkdir(parents=True)
    (src_root / "app/adapters/input/cli/commands").mkdir(parents=True)
    (src_root / "core/domain").mkdir(parents=True)
    (src_root / "infrastructure/config").mkdir(parents=True)
    (src_root / "tests/unit").mkdir(parents=True)
    (src_root / "README.md").write_text("template for pytsune", encoding="utf-8")
    (src_root / "__init__.py").write_text('"""template"""', encoding="utf-8")
    (src_root / "__main__.py").write_text("from template.app.lib.main import run", encoding="utf-8")
    (src_root / "app/__init__.py").write_text("", encoding="utf-8")
    (src_root / "app/facade.py").write_text("import template", encoding="utf-8")
    (src_root / "app/lib/main.py").write_text("from template import app", encoding="utf-8")
    (src_root / "app/adapters/__init__.py").write_text("", encoding="utf-8")
    (src_root / "app/adapters/input/__init__.py").write_text("", encoding="utf-8")
    (src_root / "app/adapters/input/lib/client.py").write_text("template", encoding="utf-8")
    (src_root / "app/adapters/input/cli/cli.py").write_text("cli", encoding="utf-8")
    (src_root / "app/adapters/input/cli/args.py").write_text("args", encoding="utf-8")
    (src_root / "app/adapters/input/cli/commands/items.py").write_text("items", encoding="utf-8")
    (src_root / "core/domain/model.py").write_text("template", encoding="utf-8")
    (src_root / "infrastructure/config/settings.py").write_text("TEMPLATE", encoding="utf-8")
    (src_root / "tests/unit/test_example.py").write_text("template", encoding="utf-8")

    _copy_template(src_root, dst_root, "demo_project", "lib")

    assert (dst_root / "demo_project/core/domain/model.py").exists()
    assert (dst_root / "demo_project/infrastructure/config/settings.py").exists()
    assert (dst_root / "demo_project/app/lib/main.py").exists()
    assert (dst_root / "demo_project/app/adapters/input/lib/client.py").exists()
    assert not (dst_root / "demo_project/app/adapters/input/cli/cli.py").exists()
    assert not (dst_root / "demo_project/app/adapters/input/cli/commands/items.py").exists()
    assert (dst_root / "main.py").exists()


def test_name_substitution(tmp_path: Path) -> None:
    src_root = tmp_path / "src"
    dst_root = tmp_path / "dst"
    (src_root / "app/lib").mkdir(parents=True)
    (src_root / "core/domain").mkdir(parents=True)
    (src_root / "infrastructure").mkdir(parents=True)
    (src_root / "README.md").write_text("pytsune template TEMPLATE", encoding="utf-8")
    (src_root / "__init__.py").write_text("", encoding="utf-8")
    (src_root / "__main__.py").write_text("from template.app.lib.main import run", encoding="utf-8")
    (src_root / "app/__init__.py").write_text("", encoding="utf-8")
    (src_root / "app/facade.py").write_text("template pytsune", encoding="utf-8")
    (src_root / "app/lib/main.py").write_text("template pytsune", encoding="utf-8")
    (src_root / "app/adapters").mkdir(parents=True)
    (src_root / "app/adapters/__init__.py").write_text("", encoding="utf-8")
    (src_root / "app/adapters/input").mkdir(parents=True)
    (src_root / "app/adapters/input/__init__.py").write_text("", encoding="utf-8")
    (src_root / "core/domain/model.toml").write_text('name = "pytsune"\nmodule = "template"', encoding="utf-8")

    _copy_template(src_root, dst_root, "demo_project", "lib")

    assert "pytsune" not in (dst_root / "README.md").read_text(encoding="utf-8")
    assert "template" not in (dst_root / "demo_project/app/lib/main.py").read_text(encoding="utf-8")
    assert "pytsune" not in (
        dst_root / "demo_project/core/domain/model.toml"
    ).read_text(encoding="utf-8")


def test_copy_template_includes_airflow_operator_package(tmp_path: Path) -> None:
    src_root = tmp_path / "src"
    dst_root = tmp_path / "dst"
    (src_root / "app/airflow/etl").mkdir(parents=True)
    (src_root / "app/adapters/input/airflow").mkdir(parents=True)
    (src_root / "core/application/ports/input").mkdir(parents=True)
    (src_root / "core/application/ports/output").mkdir(parents=True)
    (src_root / "core/application/use_cases").mkdir(parents=True)
    (src_root / "core/domain").mkdir(parents=True)
    (src_root / "infrastructure").mkdir(parents=True)
    (src_root / "tests/airflow").mkdir(parents=True)
    (src_root / "README.md").write_text("template", encoding="utf-8")
    (src_root / "__init__.py").write_text("", encoding="utf-8")
    (src_root / "__main__.py").write_text("from template.app.airflow.dag import run", encoding="utf-8")
    (src_root / "app/__init__.py").write_text("", encoding="utf-8")
    (src_root / "app/facade.py").write_text("template", encoding="utf-8")
    (src_root / "app/adapters/__init__.py").write_text("", encoding="utf-8")
    (src_root / "app/adapters/input/__init__.py").write_text("", encoding="utf-8")
    (src_root / "app/airflow/dag.py").write_text("template", encoding="utf-8")
    (src_root / "app/airflow/etl/__init__.py").write_text("", encoding="utf-8")
    (src_root / "app/airflow/etl/operators.py").write_text("template", encoding="utf-8")
    (src_root / "app/airflow/etl/dag_etl.py").write_text("template", encoding="utf-8")
    (src_root / "app/airflow/etl/stubs.py").write_text("template", encoding="utf-8")
    (src_root / "app/adapters/input/airflow/__init__.py").write_text("", encoding="utf-8")
    (src_root / "app/adapters/input/airflow/operators.py").write_text("template", encoding="utf-8")
    (src_root / "core/application/ports/input/producer.py").write_text("template", encoding="utf-8")
    (src_root / "core/application/ports/output/consumer.py").write_text("template", encoding="utf-8")
    (src_root / "core/application/use_cases/etl_use_case.py").write_text("template", encoding="utf-8")
    (src_root / "infrastructure/queue.py").write_text("template", encoding="utf-8")
    (src_root / "tests/airflow/__init__.py").write_text("", encoding="utf-8")

    _copy_template(src_root, dst_root, "demo_project", "airflow")

    assert (dst_root / "demo_project/app/airflow/dag.py").exists()
    assert (dst_root / "demo_project/app/airflow/etl/__init__.py").exists()
    assert (dst_root / "demo_project/app/airflow/etl/operators.py").exists()
    assert (dst_root / "demo_project/app/airflow/etl/dag_etl.py").exists()
    assert (dst_root / "demo_project/app/airflow/etl/stubs.py").exists()
    assert (dst_root / "demo_project/app/adapters/input/airflow/__init__.py").exists()
    assert (dst_root / "demo_project/app/adapters/input/airflow/operators.py").exists()
    assert (dst_root / "demo_project/core/application/ports/input/producer.py").exists()
    assert (dst_root / "demo_project/core/application/ports/output/consumer.py").exists()
    assert (dst_root / "demo_project/core/application/use_cases/etl_use_case.py").exists()
    assert (dst_root / "demo_project/infrastructure/queue.py").exists()
    assert (dst_root / "tests/airflow/__init__.py").exists()


def test_write_pyproject_lib_none(tmp_path: Path) -> None:
    deps = _write_pyproject(tmp_path, "demo_project", "lib", "none", [])
    pyproject = tomllib.loads((tmp_path / "pyproject.toml").read_text(encoding="utf-8"))

    assert deps == ["pydantic-settings"]
    assert "pydantic-settings" in pyproject["project"]["dependencies"]
    assert "fastapi" not in pyproject["project"]["dependencies"]
    assert "scripts" not in pyproject.get("project", {})


def test_write_pyproject_web_postgresql(tmp_path: Path) -> None:
    _write_pyproject(tmp_path, "demo_project", "web", "postgresql", ["httpx"])
    pyproject = tomllib.loads((tmp_path / "pyproject.toml").read_text(encoding="utf-8"))

    dependencies = pyproject["project"]["dependencies"]
    assert "fastapi" in dependencies
    assert "uvicorn" in dependencies
    assert "asyncpg" in dependencies
    assert "sqlalchemy[asyncio]" in dependencies
    assert "httpx" in dependencies


def test_write_pyproject_cli_adds_console_script(tmp_path: Path) -> None:
    _write_pyproject(tmp_path, "demo_project", "cli", "none", [])
    pyproject = tomllib.loads((tmp_path / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["scripts"]["demo_project"] == "demo_project.app.adapters.input.cli:app"


def test_write_pyproject_airflow_uses_versioned_dependency(tmp_path: Path) -> None:
    _write_pyproject(tmp_path, "demo_project", "airflow", "none", [])
    pyproject = tomllib.loads((tmp_path / "pyproject.toml").read_text(encoding="utf-8"))

    assert "apache-airflow>=2.3" in pyproject["project"]["dependencies"]


def test_download_template_extracts_top_level_dir(tmp_path: Path) -> None:
    archive_path = tmp_path / "archive.tar.gz"
    extracted = tmp_path / "template-main"
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    extracted.mkdir()
    (extracted / "README.md").write_text("hello", encoding="utf-8")
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(extracted, arcname="template-main")
    shutil_src = archive_path

    def fake_urlretrieve(url: str, destination: Path) -> tuple[str, object]:
        Path(destination).write_bytes(shutil_src.read_bytes())
        return str(destination), object()

    with patch("scaffold.urllib.request.urlretrieve", side_effect=fake_urlretrieve):
        result = _download_template(work_dir)

    assert result.name == "template-main"
    assert (result / "README.md").exists()


def test_ask_valid_choice() -> None:
    with patch("scaffold._tty_input", side_effect=["wrong", "web"]):
        assert ask("Project type", ("cli", "web")) == "web"


def test_tty_input_uses_builtin_input_when_stdin_is_tty() -> None:
    stdin = Mock()
    stdin.isatty.return_value = True

    with patch("scaffold.sys.stdin", stdin), patch("builtins.input", return_value="demo") as input_mock:
        assert _tty_input("Project name: ") == "demo"

    input_mock.assert_called_once_with("Project name: ")


def test_tty_input_reads_from_dev_tty_when_stdin_is_not_tty() -> None:
    stdin = Mock()
    stdin.isatty.return_value = False
    tty_stream = io.StringIO("telegram\n")

    with (
        patch("scaffold.sys.stdin", stdin),
        patch("pathlib.Path.open", return_value=tty_stream) as open_mock,
        patch("builtins.print") as print_mock,
    ):
        assert _tty_input("Project type: ") == "telegram"

    open_mock.assert_called_once_with(encoding="utf-8")
    print_mock.assert_called_once_with("Project type: ", end="", flush=True)


def test_tty_input_raises_human_readable_eoferror_without_dev_tty() -> None:
    stdin = Mock()
    stdin.isatty.return_value = False

    with patch("scaffold.sys.stdin", stdin), patch(
        "pathlib.Path.open", side_effect=OSError("no tty")
    ):
        with pytest.raises(EOFError, match="Interactive input is unavailable"):
            _tty_input("Database: ")


@patch("scaffold.shutil.which", return_value="/usr/bin/uv")
@patch("scaffold._tty_input", side_effect=EOFError("Interactive input is unavailable."))
def test_main_returns_error_without_traceback_on_eoferror(
    tty_input_mock: Mock, which_mock: Mock, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main() == 1

    captured = capsys.readouterr()
    assert "Interactive input is unavailable." in captured.err
    assert "Traceback" not in captured.err
    which_mock.assert_called_once_with("uv")
    tty_input_mock.assert_called_once_with("Project name: ")


def test_validate_project_name_accepts_valid() -> None:
    assert validate_project_name("my_project") is True


def test_validate_project_name_rejects_invalid() -> None:
    assert validate_project_name("MyProject") is False
    assert validate_project_name("my-project") is False
    assert validate_project_name("123foo") is False
