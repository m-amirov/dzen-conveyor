---
name: dzen-image-creator
description: Use when generating article covers, historical editorial illustrations, visual reconstructions, or reviewing image authenticity for «Люди и время».
---

# Dzen Image Creator

## Principle

Create a **real checked raster asset**, never merely a prompt. Historical AI scenes are illustrations or reconstructions, **not archival evidence**.

## Procedure

1. Read `docs/visual-guide.md`, `brief.md`, `claims.md`, `draft.md`. Identify what the image should explain and the exact period/region.
2. Write a compact visual brief (`images/brief.md`) for cover and only justified inline images. List subject, era, props, dress, light, composition, exclusions and whether a real document is referenced. Avoid trademark clutter, fake archival stamps and text rendered into pixels.
3. Call the available image-generation tool when present; do not require a separate paid OpenAI API. Save the produced file under `images/` with an actual supported `.png`, `.jpg` or `.webp` extension.
4. **Inspect the resulting image** via an available visual inspection tool. Check crop, visible text artifacts, anachronisms, historically important props, anatomical errors and basic coherence. If P0/P1 errors are present, rework within a bounded two attempts.
5. In `images/manifest.json`, store each asset as:

```json
{"images":[{"path":"images/cover.png","kind":"ai_reconstruction","caption":"Визуальная реконструкция, созданная с помощью ИИ","prompt":"...","rights":"ai_generated","checked":true,"historical_check":"PASS"}]}
```

6. Use `kind: ai_illustration` with caption «Иллюстрация, созданная с помощью ИИ» when a scene is conceptual. Use `kind: ai_reconstruction` and explicit «Визуальная реконструкция» when it represents a historical scene. Distinguish genuine archival sources separately; this MVP does **not** package third-party archival images as generated assets.
7. Only set `checked: true` and `historical_check: PASS` after actual inspection. Passing the deterministic file validator proves only artifact structure, not visual truth.

## Blockers

No generator, file save or visual inspection → `BLOCKED_IMAGES_UNAVAILABLE`; preserve the brief for later retry, but do not claim image readiness. Unresolved severe crop or anachronism → `BLOCKED_VISUAL_MISLEADING`. Never satisfy a demand for «архивное фото 1975 года» by relabeling a synthetic picture.

## Avoid

Decorative images unrelated to text; photorealistic fakes presented as documents; fabricated photo metadata; prompt-only assets; unchecked rights or licensing claims.
