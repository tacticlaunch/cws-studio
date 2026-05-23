---
name: cws-sprint
description: >-
  Orchestrate a full Chrome Web Store (CWS) extension launch end to end — the
  whole micro-product sprint from idea to monetization. Use this when the user
  wants to launch a browser extension as a product and wants the entire pipeline
  (not just one stage), says things like "launch a chrome extension", "build and
  ship an extension", "run the cws sprint", "take my extension idea all the way",
  "what's the full process for a CWS product", or asks where they are in the
  launch. This skill is the conductor: it walks the six stages in order, hands
  off to the per-stage skills (cws-idea, cws-package, cws-build, cws-launch,
  cws-promote, cws-monetize), enforces the gates between them, and tracks
  progress. For a single isolated stage, the matching per-stage skill triggers
  on its own — but route through here whenever the goal is the whole launch.
---

# CWS Studio — the Sprint

Conductor for launching a **Chrome Web Store browser extension** as a profitable
micro-product. The method gets **free organic Google traffic** to the extension's
store page, converts installs into Tier-1 users, then monetizes. It is an
**SEO + product-launch operation**, not an "is this a cool app" exercise.

A sprint is **six stages**. Walk them in order, hand off to the per-stage skill,
and don't pass a gate until it's met. Each stage skill has its own detailed
references — this skill is the map and the checklist.

## Pipeline state lives in `./.cws/`

Sprints are not held in conversation memory — they live on disk. Every stage
skill reads and writes `./.cws/state.json` (pipeline status, IDs, history) and a
per-stage artifact (`./.cws/01-idea.md`, `./.cws/02a-listing.md`, etc.). This is
what makes the sprint cohesive instead of seven isolated skills: handoffs are
**files**, re-entry is **file detection**, gates are **JSON fields**.

**Before doing anything on a sprint invocation, follow the re-entry protocol in
`references/pipeline-state.md`** — locate or create `.cws/`, read `state.json`,
diagnose where the user is in the pipeline, never silently skip a gate.

If no `.cws/` exists, route to **cws-init** to scaffold, then on return show
the status block below — never dump a file-creation log. Don't ad-hoc create
the directory yourself.

## Output convention — gstack-style, NOT a file dump

Every sprint invocation prints **exactly these blocks, in this order**, and
nothing else:

```
CWS sprint status
─────────────────
Project:   <project_name>
Stage:     <human-readable current stage — "Account setup" / "Idea validation" / …>
Progress:  <bar of 7 gates>   e.g.  ●●○○○○○  account-setup → idea
Last:      <last 3 history events, oldest first, one line each>

Next:  /cws-<skill>
Why:   <one sentence — what this step does and why it's next>
```

Rules:
- **One next action**, never a menu. Pick by the table in "Proactive next-skill
  suggestion" below. Override only if the user explicitly asked for something
  else.
- **No raw file lists** ("Created 01-idea.md +8 -0"). Summarize: "Scaffold ready
  — 9 artifact stubs + state.json."
- **No raw JSON dumps**. Read state.json, render the status block.
- **No emoji / decoration** unless the user uses them first.
- When `.cws/` was just scaffolded by cws-init, the status block still applies —
  show `Stage: not started`, `Progress: ○○○○○○○`, `Next: /cws-idea`.

## Proactive next-skill suggestion

After every "where am I" answer, propose the **single best next action**:

| Situation | Suggest |
|---|---|
| `.cws/` missing | `cws-init` (scaffold first) |
| Scaffolded but `account-setup` not gated | `cws-idea` (it walks Stage 0 proxy/profile/account first) |
| Just gated `account-setup` | `cws-idea` (validate the idea) |
| Just gated `idea` | `cws-challenge` (stress-test before building) |
| Just gated `package` | `cws-build` (or `cws-challenge` first if listing is borderline) |
| Both `build` + `package` gated | `cws-launch` |
| `launch` gated, moderation `pending` | wait + `cws-retro` snapshot to baseline |
| `launch` gated, moderation `approved` | `cws-promote` (don't delay ads) |
| `promote` gated, < 3K weekly users | `cws-retro` weekly cadence |
| `promote` gated, ≥ 3K users, search consolidated | `cws-challenge` then `cws-monetize` |
| `monetize` gated | `cws-retro` monthly + queue next idea (`cws-idea`) |
| Last retro flagged regression | `cws-resync` or the relevant stage skill |

Show one suggestion plus a one-line "why". User can override.

## Taste-memory readback

Read `.cws/learnings.md` and surface the **3 most relevant prior learnings**
filtered by the current stage's tag whenever the user resumes a sprint or asks
"where am I". Catches "we said we'd avoid X next time" without the user having
to remember to run `cws-learn`.

## Core principles (every stage follows from these)

1. **Traffic comes from Google, not CWS search.** Users Google a query, land on
   a store page, install. The extension's *name* (its ranking keyword) is ~70%
   of the SEO outcome; the description ~30%. (~90% of traffic is Google search,
   ~10% CWS internal search.)
2. **Extensions win "software" queries** — `dark theme`, `color picker`. Not
   informational / commercial / entity queries.
3. **Extensions beat *sites*, not other *optimized extensions*.** Aim for a
   keyword that is software-y AND not owned by a well-optimized competitor.
4. **Small niche keywords are undervalued — the opportunity.** 500 US searches/mo
   ≈ 50K real reach (×10 other Tier-1 English, ×10 other languages).
5. **Reduce to one simple function.** Open-source prior art makes the build easy.
6. **Launch fast, monetize later.** Ship a minimal clean build, get organic
   traffic, *then* monetize (monetization stresses SEO).
7. **The brain lies to the founder.** Early "no sales" = "too few users yet".
   Haters write, happy users stay silent. ~50% of products get users, ~33% get
   subscriptions — plan to launch several.
8. **Behavioral factors decide the launch.** Google tests a new extension on
   tiny random samples; if users stay, it widens the test over **~6 months**; if
   they bounce to search, ranking dies. The launch build must be bug-free,
   simple and instantly clear; every asset must minimize friction.

## The 6-stage pipeline

| # | Stage | Skill | Gate to pass before moving on |
|---|---|---|---|
| 0 | Account setup (proxy, antidetect profile, Google account) | **cws-idea** (Stage 0 routine; uses cws-dolphin) | Proxy validated (residential ASN, country match), Dolphin profile created, dedicated Google account registered |
| 1 | Idea validation | **cws-idea** | A scored hypothesis with a winning name keyword that clears all gates (one function, volume, softness, keyword free) |
| 2a | Listing copy (name, short/full description, SEO) | **cws-package** | Name + descriptions written, spam-checked, name keyword saturated |
| 2b | Build the minimal extension | **cws-build** | Bug-free manifest v3 build, one clear function, doesn't break pages |
| 3 | Store assets, translations, publishing | **cws-launch** | Banners + icons + Welcome Page done, 50+ locales, submitted & approved |
| 4 | Paid promotion & optimization | **cws-promote** | 100–300 paid installs, analytics + reviews set up |
| 5 | Monetization & scaling | **cws-monetize** | Monetization wired once the product holds a search position |

## How to run a sprint

1. **Find out where the user is.** New idea → start at Stage 0–1. Already has X
   done → resume at the next stage. Confirm before assuming.
2. **For each stage, invoke the matching per-stage skill** and complete its
   workflow fully. Each stage skill loads its own references.
3. **Enforce the gate** before advancing. A failed Stage-1 gate means looping
   back to generate new name keywords — not pushing a doomed idea forward.
4. **Track progress** — keep a visible checklist of the six stages (use the task
   tools). Mark a stage done only when its gate is met.
5. **Stay honest about timing.** First organic traffic ~1–2 months post-launch;
   full SEO ~6 months. Recommend lining up a 2nd/3rd idea rather than waiting.

## When NOT to route through the sprint

If the user clearly wants just one stage ("score these ideas", "write my
description", "set up ads"), the per-stage skill handles it directly — no need to
spin up the whole pipeline. Use the sprint when the goal is the full launch or
the user is unsure of the order.

## Companion skills (orchestration layer)

These run alongside the six stage skills:

| Skill | Use it when |
|---|---|
| **cws-autoplan** | User wants the sprint run as autonomously as possible — only taste decisions surface. |
| **cws-challenge** | Adversarial second-opinion on a finalized stage decision (idea, listing, monetization). Run **before** every irreversible commitment. |
| **cws-careful** | Pre-flight guardrail on any irreversible action (submit to moderation, enable paywall, max host permissions on a populated extension, etc.). Required confirmation. |
| **cws-retro** | Weekly → monthly post-launch metrics retrospective; flags regressions vs benchmark norms; writes a dated artifact under `.cws/retro/`. |
| **cws-learn** | Per-launch learnings journal (`.cws/learnings.md`). Append-only. Read it before starting a new launch; append when something notable lands. |
| **cws-resync** | Propagate a mid-launch change (e.g. new name keyword, edited full description, new banner) — identifies and marks every downstream artifact as `superseded`, routes you through the re-do. |

A typical flow uses them in this rhythm: `cws-idea` → `cws-challenge` →
`cws-package` + `cws-build` → `cws-challenge` (light) → `cws-launch` →
`cws-careful` (submit) → `cws-promote` → `cws-retro` weekly → `cws-monetize` +
`cws-careful` (paywall) → `cws-retro` monthly + `cws-learn` as findings land.
