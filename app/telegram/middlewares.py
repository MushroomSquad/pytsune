from __future__ import annotations

from typing import Any, Awaitable, Callable

try:
    from aiogram import BaseMiddleware
except ImportError:  # pragma: no cover - optional dependency
    class BaseMiddleware:
        async def __call__(
            self,
            handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
            event: Any,
            data: dict[str, Any],
        ) -> Any:
            return await handler(event, data)


class InjectFacadeMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        dispatcher = data.get("dispatcher")
        workflow_data = getattr(dispatcher, "workflow_data", {}) if dispatcher is not None else {}
        data["facade"] = workflow_data["facade"]
        return await handler(event, data)
