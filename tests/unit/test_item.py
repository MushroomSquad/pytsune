from __future__ import annotations

import math
import unittest

from template.core.domain.entities.model import Item
from template.core.domain.exceptions.exception import ItemValidationError


class ItemTestCase(unittest.TestCase):
    def test_validate_happy_path(self) -> None:
        item = Item(name="example", value=42.0)

        result = item.validate()

        self.assertIs(result, item)
        self.assertEqual(item.to_event().name, "example")

    def test_validate_rejects_empty_name(self) -> None:
        with self.assertRaises(ItemValidationError):
            Item(name="   ", value=1.0).validate()

    def test_validate_rejects_non_numeric_value(self) -> None:
        with self.assertRaises(ItemValidationError):
            Item(name="example", value="bad").validate()  # type: ignore[arg-type]

    def test_validate_rejects_non_finite_value(self) -> None:
        with self.assertRaises(ItemValidationError):
            Item(name="example", value=math.inf).validate()
