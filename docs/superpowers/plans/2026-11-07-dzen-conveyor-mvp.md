# Dzen Conveyor MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a seven-skill Codex-first editorial system that fully generates researched Russian articles and original illustrative assets for «Люди и время», then prepares packages for manual publication.

**Architecture:** `AGENTS.md` orchestrates seven project-local skills, each producing durable Markdown/JSON evidence inside `editorial/articles/<slug>/`. A small standard-library Python validator checks artifact contracts and rejects incomplete, unattributed or misleading packages. There is no separate AI API, server or automatic upload to Dzen.

**Tech Stack:** Markdown, YAML skill frontmatter, JSON, Python 3 standard library `unittest`, GitHub PR.

**Spec:** `docs/superpowers/specs/2026-11-07-people-and-time-conveyor-design.md`

## Global Constraints

- Generate every article's narrative text automatically; never require human source paragraphs or author notes.
- Do not auto-publish, pay for external services, impersonate a human author, fabricate sources or conceal AI origin.
- All finished packages must disclose `generation: fully_ai_generated` and platform-policy risk.
- If a required tool, source or image is unavailable, return a specific `BLOCKED` status rather than falsely declaring success.
- Scope of MVP is documentation, skills, reusable templates, validation, and one safe dry-run example; no external Dzen writes.
- Preserve original research questions and thirty topics in the spec.

## Review Focus

1. No browser access: research must block instead of hallucinating source URLs.
2. Contradictory or weak sources: prevent `QA_PASSED` while central claims remain disputed.
3. No image generator: cannot package missing imagery as completed.
4. Fictional archival photo passed as genuine: image acceptance must reject that representation.
5. Pressure to auto-publish despite explicit exclusion: publishing skill must package only.

---

### Task 1: Foundation, editorial docs and sample set

**Files:** Create `README.md`, `AGENTS.md`, `docs/editorial-concept.md`, `docs/style-guide.md`, `docs/visual-guide.md`, `docs/fact-checking.md`, `docs/dzen-compliance.md`, `editorial/first-30-topics.md`.

**Interfaces:** `AGENTS.md` defines commands `подготовь статью на тему`, `подготовь следующую тему`, `проверь статью` and the order of seven skills. Documents refer to one approved spec rather than restating contradictory requirements.

- [ ] **Step 1: Red check.** Confirm no existing project files (or inspect and preserve any newly added files); record missing docs and routing.
- [ ] **Step 2: Implement.** Write concise docs, topic backlog with six rubrics and provenance policy; no mandatory author-text gate.
- [ ] **Step 3: Verify.** Check relative links, document consistency, `git diff --check`; reject presence of obsolete `AUTHOR_DRAFT` or `HUMAN_APPROVAL` requirements for generation.
- [ ] **Step 4: Commit.** Commit only foundation files.

### Task 2: Contract templates and deterministic validator

**Files:** Create `templates/article-brief.md`, `templates/source-register.md`, `templates/claim-ledger.md`, `templates/review.md`, `templates/manifest.json`, `scripts/validate_package.py`, `tests/test_validate_package.py`, `tests/fixtures/`.

**Interfaces:** Validator CLI: `python3 scripts/validate_package.py editorial/articles/<slug>`. Returns exit 0 only when package has valid status `PACKAGED`, provenance, source ledger, full article, review evidence, non-empty existing images with accurate captions, and publication risk note.

- [ ] **Step 1: Red.** Write `unittest` fixtures for valid package and for each Review Focus failure (missing sources, disputed claims, missing image, archive-image mislabel, absent risk note).
- [ ] **Step 2: Run.** `python3 -m unittest discover -s tests -v`, expect contract tests to fail before validator exists.
- [ ] **Step 3: Green.** Add the minimal standard-library validator and templates.
- [ ] **Step 4: Verify.** Run all tests and `git diff --check`, verify no external writes/network calls.
- [ ] **Step 5: Commit.** Commit templates, validator, fixtures, tests.

### Task 3: Idea generator skill

**Files:** Create `.agents/skills/dzen-idea-generator/SKILL.md` and skill test scenarios in `tests/skill-scenarios/idea-generator.md`.

**Interfaces:** Output ranked idea cards with title, rubric, central question, novelty check, needed sources, visual concept, confidence and duplicate warning.

- [ ] **Step 1: Red.** Exercise an identical-topic and a sensational-claim baseline without the skill; record failures.
- [ ] **Step 2: Green.** Write minimal skill with triggering frontmatter and outputs.
- [ ] **Step 3: Verify.** Re-run scenarios with the skill, validate frontmatter, then commit.

### Task 4: Research skill

**Files:** Create `.agents/skills/dzen-research/SKILL.md`, `tests/skill-scenarios/research.md`.

**Interfaces:** Source register + claim ledger; source classification and epistemic status for disputed/unsourced claims. `BLOCKED` when central facts cannot be verified.

- [ ] **Step 1: Red.** Baseline with inaccessible source, conflicting timelines and fabricated quotation pressure.
- [ ] **Step 2: Green.** Implement read-the-source rules, claim linking and blocked output.
- [ ] **Step 3: Verify.** Pressure-test, validate frontmatter, commit.

### Task 5: Fully automatic writer skill

**Files:** Create `.agents/skills/dzen-writer/SKILL.md`, `tests/skill-scenarios/writer.md`.

**Interfaces:** Consumes verified brief and claim ledger. Produces a **complete** original, readable article in Russian; no human-written starting text required. Marks unsourced flourishes as suspect; does not insert fabricated eyewitness memories or quotes.

- [ ] **Step 1: Red.** Test lack of author notes, sparse claims and pressure to invent personal recollections.
- [ ] **Step 2: Green.** Author skill, explicitly ensure it never blocks solely because no human draft exists.
- [ ] **Step 3: Verify.** Pressure-test readable article generation and provenance, validate frontmatter, commit.

### Task 6: Anti-slop skill

**Files:** Create `.agents/skills/dzen-anti-slop/SKILL.md`, `tests/skill-scenarios/anti-slop.md`.

**Interfaces:** Produces rewritten `draft.md` and an evidence-backed change log; no superficial keyword substitution or AI-detector evasion.

- [ ] **Step 1: Red.** Test repetitive but keyword-clean prose and factual but dry prose.
- [ ] **Step 2: Green.** Implement a content-first editing rubric and bounded automatic revision cycle.
- [ ] **Step 3: Verify.** Re-test, validate frontmatter, commit.

### Task 7: Image creator and image truthfulness

**Files:** Create `.agents/skills/dzen-image-creator/SKILL.md`, `tests/skill-scenarios/images.md`.

**Interfaces:** Generate actual image assets when tool available; emit provenance, caption, historical-detail checks and credit/rights status. Do not conflate prompt file with image file.

- [ ] **Step 1: Red.** Test unavailable image tool and photorealistic false archival-document scenario.
- [ ] **Step 2: Green.** Write creation/inspection/caption contract, preserve true tool failure.
- [ ] **Step 3: Verify.** Validate image metadata and real presence; pressure-test and commit.

### Task 8: Editor and publishing package

**Files:** Create `.agents/skills/dzen-editor/SKILL.md`, `.agents/skills/dzen-publishing/SKILL.md`, `tests/skill-scenarios/editor.md`, `tests/skill-scenarios/publishing.md`.

**Interfaces:** Editor issues machine-readable gates and bounded rework directions; publisher packages only when validator passes. Both carry platform warning and fully-AI provenance. Does not publish anywhere.

- [ ] **Step 1: Red.** Test contradictions and source uncertainty, then pressure to auto-publish or omit AI provenance.
- [ ] **Step 2: Green.** Write and verify editor skill first; commit it before beginning publisher.
- [ ] **Step 3: Red/green publisher.** Test packaging-only boundary without publisher skill; write it, re-test, validate frontmatter, commit.
- [ ] **Step 4: Verify.** Run all contract and skill scenarios; `git diff --check`.

### Task 9: End-to-end dry run, documentation and PR

**Files:** Create a clearly marked example in `examples/` (not a public article) and record `docs/verification.md`.

**Interfaces:** From one explicit instruction, Codex triggers idea/research/writer/anti-slop/image/editor/package automatically. No manual author step. If real research/image tools unavailable, the pipeline stops with an honest `BLOCKED` outcome and recorded cause; never substitutes imaginary evidence.

- [ ] **Step 1: Execute.** Attempt one pilot topic through all skills with real research and image tools when available.
- [ ] **Step 2: Verify.** Record actual tool invocations, concrete artifact paths, validator and style results, and any gates not run. Do not claim PASS unless observed.
- [ ] **Step 3: Run.** `python3 -m unittest discover -s tests -v`, `python3 scripts/validate_package.py <example-if-packaged>`, `git diff --check`.
- [ ] **Step 4: Inspect.** Review 7 skill trigger descriptions, references, no duplicate rules, and zero external Dzen writes.
- [ ] **Step 5: Create PR.** Commit all tested changes in a dedicated branch; report PR and evidence without merging unless separately authorized.

## Acceptance criteria

- All seven project-local `SKILL.md` files are discoverable and individually pressure-tested.
- A single Codex instruction can initiate full article creation **without** user-authored text or intermediate approval prompts.
- Every retained article has complete source and claim tracking, style and visual checks, and a verifiable manifest.
- Automated results distinguish `PACKAGED` from `BLOCKED` and never pretend tools succeeded.
- All generated packages explicitly disclose fully AI-generated provenance and Dzen policy risk.
- Dzen publication and monetization remain outside automation scope.
- Automated unit tests pass and a real dry run has an evidence-based verdict.
