# Pipeline state & artifacts — the single source of truth

Every skill in `cws-studio` reads from and writes to the same per-project state
directory: `./.cws/`. This is what makes the sprint cohesive instead of seven
isolated skills — handoffs are *files*, re-entry is *file detection*, gates are
*JSON fields*.

## Directory layout (per project)

```
./.cws/
  state.json                # pipeline state — current stage, gates, IDs
  01-idea.md                # scoring table + chosen hypothesis (cws-idea)
  02a-listing.md            # name, short/full desc, Turgenev results (cws-package)
  02b-build.md              # manifest type, donor, build status (cws-build)
  03-launch.md              # banners, icons, Welcome Page, locales, draft ID, mod status (cws-launch)
  04-promote.md             # campaigns, UTMs, analytics IDs, reviews (cws-promote)
  05-monetize.md            # paywall config, billing cycle, rollout (cws-monetize)
  challenges/               # /cws-challenge outputs
    YYYY-MM-DD-<stage>.md
  retro/                    # /cws-retro outputs
    YYYY-MM-DD.md
  learnings.md              # /cws-learn append-only journal
  .resync.log               # /cws-resync change log
```

A user typically invokes a stage skill from the project root; `.cws/` lives
there. If the user runs from a subdirectory, walk up to find `.cws/` (max 4
levels) before creating a new one.

## state.json schema

```json
{
  "schema": 1,
  "project_name": "color-code-picker",
  "current_stage": "cws-promote",
  "gates_passed": ["idea", "package", "build", "launch"],
  "extension": {
    "id": "abcdefghijklmnopqrstuvwxyz000000",
    "draft_uploaded": true,
    "submitted_for_review": true,
    "moderation_status": "approved",
    "store_url": "https://chromewebstore.google.com/detail/..."
  },
  "idea": {
    "name_keyword": "color code picker",
    "us_volume_exact": 1900,
    "kd_zone": "orange",
    "donor_url": "https://github.com/..."
  },
  "monetization": {
    "enabled": false,
    "weekly_users_at_enable": null,
    "paywall_url": null
  },
  "history": [
    { "ts": "2026-05-23T10:00:00Z", "stage": "cws-idea", "event": "gate_passed" },
    { "ts": "2026-05-24T14:30:00Z", "stage": "cws-package", "event": "gate_passed" }
  ],
  "last_updated": "2026-05-26T09:12:00Z"
}
```

Fields are additive — skills extend the JSON as needed. Never delete keys
written by an earlier stage; the audit trail is the entire pipeline.

## Stage-artifact contract

Each stage produces **one** Markdown artifact at the path in the layout. The
artifact is the **handoff** to the next stage. Mandatory top of every artifact:

```markdown
---
stage: cws-package
status: complete   # one of: draft | complete | superseded
created: 2026-05-23
updated: 2026-05-23
---
```

Body sections are defined per-stage (see each stage skill). The status flag
matters: `draft` means re-entry resumes; `complete` means the gate is met and
downstream stages can depend on it; `superseded` means /cws-resync has rewritten
it after a mid-launch change.

## Re-entry protocol — what every stage skill MUST do first

On invocation, before doing any work:

1. **Locate `.cws/`**: walk up from cwd up to 4 levels; if not found, ask the
   user where the project root is, then create `.cws/`.
2. **Read `state.json`** (create with `schema: 1` if missing).
3. **Read the stage's own artifact** if it exists.
4. **Branch**:
   - **No artifact** → start fresh; begin the workflow.
   - **Artifact exists, status `draft`** → resume; tell the user what's done,
     what remains, ask if they want to continue or restart.
   - **Artifact exists, status `complete`** → the stage is already done; ask if
     the user wants to **edit**, **rerun**, or **route elsewhere** (e.g. next
     stage). Do not silently overwrite a complete artifact.
   - **Artifact exists, status `superseded`** → behave like `draft`: the
     content is stale post-resync; re-do the affected parts.
5. **Verify prior gates**. If the stage requires a prior gate (e.g. cws-launch
   needs `idea`, `package`, `build`), confirm `gates_passed` contains all of
   them. If not, tell the user the missing prerequisites and offer to route to
   the earliest missing stage. **Never silently skip gates.**

## Gates — definition

A stage's gate is *passed* when:

- The artifact exists and has `status: complete`.
- Stage-specific exit criteria in the SKILL.md are satisfied.
- The skill writes `gates_passed: [..., "<stage-name>"]` and appends a
  `gate_passed` event to `history`.

Gates in order: `idea` → `package` → `build` → `launch` → `promote` → `monetize`.
(`package` and `build` run in parallel; both must pass before `launch`.)

## Writing JSON safely

Use a read-modify-write pattern:

```bash
jq '. + {"last_updated":"'"$(date -u +%FT%TZ)"'"}' .cws/state.json > .cws/state.json.tmp
mv .cws/state.json.tmp .cws/state.json
```

…or do it via a small Python snippet — whichever fits the session. Don't
clobber unknown keys; treat state.json as additive across skills.

## What changes vs. doesn't trigger a resync

Some mid-launch changes propagate across stages (handled by `cws-resync`):

| Change | Affects |
|---|---|
| Name keyword changed | listing copy, Welcome Page, banners, ad copy, translations |
| Banner / icon changed | launch artifact, possibly ad creatives |
| Full description changed | listing, all 50+ locale translations, Turgenev re-check |
| Paywall config changed | monetization artifact + monetization rollout history |

When a stage rewrites a value used downstream, it must mark downstream
artifacts as `superseded` so re-running them is mandatory.

## When a user asks "where am I?"

cws-sprint's first job is to read `state.json` and the artifacts and answer
this question concretely. Show: current stage, gates passed, last 3 history
events, next gate's exit criteria.
