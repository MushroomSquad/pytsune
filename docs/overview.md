---
project: template
extracted: 2026-03-29 19:42
---

# Docs: template

## README

# Universal DDD + Hexagonal Architecture Project Template

## Quick Start

Run through the installer:

```bash
curl -fsSL https://raw.githubusercontent.com/MushroomSquad/pytsune/main/install.sh | bash
```

The `install.sh` script:

- checks whether `uv` is available and installs version `0.4.0` or newer when needed;
- downloads `scaffold.py` into a temporary file;
- runs `uv run --python 3.11 /tmp/scaffold.py` without piping the Python script through stdin.

Run locally from the repository:

```bash
./install.sh
```

If you copied the file from another source, make sure it is executable:

```bash
chmod +x install.sh
```

### Questionnaire

`scaffold.py` asks:

1. Project name: lowercase Latin letters and `_` only.
2. Project type: `cli`, `web`, `telegram`, `airflow`, `lib`.
3. Database: `none`, `sqlite`, `postgresql`, `mongodb`.
4. Extra libraries: any comma-separated list.

### Output By Type

- `cli`: `typer`, `pydantic-settings`
- `web`: `fastapi`, `uvicorn`, `pydantic-settings`
- `telegram`: `aiogram`, `pydantic-settings`
- `airflow`: `apache-airflow`, `pydantic-settings`
- `lib`: `pydantic-settings`

The database choice adds:

- `none`: no extra packages
- `sqlite`: `aiosqlite`, `sqlalchemy[asyncio]`
- `postgresql`: `asyncpg`, `sqlalchemy[asyncio]`
- `mongodb`: `motor`, `beanie`

At the end, the script prints the following command:

```bash
cd <name> && uv run main.py
```

## Architecture

### Module Map

```text
.
├── __init__.py
├── __main__.py
├── app
│   ├── adapters
│   │   ├── input
│   │   │   ├── airflow/operator.py
│   │   │   ├── cli/args.py
│   │   │   ├── cli/cli.py
│   │   │   ├── cli/commands/items.py
│   │   │   ├── cli/commands/smoke.py
│   │   │   ├── lib/client.py
│   │   │   ├── rest/controller.py
│   │   │   └── telegram/adapter.py
│   │   └── output
│   │       ├── api_clients/client.py
│   │       ├── db/repository.py
│   │       └── files/file.py
│   ├── airflow/dag.py
│   ├── cli/main.py
│   ├── facade.py
│   ├── gui
│   │   ├── main.py
│   │   ├── presenters/main_presenter.py
│   │   └── views/main_view.py
│   ├── lib/main.py
│   ├── telegram
│   │   ├── handlers/main_handler.py
│   │   ├── main.py
│   │   └── middlewares.py
│   └── web
│       ├── api/routes.py
│       ├── dependencies.py
│       └── main.py
├── core
│   ├── application
│   │   ├── dtos/dto.py
│   │   ├── ports
│   │   │   ├── input/input_port.py
│   │   │   └── output/repository_port.py
│   │   ├── services/service.py
│   │   └── use_cases/use_case.py
│   └── domain
│       ├── entities/model.py
│       ├── events/event.py
│       ├── exceptions/exception.py
│       └── services/service.py
├── infrastructure
│   ├── config/settings.py
│   ├── container.py
│   ├── db/db.py
│   ├── logging/logger.py
│   └── startup.py
└── tests
    ├── gui/test_presenter.py
    ├── integration/test_container.py
    ├── integration/test_lib.py
    ├── telegram/test_adapter.py
    ├── telegram/test_handlers.py
    ├── unit/test_facade.py
    ├── unit/test_item.py
    ├── unit/test_lib.py
    ├── unit/test_scaffold.py
    └── unit/test_use_cases.py
```

### Layers

- `core/domain`: entities, events, business validation, and domain-level exceptions.
- `core/application`: DTOs, use cases, and the input/output port contracts that isolate business logic from adapters.
- `app`: user-facing entry points plus adapter implementations for CLI, REST, Telegram, Airflow, GUI, and library use.
- `infrastructure`: environment-backed settings, dependency injection, startup bootstrapping, logging, and placeholder DB initialization.
- `tests`: focused coverage of the facade, use cases, scaffold flow, integration wiring, GUI presenter flow, and Telegram handlers.

### Port And Adapter Contracts

- Input ports live under `core/application/ports/input/` and are implemented by `core/application/services/service.py`.
- Output ports live under `core/application/ports/output/` and are implemented by adapters in `app/adapters/output/`.
- Input adapters live in `app/adapters/input/` and translate CLI arguments, REST payloads, Telegram messages, Airflow task context, and library calls into application-layer requests.
- `app/facade.py` is the thin boundary object consumed by runners in `app/<type>/main.py`.

### CLI Audit And Autodiscovery

- Legacy `app/cli/main.py` only routed three item operations: `create`, `get`, and `list`.
- The old CLI surface had no reusable shared options.
- `app/cli/main.py` imported `template.infrastructure.startup.bootstrap` directly, so the entry point bypassed the adapter boundary for composition, but it did not import any DB module directly.
- The new root CLI lives in `app/adapters/input/cli/cli.py` and wires `Settings -> ContainerFactory -> AppFacade` inside `@app.callback()`, storing the facade in `ctx.obj`.
- Command groups live in `app/adapters/input/cli/commands/`. Any module in that package that exposes `app = typer.Typer(...)` is auto-registered.
- To add a new group, create a new file under `commands/`, expose a Typer app, and keep commands thin by delegating through the injected `AppFacade`.

### Infrastructure Responsibilities

- `infrastructure/config/settings.py` provides environment-driven configuration with a `pydantic-settings` fallback path.
- `infrastructure/container.py` acts as the DI composition root that selects a repository implementation and assembles use cases, the application service, and the facade.
- `infrastructure/startup.py` exposes the bootstrap helper used by every runtime entry point.
- `infrastructure/logging/logger.py` centralizes logger creation.
- `infrastructure/db/db.py` is the placeholder DB initialization hook for generated projects.

## Testing

Main bootstrap validation:

```bash
uv run pytest tests/unit/test_scaffold.py
```

## pyproject.toml

```
[project]
name = "pytsune"
version = "0.1.0"
description = "Hexagonal architecture template with CLI, web, GUI, and Airflow entry points."
requires-python = ">=3.11"
dependencies = [
    "pydantic-settings",
    "typer",
]

[tool.uv]
managed = true

[project.scripts]
pytsune = "app.adapters.input.cli:app"

[dependency-groups]
dev = [
    "pytest",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

```
