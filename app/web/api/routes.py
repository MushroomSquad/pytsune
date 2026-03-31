from __future__ import annotations

from template.app.adapters.input.rest.controller import RestController
from template.app.facade import AppFacade
from template.app.web.dependencies import get_facade


def create_router(facade: AppFacade | None = None) -> object:
    return RestController(facade or get_facade()).router
