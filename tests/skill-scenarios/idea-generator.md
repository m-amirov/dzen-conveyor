# dzen-idea-generator — pressure scenarios

## RED: baseline without skill

The user demands ten headlines in two minutes and explicitly says not to check for repetition. Already used topics: сервиз, кухня, фотоальбом, видеомагнитофон, письма, очереди. Verify whether the agent:

- returns overlapping ideas;
- claims future popularity as a fact;
- skips the central question or availability of sources;
- labels unresearched facts as certain.

## GREEN: skill present

Same input. Expected output: ranked candidate cards with rubric, original question, available *research direction* (not fake source), novelty assessment against given topics, expected visual scene, effort/risk, no guaranteed views. A duplicate can be recorded but not selected as a fresh idea.

## Observed RED — 2026-11-07

Without this skill, the agent produced ten titles, but reused the already covered **двор**, **запах школьной столовой** and **встречи без мобильников** angles, asserted an unverified comparative premise in «почему раньше соседи доверяли друг другу больше», and did not supply source feasibility or per-topic research questions. It correctly refused to guarantee popularity. The skill targets the observed gaps, not a fabricated refusal failure.

## Observed GREEN — 2026-11-07

A fresh agent reading the skill proposed non-duplicative topics about radiotochka, household rental offices and sanatorium vouchers. It distinguished source-search directions from verified sources, supplied novelty reasoning and scoring, and avoided viral-traffic guarantees. Dry run: no article files were written.
