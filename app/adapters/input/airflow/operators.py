from __future__ import annotations

from collections.abc import Sequence

try:
    from airflow.models import BaseOperator
    AIRFLOW_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    AIRFLOW_AVAILABLE = False

    class BaseOperator:  # type: ignore[override]
        def __init__(self, task_id: str | None = None, **_: object) -> None:
            self.task_id = task_id
            self.output: list[dict[str, object]] = []

        def execute(self, context: dict[str, object] | None = None) -> object:
            raise NotImplementedError

        def __rshift__(self, other: object) -> object:
            return other


class _PartialConsumerOperator:
    def __init__(self, kwargs: dict[str, object]) -> None:
        self._kwargs = kwargs

    def expand(self, *, item: Sequence[dict[str, object]] | object) -> "ConsumerOperator":
        return ConsumerOperator(item=item, **self._kwargs)


class ProducerOperator(BaseOperator):
    def __init__(self, source_id: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.source_id = source_id

    def execute(self, context: dict[str, object] | None = None) -> list[dict[str, object]]:
        _ = context
        from template.infrastructure.startup import bootstrap

        facade = bootstrap()
        return facade.produce(source_id=self.source_id)


class ConsumerOperator(BaseOperator):
    def __init__(self, item: object | None = None, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.item = item

    def execute(self, context: dict[str, object] | None = None) -> dict[str, object]:
        _ = context
        from template.infrastructure.startup import bootstrap

        facade = bootstrap()
        if not isinstance(self.item, dict):
            raise TypeError("ConsumerOperator expects 'item' to be a dict.")
        return facade.consume(item=self.item)


if not AIRFLOW_AVAILABLE:
    ConsumerOperator.partial = classmethod(  # type: ignore[attr-defined]
        lambda cls, **kwargs: _PartialConsumerOperator(kwargs)
    )
