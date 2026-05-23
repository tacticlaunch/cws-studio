---
name: cws-launch
description: >-
  Create Chrome Web Store launch assets, translate the extension, and publish it
  — banners, icons, Welcome Page, 50+ locale translations, pre-publish checks,
  uploading to CWS and passing moderation. Stage 3 of the CWS launch pipeline.
  Use when the user wants to make the small/large store banners or icons, build
  and publish a Welcome Page, auto-translate the extension into many locales,
  manually translate the name for important languages, run pre-publish checks
  (antivirus, competitor differentiation), upload the extension to the CWS
  developer dashboard, fill the store card, justify permissions, or pass
  moderation. Triggers on "make my extension banners", "create a Welcome Page",
  "translate my extension", "publish to Chrome Web Store", "upload to CWS", or
  "pass CWS moderation".
---

# CWS Studio — Stage 3: Assets, translations & publishing

Banners, icons, Welcome Page, 50+ locale translations, pre-publish checks, and
uploading to CWS. Every asset is judged by one question: does it reduce friction
so a tested user stays instead of bouncing back to Google?

## Core principles

1. **Behavioral factors decide the launch.** Google tests a new extension on
   tiny random samples over ~6 months; bugs, a confusing banner or Welcome Page
   tank ranking. Every asset must minimize friction.
2. **Simple and clear beats clever** — banners, Welcome Page, onboarding flow.
3. **Translate widely** — 50+ locales multiplies ranking chances; other
   languages have far lower competition than English.
4. **Differ from competitors** — a full copy-paste gets rejected by moderation.

## What this stage produces

- Small banner (440×280), large banner (1280×800), icon set.
- A Welcome Page that opens after install, hosted and auto-opened.
- The extension translated into 50+ locales.
- The extension uploaded to CWS, store card filled, submitted for moderation.

## How to run it

Follow `references/assets-and-publish.md` — the full workflow: pre-launch
testing, behavioral factors, banner/icon rules and mistakes, the Welcome Page
(and its mistakes), translations (Localizer, manual translation, transliteration),
pre-publish checks (antivirus, differentiation), uploading to CWS, justifying
permissions, the Privacy Policy, and launch-time decisions (analytics, auth
timing, extension ID, A/B tests, location handling).

For bulk-uploading all locale full descriptions to CWS, use the script
`references/cws-locale-uploader.js`.

## Gate to the next stage

Extension submitted and **approved** by moderation, with banners, icons, Welcome
Page and 50+ locales in place.

Next stage: **cws-promote** (paid installs, analytics, reviews).

## Artifacts & re-entry

This skill reads `./.cws/state.json` + `./.cws/01-idea.md` + `02a-listing.md` +
`02b-build.md` (required prior gates: `idea`, `package`, `build`) and writes
`./.cws/03-launch.md`. Follow the re-entry protocol in cws-sprint's
`pipeline-state.md` reference.

**`03-launch.md` must contain:**
- Banner files: small (440×280) + large (1280×800) paths, with notes on
  alternatives tried.
- Icon set paths (16 / 48 / 64 / 96 / 128, plus the 128-with-margin for the
  store).
- Welcome Page URL (Tilda subdomain or own domain) + screenshot framing notes
  (arrow + number combo, full browser visible, etc.).
- Translations: which locales auto-translated, which manually done; the 10×
  rule decisions per locale name.
- Pre-publish checks: VirusTotal clean (date), differentiation from competitor
  documented, `_locales` cleanup if English-only.
- **Extension ID** (grabbed right after the first draft upload — feeds the
  review widget URL and Welcome Page).
- Moderation status: `pending` / `approved` / `rejected` (+ reason if
  rejected) / `resubmitted` (+ what changed).
- Store URL once approved.

**On gate pass**, update `state.json`:
- `extension.id`, `extension.draft_uploaded: true`,
  `extension.submitted_for_review: true`, `extension.moderation_status`,
  `extension.store_url`.
- Append `"launch"` to `gates_passed`; log `gate_passed` event.
- Set artifact frontmatter `status: complete`.
