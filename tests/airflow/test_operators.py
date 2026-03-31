from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from template.app.adapters.input.airflow.operators import ConsumerOperator, ProducerOperator


class TestProducerOperator(unittest.TestCase):
    def test_execute_returns_serialisable_list(self) -> None:
        facade = Mock()
        facade.produce.return_value = [{"item_id": "demo-1", "source_id": "demo"}]

        with patch("template.app.adapters.input.airflow.operators.bootstrap", return_value=facade):
            result = ProducerOperator(task_id="produce_items", source_id="demo").execute()

        self.assertEqual(result, [{"item_id": "demo-1", "source_id": "demo"}])
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(item, dict) for item in result))
        facade.produce.assert_called_once_with(source_id="demo")


class TestConsumerOperator(unittest.TestCase):
    def test_execute_delegates_to_facade(self) -> None:
        facade = Mock()
        item = {"item_id": "demo-1", "source_id": "demo"}
        facade.consume.return_value = {"status": "processed", "item": item}

        with patch("template.app.adapters.input.airflow.operators.bootstrap", return_value=facade):
            result = ConsumerOperator(task_id="consume_item", item=item).execute()

        self.assertEqual(result, {"status": "processed", "item": item})
        self.assertIsInstance(result, dict)
        facade.consume.assert_called_once_with(item=item)
