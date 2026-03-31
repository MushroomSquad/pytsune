from __future__ import annotations


class ItemNotFoundError(Exception):
    def __init__(self, item_id: str) -> None:
        super().__init__(f"Item '{item_id}' was not found.")


class ItemValidationError(Exception):
    pass
