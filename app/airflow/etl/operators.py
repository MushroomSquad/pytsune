from __future__ import annotations

import asyncio

from template.infrastructure.container import ContainerFactory

try:
    from airflow.models import BaseOperator
except ImportError:  # pragma: no cover - optional dependency
    class BaseOperator:  # type: ignore[override]
        def __init__(self, task_id: str | None = None, **_: object) -> None:
            self.task_id = task_id

        def execute(self, context: dict[str, object] | None = None) -> object:
            raise NotImplementedError

        def __rshift__(self, other: object) -> object:
            return other


class ProducerOperator(BaseOperator):
    def execute(self, context: dict[str, object] | None = None) -> None:
        _ = context
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(ContainerFactory().create_etl_use_case()._run_producer())
        finally:
            asyncio.set_event_loop(None)
            loop.close()


class ConsumerOperator(BaseOperator):
    def execute(self, context: dict[str, object] | None = None) -> None:
        _ = context
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(ContainerFactory().create_etl_use_case()._run_consumer())
        finally:
            asyncio.set_event_loop(None)
            loop.close()
