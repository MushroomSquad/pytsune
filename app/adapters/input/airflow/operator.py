from __future__ import annotations

try:
    from airflow.models import BaseOperator
except ImportError:
    class BaseOperator:  # type: ignore[override]
        def __init__(self, **_: object) -> None:
            pass

        def execute(self, context: dict[str, object] | None = None) -> object:
            raise NotImplementedError


from template.infrastructure.startup import bootstrap


class ItemProcessingOperator(BaseOperator):
    def __init__(self, item_name: str = "scheduled-item", item_value: float = 1.0, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.item_name = item_name
        self.item_value = item_value

    def execute(self, context: dict[str, object] | None = None) -> dict[str, object]:
        facade = bootstrap()
        item = facade.create_item(self.item_name, self.item_value)
        return {
            "item_id": item.id,
            "name": item.name,
            "value": item.value,
            "context": context or {},
        }
