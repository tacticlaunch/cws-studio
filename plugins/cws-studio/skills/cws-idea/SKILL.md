---
name: cws-idea
description: >-
  Validate and score ideas for launching Chrome Web Store (CWS) browser
  extensions, and set up the CWS developer account. Stage 1 (and 0) of the CWS
  launch pipeline. Use whenever the user wants to evaluate a Chrome extension
  idea, pick or check a name keyword, decide which extension hypothesis to
  build, research extension competitors, estimate an extension's revenue or
  traffic potential, check whether a search query is "soft"/non-noisy and not
  taken by an optimized competitor, or set up a CWS developer account
  (antidetect browser, proxy, 2FA). Triggers on "is this a good extension idea",
  "score these extension ideas", "find a name keyword for my extension", "should
  I build X as a Chrome extension", a pasted list of CWS competitors, or "set up
  my Chrome Web Store account". Leans on the Semrush MCP and web search.
---

# CWS Studio — Stage 1: Idea validation

Score and rank ideas for launching **CWS browser extensions** the way an
SEO-driven studio does. The launch hinges on **organic Google traffic** to the
store page, so validation is a keyword/SEO exercise. Deliverable: a ranked
**Markdown scoring table** of 5–10 hypotheses + a short recommendation, in
**English**.

## Core principles

1. Traffic comes from **Google**, not CWS search; the **name keyword** is ~70%
   of SEO success.
2. Extensions rank for **software** queries only — not informational /
   commercial / entity queries.
3. Extensions outrank **sites**, not **optimized extensions** — target a
   software-y keyword not owned by a well-optimized competitor.
4. **Small niche keywords are undervalued** — 500 US/mo ≈ 50K real reach.
5. **Reduce to one simple function**; open-source prior art makes the build easy.

## What this stage produces

- A CWS developer account ready to publish (Stage 0).
- 5–10 scored product hypotheses, each with a name keyword.
- One winning hypothesis whose keyword **clears every gate**: collapses to one
  function · US-exact volume ≥ 2,000 (broad) / ≥ 500 (narrow) · softness (>50%
  software SERP) · not owned by an optimized extension.

## How to run it

- **Account setup** (RU/BY builders especially): follow
  `references/account-setup.md` — antidetect browser, proxy, Google account,
  2FA, CWS developer registration.
- **Idea validation**: follow the 10-step workflow in
  `references/idea-validation.md` — it is the authoritative procedure. Use
  `references/scoring-rubric.md` for the column set and output table, and
  `references/semrush-playbook.md` for exact Semrush report names and parameters.
- Always **generate 5–8 alternative name keywords** — never score only the
  user's first guess; it is usually occupied or red-zone.

## Tools

- **Semrush MCP** — the workhorse for volume / SERP / KD research. If it's not
  connected, say so and offer lower-confidence web-search estimates or wait.
- **web_search / web_fetch** — browsing CWS, reading competitor store pages and
  source, GitHub open-source checks, SimilarWeb traffic.
- Do **not** rely on app-database.com (login-walled).

## Gate to the next stage

Two gates from this stage. **Both** must pass.

### Gate 0 — account-setup (hard gate; precedes idea work for RU/BY)

The proxy is the foundation. A leaky proxy poisons everything downstream
(Google account flagged, CWS rejection on first impression, ad bans). Run
`cws-dolphin proxies-suggest` to pick a provider from the vetted list, buy
(or `proxy6-buy --yes` for autonomous), then **`dolphin-cli check-proxy
--id <id> --expect-country=<X>`** before attaching it to a profile. The
command must return `ok:true` AND `is_hosting:false`. Cross-verify with
whoer.net ≥80% green + pixelscan "consistent". Only then create the Dolphin
profile and the Google account inside it. See `references/account-setup.md`
for the full residential-ASN gate and provider table.

### Gate 1 — idea

Don't advance to packaging until one hypothesis has a name keyword that clears
all gates. If the obvious head keywords are occupied or red-zone, loop back to
step 4 and generate fresh candidates before declaring the idea dead.

Next stage: **cws-package** (write the listing) and **cws-build** (build it).

## Artifacts & re-entry

This skill reads/writes `./.cws/state.json` and writes `./.cws/01-idea.md`.
Follow the re-entry protocol in cws-sprint's `pipeline-state.md` reference:
locate or create `.cws/`, read `state.json`, **never silently overwrite a
complete artifact**.

**`01-idea.md` must contain:**
- The full scoring table (per `scoring-rubric.md`).
- The chosen hypothesis: seed extension, name keyword, US exact volume, KD %
  and zone, softness verdict, occupation verdict, donor URL (if any), per-niche
  notes.
- A "Why this keyword" 2–4 sentence justification.
- A "Rejected candidates" list (the other 4–9 hypotheses) with one-line reasons
  so a future re-entry doesn't re-evaluate the same dead ends.

**On gate pass**, update `state.json`:
- `idea.name_keyword`, `idea.us_volume_exact`, `idea.kd_zone`, `idea.donor_url`
- Append `gates_passed: ["idea"]`
- Append `{ts, stage: "cws-idea", event: "gate_passed"}` to `history`
- Set `current_stage: "cws-package"` (or `"cws-build"` if running them in
  parallel)
- Set artifact frontmatter `status: complete`
