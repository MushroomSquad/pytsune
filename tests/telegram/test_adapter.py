from __future__ import annotations

from types import SimpleNamespace

from template.app.adapters.input.telegram.adapter import TelegramInputAdapter


class TestTelegramInputAdapter:
    def test_to_dto_maps_start_command(self) -> None:
        adapter = TelegramInputAdapter()

        dto = adapter.to_dto(SimpleNamespace(text="/start"))

        assert dto.name == "telegram-start"
        assert dto.value == 0.0

    def test_to_dto_maps_message_name_and_value(self) -> None:
        adapter = TelegramInputAdapter()

        dto = adapter.to_dto(SimpleNamespace(text="demo 12.5"))

        assert dto.name == "demo"
        assert dto.value == 12.5
