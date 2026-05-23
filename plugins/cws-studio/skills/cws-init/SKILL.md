---
name: cws-init
description: >-
  Scaffold a fresh CWS launch project — create the `./.cws/` state directory,
  write a starter `state.json`, drop empty per-stage artifact stubs, and
  optionally capture a one-liner seed idea. Use at the very start of a new
  extension launch, or when the user is in a directory that has no `.cws/`
  yet and is asking the sprint to begin. Triggers on "start a new launch",
  "set up a cws project", "init cws", "new extension", "begin sprint here",
  "initialize the pipeline". Also use to upgrade an old state.json (schema
  migration) — detects the prior schema, rewrites it, preserves data.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
triggers:
  - init cws
  - start a new launch
  - new extension
  - set up a cws project
  - begin sprint here
---

# cws-init — scaffold a project

Scaffold `./.cws/` so every other skill has a known place to read and write.
Migrate an older `state.json` if found. Capture a one-liner seed idea if the
user typed one. End with a single next-move route — never a menu.

## Preamble (run first)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.0.0}"
BIN="$PLUGIN_ROOT/bin"
eval "$("$BIN/cws-slug" 2>/dev/null)"
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_SESSION_ID="$$-$(date +%s)"
mkdir -p "$CWS_PROJECT_DIR" 2>/dev/null
echo "SLUG: $SLUG"
echo "BRANCH: $_BRANCH"
echo "CWD: $(pwd)"
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; print('SCHEMA:', json.load(open('$_STATE_FILE')).get('schema','?'))"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-init\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

## AskUserQuestion Format

See `shared/askuserquestion-format.md`. D-numbering starts at D1 per invocation.

## Voice

See `shared/voice.md`. Do NOT print a file-by-file creation log. Summarize in
one line: "Scaffold ready: state.json + 9 stage stubs + learnings + log."

## Skill Routing Footer

See `shared/skill-routing.md`. One `Next: /cws-<skill>` line.

---

## Phase 0 — Sanity-check the project root

Refuse if `pwd` is `$HOME` or `/`. Refuse if `.cws/` exists with `schema` equal
to current and the user did not ask to "reset". If `.git` is not present,
print a one-line warning (artifacts should be committed) but proceed.

## Phase 1 — Existing state?

- `CWS_STATE: missing` → proceed to scaffold.
- `CWS_STATE: present`, schema matches: **abort** the scaffold; one line
  ("`.cws/` already initialized — schema 1"), route the user to `/cws-sprint`
  to see where they are.
- `CWS_STATE: present`, schema lower than current: **migrate**. Load all keys
  into a dict, write under the new schema, archive the old file to
  `.cws/state.json.bak.<timestamp>`. Preserve `history`. End the run with
  `Next: /cws-sprint`.

## Phase 2 — Capture seed (if any)

If the user's invoking message contains a one-liner idea ("init cws for a PDF
to PNG extension"), capture it. Otherwise skip — do not ask. The full idea
brainstorm happens in `cws-idea`, not here.

## Phase 3 — Scaffold

Create exactly this layout, **no extra files**:

```
./.cws/
  state.json
  00-account-setup.md   — stage:cws-idea(stage-0), status:draft
  01-idea.md            — stage:cws-idea(stage-1),  status:draft (with ## Seed if captured)
  02a-listing.md        — stage:cws-package,        status:draft
  02b-build.md          — stage:cws-build,          status:draft
  03-launch.md          — stage:cws-launch,         status:draft
  04-promote.md         — stage:cws-promote,        status:draft
  05-monetize.md        — stage:cws-monetize,       status:draft
  learnings.md          — empty section "# Project learnings"
  .resync.log           — empty
  .gitignore            — `*.tmp` and `state.json.bak.*`
```

state.json seed:

```json
{
  "schema": 1,
  "project_name": "<from user or dir name>",
  "current_stage": null,
  "gates_passed": [],
  "account_setup": {
    "proxy_provider": null,
    "proxy_id_in_dolphin": null,
    "proxy_country": null,
    "proxy_validated": false,
    "proxy_residential": null,
    "dolphin_profile_id": null,
    "google_account": null
  },
  "extension": {
    "id": null,
    "draft_uploaded": false,
    "submitted_for_review": false,
    "moderation_status": null,
    "store_url": null
  },
  "idea": {},
  "monetization": { "enabled": false },
  "history": [
    { "ts": "<iso8601 utc>", "stage": "cws-init", "event": "scaffolded" }
  ],
  "last_updated": "<iso8601 utc>"
}
```

Each artifact stub gets only frontmatter:

```markdown
---
stage: cws-<owning-skill>
status: draft
created: <iso8601 utc>
updated: <iso8601 utc>
---
```

## Phase 4 — Speak

One short line. **No file-creation log.**

> Scaffold ready for `<SLUG>`: state.json + 9 stage stubs + learnings + log.

If a seed was captured: append "Seed: <one-line>".

## Skill Routing Footer

```
Next: /cws-idea
Why: Stage 0 (proxy + antidetect + Google account) is the first hard gate;
cws-idea walks it before any keyword work.
```

If a schema migration ran instead of a fresh scaffold:

```
Next: /cws-sprint
Why: state.json migrated to schema 1; sprint will read it and pick up where
you left off.
```

---

## What init never does

- Doesn't overwrite an existing `.cws/` of the same schema.
- Doesn't decide an idea — only records the one-liner if the user gave one.
- Doesn't run any stage.
- Doesn't print a file-by-file creation log.
