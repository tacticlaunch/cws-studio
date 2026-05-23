---
name: cws-init
description: >-
  Scaffold a fresh CWS launch project — create the `./.cws/` state directory,
  write a starter `state.json`, drop empty per-stage artifact templates, and
  optionally seed a project name + idea description. Use at the very start of a
  new extension launch, or when the user is in a directory that has no `.cws/`
  yet and is asking the sprint to begin. Triggers on "start a new launch", "set
  up a cws project", "init cws", "new extension", "begin sprint here",
  "initialize the pipeline". Also use to upgrade an old state.json (schema
  migration) — detects the prior schema, rewrites it, preserves data.
---

# CWS Studio — init

Project scaffolder. Creates the `./.cws/` skeleton so every other skill has a
known place to read/write.

## When to use

- **Fresh project**: a new directory with no `.cws/`, user wants to start.
- **Existing repo, no `.cws/`**: user has been working ad-hoc and now wants
  to formalize the launch state.
- **Schema upgrade**: an older `state.json` exists (`schema < current`) —
  this skill migrates it, preserves data, never destructive.

## What it creates

```
./.cws/
  state.json                 # schema:1, current_stage:null, gates_passed:[]
  01-idea.md                 # frontmatter only, status:draft
  02a-listing.md             # frontmatter only, status:draft
  02b-build.md               # frontmatter only, status:draft
  03-launch.md               # frontmatter only, status:draft
  04-promote.md              # frontmatter only, status:draft
  05-monetize.md             # frontmatter only, status:draft
  challenges/                # empty
  retro/                     # empty
  learnings.md               # frontmatter only
  .resync.log                # empty
  .gitignore                 # ignore tmp files; keep artifacts tracked
```

## Steps

1. **Find project root.** Ask user if uncertain (cwd? git toplevel? a parent
   dir?). Default to cwd. Refuse if cwd is `~` or `/`.
2. **Detect existing `.cws/`.** If present:
   - Read `state.json`. If `schema` matches current, **abort** with the
     status; route the user to `cws-sprint` to see where they are.
   - If `schema < current`, **migrate**: load all keys, write under new
     schema, preserve `history`, archive the old file to
     `.cws/state.json.bak.<timestamp>`.
3. **Create the directory tree** above.
4. **Seed `state.json`** with:
   ```json
   {
     "schema": 1,
     "project_name": "<from user or dir name>",
     "current_stage": null,
     "gates_passed": [],
     "extension": { "id": null, "draft_uploaded": false,
                    "submitted_for_review": false,
                    "moderation_status": null, "store_url": null },
     "idea": {},
     "monetization": { "enabled": false },
     "history": [
       { "ts": "<iso8601 utc>", "stage": "cws-init", "event": "scaffolded" }
     ],
     "last_updated": "<iso8601 utc>"
   }
   ```
5. **Write artifact stubs** — each gets the standard frontmatter (`stage`,
   `status: draft`, `created`, `updated`) and a one-line `TODO` comment
   pointing to its stage skill.
6. **Optionally collect seed info** — if the user typed a one-liner idea
   description, write it into `01-idea.md` under a `## Seed` section so
   `cws-idea` picks it up on entry.
7. **End by routing**: tell the user to invoke `cws-sprint` (overview),
   `cws-idea` (begin Stage 1), or `cws-autoplan` (run autonomously).

## .cws/.gitignore

```gitignore
# committed: state.json, *.md, challenges/, retro/, learnings.md
# ignored:
*.tmp
state.json.bak.*
```

State.json and artifacts **should** be committed — they are the audit trail.
Only backups and tmp files are ignored.

## What init never does

- Doesn't overwrite an existing `.cws/` of the same schema.
- Doesn't decide an idea — only records what the user gave.
- Doesn't run any stage. It scaffolds and routes.
