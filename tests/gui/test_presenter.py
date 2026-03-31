from __future__ import annotations

import os
import unittest

try:
    import pytest
except ImportError:  # pragma: no cover - local fallback
    class _Mark:
        @staticmethod
        def skipif(condition: bool, reason: str) -> object:
            return unittest.skipIf(condition, reason)

    class _Pytest:
        mark = _Mark()

    pytest = _Pytest()

from template.app.facade import AppFacade
from template.app.gui.presenters.main_presenter import MainPresenter
from template.core.application.dtos.dto import ItemResponseDTO


@pytest.mark.skipif(not os.environ.get("DISPLAY"), reason="DISPLAY is required for GUI smoke tests")
class PresenterGuiTestCase(unittest.TestCase):
    def test_presenter_smoke(self) -> None:
        class Service:
            def create_item(self, dto: object) -> ItemResponseDTO:
                return ItemResponseDTO(id="item-1", name="demo", value=1.0)

            def get_item(self, item_id: str) -> ItemResponseDTO:
                return ItemResponseDTO(id=item_id, name="demo", value=1.0)

            def list_items(self) -> list[ItemResponseDTO]:
                return [ItemResponseDTO(id="item-1", name="demo", value=1.0)]

        presenter = MainPresenter(AppFacade(Service()))

        items = presenter.load_items()
        created = presenter.create_item("demo", 1.0)

        self.assertEqual(items, ["demo: 1.0"])
        self.assertEqual(created, "demo: 1.0")
