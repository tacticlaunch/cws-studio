---
name: cws-challenge
description: >-
  Adversarial second-opinion pass on a finalized CWS launch decision — tries to
  break the scoring, find a hidden occupation, catch an over-optimistic softness
  call, or expose a wrong-software-type SERP. Use after cws-idea has chosen a
  hypothesis and BEFORE moving into packaging/build; also useful before
  pre-publish (Stage 3) and before turning on monetization (Stage 5). Triggers on
  "challenge this idea", "second opinion on this keyword", "stress-test the
  scoring", "is this idea actually good", "play devil's advocate", or "are we
  missing anything before we build". Pessimistic by design — meant to catch
  blind spots, not to validate. Inspired by /codex challenge mode.
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
# CWS Studio — challenge

Adversarial review. **Pessimistic by design** — actively tries to break the
plan, not validate it. Run before every irreversible commitment.

## When to use

- **Before Stage 2** (after `cws-idea` chose a hypothesis) — most common.
  Catches scoring optimism, soft gate mis-calls, hidden occupation in non-
  obvious word forms.
- **Before Stage 3 submit-for-review** — catches name collisions, listing
  text issues moderation will flag, missing extra-modules in site-wrappers.
- **Before Stage 5 monetization rollout** — checks behavioral-factor risk
  (search-position stability, geo distribution, user-base size).
- User explicitly asks for a stress test / devil's-advocate / second opinion.

## How to run

1. Run the re-entry protocol (read `.cws/state.json` + the latest stage
   artifact relevant to the challenge).
2. **Identify the stage being challenged**:
   - Stage 1 → challenge the chosen hypothesis in `01-idea.md`.
   - Stage 3 → challenge the listing + assets + draft in `02a-listing.md` +
     `03-launch.md`.
   - Stage 5 → challenge the monetization config in `05-monetize.md`.
3. Walk the **challenge checklist** for that stage (below). For each item,
   actually verify — pull Semrush again, open the SERP again, re-check the
   CWS DB with all-words-required search. **Don't trust prior session
   findings.**
4. Write the output to `./.cws/challenges/YYYY-MM-DD-<stage>.md` with:
   - **Verdict** at the top: `PASS` / `FAIL` / `WEAK PASS` (proceed with
     caveats).
   - **Findings** as a numbered list, each: severity (red / yellow / info),
     the issue, the evidence (link / quote / Semrush number), and the
     suggested fix.
   - **Re-verify list** — what the user should re-check before proceeding.

## Stage 1 challenge checklist

- **Word-form occupation recheck.** Run the CWS DB all-words-required search
  (each name word separately) — does an optimized rival exist that the
  phrase-only check missed?
- **Form-factor SERP recheck.** Open the top 3 SERP results. Does each
  *actually* implement the same product type as the plan, or is the SERP
  "software but wrong software"?
- **CPC history recheck.** Walk Semrush CPC chart across the last 12 months.
  Was the lit-up CPC a one-month fluke?
- **KD word-count normalization.** Is the KD score on the chosen keyword
  being compared against same-word-count peers, or against shorter keywords
  (making the score misleadingly favorable)?
- **Hidden niche saturation.** Run a CWS DB count of extensions containing
  *just the topic word*. Saturated vertical (1,800+ extensions) is a hidden
  red flag even when the keyword phrase looks clean.
- **Acquirer-availability risk.** Brand-piracy / downloader / VPN niches —
  Stripe-class acquirers refuse; flag if not already in the artifact.
- **V2 vs V3 donor.** If the donor is on manifest v2, flag — porting cost
  may break the timeline.
- **Donor liveness.** Install the donor right now — does it still work?
- **Volume reality.** US exact volume genuinely ≥ 2K (broad) or ≥ 500
  (narrow), without rounding tricks?

## Stage 3 challenge checklist

- **Name collision recheck.** Search CWS for the final name plus 1–2 letter
  variants — any optimized rival exists?
- **Listing spam recheck.** Re-paste name + short + full into Turgenev — any
  red / purple flags?
- **Two adjacent same-root words.** Scan for `Convert PDF Converter`-style
  patterns; moderation hates them.
- **Comma-chained keyword lists** in short or full — guaranteed moderation
  trigger.
- **Site-wrapper extras.** If the build is a site-in-tab type, is there at
  least one capability that *only* the extension API can deliver? Without
  it, ~95% rejection rate.
- **Permission justifications.** Each is one specific sentence, not "to
  store data".
- **`free` / `best` / `recommended` / `premium` / `#1`** anywhere in the
  meta?
- **Banner regression.** Banner reads at the actual CWS thumbnail size
  (not just the design dimension)?
- **Welcome Page screenshot framing** — full browser visible, framed border,
  numbered arrows, puzzle-shape match?
- **Locale dupes.** Multiple English locales (`en` + `en_US` + ...) — kill.
- **Extension ID wired** into review widget + Welcome Page + paywall URL
  before submit?

## Stage 5 challenge checklist

- **User-count floor.** ≥ 3K–4K weekly users? If not, **fail** — don't
  monetize yet.
- **Search position consolidated?** First organic installs visible for ≥ 2
  weeks?
- **Geo rollout plan defines Tier-1-first?** Tier-2/3 must stay free at the
  start.
- **Billing cycle composition exists** (not just one price)?
- **Trial design specified** (time / action / card-first)?
- **Grandfathering decided** for existing users?
- **Host permissions already max'd** in the manifest? If not, monetization
  + permission-change together = 2× user loss.
- **Uninstall Page live and wired** (`setUninstallURL`)?

## Output rules

- A `FAIL` finding **must** include the exact remediation (what to change,
  where, with the value).
- Don't repeat findings already in the prior artifact — only flag what's
  new or what was glossed over.
- If the challenge passes cleanly, the verdict file is still written —
  it's the audit trail.
- The challenge result does **not** update `gates_passed`. It only informs
  the user. The user (or autoplan) decides whether to proceed.
