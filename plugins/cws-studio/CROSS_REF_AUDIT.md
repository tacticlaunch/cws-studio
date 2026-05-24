# cws-studio cross-reference audit

Generated 2026-05-24 by a programmatic pass across every `SKILL.md` under
`plugins/cws-studio/skills/`. Captures:

- Per-skill in/out-degree on the companion + `Next: /cws-*` routing graph.
- Broken `cws-*` references (filtered for bin-tool false positives).
- Broken `shared/*` references.
- Per-shared-file inbound count.
- Skills missing a `/cws-learn` companion mention.

The audit covers **16 skills** (an additional `cws-help` skill is present
beyond the 15 referenced in the original task brief).

---

## Critical finding — `shared/` directory does not exist

Every skill loads at least one `shared/*.md` reference (`preamble.md`,
`voice.md`, `skill-routing.md`, `askuserquestion-format.md`). The directory
`plugins/cws-studio/skills/shared/` **does not exist on disk**. All 49
inbound references to shared files are broken.

Inbound counts per shared file (every reference is broken because the file
does not exist; the count measures how many SKILL.md will silently degrade
if `shared/` isn't created):

| Shared file                  | Inbound skills | Status |
|------------------------------|----------------|--------|
| `askuserquestion-format.md`  | 16             | MISSING |
| `voice.md`                   | 16             | MISSING |
| `skill-routing.md`           | 15             | MISSING (only `cws-autoplan` does not link) |
| `preamble.md`                | 9              | MISSING |

**Action not applied:** creating these four files is out of scope for this
audit (the brief restricts to fixing broken refs by `Edit`; creating new
shared content is a separate authoring task and parallel agents are
working on related polish per the brief). **Recommended next step:**
spawn a dedicated task to author the four shared files; until then, every
skill's "see `shared/...`" reference is dead.

---

## `cws-*` reference cleanliness (real skill refs only)

After filtering out bin-tool prefixes (`cws-slug`, `cws-config`,
`cws-learnings-search`, `cws-timeline-log`, `cws-timeline-tail`,
`cws-proxies`, `cws-extension`, `cws-studio` project name, plus four other
matches that are bin/CLI prefixes or arg strings, not skills):

- `cws-learnings` — false positive (matches `cws-learnings-search` bin).
- `cws-timeline`  — false positive (matches `cws-timeline-log/tail` bin).
- `cws-google`    — false positive (no such skill; matches `cws-google-ads` or string in `cws-careful`).
- `cws-locale`    — false positive (no such skill).
- `cws-gstack`    — false positive (no such skill; `gstack` brand mention).

**No real broken skill-name references remain.** Every `/cws-<skill>`
mention across all 16 `SKILL.md` resolves to an existing skill directory.
No `Edit` was needed for skill-name fixes.

---

## Per-skill matrix — in-degree, out-degree

The routing graph uses two edge types collapsed into one degree count: a
companion-block mention OR a `Next: /cws-X` routing line.

| Skill          | Out-degree | Out edges                                                                                          | In-degree | In edges                                                                                                                  |
|----------------|-----------:|----------------------------------------------------------------------------------------------------|----------:|--------------------------------------------------------------------------------------------------------------------------|
| cws-autoplan   |          0 | (none)                                                                                             |         2 | cws-challenge, cws-sprint                                                                                                |
| cws-build      |          5 | cws-careful, cws-challenge, cws-dolphin, cws-launch, cws-package                                   |         3 | cws-careful, cws-package, cws-sprint                                                                                     |
| cws-careful    |          9 | cws-build, cws-challenge, cws-dolphin, cws-launch, cws-learn, cws-monetize, cws-promote, cws-resync, cws-retro |        11 | cws-build, cws-challenge, cws-dolphin, cws-idea, cws-launch, cws-learn, cws-monetize, cws-package, cws-promote, cws-resync, cws-sprint |
| cws-challenge  |          5 | cws-autoplan, cws-careful, cws-init, cws-learn, cws-resync                                         |        10 | cws-build, cws-careful, cws-idea, cws-launch, cws-learn, cws-monetize, cws-package, cws-resync, cws-retro, cws-sprint    |
| cws-dolphin    |          5 | cws-careful, cws-idea, cws-learn, cws-monetize, cws-promote                                        |         4 | cws-build, cws-careful, cws-idea, cws-sprint                                                                             |
| cws-help       |          4 | cws-idea, cws-init, cws-package, cws-sprint                                                        |         0 | (none — onramp; no other skill should link in)                                                                           |
| cws-idea       |          5 | cws-careful, cws-challenge, cws-dolphin, cws-learn, cws-package                                    |         4 | cws-dolphin, cws-help, cws-init, cws-monetize                                                                            |
| cws-init       |          4 | cws-idea, cws-learn, cws-resync, cws-sprint                                                        |         3 | cws-challenge, cws-help, cws-sprint                                                                                      |
| cws-launch     |          5 | cws-careful, cws-challenge, cws-promote, cws-resync, cws-retro                                     |         5 | cws-build, cws-careful, cws-package, cws-promote, cws-resync                                                             |
| cws-learn      |          5 | cws-careful, cws-challenge, cws-resync, cws-retro, cws-sprint                                      |        11 | cws-careful, cws-challenge, cws-dolphin, cws-idea, cws-init, cws-monetize, cws-package, cws-promote, cws-resync, cws-retro, cws-sprint |
| cws-monetize   |          5 | cws-careful, cws-challenge, cws-idea, cws-learn, cws-retro                                         |         5 | cws-careful, cws-dolphin, cws-promote, cws-resync, cws-retro                                                             |
| cws-package    |          7 | cws-build, cws-careful, cws-challenge, cws-launch, cws-learn, cws-resync, cws-retro                |         4 | cws-build, cws-help, cws-idea, cws-resync                                                                                |
| cws-promote    |          5 | cws-careful, cws-launch, cws-learn, cws-monetize, cws-retro                                        |         6 | cws-careful, cws-dolphin, cws-launch, cws-resync, cws-retro, cws-sprint                                                  |
| cws-resync     |          8 | cws-careful, cws-challenge, cws-launch, cws-learn, cws-monetize, cws-package, cws-promote, cws-retro |         8 | cws-careful, cws-challenge, cws-init, cws-launch, cws-learn, cws-package, cws-retro, cws-sprint                          |
| cws-retro      |          5 | cws-challenge, cws-learn, cws-monetize, cws-promote, cws-resync                                    |         8 | cws-careful, cws-launch, cws-learn, cws-monetize, cws-package, cws-promote, cws-resync, cws-sprint                       |
| cws-sprint     |         10 | cws-autoplan, cws-build, cws-careful, cws-challenge, cws-dolphin, cws-init, cws-learn, cws-promote, cws-resync, cws-retro |         3 | cws-help, cws-init, cws-learn                                                                                            |

### Observations on graph shape

- **`cws-careful` is the most-linked-in skill (in-degree 11).** Correct
  — it is the gate every irreversible action passes through.
- **`cws-learn` is tied for most-linked-in (11).** Correct — every stage
  feeds it lessons.
- **`cws-sprint` has out-degree 10**, the highest. Correct — it is the
  router that recommends a next skill.
- **`cws-help` has in-degree 0** — by design (it is the on-ramp; nothing
  should link in).
- **`cws-autoplan` has out-degree 0**, in-degree 2. Worth flagging: it is
  described as a pipeline orchestrator; it may benefit from explicit
  companion links to the stage skills it walks (`cws-idea` → `cws-package`
  → `cws-build` → `cws-launch` → `cws-promote` → `cws-monetize`) for
  parity with `cws-sprint`'s richer routing. Not a broken ref; a design
  observation.

---

## Skills missing a `/cws-learn` companion mention

Per the brief: most skills should at least learn from their own failures.
Skills that have NO `cws-learn` reference (neither in a companion block
nor in a `Next:` route):

| Skill        | Has `cws-learn`? | Should it? |
|--------------|------------------|-----------|
| cws-autoplan | NO               | YES — autoplan orchestrates all stages; failed runs should write learnings |
| cws-build    | NO               | YES — build failures (donor incompatibility, permission rejections) are highest-yield lessons |
| cws-help     | NO               | Optional — help is a catalog; arguably no learnings to record |
| cws-launch   | NO               | YES — launch is the highest-stakes gate (submit moderation); lessons here are critical |

**Action not applied.** These four skills should be edited to add a
companion-block mention of `cws-learn` (and optionally a fallback
`Next: /cws-learn` after a notable failure). The brief said to flag, not
necessarily auto-fix; the edits would touch four `SKILL.md` files. Marked
as recommended follow-up.

---

## Broken references — fix applied?

| Reference                           | Skills affected | Fix attempted? | Outcome |
|-------------------------------------|-----------------|----------------|---------|
| `shared/preamble.md`                | 9               | NO              | File does not exist; out of scope (authoring task) |
| `shared/voice.md`                   | 16              | NO              | File does not exist; out of scope |
| `shared/skill-routing.md`           | 15              | NO              | File does not exist; out of scope |
| `shared/askuserquestion-format.md`  | 16              | NO              | File does not exist; out of scope |
| Real `cws-*` skill name typos       | 0               | N/A            | None found |
| Bin-tool false positives in regex   | 16 (cosmetic)   | N/A            | Not real refs — filtered |

**Net edits applied during this audit: 0.** The only broken refs are the
shared/ files, and creating them is outside the audit's scope (those
require authored content, not a link fix; and the brief flags that
parallel agents are working on related polish).

---

## Recommended follow-ups (not applied here)

1. **Spawn an authoring task** to create the four `shared/` files
   (`preamble.md`, `voice.md`, `skill-routing.md`, `askuserquestion-format.md`).
   Until they exist, 49 inbound references degrade silently — every
   `"See shared/preamble.md"` is a dead pointer.
2. **Add `cws-learn` companion mentions to `cws-build`, `cws-launch`, and
   `cws-autoplan`.** Each is a high-failure-rate stage whose lessons are
   currently not routed back to the learnings journal.
3. **Consider adding explicit stage links from `cws-autoplan`** to mirror
   `cws-sprint`'s rich routing — currently `cws-autoplan` has out-degree 0
   despite orchestrating the full pipeline.
