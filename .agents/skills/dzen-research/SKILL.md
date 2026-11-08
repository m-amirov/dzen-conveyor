---
name: dzen-research
description: Use when researching a «Люди и время» article, checking historical or psychological claims, building a source register, or resolving conflicting evidence for Dzen.
---

# Dzen Research

## Principle

Make a checkable claim ledger from **sources actually accessed**. This step consumes `brief.md` and produces `sources.md` and `claims.md`; it never equates a search result with a read source.

## Process

1. Read the research question and time/geography in `brief.md`. Extract the central assertions that a future article would need.
2. Search primary sources (museum/archive pages, original documents, statistics, peer-reviewed studies), then reliable secondary analysis. Prefer two genuinely independent sources for the central premise.
3. Open and read each relevant source. For each, record a stable ID, title, publication/author, URL or archive catalog reference, access date, exact relevant information, limits and rights. A snippet, inaccessible link or guessed citation belongs only in **Leads to investigate**, never in the verified-source list.
4. For each material claim, add an entry using the exact contract: `- [C1] verified [S1] [S2] — precise assertion and scope`. Use `disputed` or `unverified` for weaker cases; do not promote uncertainty to fact because the piece is due today.
5. Check chronology, region, representation and the difference between policy, memoir and observed practice. If evidence conflicts, record both interpretations and explain the narrower supported version.
6. Save `sources.md` with `- [S1] https://... — author/title; accessed: YYYY-MM-DD; evidence: what was actually read; scope: period/region and limits`. These literal markers are required by the **internal-ledger** validator, and must record actual observations, not decorative text. Save `claims.md` with every claim's status and evidence. Keep search leads separate under a non-verified heading. Source/claim IDs are for internal checking and must not be appended to `draft.md` or `publish.md`.

## Gate

- If fewer than two credible independent evidence strands support a central thesis, seek more evidence or narrow the thesis. If no support can be obtained, return `BLOCKED_UNVERIFIED_CLAIM` with the exact missing source class.
- Without working research/browsing capability, do **not** fabricate an archive, URL, direct quote or document. Return `BLOCKED_RESEARCH_UNAVAILABLE` and make the failure visible.
- Never infer «в каждом доме», «все считали» or exact numbers from generic descriptions such as «widely used».

## Output to the writer

Provide: research question, supported angle, verified claims with source IDs, unresolved facts that **must not be stated**, and 3–5 essential concrete details. The writer may only assert what the ledger supports.

## Example

Input: «В 1978 году в каждом доме была радиоточка». Without statistical evidence, record `unverified` and narrow the investigation to *распространённость проводного радио и различия между регионами*, not an invented absolute.
