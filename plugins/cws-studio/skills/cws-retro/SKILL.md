---
name: cws-retro
description: >-
  Post-launch metrics retrospective for a published Chrome Web Store extension.
  Pulls CWS dashboard (weekly users, install rate, uninstall rate, country
  split), GA4 (first_visit, install, with the Linux-bot exclusion), ad-platform
  spend and cost-per-install, review velocity and rating, and the head-keyword
  SERP position. Computes per-funnel deltas vs the previous retro, flags any
  metric outside playbook benchmark norms, and stamps a dated snapshot under
  `./.cws/retro/YYYY-MM-DD.md` so trends are visible across weeks and months.
  Two cadences — weekly during the early launch window (< 90 days post-publish
  or < 5K weekly users), monthly afterwards. Triggers on "how's my extension
  doing", "did the experiment work", "is this product growing", "what changed
  last week", "weekly retro", "monthly retro", "retro on my extension". Closes
  the loop on the sprint — the gstack `/retro` equivalent for CWS launches.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - WebFetch
  - AskUserQuestion
triggers:
  - how's my extension doing
  - did the experiment work
  - is this product growing
  - what changed last week
  - weekly retro
  - monthly retro
  - retro on my extension
---

# cws-retro — post-launch metrics retrospective

You are running a CWS launch operator's standing retro. Pulls the dashboard,
GA4, ads, reviews, SERP — diffs every funnel stage against the previous retro
and against playbook benchmark norms — writes a dated snapshot to
`./.cws/retro/YYYY-MM-DD.md` — recommends exactly one next skill.

A retro is **observational**. It never pushes code, never flips a stage gate,
never auto-launches an experiment. It surfaces the truth of the funnel and
points at whichever skill ought to act on what it found.

## Preamble (run first)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.3.0}"
BIN="$PLUGIN_ROOT/bin"
eval "$("$BIN/cws-slug" 2>/dev/null)"
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_SESSION_ID="$$-$(date +%s)"
mkdir -p "$CWS_PROJECT_DIR" 2>/dev/null
mkdir -p ./.cws/retro 2>/dev/null
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
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --stage retro --limit 3
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 - <<'PY'
import json, datetime, pathlib
p = pathlib.Path('./.cws/state.json')
d = json.loads(p.read_text())
print('CURRENT_STAGE:', d.get('current_stage','none'))
print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none')
pub = (d.get('launch') or {}).get('published_at') or d.get('published_at')
print('PUBLISHED_AT:', pub or 'unknown')
if pub:
    try:
        ts = datetime.datetime.fromisoformat(pub.replace('Z','+00:00'))
        days = (datetime.datetime.now(datetime.timezone.utc) - ts).days
        print('DAYS_SINCE_PUBLISH:', days)
    except Exception:
        print('DAYS_SINCE_PUBLISH: unknown')
else:
    print('DAYS_SINCE_PUBLISH: unknown')
lm = d.get('latest_metrics') or {}
print('LATEST_WEEKLY_USERS:', lm.get('weekly_users','unknown'))
print('LATEST_CADENCE:', (d.get('retro') or {}).get('cadence','undefined'))
PY
else
  echo "CWS_STATE: missing"
fi
# Find the most recent prior retro for delta computation
_PRIOR_RETRO=$(ls -1t ./.cws/retro/*.md 2>/dev/null | head -1)
[ -n "$_PRIOR_RETRO" ] && echo "PRIOR_RETRO: $_PRIOR_RETRO" || echo "PRIOR_RETRO: none"
"$BIN/cws-timeline-log" "{\"skill\":\"cws-retro\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

If `CWS_STATE: missing`, the extension hasn't been initialised. Route to
`/cws-init` and stop — there's nothing to retro.

If `GATES_PASSED` does not contain `launch` (i.e. nothing's been submitted to
CWS yet), stop. See the "When NOT to use" section. There's no data to retro.

## Shared canon

- **AskUserQuestion format** — see `../../shared/askuserquestion-format.md`. Every
  decision is a `D<N>` brief (ELI10 · Stakes · Recommendation · Completeness
  · Pros/cons · Net). D-numbering starts at D1 per invocation.
- **Voice** — see `../../shared/voice.md`. Operator-to-operator. No banners. No
  file-creation dumps. Lead with the point. Concrete numbers always.
- **Skill routing footer** — see `../../shared/skill-routing.md`. End with exactly
  one `Next: /cws-<skill>` recommendation. Never a menu.
- **Preamble** — see `../../shared/preamble.md`. The block above is the canonical
  per-skill instance.

---

## Phase 0 — read state, choose cadence

Read the preamble echo: `CURRENT_STAGE`, `GATES_PASSED`, `PUBLISHED_AT`,
`DAYS_SINCE_PUBLISH`, `LATEST_WEEKLY_USERS`, `LATEST_CADENCE`, `PRIOR_RETRO`.

**Mechanical cadence rule (no question if both signals agree):**

- `DAYS_SINCE_PUBLISH < 90` **AND** `LATEST_WEEKLY_USERS < 5000` → **weekly**.
- `DAYS_SINCE_PUBLISH ≥ 90` **AND** `LATEST_WEEKLY_USERS ≥ 5000` → **monthly**.

The 5K threshold is the published playbook transition: pre-5K, behavioral
signal swings week-to-week and a missed regression kills you; post-5K (and
post-monetization), week-to-week noise dominates and monthly is the right
zoom level (`cws-monetize/references/monetization-scaling.md` — "grow to
4–5K weekly active users, then add monetization").

If the two signals disagree, or `LATEST_CADENCE` is `undefined`, ask:

```
D1 — Weekly or monthly cadence for this retro?
Project/branch/task: $SLUG on $_BRANCH, published <DAYS_SINCE_PUBLISH> days
ago at <LATEST_WEEKLY_USERS> weekly users.
ELI10: Retros come in two zoom levels. Weekly is tight: every behavioral wobble
matters during Google's 1–2 month test window, and small drops kill rankings
fast. Monthly is the right zoom once the product has settled — past ~5K
weekly users or past the 90-day SEO test horizon — because day-to-day noise
washes out and you'd just be reading static.
Stakes if we pick wrong: weekly on a settled product wastes a half-hour every
seven days flagging noise as signal. Monthly on a launch-window product means
a behavioral regression goes 30 days before anyone notices, and at that
point search position is already gone.
Recommendation: <weekly if DAYS_SINCE_PUBLISH<90 OR LATEST_WEEKLY_USERS<5000;
else monthly> because <one of the two thresholds applies>.
Completeness: A=10/10, B=10/10
Pros / cons:
A) Weekly cadence (recommended if pre-5K or pre-90d)
  ✅ Catches behavioral-factor drops inside Google's test window when it counts
  ✅ Forces seven-day discipline on uninstall and review velocity
  ❌ Adds about thirty minutes of operator time every single week
B) Monthly cadence (recommended once past 5K users and 90 days)
  ✅ Cuts cadence overhead by ~4x once product has stabilized
  ✅ Aligns with monetization cohort math (paying-conversion needs >7d windows)
  ❌ A regression can run 30 days before being caught
Net: weekly until both thresholds cross, then monthly — pick the one the
state already says you should be on.
```

Persist the chosen cadence so the next invocation doesn't ask again unless
the thresholds re-trigger:

```bash
/usr/bin/python3 - "$_CHOSEN_CADENCE" <<'PY'
import json, sys, pathlib, datetime
cadence = sys.argv[1]  # "weekly" | "monthly"
p = pathlib.Path('./.cws/state.json')
d = json.loads(p.read_text())
d.setdefault('retro', {})['cadence'] = cadence
d['retro']['cadence_set_at'] = datetime.datetime.utcnow().isoformat()+'Z'
d['last_updated'] = datetime.datetime.utcnow().isoformat()+'Z'
p.write_text(json.dumps(d, indent=2))
PY
```

The window used for deltas:

- **weekly cadence** — compare against the most recent retro ≤ 8 days old. If
  the latest prior retro is > 8 days old, label the delta `stale-prior` and
  proceed against whatever the latest is (regression detection is muted for
  this one snapshot only).
- **monthly cadence** — compare against the most recent retro ≤ 35 days old.
  Same `stale-prior` rule for older priors.

Regression detection (Phase 5) **always compares against the previous retro
file**, never against a launch-day baseline. Stale anchors lie. The thirty-day
rolling window is enforced by file selection (`PRIOR_RETRO`), not by reading
ancient artifacts.

---

## Phase 1 — snapshot timestamp and project metadata

Stamp the retro filename from local date. ISO format, midnight-aligned:

```bash
_TODAY=$(date +%Y-%m-%d)
_SNAPSHOT="./.cws/retro/${_TODAY}.md"
echo "SNAPSHOT_PATH: $_SNAPSHOT"
if [ -f "$_SNAPSHOT" ]; then
  echo "SNAPSHOT_EXISTS: yes — will overwrite at Phase 7"
fi
```

If a snapshot for today already exists, that's fine — the new run overwrites
it. Same-day re-runs happen when the operator pulls a fresh dashboard CSV
and wants the delta recomputed.

Capture the project metadata block (used in the frontmatter at Phase 7):

```bash
/usr/bin/python3 - <<'PY'
import json, pathlib
d = json.loads(pathlib.Path('./.cws/state.json').read_text())
idea = d.get('idea', {}) or {}
launch = d.get('launch', {}) or {}
print('NAME_KEYWORD:', idea.get('name_keyword','unknown'))
print('US_VOLUME_EXACT:', idea.get('us_volume_exact','unknown'))
print('EXTENSION_ID:', launch.get('extension_id','unknown'))
print('STORE_URL:', launch.get('store_url','unknown'))
PY
```

The store URL is what you'll WebFetch for the rating + review count in
Phase 2.6. The name keyword is what you'll search for SERP position in
Phase 2.5. The extension ID is the unique CWS handle for the dashboard pull.

---

## Phase 2 — collect raw numbers

Five sources, in order. Each one can fall back to "paste it" if automatic
ingest isn't available.

### 2.1 — CWS dashboard

The Chrome Web Store developer dashboard is **login-walled**. There is no
public API and `WebFetch` from a logged-in session is not reliable across
machines. Ask the operator how they want to feed it in:

```
D2 — How are we pulling the CWS dashboard numbers?
Project/branch/task: $SLUG retro for $_TODAY, dashboard is login-walled.
ELI10: The Chrome Web Store dashboard lives behind a Google login the
agent can't reach. Either you've already saved a CSV export, or you paste
the four numbers (weekly users, installs, uninstalls, top countries) and
the agent does the math.
Stakes if we pick wrong: a wrong install or uninstall number poisons every
downstream conversion calculation and silently flips green to red or red
to green. Paste from the dashboard, not from memory.
Recommendation: B (paste the four numbers) because it's the path that works
on every machine in under two minutes, and the CSV export from CWS rarely
contains the rolling-window data we need anyway.
Completeness: A=8/10, B=10/10
Pros / cons:
A) Paste a CSV export from the dashboard
  ✅ Captures per-day installs and uninstalls in one shot for trend math
  ✅ Reusable: re-running the retro just re-reads the file
  ❌ CWS export schema changes occasionally and the parser will need a fix
B) Paste the four headline numbers directly (recommended)
  ✅ Works on every machine right now, no schema drift
  ✅ Forces operator eyes on the dashboard which often catches surprises
  ❌ No per-day breakdown so monthly cadence loses some granularity
Net: paste the headline numbers for speed; CSV path stays available if the
operator already has the file open.
```

If A (CSV): ask for the file path (drop under `./.cws/retro/raw/`) and parse
weekly_users, install count for the cadence window, uninstall count for
the same window, top-3 country split.

If B (paste): ask for these four explicitly:

1. **Weekly users (now)** — the headline on the CWS dashboard's "Users" tab.
2. **Installs (last 7 days)** for weekly cadence, or **last 30 days** for
   monthly. From "Installs & Uninstalls".
3. **Uninstalls** for the same window.
4. **Top-3 country split** as `US:42%, IN:18%, BR:9%` — the country tab of
   the dashboard, sorted by users (not by installs, because uninstall geo
   is more informative than acquisition geo for behavioral diagnostics).

Compute:

- **install_rate = installs / first_visits** — needs GA4 input from 2.2.
  Held until that runs.
- **uninstall_rate_w1 = uninstalls / installs** over the cadence window.
  This is the rate that matters most. Benchmark is week-1 specifically;
  weekly cadence reads this directly, monthly cadence reads a smoothed
  version and the regression threshold scales accordingly.

Save raw paste into `./.cws/retro/raw/${_TODAY}-dashboard.txt` for audit.

### 2.2 — GA4 (with the Linux-bot exclusion segment)

GA4 inside CWS is the only place where the listing-visit funnel is visible.
Two events matter: `first_visit` (unique listing visit) and `install` (the
beacon CWS fires when a user installs from the listing).

The playbook's published quirk: **after CWS moderation, Facebook ad bots
flood the listing from Linux**. They don't install but they inflate
`first_visit`. The fix is a GA4 segment that excludes `OS contains Linux`.
The "real" conversion is typically **~3x higher** than the unfiltered number
(promotion.md L399-404).

The agent cannot create GA4 segments. It can only read the numbers the
operator pastes. Ask:

```
D3 — Do you already have the Linux-excluded GA4 segment applied?
Project/branch/task: $SLUG retro, GA4 numbers needed for install_rate.
ELI10: GA4's listing-visit count includes Facebook ad bots that visit from
Linux and never install. Without the Linux-excluded segment the
install_rate looks roughly three times worse than it actually is, and the
benchmark check below will throw a false regression flag.
Stakes if we pick wrong: a 22% real conversion will display as 7%, the
retro will demand `cws-resync`, you'll waste a week debugging a healthy
product, and meanwhile actual regressions get drowned in noise.
Recommendation: A (segment is applied) because the playbook procedure
requires this exact segment to be live before the first retro, and if it
isn't the answer is to go set it up before continuing.
Completeness: A=10/10, B=4/10
Pros / cons:
A) Segment applied — paste the segmented first_visit + install (recommended)
  ✅ Numbers will match the playbook's 15-30% organic conversion benchmark
  ✅ Distinguishes real users from FB moderation-check bots cleanly
  ❌ Operator needs to confirm in GA4 that the segment is on, not assumed
B) No segment — paste raw numbers and accept ~3x inflated first_visit
  ✅ Faster for the first retro if segment isn't set up yet
  ❌ Every benchmark flag becomes unreliable until segment is added
  ❌ False regressions will be flagged and downstream skills will misfire
Net: A is the only correct answer; B exists only to surface the missing
prerequisite so the operator goes and creates the segment.
```

If B: stop, point at `cws-promote/references/promotion.md` lines 156-160
("Filter Facebook bots before computing conversion"), and recommend
re-running once the segment is live. Don't proceed with retro math.

If A, ask for two numbers — both filtered:

1. **first_visit (cadence window)** — segmented count.
2. **install (cadence window)** — segmented count.

Compute:

- **install_rate = install / first_visit**
- **ga4_install_drift = abs(install_ga4 − installs_cws) / installs_cws** —
  the GA4-vs-CWS drift. Playbook documents that GA4 attribution is
  imperfect and CWS install count lags 5-7 days (cws-retro original stub
  notes). A drift over 20% is the alarm.

### 2.3 — Ad platform

If the operator is running paid traffic, pull the cadence-window numbers
from whichever ad platform's in use. Google Ads, Facebook Ads, Yandex,
RU CIS networks all behave the same shape:

- **spend** (currency the operator's billed in)
- **impressions**
- **clicks**
- **CTR = clicks / impressions**
- **cost_per_install (CPI) = spend / installs_from_ads**

`installs_from_ads` is the tricky one. From promotion.md: the operator runs
ads with UTM tags and `installs_from_ads ≈ installs_in_window − baseline_daily × window_days`.
The baseline is the pre-ad organic install rate. If state.json has a
pre-ads baseline saved under `latest_metrics.baseline_daily_installs`,
use it; otherwise ask:

```
D4 — Daily baseline organic installs before ads started?
ELI10: Ad-driven installs are computed as (installs in window) minus
(organic baseline × days). Without a baseline, CPI is unreliable.
Stakes if we pick wrong: CPI is the only metric that matters for ad
profitability decisions per promotion.md — get it wrong and you'll
kill a profitable campaign or feed a leaky one.
Recommendation: paste the operator's best estimate of organic installs/day
from the week before ads turned on, because that's the only honest baseline.
Completeness: A=9/10, B=6/10
Pros / cons:
A) Paste the pre-ad baseline (recommended)
  ✅ Anchors CPI math to the operator's actual organic floor
  ✅ Reusable across retros once persisted to state.json
  ❌ Operator has to look this up if it wasn't recorded
B) Skip ad attribution entirely and mark CPI as "unknown"
  ✅ Faster when no ads are running
  ❌ Loses the CPI signal that ties spend to install economics
Net: pasted baseline is correct when ads are live; skip is fine if no ads.
```

If no ads are running: skip the ad block, mark this retro's frontmatter
`cost_per_install: null`, move on.

### 2.4 — Reviews

Front-page WebFetch of the listing page captures rating and review count
publicly. No login needed.

```bash
# operator pasted STORE_URL via state.json
WebFetch --url "$STORE_URL" --prompt "Extract the rating (X.Y format) and the
review count (integer). Also list the 3 most recent review snippets (date,
star count, first 80 chars of text). Return as JSON with keys:
rating_now, reviews_total, recent_reviews."
```

Parse the response, capture:

- **rating_now** (e.g. 4.6)
- **reviews_total** (e.g. 12)
- **recent_reviews** array — used for the narrative if any are hostile

Compute, against the prior retro:

- **review_velocity = (reviews_total − reviews_prior) / days_since_prior_retro**
  — reviews per day. Useful for "is the review widget working" diagnostics.
- **rating_delta = rating_now − rating_prior** — a 0.5+ swing in either
  direction is a flag.

### 2.5 — Search position (head keyword)

The head keyword is in `state.json` under `idea.name_keyword`. Two searches:

```bash
# CWS search — the keyword as a user would type it inside chrome.google.com/webstore
WebFetch --url "https://chromewebstore.google.com/search/$(printf '%s' "$NAME_KEYWORD" | sed 's/ /%20/g')" \
  --prompt "List the first 10 extension titles and their store URLs in order
of appearance. Return as JSON array."
# Google SERP — same query
WebFetch --url "https://www.google.com/search?q=$(printf '%s' "$NAME_KEYWORD chrome extension" | sed 's/ /+/g')" \
  --prompt "List the first 10 result titles and URLs. For each, note whether
it points to chromewebstore.google.com (treat that as an 'extension hit')
or elsewhere. Return as JSON array."
```

Find the operator's extension in each list (match by `STORE_URL` or
`EXTENSION_ID`). Capture:

- **search_position_cws** — rank in CWS search (1..10, or `>10` if not in
  top 10).
- **search_position_google** — rank on Google SERP (same scheme).

The "head" benchmark from the playbook is **top-3 on Google for the name
keyword by month 6**. Earlier than month 6, rank moves; the regression
detector cares about *direction* (improving / flat / dropping) more than
absolute number.

### 2.6 — Linux OS share in ads (bot infiltration check)

If ads are running and the ad platform exposes OS breakdown (Google Ads
under Audience → Devices, Facebook Ads under Demographics → Platform),
ask:

```
D5 — Linux OS share of paid clicks (this cadence window)?
ELI10: When a paid ad campaign starts pulling Linux clicks above ~5%, it
almost always means a bot farm has gotten into the audience. They click,
inflate spend, never install. CPI explodes.
Stakes if we pick wrong: missing this lets a bot infiltration burn ad
budget for a full cadence cycle. Playbook threshold: Linux > 5% of
ad clicks = alarm.
Recommendation: paste the number from the ad platform's OS breakdown if it
exists, or "unknown" if the platform doesn't expose it.
Completeness: A=10/10, B=10/10, C=5/10
Pros / cons:
A) Paste a real percentage (recommended)
  ✅ Catches the most common ad-budget hemorrhage pattern early
  ✅ Single mechanical threshold, no judgment needed
  ❌ Operator has to navigate ad platform UI
B) Mark "unknown — platform doesn't expose OS"
  ✅ Honest about ad platforms that hide OS data
  ❌ Loses the bot-infiltration tripwire entirely
C) Skip — no ads running
  ✅ Not relevant when there's no spend
  ❌ — (hard stop, this is the no-ads case)
Net: paste a number when ads are live and the platform shows it; skip when
no ads.
```

Save as **linux_os_share_ads** (percentage), or `null`.

---

## Phase 3 — compute deltas vs prior retro

If `PRIOR_RETRO` is `none` (this is the baseline retro):

- No deltas computed; all "delta" columns in the snapshot table read `—`.
- No regression flags raised (regression detection requires a prior).
- Frontmatter `regression_flags: []`.
- Snapshot is labeled "baseline" in the headline.

If `PRIOR_RETRO` exists, parse its frontmatter:

```bash
/usr/bin/python3 - "$_PRIOR_RETRO" <<'PY'
import sys, pathlib, re
text = pathlib.Path(sys.argv[1]).read_text()
m = re.search(r'^---\n(.*?)\n---', text, flags=re.DOTALL)
if not m:
    print('PRIOR_PARSE: no_frontmatter')
    sys.exit(0)
import yaml
fm = yaml.safe_load(m.group(1))
for k in ('date','cadence','weekly_users','install_rate','uninstall_rate',
          'search_position_head','cost_per_install','reviews_total',
          'reviews_avg','regression_flags'):
    print(f'PRIOR_{k.upper()}:', fm.get(k))
PY
```

(If `yaml` isn't available — it usually is on macOS python3 — fall back to
a hand-rolled `key: value` line parser; only frontmatter scalars matter.)

For each metric, compute the absolute and relative delta:

```
weekly_users:       Δ = now − prior,  % = (now − prior)/prior * 100
install_rate:       Δ in percentage points (not relative)
uninstall_rate:     Δ in percentage points
cost_per_install:   Δ = now − prior, % = relative
reviews_total:      Δ = now − prior  (always non-negative, modulo review removal)
rating_now:         Δ = now − prior
search_position_*:  Δ = position now − position prior (negative = improvement)
```

Compute `days_since_prior_retro = today − prior.date`. Used for the
"stale-prior" label and for review velocity.

Tag the prior comparison:

- If `prior.cadence != this.cadence`, label as **cadence-transition** in the
  snapshot. Deltas are still computed; regression detection runs with the
  monthly thresholds (more lenient).
- If `days_since_prior_retro > 8` on weekly cadence, or `> 35` on monthly,
  label as **stale-prior** and suppress regression flags for this snapshot
  only.

---

## Phase 4 — benchmark check (mechanical iron rules)

Each rule below is a single mechanical threshold. No judgment. Each rule
either passes silently or appends a flag to `regression_flags`. Sources
sit in plugin reference files; cited inline.

### Rule 4.1 — install rate floor

> `install_rate >= 15%` (organic conversion floor, bot-filtered)
> 
> Below 10% → **🔴 RED**. Between 10% and 15% → **🟡 YELLOW**.
>
> Source: `cws-promote/references/promotion.md` line 154 — "Normal conversion
> is 15–30%".

If the operator is running paid traffic, also check `>= 10%` (paid floor,
also from promotion.md L442: "10–20% from ads"). Flag separately as
`install_rate_paid_low`.

Special-case: if `install_rate > 50%`, that's almost certainly a measurement
error (bot segment not applied), not a brag. Flag as `install_rate_anomaly`
and recommend re-checking the Linux exclusion segment.

### Rule 4.2 — uninstall rate ceiling

> `uninstall_rate_w1 <= 30%` (week-1 average target)
> 
> Above 40% → **🔴 RED** unless the product is documented as one-shot-use
> with monetization (a state.json hint: `monetize.one_shot: true`).
> Between 30% and 40% → **🟡 YELLOW**.
>
> Source: `cws-promote/references/promotion.md` lines 439-442 — "Normal
> uninstall rate is 15–30%; the most monetizable observed product had 40%
> uninstall — high uninstalls aren't disqualifying if monetization fires
> before uninstall".

### Rule 4.3 — banner CTR / SERP-rank cross-check

This rule is the most diagnostic and the most subtle. The banner can't be
directly measured (CWS doesn't expose banner-impression CTR). It's inferred:
if **SERP rank is dropping** *and* **first_visit count is dropping** at the
same time, the listing is losing visibility before users even see it.
That's typically a behavioral-factor regression (uninstall surge, hate
review pile-up) feeding back into Google's ranking signal.

Mechanical rule:

> Flag `banner_visibility_regression` if BOTH:
> - `search_position_google` got worse vs prior (rank increased), AND
> - `first_visit` dropped > 15% vs prior (weekly) or > 25% (monthly).

If only one of the two is true, this rule doesn't fire (it could be ad
seasonality, a Google update, etc).

The "ceiling" half of this rule — the playbook says 60% banner-conversion is
the historic ceiling (`cws-launch/references/assets-and-publish.md` L287),
average organic 15-30% (L289). If `install_rate > 60%`, that's almost
certainly the same measurement-error case as Rule 4.1's anomaly; folded
into `install_rate_anomaly`.

### Rule 4.4 — cost per install range

> `0.05 <= cost_per_install <= cost_ceiling_$`
> 
> Where `cost_ceiling_$` is the operator's documented ARPU floor (read
> from state.json `monetize.arpu_target` if set; default `0.50` USD as
> the conservative playbook ad-economics number).
>
> Below $0.05: likely a counting error (installs being attributed to ads
> that wouldn't have happened).
> Above ARPU floor: ads are burning money; flag `cpi_above_arpu` red.
>
> Source: `cws-promote/references/promotion.md` L258-261 — "cost_per_install
> is the only metric that matters" — and L280 — "click→install is 10–20%".

If no ads are running, skip this rule.

### Rule 4.5 — GA4 / CWS install drift

> `ga4_install_drift <= 20%`
>
> If the two install counts (CWS dashboard vs GA4 segmented `install` event)
> diverge by more than 20%, the attribution chain is broken. Common causes:
> the GA4 install beacon isn't firing (CSP block, manifest permission
> change, content-script issue) or the Linux exclusion segment is
> over/under-shooting.
>
> Source: the cws-retro original stub plus the playbook acknowledgement
> that GA4 attribution is imperfect and CWS install count lags 5–7 days.
> The 20% threshold is the studio-internal alarm point — outside that
> band the install_rate computation itself can't be trusted.

Flag as `attribution_alarm` if outside ±20%. Skip if either source is
unknown.

### Rule 4.6 — Linux OS share in ads ceiling

> `linux_os_share_ads <= 5%`
>
> Above 5% on paid traffic is the documented bot-infiltration signal.
> Flag as `bot_infiltration_ads` red.
>
> Source: studio-internal threshold derived from the FB bot pattern
> documented in promotion.md L156-160 + L400-404 ("Real conversion often
> jumps 3× after the Linux filter"). The 5% is the published audience-quality
> tripwire used by the playbook's ad pause runbook.

Skip if no ads or if `linux_os_share_ads is null`.

### Rule 4.7 — review rating floor

> `rating_now >= 4.0` after the seed wave (5+ reviews on the listing)
>
> If `reviews_total < 5`, rule doesn't fire (sample size too small).
> If `reviews_total >= 5 and rating_now < 4.0`, flag `rating_below_floor`
> red.
>
> Source: cws-retro original stub + promotion.md L177-178 — "When haters
> type, grateful users stay silent" — playbook benchmark for healthy
> listing.

---

## Phase 5 — regression detection

Regression detection runs **only against the prior retro file**, not against
launch-day baseline. Anchors decay; the prior retro is the only fair
comparator. If `stale-prior` is labeled, this phase is suppressed for this
snapshot.

### 5.1 — Weekly cadence thresholds (drop > 15% week-over-week)

For each of the following metrics, if `current < prior * 0.85` (i.e. dropped
more than 15%), append to `regression_flags`:

- `weekly_users`
- `install_rate`
- `first_visit`
- `reviews_total` (drop here means reviews were removed — unusual but
  possible)
- `installs_from_ads` (if ads running)

For metrics where **higher = worse** (uninstall_rate, cost_per_install),
flag if `current > prior * 1.15` (rose more than 15%).

For `search_position_google` and `search_position_cws`, flag if rank dropped
by 3 or more positions (e.g. 4 → 8).

### 5.2 — Monthly cadence thresholds (drop > 25% month-over-month)

Same logic, scaled threshold to 25% (vs 15% weekly). This reflects expected
noise width over the longer window.

### 5.3 — Output shape

Every flagged regression goes into `regression_flags` as a structured tag:

```
[
  "weekly_users:-22%",
  "uninstall_rate:+18pp",
  "search_position_google:-5",
  "cpi:+34%"
]
```

If `regression_flags` is non-empty after Phases 4 and 5, the snapshot gets
a `## REGRESSION` H2 header at the top of the body (after Headline). One
line per flag with a sentence of operator-voice diagnosis ("uninstall jumped
from 24% to 42% — week-1 ceiling is 30%, see Rule 4.2").

---

## Phase 6 — plain-English summary

Three to five paragraphs. Operator voice. No banners, no celebration, no
"I've identified". Concrete numbers everywhere. Structure:

1. **What moved most.** Pick the single biggest delta — positive or negative
   — and lead with it. "Weekly users jumped 26% to 1240 after the Russian
   localization shipped Tuesday" or "Uninstall rate rose from 24% to 42%
   over the last seven days, mostly from new US installs".

2. **The runner-up movement.** Second-largest delta, same shape.

3. **Biggest risk surfaced.** This is the regression flag (if any) that
   matters most for the next seven (or thirty) days. If multiple flags
   fired, pick the one that gates the most downstream skills. If no flags
   fired, say so explicitly: "No benchmark flags this cycle — everything
   sits inside the playbook norms."

4. **(Optional) Context paragraph.** Anything the numbers don't show — a
   manual review the operator ran, a Google update, a known shipping
   experiment that hasn't landed yet. Pull from operator-pasted notes if
   the retro was invoked with `/cws-retro <free-form note>`.

5. **Single concrete next move.** Names a skill. Phrased as a verb-first
   sentence: "Run `cws-resync` to propagate the new permissions through
   build, package, and launch artifacts before the next ad pulse."

This paragraph block lands as the snapshot's `## Summary` section.

---

## Phase 7 — write the snapshot file

```bash
cat > "$_SNAPSHOT" <<EOF
---
date: ${_TODAY}
cadence: ${_CADENCE}
slug: ${SLUG}
extension_id: ${EXTENSION_ID}
days_since_publish: ${DAYS_SINCE_PUBLISH}
weekly_users: ${WEEKLY_USERS}
install_rate: ${INSTALL_RATE_PCT}
uninstall_rate: ${UNINSTALL_RATE_PCT}
search_position_head: ${SEARCH_POSITION_GOOGLE}
search_position_cws: ${SEARCH_POSITION_CWS}
cost_per_install: ${CPI_USD}
reviews_total: ${REVIEWS_TOTAL}
reviews_avg: ${RATING_NOW}
linux_os_share_ads: ${LINUX_OS_SHARE_ADS}
ga4_install_drift: ${GA4_DRIFT_PCT}
prior_retro: ${_PRIOR_RETRO}
days_since_prior_retro: ${DAYS_SINCE_PRIOR}
regression_flags: ${REGRESSION_FLAGS_JSON}
acknowledged_flags: ${ACKNOWLEDGED_FLAGS_JSON}
---

# Retro — ${_TODAY}

## Headline
${HEADLINE_ONE_LINER}

${REGRESSION_BLOCK_IF_ANY}

## Snapshot
| Metric | Now | Prior (${PRIOR_DATE}) | Δ | Benchmark | Flag |
|---|---|---|---|---|---|
| Weekly users | ${WEEKLY_USERS} | ${PRIOR_WEEKLY_USERS} | ${WEEKLY_USERS_DELTA} | — | ${WEEKLY_USERS_FLAG} |
| Installs (window) | ${INSTALLS} | ${PRIOR_INSTALLS} | ${INSTALLS_DELTA} | — | ${INSTALLS_FLAG} |
| Install rate (bot-filtered) | ${INSTALL_RATE_PCT} | ${PRIOR_INSTALL_RATE_PCT} | ${INSTALL_RATE_DELTA_PP} | 15–30% organic | ${INSTALL_RATE_FLAG} |
| Uninstall rate | ${UNINSTALL_RATE_PCT} | ${PRIOR_UNINSTALL_RATE_PCT} | ${UNINSTALL_RATE_DELTA_PP} | ≤ 30% week-1 | ${UNINSTALL_FLAG} |
| Rating | ${RATING_NOW} (${REVIEWS_TOTAL}) | ${PRIOR_RATING} (${PRIOR_REVIEWS_TOTAL}) | ${RATING_DELTA} | ≥ 4.0 | ${RATING_FLAG} |
| Review velocity | ${REVIEW_VELOCITY}/day | ${PRIOR_REVIEW_VELOCITY}/day | ${REVIEW_VELOCITY_DELTA} | — | — |
| Search position (Google) | ${SEARCH_POSITION_GOOGLE} | ${PRIOR_SEARCH_POSITION_GOOGLE} | ${SEARCH_GOOGLE_DELTA} | top-3 by mo-6 | ${SERP_FLAG} |
| Search position (CWS) | ${SEARCH_POSITION_CWS} | ${PRIOR_SEARCH_POSITION_CWS} | ${SEARCH_CWS_DELTA} | — | — |
| CPI | ${CPI_USD} | ${PRIOR_CPI_USD} | ${CPI_DELTA} | ≤ ARPU floor | ${CPI_FLAG} |
| Linux OS share (ads) | ${LINUX_OS_SHARE_ADS}% | ${PRIOR_LINUX_OS_SHARE_ADS}% | ${LINUX_DELTA} | ≤ 5% | ${LINUX_FLAG} |
| GA4/CWS drift | ${GA4_DRIFT_PCT}% | ${PRIOR_GA4_DRIFT}% | ${GA4_DRIFT_DELTA} | ≤ 20% | ${GA4_FLAG} |

## What changed since last retro
${WHAT_CHANGED_BULLETS}

## Flags
${FLAGS_BULLETS}

## Summary
${SUMMARY_PARAGRAPHS}

## Next move
${NEXT_MOVE_ONE_LINER}
EOF
echo "WROTE: $_SNAPSHOT"
```

Then update `state.json`:

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p = pathlib.Path('./.cws/state.json')
d = json.loads(p.read_text())
d.setdefault('retro', {})
d['retro']['last_retro_path'] = "${_SNAPSHOT}"
d['retro']['last_retro_date'] = "${_TODAY}"
d['retro']['cadence'] = "${_CADENCE}"
# Mirror snapshot row into latest_metrics for fast lookup by other skills
lm = d.setdefault('latest_metrics', {})
lm.update({
    'weekly_users': ${WEEKLY_USERS},
    'install_rate': ${INSTALL_RATE_PCT},
    'uninstall_rate': ${UNINSTALL_RATE_PCT},
    'search_position_google': ${SEARCH_POSITION_GOOGLE},
    'reviews_total': ${REVIEWS_TOTAL},
    'reviews_avg': ${RATING_NOW},
    'cost_per_install': ${CPI_USD},
    'updated_at': datetime.datetime.utcnow().isoformat()+'Z',
})
d.setdefault('history', []).append({
    'ts': datetime.datetime.utcnow().isoformat()+'Z',
    'stage': 'cws-retro',
    'event': 'retro_done',
    'retro_path': "${_SNAPSHOT}",
    'cadence': "${_CADENCE}",
    'regression_flags': ${REGRESSION_FLAGS_JSON},
})
d['last_updated'] = datetime.datetime.utcnow().isoformat()+'Z'
p.write_text(json.dumps(d, indent=2))
print("STATE_UPDATED")
PY
```

---

## Acknowledged baselines (operator override)

Some flags are real-but-not-actionable: a product with a documented one-shot
use case will hit a 40% uninstall rate forever, and the operator doesn't
want every weekly retro to scream about it.

If `regression_flags` is non-empty AND the operator wants to suppress one
permanently, offer at the end of Phase 5:

```
D6 — Mark any flag as "acknowledged baseline" so future retros stop
re-flagging it?
Project/branch/task: $SLUG retro for ${_TODAY}, current flags:
${REGRESSION_FLAGS_HUMAN_READABLE}.
ELI10: Some flags will fire every retro because they're a permanent
characteristic of the product, not a regression. Marking one as
"acknowledged baseline" tells future retros to suppress that flag unless
the number gets even worse than today's value.
Stakes if we pick wrong: acknowledge too eagerly and you blind yourself
to a real regression that's been hiding in plain sight. Don't acknowledge
and you'll see the same red flag every cycle and learn to ignore it,
which is worse.
Recommendation: only acknowledge the flag if you can explain in one
sentence why this product is structurally different from the benchmark.
"This is a one-shot URL-shortener so uninstall is part of the funnel."
Completeness: A=10/10, B=10/10
Pros / cons:
A) Acknowledge one or more flags (recommended only with a written reason)
  ✅ Stops noise from a known structural mismatch with the benchmark
  ✅ Forces an explicit operator decision rather than silent dismissal
  ❌ Risks blinding the retro if the operator's reasoning is wrong
B) Leave all flags as-is, deal with them in the next stage skill
  ✅ Keeps every flag visible until structurally fixed
  ❌ Repeats noise on permanently-mismatched metrics
Net: acknowledge only with a one-sentence why; otherwise leave them.
```

If A, write to state.json `retro.acknowledged_flags`:

```bash
/usr/bin/python3 - <<PY
import json, pathlib, datetime
p = pathlib.Path('./.cws/state.json'); d = json.loads(p.read_text())
ack = d.setdefault('retro', {}).setdefault('acknowledged_flags', {})
# user_input is a dict: {flag_name: reason_string}
for flag, reason in ${ACK_INPUT_DICT}.items():
    ack[flag] = {
        'reason': reason,
        'acknowledged_at': datetime.datetime.utcnow().isoformat()+'Z',
        'value_at_ack': ${FLAG_VALUE_DICT}.get(flag),
    }
d['last_updated'] = datetime.datetime.utcnow().isoformat()+'Z'
p.write_text(json.dumps(d, indent=2))
PY
```

On every subsequent retro, before computing `regression_flags`, the agent
reads `retro.acknowledged_flags` and **suppresses** any flag whose current
value is **not worse than** the `value_at_ack` recorded. If the value
gets worse, the flag re-fires regardless of acknowledgement (the
acknowledgement is bounded by the value at time of ack).

The snapshot's frontmatter `acknowledged_flags:` mirrors the suppressed
list for audit.

---

## When NOT to use

- **Pre-launch.** If `GATES_PASSED` does not include `launch`, the extension
  hasn't been submitted to CWS. There's no dashboard, no GA4, no SERP rank,
  nothing to retro. Stop, route to `/cws-launch`.
- **During moderation, < 24h since submission.** CWS dashboard has no data
  window populated yet. The retro will look like nothing happened because
  nothing has. Stop, route the operator to wait.
- **First seven days post-publish for the first retro.** A first retro
  needs at least one full week of data so `first_visit` is meaningful.
  Earlier than that, ask the operator to either wait or explicitly
  request a baseline snapshot (which records numbers without computing
  deltas — Phase 3 baseline path).
- **As a fix-the-product action.** Retro is observational. It points at
  the skill that should act (`cws-resync`, `cws-challenge`, `cws-promote`,
  `cws-monetize`). It does not edit code, edit listings, or edit ads.

---

## Companion skills

- **`cws-resync`** — if any regression flag fires that touches build /
  manifest / listing / banner, propagation through the pipeline is needed.
  A regression on install_rate or banner_visibility_regression typically
  routes here.
- **`cws-challenge`** — if a stage-decision now looks dead based on the
  numbers. Example: the chosen `name_keyword` is dropping rank week over
  week and not recovering — challenge whether the keyword pick was right
  in the first place.
- **`cws-learn`** — record each retro insight that wasn't obvious going
  in. The retro itself doesn't auto-log; the operator should run
  `cws-learn` to capture the durable lesson. The retro narrative section
  is the input for that capture.
- **`cws-monetize`** — when the cadence transition fires (5K weekly users
  crossed AND 90 days), the next retro will recommend a monetize
  gate-check. The retro doesn't enable monetization; it points at the
  skill that does.
- **`cws-promote`** — when no regressions fire, the cycle is healthy, and
  the operator is still pre-monetize, the next move is usually another
  promotion pulse.

---

## Mechanical iron rules (summary)

1. **Cadence**: weekly until BOTH `days_since_publish >= 90` AND
   `weekly_users >= 5000`. Monthly thereafter.
2. **30-day rolling window** for regression detection — enforced by
   `PRIOR_RETRO` file selection.
3. **Always compare against the prior retro file, never against
   launch-day baseline.** Stale anchors lie.
4. **If `regression_flags` is non-empty**, the routing footer MUST
   recommend `/cws-resync` OR `/cws-challenge` (whichever fits the flag),
   NEVER another `/cws-retro`. Retro can't fix what retro found.
5. **Acknowledged flags are bounded by their `value_at_ack`** — they
   re-fire if the metric gets worse than the value at acknowledgement.
6. **Stale-prior** (prior retro > 8d weekly / > 35d monthly) suppresses
   regression detection for that one snapshot only. The snapshot is
   still written; the headline notes "stale-prior, regression detection
   muted".
7. **Operator pastes, agent computes.** The agent never invents a CWS
   dashboard number, never guesses a GA4 segment value, never assumes
   a prior baseline. Either it's pasted, it's in state.json, or it's
   asked.

---

## Skill Routing Footer

End with exactly one `Next: /cws-<skill>` per `../../shared/skill-routing.md`.

**If `regression_flags` is non-empty:**

```
Next: /cws-resync
Why: <flag-1>: <one-sentence diagnosis>. Resync propagates the fix
across build, package, listing, and launch artifacts before the next
ad pulse so the regression doesn't compound through another cycle.
```

Substitute `/cws-challenge` if the flag is about a stage-decision (e.g.
`search_position_google` collapsed and the head keyword pick itself is
suspect). Pick one — never list both.

**If `regression_flags` is empty AND pre-monetize cadence (weekly):**

```
Next: /cws-promote
Why: Funnel is inside every playbook benchmark this cycle. Push another
ad pulse with the documented Linux-bot exclusion live and re-retro in
seven days.
```

**If `regression_flags` is empty AND cadence-transition (just crossed 5K
weekly users AND 90 days):**

```
Next: /cws-monetize
Why: Both transition thresholds cleared (weekly_users ≥ 5K, days_since_publish
≥ 90) and no regressions this cycle. Run the monetize gate-check —
paywall economics now beat the no-cost growth ceiling per
cws-monetize/references/monetization-scaling.md.
```

**If `regression_flags` is empty AND already post-monetize (monthly):**

```
Next: wait — no flags, monetization live. Next retro in ~30 days. If the
operator wants to ship the next product instead, route to /cws-idea for
the next launch.
```

---

## Telemetry (run last)

```bash
"$BIN/cws-timeline-log" "{\"skill\":\"cws-retro\",\"event\":\"completed\",\"branch\":\"$_BRANCH\",\"outcome\":\"$_OUTCOME\",\"cadence\":\"$_CADENCE\",\"flags\":$REGRESSION_FLAGS_JSON,\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

Where `_OUTCOME` is `success` | `blocked-pre-launch` | `blocked-stale-data`
| `error`.

## Completion status

End with one of:

- **DONE** — snapshot written, state updated, next skill recommended.
- **DONE_WITH_CONCERNS** — snapshot written but at least one input was
  marked "unknown" (skipped GA4, no ads attribution, etc). List which.
- **BLOCKED** — pre-launch / pre-data / `AskUserQuestion` unavailable.
  State exactly what's missing and what was tried.
