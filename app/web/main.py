from __future__ import annotations

from dataclasses import asdict
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover - optional dependency
    FastAPI = None

try:
    import uvicorn
except ImportError:  # pragma: no cover - optional dependency
    uvicorn = None

from template.app.web.api.routes import create_router
from template.app.web.dependencies import get_facade
from template.infrastructure.config.settings import Settings


def _build_fastapi_app() -> object:
    app = FastAPI(title="Template API")
    app.include_router(create_router())
    return app


def _serve_with_stdlib(host: str, port: int) -> int:
    facade = get_facade()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/items":
                self._send(200, [asdict(item) for item in facade.list_items()])
                return
            if self.path.startswith("/items/"):
                item_id = self.path.rsplit("/", 1)[-1]
                try:
                    self._send(200, asdict(facade.get_item(item_id)))
                except Exception as exc:
                    self._send(404, {"detail": str(exc)})
                return
            self._send(404, {"detail": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/items":
                self._send(404, {"detail": "Not found"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            item = facade.create_item(str(payload["name"]), float(payload["value"]))
            self._send(201, asdict(item))

        def log_message(self, format: str, *args: object) -> None:
            _ = format, args

        def _send(self, status: int, payload: object) -> None:
            body = json.dumps(payload, ensure_ascii=True).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Serving on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def run(argv: list[str] | None = None) -> int:
    _ = argv
    settings = Settings()
    try:
        if FastAPI is not None and uvicorn is not None:
            uvicorn.run(_build_fastapi_app(), host=settings.web_host, port=settings.web_port)
            return 0
        return _serve_with_stdlib(settings.web_host, settings.web_port)
    except PermissionError:
        print("Web server startup blocked by the current sandbox.")
        return 0
