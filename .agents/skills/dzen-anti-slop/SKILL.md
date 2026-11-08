---
name: dzen-anti-slop
description: Use when reviewing or rewriting an AI-generated Dzen draft for semantic repetition, generic nostalgia, weak scenes, unnatural prose, or a lack of specific facts.
---

# Dzen Anti-Slop

## Principle

Quality means **substance per paragraph**, not hiding AI markers. This skill revises the complete automatically generated `draft.md` while preserving the verified meaning of `claims.md`.

## Procedure

1. Read `draft.md`, `brief.md`, `claims.md`, `sources.md` and `docs/style-guide.md`.
2. Map each paragraph to one new fact, interpretation or necessary story function. Mark duplicates, generalities and ungrounded emotional claims. Repeated «прошлое и настоящее связаны» metaphors without new information are not new content.
3. Check that headline, lead, development and conclusion answer the same research question, without excessive symmetry and boilerplate introductions.
4. Revise autonomously: cut repetitions, reorganize details, simplify pretentious phrases, replace unsupported claims with a sourced explanation, **never** invent quotes, people, dates or remembered dialogue to fill space.
5. Run a second pass against `claims.md` after every substantive rewrite. Internal source IDs must still support all factual statements, but their literal `[S#]` / `[C#]` markers and source footers must not appear in `draft.md`. Prefer a shorter, dense article over length achieved by paraphrase.
6. If the article lacks enough distinct verified detail to stand alone, send the pipeline back to `dzen-research` or return `BLOCKED_INSUFFICIENT_SUBSTANCE`; do not force a PASS by synonym swapping.
7. Save the revised full text in `draft.md` and the changes in `anti-slop-report.md`: repeated thesis clusters, deleted padding, newly added *sourced* details, unresolved issues, `VERDICT: PASS|REWORK|BLOCKED`.

## Pass criteria

- Every main paragraph adds something new.
- No imaginary memoirs, fabricated personal feelings, filler lists or unverified historical claims.
- The headline's promise is delivered in the text.
- The article has rhythm and specificity without sensationalism.
- No use of «AI detector bypass» tools or claims that a detector score proves human authorship.

## Example

Nine variations of «альбом сохраняет память» become one precise sentence; the rest of the space is used only if additional verified evidence about archival habits, sending photos and dating family albums is available.
