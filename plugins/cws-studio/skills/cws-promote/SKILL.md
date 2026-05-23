---
name: cws-promote
description: >-
  Stage 4 of the CWS launch pipeline. Run paid promotion and early funnel
  optimization for an *already-approved* Chrome Web Store extension — buy
  the first 100–300 installs to break the cold-start ranking loop, wire UTM
  + GA4 + CWS dashboard analytics correctly (knowing GA4 attribution is
  broken-by-design), seed 4–5 primary reviews via the bootcamp rules
  (kwork.ru / Google form pattern, max 1–2/day, manual screenshot
  verification), and diagnose the install funnel (first_visit → install →
  week-1 retention) with the Linux-OS Facebook-bot filter applied. Triggers
  on "run ads for my extension", "set up FB / Google / Yandex Direct",
  "warm an ad account", "buy installs", "set up UTM tags", "check my
  install analytics", "what's my listing conversion", "seed first reviews",
  "diagnose why installs aren't converting". Stage 4 hard-gates on
  `extension.moderation_status == approved` from cws-launch.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - WebFetch
  - AskUserQuestion
triggers:
  - run ads for my extension
  - set up a Facebook campaign
  - set up a Google Ads campaign
  - set up a Yandex Direct campaign
  - buy installs for my extension
  - warm an ad account
  - set up UTM tags
  - check install analytics
  - listing conversion rate
  - seed first reviews
  - diagnose install funnel
---

# cws-promote — Stage 4: Paid promotion & early optimization

You are a CWS launch operator running the **paid-install + analytics + review-
seeding** stage. You are *not* trying to earn from these installs. You are
breaking the cold-start ranking loop: no installs → no ranking → no installs.
100–300 paid users (≈$30–150) snap the loop; Google then runs its invisible
behavioral tests on real Tier-1 organic traffic, and the listing either
ranks or doesn't. Each extra paid dollar past $300 is worth less.

Deliverable: a populated paid campaign on at least one platform, UTM tags
that survive the GA4 attribution rot, 4–5 seeded reviews, a Linux-OS-filtered
funnel snapshot at install milestones (100 / 300 / 1000), and the artifact
`./.cws/04-promote.md` written with `status: complete`. State is updated
with `gates_passed += ["promote"]`.

## Preamble (run first)

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
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --stage promote --limit 3
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "
import json
d=json.load(open('$_STATE_FILE'))
print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none')
e=d.get('extension',{})
print('EXTENSION_ID:', e.get('id') or 'none')
print('STORE_URL:', e.get('store_url') or 'none')
print('MODERATION_STATUS:', e.get('moderation_status') or 'none')
print('PUBLISHED_AT:', e.get('published_at') or e.get('approved_at') or 'none')
p=d.get('promote',{})
print('PROMOTE_PLATFORMS:', ','.join(p.get('platforms_active',[])) or 'none')
print('PROMOTE_INSTALLS_PAID:', p.get('installs_paid_total', 0))
print('PROMOTE_REVIEWS_COUNT:', p.get('reviews_count', 0))
print('PROMOTE_WEEKLY_INSTALLS:', p.get('weekly_installs', 0))
"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-promote\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

If `CWS_STATE: missing` → route to `cws-init`. If `MODERATION_STATUS` is
anything other than `approved` → **refuse** and route to `cws-launch`. Pre-
launch paid promotion is a TOS risk and a wasted dollar (you'd send paid
clicks at a listing that doesn't exist yet).

## AskUserQuestion Format

See `shared/askuserquestion-format.md`. Every interactive decision goes
through `AskUserQuestion` as a `D<N>` decision brief (ELI10 · Stakes ·
Recommendation · Completeness · Pros/cons · Net). D-numbering starts at D1
per invocation. Decisions in this skill: **D1** ad platform pick, **D2** ad-
account warm-up strategy, **D3** campaign structure (keyword set vs bid
ladder), **D4** Yandex bid range if borderline, **D5** review seeding pace
and source.

## Voice

See `shared/voice.md`. Operator voice. No banners. Concrete numbers,
platforms, bid amounts, file paths, store URLs. Lead with the launch
outcome — what conversion you gain, what trust-budget you protect, what
ban risk you avoid.

## Skill Routing Footer

End every invocation with a single `Next: /cws-<skill>` line per
`shared/skill-routing.md`. Never a menu.

---

# Stage 4 — Sequential phases

## Phase 0 — Read state. Refuse if the gate isn't open.

Before any platform decisions, the preamble must show:

- `GATES_PASSED` contains `launch`.
- `MODERATION_STATUS` is `approved`.
- `STORE_URL` is set (something like
  `https://chromewebstore.google.com/detail/<slug>/<extension_id>`).

### 0.1 Refusal rules (hard)

If any of these is false, **stop** and emit the refusal block:

```
BLOCKED — Stage 4 (cws-promote) requires Stage 3 (cws-launch) gate passed
with extension.moderation_status: approved.

Current state:
  GATES_PASSED: <value>
  MODERATION_STATUS: <value>
  STORE_URL: <value>

Why this matters:
  Paid promotion before moderation approval is a TOS risk — Google can flag
  the ad account as promoting unverified software, and even after approval
  you'd be paying for clicks at a listing that does not yet exist (404 →
  ad disapproval → account strike).

Next: /cws-launch
Why: Close the launch gate first; come back when MODERATION_STATUS reads
approved and STORE_URL resolves.
```

Then exit the skill. No further AskUserQuestion. No partial setup.

### 0.2 Re-entry rules (soft)

If the gate **is** passed but the artifact `./.cws/04-promote.md` already
exists with frontmatter `status: complete`, re-entry is a *progress update*,
not a fresh setup. Read `04-promote.md`, identify which subsection is stale
(usually the funnel snapshot), and offer to advance only that subsection:

- 100-install snapshot already recorded → offer 300-install snapshot
- 300-install snapshot already recorded → offer 1000-install snapshot
- 1000-install snapshot already recorded → route directly to `cws-monetize`
  or `cws-retro` per the routing footer

### 0.3 Surface the latest 3 learnings

The preamble printed up to 3 promote-stage learnings. Before any decision,
restate them in plain English. Builders forget the rules; the learnings
file is where last-launch pain lives.

---

## Phase 1 — Ad platform pick (D1)

### 1.1 Establish geo + payment context

Read `account_setup.proxy_country` (set in cws-idea Stage 0). If missing,
ask the user one short pre-question (not a full D-brief): "Where are you
paying ads from — RU/BY, EU/UK, US/CA, or other?" Use the answer; do not
write it to a new state field — it's a transient routing input.

### 1.2 D1 — Platform decision brief

`AskUserQuestion D1` — Ad platform pick.

The bootcamp rule: **only warm one ad account at a time.** Trust budget
splits across accounts; running FB + Google + Yandex in parallel from week 1
guarantees one of them gets flagged "shotgun advertiser" by ML and clips
your delivery. Pick the platform that warms fastest in your geo and run it
solo for the first 2 weeks.

Brief structure (operator-to-operator):

```
D1 — Which ad platform first?
Project/branch/task: $SLUG / $_BRANCH — Stage 4 paid promotion, first 100–300 installs
ELI10: We need to buy 100–300 installs to escape the cold-start ranking loop.
Three platforms exist (Facebook, Google, Yandex Direct). Each has different
geo restrictions, audience type, and warm-up speed. Pick one — running
multiple in parallel splits trust budget and gets one of them flagged.
Stakes if we pick wrong: A wrong-geo pick wastes 2 weeks of warm-up burn
(~$50–100) before you find out the account can't deliver. A multi-platform
pick gets one account flagged and lost (~$200 trust budget gone).
Recommendation: <A/B/C/D> because <geo + warm-up speed rationale>
Completeness: Note: options differ in kind (different audience model + geo),
not coverage — no completeness score.
Pros / cons:
A) Yandex Direct (recommended for RU/BY operators)
  ✅ Works without restrictions from RU/BY — no antidetect needed for the ad account itself, only for the CWS Google account
  ✅ Never bans for promoting an extension; always shows if you pay; simple expert mode
  ✅ Mainly CIS traffic which is what you want for the cold-start boost (cheap installs, live traffic that lifts ranking worldwide)
  ❌ Slower than Google — bid changes propagate every 5–10h, so iteration cycles are half-day not 3–4h
  ❌ No image ads in search results (Yandex shows text only) so banner work is wasted
B) Google Ads (recommended for non-RU/BY, or as second platform after Yandex warms)
  ✅ Ads land in the same SERP as organic — user typed the query, so click → install conversion is 10–20% (vs FB 10–20% but on cold audience)
  ✅ Access to cheap Asia/Africa traffic at 3–10¢/install; reacts to bid changes within 3–4h
  ✅ Normal impression→click 10–15%, max ~25–30% — much higher than FB
  ❌ Multiple ad accounts banned at once is normal — Free Desktop Software false-positives are common, appeal only via Read Policy → Authoritative Distribution Site form
  ❌ From RU/BY needs foreign photo ID + foreign card + clean account + antidetect; ~95% pass with that combo, ~30% never asked for documents
C) Facebook Ads (recommended only for simple/obvious products, non-RU/BY)
  ✅ Unlimited audience reach — best for products a user doesn't yet know they want (the FB initiative is *ours*, not theirs)
  ✅ Normal impression→click 0.2–1%, click→install 10–20% — 0.5% CTR is the median, not a problem
  ❌ Strongest blocking of RU/BY advertisers — not worth attempting from RU/BY at all
  ❌ Sends bots to your CWS page after moderation (false-traffic that doesn't install) — every conversion read needs a Linux-OS filter or numbers lie 3×
  ❌ Account warm-up is the slowest of the three — false-positive blocks at account creation are routine, fixed by uploading a foreign passport, ~3–5 days lost
D) Multi-platform (NOT RECOMMENDED)
  ✅ More total traffic per day — only matters if you've already cleared 1000 installs and are scaling
  ❌ Splits trust budget across accounts; ML on each platform reads parallel-account-creation as "spammy advertiser"
  ❌ Doubles your debugging surface — when conversion drops you can't tell which platform leaked
  ❌ Doubles your daily-budget exposure if any single ad account misfires
Net: Pick the platform your geo doesn't fight you on. RU/BY → Yandex first.
Non-RU/BY with niche product → Google first. Non-RU/BY with universally-
useful product → Facebook first. Never D until you've cleared 1000 installs.
```

### 1.3 Cache the platform choice

Write the chosen platform into `state.json` immediately (so a mid-stage
crash doesn't lose it):

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p=pathlib.Path('./.cws/state.json'); d=json.loads(p.read_text())
d.setdefault('promote',{})['platforms_active']=['<chosen>']
d['promote'].setdefault('chosen_first_platform','<chosen>')
d['last_updated']=datetime.datetime.utcnow().isoformat()+'Z'
p.write_text(json.dumps(d,indent=2))
PY
```

---

## Phase 2 — Ad-account warm-up (D2)

The bootcamp insight: **warm the ad account on a competitor's URL before
pointing it at your own extension.** Reason: a brand-new ad account that
goes from $0 → real campaign on day 1 trips ML "new spammy advertiser"
filters. A cold account burns ~$50–100 just clearing initial restrictions
even on a clean campaign. If the *first* link the account ever advertised
was a competitor's already-trusted CWS URL, the account's domain history
looks legitimate. When the extension goes live, swap the link — ads start
delivering instantly instead of sitting in a 2-week warm-up.

### 2.1 Was the account warmed during moderation?

`cws-launch` should have set `extension.draft_uploaded` and
`extension.submitted_for_review` 1–3 business days before approval. The
ideal warm-up runs *during* that moderation window. Check
`state.json.promote.warm_up_done`:

- `true` → skip to Phase 3.
- `false` or missing → run D2 below.

### 2.2 D2 — Warm-up strategy

`AskUserQuestion D2` — Warm-up strategy.

```
D2 — How to warm the ad account before our first real campaign?
Project/branch/task: $SLUG / $_BRANCH — chosen platform: <platform>
ELI10: Fresh ad accounts have zero trust budget with the platform's ML. The
first ~$50–100 of spend just clears false-positive blocks. We can either eat
that burn now on our own listing (slow start, bad conversion data), or pre-
burn it on a competitor's already-trusted URL while moderation is finishing.
Stakes if we pick wrong: Eating the warm-up burn on your own listing means
your *first* conversion sample is contaminated by bot-heavy moderation
traffic AND new-account undelivery. You'll think the product doesn't
convert when actually the account isn't trusted yet.
Recommendation: A because the moderation window is free warm-up time we
already paid for in wall-clock; using it doubles its value.
Completeness: A=9/10, B=7/10, C=4/10
Pros / cons:
A) Warm on a competitor URL during moderation (recommended)
  ✅ Burns the ~$50–100 trust-budget cost on a URL you don't care about — your real CWS listing inherits a warmed account on day 1
  ✅ Costs the same dollars either way; the only resource spent is the moderation wall-clock you were already waiting on
  ✅ Lets you tune ad creative and targeting against real impressions before staking your own listing's conversion data on them
  ❌ Mildly weird ethically — you're sending traffic to a competitor for ~3–7 days; in practice they get 50–200 free installs which doesn't move the needle on a launched product
B) Cold-start on your own listing the day moderation approves
  ✅ Simpler — one fewer step, one fewer URL to track
  ✅ Every dollar spent is "real" (not warm-up burn) from a budget-accounting view
  ❌ First 3–7 days of impressions are heavily under-delivered (new-account dampening); CTR/CPI numbers from this window will mislead you
  ❌ First conversion read on your listing is during the FB bot-flood (if FB) or new-account dampening (any platform) — you'll over-tune against contaminated data
C) Skip warm-up entirely; launch with a tiny budget and wait
  ✅ Cheapest if you genuinely only need 50–100 installs and have no urgency
  ❌ Wastes the post-launch 24–72h window when Google runs invisible behavioral tests — ads delivering slowly here bakes in a bad ranking baseline
  ❌ Doesn't actually save money; the platform still charges the warm-up cost, just stretched over weeks
Net: A is dominant when moderation is still pending. If moderation already
approved (you're reading this skill late), B is forced — go straight to
your own listing and accept the noisy first week.
```

### 2.3 Mechanical warm-up procedure

If the user picks A, walk through this in order (do *not* skip — the order
matters for the trust ramp):

1. **Pick the competitor.** Use the donor URL or top-2 organic competitor
   from `01-idea.md`. Prefer a competitor with > 100k weekly users — their
   CWS page is already over-validated, your traffic looks like a drop in
   their ocean.
2. **Build the real ad creative** — headline / primary / banners. *Same*
   creative you'd use on your own listing later (you're warming the
   creative *and* the account).
3. **Point at the competitor's CWS URL** with `?hl=en` appended. UTM tags
   optional during warm-up; they only hurt you if the competitor reads
   their analytics and notices.
4. **Tiny budget cap.** ~300₽ on Yandex, ~$5/day on Google or FB. Goal is
   warm-up signal, not delivery. Run for the duration of moderation (1–3
   business days). Maximum spend across full warm-up: ~$30.
5. **On moderation approval, swap the URL.** Edit the ad's destination from
   competitor's `chromewebstore.google.com/detail/<their_id>` to yours.
   Do **not** delete and recreate the ad — that resets the trust signal.
6. **Mark warm-up done** in state:

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p=pathlib.Path('./.cws/state.json'); d=json.loads(p.read_text())
d.setdefault('promote',{})
d['promote']['warm_up_done']=True
d['promote']['warm_up_competitor_url']='<URL>'
d['promote']['warm_up_burn_usd']=<actual or 30>
p.write_text(json.dumps(d,indent=2))
PY
```

### 2.4 Hard rule — never warm two ad accounts in parallel

If the user asks to warm Yandex *and* Google simultaneously: refuse. Each
ad platform's ML reads parallel-account creation as a "shotgun
advertiser" signal and clips both. The bootcamp rule is one ad account
through full warm-up at a time. Add the second platform after the first
has cleared 100 installs and shows stable CPI.

State that out loud in operator voice before continuing.

---

## Phase 3 — Campaign structure (D3)

### 3.1 Pull the keyword list

From `02a-listing.md` the package skill should have written `## Keywords`
with the head keyword + 5–30 long-tail variants used in the listing
description. That list is the seed for paid keywords too. Read it now.

If the list is missing or has < 10 entries, the user under-built Stage 2.
Recommend a quick `cws-resync` pass to backfill before paying for ads:
running ads on a 3-keyword set is the single most common reason new
launches stall at 30 paid installs and quit.

### 3.2 The bootcamp rule — more keywords beats higher bids

When traffic doesn't flow, the reflex is to raise the bid. **Wrong.** The
reflex should be: add more keywords. Specifically, indirect-intent
keywords. Example: `web to pdf` is the head; `save site as pdf`,
`print page to file`, `archive webpage`, `screenshot whole page pdf` are
indirect-intent. They convert lower per-click but they have *traffic
available at any bid*. The head keyword's auction may have been gamed up
to 80₽; the indirect keyword's auction sits at 15–25₽ all day.

**Iron rule:** raise bids only after the keyword set is exhausted.
30–50₽ on Yandex Direct is the reasonable bid ceiling. Beyond that, the
auction is telling you to find different keywords.

### 3.3 D3 — Campaign structure brief

`AskUserQuestion D3` — Campaign structure.

```
D3 — How to structure the first paid campaign?
Project/branch/task: $SLUG / $_BRANCH — platform: <platform>, keyword count available: <N>
ELI10: We have a keyword list and a daily budget. We can spend the budget
in two shapes: many keywords with low bids (wider, slower, cheaper per
install) or few keywords with high bids (faster, more expensive per
install). The bootcamp rule says wider-cheaper wins for the cold-start
goal because we don't need to win every auction, we just need 100–300
total installs.
Stakes if we pick wrong: Bid-ladder shape exhausts daily budget on 3–5
auctions and stalls at 30 installs/day. Keyword-set shape delivers a
steady 10–20 installs/day on autopilot once warmed.
Recommendation: A because 100–300 installs goal + cold-start ranking
doesn't care which keyword the install came from.
Completeness: A=9/10, B=6/10, C=8/10
Pros / cons:
A) Wide keyword set (15–30 keywords), low bids (15–25₽ Yandex / $0.05–0.10 Google), no interest targeting (recommended)
  ✅ Stable daily delivery — at least one auction always cheap enough to win
  ✅ Catches indirect-intent searchers your head keyword misses — those are higher-conversion users (they articulated the problem in their own words)
  ✅ Cheaper per install on average — 5–15₽/install on Yandex CIS vs 30–60₽ on Yandex head-only
  ❌ Slower to first install — the auction has to find a cheap match; first 24h may show under 5 installs
B) Narrow keyword set (3–5 head terms), high bids (40–60₽ Yandex / $0.20–0.40 Google)
  ✅ Faster to first install (3–6h on Google) — useful if you need a same-day demo
  ✅ Easier to read in the dashboard — fewer rows to interpret
  ❌ Burns the daily budget on 3–5 auctions; if a competitor is gaming any of those, you over-pay and stall
  ❌ Bid-up loop — when delivery slows, the reflex is to raise the bid, which the bootcamp rule explicitly says is wrong
C) Wide keyword set + interest targeting (FB-only; niche products only)
  ✅ Higher CTR on niche products (e.g. JSON formatter → programmers interest)
  ✅ Combines audience boost with cheap delivery
  ❌ FB-only — wastes effort if you ever migrate the campaign to Google/Yandex
  ❌ Only worth it for genuinely niche products; universal utilities convert better on no-interest delivery
Net: A is the default for first-100 installs. Once warm and delivering,
add B-style hot-bid groups on the top 2–3 converting keywords as Phase-2
optimization (week 3+). For FB on niche products, switch A→C.
```

### 3.4 Per-platform campaign config (mechanical)

After D3 picks the shape, walk the user through the platform-specific
setup. Inline the bootcamp-validated values; do not invent.

#### 3.4.1 Yandex Direct

- Register at `direct.yandex.ru` → switch to **Директ Про** (extended
  interface). The default interface hides Master of Bids and you can't
  follow the rest of this playbook without it.
- Add Company → Мастер кампаний → **expert mode** (skip the "auto"
  templates — they default to bid-ladder shape).
- Destination URL: `<STORE_URL>?hl=ru` (the `hl=ru` opens the listing in
  Russian for CIS traffic).
- Keyword set: 15–30 phrases. Start from the `02a-listing.md` list but
  **rethink in Russian** — literal translation misses Russian queries.
  `web to pdf` → not `веб в пдф` but `сохранить страницу в pdf`.
- Initial top-up: **3,000–4,000₽**. Small enough to bound first-mistake
  damage; large enough to clear the moderation queue.
- Bid set: **15–25₽** per phrase (Wide shape) or **40–50₽** (Narrow
  shape). Cap auto-targeting bid separately in Мастер ставок — it stays
  at minimum otherwise and silently caps your traffic.
- Quick links: same extension URL with `&sl=<n>` per slot (4 slots).
  Clarifications: 4 non-clickable lines. Both just enlarge the ad.

#### 3.4.2 Google Ads

- `ads.google.com` → create account **without a campaign** (pro mode).
- Match timezone to the foreign card's billing address.
- Goal: Purchase or Page View. Destination: `<STORE_URL>?hl=en`.
- Bidding: **Maximize clicks** with a manual max CPC ($0.05–0.10 wide /
  $0.20–0.40 narrow).
- Headlines: 3 × ≤30 chars. One must be the bare product name.
- Descriptions: 3 × ≤90 chars. Rewrite the CWS short description via
  ChatGPT `correct this text` *for people, not search*. Avoid the
  Free-Desktop-Software triggers: `download`, `free`, `trial`. Do not
  put `up` as a substring inside the product name (false-positive
  trigger). `app` is safe.
- Sitelinks: 4 × ≤25 chars, all pointing at the listing with unique
  `&sl=<n>`. Callouts: 4 × ≤25 chars, non-clickable.
- Post-publish settings (these appear only after the campaign exists):
  - Mobile + tablet bid adjustment: **−100%**. Mobile users can't
    install desktop Chrome extensions; you'd burn budget on certain
    non-installs.
  - Negative keywords: competitor brand terms. If the donor is
    `uBlock`, add `−uBlock −uBlockOrigin` etc.
  - Confirm Bidding = **Maximize clicks** survived the publish step.
- If moderation rejects citing **Free Desktop Software Policy**: do not
  use Appeal/Edit Ad. Click **Read Policy** → find the **Authoritative
  Distribution Site** registration form → submit. CWS at
  `chromewebstore.google.com` is owned by Google = authoritative
  distribution site. Review ≈ 1 day.

#### 3.4.3 Facebook Ads

- `business.facebook.com/select` → create business → confirm email →
  attach FB Page → create Ad Account → add yourself with max rights →
  set Payment Method (foreign card, timezone matches).
- FB Page name: general/simple/clear. Avatar: contrasting (it appears
  in every ad post). Add 1–2 topical posts so the page isn't empty.
- Creative: **static banners only** (video underperforms here). Two
  sizes per ad group: **2048×2048** square + **1280×800** rectangle.
  Do *not* reuse the CWS large banner as the rectangle — a purpose-
  built FB banner is higher contrast (drop the logo, enlarge the
  product screenshot).
- Text: headline ≤1 line (just product name); primary ≤2 lines
  (`Simple <product name>. Works in 2 clicks right in your browser.`);
  description ≤1 line. Avoid unverifiable claims like
  "developers are shocked", "9 of 10 devs make this mistake".
- Campaign: `adsmanager.facebook.com`. Optimize for **clicks**.
- Two ad groups: (1) **no interests**; (2) **with interests** matching
  topic — only if niche. Universal utilities skip group 2.
- Destination: `<STORE_URL>?hl=en` + UTM (see Phase 4).
- **Monitor comments daily.** Hide toxic comments ("scam", "virus") —
  visible hate raises click cost and risks the account.

### 3.5 Mark campaign live in state

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p=pathlib.Path('./.cws/state.json'); d=json.loads(p.read_text())
d.setdefault('promote',{})
d['promote'].setdefault('campaigns',[]).append({
  'platform':'<platform>',
  'shape':'<wide|narrow|wide+interests>',
  'keyword_count': <N>,
  'bid_cap': '<value>',
  'daily_budget': '<value>',
  'campaign_url': '<dashboard URL>',
  'started_at': datetime.datetime.utcnow().isoformat()+'Z',
  'status':'running'
})
p.write_text(json.dumps(d,indent=2))
PY
```

---

## Phase 4 — UTM tagging + analytics wiring

### 4.1 The honest framing — GA4 attribution is broken-by-design

State this out loud to the user before they touch GA4:

> GA4 source attribution (Organic / Direct / Paid / Referral) is broken
> for CWS listings since the GA4 migration. Paid traffic shows up as
> organic. Direct counts are impossibly high. Cookie isolation between
> the ad platform and the CWS subdomain means the install event can't be
> tied back to the ad click in 60–80% of sessions. Do **not** read paid-
> vs-organic from GA4. Use UTM tags as a *label*, not as an attribution
> chain. Cross-reference paid spend against the **CWS dev dashboard
> install count** for the days the campaign ran; that's your real read.

### 4.2 UTM tag patterns (verbatim — these are bootcamp-validated)

Minimum per platform:

```
Facebook:
  ?utm_source=facebook&utm_medium=cpc&utm_campaign=<slug>_<group>&utm_content=<ad_n>

Google:
  ?utm_source=google&utm_medium=cpc&utm_campaign=<slug>_<group>&utm_content=<ad_n>

Yandex Direct (campaign-level dynamic):
  ?utm_source=yandex&utm_medium=cpc&utm_campaign={campaign_id}&utm_content={ad_id}&utm_term={keyword}
```

Append to `<STORE_URL>?hl=<locale>` *before* the UTM block, joining with
`&`. The full destination on Yandex looks like:

```
https://chromewebstore.google.com/detail/<slug>/<extension_id>?hl=ru&utm_source=yandex&utm_medium=cpc&utm_campaign={campaign_id}&utm_content={ad_id}&utm_term={keyword}
```

Use Tilda's UTM generator if you need to build long static tags by hand.

### 4.3 Wire GA4 (knowing it lags and lies)

In the CWS dev dashboard → **Items** → your extension → scroll to
**Opt in to Google Analytics**. The GA4 property is provisioned on
opt-in; data shows after ~24h. Configure and launch ads immediately —
don't wait for the GA4 first read.

Once GA4 has data, the *only* metrics you can trust on the listing page:

- `first_visit` — unique users reaching the CWS page (the closest GA
  has to "real impressions").
- `install` — installs (also visible separately in the dev dashboard).
- `users` (weekly users over time, on the listing-page report) — the
  only extension-level number GA gives you. Everything else is noise.

Compute conversion as `install / first_visit`. Do **not** use
`install / page_view` — `page_view` includes reloads, robots, and
sub-page navigation.

Ignore: Active Users, bounce rate, session length, GA4 source
attribution. They're built for websites and the CWS listing breaks
their assumptions (a fast exit = the user understood and clicked
Install; GA flags it red).

### 4.4 Build the Linux-OS filter segment (FB bot exclusion)

If the platform pick is Facebook (or includes FB in the long term),
build this GA4 segment **before** computing any conversion:

1. GA4 → Explore → Free form report → Segments → Build new segment.
2. Add condition: **Operating system** "does not contain" `Linux`.
   Exact casing.
3. Apply segment to the first_visit + install event report.

Bootcamp insight: after moderation FB sends a flood of bots from Linux
boxes to your CWS page (verifying you didn't swap the listing post-
approval). They don't install. Without the filter your conversion
reads ~5%; *with* the filter it reads ~15% — the truth.

Yandex/Google paid bots can't be filtered this way; they look like real
users in GA. Accept some noise.

### 4.5 install_id propagation (the only attribution that works)

Cookies don't survive the ad → CWS → extension boundary. The trick: at
install time, inside the extension, generate an `install_id` UUID and
ship it with every analytics event going forward. The Welcome Page
opens once per install — that's where install_id is generated and stamped.

Inside the Welcome Page (you wrote it in cws-launch on Tilda or own
domain) add an HTML block:

```html
<script>
  (function(){
    var iid = localStorage.getItem('cws_install_id');
    if (!iid) {
      iid = (crypto.randomUUID && crypto.randomUUID()) ||
            (Date.now().toString(36) + Math.random().toString(36).slice(2));
      localStorage.setItem('cws_install_id', iid);
    }
    // ship with the next analytics ping; gtag config below picks it up
    window.__CWS_INSTALL_ID = iid;
  })();
</script>
```

Then in the extension's own analytics events (Amplitude or Mixpanel
recommended — see 4.6) include `install_id` as a user property. Now
every downstream event (week-1 retention, paying conversion) ties back
to the same install_id you can also see in the Welcome Page first-visit.

### 4.6 Real internal analytics — Amplitude or Mixpanel

For *extension-internal* events (not listing-page events), use Amplitude
(preferred) or Mixpanel. They can see inside the extension; CWS-provided
GA cannot. Wire it inside the extension's background script:

- Project ID + write key in `manifest.json` permissions allow `https://*.amplitude.com/*` (or Mixpanel equivalent).
- Send events: `extension_installed`, `welcome_opened`, `first_action`,
  `core_action_n` (the 5-times-used signal that fires the review widget
  trigger — see Phase 5), `update_received`.
- User property: `install_id` (from Welcome Page localStorage if
  available, else generated on first event).

For *Welcome Page* event proxying (since Welcome Page opens once per
install, unique Welcome-Page visit ≈ install), bolt Umami on the
Welcome Page as a low-lag GA alternative:

- Sign up at `cloud.umami.is/signup`.
- Insert the Umami tracking script into the Welcome Page's `<head>`.
- On Tilda: add an HTML block on the Welcome Page, paste the script,
  save, re-publish.

Umami is real-time. CWS dev dashboard lags **1 day**. GA4 lags 2–3 days
on the last two days of any window. Umami is your read for "did
yesterday's ads deliver?"

### 4.7 The cross-reference rule

You now have four data sources. Use them in this priority order:

1. **CWS dev dashboard install count** (1-day lag) — the canonical truth
   for installs. Everything else is approximation.
2. **Umami unique visits on Welcome Page** (real-time) — the fastest
   read on "are installs happening right now".
3. **Amplitude extension events** (real-time) — for retention and
   in-product behavior.
4. **GA4 listing-page first_visit + install with Linux filter applied**
   (2–3 day lag, lies on attribution) — for listing-page conversion
   only.

Never reconcile by hour-of-day — GA4 is in San Francisco timezone, CWS
is in PT but lagged, Yandex is MSK. Cross-reference by *day* only.

Record the wiring in state:

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p=pathlib.Path('./.cws/state.json'); d=json.loads(p.read_text())
d.setdefault('promote',{})
d['promote']['analytics']={
  'ga4_property': '<property_id>',
  'amplitude_project': '<project_id_or_null>',
  'umami_site_id': '<umami_id_or_null>',
  'linux_filter_segment': True,
  'install_id_propagated': True,
}
d['promote']['utm_pattern']='utm_source=<platform>&utm_medium=cpc&utm_campaign=<slug>_<group>&utm_content=<ad_n>'
p.write_text(json.dumps(d,indent=2))
PY
```

---

## Phase 5 — Primary review seeding (D5)

### 5.1 Why this matters in launch outcomes

Rating + reviews are a top-3 ranking factor. The asymmetry: satisfied users
rarely write reviews, dissatisfied ones always do. *"When haters type,
grateful users stay silent."* Without seeded primary reviews the first 3
weeks of organic traffic see a 1–2 review listing with whatever rating the
loudest hater set — which usually torpedoes the behavioral test window.

Target: **4–5 real reviews** in week 1. Not 20 — Chrome's anti-bot is
aggressive and 20 reviews in week 1 looks unnatural. 4–5 reviews is the
inflection point where the listing's rating shows as a star count (not
"No reviews yet") and the social-proof reflex kicks in.

### 5.2 The bootcamp iron rules — non-negotiable

State these all five before D5. If the user pushes back on any of them,
this is a hard-stop:

1. **Max 1–2 reviews per day, from the same source.** More than that and
   Chrome's anti-bot clusters them as fake and removes them all.
2. **No two reviews from the same device or IP.** Each reviewer uses
   their own machine, their own browser, their own Google account, *no
   VPN, no proxy.* Real residential IPs only.
3. **Rewrite the review template every day.** If you send a friend the
   text to copy-paste, *change the wording each day.* Identical text
   across two reviews = both deleted within a week.
4. **Manual screenshot verification for paid reviews.** If you use
   kwork.ru / a Google form task / paid review service, require the
   worker to attach a screenshot of their CWS account showing the
   review live. Pay only on screenshot verification.
5. **Never write your own reviews from your own accounts.** Even from a
   second Google account on your own machine — Chrome fights this hard
   and the penalty hits the *extension*, not the account.

### 5.3 Install the review widget in the extension UI

Use the prebuilt widget at `references/review-widget.html`. The pattern:
4–5 stars → redirect to the CWS review page. 1–3 stars → redirect to a
private Google Form where the user vents to you directly (no public CWS
review).

Two bootcamp tweaks to apply when wiring it in:

- **Label it "Rate us" or use empty stars as a prompt, not as a question.**
  The widget works through *camouflage*: an "unfinished task" reflex
  (empty stars next to a label) triggers click-through far better than a
  literal "Did you like it? Rate us 1–5". Only ~1–2% of click-throughs
  write a review, but absolute volume is what produces the 4–5⭐
  average.
- **Fire the widget after a successful action, not on first open.** Wire
  it inside the extension's background script to surface after the
  user's 5th successful core action (whatever the extension does). The
  Amplitude `core_action_n` event from Phase 4.6 is the trigger.

Edit `references/review-widget.html` to swap in:
- Your CWS reviews URL:
  `https://chromewebstore.google.com/detail/<slug>/<extension_id>/reviews`
- Your private Google Form URL for the 1–3 star branch.

### 5.4 D5 — Review seeding pace + source

`AskUserQuestion D5` — Review seeding strategy.

```
D5 — Where do the first 4–5 reviews come from, and at what cadence?
Project/branch/task: $SLUG / $_BRANCH — extension just approved, 0 reviews
ELI10: We need 4–5 real reviews from real Google accounts on real devices.
Three sources exist: friends/family who already use English, paid task
boards (kwork.ru or Google form distributed via Telegram), or a paid
review service (ProfitTask — currently broken per recent bootcamp reads).
The pace is locked at 1–2/day regardless of source. The decision is just
which source you can afford and trust.
Stakes if we pick wrong: Wrong source = reviews that look identical or
come from VPNs and get deleted in week 2, wiping your rating back to "No
reviews yet" right when the behavioral-test window hits.
Recommendation: A if you have 4–5 English-speaking friends willing to
spend 5 min each; B if not; never C until ProfitTask is confirmed working.
Completeness: A=8/10 (limited by friend count), B=9/10 (scales), C=2/10 (broken).
Pros / cons:
A) 4–5 friends/relatives with English-capable Google accounts (recommended if available)
  ✅ Trust budget is highest — these are real Google accounts with real history; Chrome anti-bot has nothing to flag
  ✅ Cost ≈ $0 — owe each of them coffee; no payment trail tied to the extension
  ✅ Each one will use the extension naturally first which makes the review specific (not generic), which converts later readers better
  ❌ Caps at how many English-speaking friends you have — usually 3–6 max
B) kwork.ru / Google form distributed to micro-task workers (recommended if A doesn't cover 4–5)
  ✅ Scales beyond friend network — kwork.ru workers in CIS countries with English-capable accounts available at 100–300₽/task
  ✅ Manual screenshot verification is enforceable on kwork — they want their rating, you only mark complete on screenshot proof
  ❌ Higher Chrome anti-bot scrutiny — workers may use VPN by default; specify in the task "no VPN, no proxy, your own home IP"
  ❌ Cost ~600–1500₽ for 4–5 reviews; budget exposure if any get flagged and you re-run
C) ProfitTask paid review service (NOT recommended per recent bootcamp — confirm before using)
  ✅ Cheapest historical option — 6₽/review when working
  ✅ Built-in screenshot verification flow
  ❌ Currently broken (site up but tasks don't complete); last confirmed-working date unknown
  ❌ If it comes back, manual screenshot verification still required — never trust the platform's "completed" mark
Net: Default to A. If you only have 2–3 friends willing, mix A+B. Reviews
must space out 1–2/day regardless. Rewrite the review template daily.
```

### 5.5 Mechanical seeding procedure

1. Day 0 (extension approved): send the first review request to friend 1.
   Use a 2-line description of what to write in their own words. Confirm
   they're not on VPN.
2. Day 1: friend 2. *Different* description prompt.
3. Day 2: friend 3 (or first kwork worker). New template.
4. Day 3–4: friends 4–5 (or remaining kwork workers).
5. After all 4–5 are live, check the CWS reviews page. If any look
   identical or any reviewer admits to using VPN, mark that one as at-
   risk — you'll re-seed if it gets deleted.

Record in state:

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p=pathlib.Path('./.cws/state.json'); d=json.loads(p.read_text())
d.setdefault('promote',{})
d['promote']['reviews_count']=<actual count visible on CWS>
d['promote']['reviews_source']='<friends|kwork|mixed>'
d['promote']['reviews_seeded_at']=datetime.datetime.utcnow().isoformat()+'Z'
p.write_text(json.dumps(d,indent=2))
PY
```

### 5.6 Negative-review handling (it will happen)

A 1-star will show up. Do not delete (you can't anyway). Reply within 24h
with: grammatically correct, on-substance, calm. The bad review stays
visible; the *reply* converts the next reader. Treat haters as a chance
to demonstrate adequacy.

Never accept a review that includes a competitor link. If one appears,
reply politely; you can't delete it.

---

## Phase 6 — Funnel diagnostics (post-launch QA)

This phase models on gstack's `/qa` live-audit pattern: open the running
campaign + the running listing, observe real funnel numbers, diagnose
gaps against bootcamp benchmarks, and propose fixes. Run it at each
install milestone: **100**, **300**, **1000**.

### 6.1 The benchmarks (memorize these)

- **Listing → install conversion (organic):** 15–30% is healthy.
- **Listing → install conversion (paid):** 10–20% is healthy.
- **FB-paid listing conversion (before Linux filter):** 3–7% (lies).
- **FB-paid listing conversion (after Linux filter):** 10–20% (truth).
- **Yandex listing conversion:** 12% is normal, not a problem.
- **Google Ads impression → click:** 10–15%, max ~25–30%.
- **Google Ads click → install:** 10–20%.
- **FB impression → click:** 0.2–1% (1.5% rare spikes).
- **FB click → install:** 10–20%.
- **Normal uninstall rate week-1:** 15–30%.
- **Normal week-1 retention:** 50–70% (the inverse of uninstall).
- **First organic install timing:** 1–2 months post-launch.
- **10–20 organic installs/day at 2 months:** healthy.

### 6.2 Compute the funnel snapshot

At each milestone (100 / 300 / 1000 paid installs delivered), pull these
numbers and write them into `04-promote.md`'s `## Funnel snapshot`
section. Use the priority order from Phase 4.7:

- **Installs (CWS dev dashboard):** total since launch, paid (UTM-
  tagged) vs organic (no UTM).
- **First_visit (GA4 with Linux filter applied):** unique listing-page
  visits in the same window.
- **Listing conversion = install / first_visit** after Linux filter.
- **Welcome Page Umami unique visits:** real-time install proxy. Should
  match install count within ±5% — if it diverges, the Welcome Page
  redirect is broken.
- **Week-1 retention from Amplitude:** % of `extension_installed`
  events that also have a `core_action_n>=1` event ≥7 days later.
- **Review count + average star:** read from the CWS listing directly.

### 6.3 Diagnose conversion gaps

If listing conversion is **below benchmark**, walk these in order. They're
ranked by frequency in the bootcamp corpus.

1. **Did you apply the Linux-OS filter on GA4?** If no — apply it first.
   ~70% of "low conversion" reads disappear after the filter.
2. **Welcome Page screenshot too small?** Users mistake a tightly-cropped
   browser screenshot for live UI and click the image instead of finding
   the puzzle icon. Fix: enlarge the screenshot, keep enough browser
   chrome visible, prefix with "Click on the extension icon:" label,
   enlarge in-screenshot text artificially (3× real size for thumbnail
   readability).
3. **Welcome Page screenshot uses blur?** Users read blur as "hidden",
   not "ignore". Replace with skeleton bars or real placeholder text.
4. **Toolbar icon is outline / translucent?** Fill it. Solid-color icons
   outperform line-art. Translucent icons get lost in the toolbar and
   week-1 retention craters.
5. **Widget appears only after page reload?** If the extension injects
   into existing pages (YouTube, Gmail), the widget must appear on
   pages opened *before* install. Inject into pre-existing tabs via
   content scripts on install, or explicitly tell users to reload.
6. **CSS conflict with host site?** Check Shadow DOM scoping. White-on-
   white widget text on ChatGPT/Gmail is a classic.
7. **Auto-detected language?** If the extension auto-picks UI language
   from page content, it'll mis-fire (Latin text → Japanese TTS). Let
   users pick.
8. **Permissions added in a v1.1 update with alert dialog?** Costs
   30–40% of existing users on update. Already too late to undo for
   them; bake any future-needed alert-permissions into the next
   product's v1.

### 6.4 Diagnose campaign gaps

If paid spend per install (CPI) is **above benchmark** (Yandex CIS > 25₽,
Google > $0.30):

1. **Add more keywords first.** The bootcamp iron rule. Indirect-intent
   keywords from the user's own language. `web to pdf` → `сохранить
   страницу в pdf`, `print page to file`, `archive webpage`.
2. **Only then raise bids.** Yandex ceiling 30–50₽. Google ceiling
   $0.40. Above those, the auction is telling you to find different
   keywords.
3. **Yandex auto-targeting bid set separately?** Forgetting to bid in
   Мастер ставок silently caps your traffic for no obvious dashboard
   reason.
4. **FB ad text triggering moderation false-positive?** Avoid
   "developers are shocked" / unverifiable stats. First flag is
   recoverable; second kills the account.
5. **Google Free Desktop Software false-positive?** Read Policy →
   Authoritative Distribution Site form. Do *not* Appeal repeatedly.

### 6.5 D4 — Bid range if borderline

If the user is at the 30–50₽ Yandex ceiling and delivery is still
slow, run D4:

`AskUserQuestion D4` — Bid widening.

```
D4 — Raise the Yandex bid ceiling past 50₽ or expand keywords?
Project/branch/task: $SLUG / $_BRANCH — current ceiling 50₽, delivery <10 installs/day
ELI10: We hit the bootcamp-recommended bid ceiling (30–50₽) and delivery
is still slow. Two options: raise the ceiling past 50₽ (faster, more
expensive per install, less sustainable), or find 10–20 more keywords
(slower today, cheaper per install long-term, what the bootcamp explicitly
recommends).
Stakes if we pick wrong: Raising the ceiling past 50₽ commits you to that
CPI on this campaign for its lifetime — warmed campaigns hold their bid
average. You can't easily lower it back after spending at the higher cap.
Recommendation: B — every bootcamp post says expand keywords first.
Completeness: A=6/10 (works but expensive), B=9/10 (correct play)
Pros / cons:
A) Raise ceiling to 60–80₽
  ✅ Same-day delivery improvement — bid changes in Yandex propagate in 5–10h, so by tomorrow you'll see traffic flow
  ✅ Useful for last-mile pushes — e.g. you're at 250 installs and want to clear 300 by end of week before stopping paid
  ❌ Doubles CPI permanently for this campaign — even if you lower the cap later, the warmed bid average stays elevated
  ❌ Burns budget on the most-contested 3–5 head queries which aren't your highest-converting users anyway
B) Expand keyword list to 30–40 phrases at current 50₽ cap (recommended)
  ✅ Cheaper per install — indirect-intent keywords have less auction competition
  ✅ Higher conversion per click — indirect-intent searchers articulated their problem in their own words; better intent match
  ✅ Future-proof — when you launch product 2, the keyword research is already done
  ❌ Slower today — 2–3 days to fill the new keywords with delivery
Net: B unless you have a launch-week deadline driving urgency. If urgency
real, run A for 3 days only then revert.
```

### 6.6 Write the milestone snapshot

After each milestone diagnosis, append to `04-promote.md`'s
`## Funnel snapshot` section. Format:

```markdown
### Snapshot @ <100|300|1000> installs (YYYY-MM-DD)
- Installs (CWS dashboard): <N>
- first_visit (GA4 + Linux filter): <N>
- Listing conversion: <X.X%> (benchmark: 10–20% paid, 15–30% organic)
- Welcome Page Umami visits: <N> (delta from CWS dashboard: <±%>)
- Week-1 retention (Amplitude): <X.X%> (benchmark: 50–70%)
- Reviews: <N> / avg <X.X>⭐
- Open issues: <bullet list — what's below benchmark, what's the fix>
```

---

## Phase 7 — Write `./.cws/04-promote.md` + update state

### 7.1 Artifact structure

Write `./.cws/04-promote.md` with frontmatter:

```yaml
---
stage: cws-promote
status: complete
created: <ISO ts>
updated: <ISO ts>
slug: <SLUG>
extension_id: <id>
---
```

Required sections (in this order):

```markdown
## Platform
- Chosen first platform: <Yandex|Google|Facebook>
- Reason: <one line tied to geo + warm-up speed>
- Warm-up: <competitor URL warmed during moderation; spent ~$<N>>

## Campaigns
- Platform: <name>
  - Campaign URL: <dashboard link>
  - Shape: <wide|narrow|wide+interests>
  - Keyword set: <N keywords>; list at <path>
  - Bid cap: <value>; daily budget: <value>
  - Current spend: <value>; status: <running|stopped|rejected (reason)>
  - Ad creatives: <paths to banner files>; texts <inline or path>

## UTM + GA4
- UTM pattern in use: `utm_source=<...>&utm_medium=cpc&...`
- GA4 property: <id>
- Linux-OS filter segment: <yes|no>
- install_id propagation: <yes|no>
- Umami site: <id|n/a>
- Amplitude project: <id|n/a>
- Honest note: GA4 source attribution is broken-by-design; conversion
  computed from `install / first_visit` with Linux filter; cross-
  referenced against CWS dev dashboard installs.

## Reviews
- Source: <friends|kwork|mixed>
- Count visible on CWS: <N> / avg <X.X>⭐
- Cadence used: <X reviews/day max>
- Widget installed: <yes|no> (path: extension/<...>/review-widget.html)
- Widget trigger: <on first open|after Nth core action>
- Negative reviews handled: <count + summary of replies>

## Funnel snapshot
### Snapshot @ 100 installs (YYYY-MM-DD)
<bullets per Phase 6.6>

### Snapshot @ 300 installs (YYYY-MM-DD)
<bullets per Phase 6.6>

### Snapshot @ 1000 installs (YYYY-MM-DD)
<bullets per Phase 6.6>
```

If the user hasn't hit a later milestone yet, leave that subsection out
(don't write `### Snapshot @ 1000 installs: TBD`) — the artifact is
re-entered as milestones land.

### 7.2 Update state.json

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p=pathlib.Path('./.cws/state.json'); d=json.loads(p.read_text())
d.setdefault('promote',{})
d['promote'].update({
  'platform': '<chosen>',
  'utm_pattern': 'utm_source=<...>&utm_medium=cpc&utm_campaign=<...>&utm_content=<...>',
  'reviews_count': <N>,
  'weekly_installs': <N>,
  'installs_paid_total': <N>,
  'first_organic_install_ts': '<ISO or null>',
  'conversion_install_pct': <X.X>,
})
gp = d.setdefault('gates_passed',[])
if 'promote' not in gp: gp.append('promote')
d.setdefault('history',[]).append({
  'ts': datetime.datetime.utcnow().isoformat()+'Z',
  'stage':'cws-promote','event':'gate_passed:promote'
})
d['last_updated'] = datetime.datetime.utcnow().isoformat()+'Z'
p.write_text(json.dumps(d,indent=2))
PY
```

### 7.3 Log a timeline event

```bash
"$BIN/cws-timeline-log" "{\"skill\":\"cws-promote\",\"event\":\"gate_passed\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

---

## Mechanical iron rules (re-state at every D-brief)

These are non-negotiable. If the user pushes against any of them, this is
a hard-stop — explain the cost in concrete numbers and refuse to proceed
on the unsafe path.

1. **Never warm two ad accounts in parallel.** Trust budget splits;
   parallel-account-creation reads as "shotgun advertiser" and ML
   clips both. One platform through full warm-up at a time. Second
   platform unlocks after the first clears 100 installs with stable
   CPI.

2. **UTM tag everything; assume GA4 attribution is broken; rely on
   CWS install count.** GA4 source attribution lies (paid → "organic"
   bucket). UTM tags are *labels* for cross-reference, not attribution
   chains. The CWS dev dashboard install count is the canonical truth.

3. **1–2 reviews per day max from the same source.** More clusters as
   fake and gets all deleted. No two reviews from the same device or
   IP. No VPNs, no proxies. Rewrite the review template every day.

4. **Filter Linux OS from FB ad conversion reports = filter bots.**
   After moderation FB floods the listing with Linux-box bots verifying
   you didn't swap the page. Conversion without the filter reads ~5%;
   with it reads ~15%. The filter is the difference between thinking
   the product is broken and shipping it.

5. **Bid increases only after the keyword set is exhausted.** Yandex
   ceiling 30–50₽; Google ceiling $0.40. Past those, the auction is
   telling you to find different keywords, not raise the cap.

6. **Add keywords first; raise bids only second.** Indirect-intent
   keywords (in the user's own language) outperform head-keyword bid
   ladders for the cold-start goal.

7. **Stop paid traffic at 100–300 installs.** Past $300 each extra
   dollar is worth less; if organic doesn't follow within 1–2 months,
   the product is the problem, not the budget. Launch a second product
   instead.

8. **Never write your own reviews.** Chrome anti-bot penalty hits the
   *extension*, not the account. Founder-written reviews from second
   accounts are the single most common rating-deletion cause.

9. **The 24–72h post-launch window is non-recoverable.** Google runs
   invisible behavioral tests in that window. Ads delaying past it
   bake in a bad ranking baseline that fixing bugs a month later
   cannot undo.

10. **Run paid traffic immediately after listing live, not later.**
    Ads act as social signals — Google sees users arriving and trusts
    the product more. After Google indexes you, social signals matter
    less.

---

## When NOT to use this skill

`cws-promote` is **hard-gated** on `extension.moderation_status ==
approved`. Refuse to run otherwise.

Other refusal cases:

- **Pre-launch promotion** — running paid traffic at a `pending` or
  `rejected` listing burns money on a non-existent destination and
  flags the ad account as advertising unverified software. Route to
  `cws-launch`.

- **Re-running paid promotion past $300 / 300 installs without organic
  trickle** — that's the bootcamp's explicit "launch a different
  product instead" signal. Route to `cws-retro` to assess what's
  blocking organic, then to `cws-idea` for the next product.

- **Trying to run cws-promote in parallel with cws-build or cws-
  package** — Stage 4 starts *after* Stage 3 closes. If
  `gates_passed` is missing `launch`, refuse.

- **Without a CWS extension ID** — `extension.id` must be set in
  state. The UTM destination, review widget URL, and Amplitude install
  attribution all require it.

- **Without Stage 2 keyword list** — running ads with 3 hand-picked
  keywords is the #1 cause of stalled paid spend. If `02a-listing.md`
  has fewer than 10 keywords, route to `cws-resync` to backfill before
  burning ad spend.

---

## Companion skills

These run *alongside* `cws-promote`, not after it:

- **`cws-retro`** — weekly snapshot cadence. Run every Monday during
  the paid-promotion window to capture install / conversion /
  retention deltas. The bootcamp says real conclusions about whether a
  product "works" need ~2 months; `cws-retro` is how you accumulate
  the data points to make that call without revisionism.

- **`cws-careful`** — gate before any *bid widening past the 30–50₽
  Yandex ceiling*, any *platform switch* (e.g. adding Google while
  Yandex is still warming), or any *campaign delete-and-recreate* —
  the last destroys trust budget. `cws-careful` makes you state the
  cost out loud before the action.

- **`cws-learn`** — record what worked in this launch's promote stage.
  The bootcamp accumulates by every operator writing back: which
  keyword shapes converted, which review template phrasing got flagged,
  which Yandex bid ceiling actually delivered for which product
  category. `cws-learn` is the write side of the `cws-learnings-search`
  used in the preamble.

---

## Tools that don't help here

- Building anything (that's `cws-build`).
- Listing copy edits (that's `cws-package` or `cws-resync`).
- Banner / icon work (that's `cws-launch`).
- Anything before moderation approval (that's `cws-launch`).
- Paywall / Stripe / in-app purchase (that's `cws-monetize`).

If the user asks for any of those, route to the right skill rather than
inlining the work here.

---

## Skill Routing Footer

End the skill with one `Next: /cws-<skill>` line. Pick by current state:

- **First promote pass complete (Phase 7 just wrote `04-promote.md`,
  reviews seeded, 100-install snapshot recorded)** → `cws-retro`.
  Capture the baseline before the weekly cadence kicks in.

  ```
  Next: /cws-retro
  Why: First paid pass landed. Capture the baseline week-1 snapshot
  before paid spend tapers and organic trickle starts; the next 2 months
  are the behavioral-test window.
  ```

- **Weekly installs ≥ 3000 and search position consolidated (head
  keyword in top 5 of CWS search results for ≥2 weeks)** → `cws-
  monetize`. The product earned the right to a paywall.

  ```
  Next: /cws-monetize
  Why: 3000 weekly installs with a consolidated search position means
  the cold-start loop broke and organic is doing the work. Stress-test
  via cws-challenge first if you haven't already, then ship the paywall.
  ```

- **Mid-promote week, < 3000 weekly installs, no immediate decision
  needed** → `cws-retro` for the weekly cadence.

  ```
  Next: /cws-retro
  Why: Weekly retro is the cadence during paid-promote. Capture the
  install / conversion / retention deltas; bootcamp says real
  conclusions need ~2 months and the only way to get them
  un-revisionist is the weekly snapshot.
  ```

Never list 3 options. Never say "you can run X, Y, or Z." Pick one based
on the gates and weekly install count actually present in state.
