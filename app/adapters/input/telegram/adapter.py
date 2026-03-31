from __future__ import annotations

from typing import TYPE_CHECKING

from template.core.application.dtos.dto import ApplicationDTO

if TYPE_CHECKING:  # pragma: no cover - typing only
    from aiogram.types import Message


class TelegramInputAdapter:
    def to_dto(self, message: "Message") -> ApplicationDTO:
        text = (getattr(message, "text", "") or "").strip()
        if not text or text == "/start":
            return ApplicationDTO(name="telegram-start", value=0.0)

        name, separator, value = text.rpartition(" ")
        if separator:
            return ApplicationDTO(name=name or text, value=float(value))
        return ApplicationDTO(name=text, value=0.0)
