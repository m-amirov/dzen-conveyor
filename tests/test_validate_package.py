"""Contract tests for a complete, locally packaged Dzen article."""

import json
import gc
import tempfile
import unittest
import warnings
from pathlib import Path
from PIL import Image

from scripts.validate_package import validate_package


class PackageContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.article = Path(self.tmp.name) / "example-article"
        images = self.article / "images"
        images.mkdir(parents=True)

        (self.article / "brief.md").write_text("# Сервиз\nИсследовательский вопрос", encoding="utf-8")
        (self.article / "sources.md").write_text(
            "- [S1] https://museum.example/collection — Музей; accessed: 2026-11-07; evidence: описание сервизов; scope: частная коллекция\n"
            "- [S2] https://archive.example/paper — Архив; accessed: 2026-11-07; evidence: семейный быт; scope: семейная выборка\n",
            encoding="utf-8",
        )
        (self.article / "claims.md").write_text(
            "- [C1] verified [S1] [S2] — описание семейных сервизов\n",
            encoding="utf-8",
        )
        article_text = (
            "# Почему сервиз стоял за стеклом?\n\n"
            + "В статье исследуется бытовой контекст. " * 35
            + "\n\n## Важные детали\n\n"
            + "В статье исследуется бытовой контекст. " * 35
            + "\n\n![Деталь посуды](images/detail-one.png)\n"
            + "*Иллюстрация, созданная с помощью ИИ: крупный план посуды.*\n\n"
            + "## Вещь и память\n\n"
            + "В статье исследуется бытовой контекст. " * 35
            + "\n\n![Праздничная сервировка](images/detail-two.png)\n"
            + "*Иллюстрация, созданная с помощью ИИ: праздничный стол.*\n\n"
            + "В статье исследуется бытовой контекст. " * 10
        )
        (self.article / "draft.md").write_text(
            article_text,
            encoding="utf-8",
        )
        (self.article / "review.md").write_text(
            "VERDICT: PASS\nFACT_CHECK: PASS\nSTYLE_CHECK: PASS\n"
            "COPYRIGHT_CHECK: PASS\nVISUAL_CHECK: PASS\n",
            encoding="utf-8",
        )
        (self.article / "anti-slop-report.md").write_text("VERDICT: PASS\nПовторы удалены.\n", encoding="utf-8")
        Image.new("RGB", (16, 16), color=(170, 130, 110)).save(images / "cover.png")
        Image.new("RGB", (16, 16), color=(110, 150, 130)).save(images / "detail-one.png")
        Image.new("RGB", (16, 16), color=(170, 120, 140)).save(images / "detail-two.png")
        self.images_manifest = {
            "images": [{
                "path": "images/cover.png",
                "kind": "ai_illustration",
                "caption": "Иллюстрация, созданная с помощью ИИ",
                "prompt": "An old porcelain tea set",
                "rights": "ai_generated",
                "checked": True,
                "historical_check": "PASS",
            }, {
                "path": "images/detail-one.png",
                "kind": "ai_illustration",
                "caption": "Иллюстрация, созданная с помощью ИИ: крупный план посуды.",
                "prompt": "Close-up of porcelain",
                "rights": "ai_generated",
                "checked": True,
                "historical_check": "PASS",
            }, {
                "path": "images/detail-two.png",
                "kind": "ai_illustration",
                "caption": "Иллюстрация, созданная с помощью ИИ: праздничный стол.",
                "prompt": "Tea party table",
                "rights": "ai_generated",
                "checked": True,
                "historical_check": "PASS",
            }]
        }
        self.write_json(images / "manifest.json", self.images_manifest)
        (self.article / "publish.md").write_text(
            "![Обложка](images/cover.png)\nИллюстрация, созданная с помощью ИИ\n\n"
            "<!-- APPROVED_ARTICLE_START -->\n" + article_text + "\n<!-- APPROVED_ARTICLE_END -->\n"
            "\n<!-- DZEN_POLICY_RISK: AI_GENERATED_TEXT -->\n"
            "## Происхождение и ограничения\n"
            "Текст полностью создан с помощью ИИ. Требования Дзена могут запрещать такие тексты, "
            "и публикация, модерация и монетизация не гарантированы.\n",
            encoding="utf-8",
        )
        self.manifest = {
            "schema_version": 1,
            "generation": "fully_ai_generated",
            "status": "PACKAGED",
            "title": "Почему сервиз стоял за стеклом?",
            "source_gate": "PASS",
            "editorial_gate": "PASS",
            "image_gate": "PASS",
            "policy_risk_acknowledged": True,
            "publication_status": "NOT_PUBLISHED",
            "moderation_status": "NOT_CHECKED",
            "monetization_status": "NOT_VERIFIED",
        }
        self.write_json(self.article / "manifest.json", self.manifest)

    @staticmethod
    def write_json(path: Path, data: dict):
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def check_errors(self):
        return "\n".join(validate_package(self.article))

    def test_valid_package(self):
        self.assertEqual([], validate_package(self.article))

    def test_rejects_article_with_only_one_image(self):
        self.images_manifest["images"] = self.images_manifest["images"][:1]
        self.write_json(self.article / "images" / "manifest.json", self.images_manifest)
        self.assertIn("images: expected 3 or 4 illustrations including cover", self.check_errors())

    def test_rejects_two_or_five_images(self):
        original = self.images_manifest["images"]
        for count in (2, 5):
            with self.subTest(count=count):
                self.images_manifest["images"] = original[:2] if count == 2 else original + [dict(original[1]), dict(original[2])]
                self.write_json(self.article / "images" / "manifest.json", self.images_manifest)
                self.assertIn("images: expected 3 or 4 illustrations including cover", self.check_errors())
        self.images_manifest["images"] = original

    def test_accepts_four_distinct_images(self):
        Image.new("RGB", (16, 16), color=(130, 110, 180)).save(self.article / "images" / "extra.png")
        self.images_manifest["images"].append({
            "path": "images/extra.png", "kind": "ai_illustration",
            "caption": "Иллюстрация, созданная с помощью ИИ: другой сюжет.",
            "prompt": "Another distinct historical detail", "rights": "ai_generated",
            "checked": True, "historical_check": "PASS",
        })
        self.write_json(self.article / "images" / "manifest.json", self.images_manifest)
        addition = ("\n\n## Третий сюжет\n\nДругая подтверждённая деталь.\n\n"
                    "![Другой сюжет](images/extra.png)\n"
                    "*Иллюстрация, созданная с помощью ИИ: другой сюжет.*\n\n"
                    "Вывод с новой мыслью.")
        draft = self.article / "draft.md"
        draft.write_text(draft.read_text(encoding="utf-8") + addition, encoding="utf-8")
        publish = self.article / "publish.md"
        publish.write_text(publish.read_text(encoding="utf-8").replace("\n<!-- APPROVED_ARTICLE_END -->", addition + "\n<!-- APPROVED_ARTICLE_END -->"), encoding="utf-8")
        self.assertEqual([], validate_package(self.article))

    def test_rejects_missing_inline_illustration(self):
        for filename in ("draft.md", "publish.md"):
            with self.subTest(filename=filename):
                path = self.article / filename
                original = path.read_text(encoding="utf-8")
                path.write_text(original.replace("![Деталь посуды](images/detail-one.png)", ""), encoding="utf-8")
                expected = ("publish: missing inline image reference images/detail-one.png" if filename == "draft.md"
                            else "publish: approved draft content differs")
                self.assertIn(expected, self.check_errors())
                path.write_text(original, encoding="utf-8")

    def test_rejects_inline_illustration_caption_mismatch(self):
        path = self.article / "draft.md"
        path.write_text(path.read_text(encoding="utf-8").replace("*Иллюстрация, созданная с помощью ИИ: праздничный стол.*", "*Подлинная фотография.*"), encoding="utf-8")
        self.assertIn("publish: missing inline image caption for images/detail-two.png", self.check_errors())

    def test_rejects_inline_illustrations_clustered_in_one_section(self):
        for filename in ("draft.md", "publish.md"):
            path = self.article / filename
            path.write_text(path.read_text(encoding="utf-8").replace("## Вещь и память", "### Вещь и память"), encoding="utf-8")
        self.assertIn("publish: inline images not distributed across sections", self.check_errors())

    def test_rejects_duplicated_image_asset(self):
        self.images_manifest["images"][2]["path"] = "images/detail-one.png"
        self.write_json(self.article / "images" / "manifest.json", self.images_manifest)
        self.assertIn("images: duplicate image path", self.check_errors())

    def test_rejects_same_image_under_different_filenames(self):
        source = self.article / "images" / "detail-one.png"
        (self.article / "images" / "detail-two.png").write_bytes(source.read_bytes())
        self.assertIn("images: duplicate image content", self.check_errors())

    def test_requires_two_real_source_entries(self):
        (self.article / "sources.md").write_text("- [S1] https://museum.example/x\n", encoding="utf-8")
        self.assertIn("sources", self.check_errors())

    def test_rejects_disputed_central_claim(self):
        (self.article / "claims.md").write_text("- [C1] disputed [S1] [S2] — спорно", encoding="utf-8")
        self.assertIn("claims", self.check_errors())

    def test_rejects_unknown_claim_source(self):
        (self.article / "claims.md").write_text("- [C1] verified [S99] — несуществующий источник", encoding="utf-8")
        self.assertIn("S99", self.check_errors())

    def test_requires_actual_image_file(self):
        (self.article / "images" / "cover.png").unlink()
        self.assertIn("image", self.check_errors())

    def test_rejects_image_path_escape(self):
        self.images_manifest["images"][0]["path"] = "../../escaped.png"
        self.write_json(self.article / "images" / "manifest.json", self.images_manifest)
        self.assertIn("image", self.check_errors())

    def test_rejects_ai_reconstruction_without_disclosure(self):
        image = self.images_manifest["images"][0]
        image["kind"] = "ai_reconstruction"
        image["caption"] = "Редкое архивное фото 1978 года"
        self.write_json(self.article / "images" / "manifest.json", self.images_manifest)
        self.assertIn("reconstruction", self.check_errors())

    def test_requires_visual_review(self):
        self.images_manifest["images"][0]["checked"] = False
        self.write_json(self.article / "images" / "manifest.json", self.images_manifest)
        self.assertIn("image", self.check_errors())

    def test_rejects_missing_policy_warning(self):
        (self.article / "publish.md").write_text("# Готово", encoding="utf-8")
        self.assertIn("policy", self.check_errors())

    def test_rejects_stub_publication_with_policy_warning(self):
        (self.article / "publish.md").write_text(
            "<!-- DZEN_POLICY_RISK: AI_GENERATED_TEXT -->\nИИ, риск Дзена.\n",
            encoding="utf-8",
        )
        self.assertIn("publish: packaged article is too short", self.check_errors())

    def test_rejects_missing_readable_platform_risk_disclosure(self):
        path = self.article / "publish.md"
        path.write_text(
            path.read_text(encoding="utf-8").split("<!-- DZEN_POLICY_RISK:")[0]
            + "<!-- DZEN_POLICY_RISK: AI_GENERATED_TEXT -->\nИИ\n",
            encoding="utf-8",
        )
        self.assertIn("policy: complete visible AI/platform disclosure missing", self.check_errors())

    def test_rejects_disclosure_hidden_in_html_comment(self):
        path = self.article / "publish.md"
        original = path.read_text(encoding="utf-8")
        original = original.replace("## Происхождение и ограничения\n", "<!-- hidden disclosure begins\n## Происхождение и ограничения\n") + "\n-->"
        path.write_text(original, encoding="utf-8")
        self.assertIn("policy: complete visible AI/platform disclosure missing", self.check_errors())

    def test_rejects_modified_publication_text(self):
        path = self.article / "publish.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("В статье исследуется бытовой контекст.", "В статье продаётся дорогой товар."), encoding="utf-8")
        self.assertIn("publish: approved draft content differs", self.check_errors())

    def test_rejects_injected_unreviewed_paragraph(self):
        path = self.article / "publish.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "<!-- APPROVED_ARTICLE_END -->",
                "Рекламный абзац: покупайте секретный товар.\n<!-- APPROVED_ARTICLE_END -->",
            ),
            encoding="utf-8",
        )
        self.assertIn("publish: approved draft content differs", self.check_errors())

    def test_rejects_source_appendix_in_publication(self):
        path = self.article / "publish.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "<!-- DZEN_POLICY_RISK: AI_GENERATED_TEXT -->",
                "## Ссылки на источники\n- [S1] [Музей](https://museum.example/collection)\n"
                "<!-- DZEN_POLICY_RISK: AI_GENERATED_TEXT -->",
            ),
            encoding="utf-8",
        )
        self.assertIn("publish: unexpected content after approved article", self.check_errors())

    def test_rejects_missing_image_link_in_publication(self):
        path = self.article / "publish.md"
        path.write_text(path.read_text(encoding="utf-8").replace("![Обложка](images/cover.png)", ""), encoding="utf-8")
        self.assertIn("publish: missing image reference", self.check_errors())

    def test_rejects_image_caption_mismatch_in_publication(self):
        path = self.article / "publish.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("Иллюстрация, созданная с помощью ИИ", "Старинная фотография"),
            encoding="utf-8",
        )
        self.assertIn("publish: missing image caption", self.check_errors())

    def test_rejects_fake_visible_caption_with_real_caption_hidden(self):
        path = self.article / "publish.md"
        published = path.read_text(encoding="utf-8").replace(
            "Иллюстрация, созданная с помощью ИИ\n\n<!-- APPROVED_ARTICLE_START -->",
            "Подлинный снимок из семейного архива\n\n<!-- Иллюстрация, созданная с помощью ИИ -->\n<!-- APPROVED_ARTICLE_START -->",
        )
        path.write_text(published, encoding="utf-8")
        self.assertIn("publish: missing image caption", self.check_errors())

    def test_rejects_source_ids_inside_draft_and_approved_article(self):
        for filename in ("draft.md", "publish.md"):
            with self.subTest(filename=filename):
                path = self.article / filename
                original = path.read_text(encoding="utf-8")
                path.write_text(original.replace("В статье исследуется бытовой контекст.", "В статье исследуется бытовой контекст. [S4] [C2]"), encoding="utf-8")
                self.assertIn(f"{filename.split('.')[0]}: internal citation marker in reader text", self.check_errors())
                path.write_text(original, encoding="utf-8")

    def test_rejects_source_summary_in_reader_text(self):
        for filename in ("draft.md", "publish.md"):
            with self.subTest(filename=filename):
                path = self.article / filename
                original = path.read_text(encoding="utf-8")
                path.write_text(original + "\n**Источники:** музей, архив.\n", encoding="utf-8")
                self.assertIn(f"{filename.split('.')[0]}: source list in reader text", self.check_errors())
                path.write_text(original, encoding="utf-8")

    def test_rejects_internal_filename_in_reader_text(self):
        path = self.article / "draft.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nСсылки приведены в `sources.md`.\n", encoding="utf-8")
        self.assertIn("draft: internal file reference in reader text", self.check_errors())

    def test_internal_claim_ledger_remains_allowed(self):
        self.assertIn("[S1]", (self.article / "sources.md").read_text(encoding="utf-8"))
        self.assertIn("[C1]", (self.article / "claims.md").read_text(encoding="utf-8"))
        self.assertEqual([], validate_package(self.article))

    def test_rejects_corrupt_image_with_valid_magic_bytes(self):
        (self.article / "images" / "cover.png").write_bytes(b"\x89PNG\r\n\x1a\nXXXX")
        self.assertIn("image 1: cannot decode image", self.check_errors())

    def test_rejects_fake_archival_caption_even_with_ii_letters(self):
        self.images_manifest["images"][0]["caption"] = "Иллюстрации из архива: подлинный снимок"
        self.write_json(self.article / "images" / "manifest.json", self.images_manifest)
        self.assertIn("AI illustration disclosure missing", self.check_errors())

    def test_rejects_non_string_image_caption_without_exception(self):
        self.images_manifest["images"][0]["caption"] = 42
        self.write_json(self.article / "images" / "manifest.json", self.images_manifest)
        self.assertIn("image 1: caption must be a string", self.check_errors())

    def test_requires_anti_slop_pass_report(self):
        (self.article / "anti-slop-report.md").unlink()
        self.assertIn("anti-slop", self.check_errors())

    def test_rejects_unfinished_anti_slop_report(self):
        (self.article / "anti-slop-report.md").write_text("VERDICT: REWORK", encoding="utf-8")
        self.assertIn("anti-slop: missing VERDICT: PASS", self.check_errors())

    def test_rejects_incomplete_source_evidence(self):
        (self.article / "sources.md").write_text(
            "- [S1] https://a.example/one\n- [S2] https://b.example/two\n", encoding="utf-8"
        )
        self.assertIn("sources: missing evidence metadata", self.check_errors())

    def test_rejects_empty_or_fake_source_metadata(self):
        (self.article / "sources.md").write_text(
            "- [S1] https://a.example/one — A; accessed: ; evidence: ; scope: \n"
            "- [S2] https://b.example/two — B; accessed: oops; evidence: not read; scope: none\n",
            encoding="utf-8",
        )
        self.assertIn("sources: invalid access/evidence metadata", self.check_errors())

    def test_rejects_fictional_external_statuses(self):
        self.manifest["publication_status"] = "PUBLISHED"
        self.manifest["moderation_status"] = "APPROVED"
        self.manifest["monetization_status"] = "VERIFIED"
        self.write_json(self.article / "manifest.json", self.manifest)
        self.assertIn("publication_status", self.check_errors())

    def test_requires_ai_origin_in_manifest(self):
        self.manifest["generation"] = "human_authored"
        self.write_json(self.article / "manifest.json", self.manifest)
        self.assertIn("generation", self.check_errors())

    def test_rejects_editor_failure(self):
        (self.article / "review.md").write_text("VERDICT: REWORK", encoding="utf-8")
        self.assertIn("review", self.check_errors())

    def test_rejects_stub_article(self):
        (self.article / "draft.md").write_text("# Скоро", encoding="utf-8")
        self.assertIn("draft", self.check_errors())

    def test_unfinished_status_cannot_pass(self):
        self.manifest["status"] = "BLOCKED"
        self.write_json(self.article / "manifest.json", self.manifest)
        self.assertIn("status", self.check_errors())

    def test_image_validation_closes_file_handles(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ResourceWarning)
            self.assertEqual([], validate_package(self.article))
            gc.collect()
        self.assertEqual([], [x for x in caught if issubclass(x.category, ResourceWarning)])


if __name__ == "__main__":
    unittest.main()
