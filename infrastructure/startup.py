from __future__ import annotations

from template.app.facade import AppFacade
from template.infrastructure.config.settings import Settings
from template.infrastructure.container import ContainerFactory


def bootstrap(settings: Settings | None = None) -> AppFacade:
    return ContainerFactory(settings=settings).create_facade()
