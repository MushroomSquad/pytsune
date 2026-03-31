from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from template.core.application.dtos.dto import CreateItemDTO
from template.core.application.ports.output.repository_port import ItemRepositoryPort
from template.core.application.use_cases.use_case import (
    CreateItemUseCase,
    GetItemUseCase,
    ListItemsUseCase,
)
from template.core.domain.entities.model import Item
from template.core.domain.exceptions.exception import ItemNotFoundError


class UseCaseTestCase(unittest.TestCase):
    def test_create_item_use_case(self) -> None:
        repository = MagicMock(spec=ItemRepositoryPort)
        repository.save.side_effect = lambda item: item
        use_case = CreateItemUseCase(repository)

        item = use_case.execute(CreateItemDTO(name="demo", value=5.5))

        self.assertEqual(item.name, "demo")
        repository.save.assert_called_once()

    def test_get_item_use_case(self) -> None:
        repository = MagicMock(spec=ItemRepositoryPort)
        repository.get.return_value = Item(name="demo", value=5.5, id="item-1")
        use_case = GetItemUseCase(repository)

        item = use_case.execute("item-1")

        self.assertEqual(item.id, "item-1")
        repository.get.assert_called_once_with("item-1")

    def test_get_item_use_case_raises_when_missing(self) -> None:
        repository = MagicMock(spec=ItemRepositoryPort)
        repository.get.return_value = None
        use_case = GetItemUseCase(repository)

        with self.assertRaises(ItemNotFoundError):
            use_case.execute("missing")

    def test_list_items_use_case(self) -> None:
        repository = MagicMock(spec=ItemRepositoryPort)
        repository.list.return_value = [Item(name="demo", value=5.5, id="item-1")]
        use_case = ListItemsUseCase(repository)

        items = use_case.execute()

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, "item-1")
        repository.list.assert_called_once_with()
