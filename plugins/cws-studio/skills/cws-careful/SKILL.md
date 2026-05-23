---
name: cws-careful
description: >-
  Guardrail mode for irreversible or high-blast-radius CWS actions — submit for
  moderation, enable monetization, expand host permissions on a populated user
  base, relaunch the extension on a second account, delete a developer account,
  push a major listing-text change to a ranking extension. Use BEFORE any of
  these actions in any stage skill, or invoke directly when the user says
  "careful", "double-check before", "make sure I'm not breaking anything",
  "should I do this", "is this safe to ship". Refuses to proceed until the
  pre-flight checklist passes and the user explicitly confirms. Inspired by
  gstack /careful.
---

# CWS Studio — careful

Pre-flight guardrails on the actions that can wreck a launch.

## Actions this skill gates

| Action | Why gated |
|---|---|
| **Submit for CWS moderation** | First impression to Google. Re-submissions after rejection get stricter scrutiny. |
| **Enable monetization** | Behavioral-factor stress; user-count floor required (3–4K min). Premature monetization can kill ranking permanently. |
| **Add `<all_urls>` / max host permissions to a populated extension** | 30–40% of existing users click Remove on the permission-change dialog. |
| **Relaunch the same extension on a second account** | Chrome detects code reuse across accounts → potential ban of both. |
| **Major listing-text change to a ranking extension** | SEO ranking takes ~6 months to consolidate; tuning copy mid-rank can crash position. |
| **Delete a CWS developer account / extension** | Permanent; loses the rating + review history + the published URL. |
| **Push minified-code rewrite to existing extension** | If the diff is large, moderation may re-evaluate the whole extension. |

## How to run

Invoke this skill explicitly (`/cws-careful submit-moderation`) or have stage
skills route through it for the actions listed above.

1. **Identify the action**. From the user's request or the calling skill's
   context.
2. **Run the action's pre-flight checklist** (below). For each item, check
   `.cws/state.json` and the relevant artifact; if a check fails, **stop**
   and tell the user precisely what's missing.
3. **Show the consequence statement** — one sentence: what this action does
   and what cannot be undone.
4. **Require explicit confirmation**. The user must type something
   specific (e.g. "submit to moderation", "enable paywall") — not just
   "yes". This is to avoid accidental confirms after a long context.
5. **Only then** let the calling skill (or the user) execute the action.
6. **Log it**: append a `careful_confirm` event to `state.json` history
   with the action, timestamp and the user's exact confirmation string.

## Pre-flight checklists

### Submit for moderation

- `02a-listing.md` status: `complete`, Turgenev no red/purple flags.
- `02b-build.md` status: `complete`, dogfood test logged.
- `03-launch.md` has banners + icons + Welcome Page URL + 50+ locales + the
  extension ID (from a prior draft upload).
- Antivirus clean (VirusTotal date in artifact).
- Differentiation from competitor documented in `03-launch.md`.
- 2FA on the developer account confirmed.
- `_locales/*` cleaned to only locales actually used.
- Manifest permissions list is minimal — every permission has a 1-sentence
  justification ready to paste into the Privacy section.

### Enable monetization

- `state.extension.moderation_status: approved`.
- Weekly users ≥ 3,000 (read from latest retro / CWS dashboard).
- First organic installs visible for ≥ 2 weeks.
- `05-monetize.md` has: paywall provider, billing cycles, trial config, geo
  rollout plan (Tier-1 first), grandfathering decision, host-permissions
  status.
- Host permissions already max'd? If NOT, **strongly warn** — combining
  permission expansion with monetization rollout is double user loss.

### Add `<all_urls>` to a populated extension

- Read latest user count from state.
- If users > 1–2K: warn that 30–40% will click Remove on the update
  dialog. Suggest pairing with a value-add the user must see.
- Confirm the justifying all-sites function is implemented (artifact /
  draggable widget per `cws-monetize` references).

### Relaunch on a second account

- Confirm the new account is properly distanced (different antidetect
  profile, different proxy, fully different fingerprint).
- Confirm the rebuild has gone through full distancing per
  `cws-build/references/development.md` (CSS / icons / text / minifier
  settings changed).
- Confirm the second-account name keyword is **different by ≥ 2 words**
  from the first.
- Warn: Chrome can detect code reuse and ban both accounts. There is no
  guarantee even with full distancing.

### Major listing-text change to a ranking extension

- Read the latest retro snapshot — what's the current rank/position?
- If ranking position is good (≥ #5 on the head term), warn: copy changes
  reset behavioral signals partially; expect 2–3 weeks of noise.
- If ranking position is poor, the change is low-risk; proceed.
- Recommend running a `cws-challenge` pass on the new copy first.

### Delete a CWS developer account / extension

- Permanent. No recovery of ratings, reviews, or the store URL.
- If extension has > 1K users → strong warning, recommend transfer (Google
  one-stop support form) instead.
- Require the user to type the extension name exactly.

### Push minified-code rewrite

- Confirm the diff size in lines / files.
- If > 50% of the codebase is changing → warn moderation may re-evaluate
  the whole extension; stage it as a 2-step update (split into smaller
  diffs across two moderation passes).

## What careful never does

- Doesn't perform the action itself — it gates and confirms.
- Doesn't override a real-world rule (e.g. CWS terms). If an action would
  violate ToS, careful refuses and explains.
- Doesn't replace `cws-challenge`. They complement: challenge probes the
  *plan*, careful gates the *action*.
