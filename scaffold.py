#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

from pathlib import Path
from typing import TextIO
from urllib.error import HTTPError, URLError
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import urllib.request


PROJECT_TYPES = ("cli", "web", "telegram", "airflow", "lib")
DATABASE_CHOICES = ("none", "sqlite", "postgresql", "mongodb")
TYPE_INCLUDES = {
    "cli": ("app/cli/", "app/adapters/input/cli/"),
    "web": ("app/web/", "app/adapters/input/rest/"),
    "telegram": ("app/telegram/", "app/adapters/input/telegram/"),
    "airflow": ("app/airflow/", "app/adapters/input/airflow/"),
    "lib": ("app/lib/", "app/adapters/input/lib/"),
}
ALWAYS_INCLUDE = (
    "__init__.py",
    "__main__.py",
    "README.md",
    "app/__init__.py",
    "app/facade.py",
    "app/adapters/__init__.py",
    "app/adapters/input/__init__.py",
    "app/adapters/output/",
    "core/",
    "infrastructure/",
    "tests/",
)

TEMPLATE_URL = "https://github.com/MushroomSquad/pytsune/archive/refs/heads/main.tar.gz"
TEMPLATE_DIR_ENV = "PYTSUNE_TEMPLATE_DIR"
NON_TEXT_EXTENSIONS = {
    ".db",
    ".der",
    ".d.er",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".png",
    ".pyc",
    ".sqlite",
    ".tar",
    ".tgz",
    ".woff",
    ".woff2",
}
SKIP_NAMES = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "PR_DESCRIPTION.md",
    "install.sh",
    "logo.png",
    "pyproject.toml",
    "scaffold.py",
}
ROOT_PACKAGE_PATHS = ("__init__.py", "__main__.py", "app/", "core/", "infrastructure/")
ENTRY_MODULES = {
    "cli": "app.adapters.input.cli.cli",
    "web": "app.web.main",
    "telegram": "app.telegram.main",
    "airflow": "app.airflow.dag",
    "lib": "app.lib.main",
}


def _tty_input(prompt: str) -> str:
    if sys.stdin.isatty():
        return input(prompt)

    try:
        tty: TextIO
        with Path("/dev/tty").open(encoding="utf-8") as tty:
            print(prompt, end="", flush=True)
            return tty.readline().rstrip("\n")
    except OSError as exc:
        raise EOFError(
            "Interactive input is unavailable. Run this command from a terminal with /dev/tty access."
        ) from exc


def ask(prompt: str, choices: tuple[str, ...]) -> str:
    choice_list = ", ".join(choices)
    while True:
        answer = _tty_input(f"{prompt} [{choice_list}]: ").strip()
        if answer in choices:
            return answer
        print(f"Invalid choice: {answer or '<empty>'}. Expected one of: {choice_list}.")


def validate_project_name(name: str) -> bool:
    return re.match(r"^[a-z_]+$", name) is not None


def build_dependencies(project_type: str, db: str, extra_libs: list[str]) -> list[str]:
    project_dependencies = {
        "cli": ["typer", "pydantic-settings"],
        "web": ["fastapi", "uvicorn", "pydantic-settings"],
        "telegram": ["aiogram", "pydantic-settings"],
        "airflow": ["apache-airflow>=2.3", "pydantic-settings"],
        "lib": ["pydantic-settings"],
    }
    database_dependencies = {
        "none": [],
        "sqlite": ["aiosqlite", "sqlalchemy[asyncio]"],
        "postgresql": ["asyncpg", "sqlalchemy[asyncio]"],
        "mongodb": ["motor", "beanie"],
    }

    deps: list[str] = []
    for dependency in [
        *project_dependencies[project_type],
        *database_dependencies[db],
        *extra_libs,
    ]:
        if dependency not in deps:
            deps.append(dependency)
    return deps


def _matches_prefix(rel: str, prefixes: tuple[str, ...]) -> bool:
    return any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in prefixes)


def _download_template(tmp_dir: Path) -> Path:
    override = os.getenv(TEMPLATE_DIR_ENV)
    if override:
        return Path(override).expanduser().resolve()

    archive_path = tmp_dir / "template.tar.gz"
    extract_root = tmp_dir / "template"
    extract_root.mkdir()

    token = os.getenv("GITHUB_TOKEN")
    if token:
        opener = urllib.request.build_opener()
        opener.addheaders = [("Authorization", f"Bearer {token}")]
        urllib.request.install_opener(opener)

    try:
        urllib.request.urlretrieve(TEMPLATE_URL, archive_path)
    except HTTPError as exc:
        if exc.code in {403, 429}:
            print(
                "GitHub rejected the template download "
                f"({exc.code}) from {TEMPLATE_URL}. Set GITHUB_TOKEN to raise the rate limit.",
                file=sys.stderr,
            )
        else:
            print(
                f"Failed to download template from {TEMPLATE_URL} (HTTP {exc.code}).",
                file=sys.stderr,
            )
        raise
    except URLError as exc:
        print(f"Failed to download template from {TEMPLATE_URL}: {exc}", file=sys.stderr)
        raise

    with tarfile.open(archive_path) as archive:
        archive.extractall(extract_root)

    extracted_dirs = [path for path in extract_root.iterdir() if path.is_dir()]
    if len(extracted_dirs) != 1:
        raise RuntimeError(f"Expected one extracted template directory in {extract_root}.")
    return extracted_dirs[0]


def _should_include(rel: str, project_type: str) -> bool:
    if project_type not in TYPE_INCLUDES:
        raise ValueError(f"Unsupported project type: {project_type}")

    parts = Path(rel).parts
    if any(part in SKIP_NAMES for part in parts):
        return False

    if _matches_prefix(rel, ALWAYS_INCLUDE):
        return True

    if rel.startswith("app/adapters/input/"):
        return _matches_prefix(rel, TYPE_INCLUDES[project_type][1:])

    if rel.startswith("app/"):
        top_level_entry = next(
            (
                prefix
                for prefix in TYPE_INCLUDES
                if rel == f"app/{prefix}" or rel.startswith(f"app/{prefix}/")
            ),
            None,
        )
        if top_level_entry is not None:
            return top_level_entry == project_type

    return False


def _destination_relpath(rel: str, project_name: str) -> Path:
    if _matches_prefix(rel, ROOT_PACKAGE_PATHS):
        return Path(project_name) / rel
    return Path(rel)


def _copy_template(
    src_root: Path, dst_root: Path, project_name: str, project_type: str
) -> None:
    for src_path in src_root.rglob("*"):
        if not src_path.is_file():
            continue

        rel = src_path.relative_to(src_root).as_posix()
        if not _should_include(rel, project_type):
            continue

        dst_path = dst_root / _destination_relpath(rel, project_name)
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        if src_path.suffix in NON_TEXT_EXTENSIONS:
            shutil.copy2(src_path, dst_path)
            continue

        try:
            content = src_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src_path, dst_path)
            continue

        content = content.replace("pytsune", project_name)
        content = content.replace("template", project_name)
        content = content.replace("TEMPLATE", project_name.upper())
        dst_path.write_text(content, encoding="utf-8")

    launcher = textwrap.dedent(
        f"""
        from __future__ import annotations

        from {project_name}.{ENTRY_MODULES[project_type]} import run


        if __name__ == "__main__":
            raise SystemExit(run())
        """
    ).lstrip()
    (dst_root / "main.py").write_text(launcher, encoding="utf-8")


def _write_pyproject(
    dst_root: Path, project_name: str, project_type: str, db: str, extra_libs: list[str]
) -> list[str]:
    dependencies = build_dependencies(project_type, db, extra_libs)
    dependency_block = "".join(f'    "{dependency}",\n' for dependency in dependencies)
    scripts_block = ""
    if project_type == "cli":
        scripts_block = textwrap.dedent(
            f"""

            [project.scripts]
            {project_name} = "{project_name}.app.adapters.input.cli:app"
            """
        ).rstrip()
    content = textwrap.dedent(
        f"""
        [project]
        name = "{project_name}"
        version = "0.1.0"
        requires-python = ">=3.11"
        dependencies = [
        {dependency_block}]
        {scripts_block}

        [tool.uv]
        managed = true

        [dependency-groups]
        dev = [
            "pytest",
        ]
        """
    ).lstrip()
    (dst_root / "pyproject.toml").write_text(content, encoding="utf-8")
    return dependencies


def _run_optional_command(command: list[str], cwd: Path) -> None:
    try:
        subprocess.run(command, cwd=cwd, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(
            f"Warning: {' '.join(command)} failed in {cwd}: {exc}",
            file=sys.stderr,
        )


def main() -> int:
    if shutil.which("uv") is None:
        print("uv is required. Run ./install.sh or install uv first.", file=sys.stderr)
        return 1

    try:
        print(
            textwrap.dedent(
                """
                Project scaffold
                - project name: lowercase letters and underscores only
                - project types: cli, web, telegram, airflow, lib
                - databases: none, sqlite, postgresql, mongodb
                """
            ).strip()
        )

        while True:
            name = _tty_input("Project name: ").strip()
            if validate_project_name(name):
                break
            print("Invalid project name. Use only lowercase letters and underscores.")

        project_type = ask("Project type", PROJECT_TYPES)
        db = ask("Database", DATABASE_CHOICES)
        extra_libs_input = _tty_input("Extra libraries (comma-separated, optional): ").strip()
        extra_libs = [item.strip() for item in extra_libs_input.split(",") if item.strip()]

        target_dir = Path.cwd() / name
        if target_dir.exists():
            raise FileExistsError(f"Target directory already exists: {target_dir}")

        temp_dir = Path(tempfile.mkdtemp(prefix="pytsune-template-"))
        try:
            src_root = _download_template(temp_dir)
            target_dir.mkdir(parents=False)
            _copy_template(src_root, target_dir, name, project_type)
            deps = _write_pyproject(target_dir, name, project_type, db, extra_libs)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        _run_optional_command(["git", "init"], target_dir)
        _run_optional_command(["git", "add", "-A"], target_dir)
        _run_optional_command(["uv", "sync"], target_dir)
    except EOFError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (FileExistsError, HTTPError, URLError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Created {project_type} project in {target_dir}")
    print(f"Dependencies: {', '.join(deps) if deps else 'none'}")
    print(f"cd {name} && uv run main.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
