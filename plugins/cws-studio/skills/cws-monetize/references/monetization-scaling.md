# Stage 5 — Monetization & scaling

Post-launch: collect uninstall feedback, wire monetization, lock in host
permissions, and optionally sell the product.

## Uninstall Page

Opens immediately after a user removes the extension; collects removal reasons
via a simple Google Form (single question: *"Why have you deleted the app?"*).
~5–15% of users fill it in — valuable for improving the product. Host it on the
same domain as the Welcome Page (same setup as Stage 3). Examples:
service-pages.info/extensions/newtab/dark_theme/uninstall,
ext.aitools.band/delete/bingchatgpt. Wire it in the service worker:
```js
const UNINSTALL_URL = "https://your-uninstall-page";
chrome.runtime.setUninstallURL(UNINSTALL_URL);
```
Expect emotional feedback — only ~5% of form answers are reasoned critique. You
only ever see feedback from people who *left*; the silent 90% who kept the
product are invisible. Don't let it distort your judgment.

## When to add monetization

Monetization is a **stress factor for SEO** — secure a good search position
first, then turn it on. You also want to compare traffic before/after
monetization per country (disable it where traffic dropped, keep it where it
didn't). At low user counts there may simply be no payments yet — that's
statistics, not a broken product (the founder's brain will insist otherwise).

- **No-cost product**: grow to **4–5K weekly active users**, then add
  monetization (e.g. the studio Paywall).
- **Product with running costs**: cover the costs yourself at first (builders
  average $100–200), wait for active installs, then add monetization.

## Monetization is systematic experiments, not a recipe

There is **no fixed "do 1-2-3"**. Two products in the same niche, same geo, same
price — one monetization setup earns, the other doesn't (Google trains each
listing's audience slightly differently). The only method is to run a **broad,
systematic pool of pricing experiments** and find your audience's optimal point.
The studio Paywall exists to run these experiments fast — attached on the
frontend, so you change tariffs/trials/targeting **without re-moderation**.

**What moves payment conversion most** (studio statistics, your product may
differ):
1. **Billing cycle** — *the* biggest lever, bigger than price. Which options you
   offer (weekly / monthly / yearly) strongly shifts conversion.
2. **Trials** — with / without; trial limited by time or by **action count**;
   card-first-then-trial vs. open trial.
3. Price — lower-impact than the above two.

Paywall also supports **geo-localized pricing** (price-discriminate by country —
a Swiss user pays more than a Vietnamese one; Big Mac index), currency per geo,
and custom country targeting — all without moderation.

Monetization is a behavioral-factor stress: expect a small ranking dip (e.g.
#3 → #5) and tune aggressiveness against it. A well-established product can keep
growing even with monetization on. Roll out gradually (see below).

## Monetization models

**Subscription / one-time purchases** — the highest-converting model. Use the
studio Paywall (monetize.software/ru/publisher/paywalls; activation instructions
in its Telegram channel). Once you have a few thousand users, switch the paywall
to live mode and leave only a few free actions.

**Banner ads** — for any extension with UI windows. Register your site in Google
AdSense, pass its moderation, embed an ad script on the most-opened page (e.g.
Tab for a Cause puts AdSense banners on the new tab).

**Search affiliate programs** (Google, Bing, Yahoo, Yandex) — for any extension;
request the integration library from the studio.

**Traffic resale to other products** — for any extension; show partners' banners
on your Welcome Page / in the UI. Extensions doing this: Dark Reader, ChatGPT for
Google, chrome-stats.com. Heavy buyers of such traffic: Merlin, Monica, Sider,
MaxAI, Honey, DuckDuckGo. To implement: email a potential partner offering a
banner placement, agree terms, place it.

**Community around the product** — for topical extensions whose users share an
interest/profession. Run an English newsletter for the audience; add a popup
offering Google sign-in with a checkbox subscribing the user to the newsletter
(opt-out allowed); send via beehiiv.com; after 1–2K emails find a relevant
sponsor on paved.com. The studio E-wall service collects emails in a few clicks
(Google auth, per-country collection, customizable UI/copy, daily analytics, CSV
export). Example: Superpower ChatGPT.

**Selling the product** — for any extension. Ensure a working contact email is on
the store page; get an offer and close via escrow.org, or list on flippa.com and
settle via escrow.

## Maximum host permissions — lock in early

Chrome docs say to request minimal permissions; for this method do the
**opposite** — request maximum host permissions / content scripts **early**:
```json
"host_permissions": ["http://*/*", "https://*/*"]
```
(or equivalently `["<all_urls>"]`; `content_scripts[].matches` follows the same
logic, e.g. `["<all_urls>"]`).

**Why:** if you add max host permissions *later*, every existing user gets a
scary permission-change dialog on update — many click **Remove**, and you lose
half your user base. So introduce a function that *justifies* max permissions
early — at the **1–2K users** mark, not at tens of thousands. You must justify it
to moderation with a real feature that works on all pages.

## A function that needs access to all sites

Add a feature that genuinely runs on every page so the broad permission is
justified — e.g. a barely-visible artifact in the corner of all pages that, on
hover, reveals a link (e.g. activating dark theme on YouTube); or a more visible
draggable artifact (dismissible via an `x` icon) that opens the extension's
functionality on click. The studio has a ready draggable/dismissible-artifact
repo for bootcamp participants (request access from curators).

## Case-study insights from the final wrap-up call

### When to monetize

- **Hard floor: never before ~3,000–4,000 users.** Recent in-house launches
  wait until **~100K users** before turning monetization on. The earlier you
  monetize, the more you risk a permanent SEO collapse.
- Don't enable monetization until the product has **consolidated in search**
  (first organic installs visible). Typical timeline: first organic trickle
  **1–2 months** post-launch; full-power organic **~6 months**.
- KPI for "the project worked": **>10K users after 1 year**. Median funnel:
  every 2nd in-house launch passes this; every 3rd produces revenue.
- Median launch cadence for revenue-earning builders is **~2.4 products/year**,
  not 12. Larger 4–5/year only after a first hit.

### Paywall mechanics — observed conversion impact

- Lift ordering: **(1) billing-cycle composition** (weekly/monthly/yearly mix)
  outweighs **(2) trial design**, which outweighs **(3) price**. Cycle
  composition is bigger than price.
- Trial sub-variants worth testing independently: time-limited vs
  action-count-limited vs no-trial; open trial vs **card-first-then-trial**
  (card-first converts higher but irritates on mobile; mixed on web).
- **Tier-1-first paywall rollout.** Serve Tier-2/3 a free experience so they
  keep generating behavioral-factor signal (engagement) without paying — a
  stealth way to maintain SEO rank during monetization.

### Pricing

- **Start at the low end of the price range** and ratchet upward — opening at
  $100/mo yields zero data because nobody pays.
- **VAT applies on top per buyer-country** (5–27%; peak 27% in Hungary). When
  selling into the EU from elsewhere, remit via the EU **One Stop Shop**.
- Realistic all-in cost stack on web subscriptions: **~30% total** (acquirer
  ~5%, bank 1–3%, payout 2–4%, paywall 8%, VAT, corp tax capped ~10%).
  Compares favorably to mobile's 15–30% store cut alone.

### Experiment design

- **Minimum sample per paywall variant: 300–500 unique paywall-viewers**
  before drawing conclusions. Below this, draw no conclusions — average
  paying conversion ~1%.
- **Skip A/B split tests inside the paywall.** Run **sequential cohorts**
  (500 viewers config A, then 500 viewers config B). Simpler, fewer bugs,
  equally informative at this scale.
- **Skip Amplitude/Mixpanel** until you have several thousand users — small-
  sample funnels mislead. Use self-testing + friends/family as the primary
  signal source pre-monetization. Even at monetization time, a hand-rolled
  funnel (listing → install → activation → key action → paywall view →
  payment) is sufficient.
- Change cadence is driven by **sample size, not calendar**. Daily changes
  are fine if you have ~500 paywall views per change.
- **SEO copy (title/short/long description) — change at most every 6 months,
  typically less.** Don't tune SEO while still learning whether current SEO
  works.

### Behavioral-factor protection

- **Expected ranking dip on monetization: ~2 positions** (e.g. #3 → #5).
  Stable, well-ranked products keep growing through it.
- **Roll out paywall to paying-geo Tier-1 first**; keep Tier-2/3 free
  initially to preserve engagement-based ranking signal.
- Treat pre-monetization ad spend as cheap behavioral-factor purchase:
  **~$50–$150 (median $100, range $150–$300)** for ~250 installs is the
  calibration point. **Cut paid traffic abruptly** the moment ~250 installs
  land — not gradually.

### Models — when each works

- **Banner/AdSense monetization needs several thousand DAU** minimum to make
  meaningful revenue; subscriptions can earn on far smaller bases.
- **ExtNet** (cross-extension traffic resale): route users from high-user/
  low-revenue extensions to high-revenue extensions in the same network;
  revenue split. Useful once you have a portfolio.
- **Breakeven for own merchant entity vs shared paywall: ~$1,015/mo
  revenue.** Below that, shared infrastructure (8% fee) is cheaper than
  legal/banking setup.
- **Acquirers: Stripe or Paddle only.** Stripe approves first, audits later
  (silent freezes common); Paddle moderates upfront.
- **Diversification target: ≥10 company-acquirer pairs** so any single
  freeze ≤ 10% of revenue (in-house team target: 30 pairs by year-end).

### Traffic resale / email / sale

- **Selling the extension is most justified when you have traffic but no
  monetization yet.** Multiplier formulas differ for revenue-bearing vs
  pre-revenue assets.
- Pre-revenue sale benchmark: first founder extension sold for **$50K with
  no revenue attached**.

### Uninstall Page — observed patterns

- Observed completion rate: **~1 in 5 (~20%)** — far higher than any normal
  survey, because users believe the form is mandatory to complete uninstall
  (it isn't).
- Quality distribution: **~1 in 15–20** responses is thoughtful multi-
  paragraph feedback; rest is venting. Filter accordingly.
- Geo skew on useful feedback: thoughtful reasoned responses concentrate in
  Western Europe / North America.

### Host permissions — timing

- **Justify max host permissions BEFORE monetization rollout, not after.**
  Adding them post-monetization triggers the permission-update dialog
  simultaneously with revenue-on stress, doubling user loss.

### Post-launch scaling

- **Don't spawn near-duplicate extensions on multiple accounts** — Chrome
  detects code reuse across accounts at distance; the whole network gets
  banned. Maximum safe portfolio: **2–3 extensions**, each with a genuinely
  distinct functional spin (different niche or differentiated function),
  launched on different store accounts as insurance even when policy permits
  one account.
- **Genuinely different niches** (e.g. converter + AI chat) may share one
  account.
- **Don't delegate before ~$2K–$5K MRR solo on one product.** Delegation
  scales whatever errors you still have. Build revenue first.
- **Solo-founder dominates** in micro-extension success — top 5 by revenue
  in the alumni community are all solo; 60/40 solo-vs-pair across the whole
  revenue cohort; 3+ person teams almost universally fail or self-destruct
  via internal conflict.
- **Co-founder split: 50/50 with ~1% tiebreaker** to the SEO/product lead so
  decision deadlocks resolve. Equity stinginess (giving devs 15%) reliably
  kills partnerships.
- **Don't relaunch in cycles shorter than 3–4 months apart.** Rapid relaunch
  cannibalizes your own learning. The first launch often outperforms later
  ones once Google's per-country experiment phase completes (~6-month
  consolidation).
- **First-time-success trap.** Builders whose first-ever launch succeeds tend
  to abandon the method assuming general talent; the founder's own case
  showed a 7-year gap between first lucky hit and second working launch,
  then 4 more years to systematic repeatability.

### Analytics gotchas (used to time monetization decisions)

- **Chrome dashboard Installs/Users graphs always read 0 on the latest date**
  — data lag, not a drop.
- **GA4 "Active Users" and "New Users" on the listing page are meaningless**
  for extensions (metric inherited from website analytics). Use **First
  Visits** (unique listing visits) and **Install** events; their ratio = real
  install conversion. Norms: **paid traffic 10–15%, organic 15–30%**.
- **GA4 timezone is locked to San Francisco** — expect ~half-day lag and
  mismatch vs ad-platform stats.
- **Filter Facebook ad bots** by excluding `Operating System contains Linux`
  in GA4 segments — FB sends large bot waves from Ireland/UK/US on Linux
  post-moderation to verify the listing.
- **Per-country install table: last column is always 0** (data not yet
  pulled) — diagonal-pattern fills indicate Google's per-country ranking
  experiments, not bot traffic.
- **Uninstall-rate benchmark**: ~30% average; **≤15% excellent**; 40% can
  still be a $13K/mo product if it's a one-shot-use extension with
  monetization.
- **Enable/disable rate ~10% over distance is normal**; 3% on a new product
  is fine.

