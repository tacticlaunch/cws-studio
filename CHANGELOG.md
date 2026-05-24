# Changelog

All notable changes to **CWS Studio** are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The version cut into `plugin.json` is the canonical version. Each entry below
ties back to a commit in the repo.

## [2.1.0] — 2026-05

Polish + backfill pass. Additive over 2.0.0; no breaking changes.

### Added
- **`cws-help` skill** (169 LOC). Plugin catalog + entry-point router with
  posture detection (no state → catalog mode; state present → route to
  `/cws-sprint`; topic-specific → answer + route; RU/BY Stage-0 callout).
  Total skills now 16 (was 15).
- **`tests/smoke.sh`** (324 LOC). Self-contained test suite covering `bin/`
  helpers and `dolphin-cli` regression cases (forceDelete on delete,
  minimal create payload, parser format coverage). 11/11 PASS.
- **`CROSS_REF_AUDIT.md`** under `plugins/cws-studio/`. Per-skill in/out-
  degree matrix on the companion + routing graph.
- **`README.md`** rewritten with version/license/repo badges, quick
  install, ASCII pipeline diagram, full skill catalog (pipeline /
  companions / ops tables with LOC + D-brief columns read fresh from
  disk), MCP server table, `.cws/` state layout, `bin/` helpers table,
  bootcamp methodology attribution.

### Changed — skill polish (4 underweight skills brought to full depth)
- **`cws-init`**: 186 → 808 LOC. Three D-briefs (root-ambiguous, schema-
  migration, project-name). Refusal catalog (7 forbidden paths + 3 soft
  warnings), schema-migration framework with registry pattern, seed-
  extraction rules, voice cookbook, edge cases table, two worked examples
  (fresh repo + schema migration).
- **`cws-sprint`**: 221 → 650 LOC. Three D-briefs (scaffold-or-cd, fast-
  forward, skip-the-wait). 8-question silent diagnostic battery,
  re-entry protocol, taste-memory readback, 14-row companion-suggestion
  matrix, Confusion Protocol, 5-tier staleness health metrics,
  3-persona output examples.
- **`cws-idea`**: 276 → 1453 LOC. Eight D-brief shapes (D5 occupation
  tie-break, D6 donor selection, D7 narrow/broad + Confusion). Phase 0
  deep dive with provider payment matrix + Phase 0 fail modes; Phase 1
  with Semrush calls inlined, rubric thresholds, exact artifact template;
  20 iron rules; 12-row edge-cases table; 2 worked examples.
- **`cws-autoplan`**: 345 → 1443 LOC. Full approval-gate brief + ~30
  phase-emitted briefs cataloged. 6 principles each with definition /
  example / misapplication / conflict; phase-specific play details
  (Phases 1-7); 12 examples per Mechanical / Taste / User-Challenge;
  audit-trail schema; per-phase approval gate; 15-entry hard refusals
  catalog; restore procedure; full sprint worked example on
  `color-picker-pro`; Confusion Protocol.

### Changed — reference backfills (7 files, 5 sub-agents)
- **`listing-copy.md`**: 327 → 577 LOC. 6 gaps filled or partial. Name-
  occurrence audit table (Temp Phone Number, lesson 056); Turgenev
  service-word list (3 confirmed + master-list TODO); FAQ keyword
  density rule (lessons 055-079); morphology heuristic downgraded from
  math to qualitative (lesson 079); translation count-preservation
  policy (lessons 124-166). Above-fold char count flagged TODO (not in
  transcripts).
- **`listing-examples.md`**: 84 → 209 LOC. Examples 2 + 3 full text added
  from lesson 056; Example 1 counted table linked; Examples 2/3 hand-
  counts TODO.
- **`development.md`**: +52 LOC for Chrome 114+ side-panel form factor
  (manifest snippet, background opener, marked "not in bootcamp").
- **`assets-and-publish.md`**: 534 → 682 LOC. Welcome Page 60-70%
  conversion callout (lesson 115); 10× rule promoted to main Translations
  body (lesson 115); full pre-submit mechanical checklist (lessons
  130-135).
- **`promotion.md`**: 452 → 798 LOC. 5 TODO + working-pattern stubs:
  kwork.ru workflow (transcripts cover ProfitTask only, lesson 203);
  `install_id` propagation (`uuid` → `localStorage` → `chrome.storage.
  sync` → Amplitude); 1000-install milestone benchmark table; second-
  platform unlock gate (4 conditions); negative-keyword starter lists
  for 7 donor categories.
- **`monetization-scaling.md`**: 272 → 545 LOC. 6 gaps: paywall
  conversion bands per tier; card-first vs trial split; grandfathering
  policy; refund/chargeback benchmarks; ExtNet pricing verified (the
  "8% fee" was actually Paywall, not ExtNet — fixed; ExtNet still TODO);
  Tier-1 allowlist enumerated from lesson 182.

### Changed — `cws-challenge`
- Adds **Phase 2.5 — cross-stage drift checks** (1343 → 1698 LOC). Seven
  drift checks: name-keyword drift, donor URL + freshness, permission
  drift, locale set drift, moderation status drift, monetization drift,
  recent learnings drift. Each with detection bash, fail criteria,
  remediation, severity (HARD red / WEAK PASS yellow). Phase 3 verdict
  folds drift findings; Phase 4 schema gains `drift_red_count`,
  `drift_yellow_count`, `## Drift findings` section.

### Fixed
- **`shared/X.md` references resolve correctly.** 65 references across 16
  `SKILL.md` rewritten from `shared/X.md` to `../../shared/X.md` so they
  resolve from `skills/cws-<X>/SKILL.md` up to `plugins/cws-studio/
  shared/`. Surfaced by the CROSS_REF_AUDIT pass.
- **`monetization-scaling.md` ExtNet vs Paywall fee misattribution.** The
  "8% fee" was Paywall's commission (lesson 243 line 953), not ExtNet's.
  Fixed in the backfill.

### Commits
- `(this release)` Wave 2 polish + backfill (v2.1.0)

## [2.0.0] — 2026-05

Major rewrite: every skill on the gstack pattern.

### Changed
- **Full gstack-pattern rewrite of all 16 skills.** Each `SKILL.md` now ships
  the same structure: executable preamble, sequential phases, `### D<N>`
  decision briefs with `AskUserQuestion` payload templates, operator voice,
  and a single-recommendation routing footer.
- Skill prose grew from ~1.8K lines (1.3.0) to ~13.6K lines across the 16
  skills (cws-autoplan, cws-build, cws-careful, cws-challenge, cws-dolphin,
  cws-help, cws-idea, cws-init, cws-launch, cws-learn, cws-monetize,
  cws-package, cws-promote, cws-resync, cws-retro, cws-sprint). Total skill
  LOC ≈ 14.4K.
- Em-dash policy reconciled across the catalog.
- Mojibake from prior copy-paste passes scrubbed.

### Commits
- `64029fc` Full gstack-pattern rewrite of all 16 skills (v2.0.0)

## [1.4.0] — 2026-05

### Added
- **`bin/` helpers** — `cws-slug`, `cws-config`, `cws-learnings-search`,
  `cws-timeline-log`. Shared CLI surface used by every skill for project
  identity, per-project config, learnings recall, and timeline append.
- **`shared/` canon** — `preamble.md`, `askuserquestion-format.md`,
  `voice.md`, `skill-routing.md`. Single source of truth for skill prose
  conventions.
- **cws-sprint / cws-idea / cws-autoplan rewritten** under the gstack pattern
  ahead of the full 2.0.0 sweep.

### Fixed
- **Author/owner format** corrected per the Claude Code plugin spec.

### Commits
- `e05bc86` Fix author/owner format per Claude Code plugin spec
- `5885356` Rewrite skills under gstack pattern: preamble, AskUserQuestion D<N>,
  voice, single next-move

## [1.3.0] — 2026-05

### Added
- **Sprint UX refactor.** gstack-style status block at every skill entry,
  single next-action footer, no raw file dumps in chat.
- **cws-init scaffold** now writes `00-account-setup.md` and an
  `account_setup{}` block in `state.json` so the proxy/reliability gate is
  visible from project birth.
- **Pipeline-state schema bumped** to accommodate the account-setup gate.

### Commits
- `d68009c` Sprint UX: gstack-style status block, single next-action, no file
  dumps
- `6fd3229` Wire account-setup gate (proxy reliability) into the sprint cycle

## [1.2.0] — 2026-04

### Added
- **Semrush MCP wired** into the plugin manifest for keyword research inside
  cws-package.
- **Bulk proxy import** (`dolphin-cli bulk-add-proxies`) — parses four shapes
  (`host:port:user:pass`, `user:pass@host:port`, `scheme://user:pass@host:port`,
  `host:port`) with a `--dry-run` and a `--strict` mode.
- **`check-proxy`** with hosting-ASN detection — flags AWS / DigitalOcean /
  OVH / Hetzner / Linode / Vultr / GCP / Azure / Oracle / Alibaba / Tencent /
  Contabo / Scaleway / Cloudflare / DataCamp / M247 / Psychz as non-residential.
- **`proxies-suggest`** — curated provider catalog (Space Proxy, Proxy6,
  Proxyline, Proxy-Sale, iProxy.online, Smartproxy/Decodo) printed without
  network access.
- **`proxy6-buy`** — autonomous Proxy6 purchase flow (price check → buy →
  auto-import into Dolphin). Gated behind `PROXY6_API_KEY` and `--yes`.
- **Account-setup reliability gate** surfaced through the sprint cycle.

### Commits
- `50615a5` Add Semrush MCP + bulk proxy import to cws-dolphin
- `71ed1cf` Add proxy provider catalog + Proxy6 auto-buy to cws-dolphin

## [1.1.1] — 2026-04  *(internal)*

### Fixed
- **`dolphin-cli create` payload minimized** — emits only
  `useragent: {mode: "manual", value: ...}` and drops the bloated mode-objects
  (cpu / memory / audio / webgl / canvas / etc.) that triggered Dolphin's
  *"Undefined array key mode"* 500s.
- **`dolphin-cli delete`** now posts `{forceDelete: true}` in the body
  (previously the cloud API silently ignored the request without it).

### Commits
- `fd9e161` Fix cws-dolphin CLI create + delete payloads

## [1.1.0] — 2026-04

### Added
- **`cws-dolphin` skill** (the 15th) — Dolphin{anty} antidetect profile
  automation: create / start / stop / cookies + proxy lifecycle via the cloud
  + local agent REST APIs. Ships `dolphin-cli.py` (stdlib-only Python).
- **`dolphin-anty-docs` MCP** wired into the plugin manifest.

### Commits
- `57e62e1` Add cws-dolphin skill (Dolphin{anty} API automation) + wire docs MCP

## [1.0.1] — 2026-03  *(internal)*

### Added
- **`cws-init` skill** (the 14th) — scaffolds `./.cws/` on a fresh project.
- **Proactive Suggestions** convention added to skill front-matter.
- **Taste Memory readback** — skills surface prior taste decisions on
  re-entry instead of re-asking.

### Commits
- `28336e6` Add cws-init skill + git install instructions + sprint orchestration

## [1.0.0] — 2026-03

### Added
- **Initial CWS Studio plugin** — 13 skills, gstack-style pipeline.
  Pipeline stages (`cws-idea`, `cws-package`, `cws-build`, `cws-launch`,
  `cws-promote`, `cws-monetize`) plus the orchestrator (`cws-sprint`) and
  companions (`cws-autoplan`, `cws-careful`, `cws-challenge`, `cws-resync`,
  `cws-retro`, `cws-learn`).

### Commits
- `512b550` Initial commit: CWS Studio plugin (13 skills, gstack-style
  pipeline)

[2.1.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v2.1.0
[2.0.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v2.0.0
[1.4.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.4.0
[1.3.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.3.0
[1.2.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.2.0
[1.1.1]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.1.1
[1.1.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.1.0
[1.0.1]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.0.1
[1.0.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.0.0
