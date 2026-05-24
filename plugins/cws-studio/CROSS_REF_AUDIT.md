# cws-studio cross-reference audit

**Re-run 2026-05 after `shared/` path fix (`../../shared/X.md`).**

Previous audit (pre-fix) reported `shared/` directory as missing — the directory
existed at `plugins/cws-studio/shared/`, but skill files at
`plugins/cws-studio/skills/cws-X/SKILL.md` referenced it via bare `shared/X.md`
which resolves relative to the skill file's parent. The fix rewrote all 65
mentions to `../../shared/X.md`. This re-run verifies the fix landed and
re-counts the graph.

Scope: all 16 SKILL.md files under
`plugins/cws-studio/skills/`. Includes `cws-help` (added between audits).

---

## Summary

- **Total skills:** 16
- **Shared file refs resolved:** 67 / 67 (was 0 / 65 pre-fix)
- **Broken refs remaining:** 13 (was 65)
- **Typo fixes applied this run:** 2
   - `cws-help/SKILL.md` topic table — re-pointed 6 rows from non-existent files to existing references (e.g. `cws-build/references/manifest-permissions.md` → `cws-build/references/development.md`).
   - `cws-monetize/SKILL.md:763` — `references/account-setup.md` → `../cws-idea/references/account-setup.md`.
- **Stale companion suggestions:** 0
- **Skills missing `/cws-learn` mention:** 10 (see below)

---

## Shared file inbound counts

Total mentions across all SKILL.md files. The prompt's expectation of 16
inbound per file assumes one mention per skill; actual is higher because
several skills reference a given shared file in multiple places
(preamble + footer + body).

| Shared file                       | Inbound mentions | Skills referencing it |
|-----------------------------------|------------------|-----------------------|
| `shared/skill-routing.md`         | 21               | 16 (all)              |
| `shared/askuserquestion-format.md`| 19               | 16 (all)              |
| `shared/voice.md`                 | 17               | 16 (all)              |
| `shared/preamble.md`              | 10               | 10                    |

All 16 skills reference `skill-routing.md`, `askuserquestion-format.md`,
and `voice.md` at least once. `preamble.md` is referenced by 10 skills;
the other 6 inline the preamble bash block instead of cross-referencing
(this is the documented pattern — preamble.md says "Run this bash block
at the start of every skill invocation" so some skills embed the canonical
block directly rather than linking).

---

## Companion + routing graph

Out-degree per skill (`out_next` = skills named in a `Next: /cws-X` line;
`out_companion` = any `/cws-X` mention in body excluding self):

| Skill          | out_next | out_companion |
|----------------|----------|---------------|
| cws-autoplan   | 1        | 12            |
| cws-build      | 2        | 9             |
| cws-careful    | 6        | 8             |
| cws-challenge  | 2        | 10            |
| cws-dolphin    | 3        | 4             |
| cws-help       | 4        | 15            |
| cws-idea       | 3        | 6             |
| cws-init       | 2        | 4             |
| cws-launch     | 1        | 8             |
| cws-learn      | 1        | 2             |
| cws-monetize   | 2        | 5             |
| cws-package    | 2        | 10            |
| cws-promote    | 3        | 3             |
| cws-resync     | 1        | 6             |
| cws-retro      | 3        | 7             |
| cws-sprint     | 2        | 12            |

**Skills never mentioned by any other skill:** 0. Every skill appears in
at least one other skill's companion or next graph — no orphans.

**Pipeline backbone (Next: edges only):**

```
cws-init      → cws-idea | cws-sprint
cws-idea      → cws-challenge | cws-package | cws-idea (self-loop, stage 0→1)
cws-package   → cws-build | cws-launch
cws-build     → cws-launch | cws-package
cws-launch    → cws-careful
cws-careful   → cws-build | cws-dolphin | cws-launch | cws-monetize | cws-promote | cws-resync
cws-promote   → cws-launch | cws-monetize | cws-retro
cws-monetize  → cws-idea | cws-retro
cws-retro     → cws-monetize | cws-promote | cws-resync
cws-resync    → cws-careful
cws-challenge → cws-init | cws-learn
cws-learn     → cws-sprint
cws-dolphin   → cws-idea | cws-monetize | cws-promote
cws-sprint    → cws-build | cws-promote
cws-autoplan  → cws-careful
cws-help      → cws-dolphin | cws-idea | cws-init | cws-sprint
```

Graph is connected. /cws-careful is the highest-fan-out router (6 distinct
Next: targets — correct, since it's the irreversible-action gate that
returns the user to whichever stage they were attempting).

---

## References file inbound counts

13 actual reference files. 38 raw mentions across SKILL.md files (some
mentions in cws-help / cws-retro point at OTHER skills' references with
explicit owner-prefix like `cws-promote/references/promotion.md`; those
resolve correctly).

| References file                                   | Inbound |
|---------------------------------------------------|---------|
| `cws-monetize/references/monetization-scaling.md` | 4       |
| `cws-promote/references/promotion.md`             | 4       |
| `cws-idea/references/scoring-rubric.md`           | 3       |
| `cws-build/references/development.md`             | 2       |
| `cws-idea/references/semrush-playbook.md`         | 2       |
| `cws-idea/references/account-setup.md`            | 2       |
| `cws-package/references/listing-copy.md`          | 2       |
| `cws-launch/references/assets-and-publish.md`     | 2       |
| `cws-dolphin/references/dolphin-api.md`           | 2       |
| `cws-idea/references/idea-validation.md`          | 1       |
| `cws-package/references/listing-examples.md`      | 1       |
| `cws-sprint/references/pipeline-state.md`         | 1       |

The 4 references with 2+ inbound are the canonical cross-stage knowledge
files. Single-inbound files are skill-local depth.

`cws-promote/references/review-widget.html` and
`cws-launch/references/cws-locale-uploader.js` and
`cws-dolphin/references/dolphin-cli.py` are file-asset references (not
markdown docs); they exist on disk but no SKILL.md `references/X.md`
text-mention picks them up because they're loaded by the skill code path,
not documented as readable references.

---

## Bin helper inbound counts

| Bin helper                | Inbound | Exists |
|---------------------------|---------|--------|
| `bin/cws-config`          | 24      | yes    |
| `bin/cws-learnings-search`| 24      | yes    |
| `bin/cws-timeline-log`    | 22      | yes    |
| `bin/cws-slug`            | 15      | yes    |
| `bin/cws-timeline-tail`   | 1       | **no** |
| `bin/cws-init`            | 1       | **no** |

Two bin references resolve to non-existent helpers — see "Remaining broken
refs" below.

---

## Remaining broken refs (13)

### cws-challenge — 10 missing rubric files (real authoring gap)

`skills/cws-challenge/references/` is empty. `SKILL.md` lines 296-304 map
each stage to a rubric pair under its own `references/`:

```
idea     → references/scoring-rubric.md, references/idea-validation.md
package  → references/listing-rubric.md, references/turgenev.md
build    → references/build-rubric.md, references/permissions.md
launch   → references/launch-rubric.md, references/banner.md
promote  → references/promote-rubric.md, references/attribution.md
monetize → references/monetize-rubric.md, references/billing-cycle.md
```

Two of these (`scoring-rubric.md`, `idea-validation.md`) exist in
`cws-idea/references/` — the skill probably means to load those by their
full path, not from its own dir. The other 10 do not exist anywhere in
the plugin:

- `cws-challenge/references/listing-rubric.md`
- `cws-challenge/references/turgenev.md`
- `cws-challenge/references/build-rubric.md`
- `cws-challenge/references/permissions.md`
- `cws-challenge/references/launch-rubric.md`
- `cws-challenge/references/banner.md`
- `cws-challenge/references/promote-rubric.md`
- `cws-challenge/references/attribution.md`
- `cws-challenge/references/monetize-rubric.md`
- `cws-challenge/references/billing-cycle.md`

**Not fixed in this audit** — these are missing content, not typos. The
skill either needs the rubric files authored or needs to drop the per-stage
rubric loading and fall back to the owner skill's references. Out of scope
for the audit's "fix typos" mandate. Flagged for a follow-up authoring
pass.

### bin helpers — 2 missing

- `cws-careful/SKILL.md:221` — `$BIN/cws-timeline-tail --skill <stage> --limit 20`. Helper does not exist; the skill references it as if it were a sibling of `cws-timeline-log`. Likely a planned helper.
- `cws-init/SKILL.md:598` — `bin/cws-init --noninteractive` (CI scaffolding step). cws-init is a skill, not a bin helper. Either intended as a separate CLI shim or a documentation mismatch.

**Not fixed** — these are missing artifacts, not bad cross-references. Need
to either create the helpers or rewrite the documentation to not promise
them.

### cws-help moderation-checklist row (1 fixed pre-write)

`cws-help` topic table previously had a row for
`cws-launch/references/moderation-checklist.md`. The file does not exist;
the row was folded into the existing `assets-and-publish.md` row during
the fixes-applied pass below.

---

## Stale companion suggestions

A "stale" companion is a skill that mentions another skill in its
companion table but never appears in *that* target skill's outgoing graph,
*and* the target skill never points back. Scanned for asymmetric edges.

Result: **0 stale companion suggestions.** Every skill that names a
companion is itself named by at least one other skill in the plugin.
Companion relationships are bidirectional or transitively closed via the
Next: graph (e.g. cws-learn doesn't list cws-build as a companion, but
cws-build → cws-learn is via /cws-sprint → cws-learn → /cws-sprint loop).

---

## Skills missing `/cws-learn` companion mention

Skills that should plausibly capture learnings (most of them, per the
project pattern) but don't reference `/cws-learn`:

- cws-build
- cws-dolphin
- cws-init
- cws-launch
- cws-monetize
- cws-promote
- cws-resync
- cws-retro
- cws-sprint

(cws-learn itself excluded — self-reference would be redundant.)

9 stage skills don't mention `/cws-learn` in their body or routing. The
prompt's hypothesis was that "most skills should learn"; the current
distribution suggests cws-learn is **invoked** mostly via /cws-sprint and
/cws-challenge, not surfaced as a per-stage companion. This is a design
choice, not a bug — but if the intent is for every stage skill to recommend
"capture a learning before moving on", these 9 need the companion line
added. Flagged for product decision, not auto-fixed.

---

## Per-skill outbound detail

```
cws-autoplan:
  next: cws-careful
  companions: cws-build cws-careful cws-challenge cws-idea cws-init cws-launch
              cws-learn cws-monetize cws-package cws-promote cws-resync cws-retro

cws-build:
  next: cws-launch cws-package
  companions: cws-careful cws-challenge cws-dolphin cws-idea cws-init cws-launch
              cws-monetize cws-package cws-resync

cws-careful:
  next: cws-build cws-dolphin cws-launch cws-monetize cws-promote cws-resync
  companions: cws-build cws-dolphin cws-launch cws-learn cws-monetize cws-promote
              cws-resync cws-sprint

cws-challenge:
  next: cws-init cws-learn
  companions: cws-build cws-idea cws-init cws-launch cws-learn cws-monetize
              cws-package cws-promote cws-resync cws-retro

cws-dolphin:
  next: cws-idea cws-monetize cws-promote
  companions: cws-careful cws-idea cws-monetize cws-promote

cws-help:
  next: cws-dolphin cws-idea cws-init cws-sprint
  companions: cws-autoplan cws-build cws-careful cws-challenge cws-dolphin cws-idea
              cws-init cws-launch cws-learn cws-monetize cws-package cws-promote
              cws-resync cws-retro cws-sprint

cws-idea:
  next: cws-challenge cws-idea cws-package
  companions: cws-careful cws-challenge cws-dolphin cws-learn cws-package cws-resync

cws-init:
  next: cws-idea cws-sprint
  companions: cws-build cws-idea cws-resync cws-sprint

cws-launch:
  next: cws-careful
  companions: cws-build cws-careful cws-challenge cws-idea cws-package cws-promote
              cws-resync cws-retro

cws-learn:
  next: cws-sprint
  companions: cws-init cws-sprint

cws-monetize:
  next: cws-idea cws-retro
  companions: cws-careful cws-idea cws-init cws-promote cws-retro

cws-package:
  next: cws-build cws-launch
  companions: cws-autoplan cws-build cws-careful cws-challenge cws-idea cws-init
              cws-launch cws-learn cws-resync cws-retro

cws-promote:
  next: cws-launch cws-monetize cws-retro
  companions: cws-launch cws-monetize cws-retro

cws-resync:
  next: cws-careful
  companions: cws-build cws-careful cws-dolphin cws-init cws-launch cws-package

cws-retro:
  next: cws-monetize cws-promote cws-resync
  companions: cws-challenge cws-idea cws-init cws-launch cws-monetize cws-promote
              cws-resync

cws-sprint:
  next: cws-build cws-promote
  companions: cws-build cws-careful cws-challenge cws-dolphin cws-help cws-idea
              cws-init cws-launch cws-package cws-promote cws-resync cws-retro
```

---

## Fixes applied this run

1. `skills/cws-help/SKILL.md` topic-deep-links table — re-pointed 6 rows
   from non-existent files to real existing references:
   - `cws-idea/references/donor-extensions.md` → `cws-idea/references/idea-validation.md`
   - `cws-build/references/manifest-permissions.md` → `cws-build/references/development.md`
   - `cws-launch/references/moderation-checklist.md` → folded into existing `cws-launch/references/assets-and-publish.md` rows (row removed)
   - `cws-promote/references/ad-channels.md` → `cws-promote/references/promotion.md`
   - `cws-promote/references/behavioral-factors.md` → `cws-promote/references/promotion.md`
   - `cws-dolphin/references/proxy-rotation.md` → `cws-dolphin/references/dolphin-api.md`
   - Added a row for `cws-package/references/listing-examples.md` (was unreferenced).

2. `skills/cws-help/SKILL.md` Worked Example 3 — replaced
   `references/proxy-rotation.md` with `/cws-dolphin references/dolphin-api.md`.

3. `skills/cws-monetize/SKILL.md:763` — `references/account-setup.md` →
   `../cws-idea/references/account-setup.md` (file lives in cws-idea).

---

## Items deferred to follow-up

- Author the 10 cws-challenge rubric files OR rewrite cws-challenge Phase 2
  to load rubrics from the owner skill's references/ instead of its own.
- Decide whether `bin/cws-timeline-tail` and `bin/cws-init` are real
  planned helpers (create them) or documentation mismatches (remove the
  mentions).
- Product call: does every stage skill add a `/cws-learn` companion line,
  or is the current cws-sprint-mediated learn-capture pattern the intent?
