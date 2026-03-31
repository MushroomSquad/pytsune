from __future__ import annotations

import asyncio

try:
    from aiogram import Bot, Dispatcher
except ImportError:  # pragma: no cover - optional dependency
    Bot = None
    Dispatcher = None

from template.app.telegram.handlers.main_handler import router
from template.app.telegram.middlewares import InjectFacadeMiddleware
from template.infrastructure.config.settings import Settings
from template.infrastructure.startup import bootstrap


async def _run_polling() -> int:
    settings = Settings().validate_telegram()
    if Bot is None or Dispatcher is None:
        raise RuntimeError(
            "Telegram mode requires aiogram. Install it with `pip install .[telegram]`."
        )

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()

    async def on_startup() -> None:
        dispatcher.workflow_data["facade"] = bootstrap(settings)

    async def on_shutdown() -> None:
        await bot.session.close()

    dispatcher.include_router(router)
    dispatcher.message.middleware(InjectFacadeMiddleware())
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)

    await dispatcher.start_polling(bot)
    return 0


def run(argv: list[str] | None = None) -> int:
    _ = argv
    return asyncio.run(_run_polling())
