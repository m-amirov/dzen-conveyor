"""Check repository Codex skill discovery and the seven-skill contract."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = (
    "dzen-idea-generator",
    "dzen-research",
    "dzen-writer",
    "dzen-anti-slop",
    "dzen-image-creator",
    "dzen-editor",
    "dzen-publishing",
)


class SkillContractTests(unittest.TestCase):
    def test_all_seven_skills_are_discoverable(self):
        skills = ROOT / ".agents" / "skills"
        self.assertEqual(set(EXPECTED), {p.name for p in skills.iterdir() if p.is_dir()})

    def test_each_skill_has_valid_discovery_frontmatter(self):
        for name in EXPECTED:
            with self.subTest(name=name):
                text = (ROOT / ".agents" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertRegex(text, r"\A---\nname: " + re.escape(name) + r"\n")
                self.assertRegex(text, r"(?m)^description: Use when .{20,300}$")
                self.assertIn("\n---\n", text)

    def test_skills_reference_artifacts_they_own(self):
        expected_files = {
            "dzen-idea-generator": "brief.md",
            "dzen-research": "sources.md",
            "dzen-writer": "draft.md",
            "dzen-anti-slop": "draft.md",
            "dzen-image-creator": "images/manifest.json",
            "dzen-editor": "review.md",
            "dzen-publishing": "publish.md",
        }
        for name, artifact in expected_files.items():
            with self.subTest(name=name):
                content = (ROOT / ".agents" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn(artifact, content)


if __name__ == "__main__":
    unittest.main()
