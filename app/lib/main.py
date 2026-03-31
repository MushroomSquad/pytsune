from __future__ import annotations

from dataclasses import asdict

from template.app.adapters.input.lib.client import LibraryAdapter


def run(argv: list[str] | None = None) -> int:
    _ = argv
    with LibraryAdapter() as client:
        created = client.create_item("demo", 1.0)
        listed = client.list_items()

    print(f"created={asdict(created)}")
    print(f"items={[asdict(item) for item in listed]}")
    return 0
