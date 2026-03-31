from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

try:
    from aiogram import Router
    from aiogram.filters import CommandStart
except ImportError:  # pragma: no cover - optional dependency
    class Router:
        def message(self, *args: object, **kwargs: object) -> Any:
            def decorator(handler: Any) -> Any:
                return handler

            return decorator

    class CommandStart:
        pass

from template.app.adapters.input.telegram.adapter import TelegramInputAdapter

if TYPE_CHECKING:  # pragma: no cover - typing only
    from aiogram.types import Message

    from template.app.facade import AppFacade


router = Router()
adapter = TelegramInputAdapter()


@router.message(CommandStart())
async def start_handler(message: "Message", facade: "AppFacade") -> None:
    item = facade(adapter.to_dto(message))
    await message.answer(_format_response(item))


@router.message()
async def message_handler(message: "Message", facade: "AppFacade") -> None:
    item = facade(adapter.to_dto(message))
    await message.answer(_format_response(item))


def _format_response(item: object) -> str:
    payload = asdict(item) if hasattr(item, "__dataclass_fields__") else item
    return f"Created item: {payload}"
