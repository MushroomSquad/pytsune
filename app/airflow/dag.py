from __future__ import annotations

try:
    from airflow import DAG
except ImportError:  # pragma: no cover - optional dependency
    class DAG:  # type: ignore[override]
        def __init__(self, dag_id: str, schedule: str, start_date: object | None = None, catchup: bool = False) -> None:
            self.dag_id = dag_id
            self.schedule = schedule
            self.start_date = start_date
            self.catchup = catchup


from template.app.adapters.input.airflow.operator import ItemProcessingOperator

dag = DAG("item_processing_dag", schedule="@daily", catchup=False)
item_processing_task = ItemProcessingOperator(task_id="item_processing", dag=dag)  # type: ignore[arg-type]


def run(argv: list[str] | None = None) -> int:
    _ = argv
    result = item_processing_task.execute(context={"source": "template.app.airflow.dag"})
    print(result)
    return 0
