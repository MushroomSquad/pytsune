## Summary

- replace `scaffold.py`'s `uv init` stub flow with a filtered template-copy flow backed by a GitHub tarball download or local `PYTSUNE_TEMPLATE_DIR` override
- add include/filter logic for all supported scaffold types, text substitution for copied template files, generated `main.py`, generated `pyproject.toml`, and non-fatal `git init` / `git add -A` / `uv sync` setup steps
- expand scaffold coverage with unit tests for include rules, copy/substitution behavior, tarball extraction, and `pyproject.toml` generation plus an integration test that exercises `scaffold.main()` against the local repository template for all 5 supported types

## Verification

- `bash -n install.sh`
- `python -m compileall scaffold.py tests/unit/test_scaffold.py tests/integration/test_scaffold.py`
- manual local-template smoke via a Python harness:
  - `lib` scaffold created `core/domain/`, `app/lib/`, and excluded `app/cli/`
  - `web` scaffold created `app/web/` and `app/adapters/input/rest/`
  - generated `main.py` executed cleanly for a fresh `lib` scaffold with `python main.py`

## Environment Limits

- `install.sh` already used `main` and already ran `uv run --python 3.11`, so no installer change was needed
- `tests/unit/test_scaffold.py` and `tests/integration/test_scaffold.py` could not be run in this sandbox because `pytest` is not installed and `uv run pytest ...` cannot resolve packages without network access
- `scripts/ai-check.sh` could not be run because `scripts/ai-check.sh` does not exist in this repository
- tracked `__pycache__` bytecode files were touched by `compileall`; sandbox restrictions prevented restoring them through `git`
