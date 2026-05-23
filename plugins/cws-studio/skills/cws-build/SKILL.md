---
name: cws-build
description: >-
  Build the minimal Chrome Web Store browser extension — manifest v3, extension
  types, cloning open-source donors, minification, dev-mode testing. Stage 2
  (development) of the CWS launch pipeline. Use when the user wants to build the
  extension itself: choose an extension type (no-UI, site-wrapped, local page,
  popup, content-script injector, hybrid), clone and distance an open-source
  donor extension, write a manifest v3 build, minify the code, check whether a
  donor's code is obfuscated, view another extension's source, load an extension
  in developer mode, write the prototype spec, or hire a designer/developer.
  Triggers on "how do I build this extension", "clone this open-source
  extension", "what extension type should I use", "manifest v3", "minify my
  extension", or "load my extension in dev mode".
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
# CWS Studio — Stage 2: Development

Ship a CWS build that meets four points **before** monetization or extra
features. The job is to launch fast and test installs — not to build a beautiful
multi-feature product. Runs in parallel with **cws-package**.

## Core principles

1. **Functionality matches the name keyword** — build what the top SERP
   competitors for your keyword build, just simpler.
2. **One simple function**, tidy, **no bugs**, never breaks browser pages —
   bugs at launch wreck behavioral factors and can kill the product.
3. **Open-source prior art** makes the build dramatically easier — clone, change
   text/CSS, distance it from the donor.
4. **Manifest v3 only** — CWS rejects new v2 extensions.

## The four-point target

1. Functionality matches the name keyword. 2. Simple — one screen / one key
function. 3. Looks tidy. 4. No bugs.

## How to run it

Follow `references/development.md` — the full workflow: the build strategy
(open-source first), manifest version, cloning and distancing an open-source
donor so it passes moderation, minification, the six extension types and when to
use each (with manifest v3 code samples), the prototype spec, hiring a
designer/developer, installing in developer mode, viewing any extension's
source, and detecting obfuscated code.

## Gate to the next stage

A bug-free manifest v3 build with one clear core function that matches the name
keyword, distanced from any donor, that doesn't break other browser pages.

Next stage: **cws-launch** (assets, translations, publishing).

## Artifacts & re-entry

This skill reads `./.cws/state.json` + `./.cws/01-idea.md` (required prior
gate: `idea`) and writes `./.cws/02b-build.md`. Follow the re-entry protocol
in cws-sprint's `pipeline-state.md` reference.

**`02b-build.md` must contain:**
- Extension type chosen (no-UI / site-wrapper / local-page / popup /
  content-script / hybrid) and **why** (link to SERP form-factor match).
- Donor: GitHub URL + commit / "from scratch".
- Manifest: `v3` (always); list of permissions + one-line justifications each.
- Distance-from-donor checklist (`_metadata` removed, `_locales/*` pruned to
  `en`, name/branding swapped, icons swapped, CSS lightly changed, `author`/
  `fingerprint`/`key` removed).
- Minification status (yes / no / not applicable for from-scratch).
- Dogfood test log (1–2 days in your own browser; bugs found and fixed).
- Non-developer test log (2–5 testers; each with what they tripped on and
  whether you fixed it).
- Build size, file tree summary, hash of the zip.

**On gate pass**, update `state.json`:
- `build.extension_type`, `build.donor_url`, `build.permissions`,
  `build.minified`, `build.dogfood_passed: true`.
- Append `"build"` to `gates_passed`; log `gate_passed` event.
- Set artifact frontmatter `status: complete`.
