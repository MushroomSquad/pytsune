from __future__ import annotations


class HttpApiAdapter:
    def fetch_item(self, item_id: str) -> dict[str, object]:
        return {
            "status": "stub",
            "item_id": item_id,
        }
