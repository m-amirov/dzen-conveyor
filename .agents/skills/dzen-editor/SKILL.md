---
name: dzen-editor
description: Use when performing final factual, stylistic, visual, copyright and ethical acceptance of a generated «Люди и время» Dzen article before packaging.
---

# Dzen Editor

## Principle

Act as an **independent quality gate** for automatically generated articles. An output of an earlier skill is a proposal, not evidence that it passed. No manual author draft or intermediate human sign-off is required.

## Acceptance pass

Read `brief.md`, `sources.md`, `claims.md`, `draft.md`, `anti-slop-report.md`, `images/manifest.json`, the real image files and applicable docs.

1. **Factual:** Map central text claims back to the ledger. Read the supplied evidence where possible. Separate rules from actual practice, one memoir from population evidence, correlation from causation, and historical eras/regions. Mark invented quotes and missing sources.
2. **Style:** Does every section provide a new insight? Is the title's promise fulfilled? Is the opening specific, the ending earned, and the text free of repetitive sentimental filler? Check that the reader sees no `[S#]`/`[C#]` identifiers, `Источники:` footer, `sources.md` pointer or separate source appendix. Audit the facts from the internal ledgers instead.
3. **Copyright and ethics:** Is prose original? Are quoted passages attributed and appropriately limited? Are rights claims to assets justified? Are living/private individuals handled respectfully?
4. **Visual:** Inspect all **3–4 distinct assets** (one cover plus 2–3 inline images in different sections), their placement and captions. Check that each illustrates the adjacent factual topic and is not a near-duplicate. No synthetic photo may be passed as a real archive. A prompt or filename is not a visual check.
5. **Platform:** Disclose `fully_ai_generated` and the documented Dzen-policy risk; do not claim moderation or monetization approval.

## `review.md` output contract

Start with exactly these machine-readable markers, each based on an actual check:

```text
VERDICT: REWORK
FACT_CHECK: FAIL
STYLE_CHECK: NOT_RUN
COPYRIGHT_CHECK: NOT_RUN
VISUAL_CHECK: FAIL
```

Then give severity-ordered findings (`P0`, `P1`, `P2`), exact quoted passage or image, evidence IDs, minimum necessary action, and a recheck list. Only write `VERDICT: PASS` when **all** five markers read `PASS` and the image manifest also shows actual inspection.

## Automatic rework

Route factual gaps to `dzen-research`, prose issues to `dzen-writer`/`dzen-anti-slop`, image errors to `dzen-image-creator`; allow at most two full automatic correction rounds. If a P0/P1 cannot be resolved, set `VERDICT: BLOCKED` with a specific blocker and do not call the publishing skill to claim readiness.

## Example

Normative requirement «радиоточку следует установить» plus one person's memoir cannot justify «в каждом доме СССР была радиоточка». Correct the scope or research actual national statistics; a synthetic cover captioned «архивное фото 1978 года» must be relabeled reconstruction and re-reviewed.
