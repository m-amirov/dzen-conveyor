"""Regression checks for the fully packaged, unpublished editorial pilot."""

import json
import unittest
from pathlib import Path

from scripts.validate_package import validate_package


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "pilot-portrait"
SOVIET_SERVICE = Path(__file__).resolve().parents[1] / "editorial" / "articles" / "soviet-tea-service"
OFFLINE_DATE = Path(__file__).resolve().parents[1] / "editorial" / "articles" / "offline-date"
VIDEO_HOME = Path(__file__).resolve().parents[1] / "editorial" / "articles" / "video-home"


class PilotExampleTests(unittest.TestCase):
    def test_actual_pilot_passes_structural_validator(self):
        self.assertEqual([], validate_package(EXAMPLE))

    def test_existing_editorial_article_passes_structural_validator(self):
        self.assertEqual([], validate_package(SOVIET_SERVICE))

    def test_offline_date_article_passes_structural_validator(self):
        self.assertEqual([], validate_package(OFFLINE_DATE))

    def test_video_home_article_passes_structural_validator(self):
        self.assertEqual([], validate_package(VIDEO_HOME))

    def test_video_home_does_not_claim_external_publication(self):
        data = json.loads((VIDEO_HOME / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("NOT_PUBLISHED", data["publication_status"])
        self.assertEqual("NOT_CHECKED", data["moderation_status"])
        self.assertEqual("NOT_VERIFIED", data["monetization_status"])

    def test_offline_date_does_not_claim_external_publication(self):
        data = json.loads((OFFLINE_DATE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("NOT_PUBLISHED", data["publication_status"])
        self.assertEqual("NOT_CHECKED", data["moderation_status"])
        self.assertEqual("NOT_VERIFIED", data["monetization_status"])

    def test_pilot_has_no_claim_of_external_publication(self):
        data = json.loads((EXAMPLE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("NOT_PUBLISHED", data["publication_status"])
        self.assertEqual("NOT_CHECKED", data["moderation_status"])
        self.assertEqual("NOT_VERIFIED", data["monetization_status"])
        self.assertTrue(data["example_only"])


if __name__ == "__main__":
    unittest.main()
