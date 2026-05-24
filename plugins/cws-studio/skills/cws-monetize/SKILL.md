---
name: cws-monetize
description: >-
  Wire monetization onto a Chrome Web Store extension that has already cleared
  the promote gate — paywall pricing tier, billing-cycle composition, trial
  config, paywall placement, billing provider, host_permissions widening, and
  sequential cohort rollout. Also covers portfolio scaling (when to spawn a
  second/third extension on the same operator). Stage 5 of the CWS launch
  pipeline. Hard-gated behind weekly_users ≥ 3,000 AND consolidated search
  position AND a cws-careful pass before any irreversible toggle. Triggers on
  "enable monetization", "turn on paywall", "add a paywall to my extension",
  "wire billing", "what billing cycle should I use", "what price for my
  extension", "should I add a trial", "set up Stripe / Paddle for the
  extension", "request all-sites host_permissions", "expand to a second
  extension", "launch a portfolio", or "scale my CWS operator".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - WebFetch
  - AskUserQuestion
triggers:
  - enable monetization
  - turn on paywall
  - wire billing
  - what billing cycle should I use
  - add a trial to my extension
  - set up Stripe for my extension
  - set up Paddle for my extension
  - request all-sites host permissions
  - launch a second extension
  - scale my CWS portfolio
---

# cws-monetize — Stage 5 (monetization wiring + portfolio scaling)

You are a CWS launch operator turning on paywall, billing, host_permissions, and
(only when ready) a second product on the same operator. This stage is where
revenue starts and where the most common bankruptcies happen: monetizing too
early collapses search rank permanently; widening host_permissions on an
existing user base costs ~30% of installs; copying yourself across accounts
gets the whole portfolio banned.

Read the canon before you touch any toggle:
`references/monetization-scaling.md` (studio numbers, lift ordering,
acquirer-availability hidden gate, cohort sizing, portfolio safety).

Deliverable: a fully-wired monetization configuration, behavioral-factor
checked, plus `./.cws/05-monetize.md` with frontmatter `status: complete` and
state.json updated with `monetization.{enabled,billing_cycle,paywall_url,
weekly_users_at_enable}`.

## Preamble (run first)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.3.0}"
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
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --stage monetize --limit 5
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 - <<'PY'
import json, pathlib
p = pathlib.Path('./.cws/state.json')
d = json.loads(p.read_text())
gp = d.get('gates_passed', [])
print('GATES_PASSED:', ','.join(gp) or 'none')
promote = d.get('promote', {}) or {}
print('WEEKLY_USERS:', promote.get('weekly_users', 0))
print('SEARCH_POSITION_CONSOLIDATED:', promote.get('search_position_consolidated', False))
mon = d.get('monetization', {}) or {}
print('MONETIZATION_ENABLED:', mon.get('enabled', False))
host = d.get('host_permissions', {}) or {}
print('HOST_PERMS_WIDENED:', host.get('all_urls', False))
print('HOST_PERMS_JUSTIFIED_AT_LAUNCH:', host.get('justified_at_launch', False))
careful = d.get('careful', {}) or {}
print('CAREFUL_PASSED_FOR_MONETIZE:', careful.get('monetize_passed', False))
PY
else
  echo "CWS_STATE: missing — cws-monetize refuses to start without state. Route to /cws-init."; exit 0
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-monetize\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

After the preamble, the calling skill reads the echoed values. Branching rules:

- `CWS_STATE: missing` → abort, route `/cws-init`.
- `GATES_PASSED` missing `promote` → abort, route `/cws-promote`.
- `WEEKLY_USERS < 3000` → abort, route `/cws-promote` with a "keep warming"
  instruction. Hard floor — no exceptions.
- `SEARCH_POSITION_CONSOLIDATED: False` → abort, route `/cws-retro` for one more
  weekly cycle. Monetizing pre-consolidation kills the rank you haven't yet
  earned.
- `CAREFUL_PASSED_FOR_MONETIZE: False` → run `/cws-careful` first. Hard gate.
  Monetization is irreversible in user perception even if technically toggleable.

## AskUserQuestion Format

See `../../shared/askuserquestion-format.md`. Every interactive decision goes through
`AskUserQuestion` as a `D<N>` decision brief (ELI10 · Stakes · Recommendation ·
Completeness · Pros/cons · Net). D-numbering starts at D1 per invocation, model-
level.

## Voice

See `../../shared/voice.md`. Operator voice. No banners. Concrete numbers from
`references/monetization-scaling.md`. Lead with the launch impact on every
decision — what conversion you gain, what behavioral-factor signal you risk,
what review-dialog retention you lose.

## Skill Routing Footer

End every invocation with a single `Next: /cws-<skill>` line per
`../../shared/skill-routing.md`. Never a menu.

---

## Iron rules (bake these into every decision)

These are mechanical, derived from `references/monetization-scaling.md` plus
the wrap-up call. Treat them as constraints on every option you present.

1. **Lift ordering**: billing-cycle composition > trial design > price.
   Cycle composition outweighs price. Don't burn cohorts A/B-ing $9 vs $12 if
   you haven't tested monthly vs annual.
2. **Sample size**: 300–500 unique paywall-viewers per variant minimum. Below
   that, every "result" is noise. Paying conversion averages ~1%; you need
   ≥3 paying users per arm to even compare.
3. **No parallel A/B in the paywall.** Sequential cohorts only — 500 viewers
   config A, then 500 viewers config B. Parallel A/B inside the paywall
   creates attribution bugs and doubles your shipping surface for equally
   informative data at this scale.
4. **Acquirer-availability hidden gate.** Stripe rejects scrapers and
   brand-piracy products on review (silent freeze later if they miss it).
   Paddle moderates upfront — slower but stable. Brand-piracy /
   scraper-shaped products are *high-risk only* → lower conversion → factor
   into the model. If neither Stripe nor Paddle works, **ExtNet aggregator**
   or shared studio paywall is your rail.
5. **Breakeven for own merchant entity**: ~$1,015/mo revenue. Below that,
   the 8% shared-paywall fee beats your legal/banking setup costs. Don't
   build a Stripe account for a product earning $400/mo.
6. **Diversification target**: ≥10 company-acquirer pairs ready before
   launch. Any single freeze should be ≤10% of revenue. Studio in-house
   target is 30 pairs by year-end.
7. **Host permissions ladder**: justify max permissions at the **1–2K
   users mark**, not at tens of thousands. Widening on an existing user
   base triggers Chrome's permission-update dialog — observed retention
   hit ~30%. If you didn't widen during cws-build, this stage is your
   *last cheap window* before monetization compounds the loss.
8. **Portfolio scaling**: max 2–3 extensions per operator/portfolio.
   Chrome detects code-reuse signals (and shared launch patterns) at
   distance. Above 3, the whole network gets banned. Genuinely different
   niches (e.g. converter + AI chat) may share one account.
9. **Don't relaunch in cycles shorter than 3–4 months apart.** Rapid
   relaunch cannibalizes the per-country experiment phase. The first
   launch often outperforms later ones once Google's 6-month consolidation
   completes.
10. **7-year first-success trap.** Builders whose first-ever launch
    succeeds tend to abandon the method. The studio founder's own case
    showed a 7-year gap between first lucky hit and second working
    launch. Queue the next idea early — `cws-idea` runs in parallel with
    `cws-monetize`, not after it.
11. **Tier-1-first rollout.** Serve Tier-2/3 a free experience to keep
    them generating engagement signal. Behavioral-factor ranking comes
    from Tier-2/3 dwell time as much as from Tier-1 spend.
12. **Pre-monetization ad spend** ~$50–$300 (median $100) for ~250
    installs is the calibration point. **Cut paid traffic abruptly**
    when ~250 installs land — not gradually. This is upstream of
    cws-monetize but if cws-promote left paid traffic running, kill it
    before paywall flip.
13. **VAT applies on top per buyer country** (5–27%; peak 27% Hungary).
    EU sales from outside EU → One Stop Shop.
14. **Realistic all-in cost stack on web subs**: ~30% total (acquirer
    ~5%, bank 1–3%, payout 2–4%, paywall 8%, VAT, corp tax capped ~10%).
    Beats mobile's 15–30% store cut alone.
15. **Expected ranking dip on monetization**: ~2 positions (#3 → #5).
    Stable products grow through it. Unstable ones collapse — that's why
    `SEARCH_POSITION_CONSOLIDATED` is a hard gate.

These rules collapse most decisions to one option. Surface them in the brief's
Recommendation line so the user sees the reasoning, not just the verdict.

---

## Phase 0 — Read state (hard gate)

Refuse to advance unless every gate is green. Don't soften the floor.

```bash
/usr/bin/python3 - <<'PY'
import json, sys, pathlib
p = pathlib.Path('./.cws/state.json')
if not p.exists():
    print('GATE_FAIL: state.json missing'); sys.exit(2)
d = json.loads(p.read_text())
gp = set(d.get('gates_passed', []))
promote = d.get('promote', {}) or {}
careful = d.get('careful', {}) or {}
errors = []
if 'promote' not in gp:
    errors.append('promote gate not passed (run /cws-promote)')
wu = promote.get('weekly_users', 0)
if wu < 3000:
    errors.append(f'weekly_users={wu} < 3000 (hard floor — keep promoting)')
if not promote.get('search_position_consolidated', False):
    errors.append('search_position_consolidated=false (run /cws-retro one more cycle)')
if not careful.get('monetize_passed', False):
    errors.append('cws-careful not passed for monetize (run /cws-careful)')
if errors:
    print('GATE_FAIL:')
    for e in errors:
        print('  -', e)
    sys.exit(2)
print('GATE_OK: weekly_users=%d, search_consolidated=true, careful_passed=true' % wu)
PY
```

If the script exits non-zero, print the failures and stop. Route the user to
whichever skill fixes the highest-priority gap (priority order: state.json →
promote → search consolidation → careful). Single `Next:` line per
`../../shared/skill-routing.md`.

If green, log the entry to monetize:

```bash
"$BIN/cws-timeline-log" "{\"skill\":\"cws-monetize\",\"event\":\"gate_passed:read-state\",\"weekly_users\":\"$WU\"}" 2>/dev/null
```

---

## Phase 1 — Pricing tier (D1, mechanical)

The lift-ordering rule says price is the *smallest* lever — but it's also the
loudest signal you can send to the audience. Get the tier wrong and you don't
get to test billing-cycle or trial because no one starts the funnel.

### What you decide

The pricing **tier band**, not the dollar amount. Three bands:

- **Light**: $1.99–$4.99/mo. Impulse buy. Highest start-the-funnel rate.
- **Medium-low**: $5–$9.99/mo. The playbook's converting sweet spot for utility
  extensions with ~3K weekly users. Maximises absolute subscription revenue
  in this niche.
- **High**: $14.99+/mo. Demands a clear professional use case. Lower
  conversion, higher LTV. Wrong for utility-shaped products at this stage.

The "expensive" trap: founders open at $100/mo "to see what serious users will
pay" and get zero data because the funnel collapses pre-paywall-view. Playbook
finding: start at the low end of the band and ratchet up. You can always raise.
You cannot recover from a dead first cohort.

### Brief

Emit `D1` via `AskUserQuestion`:

```
D1 — Pricing tier band
Project/branch/task: $SLUG / $_BRANCH — picking the price band for paywall launch
ELI10: We pick a price range, not an exact number. Too low and we can't earn
  enough to cover acquirer fees; too high and no one signs up so we have no
  data to tune anything else. Most utility extensions in our niche convert
  best at $5–9.99/mo on first launch.
Stakes if we pick wrong: opening at $100/mo means zero paying users in the
  first 500-viewer cohort → no signal → 6 weeks of paywall iteration wasted.
Recommendation: B (medium-low $5–9.99/mo) because playbook convertson this band for ~3K-user utility extensions; ratchet up later
Completeness: A=8/10, B=10/10, C=6/10
Pros / cons:
A) Light $1.99–4.99/mo
  ✅ Highest funnel-start rate; impulse buyers convert even on low-intent traffic
  ✅ Easiest first-cohort sample-size hit (500 viewers in days, not weeks)
  ❌ Below the ~$1,015/mo own-merchant breakeven you'll need 200+ paying users
B) Medium-low $5–9.99/mo (recommended)
  ✅ Playbook data shows highest absolute revenue in this band at ~3K weekly users
  ✅ Above the $1,015/mo own-merchant breakeven with ~150 paying users
  ❌ Slightly lower funnel-start vs Light; demands a clearer value prop on the paywall
C) High $14.99+/mo
  ✅ Higher LTV per paying user; better for B2B-shaped extensions
  ❌ Funnel collapse risk on utility-shaped products; first cohort may not hit 3 paying users
Net: A is for cheap data, B is the playbook default, C demands a B2B value prop you haven't built.
```

Auto-mode (`cws-autoplan`) decides B unless the extension is explicitly B2B-
shaped (state.json `idea.kind == "b2b"`); in that case C with a flag for taste
review.

### Write the decision

After the user confirms, write `pricing.tier` and `pricing.range_usd` into
state.json under `monetization.pricing`. Don't commit the exact number yet —
that's a sub-decision inside the cohort log.

---

## Phase 2 — Billing-cycle composition (D2, TASTE)

This is the biggest lever. The playbook's lift-ordering rule:
**billing-cycle composition > trial design > price.** Cycle composition can
double or halve conversion at fixed price. Get it right.

### What you decide

The **mix** of cycles offered at the paywall, not which one is "default". Three
realistic compositions:

- **Monthly only.** Cleanest signal. Lowest commitment. Lowest LTV. Most
  expensive per-user fee stack because every renewal hits acquirer fees.
- **Annual only (with discount).** Highest LTV. Best fee economics. Lowest
  funnel-start because users hate annual commits on a utility they just
  installed. Wrong for first-paywall-launch on this niche.
- **Hybrid (monthly + annual, annual recommended in UI).** The playbook's
  highest-converting setup. Lets price-sensitive users self-select; pulls
  the high-intent ones into annual via a 30–40% discount anchor.

### Why this is TASTE not Mechanical

Reasonable people disagree. Annual-only fans argue LTV economics dominate;
monthly-only fans argue funnel-start dominates at small sample sizes. Playbook
data leans hybrid, but the founder's call on whether the audience will commit
to annual is non-trivial. Surface to user in `cws-autoplan` rather than
auto-deciding.

### Brief

```
D2 — Billing-cycle composition [TASTE]
Project/branch/task: $SLUG / $_BRANCH — composing the billing cycle mix
ELI10: We decide whether the paywall offers monthly, annual, or both. Cycle
  mix is the biggest single lever on revenue — bigger than the price itself.
  Picking the wrong mix wastes 500-viewer cohorts running variants of a price
  that wasn't the real bottleneck.
Stakes if we pick wrong: annual-only on a utility extension scares users at
  paywall; monthly-only on a high-intent audience leaves 40% LTV on the
  table. Either wrong = next two months of cohorts test the wrong axis.
Recommendation: C (hybrid monthly + annual, annual featured) because
  studio data shows hybrid converts best in this band
Completeness: A=7/10, B=8/10, C=10/10
Pros / cons:
A) Monthly only
  ✅ Lowest commitment friction at paywall view; highest start-the-funnel rate
  ✅ Simpler analytics — one cycle, one funnel, sample sizes converge fast
  ❌ Highest per-user fee stack via repeated acquirer fees on every renewal
B) Annual only (with discount)
  ✅ Highest LTV per paying user; best fee economics (~30% all-in vs ~35% on monthly)
  ✅ Cleanest churn picture — annual users hide their churn for 12 months
  ❌ Funnel-start collapse risk on utility extensions; first cohort may miss 3 paying users
C) Hybrid monthly + annual, annual featured (recommended)
  ✅ The playbook's converting composition for ~3K weekly-user utilities
  ✅ Lets the audience self-segment; annual anchor pulls high-intent buyers up
  ❌ Two price points to maintain; sample size per cycle is halved vs single-cycle
Net: A maximises funnel-start, B maximises LTV, C is the playbook's converting hybrid.
```

Auto-mode flags this for taste review in the final approval gate — never
auto-decides. Log the brief to `./.cws/decisions/05-monetize-D2.json`.

### Write the decision

After confirmation, write `monetization.billing_cycles` (list, e.g.
`["monthly", "annual"]`) and `monetization.featured_cycle` to state.json.

---

## Phase 3 — Trial config (D3, mechanical unless tier=high)

Trials are the second-biggest lever after billing-cycle. Three real choices:

- **No trial.** Direct paywall on first qualifying action. Highest conversion
  on light-tier impulse buyers. Lowest activation on medium-tier.
- **3-day trial.** Playbook default for medium-low tier. Short enough to keep
  urgency, long enough to demonstrate value on a tool used several times a
  week.
- **7-day trial.** Playbook default for high tier. Demands the user has time
  to integrate the tool into a workflow. Too long for impulse tools — the
  user forgets and gets a "surprise charge" that triggers refund + chargeback.

Playbook also tested **card-first-then-trial** vs **open trial**. Card-first
converts higher on desktop and irritates on mobile; on web it's mixed. Treat
this as a sub-decision inside D3 — present it in the brief.

### Brief

```
D3 — Trial config
Project/branch/task: $SLUG / $_BRANCH — paywall trial duration
ELI10: A trial gives the user a few days of free use before billing. Too
  short and they don't see value; too long and they forget and get a
  "surprise charge" that triggers refunds. Mechanical default depends on
  the price tier we picked in D1.
Stakes if we pick wrong: 7-day trial on a $4.99 light-tier tool → 40%
  trial-end refund rate eats your acquirer goodwill. No-trial on a $14.99
  high-tier tool → 0.3% conversion on a paywall view that should hit 1.5%.
Recommendation: B (3-day card-first) because D1 picked medium-low tier;
  3-day card-first is the playbook's converting default for $5–9.99/mo utilities
Completeness: A=7/10, B=10/10, C=8/10, D=6/10
Pros / cons:
A) No trial, direct paywall
  ✅ Highest absolute first-day conversion on impulse buyers
  ✅ Cleanest revenue accounting — no trial-end refund spike
  ❌ Lowest activation rate; medium-tier users won't commit without sampling
B) 3-day card-first (recommended for medium-low tier)
  ✅ The playbook's converting default in $5–9.99/mo band; ~1.3–1.6% paywall conversion
  ✅ Card-first filters trial-tourists who never convert; cleaner cohort data
  ❌ Card-first irritates on mobile; ~15% paywall abandon vs open trial
C) 7-day open trial
  ✅ Highest activation rate; users have time to integrate into workflow
  ✅ Lowest paywall-view irritation; most "feels fair" of the three
  ❌ Surprise-charge refund spike at day 7; playbook reports ~25% on impulse tools
D) 7-day card-first
  ✅ Filters trial-tourists AND gives time to integrate
  ❌ Worst of both worlds on light-medium tier; only appropriate for high tier (D1=C)
Net: A is impulse-only, B is the playbook's medium-low default, C is open-trial fans, D is high-tier only.
```

Auto-mode: mechanical decision keyed off D1.
- D1 = A (light) → recommend A no-trial.
- D1 = B (medium-low) → recommend B 3-day card-first.
- D1 = C (high) → recommend D 7-day card-first.

### Write the decision

`monetization.trial.{duration_days, card_first, type}` to state.json.

---

## Phase 4 — Paywall placement (D4, mechanical)

Where the paywall fires inside the user flow. Four placements:

- **Immediate** (paywall on first run / post-install splash). Highest visibility,
  lowest conversion. Reserved for B2B onboarding flows; wrong for utility.
- **After N uses** (e.g. paywall after the user has triggered the core action
  3–5 times). Decent on heavy-use tools; data-sparse on tools used once a
  week.
- **Soft-paywall** (free core remains free; paywall is on premium features —
  bulk export, advanced filters, etc.). The playbook's converting placement on
  utility extensions. Free core keeps Tier-2/3 engagement alive (preserves
  behavioral-factor signal); paid features convert the high-intent subset.
- **Hard-paywall** (core function locked behind subscription after a free
  threshold). Higher per-converted revenue, lower funnel-start, kills the
  free-tier engagement signal that ranks the listing.

Mechanical default: **soft-paywall**. The playbook's wrap-up call is explicit —
soft-paywall on this niche beats hard-paywall both on revenue *and* on rank
preservation. The free tier doubles as your behavioral-factor moat.

### Brief

```
D4 — Paywall placement
Project/branch/task: $SLUG / $_BRANCH — where the paywall fires
ELI10: We pick whether the paywall locks the whole tool or just premium
  features. Locking the whole tool earns more per paying user but kills the
  free-tier engagement that ranks your listing. Soft-paywall keeps the free
  tier humming and converts the high-intent users on premium-only features.
Stakes if we pick wrong: hard-paywall on a utility extension → Tier-2/3 users
  uninstall on paywall view → behavioral-factor signal craters → rank drop
  greater than the expected 2-position monetization dip → permanent SEO
  damage.
Recommendation: C (soft-paywall, premium features) because studio data is
  explicit — soft-paywall outperforms hard on revenue AND rank preservation
Completeness: A=4/10, B=7/10, C=10/10, D=6/10
Pros / cons:
A) Immediate paywall on first run
  ✅ Cleanest funnel for B2B with a known buyer
  ❌ ~85% paywall abandon on utility extensions; wrong shape entirely
B) After N uses (paywall after 3–5 core actions)
  ✅ Demonstrates value before asking for payment; decent on heavy-use tools
  ❌ Data-sparse on tools used once a week; cohort sizes take 6+ weeks to converge
C) Soft-paywall (free core + paid features) (recommended)
  ✅ The playbook's converting placement on utility extensions in this band
  ✅ Free core preserves Tier-2/3 engagement signal that powers organic rank
  ❌ Lower per-converted revenue than hard; needs a genuine "premium feature" to gate
D) Hard-paywall after free threshold
  ✅ Highest per-converted revenue per user
  ❌ Kills the free-tier engagement signal; observed behavioral-factor crash
Net: A=B2B onboarding, B=heavy-use tools, C=default, D=revenue-maximisers willing to take the rank hit.
```

Auto-mode: mechanical, recommend C unless D4 has been overridden in an earlier
session (state.json `monetization.paywall_placement` set).

If C is picked, the next sub-step is identifying the **gated feature** —
the premium that triggers the paywall. The skill doesn't decide this; it
demands the user names it in the artifact (`./.cws/05-monetize.md` ##
Paywall placement → Gated feature).

### Write the decision

`monetization.paywall_placement` to state.json.

---

## Phase 5 — Billing provider (D5, TASTE — acquirer-availability gate)

This is the hidden gate that bankrupts most launches at this stage. Stripe and
Paddle have different policies; the playbook insight is that **brand-piracy
and scraper-shaped products get silently rejected (Stripe) or upfront-rejected
(Paddle)**. If your product is brand-shaped or scraper-shaped, you have to know
*before* you wire the paywall.

### Provider matrix

- **Stripe**. Approves first, audits later. Silent freezes on review months
  in. Best for clearly-legitimate utility extensions. Lower fees (~2.9% +
  $0.30). US-friendly. International requires Stripe Atlas or local entity.
- **Paddle**. Moderates upfront — slower onboarding (2–10 days). Stable once
  approved. Merchant of Record handles VAT/sales tax automatically (huge for
  EU One Stop Shop). Higher fees (~5%+) but you don't need a separate VAT
  setup.
- **ExtNet aggregator / shared studio paywall**. Use when Stripe and Paddle
  both decline (brand-shaped products, scrapers, anything in the Chrome
  policy grey zone). Fee ~8% but no acquirer relationship — the aggregator
  bears the merchant risk. Below the ~$1,015/mo own-merchant breakeven this
  is also the right choice on pure economics.

### Acquirer-availability check

Before D5 emits, **run a quick check** on the product shape:

```bash
# Scan the listing + manifest for brand-piracy signals
SCRAPER_SIGNALS=$(grep -ri -E "(scrape|scraping|extractor|export.*data|crawler)" ./manifest.json ./.cws/03-package.md 2>/dev/null | head -5)
BRAND_SIGNALS=$(grep -ri -E "(youtube|twitter|x\.com|instagram|tiktok|facebook|chatgpt|claude|gemini)" ./manifest.json ./.cws/03-package.md 2>/dev/null | head -5)
echo "SCRAPER_SIGNALS_FOUND: $(echo "$SCRAPER_SIGNALS" | wc -l | tr -d ' ')"
echo "BRAND_SIGNALS_FOUND: $(echo "$BRAND_SIGNALS" | wc -l | tr -d ' ')"
```

If signals are non-zero, surface the gate in the brief: Stripe likely rejects,
Paddle likely rejects, ExtNet is the rail. Don't quietly recommend Stripe to a
brand-piracy product — the freeze 3 months in is worse than choosing ExtNet
day 1.

### Brief

```
D5 — Billing provider [TASTE — acquirer-availability gate]
Project/branch/task: $SLUG / $_BRANCH — which acquirer carries the rail
ELI10: We pick the company that processes credit cards for us. Stripe is
  cheapest but freezes accounts months in if it decides the product is
  borderline. Paddle moderates upfront — slower to get going but stable.
  ExtNet is the aggregator rail for products too brand-shaped or scraper-
  shaped for either. We have <SCRAPER_SIGNALS_FOUND> scraper signals and
  <BRAND_SIGNALS_FOUND> brand-name signals in the listing.
Stakes if we pick wrong: silent Stripe freeze 3 months in = revenue zeroed +
  user payment data trapped in dispute + listing trust damaged. Choosing
  Paddle on a clean utility = ~2% extra fee for 2 years.
Recommendation: <see below — keyed off scanner + product shape>
Completeness: A=8/10, B=9/10, C=10/10 (depending on product shape)
Pros / cons:
A) Stripe
  ✅ Lowest fees (~2.9% + $0.30); fastest onboarding for clean utility products
  ✅ Cleanest dashboard, best developer experience, mature webhook ecosystem
  ❌ Silent freezes on review — brand/scraper products get rejected months in
B) Paddle
  ✅ Moderates upfront — once approved, stable; no surprise freezes
  ✅ Merchant of Record handles VAT/sales tax (EU One Stop Shop included)
  ❌ Higher fees (~5%); 2–10 day onboarding; less developer-friendly
C) ExtNet aggregator / shared studio paywall
  ✅ Accepts brand-shaped and scraper-shaped products that Stripe/Paddle reject
  ✅ Below the ~$1,015/mo own-merchant breakeven this is cheaper than self-merchant
  ❌ 8% fee; you don't own the acquirer relationship; aggregator can change terms
Net: A is the clean default, B is the EU-friendly upgrade, C is the only rail for borderline products.
```

Recommendation logic (mechanical part of this taste call):
- `SCRAPER_SIGNALS_FOUND > 0` OR `BRAND_SIGNALS_FOUND > 2` → recommend **C** (ExtNet).
- Estimated MRR < $1,015 → recommend **C** (ExtNet, breakeven).
- EU-heavy geo mix (Tier-1 EU > 40%) → recommend **B** (Paddle, MoR).
- Otherwise → recommend **A** (Stripe).

The taste portion is the EU-vs-US lean call when signals are zero — surface to
user in `cws-autoplan`.

### Acquirer pair diversification

After D5, queue the second acquirer. **≥10 company-acquirer pairs target.**
The pair is `(legal_entity, acquirer)` — one legal entity can have one Stripe
account; ten entities can have ten Stripes. In-house studio target is 30 pairs
by year-end. The skill notes this as a `## Diversification target` section
in the artifact — it doesn't try to set up 9 more entities in one session.

### Write the decision

`monetization.provider.{primary, backup, all_in_fee_pct, mor}` to state.json.

---

## Phase 6 — host_permissions widening guard (D-N, only if needed)

If state.json `host_permissions.all_urls` is already `true` AND
`host_permissions.justified_at_launch` is `true`, **skip this phase**. The
permission was set at launch with a real all-sites function; no dialog risk.

If either is false, the user is asking to widen permissions on an existing
user base. This is the most expensive single mistake in Stage 5:

- Widening triggers Chrome's permission-change dialog on every existing
  installation.
- Playbook observed retention hit: **~30% click Remove on the dialog.**
- If you're at 3K weekly users, that's ~900 users gone in one update push.
- Stacking the widening with the monetization toggle doubles the loss.

### Hard gate

`cws-careful` is the hard gate here. Even if it passed for monetization, this
sub-decision needs its own pass:

```bash
/usr/bin/python3 - <<'PY'
import json, pathlib, sys
d = json.loads(pathlib.Path('./.cws/state.json').read_text())
careful = d.get('careful', {}) or {}
if not careful.get('host_perms_widen_passed', False):
    print('GATE_FAIL: cws-careful has not signed off on host_permissions widening')
    sys.exit(2)
print('GATE_OK')
PY
```

If the gate fails, route `/cws-careful` with the specific intent
"sign off on host_permissions widening". Stop.

If the gate passes, emit a brief acknowledging the cost:

```
D6 — Confirm host_permissions widening on existing user base
Project/branch/task: $SLUG / $_BRANCH — widening from <current> to <all_urls>
ELI10: We're adding broad permissions to an already-shipped extension. Chrome
  will show every existing user a scary dialog. Playbook data: about 30% click
  Remove. At our current 3K weekly users that's ~900 lost installs in one
  update push.
Stakes if we pick wrong: 30% existing-user retention loss stacked on a 2-
  position monetization rank dip = the rank dip never recovers because we
  lost the engagement signal that would have powered the recovery.
Recommendation: B (wire the justifying function first, ship one update with
  *only* the new function visible, wait 2 weeks, then ship monetization)
  because separating the two reduces compound loss to ~30% on the dialog
  push only, not 30% + monetization-conversion-tax
Completeness: A=4/10, B=10/10, C=6/10
Pros / cons:
A) Widen now, ship monetization in same update
  ✅ One push, one disruption, fastest to revenue
  ❌ Compound loss — 30% existing-user dialog dropoff + monetization rank dip stacked
B) Widen now, ship monetization 2 weeks later (recommended)
  ✅ Decouples the two losses; monetization runs on the post-dialog cohort
  ✅ 2-week buffer lets behavioral-factor signal recover before next stress
  ❌ Two release pushes; 2 extra weeks before revenue starts
C) Don't widen; skip the all-sites function
  ✅ No retention loss on existing users
  ❌ Losing the all-sites function that justifies the broad permission was a Stage 2 mistake; not widening here cements it
Net: A is reckless, B is the staged play, C admits the original launch was under-permissioned.
```

If the user picks A or B, write `host_permissions.all_urls = true` and queue
the justifying function in `./.cws/05-monetize.md` ## Host permissions. If C,
write a `WONTFIX` note and continue.

---

## Phase 7 — Sequential cohort rollout

The playbook's iron rule from `references/monetization-scaling.md`:
**300–500 unique paywall-viewers per variant minimum. Sequential cohorts, not
parallel A/B.** Below 300 viewers, the ~1% paying conversion gives you <3
paying users — every "result" is noise.

### Cohort plan

- **Cohort 1**: 500 viewers on the recommended config from D1–D5. Run for
  whatever calendar time it takes to hit 500 viewers (typically 3–10 days at
  3K weekly users).
- **Cohort 2**: 500 viewers on the second-most-promising variant (usually the
  D2 alternative — annual-only vs hybrid is the playbook-favored second test).
- **Cohort 3**: 500 viewers on the third variant (typically D3 trial duration
  flip — 3-day vs 7-day).

### Tier-1-first

Per the playbook rule: paywall fires for **Tier-1 only** (US/UK/CA/AU + EN-
language EU). Tier-2/3 see the free experience. This preserves their
engagement signal for behavioral-factor ranking. Implementation: the paywall
checks `navigator.language` and the IP-geo against a Tier-1 allowlist.

### Cut paid traffic

Before Cohort 1 starts, **cut any remaining paid traffic from cws-promote.**
The playbook instruction is explicit: cut paid traffic *abruptly* when ~250
installs have landed. Paywall flip on a paid-traffic-mixed cohort gives you
the conversion of paid traffic, not the conversion of your organic audience —
the audience that determines whether the SEO survives.

### Cohort log format

Append to `./.cws/05-monetize.md` under `## Rollout cohorts`:

```markdown
### Cohort 1 — 2026-MM-DD start
- Config: tier=medium-low, cycle=hybrid, trial=3day-card-first, placement=soft, provider=Stripe
- Tier filter: Tier-1 only (US/UK/CA/AU/EN-EU)
- Viewers needed: 500
- Viewers reached: <fill in>
- Paying conversions: <fill in>
- Refund/chargeback rate: <fill in>
- Behavioral-factor signal (rank position vs baseline): <fill in>
- Verdict: <continue / flip variable X / abort>
```

### Skill loop

After each cohort, `cws-monetize` doesn't auto-decide the next variant — it
emits a `D<N>` brief comparing observed conversion against the previous cohort
and recommends what to flip next. The lift-ordering rule constrains the
flipping order: D2 (cycle) before D3 (trial) before D1 (price).

### Skip the analytics platform

Per the playbook: **skip Amplitude/Mixpanel** until several thousand users. At
3K weekly users, ~500-viewer cohorts, ~5 paying users per arm — funnel
analytics tools mislead at this sample size. Use a hand-rolled funnel:

```
listing view → install → activation → key action → paywall view → paying
```

Numbers from each step go into the cohort log. That's the analytics.

---

## Phase 8 — Portfolio scaling (D-N, TASTE — only when ready)

Reachable only when:
- First product `monetization.enabled = true`
- First product has been grandfathered (older users locked into free or original price)
- Monetization revenue has stabilized (≥4 weeks of cohort data)

If any condition is unmet, **defer this phase**. Write a stub in
`./.cws/05-monetize.md` `## Portfolio` saying "Defer until ≥4 weeks
post-monetize stable". Don't surface the D brief.

### What portfolio scaling actually is

Spawning a **second** extension on the same operator (proxy + Dolphin profile +
Google account isolation per `../cws-idea/references/account-setup.md` rules). NOT
re-skinning the first extension on a new account — Chrome detects code-reuse
signals at distance and bans the whole network.

Hard constraint from playbook: **max 2–3 extensions per portfolio.** Above 3,
the founder's wrap-up call is explicit: the whole network gets banned. The
exception: **genuinely different niches** (e.g. converter + AI chat) may share
one operator account. Same-niche near-duplicates may not.

### When NOT to spawn a second

- First product MRR < ~$2K–$5K solo. The playbook's "don't delegate before $2K–$5K
  MRR" applies to portfolio scaling too — scaling out before the first product
  is dialed multiplies whatever you haven't yet fixed.
- Relaunch cadence < 3–4 months from first launch. Playbook data: the first
  launch often outperforms later ones because Google's 6-month consolidation
  hasn't completed. Spawning early cannibalizes the per-country experiment.
- The 7-year first-success trap. If the first extension was your first-ever
  success, **stay on it** through the 6-month consolidation cycle and beyond.
  The playbook founder's case: 7-year gap between first lucky hit and second
  working launch. Don't abandon the method because the first one worked.

### Brief

```
D7 — Spawn a second extension on this operator [TASTE]
Project/branch/task: $SLUG / $_BRANCH — portfolio scaling decision
ELI10: We've got a monetizing extension. Now we decide whether to start a
  second one on the same operator account. Chrome detects code-reuse across
  accounts, so we can have at most 2–3 extensions per operator. Spawning the
  second one early cannibalizes the first; spawning it too late leaves money
  on the table. The playbook says wait until first product is stable and
  monetizing for ≥4 weeks AND in a genuinely different niche.
Stakes if we pick wrong: spawn a near-duplicate on a second account = whole
  portfolio banned. Spawn early = first product loses operator attention
  before 6-month consolidation completes = first product underperforms its
  potential ceiling.
Recommendation: B (queue cws-idea now for a different-niche candidate; do
  not start the build until first product is at 8+ weeks post-monetize) because
  the 7-year first-success trap is real and the 6-month consolidation isn't
  yet complete
Completeness: A=5/10, B=10/10, C=7/10
Pros / cons:
A) Start the second extension now (same operator, different niche)
  ✅ Faster portfolio revenue; second product starts its own 6-month consolidation early
  ❌ First product loses operator attention during its consolidation phase
  ❌ Risk of code-reuse signals if the second product borrows components
B) Queue cws-idea for a different-niche candidate; defer build to 8+ weeks (recommended)
  ✅ First product completes its consolidation cycle with full operator attention
  ✅ Idea bank ready when timing is right; no idle time when first product is dialed
  ✅ Honors the 7-year first-success trap insight; doesn't abandon the working product
  ❌ 8 weeks of opportunity cost on the second product's launch curve
C) Don't scale; stay solo on the first product
  ✅ Maximum focus; the playbook's revenue leaders are all solo on one product
  ❌ Single-product revenue ceiling; one freeze = 100% revenue gone
Net: A is fast-follower mode, B is the playbook-disciplined play, C is the maximum-focus play.
```

Auto-mode flags this for taste — never auto-decides portfolio scaling.

### Operator-isolation requirement

If the user picks A or B and starts the second extension build, the second
extension **must** get its own Dolphin profile + Google account + (preferably)
its own proxy. Code reuse across the *Chrome accounts* is what triggers the
network ban; code reuse *inside one developer dashboard* is fine because
Chrome already sees one entity. Don't mix this up.

`cws-monetize` doesn't run the second-extension setup — it queues `/cws-idea`
with a context note saying "second extension on portfolio operator". The next
session re-enters `cws-idea` with `account_setup.portfolio_slot=2`.

### Write the decision

`monetization.portfolio.{decision, deferred_until_weeks, queued_skill}` to
state.json.

---

## Phase 9 — Write the artifact

Produce `./.cws/05-monetize.md`. Frontmatter:

```yaml
---
stage: cws-monetize
status: complete
created: <UTC ISO>
updated: <UTC ISO>
weekly_users_at_enable: <int>
provider: <Stripe|Paddle|ExtNet>
billing_cycles: <list>
paywall_url: <url>
---
```

Sections (in this order):

```markdown
## Pricing tier
- Tier band: <Light|Medium-low|High>
- Initial price: $<usd>/mo (initial — ratchet up after Cohort 3)
- Reasoning: <one paragraph tying D1 to launch outcome>

## Billing cycle
- Composition: <Monthly|Annual|Hybrid>
- Featured cycle: <which>
- Annual discount: <pct> if hybrid
- Reasoning: <one paragraph; cite lift-ordering rule>

## Trial
- Duration: <None|3-day|7-day>
- Card-first: <yes|no>
- Reasoning: <one paragraph>

## Paywall placement
- Placement: <Soft|Hard|After-N|Immediate>
- Gated feature (if soft): <named feature>
- Tier filter: Tier-1 only
- Reasoning: <one paragraph; cite engagement-signal preservation>

## Provider
- Primary: <Stripe|Paddle|ExtNet>
- Backup pair: <queued second acquirer pair>
- All-in fee: <pct>
- MoR: <yes|no>
- Reasoning: <one paragraph; cite acquirer-availability gate>

## Diversification target
- Current pairs: 1
- Target by year-end: ≥10
- Next pair queued: <legal_entity, acquirer>

## Host permissions
- Status at launch: <narrow|all_urls>
- Widened in this session: <yes|no>
- Justifying function: <named function or "not applicable">
- Decoupling plan if widened: <one paragraph>

## Rollout cohorts
### Cohort 1 — <start date>
- Config: <full config>
- Viewers: <n>
- Conversions: <n>
- Refund/chargeback: <pct>
- Rank position vs baseline: <delta>
- Verdict: <continue / flip X / abort>

(repeat for Cohort 2, Cohort 3 as they run)

## Portfolio
- Decision: <D7 outcome>
- Deferred until: <weeks if B>
- Queued skill: <cws-idea or none>
- Operator slot 2 plan: <one paragraph>

## State.json updates applied
- monetization.enabled: true
- monetization.billing_cycle: <chosen>
- monetization.paywall_url: <url>
- monetization.weekly_users_at_enable: <int>
- gates_passed += ["monetize"]
```

### Apply state.json updates

```bash
/usr/bin/python3 - <<'PY'
import json, datetime, pathlib
p = pathlib.Path('./.cws/state.json')
d = json.loads(p.read_text())
mon = d.setdefault('monetization', {})
mon['enabled'] = True
mon['billing_cycle'] = '<chosen from D2>'
mon['paywall_url'] = '<paywall url>'
mon['weekly_users_at_enable'] = <int from preamble>
mon['provider'] = '<from D5>'
mon['paywall_placement'] = '<from D4>'
mon['trial'] = {'duration_days': <int>, 'card_first': <bool>}
mon['pricing'] = {'tier': '<from D1>', 'initial_usd': <float>}
gp = d.setdefault('gates_passed', [])
if 'monetize' not in gp:
    gp.append('monetize')
d.setdefault('history', []).append({
    'ts': datetime.datetime.utcnow().isoformat() + 'Z',
    'stage': 'cws-monetize',
    'event': 'gate_passed:monetize'
})
d['last_updated'] = datetime.datetime.utcnow().isoformat() + 'Z'
p.write_text(json.dumps(d, indent=2))
print('state.json updated')
PY
```

Log the gate:

```bash
"$BIN/cws-timeline-log" "{\"skill\":\"cws-monetize\",\"event\":\"gate_passed:monetize\",\"weekly_users\":\"$WU\",\"provider\":\"$PROVIDER\"}" 2>/dev/null
```

---

## When NOT to use cws-monetize

- **Pre-3K-weekly users**: blocked. Phase 0 refuses to advance. The hard floor
  is non-negotiable. Playbook finding: monetizing below 3K kills the
  behavioral-factor signal before it consolidates. Recent in-house launches
  wait until ~100K users; 3K is the studio's documented floor for solo
  builders, not the optimal point.
- **Mid-launch / active moderation**: blocked. If the extension is in
  moderation or just emerged from it and hasn't shown ≥4 weeks of stable
  organic, monetization adds stress on top of moderation stress. Route to
  `/cws-retro` for one more weekly cycle.
- **Search position not consolidated**: blocked. The 2-position dip from
  monetization is survivable only when rank is established. Pre-consolidation,
  the dip becomes permanent because there's no engagement-signal moat to
  recover from.
- **`cws-careful` not passed for monetize**: blocked. The skill refuses to run
  Phase 1 onward without an explicit `careful.monetize_passed = true`.
- **Existing monetized extension with stable revenue**: route to `/cws-retro`
  for monthly snapshots. `cws-monetize` is for *enabling*, not maintaining.
  The maintenance cadence lives in retro.
- **Brand-piracy or scraper-shaped product without acquirer pre-clearance**:
  Phase 5 must explicitly assign ExtNet or shared studio paywall. Don't try
  Stripe; the silent freeze 3 months in is the worst outcome in this stage.

---

## Companion skills

- **`cws-careful`** — HARD gate before enabling monetization. Required to set
  `careful.monetize_passed = true`. Re-runs as a sub-gate before any
  host_permissions widening. Skip this and Phase 0 refuses.
- **`cws-challenge`** — adversarial stress-test of the billing-cycle decision
  (D2). The lift-ordering rule says D2 is the biggest lever — challenge it
  before committing 1500 viewers across 3 cohorts. The playbook's wrap-up call
  explicitly recommends stress-testing the cycle composition against the
  audience persona.
- **`cws-retro`** — monthly cadence after monetization is live. Tracks
  conversion drift, refund-rate drift, rank-position recovery from the
  2-position dip, geo-localized pricing experiments.
- **`cws-learn`** — record what worked. Every cohort log entry that crosses
  a verdict threshold should be promoted to a learning. The playbook data
  itself is somebody else's learning bank; build your own.

---

## Gate to the next stage

`gates_passed` must include `monetize` and `monetization.enabled` must be
`true` in state.json before any post-monetize skill runs. Re-entry protocol:
`cws-resync` if state and artifacts drift.

## Skill Routing Footer

After monetization is enabled, the cadence is monthly retro (not weekly — the
post-monetize curve is slower and weekly noise dominates signal). If
portfolio scaling D7 picked A or B, the parallel cadence is queue `cws-idea`
for the second-extension candidate. Pick one Next line:

```
Next: /cws-retro
Why: Monthly cadence post-monetize — track conversion drift, refund-rate
  drift, rank recovery from the 2-position monetization dip, and geo-pricing
  experiments. Weekly retro is too noisy at this stage.
```

If D7 picked A (start second extension now) or B (queue for second extension):

```
Next: /cws-idea
Why: D7 picked second-extension portfolio scaling. Run cws-idea with
  account_setup.portfolio_slot=2 — different-niche candidate, separate Dolphin
  profile + Google account on the same operator.
```

Never list both. If the operator has both monthly retro *and* a second-
extension queued, pick the retro on first run after enabling monetization
(immediate cadence), then `/cws-idea` on the next session.
