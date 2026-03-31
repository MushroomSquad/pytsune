from __future__ import annotations

import os
import unittest

from template.infrastructure.startup import bootstrap


class ContainerIntegrationTestCase(unittest.TestCase):
    def test_bootstrap_memory_repository_end_to_end(self) -> None:
        previous = os.environ.get("TEMPLATE_REPOSITORY_TYPE")
        os.environ["TEMPLATE_REPOSITORY_TYPE"] = "memory"
        try:
            facade = bootstrap()
            created = facade.create_item("demo", 12.5)
            fetched = facade.get_item(created.id)
            listed = facade.list_items()
            produced = facade.produce(source_id="demo-source")
            consumed = facade.consume(item=produced[0])
        finally:
            if previous is None:
                os.environ.pop("TEMPLATE_REPOSITORY_TYPE", None)
            else:
                os.environ["TEMPLATE_REPOSITORY_TYPE"] = previous

        self.assertEqual(fetched.id, created.id)
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0].name, "demo")
        self.assertEqual(produced[0]["source_id"], "demo-source")
        self.assertEqual(consumed["status"], "processed")
