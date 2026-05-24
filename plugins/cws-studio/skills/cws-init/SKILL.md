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

This skill is the **front door** to a CWS launch. Every other skill in the
pipeline (cws-idea, cws-package, cws-build, cws-launch, cws-promote,
cws-monetize, cws-retro, cws-learn, cws-resync, cws-challenge, cws-careful,
cws-autoplan, cws-sprint) reads from `./.cws/state.json` and writes to one
of the per-stage artifact files in `./.cws/`. If that directory does not
exist, the pipeline cannot run. cws-init creates it once, exactly, with no
extra files.

You are not a planner here. You are a **scaffolder**. The idea brainstorm
happens in cws-idea. The Chrome Web Store account work happens in cws-idea
(Stage 0). The keyword research happens in cws-idea (Stage 1). The listing
copy happens in cws-package. The code happens in cws-build. None of that is
yours. Yours is: lay down the directory, write the JSON, leave.

## Preamble (run first)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.4.0}"
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

Branch off the echoed values:

- `CWD` is a refusable path (see Phase 0 catalog) → stop, refuse, give the
  remediation line. No scaffold.
- `CWS_STATE: missing` → fresh scaffold path (Phase 1 → 2 → 3 → 4).
- `CWS_STATE: present` with `SCHEMA: <current>` → abort: scaffold is already
  done. One-line acknowledgement, route to `/cws-sprint`.
- `CWS_STATE: present` with `SCHEMA: <lower than current>` → migration path
  (Phase 1 D2 brief, then archive-and-rewrite).
- `CWS_STATE: present` with `SCHEMA: ?` or `SCHEMA: <higher than current>` →
  refuse with a clear line: a future or unknown schema means the user has a
  newer cws-studio than this skill knows; do not downgrade.

## AskUserQuestion Format

See `../../shared/askuserquestion-format.md`. D-numbering starts at D1 per
invocation. Briefs in this skill are rare — most invocations are silent
scaffold-and-leave. D1, D2, D3 only fire when the situation is genuinely
ambiguous (see the three D-brief sections below).

## Voice

See `../../shared/voice.md`. Do NOT print a file-by-file creation log. Summarize in
one line: `Scaffold ready: state.json + 9 stage stubs + learnings + log.`
Optionally append the seed line if one was captured. That is the entire
visible output of a successful run.

## Skill Routing Footer

See `../../shared/skill-routing.md`. One `Next: /cws-<skill>` line.

---

## Phase 0 — Sanity-check the project root

Before any directory is created, refuse if the working directory is one of
the listed forbidden paths. Each refusal has a user-visible cost (what
breaks if we went ahead) and a one-line remediation (what the user should
do instead). The refusal is one line, then the remediation, then stop.

### Refusal catalog

| Refused `CWD` | User-visible cost | Remediation |
|---|---|---|
| `$HOME` | Polluting the home directory with `.cws/`; every shell `ls` in `$HOME` would surface it; risks accidental commits into a dotfiles repo. | `mkdir ~/projects/<extension-name> && cd ~/projects/<extension-name>` then re-run. |
| `/` (root) | A `.cws/` at filesystem root requires sudo; every stage skill afterward would also need sudo; total operational mess. | Pick a real project directory under `$HOME` and `cd` there first. |
| `/tmp` (top level) | `/tmp` is wiped at reboot on most distros and on macOS at boot. The user would lose every artifact, every learning, every state file. | If you genuinely want a throwaway, scaffold under `/tmp/cws-<name>/` and re-run from inside that subdir — refusal applies only to top-level `/tmp`. |
| `/Applications` | macOS gatekeeper-protected. Writes may silently succeed and then disappear on the next Apple-controlled rewrite. | Use a directory you own under `$HOME`. |
| `/System` | macOS SIP. Writes fail. Even if they did not, you'd be poisoning a system path. | Use a directory you own under `$HOME`. |
| Inside another `.cws/` subtree | The state file you'd create would shadow the parent's project; later stage skills would walk up the tree, pick the wrong one, and corrupt cross-state. | `cd` out to a sibling directory of the existing project. |
| Read-only mount (`/Volumes/<readonly>`) | Writes fail mid-scaffold; you get a half-written state.json with no artifacts; later runs cannot detect the corruption cleanly. | `cp -R` the project to a writable location first. |
| `$HOME/Desktop` (warning, not refusal) | Not refused — but warn: Desktop syncs to iCloud on default macOS setups; the artifacts will replicate to every signed-in device. Acceptable for solo dev; not acceptable for a paid Dolphin profile that the user does not want syncing. | If undesired, `mv` the directory into `~/projects/` and re-run. |

If `CWD` matches a refused row: one short line plus the remediation, log
the refusal to the timeline (`{"skill":"cws-init","event":"refused","reason":"<row>"}`),
exit. Do not scaffold anything.

### Soft warnings (proceed, but mention)

- `.git` missing → one-line warning: `No git repo here. Stage artifacts should be committed so cws-retro can diff history. Run \`git init\` before /cws-idea.`
- `node_modules`, `.next`, `dist`, or `build` present in `CWD` and `.gitignore` absent → warn: `Found build output, no .gitignore — cws-init writes its own .gitignore rules into ./.cws/.gitignore only; you may also want a project-level .gitignore.`
- Directory name contains spaces → warn: `Spaces in the project path complicate every shell tool downstream (Dolphin runner, semrush exporter). Consider renaming.` Do not refuse — but flag.

### D1 brief — "project root ambiguous?"

Trigger: `CWD` is not on the refusal list **and** not obviously a project
root (no `.git`, no `package.json`, no `manifest.json`, no `Cargo.toml`,
no `pyproject.toml`, no `pom.xml`), **and** the directory name is generic
(`code`, `dev`, `projects`, `work`, `temp`, `new`, single-letter).

```
D1 — Scaffold .cws/ here, or change dir first?
Project/branch/task: $SLUG on $_BRANCH; CWD looks like a parent or scratch dir, not a project root.
ELI10: Every cws-studio skill reads and writes inside ./.cws/. That folder belongs at the root of one extension project, not in a parent folder that holds many projects. If we scaffold in the wrong place, every other stage skill writes to the wrong place too, and the SEO + build + launch artifacts get tangled with someone else's work.
Stakes if we pick wrong: state.json ends up in the parent dir; every later cd into a real project finds no .cws/ and re-scaffolds; you end up with two state files; the timeline log fragments; cws-retro can't reconstruct history.
Recommendation: B because every other cws-studio skill assumes ./.cws/ is at a single extension project root.
Completeness: A=4/10, B=10/10
Pros / cons:
A) Scaffold here anyway
  ✅ Fast — no cd, no shell juggling, scaffolds and moves on right now.
  ❌ State file lands in a generic parent; later real projects each get their own .cws/ that conflicts in scope and timeline logs.
  ❌ cws-sprint will find this scaffold first on any deeper cd and route the wrong project.
B) Stop, cd into the actual project root, re-run /cws-init (recommended)
  ✅ Lands the scaffold exactly where every other skill expects it.
  ✅ Keeps the timeline, learnings, and state coherent for the lifetime of the launch.
  ❌ Costs one extra shell round-trip before the scaffold lands.
Net: 30 seconds of cd vs. months of fragmented state. B unless the user confirms this generic dir really is the extension's home.
```

### D-brief decisions never asked

The following are Mechanical — do not raise a brief, just decide:

- `.gitignore` content (always: `*.tmp` + `state.json.bak.*`).
- Stage stub filenames and numbering (always: `00-account-setup.md`, `01-idea.md`, `02a-listing.md`, `02b-build.md`, `03-launch.md`, `04-promote.md`, `05-monetize.md`, `learnings.md`, `.resync.log`).
- State schema version (always: the current schema number).
- `last_updated` timestamp format (always: ISO-8601 UTC, `Z` suffix).

---

## Phase 1 — Existing state?

Three branches, decided by the preamble's `CWS_STATE` and `SCHEMA` echoes.

### Branch A — fresh (`CWS_STATE: missing`)

Proceed to Phase 2.

### Branch B — already current (`CWS_STATE: present` AND `SCHEMA: <current>`)

The scaffold is already done. Do not overwrite, do not re-init, do not even
re-touch timestamps — overwriting `last_updated` would lie to cws-retro
about activity. One line:

> `./.cws/` already initialized at schema <current>. Nothing to do here.

Then route to `/cws-sprint`. Skip Phase 2, 3, 4.

### Branch C — needs migration (`CWS_STATE: present` AND `SCHEMA: <lower>`)

Raise D2.

#### D2 brief — "schema migration confirmation"

```
D2 — Migrate state.json from schema <old> to <new>?
Project/branch/task: $SLUG on $_BRANCH; existing ./.cws/state.json at schema <old>, current schema is <new>.
ELI10: state.json is the single source of truth for the launch — every stage reads it. The schema number says which fields exist and in what shape. Migrating means: load the old fields into memory, write them back under the new schema with any new fields defaulted, and archive the old file with a timestamped backup. The pipeline is unchanged; only the on-disk shape moves forward.
Stakes if we pick wrong: skipping migration leaves state.json on the old schema; some later skills may read a field that doesn't exist yet, or default a field that is meant to be populated. Running it wrong overwrites your history field without backup.
Recommendation: A because every stage skill expects the current schema; running on a stale one is undefined behavior.
Completeness: A=10/10, B=2/10
Pros / cons:
A) Migrate now, archive old file to state.json.bak.<timestamp> (recommended)
  ✅ Brings state into the shape every current stage skill expects, no surprises later.
  ✅ Backup is local — recoverable instantly if migration ever needs to be reverted.
  ❌ One write to disk; old schema is gone from the live file (still in backup).
B) Skip — keep the old schema and risk per-stage skill mismatches
  ✅ Zero risk of a botched migration script.
  ❌ Every subsequent skill that reads a new field gets a None and may silently route wrong.
  ❌ cws-autoplan will refuse to run against a stale schema and abort the pipeline.
Net: Migration is the safe move; backup makes it reversible. A.
```

If user picks A: run the migration registry (next section). If B: print
one line acknowledging the user's choice, route to `/cws-sprint` without
touching state.

### Schema migration registry

Migrations are versioned, idempotent, and composable. The pattern:

```
migrations = {
  (1, 2): _migrate_v1_to_v2,
  (2, 3): _migrate_v2_to_v3,
  ...
}

def migrate(state, target):
    old = state.get("schema", 1)
    while old < target:
        fn = migrations[(old, old + 1)]
        state = fn(state)
        state["schema"] = old + 1
        old += 1
    return state
```

Each migration function is pure: takes a dict, returns a dict, no I/O. The
caller (this skill) handles the read, the archive, and the write.

#### Hypothetical v1 → v2 migration (illustrative)

If schema 2 added `account_setup.proxy_residential` (bool) and
`account_setup.proxy_country` (ISO-3166-alpha2):

```python
def _migrate_v1_to_v2(state):
    acc = state.setdefault("account_setup", {})
    acc.setdefault("proxy_residential", None)
    acc.setdefault("proxy_country", None)
    return state
```

#### Hypothetical v2 → v3 migration (illustrative)

If schema 3 split `extension` into `listing` and `package`:

```python
def _migrate_v2_to_v3(state):
    ext = state.get("extension", {})
    state["listing"] = {"id": ext.get("id"), "store_url": ext.get("store_url")}
    state["package"] = {
        "draft_uploaded": ext.get("draft_uploaded", False),
        "submitted_for_review": ext.get("submitted_for_review", False),
        "moderation_status": ext.get("moderation_status"),
    }
    state.pop("extension", None)
    return state
```

#### Migration discipline

- **Never delete a key** without moving its data somewhere; if a key is truly
  obsolete, move it under `state["_archived"]["<key>"]` for one schema cycle.
- **Always preserve `history`** verbatim; append one entry
  `{"ts": <now>, "stage": "cws-init", "event": "migrated", "from": <old>, "to": <new>}`.
- **Always archive the old file** to `./.cws/state.json.bak.<iso8601-utc>`
  before writing the new one. `.gitignore` rule already excludes `*.bak.*`.
- **Always run the registry top-down**: never jump straight from v1 → v3;
  walk each step so each migration sees the shape it was written for.
- **Never run a migration twice**: the schema number is the gate. If
  `state["schema"]` already equals the target, no-op.

After migration: write the new state file, route to `/cws-sprint`. Skip
Phase 2 (no seed capture on migration), Phase 3 (no scaffold needed —
artifacts already exist), and emit only the Phase 4 "migrated" voice line.

---

## Phase 2 — Capture seed (if any)

If the user's invoking message contains a one-liner idea — capture it. If
not, skip. The full idea brainstorm happens in cws-idea, not here. This
phase exists only so the user doesn't have to repeat themselves on the
hand-off to cws-idea.

### Seed-extraction rules

Run these in order. First rule that matches wins.

1. **Refuse on URL**. If the message contains `http://`, `https://`, or
   `www.`, do not capture — the user is referencing prior art, not stating
   an idea. Note in voice: "URL ignored — paste the donor URL inside
   /cws-idea where it belongs."
2. **Refuse on code fence**. If the message contains a triple-backtick
   block, do not capture — the user is pasting code or a manifest, not an
   idea. Note: "Code block ignored — bring it into /cws-build."
3. **Refuse on 3+ sentences**. Sentence count via simple `.!?` split. If
   ≥3, do not capture — that's a description, not a seed. Note: "Idea was
   longer than a one-liner; capture it inside /cws-idea's Phase 1 brief."
4. **Refuse on yes/no/proceed-style replies**. If the message is `ok`,
   `yes`, `go`, `proceed`, `continue`, `do it`, `start` (case-insensitive,
   trimmed), do not capture — that's a meta-reply, not an idea.
5. **Extract candidate**. Take the substring after any explicit lead-in
   token: `for`, `about`, `:`, `to`, `that`. Example: `init cws for a
   color-picker extension` → candidate is `a color-picker extension`.
6. **Trim**. Strip leading/trailing whitespace. Strip leading articles
   (`a`, `an`, `the`). Strip trailing period. Lowercase the first letter
   unless it's an obvious proper noun (acronym, capitalized brand).
7. **Cap length**. If the candidate exceeds 120 characters, truncate at
   the last word boundary before 120 chars, append `…`. Long seeds are a
   yellow flag that the user is over-describing.
8. **Write to artifact**. Put the cleaned candidate inside `01-idea.md` as:

   ```markdown
   ## Seed (captured by cws-init)
   <candidate>
   ```

   Nothing else lands in that artifact at this stage.

### Worked examples

| User message | Captured? | Seed line written |
|---|---|---|
| `init cws for a PDF to PNG converter extension` | yes | `pdf to png converter extension` |
| `start a new launch` | no | — (no idea in message) |
| `begin sprint here: chrome extension that mutes Twitter mentions of a list of words` | yes | `chrome extension that mutes twitter mentions of a list of words` |
| `init cws https://github.com/foo/bar` | no | — (refused on URL) |
| `init cws \`\`\`{"manifest_version": 3, ...}\`\`\`` | no | — (refused on code fence) |
| `init cws — I want a color picker that pulls swatches from any page, with one-click copy to clipboard, and a saved palette synced across browsers` | no | — (refused on 3+ sentences, sort of; this one is single but 30+ words; capture truncated at 120) |
| `init cws for color-picker` | yes | `color-picker` |
| `yes` | no | — (meta reply) |

The capture is intentionally narrow. The cws-idea skill is where the user
is supposed to be open-ended. Capturing too much here biases that
conversation toward whatever scraps the user happened to type at init time.

---

## Phase 3 — Scaffold

Create exactly this layout, **no extra files, no extra directories**:

```
./.cws/
  state.json              — JSON, the source of truth
  00-account-setup.md     — stage:cws-idea(stage-0), status:draft
  01-idea.md              — stage:cws-idea(stage-1),  status:draft (with ## Seed if captured)
  02a-listing.md          — stage:cws-package,        status:draft
  02b-build.md            — stage:cws-build,          status:draft
  03-launch.md            — stage:cws-launch,         status:draft
  04-promote.md           — stage:cws-promote,        status:draft
  05-monetize.md          — stage:cws-monetize,       status:draft
  learnings.md            — empty section `# Project learnings`
  .resync.log             — empty
  .gitignore              — `*.tmp` and `state.json.bak.*`
```

### Scaffold ordering rules

Order matters for crash-safety. If the process is interrupted partway, the
preamble must be able to tell on next run whether the scaffold is half-done
and refuse to compound the damage.

1. **`mkdir ./.cws/`** — first, atomic.
2. **`.gitignore`** — second, so any further writes are already covered if
   the project ends up being committed mid-scaffold.
3. **Stage stub files** in numerical order (`00-…` through `05-…`), then
   `learnings.md`, then `.resync.log`. Each is written atomically (write
   to `<file>.tmp`, then rename). Order is fixed so a partial scaffold
   can be detected: if `02a-listing.md` exists but `01-idea.md` does not,
   that's a partial — refuse on next run, do not overwrite.
4. **`state.json` last**. The state file is the gate that every other
   skill reads. If it is on disk, the scaffold is presumed complete. If it
   is missing but stub files exist, the scaffold is presumed crashed and
   the next run should warn before recreating.

### D3 brief — "name the project"

Trigger: the directory name is non-descriptive (single char, `tmp`,
`test`, `new`, `project`, `app`, `code`, `dev`, all-numeric) AND no seed
was captured AND `package.json`/`Cargo.toml`/`pyproject.toml` are absent
(no upstream name to inherit).

```
D3 — Project name?
Project/branch/task: $SLUG (derived from $(basename $(pwd))) on $_BRANCH; the dir name is generic, no upstream package name to inherit.
ELI10: state.json carries a project_name field. It shows up in cws-sprint's diagnosis line, in cws-learn entries, and in the listing default. A generic name like "tmp" or "new" makes every later report ambiguous — especially once you have more than one extension going.
Stakes if we pick wrong: every cws-sprint diagnosis prints "Project: tmp"; learnings indexed under "tmp" collide across projects; cws-package starts with a placeholder name keyword tied to "tmp".
Recommendation: A because once the launch is past Stage 1 the project_name field is read everywhere and renaming requires a cws-resync pass.
Completeness: A=10/10, B=6/10
Pros / cons:
A) Pick a short descriptive name now (recommended)
  ✅ One field set once; every later skill displays a meaningful project label.
  ✅ Learnings written under this project are searchable by a real name.
  ❌ User has to think for 10 seconds before the scaffold lands.
B) Use the dir name as-is and rename later via cws-resync
  ✅ No interaction needed; scaffold lands instantly.
  ❌ A later rename forces a cws-resync pass and rewrites every artifact's project_name reference.
  ❌ Learnings written before the rename stay under the old label.
Net: 10 seconds now or a resync later. A.
```

User-provided string is sanitized: trim, collapse internal whitespace,
strip leading/trailing punctuation, cap at 60 chars. Stored verbatim in
`state.json.project_name`. No further validation — the user owns this.

### State.json seed

```json
{
  "schema": 1,
  "project_name": "<from D3, seed, or dir name>",
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

### Stage stub format

Each artifact stub gets only frontmatter, no body:

```markdown
---
stage: cws-<owning-skill>
status: draft
created: <iso8601 utc>
updated: <iso8601 utc>
---
```

The single exception is `01-idea.md` when a seed was captured: append the
`## Seed (captured by cws-init)` block under the frontmatter.

### `.gitignore` content

```
*.tmp
state.json.bak.*
```

Two lines, nothing else. The project itself owns its top-level `.gitignore`;
this one is scoped to `./.cws/` only.

### Worked 9-file diff

Fresh repo `~/projects/color-pick/` with `.git/`, `package.json`, no `.cws/`.
User: `init cws for color-picker`.

```
A  .cws/.gitignore
A  .cws/00-account-setup.md
A  .cws/01-idea.md
A  .cws/02a-listing.md
A  .cws/02b-build.md
A  .cws/03-launch.md
A  .cws/04-promote.md
A  .cws/05-monetize.md
A  .cws/learnings.md
A  .cws/.resync.log
A  .cws/state.json
```

(11 files, because `.gitignore` and `.resync.log` count. The "9 stage stubs"
phrasing in the voice line refers to the seven 0–5 stage files plus
`learnings.md` and `.resync.log` — the user-meaningful artifacts. The
gitignore and state.json are infrastructure.)

---

## Phase 4 — Speak

One short line. **No file-creation log. No file-by-file checklist. No
banner.** The user sees the scaffold landed because the next message is
the route, not a description of the scaffold.

### Voice cookbook

| Situation | Line |
|---|---|
| Terse mode (`EXPLAIN_LEVEL: terse`) | `Scaffold ready for <SLUG>.` |
| Default, no seed | `Scaffold ready for <SLUG>: state.json + 9 stage stubs + learnings + log.` |
| Default, seed captured | `Scaffold ready for <SLUG>: state.json + 9 stage stubs + learnings + log. Seed: <one-line>.` |
| Migration ran | `Migrated state.json from schema <old> to <new>. Old file archived to .cws/state.json.bak.<iso>.` |
| Already-current schema | `./.cws/ already initialized at schema <current>. Nothing to do here.` |
| Refused (Phase 0) | `Refusing: <reason>. <remediation>.` |
| Refused (URL in seed) | `Scaffold ready for <SLUG>. URL ignored — paste the donor URL inside /cws-idea where it belongs.` |
| Refused (code block in seed) | `Scaffold ready for <SLUG>. Code block ignored — bring it into /cws-build.` |

The line stays under 200 characters in every case. No exclamation marks.
No emoji. No checkmarks. No "Done!" or "Successfully created" — those are
banner-shaped and forbidden.

---

## Skill Routing Footer

Fresh scaffold:

```
Next: /cws-idea
Why: Stage 0 (proxy + antidetect + Google account) is the first hard gate;
cws-idea walks it before any keyword work.
```

Schema migration ran instead of a fresh scaffold:

```
Next: /cws-sprint
Why: state.json migrated to schema <new>; sprint will read it and pick up where
you left off.
```

Already-current schema (Branch B in Phase 1):

```
Next: /cws-sprint
Why: scaffold is already done; sprint will diagnose where you are.
```

Refusal (Phase 0):

```
Next: stop — fix the directory issue, then re-run /cws-init.
```

---

## Iron rules — Mechanical, never asked

1. **Never overwrite an existing `.cws/` at the current schema.** Abort.
2. **Never write outside `./.cws/`.** No top-level project files.
3. **Never decide an idea.** Capture a one-liner if one was typed. That is the
   limit. The cws-idea skill owns the idea brainstorm.
4. **Never run a stage.** This skill scaffolds and routes. Per-stage skills
   own per-stage work.
5. **Never print a file-by-file creation log.** One summary line is enough.
6. **Always archive before migration.** `state.json.bak.<iso>` first, then
   overwrite. Never destructive without backup.
7. **Always preserve `history` across migration.** Append, never replace.
8. **Always run migrations one schema step at a time.** Never jump versions.
9. **Always write `state.json` last.** It is the gate that signals "scaffold
   complete" to every other skill.
10. **Never re-touch `last_updated` on a no-op invocation.** That would lie
    to cws-retro about activity.

---

## When NOT to use cws-init

- **Subtree clone of a larger repo.** If the user `git clone`d a repo that
  already has `.cws/` inside a subdirectory, do not init at the top level
  — `cd` into the subdirectory and let the existing scaffold serve.
- **Monorepo siblings.** If the user runs `init cws` at a monorepo root
  intending to launch several extensions from one repo, refuse politely:
  cws-studio assumes one `.cws/` per project root. Recommend a per-package
  directory.
- **`/tmp` throwaways at top level.** Refuse (Phase 0). If they truly want
  throwaway, scaffold under `/tmp/cws-<name>/` and re-run from there.
- **Just to look at an existing project.** If the user only wants to see
  where the launch is, route to `/cws-sprint`. cws-init does not need to
  run again.
- **Mid-launch repair.** State got corrupted or an artifact deleted? Use
  `/cws-resync`, not cws-init — cws-init refuses to overwrite a
  current-schema state and would not help anyway.
- **CI/CD agent setup.** This skill is interactive. If you need a
  non-interactive scaffolding step in a CI job, write the same files
  directly from a small shell or Python wrapper — there is no
  `bin/cws-init` helper today (the skill itself is the canonical path).

---

## Companion skills

| Skill | When |
|---|---|
| `cws-sprint` | Always the next move after init, unless the user has been told to run `/cws-idea` directly. |
| `cws-idea` | If the user already has a seed and wants Stage 0 to begin immediately. |
| `cws-resync` | If a mid-launch artifact got corrupted; not for fresh scaffolds. |
| `cws-learn` | Not relevant during init — no learnings exist yet at scaffold time. |

cws-init is **upstream** of every per-stage skill and **downstream** of
nothing. It does not call other skills; it routes. The skill graph rooted
at cws-init is: init → sprint → idea → (challenge) → package + build →
launch → promote → monetize, with retro and learn running at any cadence
once artifacts exist.

---

## Worked example — fresh repo

```bash
$ cd ~/projects/color-pick   # exists, has .git, has package.json, no .cws/
$ # user: "init cws for color-picker"
```

Preamble echoes:

```
SLUG: color-pick
BRANCH: main
CWD: /Users/devall/projects/color-pick
CWS_STATE: missing
```

Phase 0: `CWD` is not in the refusal list, the dir has `.git` and
`package.json` (clearly a project root), the name is descriptive. No D1.
No warnings.

Phase 1: `CWS_STATE: missing` → fresh branch. No D2.

Phase 2: invoking message contains "for color-picker"; sentence count 1,
no URL, no code fence, not a meta-reply. Candidate `color-picker`. Trimmed,
under 120 chars, write to `01-idea.md`.

Phase 3: dir name `color-pick` is descriptive (not on the generic list);
no D3 needed. Scaffold proceeds: mkdir, .gitignore, stubs in order,
state.json last. `project_name` set to `color-pick`.

Phase 4 voice:

> `Scaffold ready for color-pick: state.json + 9 stage stubs + learnings + log. Seed: color-picker.`

Skill routing footer:

```
Next: /cws-idea
Why: Stage 0 (proxy + antidetect + Google account) is the first hard gate;
cws-idea walks it before any keyword work.
```

Total visible output: 4 lines (preamble's 4-5 echoed values are mechanical;
the user-facing message is the scaffold line + the next/why pair).

---

## Worked example — schema migration

```bash
$ cd ~/projects/page-mute   # has .cws/ from 3 months ago
$ # user: "init cws"
```

Preamble echoes:

```
SLUG: page-mute
BRANCH: master
CWD: /Users/devall/projects/page-mute
CWS_STATE: present
SCHEMA: 1
```

Current schema is 2 (hypothetical). Phase 1 Branch C → D2 fires.

User picks A (migrate). Run migration registry:
- Load state.json (schema 1) into dict.
- Copy to backup `./.cws/state.json.bak.2026-05-24T18-22-04Z`.
- Apply `_migrate_v1_to_v2(state)` — adds `proxy_residential: null` and
  `proxy_country: null` to `account_setup`.
- Set `state["schema"] = 2`.
- Append history entry: `{"ts": "<now>", "stage": "cws-init", "event": "migrated", "from": 1, "to": 2}`.
- Update `last_updated`.
- Write atomically.

Phase 2: skip (no seed capture on migration — the project already has a
populated `01-idea.md`).

Phase 3: skip (artifacts already exist).

Phase 4 voice:

> `Migrated state.json from schema 1 to 2. Old file archived to .cws/state.json.bak.2026-05-24T18-22-04Z.`

Skill routing footer:

```
Next: /cws-sprint
Why: state.json migrated to schema 2; sprint will read it and pick up where
you left off.
```

---

## State.json schema (canonical)

Field-by-field. This is the schema 1 reference; future schemas extend by
adding fields, never by changing types in place.

### Top-level

| Field | Type | Default | Owner | Notes |
|---|---|---|---|---|
| `schema` | int | `1` | cws-init | Bumped only by migration. |
| `project_name` | string | dir name, or D3 value | cws-init | Cap 60 chars. |
| `current_stage` | string \| null | `null` | per-stage skills | One of: `account-setup`, `idea`, `package`, `build`, `launch`, `promote`, `monetize`. |
| `gates_passed` | string[] | `[]` | per-stage skills | Append-only. Order matches pipeline order. |
| `account_setup` | object | see below | cws-idea (Stage 0) | Owns Stage 0 state. |
| `extension` | object | see below | cws-package, cws-build, cws-launch | Shared. |
| `idea` | object | `{}` | cws-idea (Stage 1) | Populated incrementally. |
| `monetization` | object | `{"enabled": false}` | cws-monetize | Reads as gate. |
| `history` | object[] | one entry | every skill | Append-only timeline. |
| `last_updated` | string (ISO-8601 UTC) | now | every writer | Bumped on every state write. |

### `account_setup`

| Field | Type | Default | Notes |
|---|---|---|---|
| `proxy_provider` | string \| null | `null` | e.g. `proxy6`, `iproyal`, `oxylabs`. |
| `proxy_id_in_dolphin` | string \| null | `null` | Dolphin Anty's internal proxy ID. |
| `proxy_country` | string \| null | `null` | ISO-3166 alpha-2. |
| `proxy_validated` | bool | `false` | True once Dolphin's "check" passes. |
| `proxy_residential` | bool \| null | `null` | True if ASN check confirms residential. |
| `dolphin_profile_id` | string \| null | `null` | UUID from Dolphin Anty. |
| `google_account` | string \| null | `null` | Email; never the password. |

### `extension`

| Field | Type | Default | Notes |
|---|---|---|---|
| `id` | string \| null | `null` | 32-char extension ID from CWS. |
| `draft_uploaded` | bool | `false` | True once first zip uploaded. |
| `submitted_for_review` | bool | `false` | True once "Submit" pressed. |
| `moderation_status` | string \| null | `null` | `pending`, `approved`, `rejected`, `rejected-fixable`. |
| `store_url` | string \| null | `null` | Public CWS URL once approved. |

### `idea`

Populated incrementally by cws-idea. Fields include `name_keyword`,
`us_volume_exact`, `kd_zone` (green/yellow/orange/red), `softness_pct`,
`donor_url`, `function_one_liner`. Schema does not enforce these — cws-idea
owns the contract.

### `monetization`

| Field | Type | Default | Notes |
|---|---|---|---|
| `enabled` | bool | `false` | Gate. cws-monetize is the only writer. |

### `history`

Append-only list of events. Each entry:

```json
{ "ts": "<iso8601 utc>", "stage": "<skill-name>", "event": "<verb>", "...": "..." }
```

The `event` is a short verb: `scaffolded`, `migrated`, `gate-passed`,
`refused`, `submitted`, `monetization-enabled`. Free-form extra fields are
allowed (`from`, `to`, `reason`, `keyword`, etc.).

### `last_updated`

ISO-8601 UTC with `Z` suffix. Every state write updates it. cws-init does
**not** touch `last_updated` on a no-op invocation (Branch B in Phase 1).

---

## Edge cases

| Situation | Behavior |
|---|---|
| User runs `init cws` from inside `./.cws/` itself | Refuse: "You're inside the scaffold dir already. `cd ..` and re-run." |
| `./.cws/` exists but state.json is missing (mid-write crash) | Warn: "Found `./.cws/` without state.json — likely a crashed scaffold. Backing up the partial dir to `./.cws.crashed.<iso>` and rescaffolding." Then proceed. |
| `./.cws/state.json` exists but is invalid JSON | Refuse: "state.json failed to parse. Run `/cws-resync` to triage — cws-init won't overwrite a damaged file blindly." |
| `./.cws/` is a symlink | Warn: "`./.cws/` is a symlink to `<target>`. Operating on the resolved path. If that's wrong, fix the symlink first." Proceed. |
| `./.cws/` is owned by a different user | Refuse: "`./.cws/` is owned by `<user>`; this shell can't write to it. Fix ownership or `cd` elsewhere." |
| Disk full mid-scaffold | Half-written files: any `.tmp` files cleaned up by atomic-rename pattern. Partial state detectable on next run (state.json absent but stubs present). |
| Filesystem is case-insensitive (default macOS APFS) | Stub filenames use lowercase — no collision risk, but warn if `./.cws/State.json` exists from a prior case-different write. |
| User's shell is fish / zsh / bash | All shell snippets in this skill are POSIX. No fish-isms, no Bash 4+ features. |
| Repo is a git submodule | Proceed normally. `.gitignore` rule applies inside the submodule. |
| Repo is a bare git repo (`.git/` is the working dir) | Refuse: "This looks like a bare git repo — no working tree. Clone a normal copy and `cd` there." |
| `package.json` declares the project as a workspace member | Warn: "This is a workspace member, not a root. Confirm this is the right launch root before continuing." Proceed only if user re-asserts. |
| User passes `--reset` (or types "reset") | Archive entire `./.cws/` to `./.cws.archived.<iso>/`, then fresh-scaffold. Hard-confirm via an additional D-brief first. |

---

End of cws-init. Scaffold once, route once, leave.
