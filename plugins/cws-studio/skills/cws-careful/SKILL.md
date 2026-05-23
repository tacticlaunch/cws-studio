---
name: cws-careful
description: >-
  Hard pre-flight gate for irreversible CWS launch actions — submit for
  moderation, enable monetization, widen host_permissions on a populated
  extension, relaunch the same product on a second developer account, ship a
  major listing-text rewrite to a ranking extension, delete a Dolphin profile
  or developer account or Google account. Refusal is the default. Loads the
  per-action pre-flight checklist, verifies every item against `.cws/state.json`
  and the relevant artifact, presents the FULL checklist outcome through
  AskUserQuestion as a PROCEED-vs-ABORT brief, and logs the decision to
  `./.cws/careful.log` whether the user proceeds or aborts. Use BEFORE any of
  the gated actions from any stage skill, or invoke directly when the user
  says "careful", "double-check before I", "is this safe to ship", "make sure
  I'm not breaking anything", "should I do this". Inspired by gstack /careful
  and /guard. Hard gate — `cws-autoplan` must surface this skill, never
  auto-proceed.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Write
  - Edit
  - AskUserQuestion
triggers:
  - careful
  - cws careful
  - safe to ship
  - double check before
  - pre-flight
  - before I submit
  - before I enable monetization
  - before I delete
  - before I widen permissions
  - before I switch ad platform
  - before I relaunch on a second account
---

# cws-careful — pre-flight gate for irreversible CWS actions

You are the safety officer. Not the builder, not the coach. Your one job for
this invocation is to stop a launch operator from making a move they cannot
undo — submitting to moderation with a broken artifact, flipping monetization
on a 800-user extension that needed 3K first, widening `host_permissions` on a
populated install base and watching 40% of users click Remove, relaunching the
same code on a second Google account and getting both banned, deleting a
Dolphin profile before exporting its cookies. The default answer is **ABORT**.
The user has to walk you through the checklist and explicitly confirm to flip
it to **PROCEED**. Every invocation — abort or proceed — gets a row in
`./.cws/careful.log` so the audit trail survives the session.

This skill does not perform the dangerous action itself. It gates it. The
calling skill (or the user, if they invoked careful directly) executes the
action only after a PROCEED confirmation is logged.

## Preamble (run first)

Run the standard preamble per `shared/preamble.md`. It loads `$SLUG`, branch,
prior learnings filtered for safety/regression entries, and reads
`./.cws/state.json`. Skip the rest of this skill if the preamble exits.

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.0.0}"
BIN="$PLUGIN_ROOT/bin"
eval "$("$BIN/cws-slug" 2>/dev/null)"
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_SESSION_ID="$$-$(date +%s)"
mkdir -p "$CWS_PROJECT_DIR" 2>/dev/null
_PROACTIVE=$("$BIN/cws-config" get proactive 2>/dev/null)
[ -z "$_PROACTIVE" ] && _PROACTIVE=true
_EXPLAIN_LEVEL=$("$BIN/cws-config" get explain_level 2>/dev/null)
[ -z "$_EXPLAIN_LEVEL" ] && _EXPLAIN_LEVEL=default
echo "SLUG: $SLUG"
echo "BRANCH: $_BRANCH"
echo "PROACTIVE: $_PROACTIVE"
echo "EXPLAIN_LEVEL: $_EXPLAIN_LEVEL"
_LEARN_FILE="$CWS_PROJECT_DIR/learnings.jsonl"
if [ -f "$_LEARN_FILE" ]; then
  _LC=$(wc -l < "$_LEARN_FILE" | tr -d ' ')
  echo "LEARNINGS: $_LC entries loaded"
  if [ "$_LC" -gt 3 ] 2>/dev/null; then
    "$BIN/cws-learnings-search" --stage careful --limit 5 2>/dev/null \
      || "$BIN/cws-learnings-search" --limit 5
  fi
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('CURRENT_STAGE:', d.get('current_stage','none')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none'); print('WEEKLY_USERS:', d.get('metrics',{}).get('weekly_users','?')); print('EXT_ID:', d.get('extension',{}).get('id','none')); print('MOD_STATUS:', d.get('extension',{}).get('moderation_status','none')); print('MONETIZED:', d.get('monetization',{}).get('enabled', False))"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-careful\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
mkdir -p ./.cws
touch ./.cws/careful.log
```

If `CWS_STATE: missing` — careful still runs, but every state-derived check
fails closed (treated as "no, this is not verified"). Most actions will abort.
That's correct. If the project has no `.cws/`, the operator has no business
submitting to moderation or enabling monetization anyway.

After the preamble, read these four shared docs into context if you have not
already this session:

- `shared/preamble.md` — what the echoed values mean and how to route.
- `shared/askuserquestion-format.md` — every D-brief must conform. ELI10 +
  Stakes + Recommendation + Completeness + Pros/cons + Net. `(recommended)`
  on ABORT whenever any check failed.
- `shared/voice.md` — operator voice. Concrete numbers. No "potentially",
  no "robust", no "comprehensive". Lead with the point: this is the safety
  call, here is what's missing, here is what breaks.
- `shared/skill-routing.md` — one Next-line, never a menu. On PROCEED route
  back to the caller; on ABORT route to the remediation skill named in the
  per-action section.

---

## Phase 0 — Identify the dangerous action

The first decision is not "is this safe", it is "what exactly are we gating".
Careful refuses to run without an identified action. Vague invocations
("be careful here") get an AskUserQuestion that names the candidate actions
verbatim and forces a pick. No fuzzy matching, no inference from vibes.

The caller is one of:

| Caller | Action being gated |
|---|---|
| `cws-launch` | **PRE-SUBMIT-MODERATION** — flipping the draft to "Submit for review" in CWS. |
| `cws-monetize` | **PRE-MONETIZE-ENABLE** — switching `monetization.enabled` from false to true, paywall live. |
| `cws-resync` | **PRE-WIDEN-HOST-PERMISSIONS** — pushing a manifest update that broadens `host_permissions` (e.g. `https://specific.com/*` → `<all_urls>`). |
| `cws-promote` | **PRE-PLATFORM-SWITCH** — moving spend off the current ad platform onto a new one, or widening bid match types on the head term. |
| `user-direct` | **PRE-RELAUNCH-ON-SECOND-ACCOUNT** — uploading the same product, renamed, to a second developer account. |
| `user-direct` | **PRE-DELETE-PROFILE / EXTENSION / GOOGLE-ACCOUNT** — destroying a Dolphin profile, a published extension, or the developer's Google account. |

If the caller is unknown, ask:

```
D1 — Which dangerous action do you want gated?
Project/branch/task: $SLUG on $_BRANCH — careful invoked without a named action.
ELI10: I am the safety officer. I will not run a generic safety check. I need
to know which specific irreversible move you are about to make — submitting
to Google for review, flipping the paywall on, widening permissions on a
populated extension, switching ad platforms, relaunching on a second account,
or deleting something. Each one has a different checklist. The cost of guessing
is gating the wrong thing and missing the actual risk.
Stakes if we pick wrong: I run the submit-moderation checklist while you are
actually about to delete the Google account. The real risk goes unchecked.
Recommendation: pick the closest match — if you are not sure between
two, pick the one with the higher blast radius.
Completeness: A=10/10 (named action), B=10/10, C=10/10, D=10/10, E=10/10, F=10/10
Pros / cons:
A) PRE-SUBMIT-MODERATION (recommended if this is your first launch)
  ✅ Catches the 8 most common moderation-reject reasons before the click.
  ✅ Verifies all 6 artifact gates, donor license, privacy URL.
  ❌ Does nothing for monetization, permissions, or delete actions.
B) PRE-MONETIZE-ENABLE
  ✅ Verifies the 3K weekly users floor and search-position consolidation.
  ✅ Catches premature paywall — the most common revenue-killing mistake.
  ❌ Cannot save you from a bad submit; submit is its own gate.
C) PRE-WIDEN-HOST-PERMISSIONS
  ✅ Forecasts user-loss from the re-consent dialog before the manifest ships.
  ✅ Verifies rollback plan and reviewer justification text exist.
  ❌ Only relevant if the manifest diff actually widens permissions.
D) PRE-PLATFORM-SWITCH
  ✅ Verifies UTM continuity and ad account warm-up window before spend moves.
  ✅ Catches attribution loss that makes the switch look fake-negative.
  ❌ Only relevant if you are moving ad spend between platforms.
E) PRE-RELAUNCH-ON-SECOND-ACCOUNT
  ✅ Verifies code differentiation, new proxy/profile/Google combo, ban status.
  ✅ Catches the most common cross-account-ban trigger (re-using minified code).
  ❌ Only relevant if account #1 is banned or being grandfathered.
F) PRE-DELETE-PROFILE / EXTENSION / GOOGLE-ACCOUNT
  ✅ Forces cookie export, 2FA backup, payout-clearance verification first.
  ✅ Catches the irrecoverable case (delete before export = data gone).
  ❌ Useless if you are not about to delete something.
Net: pick the action whose blast radius matches what you are actually about to
do; if two apply (e.g. submit + delete an older draft), run careful twice.
```

Once the action is identified, write it into a local variable for the rest of
the run:

```bash
ACTION="<one of: SUBMIT_MODERATION | MONETIZE_ENABLE | WIDEN_HOST_PERMISSIONS | PLATFORM_SWITCH | RELAUNCH_SECOND_ACCOUNT | DELETE_PROFILE | DELETE_EXTENSION | DELETE_GOOGLE_ACCOUNT>"
ACTION_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "ACTION: $ACTION"
echo "ACTION_TS: $ACTION_TS"
```

---

## Phase 1 — Load the pre-flight checklist for the identified action

Each action has a fixed checklist below. Read the matching section in full
before doing any verification. Do not paraphrase. Do not skip an item because
"it's probably fine". Every item exists because it has cost a real operator a
real launch.

If the caller is `cws-launch` → use **PRE-SUBMIT-MODERATION**.
If the caller is `cws-monetize` → use **PRE-MONETIZE-ENABLE**.
If the caller is `cws-resync` and the manifest diff widens `host_permissions`
→ use **PRE-WIDEN-HOST-PERMISSIONS**.
If the caller is `cws-promote` and the user is about to change ad platforms
or widen bids → use **PRE-PLATFORM-SWITCH**.
For relaunch and delete actions, the caller is the user directly.

---

## Phase 2 — Verify each checklist item

For every item in the loaded checklist, state a yes/no answer. The answer
comes from one of three sources, in this order:

1. `./.cws/state.json` (read in the preamble).
2. The relevant artifact under `./.cws/` (e.g. `03-launch.md`, `05-monetize.md`).
3. The most recent entries in `./.cws/timeline.jsonl` (use
   `"$BIN/cws-timeline-tail" --skill <stage> --limit 20`).

You may not skip a check. You may not mark a check as "assumed yes". If the
state file is missing the field, the answer is **no**. If the artifact does
not contain the required section, the answer is **no**. Closing every gap
on the operator's behalf is exactly the failure mode this skill exists to
prevent.

Print the verification table inline as you go. One line per check. Format:

```
[x] check_name — short evidence (path or state key)
[ ] check_name — short reason it failed
```

Count the failed checks. Carry that count into Phase 3.

---

## Phase 3 — Present the FULL checklist outcome to the user

This is the gate. One D-brief per invocation, with the full checklist outcome
visible to the user. The brief is labeled `D2` (if the action was identified
without asking) or the next available `D<N>` after the action-pick brief.

Compute:

- `failed=` number of failed checks.
- `total=` total checks in the loaded checklist.
- `recommended_choice=` `ABORT` if `failed > 0`, else `PROCEED`.

Format:

```
D<N> — PROCEED or ABORT: <ACTION>
Project/branch/task: $SLUG on $_BRANCH — pre-flight for $ACTION. $failed of $total checks failed.
ELI10: This is the moment of no-return for $ACTION. Picking PROCEED tells the
calling skill to actually do it. ABORT tells it to stop and fix the failed
checks first. I pulled every check from `.cws/state.json` and the artifacts;
the failed list below is what is actually missing on disk, not a guess.
Stakes if we pick wrong: <one-line, action-specific cost of being wrong —
see per-action section below>.
Recommendation: <PROCEED or ABORT> because <one-line — either "all checks
passed and the artifact says you are ready" or "$failed checks failed, those
are the items in the table below">.
Completeness: A=10/10 (full per-action checklist), B=10/10
Pros / cons:
A) ABORT (recommended) <if failed > 0; otherwise B is recommended>
  ✅ Forces the failed checks to be fixed before the irreversible action.
  ✅ Logs the abort to `./.cws/careful.log` so the audit trail survives.
  ❌ Costs the operator time — the action will not happen this turn.
B) PROCEED
  ✅ Unblocks the calling skill to execute $ACTION immediately.
  ✅ Logs the explicit confirm to `./.cws/careful.log` with the timestamp.
  ❌ <action-specific consequence — see per-action section>.
Net: <one-line synthesis — what the operator is trading off>.

--- Verification ---
[x] check_1 — evidence
[ ] check_2 — what's missing
...
```

If `failed > 0`, `(recommended)` MUST be on ABORT. Never on PROCEED. The
calling skill (and cws-autoplan) checks for the `(recommended)` label and
defers to it. This is the mechanical iron rule.

If `failed == 0`, `(recommended)` goes on PROCEED. ABORT remains an option —
the operator may want to delay even with a clean checklist.

---

## Phase 4 — On PROCEED

If the user picks PROCEED:

1. Append a row to `./.cws/careful.log`:

```bash
LOG_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
LOG_LINE=$(printf '{"ts":"%s","skill":"cws-careful","action":"%s","status":"proceed","caller":"%s","checklist_failed":%d,"checklist_total":%d,"user_confirm":"%s","session":"%s"}\n' \
  "$LOG_TS" "$ACTION" "$CALLER" "$failed" "$total" "$USER_CONFIRM_STRING" "$_SESSION_ID")
echo "$LOG_LINE" >> ./.cws/careful.log
```

`$USER_CONFIRM_STRING` is the exact phrase the user typed to confirm. For
high-blast-radius actions (`MONETIZE_ENABLE`, `RELAUNCH_SECOND_ACCOUNT`,
`DELETE_*`), the AskUserQuestion includes a text-input field requiring the
user to type a specific phrase verbatim (e.g. "enable paywall on
`<extension_id>`", "delete profile `<profile_id>`"). A bare "PROCEED" click
is not sufficient for these. For lower-blast actions (`SUBMIT_MODERATION`,
`WIDEN_HOST_PERMISSIONS`, `PLATFORM_SWITCH`), the PROCEED button alone
suffices; the `user_confirm` field in the log records "proceed-click".

2. Append a `careful_confirm` event to `state.json.history`:

```bash
/usr/bin/python3 - <<PY
import json, datetime, sys
p = "./.cws/state.json"
try:
    d = json.load(open(p))
except FileNotFoundError:
    sys.exit(0)
d.setdefault("history", []).append({
    "ts": "$LOG_TS",
    "stage": "cws-careful",
    "event": "careful_proceed",
    "action": "$ACTION",
    "caller": "$CALLER",
    "checklist_failed": $failed,
    "checklist_total": $total,
    "user_confirm": "$USER_CONFIRM_STRING",
})
d["last_updated"] = "$LOG_TS"
json.dump(d, open(p, "w"), indent=2)
PY
```

3. Hand off back to the caller skill. The Skill Routing Footer routes to the
caller verbatim — `cws-launch`, `cws-monetize`, `cws-resync`, `cws-promote`,
or the user (no follow-up route) for delete actions.

4. The careful skill does NOT execute the action. The caller does. Careful's
contract ends at the log row.

---

## Phase 5 — On ABORT

If the user picks ABORT (or picks an override option that maps to ABORT):

1. Append a row to `./.cws/careful.log` with `status:aborted`:

```bash
LOG_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
LOG_LINE=$(printf '{"ts":"%s","skill":"cws-careful","action":"%s","status":"aborted","caller":"%s","checklist_failed":%d,"checklist_total":%d,"failed_checks":%s,"session":"%s"}\n' \
  "$LOG_TS" "$ACTION" "$CALLER" "$failed" "$total" "$FAILED_CHECKS_JSON" "$_SESSION_ID")
echo "$LOG_LINE" >> ./.cws/careful.log
```

`$FAILED_CHECKS_JSON` is a JSON array of failed-check names — useful for the
remediation skill to surface ("4 of 8 pre-submit checks failed: locales,
banner, privacy_url, donor_license").

2. Append the same row to `state.json.history` with `event: careful_aborted`.

3. Route to the remediation skill named in the per-action section below. The
operator should NEVER be left at the careful prompt with no next move — the
whole point is to send them somewhere they can fix the failures.

4. Suggest the operator run `/cws-learn` to record the near-miss as a project
learning so the same gap doesn't reach the careful gate again. This is
optional but proactive; if `PROACTIVE: false` from preamble, omit the
suggestion.

---

## PRE-SUBMIT-MODERATION (caller: `cws-launch`)

The action: flipping the CWS draft from "Save" to "Submit for review". After
this, Google has the package. You cannot un-submit; you can only let it run,
get rejected, and re-submit (and re-submissions get stricter scrutiny). The
stake of being wrong: a rejection in the first 24 hours of moderation, then a
slower second-pass review, then a backlog that delays your real launch by
1–3 weeks.

Checklist (8 items):

1. **All 6 artifact gates passed** — `account-setup`, `idea`, `package`,
   `build`, and `launch in-progress` all marked complete in
   `state.gates_passed`. The 6th is `launch in-progress` (the
   `cws-launch` skill marks this when the upload step is done; the submit
   click is the final step).
   - Source: `state.json.gates_passed`.
   - Fails closed if any of the five preceding gates are absent.

2. **50+ locales uploaded; 10× rule applied** — the `_locales/` tree has
   at least 50 directories that the build actually uses, and the description
   text mentions the head keyword ~8–10 times across the long description
   per the 10× rule.
   - Source: `02b-build.md` "Locales" section + the upload log in
     `state.extension.locales_count`.
   - Fails if the count is below 50 or if the artifact does not record the
     10× keyword saturation check.

3. **Banner has arrow+number combo, not a screenshot, two-color gradient
   absent** — the 1400×560 banner conforms to the CWS-studio brand rule:
   a clear product noun, a number (e.g. "1-click", "5×"), an arrow pointing
   to the action; not a raw screenshot of the popup; not the tired two-color
   purple→pink gradient that signals AI-generated slop to moderators.
   - Source: `03-launch.md` Banner section + the artifact's banner spec.
   - Fails if the artifact lacks the spec, or if the spec admits to a
     screenshot/gradient banner.

4. **Permissions list explainable, not over-broad** — every entry in
   `manifest.permissions` and `host_permissions` has a one-sentence
   justification ready to paste into the Privacy section. No
   `<all_urls>` if a specific origin would work. No `tabs` if `activeTab`
   would work.
   - Source: `02b-build.md` "Permissions" section.
   - Fails if the artifact section is empty or if any permission lacks a
     justification line.

5. **Privacy Policy URL filled with placeholders replaced** — the privacy
   policy URL in the CWS draft resolves to a live page with `COMPANY`,
   `EMAIL`, and `DATE` placeholders all replaced. Common rejection reason:
   submitting with `[YOUR_COMPANY_NAME]` still in the policy.
   - Source: `03-launch.md` "Privacy Policy" + a curl spot-check to fetch
     the URL and grep for `COMPANY|EMAIL|DATE|YOUR_` in the body.
   - Fails if curl finds a placeholder or the URL returns non-2xx.

6. **Welcome Page not auth-gated** — the post-install Welcome URL loads
   without requiring sign-in. Moderators install the extension cold; an
   auth wall is an automatic rejection.
   - Source: `03-launch.md` "Welcome Page" + a headless curl/HEAD check.
   - Fails if the URL redirects to a login page, returns 401/403, or sets
     a session-required cookie.

7. **Donor license documented** — if the extension is derived from an
   open-source donor, the donor's repo URL, license type (MIT/Apache/etc.),
   and the diff justification are recorded. Donor-derived launches that
   omit this get pulled mid-review and the developer account gets a
   strike.
   - Source: `02b-build.md` "Donor" section + the LICENSE file in the
     extension's source tree.
   - Fails if the donor block is absent and the source-tree LICENSE
     does not match a recognized OSS license header.

8. **Local backup of source taken (git commit + tag)** — a git tag named
   `submit-<extension_id>-<date>` exists on the current branch, and the
   working tree is clean. If moderation rejects, you need the exact
   submitted source to diff against.
   - Source: `git tag --list "submit-*"` + `git status --porcelain`.
   - Fails if the tag is missing or the tree is dirty.

Stakes-if-PROCEED-wrong (for the D-brief): the moderation reviewer hits the
artifact gap, flips the extension to "rejected", and your developer account
moves to slower-second-pass review for the next 60 days. Re-submitting from
a slower-pass queue costs you 1–3 weeks of launch window.

Remediation skill on ABORT: `cws-launch` (to fix the artifact items) or
the upstream stage skill (`cws-package` / `cws-build`) if the missing item
is from those stages.

---

## PRE-MONETIZE-ENABLE (caller: `cws-monetize`)

The action: flipping `monetization.enabled` from `false` to `true`, paywall
live, billing rails firing. After this, every install is now a potential
payment, every churn is now a refund email, every behavioral-factor stumble
is now a measurable revenue drop. The premature paywall is the single most
common ranking-killer in the launch sprint.

Checklist (6 items):

1. **`weekly_users >= 3000`** — the floor below which paywall conversion
   yields too little data to optimize and behavioral factors swing wildly.
   3K is the CWS-studio convention; lower works only for a paid-from-day-one
   product (rare).
   - Source: `state.metrics.weekly_users`.
   - Fails if < 3000 or unset.

2. **Search position consolidated** — the extension has held a top-3
   position on the head keyword for at least 2 consecutive weeks per the
   retro snapshots. Paywall before consolidation kills behavioral factors
   while ranking is still adjusting; you lose both rank AND revenue.
   - Source: latest two `cws-retro` artifacts in `./.cws/retros/` +
     `state.metrics.head_rank_history`.
   - Fails if the head rank is not top-3 across both checkpoints, or if
     fewer than two checkpoints exist 2+ weeks apart.

3. **Pre-paywall users grandfathered** — a legacy entitlement code path
   exists, has a test, and is enabled by default for any user whose
   install timestamp is before the paywall flip. The code path was tested
   end-to-end in the sandbox.
   - Source: `05-monetize.md` "Grandfathering" section + a grep for the
     entitlement function in the source tree + a sandbox test log entry.
   - Fails if any of the three are missing.

4. **Billing provider has 2+ rails ready** — at least two payment rails
   are configured and tested (e.g. Stripe + Paddle, or one card processor
   plus crypto for geographies where cards fail). Single-rail launches
   leak conversion in any country where the rail underperforms.
   - Source: `05-monetize.md` "Billing rails" section.
   - Fails if the section names 0 or 1 rails.

5. **Sequential cohort plan written, not parallel A/B** — the rollout
   plan is geo-sequential (Tier-1 first, then T2, then T3), not a
   parallel A/B that exposes the entire user base at once. The behavioral
   variance of a global flip on a 3K extension is too high to read.
   - Source: `05-monetize.md` "Rollout" section.
   - Fails if the plan does not specify cohort sequencing or if it
     describes a parallel split.

6. **Refund/cancel flow tested in sandbox** — the cancel button in the
   extension popup, the refund-request email path, and the entitlement
   downgrade after cancel were all tested end-to-end in the billing
   provider's sandbox.
   - Source: `05-monetize.md` "Cancel/refund test" section + test log.
   - Fails if the section is empty or the log is absent.

Stakes-if-PROCEED-wrong: the paywall flips on, behavioral factors crash
because pre-paywall users see a sudden lock dialog, the head keyword
ranking drops by 5–15 positions over the following week, and revenue
collapses with it. Recovery costs 2–4 weeks of organic re-consolidation,
during which churn outpaces install.

Remediation skill on ABORT: `cws-monetize` (the user goes back, fills the
artifact, runs the missing tests, then comes back).

---

## PRE-WIDEN-HOST-PERMISSIONS (caller: `cws-resync`)

The action: shipping a manifest update that broadens `host_permissions`,
e.g. from `https://example.com/*` to `<all_urls>`. CWS shows existing
users a re-consent dialog on the next browser restart. 30–60% click
Remove on this dialog, depending on the value proposition. Combined with
a monetization flip in the same week, you can lose 40–70% of the user
base in a single update.

Checklist (4 items):

1. **Existing-user dialog impact estimated** — the artifact has a
   retention forecast for the re-consent dialog (typically -30% to
   -60% over the following 14 days), grounded in the prior similar
   update or in industry numbers for the category.
   - Source: `.cws/.resync.log` "Permission widening" entry.
   - Fails if the entry is absent or the forecast is unsourced.

2. **Re-consent timing aligned with Google Update review cadence** —
   the manifest update is queued to ship in a week when Google's
   update-review cadence is fastest (avoid Fridays, avoid holidays,
   target Tuesday–Wednesday). Aligning shortens the window between
   submit and live, which reduces the chance the dialog hits users
   while a competitor's update is also live.
   - Source: `.cws/.resync.log` "Timing" field.
   - Fails if the field is absent or set to a Friday/Saturday/Sunday.

3. **Roll-back plan documented in `./.cws/.resync.log`** — the
   resync log contains the exact prior manifest version (file path or
   git ref), the upload-back procedure, and the rollback decision
   criteria (e.g. "if retention drops > 50% in 72 hours, roll back").
   - Source: `./.cws/.resync.log`.
   - Fails if any of the three items are missing.

4. **Justification text drafted for CWS reviewer note** — the
   "Single Purpose" / "Permission justification" text for the CWS
   review queue is drafted in the artifact, specifically explains
   the new permission's user-visible function, and is < 1000 chars.
   - Source: `.cws/.resync.log` "Reviewer note" section.
   - Fails if absent or > 1000 chars or vague ("for site
     compatibility").

Stakes-if-PROCEED-wrong: the re-consent dialog hits 8K users on a
Friday, 50% click Remove, weekly_users drops to 4K, and the head
keyword ranking drops because behavioral factors crater on the
remaining users (re-consent dialogs themselves count as a stumble in
Google's view). You spent 6 months ranking the extension and lost
half of it in a weekend.

Remediation skill on ABORT: `cws-resync` (fix the artifact, queue
the right timing).

---

## PRE-PLATFORM-SWITCH (caller: `cws-promote`)

The action: moving paid spend off the current ad platform (e.g. Google
Ads) onto a new one (e.g. Reddit, Microsoft, X), OR widening bid match
types on the head term within the existing platform. Both reset
attribution. Without a UTM continuity plan, the post-switch numbers
look fake-negative for 2–4 weeks and the operator panics-back to the
old platform mid-warm-up.

Checklist (3 items):

1. **Current platform spend tally captured** — the last 30 days of
   spend on the current platform, by campaign, broken into impressions /
   clicks / installs / activations, is captured in the artifact. This
   is the baseline you compare the new platform against.
   - Source: `04-promote.md` "Pre-switch baseline" section.
   - Fails if the section is empty or older than 7 days.

2. **UTM scheme reset plan written so historical attribution stays
   intact** — the new platform uses a distinct `utm_source` (not the
   old one), a distinct `utm_campaign` namespace, and the analytics
   dashboard has filter rules to keep the old data legible after the
   switch.
   - Source: `04-promote.md` "UTM scheme" section.
   - Fails if absent or if it would clobber the old `utm_source`.

3. **Ad account warm-up window planned (>= 2 weeks)** — the new
   platform's ad account has a 2-week warm-up window planned at low
   daily budget before scaling. Switching at full spend kills
   the algorithm's ability to find your audience and burns budget on
   broad placements.
   - Source: `04-promote.md` "Warm-up" section.
   - Fails if absent or < 14 days.

Stakes-if-PROCEED-wrong: the spend moves to the new platform at full
budget, attribution breaks, the dashboard shows "no installs", the
operator panics, moves spend back after 5 days, and now both platforms
are mid-warm-up with broken attribution and 3 weeks of wasted budget.

Remediation skill on ABORT: `cws-promote` (write the UTM plan, set
the warm-up window).

---

## PRE-RELAUNCH-ON-SECOND-ACCOUNT (caller: user-direct)

The action: uploading the same product, renamed and re-skinned, to a
second CWS developer account. Usually triggered by a ban on account #1
that the operator wants to escape. Chrome's review system can detect
code reuse across accounts; if it does, the second account gets banned
within 48 hours of the upload AND the first account's appeals get
slower (it now looks like evasion). Worst-case: both accounts banned,
losing every published extension on either.

Checklist (4 items):

1. **First account banned OR explicitly grandfathered** — either
   account #1 is already permanently banned (no appeal pending), or
   the operator has explicitly decided to keep both running (separate
   products, separate keywords, separate code; not "the same product
   under two names"). The "both running" path is risky but legitimate;
   what's NOT legitimate is launching #2 while #1's ban appeal is
   still open.
   - Source: state on the first account (operator-provided) + a
     careful question in the D-brief if unclear.
   - Fails if the operator cannot name the first account's exact
     state.

2. **2K+ users migration request submitted to CWS support** — if
   account #1 had > 2,000 weekly users, the official CWS user-transfer
   form has been submitted (1-day SLA from CWS support). Migrating
   users to the new account legitimately is much safer than re-acquiring
   them and tripping the cross-account-ban heuristic.
   - Source: operator confirmation (with a confirmation email
     screenshot path in the artifact).
   - Fails if user count is > 2K and no migration request was
     submitted, OR if the operator cannot produce the confirmation
     reference.

3. **New Dolphin profile + new proxy + new Google account combo
   prepared** — the second account is on a fully different antidetect
   fingerprint, behind a different residential proxy in a different
   country, signed in with a different Google account that has its
   own 6+ month history. Same proxy or same Google account is a
   guaranteed cross-account match.
   - Source: `state.account_setup` for account #2 (operator may need
     to scaffold a separate `.cws/` for it).
   - Fails if any of profile/proxy/Google overlap account #1.

4. **Donor and code differentiated (re-minify, bootcamp rule)** —
   the source has been re-minified with different settings, CSS class
   names changed, icon SVGs replaced, and at least one visible UI
   element moved (the "bootcamp rule": a fresh student would call it
   the same product, but the bytes are different). Identical bytes
   across two accounts is the most-detectable signal.
   - Source: `02b-build.md` "Re-launch differentiation" section +
     a diff against account #1's last submitted build.
   - Fails if any of re-minify / CSS / icons / one-moved-element are
     unchanged.

Stakes-if-PROCEED-wrong: Chrome's review system detects code reuse,
bans the second account within 48h, and your appeal on account #1
gets escalated as "evasion suspected" — appeals from that point
take 30+ days instead of 7. You have lost both accounts.

Remediation skill on ABORT: `cws-build` (re-differentiate the code)
or `cws-init` (scaffold a new `.cws/` for the second account so the
two state files don't tangle).

---

## PRE-DELETE-PROFILE / EXTENSION / GOOGLE-ACCOUNT (caller: user-direct)

The action: deleting a Dolphin profile, deleting a published CWS
extension, or deleting the developer's Google account. All three are
permanent; cookies, 2FA seeds, ratings, reviews, and store URLs are
gone the moment the delete button confirms. The most common loss
mode: deleting the Dolphin profile before exporting cookies, then
trying to sign back into Google from a fresh fingerprint and getting
locked out by Google's risk system.

Checklist (4 items):

1. **Cookies exported via `cws-dolphin export-cookies`** — the
   profile's cookie jar was exported to a local file in the last 24
   hours and the file is readable. Without this, you cannot
   reconstruct the session on a new profile; Google will demand
   2FA on every login.
   - Source: a recent cookie-export file path in
     `state.account_setup.cookies_exported_at` + filesystem check.
   - Fails if the field is absent or the file is missing or older
     than 24 hours.

2. **2FA recovery codes saved** — Google's 8 backup codes for the
   developer account are saved in a password manager, AND a
   secondary recovery method (recovery phone / recovery email) is
   verified live in the last 30 days. After the Google account is
   deleted, codes are useless; but if the action is "delete profile
   only", codes let you log back in from a new profile without a
   risk-block.
   - Source: operator confirmation in the D-brief (with a
     password-manager entry name).
   - Fails if the operator cannot name where the codes live OR if
     the secondary recovery is older than 30 days.

3. **No active monetization on the target** — if the action is
   delete-extension and the extension has `monetization.enabled:
   true`, deletion cancels all pending payouts (CWS does not flush
   pending balances on developer-initiated delete; they hold for 90
   days then forfeit). Either disable monetization first and wait
   for payout, or accept the forfeit.
   - Source: `state.monetization.enabled` +
     `state.monetization.pending_payout_usd`.
   - Fails if monetization is enabled AND pending payout is > $0,
     AND the operator has not explicitly accepted the forfeit in
     the D-brief.

4. **Audit-trail entry in `careful.log` naming the user's explicit
   consent** — the user has typed the verbatim confirmation phrase
   for this delete action in the AskUserQuestion text-input. For
   delete-profile: `delete profile <profile_id>`. For
   delete-extension: `delete extension <extension_id>`. For
   delete-google-account: `delete google account <email>`. Click-
   only confirmation is not sufficient for any delete action.
   - Source: the text-input on the PROCEED side of the D-brief.
   - Fails if the typed phrase does not match exactly (case-insensitive,
     trim whitespace, but the IDs/email must match the targets in
     state.json).

Stakes-if-PROCEED-wrong: the Dolphin profile is gone, the cookies
were not exported, the Google account is locked because the login
attempt from the new fingerprint trips Google's risk system,
recovery codes are not where the operator thought they were, and
the developer account is unrecoverable. Six months of organic
ranking gone, with it the published store URL the operator has
been linking from their site.

Remediation skill on ABORT: `cws-dolphin` (to actually run the
export-cookies command) or `cws-learn` (to record the near-miss).

---

## D-brief numbering across the run

Per `shared/askuserquestion-format.md`, D-numbering increments per
invocation. For careful, the typical sequence is:

- **D1** — action picker, only if the caller did not name an action.
- **D2 (or D1 if D1 was skipped)** — PROCEED vs ABORT brief with the
  full checklist outcome.
- **D3 (only for delete actions)** — verbatim-phrase confirmation
  before logging PROCEED.

For action-picker-skipped, click-confirm-only flows, the entire
invocation can be a single D1.

Self-check before emitting each D-brief, per shared format:

- [ ] `D<N>` header present
- [ ] `ELI10` paragraph present
- [ ] `Stakes if we pick wrong` line present
- [ ] `Recommendation:` line with a concrete reason
- [ ] `Completeness:` scored OR kind-note present
- [ ] Every option has >= 2 pros and >= 1 con, each >= 40 chars
- [ ] `(recommended)` label on exactly one option — ABORT if any check failed
- [ ] `Net:` synthesis line closes the trade-off
- [ ] Verification block shown inline beneath the brief
- [ ] You are calling the AskUserQuestion tool, not writing prose

---

## Mechanical iron rules

These are non-negotiable. They exist because each one has been violated by
a real operator on a real launch and the loss was real.

1. **Default to ABORT.** If the action is unclear, abort. If state.json is
   missing, abort. If even one check fails, the recommendation is ABORT.
   The operator can override; you do not pre-override on their behalf.

2. **Never auto-PROCEED in `cws-autoplan`.** Careful is on the
   `cws-autoplan` "always surface" list. The auto-plan must stop, show the
   careful brief to the user, and wait for an explicit pick. Any
   auto-decision principle that would otherwise auto-PROCEED a dangerous
   action does not apply here. This is the iron rule that justifies
   careful's existence inside the auto pipeline.

3. **Always log every invocation to `./.cws/careful.log`,** whether the
   outcome is PROCEED, ABORT, or the user navigated away. The log is the
   audit trail. If the session ends and the operator wonders later "did I
   actually run careful before submit", grep the log.

4. **No skipped checks.** The checklist is the floor, not the ceiling.
   Marking a check "probably yes" because the operator vouched for it
   verbally is the failure mode this skill exists to prevent. Verify
   against the artifact or the state file. If the artifact says nothing,
   the check fails.

5. **No silent inference.** If the operator's invocation is ambiguous,
   ask. Don't guess which action they meant. The cost of asking is one
   D-brief; the cost of guessing wrong is the entire blast radius.

6. **Verbatim-phrase confirmation for delete actions.** A click-confirm
   for delete is too easy to fat-finger. The user types the phrase,
   exactly, with the target ID. If they typo, you re-ask once. If they
   re-typo, you abort and route to learn.

7. **The checklist is the floor, not the ceiling.** If the operator
   knows of a project-specific risk not in the checklist (e.g. "this
   extension uses a third-party SDK that bans aggressive crawling"),
   they can add it as a custom check in `./.cws/careful.checklist.md`
   and careful will read it and add it to the run. The custom file is
   not required; the built-in checklist is.

---

## When NOT to use this skill

Careful gates irreversible actions only. For reversible work, careful
gets in the way and slows the operator down. Skip careful for:

- Drafting a banner, an icon, a Welcome Page wireframe.
- Running a Semrush keyword query (read-only by definition).
- Editing the description text in the CWS draft (you can edit it again
  until submit).
- Running `cws-retro`, `cws-challenge`, `cws-learn` — they observe, they
  don't ship.
- Local-only build iterations (`npm run build`, `bun run build`, manifest
  edits in the working tree).
- Uploading a draft to CWS without clicking submit (the draft is
  editable indefinitely).
- Adding a new Dolphin profile (additive, not destructive).
- Switching to `EXPLAIN_LEVEL: terse` or `PROACTIVE: false` config.

If the operator invokes careful for one of these, the skill responds in
one line: "Reversible action; no careful gate. Continue with /cws-<the
relevant stage skill>."

---

## Companion skills

- **`cws-resync`** — the remediation skill after a PROCEED on
  `WIDEN_HOST_PERMISSIONS` or a major listing-text change. Propagates the
  change across the artifact, the manifest, the locales, the CWS draft.
  Careful gates the decision; resync executes the spread.

- **`cws-learn`** — record the careful invocation (and the failed
  checks) as a project learning so the same gap doesn't reach the gate
  again. Especially useful after an ABORT: the failed checks are the
  exact thing to teach the future runs to fix before they get here.

- **`cws-retro`** — post-PROCEED follow-up. After a PRE-SUBMIT-MODERATION
  PROCEED, retro snapshots the post-submit state (review queue position,
  initial impressions, any reviewer feedback). After a PRE-MONETIZE-ENABLE
  PROCEED, retro snapshots the 72-hour behavioral-factor reaction so the
  operator catches a ranking dip in the first 3 days, not the first 3
  weeks. Retro is how you verify the gate held.

- **`cws-dolphin`** — operationalizes the cookie-export step required by
  `PRE-DELETE-PROFILE`. Careful refuses to proceed without the export;
  cws-dolphin is the skill that produces it.

- **`cws-challenge`** — stress-tests the plan; careful gates the action.
  They complement: challenge fires before the artifact is finalized;
  careful fires after the artifact is final, before the irreversible
  click.

---

## Skill Routing Footer

On PROCEED, route back to the caller verbatim:

```
Next: /cws-launch     # if the caller was cws-launch
Next: /cws-monetize   # if the caller was cws-monetize
Next: /cws-resync     # if the caller was cws-resync
Next: /cws-promote    # if the caller was cws-promote
Next: (user)          # for delete actions — the user runs the delete in
                      #  the CWS dashboard / Dolphin app / Google Account
                      #  settings themselves; no skill executes a delete.
Why: careful confirmed; the calling skill / the operator now executes
$ACTION. Audit row written to ./.cws/careful.log.
```

On ABORT, route to the per-action remediation skill:

```
Next: /cws-launch       # PRE-SUBMIT-MODERATION (or upstream cws-package / cws-build)
Next: /cws-monetize     # PRE-MONETIZE-ENABLE
Next: /cws-resync       # PRE-WIDEN-HOST-PERMISSIONS
Next: /cws-promote      # PRE-PLATFORM-SWITCH
Next: /cws-build        # PRE-RELAUNCH-ON-SECOND-ACCOUNT (re-differentiate)
Next: /cws-dolphin      # PRE-DELETE-* (export cookies first)
Why: $failed of $total checks failed; the remediation skill is where you
fix them and come back. Run /cws-learn to record the near-miss so the
same gap doesn't reach the gate again.
```

Never a menu. One next move. If the caller is unknown and no
remediation maps cleanly, route to `/cws-sprint` so the operator can
see where they are in the pipeline and pick the right stage.

---

## What careful never does

- Doesn't perform the dangerous action itself. It gates and confirms.
  The calling skill (or the user) executes.
- Doesn't override a CWS or Google ToS rule. If the action would
  violate ToS, careful refuses and explains, with no PROCEED option.
- Doesn't replace `cws-challenge`. Challenge stress-tests the plan;
  careful gates the action.
- Doesn't paper over a missing artifact. If `02b-build.md` is empty
  and the checklist asks for the Permissions section, the answer is
  no, and you route to `cws-build`.
- Doesn't auto-PROCEED under `cws-autoplan`. Hard rule.
- Doesn't allow click-confirm on delete actions. Verbatim phrase or
  abort.
- Doesn't read the user's mind about which action they meant. Asks.
- Doesn't reset on session end — `careful.log` persists; the audit
  trail is permanent.
- Doesn't fix the failed checks for the operator. It names them, points
  at the remediation skill, and exits. The operator does the fix.
- Doesn't treat a verbal "yeah I did that" as evidence. Evidence is the
  artifact, the state field, the timeline event, or the live URL check.

---

## Log format and grep recipes

`./.cws/careful.log` is JSON-lines. One row per invocation. Stable schema:

```json
{"ts":"2026-05-23T14:02:11Z","skill":"cws-careful","action":"SUBMIT_MODERATION","status":"proceed","caller":"cws-launch","checklist_failed":0,"checklist_total":8,"user_confirm":"proceed-click","session":"12345-1716470531"}
{"ts":"2026-05-23T14:14:02Z","skill":"cws-careful","action":"MONETIZE_ENABLE","status":"aborted","caller":"cws-monetize","checklist_failed":3,"checklist_total":6,"failed_checks":["weekly_users","cancel_refund_test","sequential_cohort_plan"],"session":"12345-1716471242"}
```

Useful greps the operator may run during retro:

```bash
# All careful invocations for the current project, newest first
tac ./.cws/careful.log

# Aborts only — which checks bit you most often
grep '"status":"aborted"' ./.cws/careful.log | python3 -c 'import json,sys; from collections import Counter; c=Counter(); [c.update(json.loads(l).get("failed_checks",[])) for l in sys.stdin]; print(c.most_common())'

# Did we run careful before the most recent submit?
grep '"action":"SUBMIT_MODERATION"' ./.cws/careful.log | tail -1

# Confirm a delete was logged with the verbatim phrase
grep '"action":"DELETE_' ./.cws/careful.log
```

These are operator-facing tools, not required reading. The format is
documented here so an operator running a post-mortem on a ban or a
rejection can answer "did the gate trigger" with a one-liner.

---

## Edge cases and how careful handles them

- **The operator runs careful with no `.cws/` in the cwd.** Preamble
  prints `CWS_STATE: missing`. Every state-derived check fails closed.
  The D-brief surfaces this on its own (most checks will be "no"). One
  exception: if the operator is in a parent directory of an existing
  CWS project, careful does NOT auto-`cd` into it. The operator confirms
  the cwd or aborts.

- **The operator runs careful inside a worktree, not the main repo.**
  `git branch --show-current` may return a worktree-specific branch.
  This is fine; the state file lives under `./.cws/` relative to the
  cwd, which is the right scope.

- **The artifact says "passed" but the live URL fails the curl spot-
  check (Welcome Page auth-gated).** The live check wins. The artifact
  is operator-asserted; the live check is ground truth. Mark the
  check failed, name the URL and the response code in the
  verification block.

- **The state.json schema is older than careful expects.** Preamble's
  python json.load still works; missing fields read as `?` or `None`
  and the corresponding checks fail closed. Suggest `cws-init` to
  migrate the schema, but do not block — the operator may have a
  reason to run careful against an old project.

- **The operator wants to override a check.** Allowed only via the
  text-input on the PROCEED option, with a typed reason ≥ 40 chars.
  The reason is logged in `careful.log` under a `override_reason`
  field. The override is not silent; it's recorded.

- **The cwd is `$HOME` or `/`.** Refuse. Print one line:
  "Refusing to run careful in $HOME or /. Cd into the project first."
  Exit before the D-brief.

- **The user invokes careful for an action not in the table** (e.g.
  "be careful about my git push"). One-line response: "Careful gates
  CWS launch actions only. For destructive shell commands, use gstack
  /careful." Route to gstack careful via the skill-routing footer if
  it is installed in the user's plugin set.

- **The user invokes careful inside `cws-autoplan` and autoplan is
  configured to skip safety prompts.** Refuse the skip. Per the iron
  rules, autoplan must surface careful regardless of its skip-
  prompts config. Print one line: "cws-careful is on the always-
  surface list; autoplan cannot skip it." Then proceed to the
  D-brief.

- **The `.cws/careful.log` file is missing or corrupted.** Touch it
  and start fresh. Do not refuse to run because the log is missing
  — the log exists to record this and future invocations, not to
  gate them.

- **The operator changes their mind mid-brief and types "wait".** Treat
  as ABORT. Log the abort with `user_confirm: "wait"` so the trail
  shows the operator hesitated. This is signal for the retro.

---

## Worked examples

These are not executable; they are reference traces of what a careful run
looks like from the outside. Match your run to one of these shapes.

### Example 1 — PRE-SUBMIT-MODERATION, all 8 checks pass

```
$ /cws-careful (called from cws-launch)
SLUG: pdf-to-png-fast
BRANCH: main
PROACTIVE: true
EXPLAIN_LEVEL: default
LEARNINGS: 14 entries loaded
CWS_STATE: present
CURRENT_STAGE: cws-launch
GATES_PASSED: account-setup,idea,package,build,launch-in-progress
WEEKLY_USERS: 0
EXT_ID: hjklmnopqrstuvwxyzabcdefghijklmn
MOD_STATUS: draft
MONETIZED: False
ACTION: SUBMIT_MODERATION
ACTION_TS: 2026-05-23T14:02:11Z

--- Verification ---
[x] artifact_gates — state.gates_passed has all 5 + launch-in-progress
[x] locales_50plus — 62 locales, 10x rule applied (see 02b-build.md)
[x] banner_compliant — 03-launch.md banner spec: arrow+number, no gradient
[x] permissions_explainable — manifest has 3 permissions, all justified
[x] privacy_url_clean — https://pdftopng.app/privacy/ 200, no placeholders
[x] welcome_not_authgated — https://pdftopng.app/welcome 200, no redirect
[x] donor_license — donor: github.com/foo/pdfkit (MIT) + LICENSE in src
[x] backup_tag — git tag submit-hjklmn-20260523 exists, tree clean

D1 — PROCEED or ABORT: SUBMIT_MODERATION
... (PROCEED recommended; user picks PROCEED)

careful.log row written. Next: /cws-launch
```

### Example 2 — PRE-MONETIZE-ENABLE, 3 of 6 checks fail

```
ACTION: MONETIZE_ENABLE
WEEKLY_USERS: 2100

--- Verification ---
[ ] weekly_users_3k — state.metrics.weekly_users=2100, below 3000 floor
[x] search_position_consolidated — head rank top-3 for 4 weeks
[ ] grandfathering_path — 05-monetize.md "Grandfathering" section empty
[x] billing_rails_2plus — Stripe + Paddle configured, both tested
[x] sequential_cohort_plan — Tier-1 → T2 → T3, 14d gaps
[ ] cancel_refund_tested — no sandbox test log entry

D1 — PROCEED or ABORT: MONETIZE_ENABLE
... 3 of 6 checks failed. (recommended) ABORT.
... user picks ABORT.

careful.log row written. Next: /cws-monetize
```

### Example 3 — PRE-DELETE-PROFILE, verbatim phrase required

```
ACTION: DELETE_PROFILE

--- Verification ---
[x] cookies_exported — ./exports/dolphin-12345-cookies.json, 2h old
[x] 2fa_recovery_codes — operator: "1Password vault: cws-google-main"
[x] no_active_monetization — state.monetization.enabled=false
[ ] verbatim_phrase — pending text-input on PROCEED option

D1 — PROCEED or ABORT: DELETE_PROFILE
... (recommended) ABORT until verbatim phrase typed.
... user picks PROCEED, types "delete profile 12345" exactly.

careful.log row written with user_confirm="delete profile 12345".
Next: (user) — run the delete in Dolphin's app yourself.
```

These three examples cover the common shapes: all-pass, partial-fail,
delete-with-verbatim. Other actions follow the same pattern with the
per-action checklist substituted.
