---
name: cws-monetize
description: >-
  Monetize and scale a growing Chrome Web Store extension — paywall, ads,
  traffic resale, email community, selling the product, plus the Uninstall Page
  and maximum host permissions. Stage 5 of the CWS launch pipeline. Use when the
  user wants to add monetization to an extension (subscriptions / in-app
  purchases via a paywall, banner ads, search affiliate, traffic resale, an
  email community), decide when and how aggressively to monetize, add an
  Uninstall Page to collect removal feedback, lock in maximum host permissions
  early, add a function that justifies all-sites access, or sell the extension.
  Triggers on "how do I monetize my extension", "add a paywall", "set up an
  uninstall page", "host permissions", "sell my extension", or "when should I
  add monetization".
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
# CWS Studio — Stage 5: Monetization & scaling

Post-launch: collect uninstall feedback, wire monetization once the product
holds a search position, lock in host permissions, and optionally sell.

## Core principles

1. **Monetize later, not at launch** — monetization stresses SEO. Secure a
   search position first (minimum 3–4K users; ideally tens of thousands).
2. **In-app purchases convert best** — far better per user than ads or resale.
3. **Monetization is systematic experiments**, not a recipe — the biggest lever
   is the billing cycle, then trials, then price.
4. **Roll out gradually** — by geo / % / new users only — to avoid a behavioral-
   factor crash.

## What this stage produces

- An Uninstall Page collecting removal reasons.
- Monetization wired (paywall / ads / resale / community / sale).
- Maximum host permissions locked in early, justified by a real all-sites
  function.

## How to run it

Follow `references/monetization-scaling.md` — the full workflow: the Uninstall
Page, when to add monetization, monetization as systematic experiments (billing
cycle / trials / price), the monetization models (subscription, banner ads,
search affiliate, traffic resale, email community, selling the product), locking
in maximum host permissions early, and adding a function that needs all-sites
access.

## After this stage

The launch is complete. Honest expectations: ~50% of products get users, ~33%
get subscriptions, and full SEO emerges over ~6 months. Recommend lining up the
next idea (back to **cws-idea**) rather than waiting on one product.

## Artifacts & re-entry

This skill reads `./.cws/state.json` (required prior gate: `promote`, with
weekly users ≥ 3,000–4,000) and writes `./.cws/05-monetize.md`. Follow the
re-entry protocol in cws-sprint's `pipeline-state.md` reference.

**`05-monetize.md` must contain:**
- Uninstall Page URL + Google Form ID.
- Maximum host permissions added (`<all_urls>`) — and the justifying function
  (on-page artifact / widget on every site).
- Monetization model(s) chosen: subscription (Paywall) / banner ads / search
  affiliate / traffic resale / community / sale-of-product.
- For Paywall: provider, billing-cycle composition (weekly/monthly/yearly
  mix), trial config (time-/action-/none), card-first y/n, geo-localized
  pricing per Tier, currency.
- Rollout plan: which Tier first, % of users, new-vs-existing scope, grand-
  fathering (keep older users free?).
- Weekly users at enable.
- Experiment log: each variant, sample size (cohort of 300–500 viewers
  minimum), conversion result, what changed.

**On gate pass** (monetization live, behavioral-factor dip ≤ 2 positions
recovered or accepted), update `state.json`:
- `monetization.enabled: true`,
  `monetization.weekly_users_at_enable`,
  `monetization.paywall_url`,
  `monetization.billing_cycles`,
  `monetization.rollout_geo`,
  `monetization.grandfathered: true|false`.
- Append `"monetize"` to `gates_passed`; log `gate_passed` event.
- Set artifact frontmatter `status: complete`.

The launch is then **complete** — run `cws-retro` periodically (weekly →
monthly) to track behavioral / conversion metrics over the 6-month SEO horizon.
