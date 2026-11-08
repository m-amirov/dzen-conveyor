"""Sixth DZEN pilot keeps package integrity and remains unpublished."""

import json
import unittest
from pathlib import Path

from scripts.validate_package import validate_package


ARTICLE = Path(__file__).resolve().parents[1] / "editorial" / "articles" / "nostalgia-social-bonds"


class SocialBondsPilotTests(unittest.TestCase):
    def test_article_passes_structural_validation(self):
        self.assertEqual([], validate_package(ARTICLE))

    def test_no_external_publication_is_claimed(self):
        manifest = json.loads((ARTICLE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("NOT_PUBLISHED", manifest["publication_status"])
        self.assertEqual("NOT_CHECKED", manifest["moderation_status"])
        self.assertEqual("NOT_VERIFIED", manifest["monetization_status"])


if __name__ == "__main__":
    unittest.main()
