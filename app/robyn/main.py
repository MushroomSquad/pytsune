from __future__ import annotations

try:
    from robyn import Robyn
except ImportError:  # pragma: no cover - optional dependency
    Robyn = None  # type: ignore[assignment,misc]

from template.app.robyn.api.routes import create_router
from template.app.robyn.dependencies import get_facade
from template.infrastructure.config.settings import Settings


def create_app() -> object:
    if Robyn is None:
        raise RuntimeError("robyn is not installed. Run: uv add robyn")
    app = Robyn(__file__)
    facade = get_facade()
    app.include_router(create_router(facade))
    return app


def run(argv: list[str] | None = None) -> int:
    _ = argv
    settings = Settings()
    try:
        app = create_app()
        app.start(host=settings.web_host, port=settings.web_port)
    except PermissionError:
        print("Web server startup blocked by the current sandbox.")
    return 0
