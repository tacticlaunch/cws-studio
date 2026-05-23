---
name: cws-resync
description: >-
  Propagate a mid-launch change across all downstream stages — when something
  upstream changes (name keyword, full description, banner, paywall config),
  this skill identifies every artifact and downstream file that depends on it,
  marks them `superseded`, and walks you through the re-do. Use after a
  significant edit to listing copy, name, banners, icons, build, or
  monetization config. Triggers on "I changed X, what else do I need to
  update", "resync my listing", "propagate this rename", "I updated the banner
  — what else", "make everything consistent again". Inspired by gstack
  /document-release.
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
# CWS Studio — resync

When you change something material mid-launch, downstream artifacts go stale.
This skill enforces consistency.

## When to use

- Changed the **name keyword** → listing copy + Welcome Page + banners + ad
  copy + translations all need a refresh.
- Edited the **full description** → all 50+ locale translations are stale;
  Turgenev re-check required; CWS draft needs re-upload.
- Replaced a **banner or icon** → CWS draft needs re-upload; ad creatives
  may need rebuild.
- Changed **paywall config** → monetization artifact rewrites; rollout log
  updates.
- Changed **build / manifest** (e.g. added a permission) → moderation
  permission justifications need re-write; behavioral risk of permission
  dialog reassessed.

## How to run

1. **Identify the change** — what artifact / value changed, and what was
   the old vs new value?
2. **Compute the impact set** from the dependency map (below). For each
   downstream item, decide: re-do entirely, edit, or leave (the user may
   override).
3. **Mark downstream artifacts `superseded`** in their frontmatter so the
   stage skills know to resume them.
4. **Append a resync entry** to `./.cws/.resync.log`:
   ```
   2026-05-27T10:00Z  cws-package.name  "color picker" → "color code picker"
     superseded: 03-launch.md (banners, Welcome Page, locales)
     superseded: 04-promote.md (ad copy, UTM)
     action: rerun cws-launch banners + locales, rerun cws-promote ad copy
   ```
5. **Route the user** to the first stage that needs re-doing, in order.
6. **Optionally invoke `cws-careful`** if the resync touches an
   irreversible step (re-submit for moderation, re-deploy paywall).

## Dependency map

```
NAME KEYWORD (cws-idea)
  └→ listing-copy.md   (rewrite name occurrences, recheck 8–10 floor)
  └→ Welcome Page      (text mentioning the name)
  └→ banners           (caption may include the name)
  └→ ad copy (FB/Google/Yandex)
  └→ all 50+ locale name fields
  └→ Turgenev recheck

FULL DESCRIPTION (cws-package)
  └→ all 50+ locale full descriptions (Localizer re-translate)
  └→ Turgenev recheck (name + short + full as one paste)
  └→ CWS draft re-upload  (paste per-locale)
  └→ moderation re-submit (warn — re-scrutiny)

BANNER / ICON (cws-launch)
  └→ CWS draft re-upload
  └→ FB ad rectangular creative  (consider rebuilding to match)
  └→ Welcome Page screenshot composition  (if banner shows the UI)

BUILD / MANIFEST (cws-build)
  └→ moderation permission justifications  (rewrite per added permission)
  └→ host-permissions risk reassessment    (warn — user-loss dialog)
  └→ minification (re-run after code change)
  └→ dogfood test (re-do 1–2 days)
  └→ CWS draft re-upload

PAYWALL CONFIG (cws-monetize)
  └→ rollout log (append change)
  └→ history entry  (paywall_changed)
  └→ if billing cycle composition changed: invalidate prior experiment
    cohort; start a new ≥ 300-viewer cohort before drawing conclusions
```

## Output

After running, show the user:

- The **impact set** as a checklist.
- For each item: status (`pending` / `done` / `skipped-by-user`).
- The **next concrete action** (which stage to invoke next).
- Whether `cws-careful` is needed before any of the downstream actions.

## What resync never does

- Doesn't auto-rewrite the downstream artifacts itself — it identifies
  what needs work and routes. Each downstream stage skill does the
  actual work (so its own checks run).
- Doesn't auto-submit anything to CWS.
- Doesn't delete superseded content — it stays in the artifact under a
  `## Superseded by resync on YYYY-MM-DD` section for audit.
