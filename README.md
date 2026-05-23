# CWS Studio

A Claude Code plugin: an end-to-end system for launching profitable **Chrome Web
Store browser extensions** as micro-products.

It is a **gstack-style set of skills** — six pipeline-stage skills plus a
`/cws-sprint` orchestrator that runs the whole launch.

## Skills

### Pipeline (six stages)

| Skill | Stage | What it does |
|---|---|---|
| `cws-sprint` | — | Orchestrator. Walks all six stages, enforces gates, tracks progress in `.cws/state.json`. |
| `cws-idea` | 0–1 | CWS account setup + idea validation (10-step scoring workflow). |
| `cws-package` | 2a | Listing copy — name, short/full description, SEO, spam check. |
| `cws-build` | 2b | Build the minimal manifest v3 extension; extension types; cloning donors. |
| `cws-launch` | 3 | Banners, icons, Welcome Page, 50+ translations, publishing & moderation. |
| `cws-promote` | 4 | Paid install campaigns (FB/Google/Yandex), UTM, analytics, reviews. |
| `cws-monetize` | 5 | Uninstall Page, monetization models, host permissions, selling. |

### Companions (orchestration layer)

| Skill | What it does |
|---|---|
| `cws-init` | Scaffold `./.cws/` skeleton in a fresh project (state.json + artifact stubs). |
| `cws-autoplan` | Run the sprint as autonomously as possible — only taste decisions surface. |
| `cws-challenge` | Adversarial second-opinion on a finalized stage decision. Run before every irreversible commitment. |
| `cws-careful` | Pre-flight guardrail on irreversible actions (submit moderation, enable paywall, expand host permissions). Required confirmation. |
| `cws-retro` | Post-launch metrics retrospective; flags regressions vs benchmark norms; writes dated artifacts under `.cws/retro/`. |
| `cws-learn` | Append-only learnings journal at `.cws/learnings.md`. |
| `cws-resync` | Propagate a mid-launch change across downstream stages — marks affected artifacts `superseded`, routes the re-do. |

Each stage skill has a `references/` folder with the detailed workflow and
reusable artifacts (`cws-locale-uploader.js`, `review-widget.html`, the Semrush
playbook, the scoring rubric, real listing examples).

### Pipeline state lives on disk

The sprint is **not** held in conversation memory — every skill reads and
writes `./.cws/state.json` and per-stage artifacts (`./.cws/01-idea.md`, etc.).
Re-entry, idempotent reruns, gates and handoffs all flow through these files.
Schema and the re-entry protocol live in
`plugins/cws-studio/skills/cws-sprint/references/pipeline-state.md`.

## Install

This directory is a Claude Code marketplace. From any Claude Code session:

From the GitHub repo (requires GitHub auth in Claude Code):

```
/plugin marketplace add tacticlaunch/cws-studio
/plugin install cws-studio@cws-studio
```

Or from a local clone:

```
/plugin marketplace add ~/Projects/orgs/TacticLaunch/cws-studio
/plugin install cws-studio@cws-studio
```

Then invoke a stage directly (`/cws-idea`, `/cws-package`, …) or run the whole
launch with `/cws-sprint`. The skills also trigger automatically from natural
requests ("is this a good extension idea", "write my extension description",
"publish to Chrome Web Store", etc.).

## Replaces

This plugin supersedes the standalone `cws-extension-validator` skill — that
skill's content is now `cws-idea` (idea validation), with the rest of the
launch pipeline added as the other five stages.
