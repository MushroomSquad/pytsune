from __future__ import annotations

import unittest
from unittest.mock import Mock

from template.app.facade import AppFacade
from template.core.application.dtos.dto import CreateItemDTO, ItemResponseDTO


class FacadeTestCase(unittest.TestCase):
    def test_facade_delegates_to_service(self) -> None:
        service = Mock()
        service.create_item.return_value = ItemResponseDTO(id="item-1", name="demo", value=10.0)
        service.get_item.return_value = ItemResponseDTO(id="item-1", name="demo", value=10.0)
        service.list_items.return_value = [ItemResponseDTO(id="item-1", name="demo", value=10.0)]
        facade = AppFacade(service)

        created = facade.create_item("demo", 10.0)
        fetched = facade.get_item("item-1")
        listed = facade.list_items()

        self.assertEqual(created.id, "item-1")
        self.assertEqual(fetched.name, "demo")
        self.assertEqual(len(listed), 1)
        service.create_item.assert_called_once_with(CreateItemDTO(name="demo", value=10.0))
        service.get_item.assert_called_once_with("item-1")
        service.list_items.assert_called_once_with()
