---
name: cws-resync
description: >-
  Propagate a mid-launch change across every downstream stage. When something
  upstream shifts — name keyword, full description, banner/icon, manifest
  permissions, extension type, Google account migration — this skill computes
  the full impact set, marks affected artifacts `superseded`, writes the route
  plan, and walks the user through the re-do in dependency order. Triggers on
  "I changed X, what else", "resync", "propagate this rename", "I updated the
  banner", "I widened host_permissions", "make everything consistent again".
  Inspired by gstack /document-release.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - AskUserQuestion
triggers:
  - resync
  - propagate this rename
  - I changed X what else
  - I widened host_permissions
  - I updated the banner
---

# cws-resync — propagate mid-launch change across stages

You are an operator running a structural fix-up across an in-flight launch.
Something upstream changed — a keyword, a description, a banner, a
permission, the extension type, the Google account — and downstream
artifacts are now stale. Stale artifacts are not just cosmetic: a stale
banner means the wrong ad creative goes live; a stale permission
justification means a moderation re-rejection; a widened host_permissions
without a re-consent plan loses 30 to 60 percent of installed users.

Your job:

1. Identify the trigger change and its dependency closure.
2. Mark every affected artifact `superseded` with a timestamp.
3. Log the propagation to `./.cws/.resync.log`.
4. Hand the user a single confirmed route plan: which downstream skill
   runs first, second, third.
5. Hard-gate through `cws-careful` BEFORE any irreversible action.
6. Route to the first skill in the plan.

You do NOT do the downstream work yourself. Each downstream skill is
responsible for its own re-run — cws-resync only orchestrates the cascade.

## Preamble (run first)

Run the standard preamble (see `shared/preamble.md`). It loads `$SLUG`,
`$_BRANCH`, prior learnings, and `./.cws/state.json`. Skip the rest of this
skill if the preamble exits — the preamble is the gate.

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.0.0}"
BIN="$PLUGIN_ROOT/bin"
eval "$("$BIN/cws-slug" 2>/dev/null)"
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_SESSION_ID="$$-$(date +%s)"
mkdir -p "$CWS_PROJECT_DIR" 2>/dev/null
_PROACTIVE=$("$BIN/cws-config" get proactive 2>/dev/null); [ -z "$_PROACTIVE" ] && _PROACTIVE=true
_EXPLAIN_LEVEL=$("$BIN/cws-config" get explain_level 2>/dev/null); [ -z "$_EXPLAIN_LEVEL" ] && _EXPLAIN_LEVEL=default
echo "SLUG: $SLUG"
echo "BRANCH: $_BRANCH"
echo "PROACTIVE: $_PROACTIVE"
echo "EXPLAIN_LEVEL: $_EXPLAIN_LEVEL"
_LEARN_FILE="$CWS_PROJECT_DIR/learnings.jsonl"
if [ -f "$_LEARN_FILE" ]; then
  _LC=$(wc -l < "$_LEARN_FILE" | tr -d ' ')
  echo "LEARNINGS: $_LC entries loaded"
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --limit 3
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('CURRENT_STAGE:', d.get('current_stage','none')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none'); print('LAUNCH_STATUS:', d.get('launch_status','pre-launch'))"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-resync\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

After running, branch off the echoed values:

- `CWS_STATE: missing` — STOP. Route to `/cws-init`. cws-resync cannot
  compute a propagation set without a state file and a `gates_passed` list.
- `LAUNCH_STATUS: pre-launch` — STOP. Pre-launch means no published store
  page, no banners, no ad spend, no installed users. There is nothing to
  propagate to. Tell the user: "Pre-launch — just go back to the stage skill
  and edit the artifact directly. cws-resync only earns its keep after
  `cws-launch` has shipped." Route to the relevant stage skill and exit.
- `CURRENT_STAGE` — used as the implicit "where the change originated"
  unless the user explicitly names another origin.
- `LEARNINGS: <n>` — surface the 3 most recent. Past resyncs often teach
  what propagations are most error-prone.

## AskUserQuestion Format

See `shared/askuserquestion-format.md`. Every interactive decision goes
through `AskUserQuestion` as a `D<N>` decision brief (ELI10 · Stakes ·
Recommendation · Completeness · Pros/cons · Net). D-numbering starts at D1
per invocation.

## Voice

See `shared/voice.md`. Operator voice. No banners. No file-creation dumps.
Concrete numbers, names, paths. Lead with the point. Every propagation
implication is named with the artifact path and the concrete consequence
("re-consent dialog — 30-60% retention drop").

## Skill Routing Footer

End every invocation with a single `Next: /cws-<skill>` line per
`shared/skill-routing.md`. The next skill is the FIRST skill in the
computed route plan.

---

## Phase 0 — Identify the trigger change (D1)

The user's message usually names the change, but rarely names the FULL
scope. You ask for the trigger explicitly so the impact computation has a
typed input, not a guess.

`AskUserQuestion D1` — What changed?

- ELI10: We need to know exactly what shifted upstream so we can compute
  every downstream artifact that's now stale. The same word ("name") means
  different things across stages — a name change in the store listing is
  one impact set; a name change in the manifest is a different one.
- Stakes if we pick wrong: under-classify and we miss a stale artifact
  (silent rot); over-classify and we re-run skills the user already paid
  for. The right type is the cheapest correct cascade.
- Recommendation: choose the option that matches the EXACT field the user
  edited. If unsure, ask the user for the path of the edit.
- Completeness: Note: options differ in kind, not coverage — no completeness score.
- Pros/cons:
  - A) Name keyword (the rankable head, e.g. "color picker" → "color code picker")
    - ✅ Cleanest impact set; well-understood cascade.
    - ✅ All 50+ locales need a refresh — Localizer is the one tool that
      handles it cleanly.
    - ❌ The 8-10 keyword-saturation floor must be re-counted in the
      description; cheap but mandatory.
  - B) Full description (the long copy block on the listing)
    - ✅ Localizer re-translation is mechanical.
    - ✅ Turgenev recheck is a single paste.
    - ❌ All 50+ locales re-upload to CWS — slow, mechanical, error-prone.
  - C) Banner or icon (visual creative)
    - ✅ Smallest cascade in most cases.
    - ✅ Welcome Page often skips re-route if banner is cosmetic only.
    - ❌ Ad creatives may need rebuild — separate skill, separate budget.
  - D) host_permissions widened (manifest permissions block)
    - ✅ HARD GATE through cws-careful; explicit user re-consent plan.
    - ❌ Re-consent dialog kills 30-60% of installed users. Never skip this.
    - ❌ CWS review re-triggers; ad-platform compliance review may trigger.
  - E) Extension type / manifest shape (popup → sidebar, MV2 → MV3, etc.)
    - ✅ Build artifact + all UX-shape-dependent assets need a refresh.
    - ✅ Welcome Page reposition is the highest-impact downstream.
    - ❌ Largest cascade short of a full re-launch.
  - F) Google account migration (the publishing account moved)
    - ✅ Discrete cascade; Dolphin profile + auth artifacts.
    - ❌ CWS support migration request — manual, 1-5 day SLA.
    - ❌ All previously-installed users keep the prior extension; new
      publishes go to the new account. Recovery path is non-trivial.
- Net: pick the exact upstream type. If the user edited two fields in one
  session (e.g. name AND description), run cws-resync twice — once per
  type. The cascades overlap but the routing differs.

Store the answer as `_TRIGGER_TYPE` for the rest of the skill.

If the user pasted a free-form description of the change, parse it for the
keywords above before asking D1. Skip D1 entirely if the trigger is
unambiguous in the message ("I widened host_permissions to include
`<all_urls>`" → D-option D, no question needed).

---

## Phase 1 — Compute the downstream impact (mechanical)

For the selected `_TRIGGER_TYPE`, walk the propagation matrix below and
build the impact set. The matrix is mechanical — there is one correct
output per input. Do not ask the user about individual rows; the user only
confirms the FULL plan at D2.

### 1.A — Name keyword changed

The name keyword is the head term the store listing ranks for. Changing it
invalidates copy, saturation counts, ads, banners, and every locale.

Impact set:

- `./.cws/02-package/listing.md` — name occurrences (target 8-10 in
  description), short description, title. Re-run keyword saturation count.
- `./.cws/03-launch/welcome-page.md` — Welcome Page copy that mentions
  the name. Often a single string per section.
- `./.cws/03-launch/banners.md` — banner caption text (small banner
  almost always contains the name keyword).
- `./.cws/04-promote/fb-ads.md`, `04-promote/google-ads.md`,
  `04-promote/yandex-ads.md` — ad headlines and primary text.
- `./.cws/02-package/locales/*.json` (50+ files) — name field in every
  locale. Localizer re-translates from the new English head; flag the
  per-locale character limit gotchas.
- Turgenev: re-paste name + short + full as one block for AI-detection
  re-check after Localizer outputs land.

Iron rules:

- Translations re-run is MANDATORY. Never skip locales on a name change.
- Re-run cws-package keyword-saturation count on the new name. The 8-10
  floor is keyword-specific; old saturation does not carry.

### 1.B — Full description changed

The description is the long block on the store page. Changing it
invalidates locales, Turgenev, and the CWS draft state.

Impact set:

- `./.cws/02-package/listing.md` — the description block itself.
- `./.cws/02-package/locales/*.json` (50+) — full description per locale.
  Localizer re-translation.
- Turgenev: re-paste the new English description for AI-detection score.
- CWS Developer Dashboard draft — re-upload the description per locale.
- If currently in moderation: the upload will RESET moderation. Plan to
  re-submit and accept the 1-3 business day SLA.

Iron rules:

- Translations re-run is MANDATORY. Same rule as the name change.
- If `LAUNCH_STATUS: moderation-pending`, surface the moderation reset
  cost prominently — the user may want to wait until current moderation
  resolves before pushing the description change.

### 1.C — Banner or icon changed

The banner/icon is the visual on the store listing. Cascade is narrow if
purely cosmetic; wider if the banner depicts the extension UI.

Impact set:

- `./.cws/03-launch/banners.md` — the banner artifact itself (small
  banner, marquee, screenshots).
- CWS Developer Dashboard draft — re-upload assets.
- `./.cws/04-promote/fb-ads.md` rectangular creative — if the FB
  rectangular was derived from the small banner, rebuild.
- `./.cws/03-launch/welcome-page.md` — IFF the Welcome Page screenshot
  composition shows the same banner artwork. If the Welcome Page is
  text-only or shows the extension UI directly, skip the Welcome Page
  re-route.

Iron rules:

- Banner changes CAN skip Welcome Page re-route IFF banner is purely
  cosmetic (e.g. color/spacing tweak, no element added/removed). If the
  banner depicts the extension UI itself, Welcome Page must re-route.
- Asset re-upload to CWS draft is always required.

### 1.D — host_permissions widened (HARD GATE)

This is the highest-stakes propagation in the matrix. Widening
`host_permissions` triggers an EXISTING-USER re-consent dialog ("This
extension wants additional permissions"). Industry-measured retention
drop: 30-60%.

`AskUserQuestion D3` (HARD GATE) — Have you run cws-careful for this?

- ELI10: Widening host_permissions is one of the few launch changes that
  cannot be quietly cascaded. Every existing user sees a re-consent dialog;
  most click "Don't allow" or just churn. We need the careful gate to run
  BEFORE any downstream re-run, so the user has a chance to revert or stage
  the rollout differently.
- Stakes if we pick wrong: silent cascade = 30-60% installed-user loss in
  one moderation cycle. Recovery requires re-acquiring users at promote
  spend — orders of magnitude more expensive than NOT shipping the change.
- Recommendation: **B) Pause and route to cws-careful first** — never skip.
- Completeness: A=2/10 (skips gate), B=10/10 (gate runs).
- Pros/cons:
  - A) Skip cws-careful, proceed with cascade
    - ✅ Faster if the user has already considered re-consent.
    - ❌ No structured check. One missed consideration = installed-user wipe.
    - ❌ No revert plan. If the re-consent fails badly, no rollback path
      was rehearsed.
  - B) Route through cws-careful first (recommended)
    - ✅ Forces the re-consent plan to exist before cascade.
    - ✅ Builds the revert path (narrow the permission again) into the
      plan up front.
    - ✅ No cons — this is a hard-stop choice.
- Net: B is mandatory. If the user picks A, refuse and re-ask. cws-careful
  is the gate, not a suggestion.

If B (always): STOP the resync workflow and emit:

```
Next: /cws-careful
Why: host_permissions widening is a hard gate. Run cws-careful first to
build the re-consent plan and the revert path. Re-invoke /cws-resync after
the careful gate clears.
```

Do NOT proceed to Phase 2 in this branch. cws-careful will route back when
done.

If the user has already cleared cws-careful for this change (state file
records it in `gates_passed`), continue:

Impact set (after gate cleared):

- `./.cws/02-build/manifest.md` — the manifest permissions block itself.
- `./.cws/02-package/moderation-justifications.md` — re-write justifications
  for each added permission. Moderation re-scrutiny is GUARANTEED.
- `./.cws/03-launch/listing.md` (if listing references permission scope) —
  often the description mentions the URL scope ("Works on any page").
- CWS Developer Dashboard — re-upload manifest, re-submit for moderation.
- `./.cws/04-promote/*` — ad platforms (FB especially) often re-run
  compliance review when permission scope changes. Flag this; do not assume
  the existing ad approvals carry.
- `./.cws/00-account-setup.md` — no impact unless the new permission
  introduces a new compliance category (e.g. health, finance).

Iron rules:

- cws-careful MUST run first. Non-negotiable.
- Moderation re-submit is GUARANTEED, not optional. Plan the timing.
- Ad-platform compliance re-review is LIKELY for FB Ads on
  permission-scope changes. Build the timing into the promote plan.

### 1.E — Extension type / manifest shape changed

Examples: popup → sidebar, MV2 → MV3, action button → content script
overlay. The UX shape changes; every asset that depicted it is stale.

Impact set:

- `./.cws/02-build/` — the build artifact itself. Re-build, re-minify,
  re-dogfood (1-2 days minimum).
- `./.cws/03-launch/banners.md` — banner usually shows the UX shape.
  Re-create.
- `./.cws/03-launch/welcome-page.md` — Welcome Page tour now points at
  the wrong UI elements. Reposition the entire tour.
- `./.cws/03-launch/screenshots.md` — store screenshots; re-shoot all.
- `./.cws/02-package/listing.md` — if the description names the UX shape
  ("opens in a popup"), update.
- CWS Developer Dashboard — re-upload build + assets. Moderation
  re-submit.

Iron rules:

- Dogfood re-do is MANDATORY. 1-2 days. New UX shape = new bug surface.
- Welcome Page tour is the highest-impact downstream. A tour pointing at
  the wrong UI tanks first-session retention.

### 1.F — Google account migration

The Chrome Web Store account that published the extension has moved (or
the user is moving to a fresh dedicated account). This is a Stage 0
artifact change and cascades through auth and publishing.

Impact set:

- `./.cws/00-account-setup.md` — the account artifact itself.
- Dolphin profile — rebuild via `cws-dolphin create` against the new
  account. The old profile stays for audit (do not delete during the
  migration window).
- `./.cws/02-build/` — no impact unless the build embeds an OAuth client
  ID (rare for CWS extensions, common for sign-in integrations).
- CWS Developer Dashboard — a published extension does NOT auto-migrate
  to a new publishing account. The user must either:
  a. Transfer the extension to the new account via CWS support (manual,
     1-5 day SLA, support ticket required).
  b. Publish a fresh listing under the new account and migrate users
     manually (loses all reviews, ratings, install count — usually a
     last resort).
- All auth-bearing artifacts (any token, cookie, OAuth config in the
  repo) — re-issued.

Iron rules:

- Dolphin profile rebuild is MANDATORY.
- CWS support migration request is the safe path; surface the SLA (1-5
  business days).
- Do NOT delete the old account until the new publishing path is
  confirmed working. Two-account window prevents lockout.

---

## Phase 2 — Mark affected artifacts `superseded`

For every artifact in the impact set from Phase 1, edit its frontmatter:

```yaml
---
stage: cws-package
status: superseded
superseded_by_resync: 2026-05-27T10:00:00Z
prior_status: complete
---
```

Mechanical rules:

- The `status:` field flips from `complete` (or `in-progress`, etc.) to
  `superseded`.
- A NEW field `superseded_by_resync: <ts>` is added with the resync
  timestamp.
- A NEW field `prior_status: <prior>` preserves the prior status for
  audit. Without this, the downstream stage skill cannot tell which
  artifacts were complete before the resync vs always-stale.
- The artifact content BELOW the frontmatter is NOT modified. cws-resync
  does not rewrite content; downstream skills do.

Use the Edit tool with exact `old_string` matches on the frontmatter
block. NEVER use Write — that overwrites everything below the frontmatter.

If an artifact in the impact set DOES NOT EXIST on disk yet (e.g. the user
ran cws-launch only partially and `welcome-page.md` is not yet created),
do not fabricate the file. Note it in the route plan as "not yet created;
the stage skill will produce it" and continue.

---

## Phase 3 — Log to `./.cws/.resync.log`

Append one log block per resync invocation:

```
2026-05-27T10:00:00Z  type=name-keyword
  origin: ./.cws/01-idea.md  ("color picker" → "color code picker")
  impact:
    - ./.cws/02-package/listing.md            [superseded, prior=complete]
    - ./.cws/02-package/locales/*.json        [superseded, prior=complete, count=53]
    - ./.cws/03-launch/welcome-page.md        [superseded, prior=complete]
    - ./.cws/03-launch/banners.md             [superseded, prior=complete]
    - ./.cws/04-promote/fb-ads.md             [superseded, prior=complete]
    - ./.cws/04-promote/google-ads.md         [superseded, prior=complete]
  plan: cws-package → cws-launch (banners + welcome) → cws-promote (ads)
  gates_required: none (no careful gate; not host_permissions)
```

The log is append-only. It serves three purposes:

1. Audit — six months from now, you want to see the cascade history.
2. Recovery — if a resync was interrupted (the user closed the session),
   the next session reads the log and resumes the route plan.
3. Learnings input — `cws-learn` may surface "this cascade always reveals
   a Welcome Page gap" as a high-confidence learning after 3+ resyncs of
   the same shape.

If `.resync.log` does not exist, create it with a one-line header:

```
# CWS resync log — append-only. Newest at the bottom.
```

---

## Phase 4 — Present the route plan (D2)

The route plan is mechanically computed from the impact set. The order is:

1. Upstream artifacts first (the originator, if it's not the user's edit
   itself).
2. Stage skills in dependency order: package → launch → promote →
   monetize. Skip skills with no impacted artifact.
3. Re-verification skills last (cws-challenge to confirm the cascade is
   clean).

Present the plan via:

`AskUserQuestion D2` — Run the route in this order?

- ELI10: This is the propagation cascade. Each step is one downstream
  skill that re-runs to refresh its artifacts. The skill knows to look for
  `status: superseded` in the frontmatter and will pick up where it left
  off rather than start fresh.
- Stakes if we pick wrong: a wrong order = a skill runs against still-
  stale upstream artifacts and bakes the wrong inputs into its output.
  Example: running cws-promote before cws-launch re-creates banners means
  ads ship referencing the old banner.
- Recommendation: **A) Run in computed order** — the matrix order is the
  one that respects upstream/downstream constraints.
- Completeness: A=10/10, B varies, C=2/10.
- Pros/cons:
  - A) Run in computed order (recommended)
    - ✅ Respects upstream/downstream constraints by construction.
    - ✅ Each skill sees clean upstream inputs.
    - ❌ No early bail-out if the user wants to skip a stage.
  - B) Reorder manually (user picks)
    - ✅ Useful if the user knows a downstream stage is being deprecated
      anyway.
    - ❌ Risk of running a skill against stale upstream. Each manual
      reorder must be verified.
  - C) Defer — don't run anything; just mark superseded and log
    - ✅ Useful when the user is exploring impact and not ready to re-run.
    - ❌ Artifacts stay superseded; downstream state drifts further until
      the cascade runs.
- Net: A is the default-safe pick. Surface B only if the user
  proactively asked for a different order; surface C only if the user
  said "I want to see the impact but not run yet."

After the answer:

- **A** — route to the first skill in the computed plan.
- **B** — collect the user's reordered list via free-form. Validate that
  it does not violate hard upstream constraints (e.g. promote before
  launch); if it does, refuse and re-ask. Then route to the first skill
  in the user's order.
- **C** — exit cleanly. The log + superseded frontmatter is the record;
  no skill runs. Route hint:

```
Next: (deferred)
Why: Impact set is marked and logged. Re-invoke /cws-resync when ready to
run the cascade.
```

---

## Phase 5 — Route to the first downstream skill

The skill routing footer (see `shared/skill-routing.md`) gets the first
skill in the confirmed plan. Each downstream skill detects
`status: superseded` on its artifact and:

- Re-runs in `restart_reason: resync` mode (the skill knows it is fixing
  a cascade, not building from scratch).
- Treats `prior_status: complete` as a signal that the artifact had
  passed its own checks once already — the focus is the DELTA, not a
  full re-do.
- On completion, updates the frontmatter back to `status: complete` (or
  the prior status) and removes the `superseded_by_resync` field. The log
  in `.resync.log` is the audit record; the frontmatter is the live state.

If the route plan has multiple downstream skills, EACH skill on
completion is expected to route to the NEXT skill in the plan. The plan
is stored in state.json under `resync.route_plan` for this purpose:

```json
{
  "resync": {
    "ts": "2026-05-27T10:00:00Z",
    "type": "name-keyword",
    "route_plan": ["cws-package", "cws-launch", "cws-promote"],
    "route_index": 0
  }
}
```

Each downstream skill increments `route_index` on completion and reads
the next skill from `route_plan`. When the index passes the end, the
resync block is cleared and normal stage routing resumes.

---

## Phase 6 — Iron rules (mechanical, no user confirmation)

These rules are MECHANICAL. They do not require user confirmation. They
are enforced silently in the propagation path. If a rule fails, STOP and
surface the failure to the user.

### 6.1 host_permissions widening MUST route through cws-careful

No exception. If `_TRIGGER_TYPE == D` and `gates_passed` does not contain
`careful-host-permissions-<ts>`, the resync STOPS at Phase 1.D D3 and
routes to cws-careful. The user CANNOT bypass this via cws-resync.

If the user has explicitly said "I know what I'm doing, just cascade" —
still refuse. The 30-60% retention drop is not a taste call.

### 6.2 Translations re-run is MANDATORY for name and description

If `_TRIGGER_TYPE in {A, B}`, locales are in the impact set. Period. The
user cannot opt out of the translation re-run via cws-resync; if they want
to skip, they edit the route plan in D2 to drop the locale step — but the
cws-package skill on re-run will surface a hard warning about the locale
drift and the user must opt out THERE, where the skill can record the
opt-out in `02-package/listing.md`.

cws-resync does not collect skip rationale. Downstream skills do.

### 6.3 Never delete a superseded artifact

The superseded artifact stays on disk. It stays in git history. The
`status: superseded` frontmatter is the signal; the content body is the
audit record. A downstream skill on re-run MAY rewrite the body in place;
in that case, it MUST preserve the prior body in a `## Superseded
content (resync <ts>)` section at the bottom of the file.

cws-resync itself does not modify the body — that's downstream's job.

### 6.4 Banner cosmetic-only exception

Banner changes CAN skip Welcome Page re-route IFF the change is purely
cosmetic. The decision is taste, not mechanical. Surface as part of
Phase 1.C D-question if the user picked banner — ask explicitly whether
the banner change is cosmetic (color/spacing) or structural (depicts a
different UI). Default: structural (re-route Welcome Page) unless the
user explicitly says cosmetic.

### 6.5 Pre-launch is a no-op

If `LAUNCH_STATUS: pre-launch`, the skill is a no-op (covered in Phase 0).
There are no published artifacts to propagate to. Tell the user, route
back to the stage skill, exit.

### 6.6 One trigger per invocation

If the user describes two distinct changes ("I changed the name AND
widened host_permissions"), run cws-resync once per trigger. The
cascades overlap (both touch the listing) but the routing differs
(host_permissions hard-gates through cws-careful; name does not).
Combining them in one invocation produces tangled state.

The skill surfaces this proactively: at Phase 0, if the user's message
mentions two trigger types, ask which one to handle first and STOP after
that one is resolved. The user re-invokes for the second.

---

## When NOT to use cws-resync

- **Pre-launch.** Covered above. Edit the stage artifact directly; there
  is nothing downstream to propagate to.
- **Cosmetic-only typo in the description.** A one-word typo fix does not
  cascade. Edit the artifact in place, run cws-package locally to
  re-translate that one string, done. cws-resync is for STRUCTURAL changes,
  not copy-edits.
- **Adding a new locale.** Adding a new translation is purely additive —
  it does not invalidate any other artifact. Run cws-package directly.
- **Changing the build internals without changing UX shape.** A pure
  refactor that doesn't touch the manifest or the user-facing UI does not
  cascade. Re-run cws-build alone.
- **Routine retro updates.** A retro that says "we should change X next
  sprint" is a planning input, not an upstream change. Use cws-learn to
  capture the lesson; defer the change to the next sprint, where the
  stage skill picks it up cleanly.

If the user invokes cws-resync for any of the above, redirect them to the
right tool in one line and exit. Do not waste the cascade.

---

## Companion skills

- **cws-careful** — the HARD GATE for host_permissions widening (Phase
  1.D) and Google account migration cascades. cws-resync STOPS and routes
  to cws-careful BEFORE any downstream re-run. cws-careful, on completion,
  routes back to cws-resync to resume.
- **cws-learn** — every resync is a teaching event. After Phase 5 routes
  to the first downstream skill, the user is encouraged (not required) to
  run cws-learn to record what caused the resync — the upstream edit that
  triggered the cascade. The lesson typically lands at `stage: cross` with
  evidence pointing to `.cws/.resync.log`.
- **cws-challenge** — after the FULL cascade completes (every skill in
  the route plan has re-run), cws-challenge re-runs to verify no new gaps
  were introduced. A common gap: ad creative references the OLD name
  because the cascade dropped FB ads from the plan but kept Google ads.
  cws-challenge catches the inconsistency.
- **cws-retro** — the next retro reads `.resync.log` and surfaces the
  cascade in the timeline. If a cascade became necessary, the retro asks
  why the upstream change wasn't planned earlier.
- **cws-package, cws-launch, cws-promote, cws-monetize** — the downstream
  skills that actually do the re-do work. cws-resync routes; they execute.

The pattern: cws-resync sees the shape of the cascade; each downstream
skill does the work for its stage; cws-careful gates the irreversible
sub-paths; cws-learn captures what to do differently next time; cws-
challenge verifies the cascade landed clean.

---

## Storage shape (for reference)

- `./.cws/.resync.log` — append-only resync log. Committed to git.
- `./.cws/state.json` — holds `resync.route_plan` and `resync.route_index`
  while a cascade is in flight.
- Each impacted artifact's frontmatter — flipped to `status: superseded`
  with `superseded_by_resync: <ts>` and `prior_status: <prior>`. Restored
  to `status: <prior>` on downstream re-run.

cws-resync is the only skill that writes to `.resync.log`. Downstream
skills read it (and the artifact frontmatter) to decide their restart
behavior.

---

## Phase 7 — Worked examples

These make the matrix concrete. Reference when the cascade shape is
ambiguous.

### Example A — Name keyword change (Type A)

User message: "I changed the name keyword from `color picker` to
`color code picker` in 01-idea.md."

Phase 0: trigger is unambiguous — type A. Skip D1.

Phase 1.A impact set:

- `./.cws/02-package/listing.md` (re-saturate 8-10 floor)
- `./.cws/02-package/locales/en.json, ru.json, … (53 files)`
- `./.cws/03-launch/welcome-page.md`
- `./.cws/03-launch/banners.md`
- `./.cws/04-promote/fb-ads.md`, `04-promote/google-ads.md`,
  `04-promote/yandex-ads.md`

Phase 2: flip each frontmatter to `status: superseded`,
`superseded_by_resync: <ts>`, `prior_status: complete`.

Phase 3: append to `.resync.log`:

```
2026-05-27T10:00:00Z  type=name-keyword
  origin: ./.cws/01-idea.md  ("color picker" → "color code picker")
  impact: 6 artifacts + 53 locales
  plan: cws-package → cws-launch → cws-promote
```

Phase 4: D2 — recommend A (computed order). User confirms.

Phase 5: route to `/cws-package` with `resync.route_plan = [cws-package,
cws-launch, cws-promote]` in state.json. cws-package on re-run sees
`status: superseded` on `listing.md` and runs in delta mode: re-count
saturation, re-issue Localizer batch, do not re-write the structure of
the listing block.

### Example B — host_permissions widening (Type D)

User message: "I added `https://*/*` to host_permissions because we now
support all sites."

Phase 0: trigger is unambiguous — type D. Skip D1.

Phase 1.D D3 (HARD GATE): "Have you run cws-careful for this?" The user
has not. Recommendation B. STOP the resync workflow.

```
Next: /cws-careful
Why: host_permissions widening is a hard gate. Run cws-careful first to
build the re-consent plan and the revert path. Re-invoke /cws-resync after
the careful gate clears.
```

The user runs `cws-careful`. It walks through: (a) what fraction of
installed users will see the re-consent dialog (all of them); (b) the
expected retention drop (30-60%); (c) the staged rollout plan (do a 10%
canary on a fresh listing, measure, then promote to the main listing);
(d) the revert path (narrow the permission back to the prior list); (e)
records the gate pass in `state.json` as
`gates_passed += ["careful-host-permissions-<ts>"]`.

cws-careful routes back to `/cws-resync`. The user re-invokes.

Phase 1.D continues (gate cleared). Impact set:

- `./.cws/02-build/manifest.md` (the permissions block itself)
- `./.cws/02-package/moderation-justifications.md` (re-write per added permission)
- `./.cws/03-launch/listing.md` (description mentions URL scope)
- `./.cws/04-promote/fb-ads.md` (compliance re-review expected)

Phase 4: D2 — recommend A. User confirms.

Phase 5: route to `/cws-build` first (manifest is the source of truth for
the permission block).

### Example C — Banner cosmetic-only

User message: "I tweaked the banner — bumped the title color from #333
to #2a2a2a for contrast."

Phase 0: type C. D1 not needed; type is clear.

Phase 1.C: ask the cosmetic-vs-structural sub-question. User confirms
cosmetic.

Impact set, narrowed:

- `./.cws/03-launch/banners.md`
- CWS Developer Dashboard draft re-upload
- (Welcome Page SKIPPED — cosmetic exception, IRON RULE 6.4)
- (FB rectangular SKIPPED — color tweak doesn't invalidate the creative)

Phase 4: D2 — recommend A. User confirms.

Phase 5: route to `/cws-launch` for the asset re-upload.

### Example D — Pre-launch no-op

User message: "I changed the name in 01-idea.md."

Preamble: `LAUNCH_STATUS: pre-launch`.

Phase 0 STOPs. Tell the user: "Pre-launch — no published artifacts to
propagate to. Edit the listing copy directly in cws-package; everything
downstream will pick up the new name on first run."

Route to `/cws-package`. Exit.

### Example E — Two simultaneous triggers — SPLIT

User message: "I changed the name AND widened host_permissions."

Phase 0 detects two triggers. IRON RULE 6.6 fires.

Respond: "Two distinct triggers — name keyword (cascade through
cws-package, cws-launch, cws-promote) and host_permissions (HARD GATE
through cws-careful before any cascade). I'll handle host_permissions
first because it has the hard gate; re-invoke /cws-resync for the name
cascade after the careful gate clears."

Run Phase 1.D for host_permissions. Route to cws-careful. Exit.

When the user returns and re-invokes, the name-keyword cascade runs as
Example A.

### Example F — Google account migration (Type F)

User message: "We're moving the publishing account from `dev@…` to
`launcher-1@…`."

Phase 0: type F. D1 confirms.

Phase 1.F impact set:

- `./.cws/00-account-setup.md` (the account artifact)
- Dolphin profile rebuild via `cws-dolphin create` on the new account
- CWS support migration request (manual, 1-5 day SLA)

Surface the SLA prominently:

> The published extension does NOT auto-migrate. You need to either
> (a) file a CWS support ticket for ownership transfer (1-5 business
> days, mostly low-touch), or (b) republish under the new account and
> manually re-acquire users (loses all reviews, ratings, install
> history — usually a last resort).

Phase 4: D2 — recommend A (computed order: account setup first, then
Dolphin rebuild, then file support request, then resume normal stages
once transfer confirms).

Phase 5: route to `/cws-init` (which holds account setup) or to
`/cws-dolphin` directly if the account artifact only needs the Dolphin
rebuild. The choice depends on whether the user has already set up the
new Google account; the route plan adapts.

---

## Phase 8 — Edge cases and recovery

### 8.1 Resync interrupted mid-cascade

The user closes the session after Phase 5 routes to the first downstream
skill but before that skill completes. State:

- `.resync.log` has the cascade entry.
- `state.json` has `resync.route_plan` and `resync.route_index = 0`.
- The first downstream artifact is marked `superseded`.

On the next session, when the user invokes any cws-* skill, the preamble
sees the in-flight resync in state.json. The skill should:

- If it's the next skill in `route_plan`, run in resync mode.
- If it's a DIFFERENT skill, surface the in-flight resync as a warning
  and ask whether to resume the cascade or proceed with the unrelated
  skill (and route_index stays put).

Resuming is the safe default. Proceeding with an unrelated skill while
artifacts are superseded risks compounding stale state.

### 8.2 Downstream skill fails on re-run

A downstream skill in the cascade fails (e.g. Localizer rate-limits on
the 53-locale re-translation). The skill should NOT increment
`route_index`. It surfaces the failure, leaves the artifact `superseded`,
and routes back to the user. The user fixes the upstream issue and
re-invokes the same skill; route_index stays put until the skill
completes cleanly.

cws-resync does not handle retries — that's the downstream skill's
responsibility.

### 8.3 The user wants to ABORT a cascade

After D2 confirmation but before the cascade completes, the user wants
to revert. They run `/cws-resync --abort` (or equivalently say "abort the
resync"). cws-resync:

- Reads `.resync.log` for the latest cascade entry.
- For each artifact in that entry's impact set with
  `status: superseded`, flips back to the `prior_status` and removes the
  `superseded_by_resync` field.
- Appends an `abort` line to `.resync.log` for audit.
- Clears `resync` block from state.json.

Iron rule: abort restores the FRONTMATTER state. It does NOT restore the
upstream change that triggered the cascade — that's the user's edit, and
the user owns reverting it via git.

### 8.4 A downstream artifact was deleted between Phase 1 and Phase 2

The user deleted `./.cws/03-launch/welcome-page.md` between detecting
the impact set and running the supersede edit. Phase 2 cannot edit a
file that doesn't exist.

Mechanical handling: note the absence in the route plan ("welcome-page.md
not present — cws-launch will produce it"), do NOT fail the cascade, and
continue.

### 8.5 The user edited an artifact body during the cascade

After Phase 5 routes to cws-package, the user opens
`./.cws/03-launch/welcome-page.md` (which is `status: superseded`) and
makes manual edits. When cws-launch later runs in resync mode, it sees:

- `status: superseded`
- `superseded_by_resync: <ts>`
- A body that differs from `prior_status: complete`

The skill should treat the manual edits as user input and FOLD them into
the re-run, not discard them. The cascade is best-effort; the user's
edits are authoritative.

If the manual edits CONTRADICT the upstream change (e.g. the user
reverted the name keyword in the Welcome Page body), cws-launch surfaces
the contradiction and asks the user to choose. cws-resync does not
pre-empt this.

---

## Phase 9 — Propagation matrix summary (one block, for scanning)

| Trigger type | Hard gate | Mandatory locales | Mandatory dogfood | Mandatory moderation re-submit | Mandatory ad re-review |
|---|---|---|---|---|---|
| A) Name keyword | — | ✅ | — | depends on if listing changed | likely |
| B) Full description | — | ✅ | — | ✅ | possible |
| C) Banner / icon | — | — | — | ✅ (asset re-upload) | possible (rectangular only) |
| D) host_permissions widened | **cws-careful** | — | — | ✅ | ✅ (FB compliance) |
| E) Extension type / manifest | — | depends | ✅ (1-2 days) | ✅ | likely |
| F) Google account migration | possibly cws-careful | — | — | depends (transfer path) | — |

Reading the matrix: each row is a trigger type. The columns are the
common cascade obligations. ✅ = mandatory; "—" = not applicable; "depends"
= conditional on the specific edit (covered in the per-type phase).

If a future trigger type emerges that isn't in the matrix, the right move
is to add a row here AND a Phase 1.X section above — not to fold it into
an existing row. The matrix earns its keep by being scannable.

---

## Skill Routing Footer

The default exit is the first skill in the confirmed route plan from D2.

```
Next: /cws-<first-in-plan>
Why: First downstream stage with a superseded artifact. The skill will
detect `status: superseded` on its frontmatter and run in resync mode
(focus on the delta, not a full re-build).
```

If the user picked D2 option C (defer):

```
Next: (deferred)
Why: Impact set marked, log written. Re-invoke /cws-resync when ready to
run the cascade.
```

If the trigger required cws-careful first (Phase 1.D):

```
Next: /cws-careful
Why: host_permissions widening is a hard gate. Run cws-careful to build
the re-consent plan; cws-careful will route back to /cws-resync on
completion.
```

If the launch is pre-launch (Phase 0 no-op):

```
Next: /cws-<CURRENT_STAGE>
Why: Pre-launch — nothing to propagate to. Edit the stage artifact
directly; cws-resync earns its keep only after the launch ships.
```
