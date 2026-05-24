# CWS Studio

[![version](https://img.shields.io/badge/version-2.2.0-blue.svg)](./CHANGELOG.md)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](./plugins/cws-studio/.claude-plugin/plugin.json)
[![repo](https://img.shields.io/badge/repo-tacticlaunch%2Fcws--studio-black.svg)](https://github.com/tacticlaunch/cws-studio)

A Claude Code plugin: an end-to-end system for launching profitable **Chrome
Web Store browser extensions** as micro-products.

It is a **gstack-style set of skills** — six pipeline-stage skills, an
orchestrator, plus a ring of companion skills for QA, recall, recovery,
adversarial review, and antidetect operations.

## Quick install

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

## Skill order to invoke

```
/cws-init  →  /cws-idea  ─┬─→ /cws-package ─┐
                          │                  ├─→ /cws-launch → /cws-promote → /cws-monetize
                          └─→ /cws-build ───┘

  routing & autopilot:   /cws-sprint (router) · /cws-autoplan (full auto) · /cws-help (catalog)
  per-stage guardrails:  /cws-challenge (adversarial) · /cws-careful (irreversible gates)
  recovery & memory:     /cws-resync (mid-launch changes) · /cws-retro (snapshots) · /cws-learn (lessons)
  antidetect ops:        /cws-dolphin (proxies + profiles)
```

## Skill catalog

LOC + D-brief counts are read straight from each `SKILL.md`. "D-briefs" =
`AskUserQuestion` decision points the skill is prepared to surface.

### Pipeline stages

| Skill | Stage | Purpose | LOC | D-briefs |
|---|---|---|---:|---:|
| [`cws-init`](./plugins/cws-studio/skills/cws-init/SKILL.md) | 0 | Scaffold `./.cws/` (state + per-stage artifact stubs) on a fresh project. | 809 | 3 |
| [`cws-idea`](./plugins/cws-studio/skills/cws-idea/SKILL.md) | 0–1 | CWS account setup + idea validation (10-step scoring workflow). | 1453 | 7 |
| [`cws-package`](./plugins/cws-studio/skills/cws-package/SKILL.md) | 2a | Listing copy — name, short/full description, SEO, spam check. | 1088 | 7 |
| [`cws-build`](./plugins/cws-studio/skills/cws-build/SKILL.md) | 2b | Build the minimal Manifest V3 extension; types; donor cloning. | 941 | 4 |
| [`cws-launch`](./plugins/cws-studio/skills/cws-launch/SKILL.md) | 3 | Banners, icons, Welcome Page, 50+ translations, publishing & moderation. | 1669 | 6 |
| [`cws-promote`](./plugins/cws-studio/skills/cws-promote/SKILL.md) | 4 | Paid install campaigns (FB / Google / Yandex), UTM, analytics, reviews. | 1266 | 5 |
| [`cws-monetize`](./plugins/cws-studio/skills/cws-monetize/SKILL.md) | 5 | Uninstall Page, monetization models, host permissions, selling the asset. | 1041 | 7 |

### Companions

| Skill | Role | Purpose | LOC | D-briefs |
|---|---|---|---:|---:|
| [`cws-sprint`](./plugins/cws-studio/skills/cws-sprint/SKILL.md) | Router | Conducts a full launch end-to-end; locates you in the pipeline and hands off to the right stage skill. | 650 | 3 |
| [`cws-autoplan`](./plugins/cws-studio/skills/cws-autoplan/SKILL.md) | Autopilot | Runs the sprint as autonomously as possible — only taste decisions surface. | 1443 | 7 |
| [`cws-help`](./plugins/cws-studio/skills/cws-help/SKILL.md) | Catalog | Prints the plugin's skill catalog + pipeline order; routes first-time users to the right entry skill. | 724 | 3 |
| [`cws-challenge`](./plugins/cws-studio/skills/cws-challenge/SKILL.md) | Adversarial | Per-stage adversarial second-opinion. Run before every irreversible commitment. | 1698 | 1 |
| [`cws-careful`](./plugins/cws-studio/skills/cws-careful/SKILL.md) | Guardrail | Pre-flight gate on irreversible actions (moderation submit, paywall enable, host permissions widen). | 1131 | 3 |
| [`cws-resync`](./plugins/cws-studio/skills/cws-resync/SKILL.md) | Recovery | Propagates a mid-launch change downstream; marks affected artifacts `superseded`, routes the re-do. | 989 | 3 |
| [`cws-retro`](./plugins/cws-studio/skills/cws-retro/SKILL.md) | Snapshot | Post-launch metrics retrospective; regression detection vs benchmark norms; dated artifacts under `.cws/retro/`. | 1054 | 6 |
| [`cws-learn`](./plugins/cws-studio/skills/cws-learn/SKILL.md) | Memory | Append-only learnings journal at `.cws/learnings.{md,jsonl}`; surfaces prior taste decisions on re-entry. | 1008 | 4 |

### Ops

| Skill | Role | Purpose | LOC | D-briefs |
|---|---|---|---:|---:|
| [`cws-dolphin`](./plugins/cws-studio/skills/cws-dolphin/SKILL.md) | Antidetect | Dolphin{anty} profile automation: create + start/stop, cookies, bulk proxy import & validation, Proxy6 autonomous purchase, residential-ASN gate. | 1068 | 5 |

> Per-skill workflow lives in each `SKILL.md` and its `references/` folder.
> This README does not duplicate those — read the file linked in the table.

## MCP servers

Both MCPs are declared in
[`plugins/cws-studio/.claude-plugin/plugin.json`](./plugins/cws-studio/.claude-plugin/plugin.json)
and auto-mount when the plugin is installed.

| MCP | Type | Used by | Notes |
|---|---|---|---|
| `dolphin-anty-docs` | HTTP, `https://docs.dolphin-anty.com/_mcp` | `cws-dolphin` | Read-only docs lookup. No auth. |
| `semrush` | HTTP, `https://mcp.semrush.com/v1/mcp` | `cws-package`, `cws-promote` | OAuth — first call triggers `/authenticate` flow; token persists per workspace. |

## State directory

The sprint is **not** held in conversation memory. Every skill reads and
writes a project-local `./.cws/` directory.

```
./.cws/
├── state.json                # canonical pipeline state (versioned schema)
├── 00-account-setup.md       # proxy + Dolphin + CWS dev account gate
├── 01-idea.md                # idea validation artifact
├── 02-package.md             # listing-copy artifact
├── 02-build.md               # extension build artifact
├── 03-launch.md              # store-assets + publishing artifact
├── 04-promote.md             # paid-install campaign artifact
├── 05-monetize.md            # monetization artifact
├── learnings.jsonl           # append-only learnings journal
├── timeline.jsonl            # append-only event log (skill enter/exit/etc.)
└── retro/                    # dated snapshots from /cws-retro
```

Schema, re-entry protocol, and the gate semantics live in
[`plugins/cws-studio/skills/cws-sprint/references/pipeline-state.md`](./plugins/cws-studio/skills/cws-sprint/references/pipeline-state.md).

## Shared CLI helpers

Every skill speaks through four `bin/` helpers (stdlib Bash + Python only).
They are auto-on-PATH while the plugin is loaded.

| Helper | Purpose |
|---|---|
| [`cws-slug`](./plugins/cws-studio/bin/cws-slug) | Emit `SLUG=`, `CWS_HOME=`, `CWS_PROJECT_DIR=` for the current repo. `eval`-ready. |
| [`cws-config`](./plugins/cws-studio/bin/cws-config) | Minimal JSON config store at `$CWS_HOME/config.json` (get / set / list). |
| [`cws-learnings-search`](./plugins/cws-studio/bin/cws-learnings-search) | Search per-project `learnings.jsonl`; `--stage`, `--grep`, `--limit`. |
| [`cws-timeline-log`](./plugins/cws-studio/bin/cws-timeline-log) | Append one JSON event line to per-project `timeline.jsonl` (injects `ts`). |
| [`cws-timeline-tail`](./plugins/cws-studio/bin/cws-timeline-tail) | Tail per-project `timeline.jsonl`; `--skill`, `--event`, `--since`, `--limit`. |

Smoke suite for all of the above + `dolphin-cli`:
[`plugins/cws-studio/tests/smoke.sh`](./plugins/cws-studio/tests/smoke.sh).

```
bash plugins/cws-studio/tests/smoke.sh
```

## Bootcamp methodology

CWS Studio's pipeline structure, scoring rubric, and listing-copy patterns
were distilled from the **Captain Builders bootcamp** (Igor Zuev / Captain
Labs) — 85 HTML lessons and 164 video transcripts across 5 modules. The raw
source materials are kept outside the plugin so the skills can be reworked
without re-extracting; see
[`~/Downloads/cws-bootcamp-transcripts/README.md`](file:///Users/devall/Downloads/cws-bootcamp-transcripts/README.md)
for the inventory.

## Replaces

This plugin supersedes the standalone `cws-extension-validator` skill — that
skill's content is now `cws-idea` (idea validation), with the rest of the
launch pipeline added as the other five stages plus companions.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).
