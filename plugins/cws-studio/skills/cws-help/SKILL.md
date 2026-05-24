---
name: cws-help
description: >-
  Print the cws-studio plugin's skill catalog — what each skill does, when to
  invoke, the pipeline order, and which companion skills back which stage.
  Use when the user says "what cws skills are there", "what can cws-studio
  do", "cws help", "list cws skills", "what's the launch pipeline", "how
  does cws-studio work", or is exploring the plugin for the first time.
  Routes to the right starting skill (cws-init / cws-sprint / a specific
  per-stage skill) instead of dumping a wall of docs.
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
triggers:
  - cws help
  - what cws skills are there
  - what can cws-studio do
  - list cws skills
  - how does cws-studio work
  - what's the cws launch pipeline
---

# cws-help — plugin catalog and entry-point router

You are the on-ramp for cws-studio. A new user types `/cws-help` (or the
plugin auto-suggests this skill when their message looks like exploration).
Your job is one short answer block, then one routed recommendation. **Not** a
wall of docs.

## Preamble (run first)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.1.0}"
BIN="$PLUGIN_ROOT/bin"
eval "$("$BIN/cws-slug" 2>/dev/null)"
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none')"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-help\",\"event\":\"started\",\"branch\":\"$_BRANCH\"}" 2>/dev/null
```

## AskUserQuestion Format

See `../../shared/askuserquestion-format.md`. One D-brief at most, only if the
right entry point is genuinely ambiguous.

## Voice

See `../../shared/voice.md`. Operator voice. No banner. One screen of catalog plus
one recommendation — never more.

## Skill Routing Footer

See `../../shared/skill-routing.md`. End with a single `Next: /cws-<skill>` line.

---

## Phase 0 — Decide what the user actually wants

Read the preamble echo + the user's invoking message. Pick one of four
postures:

1. **No state, no specific topic** ("what cws skills are there", "how do I
   use this") → catalog mode (Phase 1).
2. **State present, asking "where am I"** → don't recap the catalog; route
   directly to `/cws-sprint` (it does the diagnosis).
3. **State present, asking about a specific stage or topic** ("how do
   monetization", "what's cws-careful for") → one-paragraph answer about
   that skill + route to it.
4. **First-time RU/BY user mentioning antidetect / Stage 0 / Dolphin /
   proxies** → Phase 1 catalog with a Stage 0 callout, then route to
   `/cws-init` (if no state) or `/cws-idea` (if state exists with
   account-setup gate open).

## Phase 1 — Catalog (only if Phase 0 chose catalog mode)

Print this exact block, no banner, no decoration. Replace `<X>` markers with
the user's context (project slug or "this project" if no state):

```
cws-studio — Chrome Web Store launch pipeline for <X>

Pipeline (gate in → gate out):
  Stage 0  account-setup    /cws-idea (uses /cws-dolphin)
  Stage 1  idea-validation  /cws-idea
  Stage 2a listing-copy     /cws-package
  Stage 2b build            /cws-build
  Stage 3  assets + submit  /cws-launch  (gated by /cws-careful)
  Stage 4  paid promotion   /cws-promote
  Stage 5  monetization     /cws-monetize (gated by /cws-careful)

Conductor + automation:
  /cws-sprint     — single recommendation for "where am I" / "what next"
  /cws-autoplan   — execute every stage at full depth, batch taste calls
  /cws-init       — scaffold ./.cws/ on a fresh project

Companions:
  /cws-challenge  — adversarial second opinion on any gated stage
  /cws-careful    — pre-flight on irreversible actions (submit, monetize on)
  /cws-retro      — weekly/monthly metrics snapshot
  /cws-learn      — append a lesson; bias future sprints on this project
  /cws-resync     — propagate a mid-launch change across downstream stages
  /cws-dolphin    — Dolphin{anty} profile + proxy automation (Stage 0 and
                    portfolio scaling)

State lives in ./.cws/ — state.json + per-stage Markdown artifacts. See
cws-sprint references/pipeline-state.md for the schema.

MCP servers:
  semrush             — keyword research (OAuth on first use)
  dolphin-anty-docs   — semantic search over Dolphin docs (connected)
```

## Phase 2 — Recommend one entry point

Pick by state (see preamble):

- `CWS_STATE: missing` → `Next: /cws-init` ("scaffold .cws/ here so the
  pipeline can track state").
- `CWS_STATE: present`, `gates_passed: none` → `Next: /cws-idea` ("Stage 0
  proxy + antidetect + Google account, then keyword validation").
- `CWS_STATE: present`, `gates_passed: account-setup` → `Next: /cws-idea`
  ("continue into Stage 1 idea validation").
- `CWS_STATE: present`, `gates_passed: account-setup,idea` →
  `Next: /cws-package` ("listing copy is the next bottleneck on the
  critical path").
- `CWS_STATE: present`, ≥ `gates_passed: launch` → `Next: /cws-sprint`
  ("conductor will read state and pick the next move").

If the user explicitly asked about a specific skill ("what does cws-careful
do"), recommend that skill instead and skip the routing table.

## Phase 3 — Hand off

Do not run the per-stage skill yourself. End the turn with the routing
footer; the next skill will load its own preamble and play.

---

## What this skill is NOT

- Not a full docs site. Each per-stage skill has its own SKILL.md and
  `references/`.
- Not a status dashboard. `/cws-sprint` does the diagnosis.
- Not a tutorial. The skills are the tutorial; this is the index.
- Not a setup helper. `/cws-init` scaffolds; this routes there.

## Iron rules

- One catalog print per invocation. If the user re-asks "what's there",
  print one line ("see prior /cws-help") and route to /cws-sprint.
- Single Next: line. Never list 3 entry points.
- Do not invent skills. The catalog must match the `skills/` directory
  exactly. If a skill was added since this catalog was written, the agent
  should update this file in the same turn.
- Never run other skills' bash. Hand off only.

## Skill Routing Footer

```
Next: /cws-<picked-by-Phase-2>
Why: <one sentence — what it does for the user's current state>
```
