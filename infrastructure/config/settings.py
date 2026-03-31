from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # pragma: no cover - optional dependency
    BaseSettings = None
    SettingsConfigDict = dict


if BaseSettings is not None:
    class Settings(BaseSettings):
        environment: str = "development"
        repository_type: str = "memory"
        items_file_path: str = "template/items.json"
        web_host: str = "127.0.0.1"
        web_port: int = 8000
        log_level: str = "INFO"
        telegram_bot_token: Optional[str] = None

        model_config = SettingsConfigDict(env_prefix="TEMPLATE_")

        def validate_telegram(self) -> "Settings":
            if self.telegram_bot_token is None:
                raise ValueError(
                    "Telegram mode requires TEMPLATE_TELEGRAM_BOT_TOKEN to be set."
                )
            return self
else:
    @dataclass(slots=True)
    class Settings:
        environment: str = field(default_factory=lambda: os.getenv("TEMPLATE_ENVIRONMENT", "development"))
        repository_type: str = field(default_factory=lambda: os.getenv("TEMPLATE_REPOSITORY_TYPE", "memory"))
        items_file_path: str = field(default_factory=lambda: os.getenv("TEMPLATE_ITEMS_FILE_PATH", "template/items.json"))
        web_host: str = field(default_factory=lambda: os.getenv("TEMPLATE_WEB_HOST", "127.0.0.1"))
        web_port: int = field(default_factory=lambda: int(os.getenv("TEMPLATE_WEB_PORT", "8000")))
        log_level: str = field(default_factory=lambda: os.getenv("TEMPLATE_LOG_LEVEL", "INFO"))
        telegram_bot_token: Optional[str] = field(
            default_factory=lambda: os.getenv("TEMPLATE_TELEGRAM_BOT_TOKEN")
        )

        def validate_telegram(self) -> "Settings":
            if self.telegram_bot_token is None:
                raise ValueError(
                    "Telegram mode requires TEMPLATE_TELEGRAM_BOT_TOKEN to be set."
                )
            return self
