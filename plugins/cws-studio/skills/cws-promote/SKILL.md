---
name: cws-promote
description: >-
  Run paid promotion and early optimization for a published Chrome Web Store
  extension — paid install campaigns, analytics, reviews. Stage 4 of the CWS
  launch pipeline. Use when the user wants to buy the first users for a launched
  extension, run a Facebook / Google / Yandex Ads campaign, create ad creatives
  and copy, set up UTM tags, activate and read Google or Umami analytics,
  measure conversion-to-install, filter ad-platform bots, or motivate and seed
  reviews. Triggers on "run ads for my extension", "set up a Facebook/Google/
  Yandex campaign", "buy installs", "set up UTM tags", "check my install
  analytics", "what's my conversion to install", or "get reviews for my
  extension".
---

# CWS Studio — Stage 4: Paid promotion & optimization

After publishing, buy the first **100–300 users** to break the cold-start loop,
then let organic SEO take over. You buy paid users not to earn from them, but to
help Tier-1 users see the product in organic search.

## Core principles

1. **Break the cold-start loop** — no users → low ranking → fewer users. 100–300
   paid installs (~$30–150) fix it; don't exceed $300.
2. **Buy cheap-country installs** (CIS/Asia/Africa) — live traffic from anywhere
   boosts ranking worldwide, including Tier-1.
3. **Do it once, fast, right after launch** — ads act as social signals; don't
   delay them.
4. **Reviews matter** — seed 4–5 real reviews; route bad ratings to a private
   form, not public CWS reviews.

## What this stage produces

- A paid campaign on at least one platform (FB / Google / Yandex), ~100–300
  installs.
- UTM tags and analytics (Google Analytics / Umami) wired up.
- A review-routing widget in the UI and 4–5 seeded reviews.

## How to run it

Follow `references/promotion.md` — the full workflow: why paid ads, choosing the
platform, Facebook / Google / Yandex campaign setup, ad creatives and copy, UTM
tags, reading CWS / Google Analytics correctly (and filtering Facebook bots),
Umami analytics, the Free Desktop Software appeal, the review widget, and seeding
first reviews.

For the review-routing star widget, use `references/review-widget.html` (4–5
stars → CWS reviews; 1–3 stars → a private Google Form).

## Gate to the next stage

100–300 installs delivered, analytics readable, reviews seeded. Then stop the
paid campaign — let organic traffic build.

Next stage: **cws-monetize** (monetization & scaling), once the product holds a
search position.

## Artifacts & re-entry

This skill reads `./.cws/state.json` + `./.cws/03-launch.md` (required prior
gate: `launch`, with `extension.moderation_status: approved`) and writes
`./.cws/04-promote.md`. Follow the re-entry protocol in cws-sprint's
`pipeline-state.md` reference.

**`04-promote.md` must contain:**
- Platforms active: Facebook / Google / Yandex — for each: campaign URL,
  budget cap, daily budget, current spend, status (running / stopped /
  rejected with appeal).
- Ad creatives: paths to banner files used (square + rectangle for FB), ad
  texts (headline, primary text, description).
- Keyword lists used per platform.
- UTM tags in use (verbatim strings).
- Analytics IDs: GA4 property, Amplitude project, Yandex Metrica counter,
  Umami site — and where each is wired (Welcome Page / event protocol).
- Bot-filter segment configured in GA (Linux OS exclusion).
- Reviews seeded: count + source (friends / ProfitTask), max 1–2/day cadence.
- Conversion snapshot: `installs / first_visit` after bot filter; benchmark
  vs `15–30% organic, 10–20% paid` norms.

**On gate pass** (100–300 installs delivered, paid campaign stopped, organic
trickle visible), update `state.json`:
- `promote.platforms_active`, `promote.installs_paid_total`,
  `promote.first_organic_install_ts`, `promote.reviews_count`,
  `promote.conversion_install_pct`.
- Append `"promote"` to `gates_passed`; log `gate_passed` event.
- Set artifact frontmatter `status: complete`.
