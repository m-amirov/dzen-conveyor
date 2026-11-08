---
name: dzen-image-creator
description: Use when generating article covers, historical editorial illustrations, visual reconstructions, or reviewing image authenticity for «Люди и время».
---

# Dzen Image Creator

## Principle

Create a **real checked raster asset**, never merely a prompt. Historical AI scenes are illustrations or reconstructions, **not archival evidence**.

## Procedure

1. Read `docs/visual-guide.md`, `brief.md`, `claims.md`, `draft.md`. Identify what the image should explain and the exact period/region.
2. Plan **3–4 distinct illustrations total, including exactly one cover and 2–3 inline illustrations**. Choose different, fact-grounded visual subjects for different article sections, not repeated versions of the same cover. Write the brief (`images/brief.md`) with each image's subject, era, props, light, composition, exclusions and intended section. Avoid fake archival stamps and text rendered into pixels.
3. Call the available image-generation tool once per distinct asset when present; do not require a separate paid OpenAI API. Save all resulting files under `images/` with actual `.png`, `.jpg` or `.webp` extensions. Never use duplicate content under different names to satisfy the quota.
4. **Inspect every resulting image** via an available visual inspection tool. Check crop, visible text artifacts, anachronisms, historically important props, anatomical errors and basic coherence. If P0/P1 errors are present, rework within a bounded two attempts.
5. In `images/manifest.json`, store each asset in reading order: **cover first, then inline illustrations**. Each asset has its own path, prompt, caption, rights and evidence of review, e.g.:

```json
{"images":[{"path":"images/cover.png","kind":"ai_reconstruction","caption":"Сервиз в застеклённом серванте советской квартиры. Художественная реконструкция.","prompt":"...","rights":"ai_generated","checked":true,"historical_check":"PASS"}]}
```

6. Place each of the 2–3 inline assets into `draft.md` directly after a relevant paragraph **in a different `##` section** using `![Содержательное описание](images/filename.webp)` and the exact caption from its manifest on the next line. Keep at least one paragraph of prose after the final illustration. The publishing skill carries these embeds into the approved article unchanged; only the cover goes before its start marker.
7. Write **natural, specific reader captions** about the depicted people, setting or object, never repetitive «создано ИИ / нейросетью» phrases. Use `kind: ai_illustration` for conceptual illustrations; for `kind: ai_reconstruction` include the plain-language label «Художественная реконструкция» in the caption. Distinguish genuine archival sources separately; this MVP does **not** package third-party archival images as generated assets. The publishing skill provides **one visible overall disclosure** for text and images instead of repeating AI origin under every illustration; keep precise provenance in manifest metadata.
8. Only set `checked: true` and `historical_check: PASS` after actual inspection. Passing the deterministic file validator proves only artifact structure, not visual truth.

## Blockers

No generator, file save or visual inspection → `BLOCKED_IMAGES_UNAVAILABLE`; preserve the brief for later retry, but do not claim image readiness. Unresolved severe crop or anachronism → `BLOCKED_VISUAL_MISLEADING`. Never satisfy a demand for «архивное фото 1975 года» by relabeling a synthetic picture.

## Avoid

Decorative images unrelated to text; photorealistic fakes presented as documents; fabricated photo metadata; prompt-only assets; unchecked rights or licensing claims.
