# Universal DDD + Hexagonal Architecture Project Template

## Quick Start

Run through the installer:

```bash
curl -fsSL https://raw.githubusercontent.com/OWNER/REPO/main/install.sh | bash
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

See [`docs/overview.md`](docs/overview.md) for the full architecture overview.

```text
                +----------------------+
                |   app/<entry>/main   |
                | CLI / Web / Telegram |
                | Airflow / GUI / Lib  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |  app/adapters/input  |
                | CLI / REST / Telegram|
                | Airflow / Library    |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |    app/facade.py     |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |  core/application    |
                | services / use cases |
                | DTOs / ports         |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |    core/domain       |
                | entities / events /  |
                | services / errors    |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | app/adapters/output  |
                | + infrastructure     |
                +----------------------+
```

### Layer Overview

- `core/domain`: entities, domain events, domain services, and domain exceptions.
- `core/application`: DTOs, input and output ports, use cases, and the application service.
- `app`: entry-point-specific runners plus input and output adapters.
- `infrastructure`: settings, dependency wiring, startup helpers, logging, and database hooks.
- `tests`: unit, integration, Telegram, and GUI checks.

### Entry Points

| Entry point | Runner | Main adapter path |
| --- | --- | --- |
| CLI | `app/cli/main.py` | `app/adapters/input/cli/cli.py` |
| Web | `app/web/main.py` | `app/adapters/input/rest/controller.py` |
| Telegram | `app/telegram/main.py` | `app/adapters/input/telegram/adapter.py` |
| Airflow | `app/airflow/dag.py` | `app/adapters/input/airflow/operator.py` |
| GUI | `app/gui/main.py` | `app/gui/presenters/main_presenter.py` |
| Library | `app/lib/main.py` | `app/adapters/input/lib/client.py` |

### Dependency Rules

- Dependencies point inward: entry points and infrastructure may depend on `app` and `core`, but `core` does not depend on `app` or `infrastructure`.
- `core/application/ports/` defines contracts; adapters implement those contracts at the edges.
- `infrastructure/container.py` wires concrete repositories into use cases and exposes an `AppFacade`.

### Template Intent

The package metadata still uses the name `template` in [`pyproject.toml`](pyproject.toml). That is intentional: this repository is a scaffold source, and `scaffold.py` generates a project subset from the template rather than shipping `pytsune` as a finalized application package.

### Scaffold Subsets

`scaffold.py` generates the target project with a selected entry-point profile and dependency set. The template keeps all adapters in this repository, while the questionnaire decides which runtime dependencies should be installed in the generated subset.

## Testing

Main bootstrap validation:

```bash
uv run pytest tests/unit/test_scaffold.py
```
