from __future__ import annotations

from template.app.facade import AppFacade
from template.infrastructure.startup import bootstrap

_facade: AppFacade | None = None


def get_facade() -> AppFacade:
    global _facade
    if _facade is None:
        _facade = bootstrap()
    return _facade
