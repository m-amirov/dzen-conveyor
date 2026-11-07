"""Deterministic artifact validation for an AI-generated Dzen article.

This checks structural completeness and declared review evidence. It cannot
independently prove that external claims are true or that an image depicts
the correct period; those are editorial-review responsibilities.
"""

import argparse
import json
import re
from pathlib import Path

from PIL import Image, UnidentifiedImageError


SOURCE_RE = re.compile(r"(?m)^\s*-\s*\[(S\d+)\]\s+(https?://\S+)")
CLAIM_RE = re.compile(r"(?m)^\s*-\s*\[(C\d+)\]\s+(verified|disputed|unverified)\s+([^\n]+)")
SOURCE_REF_RE = re.compile(r"\[(S\d+)\]")
SOURCE_METADATA = ("accessed:", "evidence:", "scope:")
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
        if SOURCE_RE.match(line) and not all(field in line for field in SOURCE_METADATA):
            errors.append(f"sources: missing evidence metadata in {line[:70]}")

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
    base = article_dir.resolve()
    for index, image in enumerate(images, 1):
        label = f"image {index}"
        if not isinstance(image, dict):
            errors.append(f"{label}: metadata must be an object")
            continue
        relative = image.get("path")
        if not isinstance(relative, str) or not relative.startswith("images/"):
            errors.append(f"{label}: image path must be under images/")
            continue
        path = (article_dir / relative).resolve()
        if not path.is_relative_to(base / "images"):
            errors.append(f"{label}: image path escapes article directory")
            continue
        if path.suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
            errors.append(f"{label}: unsupported image format")
        if not path.is_file() or path.stat().st_size < 12:
            errors.append(f"{label}: image file missing or empty")
        else:
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


def check_publication(draft: str, publish: str, sources: str, images: list[dict], errors: list[str]) -> None:
    # All approved article paragraphs must appear in order. The publication
    # may add cover/captions and expand the source list, not rewrite the draft.
    offset = 0
    for paragraph in draft.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph or paragraph.startswith("**Источники:**"):
            continue
        position = publish.find(paragraph, offset)
        if position < 0:
            errors.append("publish: approved draft content differs")
            break
        offset = position + len(paragraph)
    for _, url in SOURCE_RE.findall(sources):
        if url not in publish:
            errors.append(f"publish: missing source URL {url}")
    for image in images:
        if not isinstance(image, dict):
            continue
        path = image.get("path")
        if isinstance(path, str) and f"]({path})" not in publish:
            errors.append(f"publish: missing image reference {path}")
        caption = image.get("caption")
        if isinstance(caption, str) and caption not in publish:
            errors.append(f"publish: missing image caption for {path}")


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
    if not re.search(r"(?m)^VERDICT: PASS\s*$", anti_slop):
        errors.append("anti-slop: missing VERDICT: PASS")
    for marker in REVIEW_MARKERS:
        if not re.search(rf"(?m)^{marker}: PASS\s*$", review):
            errors.append(f"review: missing {marker}: PASS")
    images = check_images(article_dir, errors)
    check_publication(draft, publish, sources, images, errors)
    if "<!-- DZEN_POLICY_RISK: AI_GENERATED_TEXT -->" not in publish:
        errors.append("policy: publication warning marker missing")
    disclosure = re.search(
        r"(?ms)^## Происхождение и ограничения\s*\n(.*?)(?=^## |\Z)", publish
    )
    note = disclosure.group(1).lower() if disclosure else ""
    if not all(term in note for term in ("полностью", "ии", "дзен", "монетизац")) or not (
        "требован" in note or "правил" in note
    ) or "не гарантир" not in note:
        errors.append("policy: complete visible AI/platform disclosure missing")

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
