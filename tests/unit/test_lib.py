from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from template.app.adapters.input.lib.client import LibraryAdapter
from template.core.application.dtos.dto import ItemResponseDTO


class LibraryAdapterTestCase(unittest.TestCase):
    @patch("template.app.adapters.input.lib.client.bootstrap")
    def test_library_adapter_delegates_to_facade(self, bootstrap_mock: Mock) -> None:
        facade = Mock()
        facade.create_item.return_value = ItemResponseDTO(id="item-1", name="demo", value=1.0)
        facade.get_item.return_value = ItemResponseDTO(id="item-1", name="demo", value=1.0)
        facade.list_items.return_value = [ItemResponseDTO(id="item-1", name="demo", value=1.0)]
        bootstrap_mock.return_value = facade

        adapter = LibraryAdapter()

        created = adapter.create_item("demo", 1.0)
        fetched = adapter.get_item("item-1")
        listed = adapter.list_items()

        self.assertEqual(created.id, "item-1")
        self.assertEqual(fetched.name, "demo")
        self.assertEqual(len(listed), 1)
        facade.create_item.assert_called_once_with("demo", 1.0)
        facade.get_item.assert_called_once_with("item-1")
        facade.list_items.assert_called_once_with()

    @patch("template.app.adapters.input.lib.client.bootstrap")
    def test_library_adapter_context_manager_returns_self(self, bootstrap_mock: Mock) -> None:
        bootstrap_mock.return_value = Mock()
        adapter = LibraryAdapter()

        with adapter as client:
            self.assertIs(client, adapter)

        self.assertFalse(adapter.__exit__(None, None, None))
