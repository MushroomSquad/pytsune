from __future__ import annotations

from template.app.adapters.input.rest.robyn_controller import RobynController
from template.app.facade import AppFacade
from template.app.robyn.dependencies import get_facade


def create_router(facade: AppFacade | None = None) -> object:
    return RobynController(facade or get_facade()).router
