---
name: dzen-idea-generator
description: Use when planning article topics, finding new series, replacing repeated ideas, or choosing the next «Люди и время» publication for Dzen.
---

# Dzen Idea Generator

## Purpose

Find **researchable, non-repetitive questions** for «Люди и время», not just emotional headlines. This skill owns idea selection and the `brief.md` seed; it does not write historical claims as facts.

## Inputs

Read `docs/editorial-concept.md`, `editorial/first-30-topics.md` and existing titles under `editorial/articles/`. If the user supplied a topic, preserve its purpose and optimize the question; do not silently switch rubrics.

## Procedure

1. Generate 8–12 genuinely different candidate questions, each anchored in a tangible object, documented practice, or testable psychological phenomenon.
2. Compare the core **angle**, not just headline wording, against the provided topic backlog and existing article folders. Flag conceptual duplicates, including synonyms and reused scenes.
3. For each remaining idea, record a likely source path (museum catalog, archive, research paper, primary letters, etc.). A *research direction* is not a found or verified citation.
4. Score each idea from 1–5 for reader recognition, originality, source feasibility and visual clarity. Report research complexity as low/medium/high. No guarantees of traffic or monetization.
5. Prefer ideas with a compelling question and accessible verification. Avoid premises that assert unverified social comparisons (e.g. «раньше люди были добрее»); phrase them as open questions.
6. Write a selected idea to `editorial/articles/<slug>/brief.md` using `templates/article-brief.md`, with research questions, period/geography, image direction and assumptions to test.

## Result format

Show a ranked compact table: `Тема | Рубрика | Отличие от предыдущих | Источники для поиска | Сложность | Причина выбора`. Then report the chosen `brief.md` path. If all candidates repeat published angles or lack research direction, return `BLOCKED_IDEA_QUALITY` and explain why.

## Example

Instead of «В СССР все соседи были дружнее» suggest: «Что позволяло соседям общаться во дворах типовых домов — и что менялось от района к району?» Research direction: urban sociology and memoir collections; no historical premise asserted as universal.

## Failure modes

- A headline is novel in words but identical in the reader's promised payoff → flag as duplicate.
- Emotional hook is not a verifiable question → rewrite as question.
- Model invents an archive title or URL to seem convincing → label it as a source to search, never a verified reference.
