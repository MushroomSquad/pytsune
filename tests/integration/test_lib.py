from __future__ import annotations

import unittest

from template import TemplateClient, __version__
from template.infrastructure.config.settings import Settings


class TemplateClientIntegrationTestCase(unittest.TestCase):
    def test_template_exports_version_and_client(self) -> None:
        self.assertEqual(__version__, "0.1.0")
        self.assertEqual(TemplateClient.__name__, "LibraryAdapter")

    def test_template_client_round_trip(self) -> None:
        client = TemplateClient(Settings(repository_type="memory"))

        created = client.create_item("demo", 2.5)
        fetched = client.get_item(created.id)
        listed = client.list_items()

        self.assertEqual(fetched.id, created.id)
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0].name, "demo")

    def test_template_client_context_manager_round_trip(self) -> None:
        with TemplateClient(Settings(repository_type="memory")) as client:
            created = client.create_item("demo", 3.5)
            fetched = client.get_item(created.id)

        self.assertEqual(fetched.id, created.id)
