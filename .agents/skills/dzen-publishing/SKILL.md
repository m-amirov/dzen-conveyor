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

1. Require `anti-slop-report.md` with `VERDICT: PASS`. In `publish.md`, place **only** the following sections in order:
   - one or more Markdown cover lines `![...](images/...)`, each immediately followed by the **exact** caption from `images/manifest.json` (italic markup is allowed);
   - `<!-- APPROVED_ARTICLE_START -->` on its own line; the complete `draft.md` **byte-for-byte in content** (aside from outer blank lines), including title and source-summary paragraph; `<!-- APPROVED_ARTICLE_END -->` on its own line; **never** insert unreviewed content inside;
   - `## Ссылки на источники`, then one Markdown list line `- [S1] [Название](https://...)` per source from `sources.md`, with matching IDs and URLs. No prose or advertisements in this section.
2. End with `<!-- DZEN_POLICY_RISK: AI_GENERATED_TEXT -->` and the following *exact, visible* note (keep wording aligned with `scripts/validate_package.py`, not inside another HTML comment):

   ```text
   ## Происхождение и ограничения
   Текст полностью создан с помощью ИИ. Требования Дзена могут запрещать такие тексты, и публикация, модерация и монетизация не гарантированы.
   ```

   No other unreviewed prose belongs outside the approved article block. If new text is necessary, revise and reapprove `draft.md` first.
3. Create `manifest.json` with `schema_version: 1`, `generation: "fully_ai_generated"`, `status: "PACKAGED"`, non-empty `title`, `source_gate: "PASS"`, `editorial_gate: "PASS"`, `image_gate: "PASS"`, `policy_risk_acknowledged: true`, `publication_status: "NOT_PUBLISHED"`, `moderation_status: "NOT_CHECKED"`, `monetization_status: "NOT_VERIFIED"`. These are local package assessments, **not** proof of platform approval.
4. Run `python3 scripts/validate_package.py editorial/articles/<slug>` against the **actual** article directory. If it fails, repair the concrete package defect or set `status: "BLOCKED"` and document the reason. Do not report a green result from reading a hypothetical file or from a successful test on another article.
5. Provide the absolute local package path and the validator's real exit status. Leave `publication_status: NOT_PUBLISHED`, `moderation_status: NOT_CHECKED` and `monetization_status: NOT_VERIFIED` in any user-facing status report.

## Failure behavior

If an earlier stage is blocked, create or retain `manifest.json` with `status: "BLOCKED"` and an actionable `block_reason`; do not synthesize empty images, sources or PASS reviews to satisfy the validator. No human-authored draft is required — the article itself is fully automated — but **publication is outside this pipeline**.
