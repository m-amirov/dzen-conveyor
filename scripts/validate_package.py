"""Deterministic artifact validation for an AI-generated Dzen article.

This checks structural completeness and declared review evidence. It cannot
independently prove that external claims are true or that an image depicts
the correct period; those are editorial-review responsibilities.
"""

import argparse
from datetime import date
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, UnidentifiedImageError


SOURCE_RE = re.compile(r"(?m)^\s*-\s*\[(S\d+)\]\s+(https?://\S+)")
CLAIM_RE = re.compile(r"(?m)^\s*-\s*\[(C\d+)\]\s+(verified|disputed|unverified)\s+([^\n]+)")
SOURCE_REF_RE = re.compile(r"\[(S\d+)\]")
READER_CITATION_RE = re.compile(r"\[(?:S|C)\d+\]")
READER_SOURCE_LIST_RE = re.compile(
    r"(?mi)^\s*(?:#{1,6}\s+(?:источники|ссылки на источники|список источников)\s*$"
    r"|\*\*(?:источники|ссылки на источники|список источников):?\*\*"
    r"|(?:источники|ссылки на источники|список источников):)"
)
READER_INTERNAL_FILE_RE = re.compile(r"(?i)\b(?:sources|claims)\.md\b")
SOURCE_METADATA = ("accessed:", "evidence:", "scope:")
ARTICLE_START = "<!-- APPROVED_ARTICLE_START -->"
ARTICLE_END = "<!-- APPROVED_ARTICLE_END -->"
POLICY_MARKER = "<!-- DZEN_POLICY_RISK: AI_GENERATED_TEXT -->"
POLICY_NOTICE = (
    "## Происхождение и ограничения\n"
    "Текст полностью создан с помощью ИИ. Требования Дзена могут запрещать такие тексты, "
    "и публикация, модерация и монетизация не гарантированы."
)
REVIEW_MARKERS = ("VERDICT", "FACT_CHECK", "STYLE_CHECK", "COPYRIGHT_CHECK", "VISUAL_CHECK")
ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
IMAGE_SIGNATURES = {
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".webp": (b"RIFF",),
}


def read_text(article_dir: Path, relative: str, errors: list[str]) -> str:
    path = article_dir / relative
    if not path.is_file():
        errors.append(f"missing {relative}")
        return ""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError:
        errors.append(f"invalid UTF-8 in {relative}")
        return ""
    if not text.strip():
        errors.append(f"empty {relative}")
    return text


def read_json(article_dir: Path, relative: str, errors: list[str]) -> dict:
    value = read_text(article_dir, relative, errors)
    if not value:
        return {}
    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {relative}: {exc.msg}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{relative} must contain a JSON object")
        return {}
    return data


def check_sources_and_claims(sources: str, claims: str, errors: list[str]) -> None:
    source_ids = [name for name, _ in SOURCE_RE.findall(sources)]
    if len(set(source_ids)) < 2:
        errors.append("sources: at least two distinct read source entries are required")
    if len(source_ids) != len(set(source_ids)):
        errors.append("sources: duplicated source identifiers")
    for line in sources.splitlines():
        if SOURCE_RE.match(line):
            if not all(field in line for field in SOURCE_METADATA):
                errors.append(f"sources: missing evidence metadata in {line[:70]}")
                continue
            values = {}
            for field in ("accessed", "evidence", "scope"):
                match = re.search(rf"\b{field}:\s*([^;\n]*)", line)
                values[field] = match.group(1).strip() if match else ""
            try:
                stamp = date.fromisoformat(values["accessed"])
                valid_date = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", values["accessed"])) and stamp <= date.today()
            except ValueError:
                valid_date = False
            if not valid_date or len(values["evidence"]) < 8 or len(values["scope"]) < 8:
                errors.append(f"sources: invalid access/evidence metadata in {line[:70]}")

    matches = CLAIM_RE.findall(claims)
    if not matches:
        errors.append("claims: no structured claim entries")
    for claim_id, status, body in matches:
        if status != "verified":
            errors.append(f"claims: {claim_id} is {status}, not verified")
        links = SOURCE_REF_RE.findall(body)
        if not links:
            errors.append(f"claims: {claim_id} has no source references")
        for link in links:
            if link not in source_ids:
                errors.append(f"claims: {claim_id} references unknown {link}")
    # A malformed claim line must never silently disappear from validation.
    for line in claims.splitlines():
        if line.lstrip().startswith("- [C") and not CLAIM_RE.fullmatch(line):
            errors.append(f"claims: malformed entry {line[:80]}")


def check_images(article_dir: Path, errors: list[str]) -> list[dict]:
    manifest = read_json(article_dir, "images/manifest.json", errors)
    images = manifest.get("images")
    if not isinstance(images, list) or not images:
        errors.append("images: manifest must contain at least one image")
        return []
    if not 3 <= len(images) <= 4:
        errors.append("images: expected 3 or 4 illustrations including cover")
    base = article_dir.resolve()
    seen_paths: set[str] = set()
    seen_digests: set[str] = set()
    for index, image in enumerate(images, 1):
        label = f"image {index}"
        if not isinstance(image, dict):
            errors.append(f"{label}: metadata must be an object")
            continue
        relative = image.get("path")
        if not isinstance(relative, str) or not relative.startswith("images/"):
            errors.append(f"{label}: image path must be under images/")
            continue
        if relative in seen_paths:
            errors.append("images: duplicate image path")
        seen_paths.add(relative)
        path = (article_dir / relative).resolve()
        if not path.is_relative_to(base / "images"):
            errors.append(f"{label}: image path escapes article directory")
            continue
        if path.suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
            errors.append(f"{label}: unsupported image format")
        if not path.is_file() or path.stat().st_size < 12:
            errors.append(f"{label}: image file missing or empty")
        else:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest in seen_digests:
                errors.append("images: duplicate image content")
            seen_digests.add(digest)
            with path.open("rb") as image_file:
                header = image_file.read(12)
            if not any(header.startswith(prefix) for prefix in IMAGE_SIGNATURES.get(path.suffix.lower(), ())):
                errors.append(f"{label}: image file does not match declared image format")
            if path.suffix.lower() == ".webp" and header[8:12] != b"WEBP":
                errors.append(f"{label}: invalid WEBP signature")
            try:
                with Image.open(path) as asset:
                    actual_format = asset.format
                    if asset.width < 16 or asset.height < 16:
                        errors.append(f"{label}: image dimensions are too small")
                    asset.verify()
                with Image.open(path) as asset:
                    asset.load()
                expected_format = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}.get(path.suffix.lower())
                if actual_format != expected_format:
                    errors.append(f"{label}: image format differs from extension")
            except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError):
                errors.append(f"{label}: cannot decode image")
        if not isinstance(image.get("prompt"), str) or not image["prompt"].strip():
            errors.append(f"{label}: image prompt not recorded")
        if not isinstance(image.get("rights"), str) or not image["rights"].strip():
            errors.append(f"{label}: image rights/origin not recorded")
        if image.get("checked") is not True or image.get("historical_check") != "PASS":
            errors.append(f"{label}: image not visually checked")
        kind = image.get("kind")
        caption = image.get("caption", "")
        if not isinstance(caption, str):
            errors.append(f"{label}: caption must be a string")
            continue
        caption_lower = caption.lower()
        ai_disclosed = bool(re.search(r"\bии\b", caption_lower)) and (
            "создан" in caption_lower or "сгенерирован" in caption_lower
        )
        if kind == "ai_reconstruction" and ("реконструкц" not in caption_lower or not ai_disclosed):
            errors.append(f"{label}: AI reconstruction disclosure missing")
        elif kind == "ai_illustration" and not ai_disclosed:
            errors.append(f"{label}: AI illustration disclosure missing")
        elif kind not in {"ai_reconstruction", "ai_illustration"}:
            errors.append(f"{label}: unsupported image kind")
        if any(term in caption_lower for term in ("архивное фото", "подлинный снимок", "реальное фото", "фотография из архива")):
            errors.append(f"{label}: misleading claim of archival authenticity")
    return images


def check_reader_text(text: str, label: str, errors: list[str]) -> None:
    """Editorial IDs and provenance files belong in ledgers, not reader copy."""
    if READER_CITATION_RE.search(text):
        errors.append(f"{label}: internal citation marker in reader text")
    if READER_SOURCE_LIST_RE.search(text):
        errors.append(f"{label}: source list in reader text")
    if READER_INTERNAL_FILE_RE.search(text):
        errors.append(f"{label}: internal file reference in reader text")


def check_publication(draft: str, publish: str, images: list[dict], errors: list[str]) -> None:
    # Require an exact immutable article block. Cover and policy note are
    # permitted only in their dedicated, structurally validated regions.
    if publish.count(ARTICLE_START) != 1 or publish.count(ARTICLE_END) != 1:
        errors.append("publish: approved draft markers missing or repeated")
        return
    prefix, remainder = publish.split(ARTICLE_START, 1)
    article, suffix = remainder.split(ARTICLE_END, 1)
    if article.strip() != draft.strip():
        errors.append("publish: approved draft content differs")

    # A caption must be visible right beside its own Markdown image, never
    # merely hidden in an HTML comment elsewhere in the publication.
    cover_lines = [line.strip() for line in prefix.splitlines() if line.strip()]
    expected_images = [item for item in images if isinstance(item, dict)]
    if len(cover_lines) != 2:
        errors.append("publish: unexpected cover content or missing image reference/caption")
    for index, image in enumerate(expected_images[:1]):
        path = image.get("path")
        caption = image.get("caption")
        link = cover_lines[2 * index] if len(cover_lines) > 2 * index else ""
        visible_caption = cover_lines[2 * index + 1].strip("*_ ") if len(cover_lines) > 2 * index + 1 else ""
        if not isinstance(path, str) or not re.fullmatch(r"!\[[^\]\n]+\]\(" + re.escape(path) + r"\)", link):
            errors.append(f"publish: missing image reference {path}")
        if not isinstance(caption, str) or visible_caption != caption:
            errors.append(f"publish: missing image caption for {path}")

    # Only the cover precedes the article. Remaining illustrations must be
    # embedded in the approved reader copy, each with its own visible caption.
    draft_lines = draft.splitlines()
    inline_section_indices: list[int] = []
    for image in expected_images[1:]:
        path = image.get("path")
        caption = image.get("caption")
        if not isinstance(path, str):
            continue
        image_line = re.compile(r"!\[[^\]\n]+\]\(" + re.escape(path) + r"\)")
        indices = [index for index, line in enumerate(draft_lines) if image_line.fullmatch(line.strip())]
        if len(indices) != 1:
            errors.append(f"publish: missing inline image reference {path}")
            continue
        index = indices[0]
        next_line = draft_lines[index + 1].strip("*_ ") if index + 1 < len(draft_lines) else ""
        if not isinstance(caption, str) or next_line != caption:
            errors.append(f"publish: missing inline image caption for {path}")
        previous_sections = [i for i, line in enumerate(draft_lines[:index]) if line.startswith("## ")]
        if not previous_sections or not any(line.strip() and not line.startswith("#") for line in draft_lines[index + 2:]):
            errors.append(f"publish: inline image not inside article sections {path}")
        else:
            inline_section_indices.append(previous_sections[-1])

    if len(inline_section_indices) != len(set(inline_section_indices)):
        errors.append("publish: inline images not distributed across sections")
    expected_paths = [image.get("path") for image in expected_images[1:]]
    all_inline_links = re.findall(r"!\[[^\]\n]+\]\(([^)\n]+)\)", draft)
    if sorted(all_inline_links) != sorted(path for path in expected_paths if isinstance(path, str)):
        errors.append("publish: undeclared or repeated inline image")

    parts = suffix.strip().split(POLICY_MARKER)
    if len(parts) != 2:
        errors.append("policy: publication warning marker missing or duplicated")
        return
    extra_content, policy_section = parts
    if extra_content.strip():
        errors.append("publish: unexpected content after approved article")
    if policy_section.strip() != POLICY_NOTICE:
        errors.append("policy: complete visible AI/platform disclosure missing")


def validate_package(article_dir: Path) -> list[str]:
    """Return concrete contract violations; an empty list means structural PASS."""
    errors: list[str] = []
    if not article_dir.is_dir():
        return [f"article directory does not exist: {article_dir}"]

    brief = read_text(article_dir, "brief.md", errors)
    sources = read_text(article_dir, "sources.md", errors)
    claims = read_text(article_dir, "claims.md", errors)
    draft = read_text(article_dir, "draft.md", errors)
    review = read_text(article_dir, "review.md", errors)
    anti_slop = read_text(article_dir, "anti-slop-report.md", errors)
    publish = read_text(article_dir, "publish.md", errors)
    manifest = read_json(article_dir, "manifest.json", errors)
    if brief and len(brief.strip()) < 30:
        errors.append("brief: too short")
    check_sources_and_claims(sources, claims, errors)
    if len(draft.strip()) < 1500:
        errors.append("draft: article is too short for a complete publication")
    if len(publish.strip()) < 1500:
        errors.append("publish: packaged article is too short")
    check_reader_text(draft, "draft", errors)
    check_reader_text(publish, "publish", errors)
    if not re.search(r"(?m)^VERDICT: PASS\s*$", anti_slop):
        errors.append("anti-slop: missing VERDICT: PASS")
    for marker in REVIEW_MARKERS:
        if not re.search(rf"(?m)^{marker}: PASS\s*$", review):
            errors.append(f"review: missing {marker}: PASS")
    images = check_images(article_dir, errors)
    check_publication(draft, publish, images, errors)
    if POLICY_MARKER not in publish:
        errors.append("policy: publication warning marker missing")

    expected = {
        "schema_version": 1,
        "generation": "fully_ai_generated",
        "status": "PACKAGED",
        "source_gate": "PASS",
        "editorial_gate": "PASS",
        "image_gate": "PASS",
        "policy_risk_acknowledged": True,
        "publication_status": "NOT_PUBLISHED",
        "moderation_status": "NOT_CHECKED",
        "monetization_status": "NOT_VERIFIED",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            errors.append(f"manifest: {key} must be {value!r}")
    if not isinstance(manifest.get("title"), str) or not manifest["title"].strip():
        errors.append("manifest: title required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check completeness of one Dzen article package")
    parser.add_argument("article_dir", type=Path)
    args = parser.parse_args()
    errors = validate_package(args.article_dir)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: complete structurally verified package: {args.article_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
