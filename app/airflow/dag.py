from __future__ import annotations

from template.app.airflow.etl.dag_etl import dag, run

# Original example DAG kept as a reference:
# from datetime import datetime
# from template.app.adapters.input.airflow import ConsumerOperator, ProducerOperator
#
# with DAG(
#     dag_id="producer_consumer_skeleton",
#     schedule="@daily",
#     start_date=datetime(2024, 1, 1),
#     catchup=False,
# ) as dag:
#     producer = ProducerOperator(task_id="produce_items", source_id="template.app.airflow.dag")
#     consumers = ConsumerOperator.partial(task_id="consume_item").expand(item=producer.output)
#     producer >> consumers

__all__ = ["dag", "run"]
