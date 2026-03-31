from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from template.core.application.dtos.dto import ApplicationDTO, ItemResponseDTO
from template.app.telegram.handlers.main_handler import message_handler, start_handler


@pytest.mark.asyncio
async def test_start_handler_calls_facade_with_dto() -> None:
    message = Mock()
    message.text = "/start"
    message.answer = AsyncMock()
    facade = Mock(return_value=ItemResponseDTO(id="item-1", name="telegram-start", value=0.0))

    await start_handler(message, facade)

    facade.assert_called_once_with(ApplicationDTO(name="telegram-start", value=0.0))
    message.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_message_handler_calls_facade_with_dto() -> None:
    message = Mock()
    message.text = "demo 7.5"
    message.answer = AsyncMock()
    facade = Mock(return_value=ItemResponseDTO(id="item-1", name="demo", value=7.5))

    await message_handler(message, facade)

    facade.assert_called_once_with(ApplicationDTO(name="demo", value=7.5))
    message.answer.assert_awaited_once()
