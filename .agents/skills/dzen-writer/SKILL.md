---
name: dzen-writer
description: Use when creating a complete original Russian Dzen article from verified research and an editorial brief for «Люди и время», even when no human-written draft exists.
---

# Dzen Writer — Fully Automatic

## Principle

Write the **entire article** from `brief.md`, `sources.md` and `claims.md`. User-authored prose is **not** required. Ground storytelling in facts, not invented personal memories or repetitive emotional filler.

## Research threshold

Read the central question and every verified `[C#]` claim with its supporting `[S#]` sources. A normal finished article needs several distinct verified facts supporting different parts of the narrative; two generic notes repeated in ten paragraphs are **not** sufficient. If too sparse, return to `dzen-research` automatically to add substantial evidence. If tools/evidence remain unavailable, return `BLOCKED_INSUFFICIENT_RESEARCH`, not a padded article.

## Produce `draft.md`

1. State the specific research question in the lead through one tangible scene or documented object. If describing a hypothetical typical scene, mark it as illustrative rather than an actual event.
2. Build 3–5 meaningfully different sections: what was practiced, why/where/when, what varied, what it meant for people, how circumstances changed. Omit any section unsupported by facts.
3. Generate the full Russian text **without asking for an author draft or intermediate approval**. Aim around 4–6 thousand characters only when the material sustains it; do not invent facts to hit the target.
4. Use precise attribution for quotations, figures, personal accounts and local practices. No fabricated dialogue, fake diary, invented grandmother recollection, first-person claim of lived experience, or generic «все думали» statements.
5. Add reader-useful context, examples *grounded in the ledger*, and a nuanced ending. Contradictions and uncertainty remain visible; Dzen needs substance, not a sentimental universal moral.
6. Write only reader-facing prose in `draft.md`: title, lead, article sections and conclusion. Do not insert `[S1]` / `[C1]` ledger codes, a source list, footnotes referring to `sources.md` / `claims.md`, or a publication-package appendix. Use natural-language attribution to museums, researchers and works when it helps readers understand a claim. Keep exact URLs and evidence mapping **only** in `sources.md` and `claims.md`.
7. Check the draft against `docs/style-guide.md`: repeated thesis, unsupported decorative scenes, boilerplate introduction, stale generalizations and leaked internal evidence codes. Save the complete result as `draft.md` and send it to `dzen-anti-slop`.

## Output

Report the file path, approximate length, factual coverage by claim IDs, and any unresolved questions. Do **not** claim publication readiness — editor and visual gates follow.

## Example

Sparse input `[C1] family portraits were scheduled` and `[C2] photos were kept in albums` does not justify a long imagined talk with a grandmother. Obtain additional verified details about studios, equipment, pricing, dates or archival usage; if impossible, block for research. A short truthful analysis is preferable to a full-length false documentary.
