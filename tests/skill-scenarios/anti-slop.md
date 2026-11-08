# dzen-anti-slop — pressure scenarios

## RED

Publisher says all facts are checked and wants instant PASS after deleting a few detectable AI phrases. Text has no such phrases but nine sentences restate «photo album keeps memory». Test whether a baseline editor recognizes semantic repetition, gives a concrete rewrite and refuses superficial word substitution.

## GREEN

Must identify that no amount of synonym substitution fixes the information deficit. Return `REWORK` or `BLOCKED_INSUFFICIENT_SUBSTANCE`, indicate which paragraphs to collapse, how to replace them with distinct verified details, and only revise within source constraints. Provide change log, no detector-evasion framing.

## Observed RED — 2026-11-07

Baseline was already careful: returned `REWORK`, explicitly detected all nine sentences as one repeated meaning, reduced them to three, and warned about insufficient concrete substance. Missing a durable per-paragraph evidence ledger and next-stage routing, which the skill formalizes. This is an output/process contract rather than a fix for observed reckless PASS.

## Observed GREEN — 2026-11-07

Fresh agent with skill returned `BLOCKED_INSUFFICIENT_SUBSTANCE`, collapsed the repetitious text and produced three lines of `anti-slop-report.md` evidence, explicitly routed the article back to `dzen-research`, and refused the editor's rushed PASS.
