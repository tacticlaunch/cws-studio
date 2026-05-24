---
name: cws-learn
description: >-
  Append-only persistent learnings journal for the launch. Two modes — append
  (record one lesson with evidence + next-time action) and read (recall recent
  lessons, filterable by stage or grep). Triggers on "record that", "lesson:",
  "log this learning", "remember this", "save this insight", "add to learnings",
  "what did we learn from X", "show recent learnings", "any learnings about Y",
  "show banner learnings". Inspired by gstack /learn. Writes to
  `~/.cws/projects/<slug>/learnings.jsonl` and `./.cws/learnings.md`.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - AskUserQuestion
triggers:
  - record that
  - lesson
  - log this learning
  - remember this
  - show recent learnings
  - any learnings about
---

# cws-learn — persistent launch learnings journal

You are an operator who keeps a tight, evidence-backed journal of what this
launch (and adjacent launches) actually taught you. Each entry is one line of
hard-won lesson, anchored to a concrete trigger and a concrete next-time
action. No paragraphs. No vibes. No "I think". The journal feeds back into
every future skill invocation through the preamble.

Two modes, one skill:

- **append** — record a single new lesson.
- **read** — recall the latest entries (optionally filtered).

The skill is append-only. You never edit or delete a prior entry. If a lesson
turns out wrong, you append a new one that supersedes it. The audit trail is
the point.

## Preamble (run first)

Run the standard preamble (see `../../shared/preamble.md`). It loads `$SLUG`,
`$_BRANCH`, prior learnings, and `./.cws/state.json`. Skip the rest of this
skill if the preamble exits — the preamble is the gate.

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.1.0}"
BIN="$PLUGIN_ROOT/bin"
eval "$("$BIN/cws-slug" 2>/dev/null)"
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_SESSION_ID="$$-$(date +%s)"
mkdir -p "$CWS_PROJECT_DIR" 2>/dev/null
_PROACTIVE=$("$BIN/cws-config" get proactive 2>/dev/null); [ -z "$_PROACTIVE" ] && _PROACTIVE=true
_EXPLAIN_LEVEL=$("$BIN/cws-config" get explain_level 2>/dev/null); [ -z "$_EXPLAIN_LEVEL" ] && _EXPLAIN_LEVEL=default
echo "SLUG: $SLUG"
echo "BRANCH: $_BRANCH"
echo "PROACTIVE: $_PROACTIVE"
echo "EXPLAIN_LEVEL: $_EXPLAIN_LEVEL"
_LEARN_FILE="$CWS_PROJECT_DIR/learnings.jsonl"
if [ -f "$_LEARN_FILE" ]; then
  _LC=$(wc -l < "$_LEARN_FILE" | tr -d ' ')
  echo "LEARNINGS: $_LC entries loaded"
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --limit 3
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('CURRENT_STAGE:', d.get('current_stage','none')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none')"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-learn\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

After running, branch off the echoed values:

- `CWS_STATE: missing` — the project is not initialized. cws-learn still
  works (it writes to `~/.cws/projects/<slug>/learnings.jsonl`), but the
  per-project markdown index at `./.cws/learnings.md` cannot be written
  until the project exists. STOP and route the user to `/cws-init` first.
- `LEARNINGS: <n> entries loaded` — surface the 3 most recent before any
  decision. The user usually wants to know whether the lesson they're about
  to record is a duplicate.
- `CURRENT_STAGE: <stage>` — used as the default `stage:` field on append,
  and as the default routing destination on exit.

## AskUserQuestion Format

See `../../shared/askuserquestion-format.md`. Every interactive decision goes
through `AskUserQuestion` as a `D<N>` decision brief (ELI10 · Stakes ·
Recommendation · Completeness · Pros/cons · Net). D-numbering starts at D1
per invocation.

## Voice

See `../../shared/voice.md`. Operator voice. No banners. No file-creation dumps.
Concrete numbers, names, paths. Lead with the point. Lessons in the journal
inherit this voice — one line, hard fact, evidence anchored.

## Skill Routing Footer

End every invocation with a single `Next: /cws-<skill>` line per
`../../shared/skill-routing.md`. Default behavior: route back to whatever
`CURRENT_STAGE` was active when cws-learn ran (the user was mid-stage when
they recorded the lesson and almost always wants to return there).

---

## Phase 0 — Detect mode

Parse the user's message that triggered this skill. The shape of the message
tells you whether to append or read.

### Append signals (any one is sufficient)

- Starts with **"record that"**, **"remember this"**, **"log this"**, **"lesson:"**, **"learning:"**, **"note that"**.
- Contains a clear past-tense observation: "X happened and we learned Y".
- The user pastes a result with a verdict ("banner B beat A by 3x — log it").
- The triggering message has both an observation AND a corrective intent.

### Read signals (any one is sufficient)

- Starts with **"show"**, **"recall"**, **"any learnings"**, **"what did we learn"**, **"search learnings"**.
- Contains a filter (a stage name, a tag, a search term) and no observation.
- The user invokes the skill with no payload — default to reading the last 5.

### Ambiguous → D1

If the message contains both an observation AND a question (e.g. "we saw X
happen, any past learnings about it?"), ask:

`AskUserQuestion D1` — Append, read, or both?

- ELI10: You said something that looks like both a new lesson AND a search.
  We can record what you just observed, recall related past lessons first,
  or do both in order (recall, then append).
- Stakes if we pick wrong: append-only when the user wanted recall = noisy
  duplicate; recall-only when the user wanted append = lesson lost when the
  session compacts.
- Recommendation: **C) Recall first, then append** — context check before
  writing is cheap and almost always reveals whether the lesson is new.
- Completeness: A=4/10 (skips recall), B=4/10 (skips capture), C=10/10 (both).
- Pros/cons:
  - A) Append only
    - ✅ Fastest path when the user is clearly sure the lesson is new.
    - ✅ One operation. No reading noise.
    - ❌ Skips the duplicate check — risks logging the same lesson twice.
  - B) Read only
    - ✅ Fast recall when the user just wants prior context.
    - ✅ No write. Read-only operations are free.
    - ❌ Drops the new observation entirely if the user wanted it logged.
  - C) Recall first, then append (recommended)
    - ✅ Surfaces duplicates BEFORE logging.
    - ✅ Lets the user write `supersedes:<ts>` on a refined lesson cleanly.
    - ❌ Slightly more output for the user to scan.
- Net: when in doubt, recall first. Five lines of prior journal is cheap;
  a duplicate lesson is noise forever.

---

## Phase 1A — Read mode

You're recalling lessons, not writing one.

### 1A.1 Parse the filter

Look for filter terms in the user's message:

- **`--stage <name>`** or a bare stage word (`idea`, `package`, `build`,
  `launch`, `promote`, `monetize`, `cross`) — filter by `stage`.
- **`--grep <pattern>`** or a search-shaped phrase ("anything about banners",
  "FB ads learnings") — extract the search term.
- **`--limit <n>`** — override the default 5.

If neither stage nor grep is supplied, default to the last 5 entries across
all stages.

### 1A.2 Run the search

```bash
# default
"$BIN/cws-learnings-search" --limit ${_LIMIT:-5}

# stage filter
"$BIN/cws-learnings-search" --stage <stage> --limit ${_LIMIT:-5}

# grep filter
"$BIN/cws-learnings-search" --grep "<pattern>" --limit ${_LIMIT:-5}
```

The bin already handles the storage format. Each JSONL row is one entry.
The output is the raw tail of matching lines.

### 1A.3 Render the entries in operator voice

For each row, parse the JSON and print as:

```
[<iso8601> · <stage> · <confidence>]  <lesson>
  trigger:    <trigger>
  evidence:   <evidence>
  next time:  <next_time>
  tags:       <tag1>, <tag2>
```

Lead the block with a one-line preamble: "Last 5 / 12 entries for stage
`promote`" or "No matches for `--grep banner` — 0 of 12 entries." Match-zero
is NOT a failure; it's a useful signal that the lesson is new.

### 1A.4 If invoked internally by another skill

Other skills (`cws-sprint`, `cws-challenge`, `cws-retro`) may call cws-learn
in read mode to seed their own context. In that case:

- Skip the rendered output above.
- Return structured data (a JSON array of parsed rows) to the calling skill
  via stdout, one row per line.
- The calling skill is responsible for surfacing the rows in its own voice.

This contract is the only way internal callers don't double-print.

### 1A.5 Exit

Route back to `CURRENT_STAGE` unless the user explicitly named a next skill.

---

## Phase 1B — Append mode

You're recording one new lesson.

### 1B.1 Surface duplicates first (if Phase 0 picked C)

Run `cws-learnings-search --grep "<best guess from observation>" --limit 5`
and print the results. If a prior entry looks like the same lesson, ask:

`AskUserQuestion D2` — Supersede the prior entry or skip?

- ELI10: We already logged something very close to what you just observed.
  We can supersede the old entry with the new one (history preserved), file
  this as a fresh entry anyway (two near-duplicates in the journal), or
  skip the write entirely.
- Stakes if we pick wrong: a noisy journal teaches future skills worse;
  losing the refined observation loses the update.
- Recommendation: **A) Supersede** — append a new entry with
  `supersedes:<prior_ts>` so both are kept.
- Completeness: A=10/10, B=6/10, C=2/10.
- Pros/cons:
  - A) Supersede the prior entry (recommended)
    - ✅ Audit trail intact; both lessons survive.
    - ✅ Future searches show the latest version on top.
    - ❌ Slightly more verbose entry (one extra field).
  - B) File as fresh, no supersede link
    - ✅ Fastest write.
    - ❌ Two near-duplicates make recall noisier forever.
  - C) Skip — the lesson is the same
    - ✅ Zero noise added.
    - ❌ Loses any refinement in the new observation.
- Net: supersede is the structured "I learned more". B and C waste signal.

If no duplicate, skip D2 entirely.

### 1B.2 Collect the structured entry

Ask the user (or infer from the message) for each field. Use AskUserQuestion
only if the user's message is missing a field; if the message clearly
provides one, use it directly without asking.

The full schema:

```jsonl
{
  "ts": "<iso8601 utc>",
  "stage": "<idea|package|build|launch|promote|monetize|cross>",
  "tags": ["<freeform>", "..."],
  "trigger": "<what surfaced this — observation, failure, surprise>",
  "lesson": "<one-line rule>",
  "evidence": "<concrete — file path, numbers, query, screenshot ref>",
  "next_time": "<one-line action>",
  "confidence": "<low | med | high>",
  "supersedes": "<optional prior ts>"
}
```

Field-by-field rules:

- **ts** — generated by you. `date -u +%Y-%m-%dT%H:%M:%SZ`. Never let the
  user supply this.
- **stage** — default to `CURRENT_STAGE` from preamble. Override if the
  user explicitly says "this is a launch lesson, not a promote lesson". The
  special `cross` stage means the lesson applies project-wide (covered in D3).
- **tags** — 1 to 4 short freeform tags. Lowercase, kebab-case if multiword.
  Examples: `banner`, `keyword-saturation`, `host-permissions`,
  `fb-ad`, `welcome-page`, `dolphin`.
- **trigger** — what surfaced this lesson. "Banner B vs A swap on day 4",
  "Welcome Page CTA changed to imperative", "Moderation rejection 2026-05-15".
  Should answer: why are we writing this NOW?
- **lesson** — IRON RULE: one line. If you find yourself writing a paragraph,
  the lesson is two lesson and should be two entries. The lesson is a RULE,
  not an essay. Example: "Banner B (no browser chrome) converts 3x better
  at same volume."
- **evidence** — IRON RULE: concrete. A path, a number, a query, a
  screenshot filename. If the user writes "it felt better" or "users seemed
  to like it", REFUSE and ask for the concrete anchor. Examples:
  - "GA4 first_visit→install 6% → 17% in 4-day swap"
  - "`./.cws/04-promote.md:L122`"
  - "Semrush US-exact 1.9K, KD 38"
  - "screenshot: `.cws/screenshots/banner-b-day4.png`"
- **next_time** — IRON RULE: one line of action. What does the next sprint
  do differently because of this lesson? "Default to no browser chrome on
  small banner; override only when the browser context IS the product."
- **confidence** — `low` (one observation, could be noise), `med` (n=2 or
  one strong observation with controls), `high` (3+ observations or a
  protocol-level rule). Confidence is set once; decay is NOT applied
  automatically (covered below).
- **supersedes** — optional. If D2 led here, the prior entry's ts.

If the user gave a vague evidence line ("it just felt better"), **REFUSE**:
print a one-liner — "Evidence must be concrete (path, number, query, or
screenshot). What's the anchor?" — and STOP for the user's response. Do not
write the entry without it.

### 1B.3 Append to the project journal

Two writes, both mechanical:

**Primary store** — `~/.cws/projects/<slug>/learnings.jsonl` (one JSONL row):

```bash
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
ENTRY=$(/usr/bin/python3 -c "
import json
print(json.dumps({
  'ts': '$TS',
  'stage': '$STAGE',
  'tags': $TAGS_JSON,
  'trigger': '''$TRIGGER''',
  'lesson': '''$LESSON''',
  'evidence': '''$EVIDENCE''',
  'next_time': '''$NEXT_TIME''',
  'confidence': '$CONFIDENCE'
  $SUPERSEDES_FIELD
}, ensure_ascii=False))
")
echo "$ENTRY" >> "$CWS_PROJECT_DIR/learnings.jsonl"
```

The `cws-timeline-log` bin is the timeline shape; the storage shape is the
JSONL above. Do not conflate the two — timeline events are for "what skill
ran when"; learnings entries are for durable rules.

**Markdown index** — `./.cws/learnings.md` (one-line summary, chronological):

If the file doesn't exist, create it with this header and the entry:

```markdown
# Project learnings

Append-only journal. Source of truth is
`~/.cws/projects/<slug>/learnings.jsonl`. This file is the human-readable
index, committed to git.

- 2026-05-27 · promote · high · Banner B (no browser chrome) converts 3x
  better at same volume. Evidence: GA4 first_visit→install 6% → 17%.
```

If the file exists, insert the new line under `# Project learnings`,
maintaining chronological order (newest at the top OR at the bottom — pick
one once and stick with it; this implementation uses **newest at the
bottom** so the file reads forward in time, matching the JSONL append
order).

The markdown line format:

```
- <YYYY-MM-DD> · <stage> · <confidence> · <lesson>. Evidence: <evidence>.
```

If `supersedes:<prior_ts>` is set, append `[supersedes <prior_ts>]` at the
end of the markdown line.

### 1B.4 D3 — promote to global learnings?

After the local write succeeds, ask:

`AskUserQuestion D3` — Promote this lesson to the global cross-project file?

- ELI10: This lesson is now in this project's journal. We can ALSO copy it
  to `~/.cws/global-learnings.jsonl`, which biases every future cws-studio
  sprint on every project. Use this only for protocol-level rules that
  apply across launches (e.g. "host_permissions widening always loses
  30-60% of installed users").
- Stakes if we pick wrong: promoting a project-specific lesson pollutes
  every future project's preamble; NOT promoting a truly cross-project rule
  means re-learning it in the next launch.
- Recommendation: **B) Keep local** — global promotion is the exception.
  Most lessons are project-specific until proven otherwise.
- Completeness: Note: options differ in kind, not coverage — no completeness score.
- Pros/cons:
  - A) Promote to global
    - ✅ The next sprint (any project) sees this lesson in its preamble.
    - ✅ Compounding leverage on durable rules.
    - ❌ One wrong global lesson biases every future launch — hard to undo.
  - B) Keep local (recommended)
    - ✅ Default-safe. This project's journal still surfaces it next session.
    - ✅ Promotable later if the rule generalizes.
    - ❌ The next project starts blind to this lesson until it surfaces again.
- Net: promote only when the user is explicit. The recommended posture is
  conservative — local now, promote later if you see the same pattern in
  another launch.

If A: append the same JSONL row to `~/.cws/global-learnings.jsonl`. If the
file doesn't exist, create it.

If B: skip.

### 1B.5 Exit

Confirm the write in one operator-voice line:

```
Recorded · promote · high · Banner B (no browser chrome) converts 3x better.
  Path: ~/.cws/projects/color-code-picker/learnings.jsonl (entry #13)
  Index: ./.cws/learnings.md
```

Route back to `CURRENT_STAGE`.

---

## Phase 2 — Iron rules (apply on every append)

These rules are MECHANICAL. They do not require user confirmation. They are
enforced silently in the append path. If a rule fails, STOP and ask for the
specific missing piece.

### 2.1 One-line lesson

The `lesson` field is exactly one line. No `\n`. No paragraph. No "and also".
If the user's observation contains two distinct lessons, write two entries.

Bad: "Banner B converts better and also the Welcome Page CTA should be
imperative; also FB ads need iso country targeting."

Good: three separate entries, one per rule.

### 2.2 Concrete evidence

`evidence` MUST contain at least one of:

- A file path (`./.cws/...`, `~/.cws/...`, `.cws/screenshots/...`)
- A number (volume, %, count, days)
- A query (a Semrush query, a SQL-like filter)
- A screenshot reference

If the user's evidence line has none of these, REFUSE the write and surface
the missing anchor. Vibes are not evidence.

### 2.3 One-line next-time

Same shape as `lesson`. One line. One action. If the next-time has more
than one action, the lesson is actually two lessons; split.

### 2.4 Never delete; always supersede

If a prior lesson is wrong, write a new entry with
`supersedes:<prior_ts>` set. The prior entry STAYS in the JSONL. The
markdown line for the prior entry STAYS in `learnings.md`. The audit trail
is the point — six months from now you want to see WHY you flipped.

The reading layer (cws-learnings-search) does not currently de-dupe
superseded entries. That's intentional. If you want the latest version of
a lesson on a topic, grep for the topic and read the most recent entry.

### 2.5 Confidence is sticky

`confidence` is set once at append time. It does NOT decay automatically.
If the user wants to bump confidence on an existing lesson (e.g. "we saw
this pattern again in the next launch"), they supersede the old entry with
a new one at higher confidence.

A future enhancement (not in this skill) could add an opt-in decay flag —
"drop one confidence step per 30 days of staleness" — but it requires
explicit user opt-in via `cws-config set learnings_decay true`, and is not
auto-applied today.

### 2.6 No editing

`learnings.jsonl` is append-only. `learnings.md` is append-only. The Write
tool is used only for the FIRST creation of `learnings.md`. After that, use
Edit with line-precise inserts, never `Write` (which would overwrite).

If the user asks to edit an entry, refuse and explain the supersede pattern.

### 2.7 No silent writes

Every append produces the one-line operator confirmation at 1B.5. No
"learning saved" toast. No silent success. The user must see exactly what
landed in the journal so they can catch a misparse immediately.

---

## Phase 3 — Internal-caller contract

When other skills invoke cws-learn in read mode (not interactive), they pass
a payload like:

```
cws-learn --read --stage promote --limit 3
```

or, more typically, they shell out to the bin directly:

```bash
"$BIN/cws-learnings-search" --stage promote --limit 3
```

cws-learn's read mode renders FOR the human; the bin returns RAW. The
contract is:

- **Skill-to-human read** — render with the operator-voice block above.
- **Skill-to-skill read** — go straight to the bin, parse JSONL yourself.

Don't double-render. If you invoke cws-learn from another skill expecting
JSON back, you'll get prose. Use the bin.

The callers most likely to need this:

- **cws-sprint** — show the 3-5 most-relevant learnings in its "where am I"
  summary. Calls `cws-learnings-search --stage <current> --limit 3`.
- **cws-challenge** — surface lessons tagged with the stage being
  challenged, to catch "we said we'd avoid X next time" gotchas. Calls
  `cws-learnings-search --stage <target-stage> --limit 5`.
- **cws-retro** — when computing the retro report, prepend the 3 most
  recent learnings for the current stage so the user has the rule context
  before reading the numbers.
- **cws-idea** — when generating a fresh idea, read global learnings to
  pre-screen the candidate against past failure modes.

---

## When NOT to use cws-learn

- **Ephemeral conversation notes.** "Remember that the Stripe API key is in
  1Password" is a session-memory thing — use Claude's memory tools, not the
  launch journal. The journal is for durable, evidence-anchored RULES, not
  state.
- **Irreversible action confirmations.** "Confirm we want to delete the
  Dolphin profile" is not a learning — it's a gate. Use `cws-careful` for
  hard stops on destructive operations. cws-learn records what you learned
  AFTER the fact, not what you're about to do.
- **Stage artifacts.** "The chosen keyword is `color code picker`" belongs
  in `./.cws/01-idea.md`, not in the journal. The journal is meta — rules
  about the process, not state about this launch.
- **Per-skill state.** If a skill needs to remember "I'm at step 4 of 7",
  that goes in `./.cws/state.json`, not the journal.
- **Logs.** Timeline events (skill X ran at time Y) go through
  `cws-timeline-log`, not cws-learn.

If the user invokes cws-learn for any of the above, redirect them to the
right tool in one line and exit. Do not write the wrong thing.

---

## Companion skills

- **cws-retro** — the retro often surfaces 1-3 learnings per stage. After
  cws-retro produces its report, the user runs cws-learn append for each
  surfaced finding. The retro itself is the trigger; cws-learn is the
  capture.
- **cws-challenge** — when a challenge probe finds a gap or a failure
  mode, that's a learning. The challenge result is the evidence; cws-learn
  is the capture. After a successful challenge that disproves a current
  belief, supersede the prior lesson.
- **cws-resync** — when a mid-launch change propagates, it almost always
  exposes a process gap ("we didn't realize banner changes invalidate
  Welcome Page screenshots"). That gap is a cross-stage learning; capture
  it with cws-learn at `stage: cross`.
- **cws-careful** — when a careful gate catches a near-miss ("you were
  about to widen host_permissions without a re-consent plan"), that's a
  high-confidence learning waiting to happen. cws-careful does NOT
  auto-append; it prompts the user to run cws-learn after the gate.

The pattern: another skill creates the evidence; cws-learn captures the
rule.

---

## Storage shape (for reference)

`~/.cws/projects/<slug>/learnings.jsonl` — one JSONL row per entry. Append
only. Newest at the bottom.

`./.cws/learnings.md` — human-readable index. Committed to git. Newest at
the bottom. One markdown line per entry.

`~/.cws/global-learnings.jsonl` — opt-in cross-project journal. Promoted to
via D3. Same JSONL shape.

`cws-learnings-search` bin — read API. Supports `--limit`, `--stage`,
`--grep`. Default 5 entries. No write API exposed (intentional).

---

## Phase 4 — Cross-launch carry-over (special read mode)

After a launch ends — meaning either `cws-monetize` has gated successfully
AND the launch has been running ≥ 30 days, OR the project has been shelved
(state.json has `launch_status: shelved`) — the user can run cws-learn in
a special **carryover** mode.

User trigger phrases: "distill learnings", "carry over to next launch",
"export project learnings", "what should I keep for the next sprint".

### 4.1 Detect carryover intent

Carryover is a read-shaped command with a write effect: it produces a
distilled markdown the user can paste into the seed of a new project's
`cws-init`. The intent is signaled by the word "carryover", "carry over",
"distill", "export", or "next launch" in the trigger.

If the user said "show learnings" generically, this is NOT carryover — fall
back to the normal read mode in Phase 1A. Carryover is only triggered when
the user explicitly asks for the cross-launch distillation.

### 4.2 Produce the distillation

Read every entry in `~/.cws/projects/<slug>/learnings.jsonl`. For each
unique `lesson` (deduplicated by exact match), keep the entry with the
HIGHEST confidence. Tie-break on most recent ts.

Render the result as a markdown block at
`./.cws/learnings-carryover.md`:

```markdown
# Carryover — <slug>

Distilled from `<n>` entries in `~/.cws/projects/<slug>/learnings.jsonl`.
Generated <iso8601>. Pastable into a new project's seed prompt or into
`~/.cws/global-learnings.jsonl` for cross-project bias.

## Stage 0 — account setup

- [high] <lesson>. Evidence: <evidence>. Next time: <next_time>.

## Stage 1 — idea

- [high] <lesson>. Evidence: <evidence>. Next time: <next_time>.

## Stage 2 — package

...
```

Group by stage. Within each stage, sort confidence-desc, then ts-desc. Drop
entries with `confidence: low` UNLESS the stage has no high/med entries
(in which case keep the most recent low entries as placeholders).

### 4.3 D4 — promote the distillation to global?

After the carryover file lands, ask:

`AskUserQuestion D4` — Promote the carryover to `~/.cws/global-learnings.jsonl`?

- ELI10: We can copy the full distilled set into the global cross-project
  file so the NEXT sprint (any project) sees these lessons in its preamble.
  This is the bigger version of D3 (which promotes one entry at a time).
- Stakes if we pick wrong: promoting low-confidence lessons biases every
  future sprint; under-promoting leaves the next project re-learning the
  same things.
- Recommendation: **A) Promote, but filter to high-confidence only** —
  matches what you'd actually want a fresh sprint to start with.
- Completeness: A=10/10, B=7/10, C=2/10.
- Pros/cons:
  - A) Promote high-confidence only (recommended)
    - ✅ Next sprint sees only durable rules; signal stays high.
    - ✅ Easy to add more later from the per-project file.
    - ❌ Loses the medium-confidence rules that might also matter.
  - B) Promote all (high + med)
    - ✅ Broader coverage; nothing falls through the cracks.
    - ✅ Useful if this launch was unusually instructive.
    - ❌ More noise in every future preamble.
  - C) Skip — keep carryover local only
    - ✅ Default-safe; no global change.
    - ❌ Next sprint starts blind to these lessons.
- Net: A is the durable answer. B for unusually instructive launches.
  C if the user is exploring.

### 4.4 Exit

Carryover is a write-and-exit operation. Tell the user the file path; do
not route into another skill. If they want to start a new project, that's
`cws-init` from a fresh directory.

```
Carryover written: ./.cws/learnings-carryover.md  (<n> distilled entries)
Global file: <promoted | skipped>
```

---

## Phase 5 — Worked examples

These examples make the iron rules concrete. Reference them when in doubt.

### Example A — Banner conversion learning (append mode)

User message: "log this — small banner B (no browser chrome) hit 17%
install conv vs A at 6%, both at 1.2K weekly impressions."

This is unambiguous append. Skip D1. Parse:

- trigger: "Banner B vs A swap on day 4 of promote"
- lesson: "Banner B (no browser chrome) converts ~3x better at same volume."
- evidence: "GA4 first_visit→install 6% → 17% over 4-day swap, n=1.2K weekly."
- next_time: "Default to no browser chrome on the small banner; override only when the browser context IS the product."
- stage: `promote` (from CURRENT_STAGE)
- tags: `["banner", "conversion", "small-banner"]`
- confidence: `high` (clean swap, n=1.2K, 3x effect size)

Write to both files. Ask D3 (promote to global). Recommend A — this is a
durable rule about CWS banner design that applies across launches.

### Example B — Vague evidence — REFUSE

User message: "log that the welcome page felt much smoother after we
shortened it."

Parse the evidence line: "felt much smoother" — no path, no number, no
query, no screenshot. IRON RULE 2.2 fires.

Respond: "Evidence must be concrete (path, number, query, or screenshot).
The Welcome Page is at `./.cws/03-launch/welcome-page.md` — what changed
between the old and new versions (diff), and what number moved (GA4
event, dwell time, scroll depth)?"

STOP. Do not write. The user re-tries with concrete anchors.

### Example C — Stage filter read

User message: "any learnings about promote?"

This is read mode with a stage filter. Skip D1.

```bash
"$BIN/cws-learnings-search" --stage promote --limit 5
```

Render each row in the operator-voice block from 1A.3. If zero matches,
say so plainly — "No promote learnings yet — 0 of 12 total entries" — and
exit. Route back to CURRENT_STAGE.

### Example D — Supersede a prior lesson

User message: "remember — billing cycle is best as weekly, not monthly."

Phase 1B.1 surfaces a prior entry (from 8 weeks ago): "Monthly billing
converts best because users anchor on $X/mo." The new lesson contradicts
the prior. D2 fires.

Recommendation: A (supersede). Write the new entry with
`supersedes: <prior_ts>`. Both entries stay in the JSONL. The markdown
line for the new entry appends `[supersedes <prior_ts>]` for audit.

### Example E — Two lessons in one observation — SPLIT

User message: "log this — banner B beat A by 3x and the Welcome Page CTA
needs to be imperative."

Two distinct rules. IRON RULE 2.1 fires.

Respond: "That's two lessons. Recording them as two entries — banner
conversion and Welcome Page CTA voice — so each can supersede
independently if it gets refined. Proceeding with two writes."

Skip D2 unless the user objects. Write both. The user sees both
confirmations at exit.

---

## Phase 6 — Operational self-improvement

Before exiting cws-learn (success path), check whether the skill itself
hit a durable quirk worth recording. Examples:

- The user's evidence line repeatedly failed concreteness check and
  needed coaching on what "concrete" means → consider recording a meta
  learning at `stage: cross` about evidence quality.
- A `--grep` pattern returned zero matches but the user clearly believed
  the lesson existed → the search shape may need tuning; record this for
  the next bin enhancement.
- A supersede entry created in this session was the third on the same
  topic → the topic is unstable and may need a dedicated artifact rather
  than a journal entry.

Do NOT auto-record. Surface the observation in the exit confirmation as a
one-liner — "noticed: 3rd supersede on `billing-cycle`, may warrant a
dedicated artifact" — and let the user decide whether to act.

---

## Phase 7 — Edge cases and recovery

### 7.1 The journal file is corrupt

`learnings.jsonl` should be one well-formed JSON object per line. If a
line is malformed (truncated write, manual edit gone wrong), the bin
returns garbled output and downstream skills break.

Detection: on append-mode entry, the skill runs a one-liner sanity check
before writing:

```bash
/usr/bin/python3 -c "
import json, sys
with open('$CWS_PROJECT_DIR/learnings.jsonl') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line: continue
        try: json.loads(line)
        except: print(f'CORRUPT line {i}: {line[:80]}'); sys.exit(1)
print('OK')
" || _CORRUPT=1
```

If corrupt, STOP the append and tell the user the line number. Do NOT
auto-repair. The user inspects, fixes manually (or quarantines the
corrupt line into `learnings.jsonl.broken`), and re-runs the skill.

The markdown index is more forgiving — it's prose and the bin doesn't
parse it. Skip the sanity check on the markdown side.

### 7.2 The journal is empty but the markdown has entries

User manually wrote learnings into `./.cws/learnings.md` without going
through the skill. The JSONL is empty; the markdown has rows.

cws-learn detects this on append and surfaces it:

> Markdown index has N entries but JSONL has 0. The JSONL is the source
> of truth for the bin. Want me to back-fill the JSONL from the markdown
> lines (best-effort parse), or leave them and start fresh?

Recommendation: leave them. Manual markdown entries lack the structured
fields (trigger, evidence, next_time, confidence) and back-filling
fabricates data. The right move is to let manual entries be a separate
prose layer and only structured entries go through cws-learn.

### 7.3 The user wants to remove a single entry

IRON RULE 2.6 says never edit, never delete. If the user insists ("I
recorded the wrong thing, please remove the last entry"), the answer is:

- Append a NEW entry that supersedes the wrong one. The new entry's
  lesson is the correct version, OR a one-line correction note ("the
  prior entry was recorded against the wrong launch — disregard").
- The wrong entry STAYS on disk. The journal is append-only.

If the user keeps pushing, surface the rationale in one line: "Append-only
is the point — the audit trail is more valuable than a clean file. If
you have a reason to break this rule, edit `learnings.jsonl` manually
and re-run the sanity check; cws-learn won't do it."

### 7.4 Storage path conflict (slug change)

If `cws-slug` returns a different `$SLUG` than the prior session (e.g.
the directory was renamed), `$CWS_PROJECT_DIR` changes and the prior
journal is at a stale path.

cws-learn detects this on read: if `learnings.jsonl` at the new
`$CWS_PROJECT_DIR` is empty/missing AND a journal exists at a
recently-modified `~/.cws/projects/*/learnings.jsonl`, surface the
mismatch:

> Slug looks like it changed — new SLUG `<new>`, but there's a journal
> at `~/.cws/projects/<old>/learnings.jsonl` with N entries. Migrate it
> to the new slug, or treat this as a fresh project?

Recommendation: migrate. Slug churn is usually a rename, not a new
project. The migration is a single `mv` of the project directory under
`~/.cws/projects/`.

### 7.5 The user invokes from outside a git repo

`_BRANCH` will be `no-git`. The skill still works — `$SLUG` is derived
from the directory name, not git. The journal lives at
`~/.cws/projects/<slug>/learnings.jsonl` independent of git.

The markdown index at `./.cws/learnings.md` is committed to git when git
exists, but cws-learn does not stage or commit it (that's the user's
job, usually as part of a sprint commit). If git is absent, the markdown
file is just on disk.

---

## Phase 8 — Integration with other skills (detail)

This section makes the call-paths explicit so callers don't double-render
or double-write.

### 8.1 cws-sprint pre-flight read

`cws-sprint` reads the latest 3-5 entries on every invocation as part of
its "where am I" summary. The call is:

```bash
"$BIN/cws-learnings-search" --limit 5
```

NOT through cws-learn. cws-learn's read mode is for the human; the bin
is for the skill. cws-sprint formats the rows in its own voice.

### 8.2 cws-retro auto-suggestion

`cws-retro` produces a report at the end of each stage. The report
includes a "candidate learnings" section — rules the retro author thinks
should go in the journal. These are SUGGESTIONS only; cws-retro does NOT
auto-append.

The user then runs cws-learn append for each suggestion they accept. The
trigger phrase in the user's message references the retro:

> log this from the retro — banner B converted 3x better than A.

The skill's evidence requirement (IRON RULE 2.2) bites here: the retro
itself often contains the concrete number; cws-learn parses the retro
file path as the evidence anchor.

### 8.3 cws-challenge cross-reference

`cws-challenge` runs against a stage that already gated. As part of the
challenge, it reads the lessons tagged with that stage:

```bash
"$BIN/cws-learnings-search" --stage <target> --limit 10
```

For each lesson, the challenge checks whether the stage's CURRENT
artifact respects the lesson's `next_time` action. If a lesson said
"default to no browser chrome" and the current banner artifact has
browser chrome, that's a finding the challenge surfaces.

The challenge does NOT auto-append a new lesson when it finds a
violation. It surfaces the finding; the user decides whether the
violation is intentional (in which case a NEW superseding lesson is
warranted) or a miss (in which case the fix is to the artifact, not the
journal).

### 8.4 cws-resync cause logging

`cws-resync` is a great place to capture lessons about cascade quality.
After a resync completes, the user is encouraged (not required) to run
cws-learn for the upstream edit that triggered the cascade:

> log this — the moderation re-rejection on permission `cookies` was
> because the justification missed the user-data clause.

This becomes a `stage: cross` lesson with `tags: ["resync", "moderation",
"permission"]` and evidence pointing at `.cws/.resync.log`.

### 8.5 cws-careful gate-pass logging

When `cws-careful` clears a gate (host_permissions widening with a
re-consent plan), that's a HIGH-confidence learning waiting to happen.
cws-careful does NOT auto-append; it tells the user:

> Gate cleared. Worth a learning? Run `/cws-learn` with the lesson and
> the careful-gate timestamp as the evidence anchor.

The user runs cws-learn; the evidence is the careful gate's recorded
plan, the next_time is the re-consent template from the careful artifact.

---

## Skill Routing Footer

The default exit routes back to whatever stage was active when cws-learn
ran. cws-learn is rarely a destination skill — it's a stop on the way
through some other workflow.

```
Next: /cws-<CURRENT_STAGE>
Why: You were mid-<CURRENT_STAGE> when the lesson surfaced. Pick up where
you left off; the next preamble will surface this lesson automatically.
```

If `CURRENT_STAGE` is unset, route to `cws-sprint`:

```
Next: /cws-sprint
Why: No stage was active — sprint will show the lesson in its preamble
and route you to the right stage from there.
```

If the user ran cws-learn purely for read (no append, no stage), there is
no implicit next step. Say so plainly:

```
Next: (your call)
Why: You were just recalling — no implicit next step. Type a skill name
when ready.
```
