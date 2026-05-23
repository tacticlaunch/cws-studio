---
name: cws-learn
description: >-
  Persistent per-launch learnings journal — record what worked, what didn't,
  what surprised you, so the next launch starts smarter. Append-only. Use after
  a retro flags a notable finding, after a moderation rejection, after a
  monetization experiment shifts conversion, after you discover a new technique
  / a new SERP pattern / a new acquirer gotcha. Triggers on "remember this",
  "log this learning", "save this insight", "add to learnings", "what did we
  learn from X". Also use to *read* learnings before starting a new launch
  ("show me what we learned from prior launches", "any learnings about FB
  ads"). Inspired by gstack /learn.
---

## Preamble (run first)

Run the standard preamble (see `shared/preamble.md`). It loads `$SLUG`,
branch, prior learnings (filtered by this stage), and `./.cws/state.json`.
Skip the rest of this skill if the preamble exits — the preamble is the
gate.

## AskUserQuestion Format

See `shared/askuserquestion-format.md`. Every interactive decision goes
through `AskUserQuestion` as a `D<N>` decision brief (ELI10 · Stakes ·
Recommendation · Completeness · Pros/cons · Net). D-numbering starts at D1
per invocation.

## Voice

See `shared/voice.md`. Operator voice. No banners. No file-creation dumps.
Concrete numbers, names, paths. Lead with the point.

## Skill Routing Footer

End every invocation with a single `Next: /cws-<skill>` line per
`shared/skill-routing.md`. Never a menu.

---
# CWS Studio — learn

Per-launch learnings journal. Append-only. Tied to `.cws/learnings.md`.
Persistent across all retros and across multiple launches in the same project.

## Two modes

### `append` — record a learning

User says something like: "log this — banner B converted 3× better than A
because…". Or after a retro / challenge / careful event surfaces something
worth remembering.

Write to `./.cws/learnings.md` as a new dated entry:

```markdown
## 2026-05-27 · cws-promote
**Insight:** Banner B (no browser chrome) converted 3× better than A (with
chrome) at the same volume.
**Evidence:** GA4 first_visit→install jumped 6% → 17% in the 4-day swap.
**Action for next launch:** Default to "no browser chrome" on the small
banner. Override only when the browser context IS the product (dark theme).
**Tags:** banner, conversion, behavioral-factors
```

Each entry MUST include: date, stage tag, insight, evidence, future action,
tag list. No insight without evidence; no entry without a future action.

If the learning is project-spanning (applies to all future launches, not
just this one), also emit a memory write via the memory system so it
persists across projects.

### `read` — surface relevant learnings

User says "any learnings about FB ads", "what did we learn from the last
launch", "show banner learnings". Or another skill invokes this internally
("before starting cws-promote on a new project, surface relevant tags").

Read `./.cws/learnings.md` and filter by tag / stage / date. Output a short
list (≤ 5 most relevant entries). If invoked from another skill, return
structured data, not prose.

## What goes in / stays out

**In:**
- Numeric outcomes of experiments (banner A vs B, billing cycle X vs Y).
- Unexpected moderation rejections with the exact cause.
- Acquirer issues encountered (Stripe freeze, Paddle moderation cost).
- New tactics that worked (a keyword construction, a Welcome-Page tweak).
- Hard timelines (how long X actually took vs estimate).
- A SERP / niche-saturation observation that changed a decision.

**Out:**
- Generic methodology (it's in the references).
- Anything without evidence ("I think X works better").
- Anything that belongs in the per-stage artifact, not the journal.

## Cross-launch carry-over

When a launch ends (after `cws-monetize` gate passes OR the project is
shelved), the user can run `cws-learn carryover`. This produces a short
distilled markdown the user can paste into a new project's seed prompt — or,
better, into the memory system at the project-spanning level (`~/.claude/...`)
so the next sprint's skills surface it automatically.

## Integration with other skills

- `cws-sprint` reads the latest 5 learnings on each invocation and shows
  them in the "where am I" summary.
- `cws-challenge` reads learnings tagged by the stage it's challenging —
  catches "we said we'd avoid X next time".
- `cws-retro` may auto-append a learning if a metric flips dramatically
  (with the user's confirmation).

## What learn never does

- Doesn't edit prior entries — append-only. Outdated entries get a new
  entry that supersedes them ("Update on 2026-05-12 entry: …").
- Doesn't surface low-relevance learnings; aggressive filtering keeps the
  signal high.
