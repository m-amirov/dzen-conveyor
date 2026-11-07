---
name: dzen-publishing
description: Use when assembling a fully reviewed «Люди и время» Dzen article into a verifiable local publication package, without posting it anywhere.
---

# Dzen Publishing Package

## Scope boundary

**Publishing means packaging, not upload.** This skill never accesses Dzen Studio, browser posting flows, channel credentials, API publishing endpoints or monetization settings. Even a user request to mark an article as published cannot override the truthful artifact state. Do not call a package `published`, `moderated`, or `monetized`.

## Input gate

Read the article's real `brief.md`, `sources.md`, `claims.md`, `draft.md`, `review.md`, `images/manifest.json`, and original image files. Require `VERDICT: PASS` plus independently supported `FACT_CHECK: PASS`, `STYLE_CHECK: PASS`, `COPYRIGHT_CHECK: PASS`, `VISUAL_CHECK: PASS`. Absence of approval, checked visuals or usable assets is `BLOCKED` and must not be bypassed under deadline pressure. Follow `docs/dzen-compliance.md`.

## Assemble

1. Require `anti-slop-report.md` with `VERDICT: PASS`. Create `publish.md` with the unchanged approved **article paragraphs in order**, plus ordered Markdown image references `![...](images/...)` and **exact matching** captions from `images/manifest.json`. Include every source URL from `sources.md` in a clickable source list. Do not add unsupported material or rewrite approved paragraphs; route changes back to `dzen-editor`.
2. Include `<!-- DZEN_POLICY_RISK: AI_GENERATED_TEXT -->` followed by a visible section headed exactly `## Происхождение и ограничения`. Explicitly say «Текст полностью создан с помощью ИИ», that Dzen's current requirements may disallow automatic writing, and publication/moderation/monetization are **not guaranteed**.
3. Create `manifest.json` with `schema_version: 1`, `generation: "fully_ai_generated"`, `status: "PACKAGED"`, non-empty `title`, `source_gate: "PASS"`, `editorial_gate: "PASS"`, `image_gate: "PASS"`, `policy_risk_acknowledged: true`, `publication_status: "NOT_PUBLISHED"`, `moderation_status: "NOT_CHECKED"`, `monetization_status: "NOT_VERIFIED"`. These are local package assessments, **not** proof of platform approval.
4. Run `python3 scripts/validate_package.py editorial/articles/<slug>` against the **actual** article directory. If it fails, repair the concrete package defect or set `status: "BLOCKED"` and document the reason. Do not report a green result from reading a hypothetical file or from a successful test on another article.
5. Provide the absolute local package path and the validator's real exit status. Leave `publication_status: NOT_PUBLISHED`, `moderation_status: NOT_CHECKED` and `monetization_status: NOT_VERIFIED` in any user-facing status report.

## Failure behavior

If an earlier stage is blocked, create or retain `manifest.json` with `status: "BLOCKED"` and an actionable `block_reason`; do not synthesize empty images, sources or PASS reviews to satisfy the validator. No human-authored draft is required — the article itself is fully automated — but **publication is outside this pipeline**.
