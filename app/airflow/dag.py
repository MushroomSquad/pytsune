from __future__ import annotations

from datetime import datetime
from template.app.adapters.input.airflow import ConsumerOperator, ProducerOperator

try:
    from airflow import DAG
    from airflow.utils.task_group import TaskGroup
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

    class TaskGroup:  # type: ignore[override]
        def __init__(self, group_id: str) -> None:
            self.group_id = group_id

        def __enter__(self) -> "TaskGroup":
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
            _ = (exc_type, exc, tb)
            return False

with DAG(
    dag_id="producer_consumer_skeleton",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    with TaskGroup(group_id="producers"):
        producer = ProducerOperator(
            task_id="produce_items",
            source_id="template.app.airflow.dag",
        )

    with TaskGroup(group_id="consumers"):
        consumers = ConsumerOperator.partial(task_id="consume_item").expand(item=producer.output)

    producer >> consumers


def run(argv: list[str] | None = None) -> int:
    _ = argv
    produced_items = ProducerOperator(
        task_id="produce_items",
        source_id="template.app.airflow.dag",
    ).execute(context={"source": "template.app.airflow.dag"})
    for item in produced_items:
        result = ConsumerOperator(task_id="consume_item", item=item).execute()
        print(result)
    return 0
