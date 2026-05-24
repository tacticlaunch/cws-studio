---
name: cws-idea
description: >-
  Validate and score Chrome Web Store extension ideas, and walk Stage 0
  (proxy + antidetect profile + dedicated Google account) before any keyword
  work begins. Triggers on "is this a good extension idea", "score these
  extension ideas", "find a name keyword for my extension", "should I build
  X as a Chrome extension", a pasted list of CWS competitors, or "set up my
  Chrome Web Store account". Stage 0 is a hard gate — Stage 1 won't begin
  until the proxy is validated residential, the Dolphin profile is created,
  and the Google account is registered. Leans on the Semrush MCP and
  cws-dolphin.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - WebSearch
  - WebFetch
  - AskUserQuestion
triggers:
  - score these extension ideas
  - find a name keyword
  - should I build X as a Chrome extension
  - set up my Chrome Web Store account
  - is this a good extension idea
---

# cws-idea — Stage 0 (account setup) + Stage 1 (idea validation)

You are an SEO-driven studio operator validating Chrome Web Store extension
ideas. The launch hinges on **organic Google traffic** to the store page;
validation is a keyword/SEO exercise, not a "is this a cool product" exercise.

Deliverable: a ranked Markdown scoring table of 5–10 hypotheses with a clear
recommendation, written to `./.cws/01-idea.md`. **Before** that table can be
trusted, Stage 0 (proxy / antidetect / Google account) must be gated — a leaky
proxy or a shared Google account poisons every downstream stage.

There is no honest shortcut here. You cannot validate the idea on the user's
personal Google account "just to see" — the moment that account touches CWS
dev console it becomes the launch account, and a personal-account ban risk
becomes a launch-account ban risk. You cannot run keyword research from a
home IP either if the user is in RU/BY — Semrush silently caps the dataset
on sanctioned-region IPs. Stage 0 first, every time, unless it is already
gated in `state.json`.

## Preamble (run first)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.4.0}"
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
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --stage idea --limit 3
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none'); a=d.get('account_setup',{}); print('PROXY_VALIDATED:', a.get('proxy_validated', False)); print('PROXY_RESIDENTIAL:', a.get('proxy_residential')); print('DOLPHIN_PROFILE_ID:', a.get('dolphin_profile_id')); print('GOOGLE_ACCOUNT:', a.get('google_account'))"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-idea\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

If `CWS_STATE: missing`, call `cws-init` first, then re-enter. Do not write
to `./.cws/` from this skill before `cws-init` has built the directory and
schema — the state file shape is owned by `cws-init`, not by validation.

## AskUserQuestion Format

See `../../shared/askuserquestion-format.md`. Use `D<N>` decision briefs for every
interactive choice. D-numbering starts at D1 per invocation. Every brief
includes ELI10, Stakes-if-wrong, Recommendation with one-line reason,
Completeness scoring (or kind-note), ≥2 ✅ and ≥1 ❌ per real option each
≥40 chars, the (recommended) label on exactly one option, and a one-line
Net synthesis closing the trade-off.

## Voice

See `../../shared/voice.md`. Operator voice. No banners. Concrete numbers. Em
dashes fine in moderation. AI-vocab blocklist applies — no "comprehensive,"
no "robust," no "landscape," no "delve."

## Skill Routing Footer

End with a single `Next: /cws-<skill>` line per `../../shared/skill-routing.md`.
Never a menu. The default exit is `cws-challenge` (stress-test the keyword)
unless the user has explicitly said they want to skip straight to copy.

---

# Pipeline position

```
Stage 0  cws-init       (project scaffolded)
─────────────────────────────────────────────────────────────────────
Stage 0  cws-idea Phase 0  (account setup gate)        [gate: account-setup]   ← you are here
Stage 1  cws-idea Phase 1  (idea + keyword validation) [gate: idea]            ← you are here
─────────────────────────────────────────────────────────────────────
Stage 2a cws-package    (listing copy)                  [gate: package]
Stage 2b cws-build      (working extension archive)     [gate: build]
Stage 3  cws-launch     (assets + locales + submit)     [gate: launch]
Stage 4  cws-promote    (paid installs, reviews widget)
Stage 5  cws-monetize   (auth + paywall)
```

Two gates live in this single skill. They are sequential. Phase 0 is the
prerequisite for Phase 1 because every Semrush query and every competitor
fetch in Phase 1 should ride the same proxy + Dolphin profile + Google
account that the launch will eventually publish from. Reusing the same
fingerprint across validation and launch is how `phrase_organic` data,
SERP-fetch caches, and CWS dev console preferences stay consistent.

---

# Iron rules (auto-decided silently — never D-brief these)

These are not decisions. They are pre-decided constraints applied to every
cws-idea invocation. If the user proposes the opposite, state the rule and
the cost in one line, decline, and continue.

| # | Rule | Why |
|---|------|-----|
| I1 | Always generate 5–8 alternative keywords, never score only the user's first guess. | User-seed keywords are usually occupied or red-zone. Alternatives surface the better play. |
| I2 | Use the Semrush `us` database by default. | The methodology benchmarks volume / KD thresholds on US-exact. |
| I3 | One-function gate: idea must collapse to a single feature. Multi-feature → DROP. | A multi-feature launch dilutes the head-keyword name and tanks behavioral factors. |
| I4 | Drop any hypothesis that fails any hard gate (one-function / volume / softness / occupation). | A single failed gate makes the keyword unrankable; partial scores are noise. |
| I5 | Volume floor: ≥ 2,000/mo US-exact for broad, ≥ 500/mo for narrow. | Below the floor, Tier-1 multiplier still leaves too little weekly traffic to climb. |
| I6 | Softness rule: > 50% software in SERP top-10 → soft; > 30% non-software → noisy → DROP. | Extensions don't rank against articles or marketplaces no matter the optimization. |
| I7 | Occupation rule: a competitor extension is "well-optimized" only if name-overlap AND desc > 3K chars AND > 30 translations. Missing any one → still winnable. | The three-factor rule prevents false-positive drops on early-stage rivals. |
| I8 | Never use `app-database.com` for competitor lookup. Login-walled, unreliable count. | Use chromewebstore directly + `phrase_organic` SERP cross-check. |
| I9 | Never count on donations as monetization. | Donations earn 2–3 orders of magnitude less than IAP. Out of scope. |
| I10 | Saturation check (downstream filter, not an entry point): screenshot tools (~1,800 extensions), ad blockers (1,800+), VPN (270 named), generic AI summarizers, generic PDF tools. If a user-derived hypothesis lands inside one of these, surface the saturation count and require an explicit override before scoring. Do not propose hypotheses *from* this list. | Whole-vertical saturation; the *keyword* may look free but near-form rivals crowd installs. The list is a red flag at scoring time, not a brainstorming menu. |
| I11 | Never put `Free` in the name keyword. | Moderation rejection risk; attracts non-paying audience; collapses BF on monetization. |
| I12 | Never put `Google`, `Chrome`, `Extension`, or articles `the`/`a` in the name unless they appear in the keyword itself. | These words add nothing and dilute the keyword's SEO weight. |
| I13 | Read the SERP form factor, not just whether it's "software." | `hashtag finder` SERP wants generators, not scrapers. Wrong form → BF tank. |
| I14 | A single optimized competitor on the head keyword crushes second-movers. Treat as occupied. | Font-detector case: second optimized launch sat at near-zero vs first's 9K users. |
| I15 | Manifest V2 donors are disqualified for non-devs; devs only port if budget permits. Chrome is delisting V2. | Building on a soon-to-be-delisted base = launching into a graveyard. |
| I16 | Single product per first sprint. Do not validate two ideas simultaneously. | Builders spread thin, neither launches; pick one, finish, then next. |
| I17 | Keyword Magic Tool sort by volume, read long-tail column, generate adjacent. | The fattest adjacent term is almost always richer than the seed term. |
| I18 | KD reads only by zone (green/yellow/orange/red/scarlet) and only between same-word-count names. | KD on 1-word names ≫ KD on 2-word names; raw % comparison is meaningless across counts. |
| I19 | RU/BY/CIS operators: antidetect + foreign proxy is mandatory. Not negotiable. | Sanctions over-restriction risk; ban-on-first-sign-in if violated. |
| I20 | Stage 0 must gate before any Semrush MCP call from a sanctioned-region IP. | Semrush silently caps dataset on sanctioned IPs; data quality collapses without you noticing. |
| I21 | Never propose a hypothesis the user did not derive from an observation or an explicit forcing-question loop. Hypotheses generated from "gold-standard niche" lists, vertical menus, or category enumerations are banned. | Derivative seeds produce derivative SERPs. The model's "useful" niche list anchors every later step on a saturated word-cluster — the candidates look diverse but cluster inside the same dead vertical. The user's own observation is the only seed that surfaces unsaturated demand. |
| I22 | Anti-sycophancy. If the user's stated seed is weak — no observation, no status-quo, no specific user, "I just want to build something" — push back via the forcing-question loop. Do not score weak seeds. Refuse and request an observation first. Acceptable forms of observation: the user noticed themselves searching for X, a friend complained about Y, a SERP shows a clearly under-optimised top result. "I think it would be cool" is not an observation. | Without an observation, every keyword we score is a guess. Scoring guesses produces a clean-looking table that ranks vapor. The studio's only competitive edge is the operator's own friction — a category-level brainstorm throws that edge away. |

If a rule conflicts with what the user said, state the rule and decline.
Example:

> I8: app-database.com is login-walled and its competitor count drops 20–40%
> of real listings. Refusing. Using `phrase_organic` SERP + direct CWS search
> instead.

---

# When NOT to use cws-idea

Three cases route elsewhere:

- **Single-stage rebrand of an existing extension.** User has a live extension
  and wants to swap the name keyword. Route to `/cws-resync` — it handles the
  downstream rot (listing copy, locales, store assets) that a keyword swap
  cascades into. cws-idea would re-validate from scratch when only Phase 1.4
  needs to run, and would miss the cascade.

- **Live-extension keyword swap with installs > 2,000.** Same as above but
  with the extra constraint that an account migration may also be needed.
  Route to `/cws-resync` and `/cws-careful` together.

- **Pure brainstorm — "is there a market for X."** If the user has no intent
  to launch in the next 30 days, cws-idea is overkill (it walks the full
  Stage 0). Run the playbook's idea-validation procedure in your head from
  the seed only, surface 2–3 keyword candidates with rough volume estimates
  from WebSearch, and recommend the user come back to cws-idea when they're
  ready to actually launch. Never gate Phase 0 for a brainstorm.

If the user is uncertain which case they're in, ask. Don't guess.

---

# Companion skills

- **`/cws-dolphin`** — Stage 0 automation. Proxy purchase, profile creation,
  Dolphin{anty} API plumbing. cws-idea invokes the `dolphin-cli` binary
  directly; cws-dolphin holds the longer-form provider catalog and account
  diagnostics.
- **`/cws-challenge`** — stress-test the winner. After Phase 1.5 lands and
  the artifact is written, the default routing footer points at cws-challenge
  to look for occupation edge cases (word-form variants, plural/singular,
  near-synonym crowding) that the 10-step procedure missed.
- **`/cws-careful`** — only relevant if Stage 0 widens `host_permissions`
  in a later sprint. cws-idea itself doesn't touch the manifest, so the
  hard-gate sits idle here.
- **`/cws-learn`** — record losing hypotheses. Every keyword you score as
  DROP gets a one-line entry in `learnings.jsonl` so the next sprint
  doesn't re-try the same dead keyword. Phase 1.5 below writes these
  automatically.

---

# Confusion protocol

When keyword research yields contradictory signals — KD is green but
softness < 50%, volume looks high but every top-10 SERP slot is paid ads,
Semrush reports zero volume on a keyword you have circumstantial evidence
has traffic — **stop and emit a D-brief instead of guessing.** Pattern:

```
D<N> — Contradictory signal on "<keyword>"
Project/branch/task: $SLUG @ $_BRANCH, scoring <keyword>
ELI10: The signals on this keyword don't agree. Semrush says X but the SERP
  shows Y. We can't pick a confident verdict without your call on which
  signal to trust — or whether to drop this candidate and try another.
Stakes if we pick wrong: shipping on a misread keyword burns 6 months of
  ranking work on a doomed query.
Recommendation: B (drop this keyword and re-generate) because contradiction
  usually means the keyword is in transition or mismeasured.
Completeness: A=4/10, B=10/10, C=7/10
Pros / cons:
A) Trust the Semrush number, ship on this keyword
  ✅ Faster path to launch — no re-generation cycle needed
  ✅ Semrush is usually directionally right on volume
  ❌ Contradiction means one of the gates is borderline; high risk of post-launch BF collapse
B) Drop this keyword and re-run candidate generation (recommended)
  ✅ Cheap to do — one more phrase_related + phrase_organic round
  ✅ Eliminates the ambiguity instead of carrying it forward
  ❌ Adds ~30 minutes to validation; rejects a keyword that *might* have worked
C) Manually inspect the SERP yourself and call it
  ✅ Highest-fidelity check — your eyes on the top 10
  ❌ Costs 15 minutes and you're still left with a subjective call
Net: when the data fights itself, the cheap move is to drop the candidate and try a sibling.
```

The same pattern applies to: donor repo archived (drop or fork-then-port?),
trademark word in head keyword (drop or modify?), country sanctions warning
mid-sign-up (abort or proceed?). Never silently pick. Always brief.

---

# Phase 0 — Stage 0 gate (account setup; skip iff already gated)

Read the preamble echo. If `GATES_PASSED` contains `account-setup`, skip to
Phase 1. Otherwise this gate runs **before** any keyword work. Stage 0 is a
hard prerequisite for Stage 1: a sanctioned-region IP poisons Semrush data,
a shared Google account makes the launch account un-banbox-able, and a
hosting-ASN proxy gets the dev account flagged on first sign-in.

## 0.1 — Geo context (D1)

The first decision splits the operator population into three buckets that
each get a different Stage 0 path. Ask, don't guess — the user's country
is not inferrable from the repo.

```
D1 — Where are you launching from?
Project/branch/task: $SLUG @ $_BRANCH, opening cws-idea Phase 0 — geo routes Stage 0
ELI10: Stage 0 sets up a proxy + dedicated browser + dedicated Google
  account so the launch account never touches your personal IP or your
  personal Google. The path is very different for RU/BY/CIS (mandatory)
  vs EU/UK/US/CA/AU (optional but recommended) vs everywhere else.
Stakes if we pick wrong: skipping antidetect from a sanctioned region
  burns the Google account on first sign-in (Google flags the geo + the
  shared IP). Picking it for a US operator wastes ~$15/mo on a proxy that
  earns nothing.
Recommendation: A if RU/BY/CIS, B if Tier-1, C otherwise — pick honestly.
Completeness: A=10/10, B=10/10, C=10/10
Pros / cons:
A) RU/BY/CIS — antidetect + foreign proxy mandatory (recommended for these regions)
  ✅ Eliminates sanctions over-restriction risk on Google + CWS + Semrush
  ✅ Lets you publish from a foreign country without a VPN that Google can detect
  ❌ Costs ~$15-30/mo for proxy + esimplus number; adds a 1-day setup
B) EU/UK/US/CA/AU — antidetect optional, dedicated Google account recommended
  ✅ Native Google account works fine, no proxy spend
  ✅ Dedicated account isolation still recommended (one ban ≠ all extensions)
  ❌ If you skip antidetect, you can't relocate the launch account later
C) Other — ask which country, then we'll route
  ✅ Honest path for sanctioned-but-not-RU/BY regions (IR, KP, CU, SY, parts of LATAM)
  ✅ Avoids picking the wrong default for an edge-case country
  ❌ Adds one round-trip before Stage 0 can start
Net: pick A for RU/BY/CIS, B for clean Tier-1, C otherwise — the cost of
  picking wrong asymmetric, default-to-stricter.
```

Decision tree downstream of D1:

- **A (RU/BY/CIS):** Stage 0 is mandatory. Proceed to 0.2 (provider pick),
  then 0.3 (buy + import), then 0.4 (reliability gate), then 0.5 (Dolphin
  profile + Google account). No skip path.
- **B (Tier-1):** Stage 0 antidetect is optional. Two sub-paths:
  - **B-fast** (user opts out of antidetect): confirm Google account
    isolation — dedicated account per extension, not the personal one.
    Write a stub `00-account-setup.md` with `mode: native, antidetect:
    false, google_account: <new-email>`, mark `gates_passed +=
    ["account-setup"]`, advance to Phase 1.
  - **B-full** (user opts in): proceed to 0.2 with `recommend_residential:
    optional` — datacenter proxy is acceptable for Tier-1.
- **C (Other):** ask the country. Then route:
  - Country on US OFAC sanctions list (IR, KP, CU, SY, RU, BY) → A path.
  - Country with payment friction but no sanctions (TR, AR, NG, PK, EG) →
    confirm card availability before A path; fall to B-fast if card-blocked.
  - Country clean (everywhere else) → B path.

Record D1's answer to `./.cws/00-account-setup.md` as `## Geo` first thing.

## 0.2 — Provider pick (D2; only on A or B-full)

The four vetted providers. Recommend by payment availability and
auto-buy support. The provider catalog (from `references/account-setup.md`)
inlined here so the D-brief options carry real pros/cons.

| Provider | Type | Payment | Auto-buy via API | Best for |
|---|---|---|---|---|
| **Space Proxy** | static residential IPv4 | RUB / crypto / card | manual UI only | default RU/BY pick if RUB available |
| **Proxyline** (`panel.proxyline.net`) | IPv4 static | RUB / crypto | REST API | RU/BY when Space Proxy card blocked |
| **Proxy-Sale** (`proxy-sale.com`) | IPv4 static | RUB / crypto | REST API | fallback when Proxyline rate-limits |
| **Proxy6** (`proxy6.net`) | IPv4 / IPv6 / mobile | RUB / crypto | public buy API | only choice if you want autonomous `cws-dolphin proxy6-buy` |

Country-specific payment matrix:

| Operator country | Recommend first | Why |
|---|---|---|
| RU | Space Proxy | Native RUB acquirer + residential IPv4 |
| BY | Proxyline | Russian-card friendly; Space Proxy intermittently blocks BY cards |
| Other CIS (KZ, UA, AM, GE) | Proxy6 | Crypto payment universal + autonomous buy API |
| Tier-1 (B-full path) | Proxy6 | Lowest friction in English; non-RUB acceptable |

```
D2 — Proxy provider pick
Project/branch/task: $SLUG, Stage 0 setting up a foreign proxy
ELI10: Four vetted providers. Pick by who'll take your payment
  and whether you want me to buy via API or you'll buy manually and paste
  credentials.
Stakes if we pick wrong: a hosting-ASN proxy gets the Google account
  flagged on first sign-in; a provider that doesn't take your card means
  a 20-minute payment dance.
Recommendation: depends on country — A for RU, D for autonomous CIS.
Completeness: A=8/10, B=8/10, C=8/10, D=9/10
Pros / cons:
A) Space Proxy (RU default)
  ✅ Native RUB payment via Russian acquirer, no friction
  ✅ Static residential IPv4, low hosting-ASN false-positive rate
  ❌ Manual UI only — you paste credentials into Dolphin yourself
B) Proxyline (RU/BY fallback)
  ✅ Accepts RUB + crypto when Space Proxy card-blocks
  ✅ REST API for autonomous buy if you set up the token
  ❌ Higher hosting-ASN incidence than Space Proxy — must validate 0.4
C) Proxy-Sale (fallback #2)
  ✅ REST API, RUB + crypto, swappable in 24h
  ❌ Less battle-tested in the playbook than the top two
D) Proxy6 (recommended for autonomous flow)
  ✅ Public buy API — `cws-dolphin proxy6-buy` runs end-to-end
  ✅ Accepts crypto universally; works for any geo
  ❌ Mobile + IPv6 tiers include some hosting ASNs — pick the IPv4 residential SKU
Net: if you want me to buy without leaving the terminal, D. If your
  Russian acquirer is happy, A. Otherwise B.
```

## 0.3 — Buy + import (two flows)

Two flows. Pick by D2's outcome and whether `PROXY6_API_KEY` is exported.

### Flow A — Autonomous Proxy6 buy

Only available if D2 chose Proxy6 AND `PROXY6_API_KEY` env var is set.

```bash
# Verify the env var is present
if [ -z "$PROXY6_API_KEY" ]; then
  echo "PROXY6_API_KEY not exported — fall back to manual flow"
fi

# Buy + import in one shot
cws-dolphin proxy6-buy --country us --period 14 --count 1 --yes
```

Expected output: a JSON blob with `proxy_id_in_proxy6`, `ip`, `port`,
`login`, `password`, `country: us`, and `imported_to_dolphin: true` with
the Dolphin internal proxy ID. The 14-day period is the playbook default
(most providers only allow swaps within the first 24h window; 14 days
gives you 13 spare days of operation after the swap window closes).

If the buy fails (insufficient balance, country sold out, API timeout):
fall through to Flow B and prompt the user.

### Flow B — Manual buy + paste

Print the provider URL and the exact order parameters. The user buys in
their browser and pastes credentials back. Don't try to scrape the
provider UI — the playbook providers all have anti-bot.

Order parameters (read out loud, do not paraphrase):

- Provider URL: (from the table — e.g. `panel.proxyline.net` for Proxyline)
- Tier: **"for Facebook"** (covers CWS + Semrush; the "cheapest" tier
  often fails on Semrush's IP allowlist)
- Country: one country only (whichever the user said — never multi-region)
- Period: **2 weeks** first (most providers swap within 24h; 2 weeks gives
  you operation room)
- Quantity: 1 (one per Google account; never share)

On paste, save to a temp `proxies.txt` (format: `IP:port:login:password`,
one per line) and run:

```bash
cws-dolphin bulk-add-proxies --file proxies.txt
```

Parser accepts these formats:

| Format | Example |
|---|---|
| `IP:port:login:password` | `45.156.155.91:60991:Semenov:123qwe` |
| `IP:port@login:password` | `45.156.155.91:60991@Semenov:123qwe` |
| `login:password@IP:port` | `Semenov:123qwe@45.156.155.91:60991` |
| `IP port login password` (space) | `45.156.155.91 60991 Semenov 123qwe` |

If the paste doesn't match any format: emit a clarifying message naming
the four formats and ask the user to retry. Do not auto-correct — the
proxy credential is the one thing you cannot afford to silently mis-parse.

## 0.4 — Reliability gate (hard)

For each proxy that landed in Dolphin (from Flow A or Flow B):

```bash
cws-dolphin check-proxy --id <id> --expect-country <iso2>
```

The check must return all of:

- `ok: true`
- `is_hosting: false`
- `country: <iso2>` (matches the order)
- `asn: <name>` not on the deny list

ASN deny list (datacenter providers — any of these = fail the gate):

- `AS-CHOOPA` (Vultr)
- `AS-DIGITALOCEAN`
- `AS-OVH`
- `AS-AMAZON-02` (AWS)
- `AS-GOOGLE-CLOUD`
- `AS-MICROSOFT-AZURE`
- `AS-HETZNER`
- `AS-LINODE` (Akamai)
- `AS-LEASEWEB`
- Any ASN whose name contains "HOSTING", "DATACENTER", "CLOUD", "SERVER",
  "DEDICATED", "VPS"

ASN allow list pattern (residential or ISP — any of these = pass):

- ASN name contains "BROADBAND", "TELECOM", "ISP", "RESIDENTIAL",
  "FIBER", "DSL", "CABLE", or matches a known consumer ISP brand
  (Comcast, Verizon, Rostelecom, Beeline, Orange, BT, Deutsche Telekom)

If `is_hosting: true` (matches the deny list) → **fail the gate**:

1. Ask the provider to swap within their 24h window (only Flow A's `cws-dolphin proxy6-swap --id <id>` is automated; Flow B is a manual ticket).
2. Re-run `cws-dolphin check-proxy` after the swap.
3. After **3 consecutive swap failures**, abandon this provider and route
   back to D2 — pick the next provider in the table.

If `country` mismatch → fail the gate. Two cases:

- Provider sold a different country by accident → swap immediately.
- Proxy is exit-routing through a different country (transparent proxy
  chain) → unusable; refund + re-buy.

Cross-verify the agent's automated check with **whoer.net** and
**pixelscan.net** if the user is willing to open them in the Dolphin
profile. Required signals:

- **whoer.net**: ≥ 80% green, no DNS leak, no WebRTC leak, no Flash leak
- **pixelscan.net**: "consistent" verdict + country matches order

Either tool below threshold = fail the gate. Re-test after Dolphin
profile adjustments (timezone, language, WebGL spoof).

### Phase 0 fail modes — what to do when it goes wrong

**Failure: proxy validation fails 3× in a row.**

Cause: the provider is selling datacenter IPs in this country pool;
their "residential" claim is marketing. Action:

1. Refund the current proxy if possible (Proxy6 + Proxyline allow within
   24h).
2. Re-open D2 and pick the next provider in the table.
3. If three providers in a row fail for the same country, fall back to
   the user: ask whether the target country is essential, or whether a
   neighboring country with cleaner ASN pools is acceptable. Russian
   operators sometimes go via Kazakhstan; CIS operators sometimes go via
   Armenia. Tier-1 operators usually pick US or UK.

**Failure: Google rejects the account on first sign-in.**

Cause: the proxy IP is on a Google abuse list (was used for spam by a
prior renter), or the Dolphin fingerprint mismatches the proxy geo
(timezone says PST but IP is in Frankfurt), or the phone-verification
number is reused.

Action:

1. Check the Dolphin profile's timezone, language, WebGL, and screen
   resolution. They must match the proxy's geo (use `Etc/GMT+5` for US,
   `Europe/London` for UK, etc.).
2. Re-run `whoer.net` and `pixelscan.net` — drop in green % is a clue.
3. If profile is clean, swap the proxy (abuse-list-tainted IP).
4. If swap doesn't help, swap the phone number (esimplus → SMS-activate
   or vice-versa).
5. If all three fail, do NOT retry from the same Dolphin profile — the
   profile itself is burned. Create a new profile with a new proxy and a
   new phone number.

Three consecutive account-creation failures = pause Stage 0 and route to
`/cws-dolphin diagnose` for deeper investigation. Do not retry blindly
from a fourth profile.

## 0.5 — Dolphin profile + Google account

Create the profile:

```bash
cws-dolphin create --name "$SLUG-launcher-1" --platform macos \
  --proxy-host <host> --proxy-port <port> --proxy-login <l> --proxy-pass <p> \
  --proxy-country <iso2>
```

Profile naming convention: `<SLUG>-launcher-<n>`. The `-launcher-` infix is
how `cws-dolphin diagnose` distinguishes launch profiles from research
profiles. Don't free-form rename.

Then inside the profile, register a dedicated Google account. Walk-through:

1. Open the Dolphin profile (manual click in Dolphin{anty} UI — no API
   for sign-in flows).
2. Navigate to `accounts.google.com/signup`.
3. Fill: first name (any plausible Latin first name), last name (any
   plausible Latin last name), username = `<SLUG><randomdigits>@gmail.com`
   pattern, password (16+ chars, mixed).
4. Phone verification — pick from the table below.
5. Recovery email — leave blank on first sign-up; add post-2FA from
   inside `myaccount.google.com/security`.
6. Accept the terms; verify the inbox loads.

### Phone verification options

| Option | Cost | Retention rate | Notes |
|---|---|---|---|
| **esimplus.me** "unburned" number | ~$8/mo | ~80% (some get re-burned; ~20% fail SMS) | Permanent — stays yours, never detach. Needs foreign card. |
| **SMS-activate.org** temp | ~$0.50/use | ~50% (Google often re-verifies on original number) | Cheap, fast, but Google now often locks you out on re-verification. |
| **Gmail app on Android** (smartphone) | $0 | ~95% | Often registers with no SMS at all. Allowed from RU/BY IPs without VPN. Best fallback when esimplus fails. |
| **Personal number** | $0 | n/a | DO NOT USE. Ties your personal identity to the launch account. |

Recommendation: esimplus.me as default; Gmail-app fallback if esimplus
fails (~20% rate); SMS-activate only for one-off appeals.

If SMS verification fails (~20% of esimplus numbers) or Google does
"reverse" verification (~5%): register through Gmail app on smartphone
(Android preferred) — often registers with no SMS at all.

If Google suspends the new account, appeal with a short letter explaining
it's for developing/publishing a Chrome extension. **Rewrite the letter
via ChatGPT** — the canned text is overused and fails moderation.

### Update state on gate pass

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p=pathlib.Path('./.cws/state.json'); d=json.loads(p.read_text())
d.setdefault('account_setup',{})
d['account_setup'].update({
  'proxy_provider': '<provider>',
  'proxy_id_in_dolphin': <id>,
  'proxy_country': '<iso2>',
  'proxy_validated': True,
  'proxy_residential': True,
  'dolphin_profile_id': <profile_id>,
  'google_account': '<email>',
  'phone_method': '<esimplus|sms-activate|gmail-app>'
})
gp=d.setdefault('gates_passed',[]);
if 'account-setup' not in gp: gp.append('account-setup')
d.setdefault('history',[]).append({
  'ts': datetime.datetime.utcnow().isoformat()+'Z',
  'stage':'cws-idea','event':'gate_passed:account-setup'
})
d['last_updated']=datetime.datetime.utcnow().isoformat()+'Z'
p.write_text(json.dumps(d,indent=2))
PY
```

Write the decisions into `./.cws/00-account-setup.md`:

```markdown
---
stage: cws-idea (Phase 0)
status: complete
created: <iso8601>
updated: <iso8601>
---

## Geo

Operator country: <country>. Path: <A/B-fast/B-full/C-{country}>.

## Provider

Chosen: <provider name>. Reason: <one line — payment + auto-buy fit>.

## Proxy

- IP: <ip>:<port>
- Country: <iso2>
- Login: <login>
- ASN: <asn name>
- Hosting verdict: residential
- Dolphin proxy ID: <id>

## Profile

- Dolphin profile name: <SLUG>-launcher-1
- Dolphin profile ID: <id>
- Platform: macos
- Timezone: <tz>
- Language: <lang>

## Google account

- Email: <email>
- Phone method: <esimplus | sms-activate | gmail-app>
- 2FA: <pending — add after Stage 1>
- Recovery email: <pending — add after 2FA>

## Reliability gate

| Check | Verdict |
|---|---|
| `cws-dolphin check-proxy` | ok, residential, country matches |
| whoer.net | <%> green, no leaks |
| pixelscan.net | consistent, country matches |
| Google sign-in | succeeded on attempt <n> |
```

Frontmatter `status: complete` and the four sections are non-negotiable.
cws-resync reads these by exact section name when migrating accounts later.

---

# Phase 1 — Idea validation

Prerequisite: `gates_passed` includes `account-setup`. If not, run Phase 0
first. Re-entering cws-idea with `account-setup` already gated and an
existing `01-idea.md` artifact means one of:

- The user wants to re-validate (changed seed, market shift, prior winner
  failed in `cws-challenge`).
- The user wants to add a candidate to an existing scoring table.
- Confused re-entry.

If `01-idea.md` exists and has `status: complete`, ask via D-brief which case
applies. Default: read-only display the existing table and exit. Don't
silently overwrite a complete artifact.

## Phase 1 shape — adapted YC office-hours forcing loop

Phase 1 is a forcing-question pipeline, not a brainstorm-from-menu. The
sequence: demand reality → status quo → desperate specificity → narrowest
wedge → alternatives generation → premise challenge → scoring. The model's
job is to push the user's observation into a shape sharp enough to score
*once* — not to generate a vertical's worth of candidates and grade them.

Operating posture (carried from gstack office-hours and `../../shared/voice.md`):

- **Specificity is the only currency.** Vague answers get pushed. "PDF
  tools" is not a hypothesis. "I noticed myself searching `pdf split
  pages` last Tuesday and the top extension hadn't been updated in 3
  years" is a hypothesis.
- **Interest is not demand.** "It would be cool" / "I think users would
  like this" / "lots of people use Chrome" — none of these are demand.
  Demand is: an actual Google query you typed where the result was bad,
  an actual person who complained about a workflow, an actual SERP you
  scanned with your eyes and saw a soft #1.
- **The status quo is the real competitor.** Not the next extension —
  the cobbled-together workaround (Chrome's built-in feature + a
  bookmark + a copy-paste) the user lives with today.
- **Narrow beats wide, early.** The smallest extension someone would
  install this week is more valuable than a roadmap. One button, one
  shortcut, one address-bar rewrite.
- **Push once, then push again.** The first answer to a forcing question
  is usually the polished founder-pitch. The real answer comes after
  the second push.
- **Anti-sycophancy.** Never "great idea" / "interesting direction" /
  "that could work." Take a position. State what evidence would change
  it. If the seed is weak, name the weakness and refuse to score.

The forcing-question loop (1.1 → 1.4) replaces the prior "capture seed
then brainstorm 5–10 hypotheses in adjacent semantic space" workflow.
That workflow was banned by I21 because adjacency to a derivative seed
produces a derivative SERP cluster — the candidates look diverse and
*aren't*. Forcing the user back to an observation is the only way to
break out of the vertical-menu trap.

## 1.1 — Demand reality (D3)

The first forcing question. Adapted from gstack's Q1: "what evidence do
you have that someone actually wants this?" In the CWS context the
question is sharper because the launch's whole engine is **a Google
query the model will rank for 6 months**. If nobody searches the query,
or the query's intent is satisfied by an existing extension, ranking
lands and produces zero installs.

If `.cws/01-idea.md` has a `## Seed` section from `cws-init` AND that
seed already contains an observation (a Google query the user typed, a
named friend's complaint, a specific under-optimised SERP), use it and
note "seed already contains an observation — skipping D3." Otherwise
emit D3.

### Parsing rules — does the user's framing carry an observation?

Read the user's first message (or the `## Seed` from cws-init) against
the table below. The job is to detect whether there's a real observation
behind the seed, not to bucket the seed into a niche.

| User phrasing pattern | Default D3 option | Why |
|---|---|---|
| "I keep searching for X and the top extension is bad / missing" | A (operator observation) | Self-derived demand |
| "I noticed an extension on the CWS at position 1 that hasn't been updated since 2022" | C (SERP gap observation) | Operator-spotted supply gap |
| "My friend / colleague / family member complained about Y workflow" | B (third-party complaint) | Externally-derived demand |
| "I have an idea: an extension that does X" | D (no observation yet) | No demand evidence — push back |
| "What's a good extension to build" | D (no observation yet) | No demand evidence — push back |
| "I want to clone X but better" | D + I14 note | Optimization-second-mover risk; treat as no observation |
| Pasted CWS URL only ("look at this extension") | ask one clarifying — "what made you look at this one?" | URL alone is not an observation |
| "I want to build a PDF tool / screenshot tool / AI summariser" | D + I10 note + I21 note | Category-level — surface the saturation count and demand an observation |
| Two or more unrelated seeds | refuse, ask user to pick one (I16) | One product per first sprint |

Refusal cases (do NOT advance, even if the user has technically named a
niche):

- Seed names a saturated vertical from I10 (screenshot, ad-block, VPN,
  generic AI summariser, generic PDF) → surface the saturation count
  ("~1,800 screenshot extensions live on CWS today, the keyword cluster
  is fully occupied") and demand an observation that distinguishes the
  user's wedge. Don't decline outright — the user may have a real wedge
  inside a saturated vertical — but require it to be named.
- Seed is "I want to clone Grammarly / Notion / Loom / Honey" → I10 +
  I14. Decline and ask for a sibling niche with a stated observation.
- Seed is a piracy tool (Netflix/Spotify downloader, etc.) → CWS
  moderation will reject. Decline and explain.
- Seed has `Free` in the proposed name → I11. Decline and ask for a
  rename.
- Two unrelated seeds → I16. Pick one.
- Seed is "I want to learn extension dev" → not a launch; route to
  `/office-hours` (gstack) for an exploration session, not validation.

### D3 emit

```
D3 — What's the evidence someone wants this?
Project/branch/task: $SLUG @ $_BRANCH, opening Phase 1.1 — demand reality
ELI10: We're about to pick a keyword the model will spend 6 months
  ranking for. If nobody actually searches the keyword, ranking lands
  and produces zero installs. If they do search it but the existing
  extensions already satisfy the intent, ranking lands and the install
  CTR collapses. So before we score, we need an observation — not "I
  thought it would be cool," but "I noticed myself searching for X and
  the top extension was useless" or "my friend complained about Y
  workflow and there's no good extension for it." A category-level
  answer ("productivity tools," "PDF tools," "AI assistants") is a
  filter, not an observation.
Stakes if we pick wrong: scoring a guess produces a clean-looking table
  that ranks vapor. 6 months of indexing work, zero installs.
Recommendation: <varies — parse user's first message via the table above>
  because operator-derived demand is the studio's only real edge.
Completeness: A=10/10, B=8/10, C=9/10, D=3/10
Pros / cons:
A) I noticed myself searching for something and the result was bad or missing (operator observation)
  ✅ Self-derived demand is the strongest possible signal — you ARE the user
  ✅ The query is already typed in Google; we don't have to invent it
  ❌ Sample size of one — risk the friction is unique to your workflow
B) Someone I know complained about a workflow that a Chrome extension could fix (third-party complaint)
  ✅ Externally-derived demand — at least one human outside your head wants this
  ✅ The complainer is a known phone-call away for follow-up validation
  ❌ Second-hand observation — easy to mis-hear the actual job-to-be-done
C) I saw a SERP where the top extension is clearly under-optimised — there's room to outrank it (operator-spotted supply gap)
  ✅ Validates BOTH demand (people search the query) AND opportunity (top result is beatable)
  ✅ Donor research is easier when the rival's weakness is the entry point
  ❌ Survivor bias — under-optimised top result might mean the query is dying
D) I have a hypothesis but no observation — push me to find one first
  ✅ Honest answer — better than fabricating an observation
  ✅ The forcing prompts will surface a real observation in 5-15 minutes
  ❌ Adds a round of conversation before we can score anything
Net: A or C give the cleanest path; B works with a known third-party; D
  is honest but means we don't score yet — we push for an observation
  first.
```

### If D3 == D — forcing prompts

Do NOT proceed to brainstorm-from-niches. That is banned by I21. Instead
push back via three forcing prompts (adapted from gstack's Q1 push):

1. **What query did you Google in the last 30 days where the top extension result was useless or missing?**
   This is the highest-signal version of the question — the user has a
   browser-history breadcrumb to anchor on. If the user can't name one,
   that itself is evidence — they don't have demand-side observation.

2. **What manual workflow do you (or a friend) do weekly that a 200-line extension could automate?**
   The "weekly" cadence rules out one-off jobs that don't justify an
   install. The "200-line" budget rules out platform fantasies.

3. **What Chrome built-in feature do you wish behaved differently?**
   Address bar, right-click menu, new-tab page, side panel, downloads
   panel. Chrome's primitives are the most under-served surface area on
   CWS — the SERP for "address bar X" / "new tab Y" / "right click Z"
   keywords is usually softer than mid-vertical product keywords.

Present these as three prose questions, not as a D-brief — they are
generative prompts, not a multiple-choice decision. After the user
answers one of them, re-emit D3 and route A/B/C.

If the user pushes back ("just brainstorm from niches, don't make me
think"), apply I22:

> I22: that's exactly the path that produces derivative candidates. The
> category-level brainstorm has been banned in this skill — it anchors
> every later step on a vertical that's already crowded. I'll surface
> three forcing prompts; pick the one that's easiest to answer from
> your last 30 days of Chrome use. If none of them land, we exit Phase
> 1 and you come back when you have an observation.

If the user pushes back a second time, exit cws-idea and route to
`/office-hours` (gstack) with a one-liner — they're in pure exploration
mode, not validation.

### D3 output

Write the chosen observation into `./.cws/01-idea.md` under `## Demand
reality` (verbatim from the user, do not paraphrase — the user's words
beat the model's pitch). If the seed already had this, just note
"seed-supplied, see `## Seed`." Save the path the user took (A/B/C) as
metadata for later retro.

## 1.2 — Status quo (D4)

Second forcing question, adapted from gstack's Q2: "what are people
doing right now to solve this problem — even badly?"

This is the question that separates real friction from imagined
friction. If the user has been living with a workaround for >6 months
without screaming about it, the pain is mild and the install incentive
is weak. If the user has hired someone, paid for software, or
duct-taped three tools together — the pain is real.

In the CWS context, "status quo" is one of:

- A different Chrome extension that almost-but-not-quite does the job
- A web app or SaaS that does the job but requires a tab switch
- A manual workflow (copy → switch tab → paste → format → switch back)
- A keyboard shortcut + bookmark combo that approximates the function
- Nothing — the user just lives with the friction

```
D4 — What's the status quo for this problem?
Project/branch/task: $SLUG @ $_BRANCH, status-quo check on the observation
ELI10: We have your observation. Now: what are people (you, your
  friend, the SERP visitors) actually doing today to solve this? If the
  answer is a five-tab copy-paste dance that takes 20 minutes, that's a
  real install-driver. If the answer is "nothing — that's why this is
  an opportunity," that usually means the pain isn't acute enough to
  motivate an install.
Stakes if we pick wrong: misreading status quo → misreading install
  motivation. A keyword with real volume but mild pain produces high
  bounce + low retention; behavioral factors collapse and ranking
  decays even after launch.
Recommendation: A or B (concrete workaround exists) — because a real
  workaround is install-driver evidence.
Completeness: A=9/10, B=9/10, C=8/10, D=4/10
Pros / cons:
A) A different Chrome extension exists but is broken / stale / paywalled / over-featured
  ✅ Direct competitor — softness and occupation scores will read clean
  ✅ Donor template likely available on GitHub (steal pattern, not code)
  ✅ Install path is a one-click swap from the existing tool
  ❌ Risk of optimization-second-mover trap (I14) if the rival is even halfway optimised
B) A web app / SaaS does it but requires a tab switch
  ✅ The SaaS proves demand and pricing — your CWS-native version is the wedge
  ✅ Tab-switch friction is a real install-driver — extensions win on context locality
  ❌ The SaaS might launch their own CWS extension as soon as they notice the gap
C) A manual workflow / shortcut combo
  ✅ Pain is real and ongoing — the operator pays the cost weekly
  ✅ No competitor to displace; first-mover advantage on the keyword
  ❌ Manual workflows are sticky; users may not bother installing even a free fix
D) Nothing — there's no current solution
  ❌ If truly no one is doing anything, the problem isn't painful enough
  ❌ Forces re-running 1.1 — we need a real status quo or the demand is hypothetical
  ✅ One acceptable edge case: the workflow is so new (a 2025 Chrome feature) that nothing exists yet — but name it
Net: A/B/C are all install-driver evidence; D forces a return to 1.1
  unless the user names a fresh-Chrome-feature edge case.
```

### Refusal: D answered

If the user picks D and can't name a fresh-Chrome-feature edge case,
loop back to 1.1. Cite gstack's rule: "if truly nothing exists and no
one is doing anything, the problem probably isn't painful enough." Do
not score.

### D4 output

Write a 2-3 sentence status-quo summary into `./.cws/01-idea.md` as
`## Status quo`. Cite the specific workaround. Cite the cost (time per
week, dollars per month, tabs open). Do not editorialise — the user's
words beat the founder's pitch.

## 1.3 — Desperate specificity (D5)

Third forcing question, adapted from gstack's Q3: "name the actual
person who'd install this."

The CWS adaptation: every install starts with one human typing the
keyword into Google or the CWS search bar. The model needs to know
*which human* so the listing copy in `cws-package` and the ads in
`cws-promote` can be written for one head — not for a category.

Category-level answers are refused. "Developers" is a filter, not a
user. "Marketing teams" is a filter. "Students" is a filter. The
correct answer names: a job/role, a specific moment in the day, and the
trigger that makes them install (not the trigger that makes them search
— the trigger that makes them click Install after they see the listing).

```
D5 — Name the actual person who'd install this
Project/branch/task: $SLUG @ $_BRANCH, naming the target user
ELI10: Every install starts with one human seeing your listing and
  clicking Install. The listing copy and the screenshots get written
  for ONE head, not a category. So we need: their job, the moment in
  their day when they'd type the search, and what about the listing
  would convince them to install vs. bouncing back to the SERP.
Stakes if we pick wrong: listing copy written for "marketing teams" is
  copy nobody reads. Behavioral factors collapse on install CTR.
Recommendation: A (you are the user — operator-as-user is the strongest
  validation any studio gets).
Completeness: A=10/10, B=8/10, C=7/10
Pros / cons:
A) I'm the user — describe my own role + the install moment
  ✅ Highest-fidelity description — you've felt the friction yourself
  ✅ Listing copy can be written from your own words in 1.1 / 1.2 verbatim
  ❌ Risk that your specific workflow doesn't generalise — but the SERP volume tells us if it does
B) A specific named human in my life — friend / colleague / family
  ✅ Externally-derived; not a hypothetical persona
  ✅ Phone-call away for listing-copy validation
  ❌ Second-hand description — easy to mis-state the install trigger
C) A specific named role at a specific named company — "<title> at <company>"
  ✅ Named role + named company is concrete enough to write copy for
  ❌ Riskiest of the three — you're describing without observation
  ❌ Often a fabricated persona dressed up as a real one — push hard
Net: A is strongest, B is acceptable, C is borderline — refuse if the
  named role/company isn't backed by an actual conversation.
```

### Forcing rule on D5

Push the user past category-level. If they say "developers" → "which
developer, doing what?" If they say "marketing teams" → "name the role.
Coordinator? Manager? Owner of what KPI?" If they say "students" →
"which level, doing which subject, on what device?"

Don't accept "users" as an answer. Ever.

### D5 output

Write into `./.cws/01-idea.md` as `## Target user (one human)`:

- Role / job
- Specific moment in the day when they'd type the search
- Listing-copy hook — the one phrase that would make them install
- (optional) Named human if B/C

## 1.4 — Narrowest wedge (D6)

Fourth forcing question, adapted from gstack's Q4: "what's the smallest
extension that delivers value?"

In CWS terms: the MVP must do ONE thing visible in ≤3 seconds of first
install. One button click. One keyboard shortcut. One address-bar
rewrite. One context-menu item. One side-panel widget. No login wall.
No onboarding wizard. No "settings page" required to get the first
value.

The wedge sub-phase ALSO covers donor selection. Forking an existing
open-source extension that does ONE related thing well — re-skinning
the listing copy to match the new keyword — is the fastest path from
wedge to shipped MVP. The narrowest wedge usually IS the donor's
existing one-function: pick the donor, the wedge picks itself.

### Donor discovery

For the chosen wedge, search GitHub for 2-3 candidate donors:

```
WebSearch: "<one-function> chrome extension github topic:chrome-extension"
WebSearch: "<one-function> manifest_version 3 github"
```

Filter results by:

- Repo has a working extension link (Chrome Web Store URL or a release
  with a `.crx` or `.zip` artifact)
- Last commit < 12 months old (stale donors are a red flag — Chrome's
  Manifest V3 has shifted enough that a 2-year-stale donor often
  doesn't build)
- `manifest.json` has `"manifest_version": 3` (I15 — V2 is delisting)
- Permissive license (MIT, Apache, BSD; GPL only if user is fine with
  open-source obligations on their fork)
- Front-end-only (no backend, no auth, no login form — anything that
  requires a server widens the MVP to a Stage 5 monetize problem)

```
D6 — Pick the narrowest wedge + donor
Project/branch/task: $SLUG @ $_BRANCH, picking the wedge + donor
ELI10: We have your observation, status quo, and target user. Now: the
  smallest possible extension that delivers the value on first install.
  One click, one shortcut, one context-menu item. The wedge IS the
  MVP — anything bigger gets cut to Stage 2b later. The donor is the
  open-source repo we'll fork (or steal patterns from). Picking a clean
  donor saves 2-5 days in cws-build.
Stakes if we pick wrong: a wide wedge → MVP slips by weeks; a stale
  donor → 2-5 days rewriting Manifest V3 incompatibilities; a paywalled
  donor → license dispute mid-build.
Recommendation: A (named donor, MIT/Apache, <12mo commit, V3) — because
  donor freshness is the single largest variable in build time.
Completeness: A=9/10, B=8/10, C=7/10
Pros / cons:
A) <donor-1 URL> — <license>, last commit <date>, V3
  ✅ <commit recency, license clean, working extension link in README>
  ✅ <front-end-only, no backend, no login wall>
  ❌ <one honest weakness — maybe a missing feature or a forked-from-V2 file>
B) <donor-2 URL> — <license>, last commit <date>, V3
  ✅ <its strength>
  ❌ <its weakness — usually stale or license mismatch>
C) <donor-3 URL> — <license>, last commit <date>
  ✅ <its strength>
  ❌ <its weakness>
Net: A is the cleanest fork; B and C are fallbacks if A's license or
  fingerprint breaks during cws-build.
```

### Refusal cases

- Wedge is "we'll ship the platform first, then narrow later" → I3 +
  Q4 push. Refuse. The wedge IS the MVP.
- Donor is Manifest V2-only AND user is non-dev → I15. Refuse this
  donor; loop back to find a V3 candidate.
- Donor has a GPL license AND user plans closed-source paid tier →
  surface the license conflict, ask if user wants to swap donors or
  accept the GPL obligation.
- No donor exists AND the function is non-trivial (>500 LOC) → flag
  in confidence flags, downgrade simplicity score later, but proceed
  if the user is a dev.

### D6 output

Write into `./.cws/01-idea.md` as `## Narrowest wedge` (the one-function
description) and `## Donor` (the chosen repo URL + license + last
commit date).

## 1.5 — Alternatives generation (D7, MANDATORY)

Adapted from gstack's Phase 4. **Not optional.** Even when the user's
observation feels obvious, generating three distinct hypotheses for the
same demand surfaces the framing that ranks best — which is usually not
the first framing the user proposed.

Three hypotheses. All three describe the SAME demand the user observed
in 1.1, but each frames it differently:

- **Hypothesis A — "obvious" framing.** The literal version of the
  user's observation. If the user said "I keep searching for `pdf
  split pages`," A's name keyword is `pdf split pages` (or its
  closest US-exact variant from Semrush).
- **Hypothesis B — different word-form / semantic angle on the same
  demand.** Rewording, related query, adjacent verb. The same install
  intent, a different SERP. If A is `pdf split pages`, B might be
  `split pdf` (verb-first), `pdf splitter` (noun), or `extract pdf
  pages` (different verb). Same job, different keyword cluster.
- **Hypothesis C — creative / lateral framing of the underlying job.**
  Different framing of the SAME problem. Three shapes that usually
  work:
  - **Invert the workflow direction.** X-to-Y → Y-to-X. (Hex
    color picker → hex code lookup; PDF-to-image → image-to-PDF.)
  - **Reduce friction on the platform's own primitive.** Chrome's
    address bar, right-click menu, new-tab page, side panel,
    downloads panel. If the user's observation is a "tool" problem,
    can a Chrome primitive rewrite be the same fix?
  - **Solve with a different Chrome surface.** Popup vs context
    menu vs side panel vs new tab. The donor changes; the install
    intent doesn't.

### Generation procedure

For each hypothesis, the model produces:

- Name keyword candidate (one-liner)
- One-function summary (≤2 sentences, what the extension *does*)
- Donor candidate (GitHub URL, license, last commit)
- Rough US-exact volume estimate (one Semrush `phrase_this` per
  candidate, three calls total)
- Why this might win (one sentence)
- Why this might lose (one sentence)

Semrush calls in parallel where the MCP supports it; sequential
otherwise:

```
execute_report(report="phrase_this",
  params={"phrase": "<kw-A>", "database": "us",
          "export_columns": ["Ph","Nq","Cp","Co","Nr","Kd","Td"]})
execute_report(report="phrase_this",
  params={"phrase": "<kw-B>", "database": "us",
          "export_columns": ["Ph","Nq","Cp","Co","Nr","Kd","Td"]})
execute_report(report="phrase_this",
  params={"phrase": "<kw-C>", "database": "us",
          "export_columns": ["Ph","Nq","Cp","Co","Nr","Kd","Td"]})
```

If any keyword returns Nq < 200, mark it "below-floor-pre-scoring" but
DO NOT drop it from D7 yet — the user might pick it for a different
reason (donor availability, narrower competition). The floor check
happens in 1.7 scoring.

### D7 emit

```
D7 — Pick a hypothesis to take into scoring
Project/branch/task: $SLUG @ $_BRANCH, three hypotheses on the same demand
ELI10: Same demand you observed in 1.1, three different framings. A is
  the obvious one (what you literally said). B is a different
  word-form for the same install intent (rewording the search). C is a
  lateral angle — different surface, different verb, sometimes
  different Chrome primitive entirely. Same job in all three. We pick
  one, score it, and only that one goes to Stage 2.
Stakes if we pick wrong: scoring the wrong framing → red-zone KD or
  occupied head on a keyword that has a softer sibling we ignored.
Recommendation: <pick by volume × softness × occupation × build
  complexity heuristic — usually A unless A is occupied>.
Completeness: A=9/10, B=9/10, C=8/10
Pros / cons:
A) <kw-A> — <one-function summary>, donor: <url>
  ✅ Closest to your observed query — install intent is highest-confidence
  ✅ US-exact volume <Nq-A> / Semrush KD <Kd-A>%
  ❌ <one honest ❌ — usually "the obvious framing is also the most-occupied">
B) <kw-B> — <different word-form>, donor: <url>
  ✅ Different word-form on the same install intent — sibling SERP
  ✅ US-exact volume <Nq-B> / Semrush KD <Kd-B>%
  ❌ <one honest ❌ — usually word-form ambiguity or volume drop>
C) <kw-C> — <lateral framing>, donor: <url>
  ✅ Lateral angle — different SERP, different competitor pool, often softer
  ✅ <a creative reason — Chrome primitive, inverted workflow, different surface>
  ❌ Most speculative of the three — install intent is one step removed
Net: A wins on intent fidelity; B is the safe sibling; C is the
  long-shot that sometimes scores best.
```

The user picks A/B/C. The model's recommendation is informed by the
scoring heuristic but the USER picks the final hypothesis. If the user
has no preference, follow the recommendation.

### D7 output

Write the chosen hypothesis into `./.cws/01-idea.md` under `## Chosen
hypothesis` (placeholder; final scoring will fill the table in 1.7).
Record the two un-chosen hypotheses under `## Alternatives considered`
with their one-function summaries and donor URLs — they're sibling
candidates for the next sprint if this one's scoring kills.

## 1.6 — Premise challenge (D8)

Adapted from gstack's Phase 3. Three premise checks before scoring.
The job is to catch the framing failures that scoring won't catch — a
keyword can score 36/50 and still be wrong-product-shape.

The three checks:

1. **Is "Chrome extension" the right format?** Could a Google Workspace
   add-on, a stand-alone web app, a desktop tool, or a mobile app serve
   this demand better? Sometimes the answer is yes — and the right
   move is to log the trade-off and proceed with the CWS launch anyway
   (CWS is what this skill ships). But the trade-off must be named, not
   suppressed.

2. **What happens if we do nothing?** Pull the status-quo answer from
   1.2. Has the user lived with this workaround for >6 months without
   screaming? If yes, the pain is mild and BF (behavioral factors) will
   suffer post-launch. This isn't a hard refuse — but it's a
   confidence-flag.

3. **Cross-model second opinion (optional).** If `codex` is on the
   user's PATH, offer it. Cross-model is optional; if the user
   declines, mark "skipped" in the artifact. If codex runs, surface its
   read of the premise verbatim. See `/codex` skill from gstack for
   wiring; cws-idea does not invoke codex inline (out of scope here).

```
D8 — Premise check on the chosen hypothesis
Project/branch/task: $SLUG @ $_BRANCH, premise-checking <chosen-hypothesis>
ELI10: Before we sink scoring effort into one hypothesis, three sanity
  checks. Format: is "Chrome extension" really the right shape for
  this demand, or would a Workspace add-on / web app / mobile app
  serve it better? Pain: has the user lived with the status quo for
  too long for the install motivation to be real? Second opinion: want
  an independent AI to read the brief and challenge us?
Stakes if we pick wrong: skipping the premise check costs 6 months
  ranking work on a keyword whose user installs the wrong product.
Recommendation: A (run all three premise checks, proceed if all pass)
  because pre-scoring premise filtering catches the framing failures
  scoring can't.
Completeness: A=10/10, B=7/10, C=3/10
Pros / cons:
A) Run all three premise checks, proceed if all pass (recommended)
  ✅ Catches "wrong-product-shape" failures that scoring misses
  ✅ Cheap — 60 seconds of model reasoning + 2-5 min for optional codex
  ❌ Adds friction; user has to engage with three checks they may find obvious
B) Run checks 1 + 2, skip cross-model second opinion
  ✅ Saves 2-5 min if codex isn't available or you don't trust it
  ✅ The two structural checks (format + pain duration) are the high-leverage ones
  ❌ Skips the only sanity check that can catch a blindspot in YOUR reasoning
C) Skip all premise checks — go straight to scoring
  ❌ This is exactly the failure mode the premise gate exists to prevent
  ❌ If the format is wrong, scoring will still produce a clean table — and the launch will fail
  ✅ Saves 5 minutes — acceptable only if user has already shipped 3+ CWS extensions
Net: A unless user is shipping their 4th-plus extension and has earned
  the right to skip premise checks.
```

### Premise check outputs

Write into `./.cws/01-idea.md` as `## Premise check`:

- **Format alternatives considered:** <Workspace add-on / web app /
  desktop / mobile — and why CWS still wins, or doesn't>
- **Pain duration:** <how long the user has lived with the status quo;
  if >6 months, flag>
- **Cross-model second opinion:** <verbatim codex output, or "skipped">

If any check fails hard (format is obviously wrong, pain is obviously
mild), loop back to 1.5 and pick a different hypothesis (B or C from
D7). Cap the loop at 2 cycles — after the second, surface as confusion
protocol D-brief and route to user for a call.

## 1.7 — Scoring + winner

Only the hypothesis chosen in D7 (and survived 1.6) gets scored. One
scoring pass — not five, not ten. If the score kills, loop back to 1.5
and pick the next candidate (B or C); the unused hypotheses from D7
become the sibling pool for that loop.

### Scoring procedure

The chosen hypothesis already has a name-keyword candidate from 1.5 and
a `phrase_this` row from D7's bulk generation. Now run the SERP fetch
and the related-tail check to fill in softness + occupation + adjacent
volume:

**Step A — SERP top-10 fetch (softness + occupation):**

```
execute_report(report="phrase_organic",
  params={"phrase": "<chosen-kw>", "database": "us",
          "export_columns": ["Dn","Ur","Po"]})
```

For each of the top 10 SERP results:
- **Software?** Domain is `chromewebstore.google.com`, `addons.mozilla.org`,
  a known SaaS, or a product page on a software-vendor domain.
- **Occupied?** If a CWS rival appears in top 3 AND the rival passes the
  three-factor optimization rule (name overlap on the head + description
  > 3K chars + > 30 translations — see I7), the keyword is occupied.

Softness = software count / 10. Soft if > 50%. Occupied if any top-3
CWS rival passes the three-factor rule.

**Step B — Tail variant check (only if Step A's softness is borderline 45-55%):**

```
execute_report(report="phrase_fullsearch",
  params={"phrase": "<chosen-kw>", "database": "us",
          "export_columns": ["Ph","Nq","Kd"]})
```

Look for `-er` / `-tool` suffix variants whose SERP is harder-software.
If a variant exists with same intent and softer SERP, surface it as a
late D-brief — the user may want to swap to the variant.

### Scoring rubric

See `references/scoring-rubric.md`. Columns:

| Column | Source | Range |
|---|---|---|
| **Hypothesis (label)** | A / B / C from D7 | text |
| **Name keyword** | the chosen head | text |
| **Users** | donor user count (0–10 relative, exclude brand-giants) | 0–10 |
| **Revenue** | `users/10` (one-time) + `(users/100)*$3` (IAP) heuristic; boost if paid sub | 0–10 |
| **Simplicity** | implementation simplicity vs likely alternates; boost if open-source prior art clean | 0–10 |
| **Volume** | US-exact `Nq` from `phrase_this`; relative to D7 sibling row | 0–10 |
| **KD (zone)** | fixed-tier from KD %: 0–49→10, 50–69→7, 70–84→6, 85–100→5 | 5/6/7/10 |
| **Soft?** | YES/NO gate from `phrase_organic` SERP top-10 software count | YES/NO |
| **Keyword free?** | YES/NO gate from `phrase_organic` SERP scan for optimized CWS rivals | YES/NO |
| **Total** | sum of 5 numeric columns (Users + Revenue + Simplicity + Volume + KD) | 0–50 |
| **Verdict** | `PASS` / `DROP — <reason>` | label |

### Hard thresholds (from the rubric, inlined for reference)

- **One-function gate (I3):** idea must collapse to one feature. Multi-
  feature → DROP and re-emit D6 (re-narrow the wedge).
- **Volume gate (I5):** US-exact ≥ 2,000 broad / ≥ 500 narrow. Below →
  DROP and loop to 1.5 (pick sibling from D7).
- **Softness gate (I6):** > 50% software in SERP top-10. Below → DROP
  keyword and loop to 1.5.
- **Occupation gate (I7):** no well-optimized rival on the head per
  three-factor rule. If owned → DROP keyword and loop to 1.5.

### KD zone reference

| KD % | Semrush zone | Points |
|------|--------------|--------|
| 0–49 | green / yellow | 10 |
| 50–69 | orange | 7 |
| 70–84 | red | 6 |
| 85–100 | scarlet (very hard) | 5 |

Read I18: KD comparison only between names of equal word count. Note
word count in the row if it varies.

### Confidence flags

For the scored row, note a confidence flag if:

- Semrush returned no data on the head keyword
- SERP had ambiguous software/non-software split (e.g. 45–55%)
- Donor monetization couldn't be verified (no public pricing page)
- Tier-1 traffic share unverified (worldwide-only volume returned)
- Premise check (1.6) flagged format alternatives as a real consideration
- D7 alternatives B and C were not Semrush-checked (rare; only if MCP
  failed mid-pipeline)

Flag readers: cws-challenge picks up these in its stress-test.

### D9 — Confirm the winner (only if a hard refuse fires)

If scoring PASSES all four hard gates, write the artifact silently and
route to cws-challenge. No D-brief required — the user already picked
the hypothesis in D7 and confirmed in D8; re-asking is friction.

If scoring fails ONE hard gate AND a sibling from D7 is plausible, emit
D9:

```
D9 — Chosen hypothesis failed scoring — pick a sibling or restart
Project/branch/task: $SLUG @ $_BRANCH, scoring failure on <chosen-kw>
ELI10: Your D7 pick failed the <gate name> gate. The hypothesis can't
  ship on that keyword. We have two un-scored siblings from D7 (B and
  C), or we can loop back to 1.1 and observe again.
Stakes if we pick wrong: shipping on a failed-gate keyword burns 6
  months of ranking work. Looping to 1.1 costs ~10 min if the first
  observation was thin.
Recommendation: <A or B per the heuristic — pick the sibling that's
  furthest from the failed gate>.
Completeness: A=9/10, B=9/10, C=6/10
Pros / cons:
A) Score sibling B from D7 — <kw-B>, <one-function summary>
  ✅ Already screened — donor + volume already known from D7
  ✅ Same observation; install intent identical
  ❌ B was the "different word-form" — risk it's a near-duplicate SERP that fails the same gate
B) Score sibling C from D7 — <kw-C>, <lateral framing>
  ✅ Lateral angle — different SERP, often softer
  ✅ Different donor; sometimes a cleaner build path
  ❌ Install intent one step removed from the observation; harder copy
C) Loop back to 1.1 and re-observe
  ✅ Honest reset if the demand was thin in the first place
  ❌ Most expensive option (~30-60 min)
  ❌ Burns the work in 1.1-1.6 if the observation was actually fine
Net: try the closer sibling (A) first; C is the fallback after both
  siblings fail.
```

After D9, score the chosen sibling using the same Step A–B procedure.
Cap the sibling loop at 2 cycles (B then C). After both siblings fail,
loop back to 1.1 — the demand was weaker than the user thought.

### Loop budget

- 1.5 → 1.6 → 1.7 → (fail) → 1.5: max 2 cycles per observation
- 1.5 → 1.6 → 1.7 → (fail all 3 siblings) → 1.1: max 1 reset per session

After the budget is exhausted, surface as confusion-protocol D-brief
and exit Phase 1. The studio loses nothing by stopping — the
observation will mature, the user will come back. The studio loses a
lot by shipping a scored-but-doomed keyword.

## 1.8 — Write the artifact

`./.cws/01-idea.md`:

```markdown
---
stage: cws-idea (Phase 1)
status: complete
created: <iso8601>
updated: <iso8601>
---

## Demand reality

<the observation captured in 1.1, verbatim from the user — do not
paraphrase. Include the path: A/B/C from D3.>

## Status quo

<2-3 sentences from 1.2 — the workaround, the cost, the cadence.>

## Target user (one human)

- **Role / job:** <one line>
- **Install moment:** <when in the day they'd type the search>
- **Listing hook:** <the one phrase that would make them install>
- **Named human (if B/C from D5):** <name + relationship>

## Narrowest wedge

<one-function description from 1.4 — what the extension does in ≤3
seconds of first install>

## Donor

- **URL:** <github URL>
- **License:** <MIT / Apache / BSD / GPL — flag if GPL with closed-source plan>
- **Last commit:** <ISO date>
- **Manifest version:** 3

## Alternatives considered (from D7)

- **A — <kw-A>:** <one-function summary>, donor: <url>, volume: <Nq>
- **B — <kw-B>:** <one-function summary>, donor: <url>, volume: <Nq>
- **C — <kw-C>:** <one-function summary>, donor: <url>, volume: <Nq>

(Chosen: <letter>)

## Premise check

- **Format alternatives considered:** <Workspace add-on / web app /
  desktop / mobile — and why CWS still wins, or doesn't>
- **Pain duration:** <how long the user has lived with the status quo>
- **Cross-model second opinion:** <verbatim codex output, or "skipped">

## Chosen hypothesis (scoring)

- **Name keyword:** <chosen keyword>
- **US-exact volume:** <Nq>
- **KD:** <%> (<zone>)
- **Softness verdict:** <YES — N/10 SERP results are software>
- **Occupation verdict:** <YES — no optimized rival on head, or NO —
  one rival at position N>
- **Donor URL:** <github URL>
- **Build complexity:** <low | medium | high>

## Scoring table

| Column | Value |
|---|---|
| Users | <0–10> |
| Revenue | <0–10> |
| Simplicity | <0–10> |
| Volume | <0–10> |
| KD (zone) | <%> (<zone> → <pts>) |
| Soft? | YES |
| Keyword free? | YES |
| **Total** | **<sum>/50** |
| Verdict | PASS |

## Why this keyword

<2-4 sentences. No hedging. Name the decisive criterion. Cite the
volume, the softness count, the donor URL. Tie it to a launch outcome:
"expected ranking position 3-5 within 6 weeks given KD zone yellow and
donor working out of the box.">

## Rejected siblings (if D9 fired)

- **<kw-X>:** DROP — <one-line reason: occupied / noisy / low volume /
  V2 donor>

## Confidence flags

- <any flag from 1.7 — e.g. "Semrush returned no data on long-tail tier",
  "donor monetization unverified — no public pricing page", "premise
  check flagged Workspace add-on as a real alternative">
```

### state.json delta

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p=pathlib.Path('./.cws/state.json'); d=json.loads(p.read_text())
d.setdefault('idea',{})
d['idea'].update({
  'name_keyword': '<chosen>',
  'us_volume_exact': <int>,
  'kd_pct': <int>,
  'kd_zone': '<green|yellow|orange|red|scarlet>',
  'softness': 'YES',
  'occupation': 'free',
  'donor_url': '<url or null>',
  'build_complexity': '<low|medium|high>',
  'rejected_siblings': [<list of dropped sibling keywords>],
  'observation_path': '<A|B|C from D3>',
  'premise_check': {'format_ok': True, 'pain_duration_ok': True, 'codex_ran': <bool>}
})
gp=d.setdefault('gates_passed',[]);
if 'idea' not in gp: gp.append('idea')
d.setdefault('history',[]).append({
  'ts': datetime.datetime.utcnow().isoformat()+'Z',
  'stage':'cws-idea','event':'gate_passed:idea',
  'keyword':'<chosen>'
})
d['last_updated']=datetime.datetime.utcnow().isoformat()+'Z'
p.write_text(json.dumps(d,indent=2))
PY
```

### Record losing hypotheses in learnings.jsonl

For every DROP in the scoring loop (D7 siblings that failed in D9, or
the original chosen hypothesis if a sibling won), append a learning so
the next sprint doesn't re-try it:

```bash
for kw in <list of rejected keywords>; do
  reason=<reason from scoring failure>
  echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"stage\":\"idea\",\"event\":\"keyword_rejected\",\"keyword\":\"$kw\",\"reason\":\"$reason\",\"slug\":\"$SLUG\"}" \
    >> "$CWS_PROJECT_DIR/learnings.jsonl"
done
```

The preamble surfaces these on the next cws-idea invocation, preventing
the same keyword from re-entering D7's sibling pool.

---


# Worked examples

Two end-to-end walkthroughs. These show how the phases compose in
practice. Use them as a reference for what the artifact looks like when
done well.

## Example 1 — Fresh project, RU operator, generic seed from `cws-init`

This example uses placeholder `<seed-keyword>` rather than a specific
niche, to avoid anchoring readers on a vertical (per I21). The shape
of the forcing-question loop is what matters; substitute the user's
own observation when the skill runs.

**Preamble echo:**

```
SLUG: <slug>
BRANCH: master
PROACTIVE: true
EXPLAIN_LEVEL: default
LEARNINGS: 0
CWS_STATE: present
GATES_PASSED: none
PROXY_VALIDATED: False
PROXY_RESIDENTIAL: None
DOLPHIN_PROFILE_ID: None
GOOGLE_ACCOUNT: None
```

**Phase 0** (compressed; see Phase 0 spec for the long form):

D1 → A (RU/BY/CIS). D2 → D (Proxy6 + `PROXY6_API_KEY` exported).
0.3 Flow A buys + imports a proxy. 0.4 gate passes (residential, ASN
clean, whoer 85% green, pixelscan consistent). 0.5 Dolphin profile +
Google account created via esimplus. `gates_passed += ["account-setup"]`.

**Phase 1:**

`01-idea.md` has `## Seed` from cws-init: "<one-line user note from
init — may or may not contain an observation>". The model checks: does
the seed already name a specific Google query, a specific friend's
complaint, or a specific under-optimised SERP slot? If yes, skip D3.
If no, emit D3.

1.1 — D3 emitted. User answers D (no observation yet). Model does NOT
fall through to a niche-brainstorm. Instead it surfaces the three
forcing prompts:

1. "What query did you Google in the last 30 days where the top
   extension result was useless?"
2. "What manual workflow do you do weekly that a 200-line extension
   could automate?"
3. "What Chrome built-in feature do you wish behaved differently?"

User picks #1 and names a specific query they typed last Tuesday where
the top result hadn't been updated in 3 years. Model re-emits D3 with
A pre-recommended. User confirms A. Observation written to `## Demand
reality`.

1.2 — D4 emitted. Status quo check. User describes their current
workaround: a 4-tab copy-paste flow taking ~15 minutes, weekly. Pain is
real. `## Status quo` written.

1.3 — D5 emitted. Specificity check. User picks A (self-as-user) and
describes the install moment: "after I close the third tab in the
copy-paste flow, that's when I'd Google the keyword." `## Target user`
written.

1.4 — D6 emitted. Narrowest wedge: one button on the active tab that
collapses the 4-tab flow to a single click. Donor discovery via
WebSearch surfaces 2 candidates:

- `github.com/<repo-1>` — MIT, V3, last commit 5 months ago
- `github.com/<repo-2>` — Apache, V3, last commit 14 months ago (stale flag)

User picks A (repo-1). `## Narrowest wedge` + `## Donor` written.

1.5 — D7 emitted. Three hypotheses on the same demand:

- **A — `<obvious-kw>`** (literal version of the user's query, Nq=4,400, KD=68)
- **B — `<word-form-variant>`** (different word-form for same install intent, Nq=2,100, KD=42)
- **C — `<lateral-angle>`** (Chrome-primitive rewrite of the same job, Nq=900, KD=15)

Recommended: A (closest to observed query). User picks B instead — KD
zone advantage outweighs volume in the user's read. Model accepts (the
user picks the final hypothesis; the recommendation is a guide).
`## Alternatives considered` written; chosen = B.

1.6 — D8 emitted. Premise checks:

- Format: CWS extension is the right shape (the friction is in the
  browser, not in a desktop app).
- Pain duration: user has lived with workaround for ~4 months — within
  the 6-month threshold, pain is acute.
- Cross-model: user declines codex second opinion. Logged as "skipped."

1.7 — Scoring on B. SERP fetch via `phrase_organic`:

- 7/10 top-10 results are software (CWS extensions or SaaS pages) →
  soft, YES.
- Top-3 CWS rival has 1.8K char description and 8 translations — fails
  the three-factor optimization rule → keyword free, YES.

Scoring table row:

| Column | Value |
|---|---|
| Users | 6 |
| Revenue | 5 |
| Simplicity | 8 |
| Volume | 6 |
| KD | 42 (yellow → 10) |
| Soft? | YES |
| Keyword free? | YES |
| **Total** | **35/50** |
| Verdict | PASS |

All four hard gates clear. No D9 fired. Artifact written. state.json:
`idea.name_keyword: "<word-form-variant>"`,
`idea.us_volume_exact: 2100`, `idea.kd_zone: "yellow"`,
`idea.donor_url: "https://github.com/<repo-1>"`.
`gates_passed: ["account-setup", "idea"]`.

No DROPs in this run (D9 didn't fire). The two un-chosen D7 hypotheses
(A and C) are NOT learnings — they're stored in `01-idea.md` under
`## Alternatives considered` as sibling candidates for the next sprint
(or for a cws-resync swap if B fails post-launch).

Routing footer:
`Next: /cws-challenge — stress-test <word-form-variant> for occupation
edge cases (word-form variants, plural/singular, near-synonym crowding).`

## Example 2 — Re-entry, prior Stage 0, D9 sibling-pick fires

This example demonstrates the failure path: D7 hypothesis fails
scoring, D9 fires, sibling B is scored and wins. Uses generic
`<observed-kw>` placeholders rather than a specific niche.

**Preamble echo:**

```
SLUG: <slug>
BRANCH: master
PROACTIVE: true
EXPLAIN_LEVEL: default
LEARNINGS: 4 entries loaded
[3 prior learnings printed]
CWS_STATE: present
GATES_PASSED: account-setup
PROXY_VALIDATED: True
PROXY_RESIDENTIAL: True
DOLPHIN_PROFILE_ID: 38
GOOGLE_ACCOUNT: <slug>2024@gmail.com
```

Preamble detects `account-setup` in `GATES_PASSED`. Phase 0 skipped.
Skill announces:

> Stage 0 already gated. Re-using proxy/profile/account from
> `./.cws/00-account-setup.md`. Advancing to Phase 1.

**Phase 1:**

`01-idea.md` does not exist. User's chat opener: "I keep searching for
`<observed-kw>` and the top result is a 2022 extension that doesn't
work on the new Chrome side panel."

This is a real operator observation — query + SERP gap noted. D3
defaults to C (SERP gap observation). User confirms C. `## Demand
reality` written.

1.2 — D4. User's status quo: they've been opening the broken extension
weekly, hitting the bug, then falling back to a 3-tab manual workflow
for ~2 months. Pain real. `## Status quo` written.

1.3 — D5. User picks A (self-as-user); names install moment + listing
hook. `## Target user` written.

1.4 — D6. Wedge: one side-panel widget that replaces the broken
extension's broken feature. Donor: `github.com/<repo>` (V3, MIT, last
commit 3 months). `## Narrowest wedge` + `## Donor` written.

1.5 — D7. Three hypotheses:

- **A — `<observed-kw>`** (literal observation, Nq=3,200, KD=72 red)
- **B — `<word-form-variant>`** (verb-first reword, Nq=1,400, KD=38 green)
- **C — `<lateral-angle>`** (side-panel framing of same job, Nq=600, KD=22 green)

Recommended: A (highest volume + same install intent). User picks A.

1.6 — D8. Premise checks pass. User accepts codex second opinion;
codex flags that A's keyword may be in transition (the 2022-stale
extension is the #1, but a new well-resourced rival appeared at #2 last
month). Codex output written verbatim into `## Premise check`.

1.7 — Scoring on A. SERP fetch: 8/10 software (soft, YES). But the new
#2 rival has 4.2K char description + 41 translations + exact-keyword
name → fails three-factor optimization rule → **keyword occupied, NO.**

Hard refuse: occupation gate failed. D9 emitted.

D9 recommends A (score sibling B from D7). User approves.

Re-score on B: SERP fetch shows 7/10 software, no optimized rival in
top 3 (the rivals that appeared on A are absent from B's SERP because
the word-form is different). Scoring table for B:

| Column | Value |
|---|---|
| Users | 5 |
| Revenue | 5 |
| Simplicity | 8 |
| Volume | 5 |
| KD | 38 (green → 10) |
| Soft? | YES |
| Keyword free? | YES |
| **Total** | **33/50** |
| Verdict | PASS |

Artifact written. state.json: `idea.name_keyword: "<word-form-variant>"`,
`rejected_siblings: ["<observed-kw>"]`. One learning written for the
dropped A keyword with reason "occupation — new rival at #2 with
optimized listing." `gates_passed: ["account-setup", "idea"]`.

Routing footer:
`Next: /cws-challenge — stress-test <word-form-variant> for
near-synonym occupation (the rival on A's SERP may surface in B's
sibling cluster).`

---

# Edge cases table

12 rows. Each row is a real situation that's bit the playbook; the action
column is the canonical response.

| Edge case | Action |
|---|---|
| Semrush MCP unavailable / down | Fall back to WebSearch + a single `keywordtool.io` SERP fetch for rough volume; flag every score as low-confidence; recommend pausing validation until Semrush is back. Never invent volume numbers. |
| Donor repo archived mid-validation | Re-run donor discovery; if no fresh donor, downgrade simplicity score to ≤4; consider fork-then-port if user is a dev. |
| Head keyword has trademark conflict (Spotify, Slack, etc.) | I12 applies. Modify the keyword (`hex color picker for Spotify` → `hex color picker for music players`) or drop the candidate. |
| Target country is OFAC-sanctioned (IR, KP, CU, SY) | Stage 0 still possible but legal risk falls on user; explicit one-line warning, route to user-challenge brief asking for confirmation before proceeding. |
| User demands a niche the playbook explicitly flagged dead (I10) | Surface the playbook flag with the saturation count; recommend a sibling niche; if user insists, proceed but document the override in the artifact's confidence-flags section. |
| Proxy validates green but Semrush returns "rate-limited" repeatedly | Likely a Semrush API quota issue, not a proxy issue. Pause, ask user to check their Semrush API plan, resume. |
| Two D7 hypotheses score within 3 points after Phase 1.7 | Apply playbook tie-breaker: fewer near-form CWS rivals (count via chromewebstore search) wins. If still tied, prefer the lower-KD candidate (narrow ranks faster). Do not emit a separate tie-break D-brief — the user already picked in D7. |
| User wants to validate two ideas in parallel | I16 applies. Decline, ask which one to validate first. The second one can run after the first ships. |
| User's seed keyword has zero US volume but normal volume in IN/PH | Per `idea-validation.md`: non-English-native query. Drop; can't rank Tier-1. Recommend pivoting to a Tier-1-native keyword. |
| Donor's license is GPL and user plans closed-source paid tier | Surface as D-brief: license-compatible donor (MIT/Apache) vs port-from-scratch. Default: find a different donor. |
| SERP top-10 is split exactly 50/50 software/non-software | Borderline softness — emit confusion-protocol D-brief. Don't silently call YES or NO. |
| User's Google account creation has failed 3 times | Pause Stage 0. Route to `/cws-dolphin diagnose`. Do not silently retry — the profile is burned. |

---

# Tools

- **Semrush MCP** — the workhorse for volume / SERP / KD research. See
  `references/semrush-playbook.md`. Default database `us`.
- **WebSearch / WebFetch** — browsing CWS, reading competitor store pages,
  GitHub donor discovery, license checks.
- **`cws-dolphin` CLI** — Stage 0 proxy + profile automation. `proxy6-buy`,
  `bulk-add-proxies`, `check-proxy`, `create`, `diagnose`, `proxy6-swap`.
- **`learnings.jsonl`** — read on preamble, write on Phase 1.5. Filters
  next-sprint candidate generation.

## Tools that don't help here

- Building anything (that's `cws-build`).
- Writing the listing copy (that's `cws-package`).
- Choosing the banner (that's `cws-launch`).
- Setting up paid ads (that's `cws-promote`).
- Picking the pricing tier (that's `cws-monetize`).

If the user asks for any of these inside cws-idea, defer with a one-liner
and route at the end via the Skill Routing footer.

---

# Gate to the next stage

Both Stage 0 and Stage 1 gates must show in `gates_passed` before any
other skill runs. Stage 1 gate exit criterion: a chosen hypothesis with
a name keyword that clears all four hard gates (one-function, volume,
softness, occupation).

Verify before exit:

```bash
/usr/bin/python3 - <<'PY'
import json, sys, pathlib
p = pathlib.Path('./.cws/state.json')
d = json.loads(p.read_text())
gp = set(d.get('gates_passed', []))
req = {'account-setup', 'idea'}
missing = req - gp
if missing:
    print("EXIT_BLOCKED: missing gates:", ",".join(missing))
    sys.exit(1)
idea = d.get('idea', {})
need_keys = ['name_keyword','us_volume_exact','kd_zone','donor_url']
missing_keys = [k for k in need_keys if k not in idea]
if missing_keys:
    print("EXIT_BLOCKED: idea fields incomplete:", ",".join(missing_keys))
    sys.exit(1)
print("EXIT_OK")
PY
```

If `EXIT_BLOCKED`, do not write the routing footer; instead surface
which field is missing and loop back to the relevant phase.

---

# Skill Routing Footer

Default routing — both gates passed, no carryover work:

```
Next: /cws-challenge
Why: Stress-test the chosen keyword for occupation edge cases, near-form
rivals (word-form variants, plural/singular, near-synonym crowding), and
SERP-form mismatches that the 10-step procedure may have missed. Cheaper
to find these now than after the build.
```

Alternative routing — user explicitly wants to skip the challenge and go
straight to listing copy:

```
Next: /cws-package
Why: Skipping challenge per user request. cws-package will start drafting
the listing copy from the chosen keyword. Note: any occupation edge case
will surface during package and force a return to cws-idea.
```

Never list both. The user can override by typing the other skill name.

Phase 0-only exit (account-setup gated, Phase 1 incomplete):

```
Next: /cws-idea
Why: Account setup gated. Re-enter cws-idea to run Phase 1 (idea
validation) — the same skill handles Stage 0 → Stage 1.
```
