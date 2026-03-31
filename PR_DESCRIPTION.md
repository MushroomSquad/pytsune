## Summary

- replace the monolithic CLI adapter with a Typer package under `app/adapters/input/cli/` that exposes shared option aliases, auto-discovers command groups, and injects `AppFacade` through `ctx.obj`
- add autodiscovered `items` and `smoke` command groups, keep `app/cli/*` as compatibility redirects, and route `__main__.py` plus the console script entry point to the new CLI app
- update `scaffold.py`, docs, and tests so generated CLI projects emit `args.py`, `commands/`, and a console script targeting `app.adapters.input.cli:app`

## Verification

- `python - <<'PY' ... _write_pyproject(..., 'cli', ...) ... PY`
  - confirmed generated CLI `pyproject.toml` contains `demo_project.app.adapters.input.cli:app`
- `python -m py_compile scaffold.py __main__.py app/adapters/input/cli/args.py app/adapters/input/cli/cli.py app/adapters/input/cli/commands/items.py app/adapters/input/cli/commands/smoke.py tests/unit/test_cli_args.py tests/unit/test_cli_autodiscover.py tests/integration/test_cli.py tests/unit/test_scaffold.py tests/integration/test_scaffold.py`

## Environment Limits

- `pytest` is not installed in this sandbox, so the new CLI tests and the existing suite could not be executed
- `typer` is not installed in this sandbox, so `python -m pytsune --help` and `CliRunner`-based runtime checks could not be executed here
- `scripts/ai-check.sh` could not be run because `scripts/ai-check.sh` does not exist in this repository
