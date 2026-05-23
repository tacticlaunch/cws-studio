---
name: cws-retro
description: >-
  Post-launch metrics retrospective for a published CWS extension — pulls users,
  installs, conversion, reviews, uninstall rate, behavioral signals; compares
  them to the benchmark norms; flags regressions; writes a dated retro markdown.
  Use weekly during the 1–2 month behavioral-test window after launch, then
  monthly for the rest of the 6-month SEO horizon, or anytime the user asks
  "how's my extension doing", "did the experiment work", "is this product
  growing", "what changed last week", "retro on my extension". Closes the loop
  on the sprint — the gstack /retro equivalent.
---

# CWS Studio — retro

Post-launch metrics roll-up. Tracks the product's behavioral health, flags
regressions against benchmarks, and stamps a dated artifact under
`./.cws/retro/` so trends are visible.

## When to use

- **Weekly for the first 2 months** post-launch — Google's behavioral test
  window. Bug-driven regressions here are the most expensive.
- **Monthly thereafter through ~6 months** — SEO consolidation horizon.
- **Anytime the user asks** "how's it going", "did X help", "what changed",
  "retro on extension".
- **Before any large change** (relaunch, monetization shift, banner swap) —
  snapshot the baseline.

## What to pull

For each retro:

1. **CWS dashboard**:
   - Weekly users over time (only real extension metric in CWS GA).
   - Installs (developer dashboard → Installs & Uninstalls).
   - Per-country installs CSV (faster refresh than per-country users).
2. **Google Analytics 4 (CWS-built-in)**:
   - `first_visit` (unique listing visits) — last 7 days, last 28 days.
   - `install` events — same windows.
   - **Conversion = `install / first_visit`** with the Linux-OS-exclusion
     segment applied (FB bot filter).
3. **Internal analytics** (Amplitude / Yandex Metrica / Umami):
   - Welcome Page unique visits ≈ installs (sanity-check the CWS install
     count, which lags 5–7 days).
   - Activation events / core feature use rate.
4. **Listing front-page**:
   - Rating + reviews count, scan for new hostile reviews.
5. **State**: read `.cws/state.json` and the previous retro under
   `.cws/retro/`.

## Benchmark norms — flag if outside

- **Listing → install conversion**: 15–30% organic, 10–20% paid. Below 10%
  → red. Above 50% → likely measurement error (re-check FB bot filter).
- **Uninstall rate**: ~30% average, ≤ 15% excellent, > 40% bad (unless
  one-shot-use product with monetization).
- **Enable/disable rate**: ~10% over distance normal; 3% on a new product
  fine.
- **First organic installs**: visible 1–2 months post-launch; 10–20/day
  after 2 months is healthy.
- **Full SEO power**: emerges ~6 months in. Don't kill the product before.
- **Review rating**: should sit ≥ 4.0 after the seed wave; below means
  hate-review pile-up or real product issues.

## Output

Write `./.cws/retro/YYYY-MM-DD.md` with:

```markdown
---
retro_date: YYYY-MM-DD
stage_at_retro: cws-promote   # current stage from state.json
days_since_publish: 42
---

# Retro — YYYY-MM-DD

## Headline
<one sentence: growing / flat / shrinking, and primary driver>

## Snapshot
| Metric | Now | 7d ago | 28d ago | Trend | Benchmark |
|---|---|---|---|---|---|
| Weekly users | 1240 | 980 | 410 | ↑ 26% / week | — |
| Installs (7d) | 380 | 290 | 90 | ↑ | — |
| Conversion (bot-filtered) | 22% | 19% | 14% | ↑ | 15–30% organic |
| Uninstall rate | 27% | 28% | 24% | flat | ≤ 30% |
| Rating | 4.6 (12) | 4.6 (10) | 4.8 (5) | flat | ≥ 4.0 |

## What changed since last retro
- <bullet> (link to commit / artifact / experiment if applicable)

## Flags
- 🔴 / 🟡 / 🟢  per metric outside benchmark, with the proposed fix.

## Decisions for next week
- <ordered list>
```

Then **update `state.json`**:
- Append `{ts, stage: "cws-retro", event: "retro_done", retro_path: "<path>"}`
  to `history`.
- Optionally update a `latest_metrics` block with the snapshot row for fast
  lookup by other skills.

## What retro never does

- Doesn't push changes. Findings → user decides.
- Doesn't reset a gate. Retro is observational; gates only flip in stage
  skills.
- Doesn't auto-launch the next experiment — but it can recommend one for the
  next session.
