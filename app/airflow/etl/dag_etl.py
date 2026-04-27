from __future__ import annotations

from datetime import datetime

from template.app.airflow.etl.operators import ConsumerOperator, ProducerOperator

try:
    from airflow import DAG
except ImportError:  # pragma: no cover - optional dependency
    class DAG:  # type: ignore[override]
        def __init__(
            self,
            dag_id: str,
            schedule: str,
            start_date: object | None = None,
            catchup: bool = False,
        ) -> None:
            self.dag_id = dag_id
            self.schedule = schedule
            self.start_date = start_date
            self.catchup = catchup

        def __enter__(self) -> "DAG":
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
            _ = (exc_type, exc, tb)
            return False


with DAG(
    dag_id="etl_pipeline",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    # This template relies on a shared in-memory queue, so it only works with LocalExecutor.
    producer = ProducerOperator(task_id="produce_records", do_xcom_push=False)
    consumer = ConsumerOperator(task_id="consume_records", do_xcom_push=False)

    producer >> consumer


def run(argv: list[str] | None = None) -> int:
    _ = argv
    ProducerOperator(task_id="produce_records").execute()
    ConsumerOperator(task_id="consume_records").execute()
    return 0
