## Summary

- add a producer-consumer Airflow adapter skeleton with `ProducerOperator` and `ConsumerOperator`, plus facade/use-case stubs for `produce()` and `consume()`
- rewrite the Airflow DAG entry point to a two-group topology using `ProducerOperator`, `ConsumerOperator.partial(...).expand(...)`, and optional import fallbacks so the module still parses without Airflow installed
- update scaffold generation and scaffold tests so `airflow` projects emit `app/adapters/input/airflow/__init__.py`, `operators.py`, the rewritten `app/airflow/dag.py`, and the Airflow test package

## Verification

- `python -m py_compile app/facade.py core/application/use_cases/use_case.py app/adapters/input/airflow/__init__.py app/adapters/input/airflow/operators.py app/airflow/dag.py scaffold.py tests/airflow/test_operators.py tests/integration/test_container.py tests/unit/test_scaffold.py tests/integration/test_scaffold.py`

## Environment Limits

- `uv run pytest tests/airflow/ tests/integration/test_container.py tests/unit/test_scaffold.py tests/integration/test_scaffold.py` could not complete because this sandbox has no network access and no preinstalled `pytest`
- `uv run ruff check` and `uv run mypy` could not complete for the same reason; the sandbox also lacks `ruff`, `mypy`, and `pydantic-settings`
- `airflow dags test producer_consumer_skeleton <date>` could not be executed because Airflow is not installed in this sandbox
