# Changelog

All notable changes to **CWS Studio** are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The version cut into `plugin.json` is the canonical version. Each entry below
ties back to a commit in the repo.

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

[2.0.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v2.0.0
[1.4.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.4.0
[1.3.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.3.0
[1.2.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.2.0
[1.1.1]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.1.1
[1.1.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.1.0
[1.0.1]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.0.1
[1.0.0]: https://github.com/tacticlaunch/cws-studio/releases/tag/v1.0.0
