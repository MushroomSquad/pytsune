#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

from pathlib import Path
from typing import TextIO
import re
import shutil
import subprocess
import sys
import textwrap


PROJECT_TYPES = ("cli", "web", "telegram", "airflow", "lib")
DATABASE_CHOICES = ("none", "sqlite", "postgresql", "mongodb")


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
        "airflow": ["apache-airflow", "pydantic-settings"],
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


def scaffold_project(name: str, project_type: str, target_dir: Path) -> None:
    if project_type not in PROJECT_TYPES:
        raise ValueError(f"Unsupported project type: {project_type}")
    if target_dir.exists():
        raise FileExistsError(f"Target directory already exists: {target_dir}")
    subprocess.run(
        ["uv", "init", "--name", name, "--python", "3.11", str(target_dir)],
        check=True,
    )


def add_dependencies(target_dir: Path, deps: list[str]) -> None:
    if not deps:
        return
    subprocess.run(["uv", "add", *deps], cwd=target_dir, check=True)


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
        deps = build_dependencies(project_type, db, extra_libs)

        scaffold_project(name, project_type, target_dir)
        add_dependencies(target_dir, deps)
    except EOFError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Created {project_type} project in {target_dir}")
    print(f"Dependencies: {', '.join(deps) if deps else 'none'}")
    print(f"cd {name} && uv run main.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
