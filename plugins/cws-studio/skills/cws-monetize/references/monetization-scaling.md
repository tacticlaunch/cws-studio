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

### Paywall conversion bands by tier (gap backfill from bootcamp Lesson 243)

The bootcamp does not publish a clean conversion-band table. The figure that
*is* cited explicitly: **"normal conversion in a project is 1%"** (Lesson 243,
line 846 of the wrap-up call: *"нормальная конверсия в проекте 1%"*). Around
that baseline, the studio gates decision-making on **300–500 unique paywall
viewers per variant** before drawing any conclusion (line 843).

Build conversion bands from the studio's geo + experiment guidance — bands are
**operator-defined targets** seeded from the 1% norm, NOT verified per-band
numbers from the transcripts. Treat as TODO unless confirmed inside the
operator's own paywall analytics.

| Tier band                 | Geo                                        | Expected paywall→paid conversion | Notes |
|---------------------------|--------------------------------------------|----------------------------------|-------|
| **High**                  | US, UK, CA, AU, CH, DE, FR, NL, SE, NO     | 1.5–3% (target band)             | Tier-1 paying audience; full pricing applies. |
| **Medium**                | Rest of EN-EU (ES, IT, PT, IE, BE, AT, FI) | 0.8–1.5%                         | Lower price elasticity; localize currency. |
| **Medium-low**            | Eastern EU + LATAM Tier-2                  | 0.3–0.8%                         | Use Big-Mac-index discounting. |
| **Low / behavioral-only** | SEA, AF, RU/CIS, IN                        | <0.3% (often ~0%)                | **Do NOT paywall.** Keep free to preserve engagement signal (Lesson 243, lines 834–836). |

**Decision rule (from Lesson 243, lines 834–836):** *"На старте не стоит на
всех раскатывать поевол. Раскатайте только на тех, кто будет платить на TR1.
Набирайте поведенческий фактор, продолжайте набирать даже во время монетизации
через TR2 и TR3."* — At launch, only enable the paywall for Tier-1; keep
Tier-2/3 free so they continue generating behavioral-factor (ranking) signal.

The 1% baseline is mean across products; the studio explicitly warns
(Lesson 243, line 847): products with ~1000 users earning $1000/mo are not
unusual — *do not extrapolate from your small sample*. Below **300 unique
paywall viewers per variant**, treat band figures as noise.

**Operator action stub:**
```
After 300+ unique paywall viewers in a single band:
  observed_cvr = paid / paywall_views
  if observed_cvr < (band_target_low / 2): reduce price OR change billing cycle
  if observed_cvr > band_target_high: hold; check refund/dispute rate before raising price
  if observed_cvr between band_target_low and band_target_high: continue, iterate trial design
```

TODO(operator): replace target bands with your own measured conversion after
500 viewers per band — bootcamp does not publish per-band CVR; only the 1%
overall baseline and the "Tier-1 first" rollout rule.

### Card-first vs open-trial — mobile vs desktop split (gap backfill from Lesson 243)

Transcript is **qualitative, not numeric** on this split. Key quotes:

- Lesson 243, lines 826–829: *"Можно попросить данные карты, но не списывать
  деньги, так называемая система, сначала карта, потом триал. Всех это,
  конечно, бесит по-мобильному, но не везде опять… Это довольно конверсионная
  механика, но не везде она работает."*
- Reference text already at lines 49 and 138–139: *"card-first converts higher
  but irritates on mobile; mixed on web."*

No bootcamp lesson publishes %s. Operator-pattern target bands (seed values,
NOT bootcamp-verified):

| Surface              | Card-first paywall CVR target | Open-trial paywall CVR target | Notes |
|----------------------|-------------------------------|-------------------------------|-------|
| Desktop (web)        | 1.5–3%                        | 0.8–1.8%                      | Card-first dominates on desktop where typing card data is low-friction. |
| Mobile (web)         | 0.3–0.8%                      | 0.8–1.6%                      | **Open trial usually wins on mobile.** Mobile keyboards + 7-day surprise charge → high refund/dispute risk. |
| Cross-device average | ~1% (matches baseline)        | ~1% (matches baseline)        | The 1% baseline absorbs the mix. |

**Decision rule (operator pattern):**
```
If extension is desktop-dominant (>70% sessions desktop): default to card-first-then-trial
If extension is mobile-significant (>30% sessions mobile): default to open-trial
  → if you must run card-first on mobile: shorten trial to 3 days, send T-1d "trial ends tomorrow" email
Always: monitor dispute rate per surface separately (see refund/chargeback section)
```

TODO(operator): the mobile/desktop split is qualitative in Lesson 243; backfill
with measured per-surface paywall_views/paid_conversions/disputes after first
1000 viewers per surface. The bootcamp's only firm number is the **1% overall
baseline** at 300–500 viewers per variant.

### Grandfathering policy (gap backfill from Lesson 243)

The bootcamp does NOT specify a grandfathering rule for pre-monetization
installs. The closest implicit guidance from Lesson 243:

- **Maximum host permissions must be justified *before* monetization rollout
  (Lesson 247 + Lesson 243 line ~1068)** — adding both stresses at once
  doubles user loss. This means: at monetization rollout time, you already
  have a stable install base that pre-dates the paywall.
- **Tier-2/3 stays free permanently as a behavioral-factor pool** (line 834).
  This is *de facto* permanent grandfathering by geo — Tier-2/3 users never
  see the paywall and keep generating engagement signal.
- **The paywall is attached on the frontend without re-moderation** (lines
  756–757). Existing users never see a "you must now pay" install dialog —
  they only encounter the paywall when they hit a gated action.

**Recommended grandfathering policy (operator pattern; bootcamp-aligned but
NOT explicitly transcribed):**

| Cohort                                       | Treatment                              | Rationale (Lesson 243 alignment) |
|----------------------------------------------|----------------------------------------|----------------------------------|
| Pre-paywall installs in Tier-1 geo           | **Free for 14 days** post-paywall enable, then standard paywall on next gated action | Soft landing; prevents uninstall spike. Lesson 243 line 1014 warns against "annoying users" with sudden monetization. |
| Pre-paywall installs in Tier-2/3 geo         | **Free forever** (no paywall ever)     | Tier-2/3 = behavioral-factor pool by policy (lines 834–836). |
| Post-paywall installs in Tier-1              | Paywall on standard cadence (1st gated action) | Default state. |
| Post-paywall installs in Tier-2/3            | No paywall                             | Same as pre-paywall Tier-2/3. |
| Users who already paid (any geo)             | **Locked price** for life of subscription unless they cancel | Standard SaaS practice; the bootcamp's "не бесить" principle (line 1014). |
| Cancelled-then-returned users                | Current price applies (no grandfather) | Operator default; not in transcripts. |

**Operator action stub:**
```js
// In service worker or paywall config
const PAYWALL_ENABLE_DATE = Date.parse("2026-MM-DDTHH:mm:ssZ");
chrome.runtime.onInstalled.addListener(({ reason }) => {
  if (reason === "install") {
    chrome.storage.local.set({ install_ts: Date.now() });
  }
});

// At paywall check:
chrome.storage.local.get(["install_ts"], ({ install_ts }) => {
  const isPreMonetize = install_ts && install_ts < PAYWALL_ENABLE_DATE;
  const userGeo = await getGeo(); // via IP lookup
  const isTier1 = TIER_1_ALLOWLIST.includes(userGeo);

  if (!isTier1) return showFree();                           // tier-2/3 permanent free
  if (isPreMonetize && (Date.now() - PAYWALL_ENABLE_DATE) < 14*864e5)
    return showFree();                                       // 14-day soft landing
  return showPaywall();
});
```

TODO(operator): the bootcamp does not transcribe an explicit grandfathering
rule. The "Tier-2/3 free forever" rule IS bootcamp-explicit (Lesson 243). The
"14-day soft landing for pre-paywall Tier-1" is **operator-recommended only**
— validate against your own uninstall-rate delta in the 14 days post-rollout
before committing.

### Refund / chargeback / dispute benchmarks (gap backfill from Lesson 243)

The bootcamp publishes ONE hard threshold:

- **Dispute rate must stay under ~1%** (Lesson 243, lines 905–906): *"в этом
  с этапе у вас диспутов сильно больше, чем 1%, то что допустимы по внутренним
  непубликуемым вот этим вот, ну таким, как бы, мануалом экварингов. Блокировка
  очень вероятна."* — Disputes above ~1% (the unpublished acquirer threshold)
  make a Stripe/Paddle ban highly likely, and bans propagate at three levels:
  product, company, founder.

The "~25% surprise-charge refund spike on impulse tools at 7-day trial"
operator-flagged in the rewrite is **NOT in Lesson 243.** It is plausibly
sourced from a different lesson or operator memory; treat as operator
heuristic. Bootcamp gives only:

- **Card-first-then-trial = "irritates on mobile"** (line 827) — refund risk
  implied, not quantified.
- **Disputes are existential** — a single dispute spike from a new product on
  a fresh acquirer cabinet can wipe the entire cabinet (lines 901–907).

**Operator-pattern dispute/refund benchmarks (NOT bootcamp-verified):**

| Tier band            | Refund-rate target | Dispute-rate target | Action threshold |
|----------------------|--------------------|---------------------|------------------|
| High (Tier-1 core)   | <3% of paid        | <0.5% of paid       | Investigate at 5% refund / 0.7% dispute |
| Medium (EN-EU rest)  | <5% of paid        | <0.7% of paid       | Investigate at 8% refund / 0.9% dispute |
| Medium-low           | <8% of paid        | <0.9% of paid       | Investigate at 12% / >1% disable card-first |
| Impulse-tool surface (any tier) | <15% of paid (rewrite cites ~25% spike on 7-day surprise charge) | <1% always | If refund spike >20% within 30d of trial change → **revert immediately** (acquirer block precedes the next month) |

**Decision rule (Lesson 243 line 905):**
```
if dispute_rate_30d > 1.0%:           # acquirer-published red line
    halt paywall changes
    audit last 30d of paid users for shared refund reason
    revert most recent paywall change
    if dispute_rate still > 1%: pause monetization for the cabinet entirely
```

**Surprise-charge mitigation (operator pattern):**
- Send T-1d trial-ending email/notification (not just T-0 charge)
- Show in-extension banner on day 6 of 7-day trial: "Your trial ends tomorrow"
- Make cancellation 1-click inside the extension (no dark-pattern flow)
- The bootcamp does NOT prescribe these; they are standard SaaS best-practice
  to keep dispute rate <1%.

TODO(operator): the per-tier refund/dispute bands above are operator seed
values, NOT bootcamp-published. The ONE bootcamp-verified threshold is
**dispute_rate < 1%** (acquirer ban risk above this). The "~25% impulse-tool
refund spike on 7-day trials" needs source confirmation (likely a separate
lesson or community note, not Lesson 243).

### ExtNet — pricing and terms verification (gap backfill from Lesson 243)

Status: **partially verified.** Lesson 243 lines 1007–1018:

- ExtNet (the bootcamp transcribes it as **"ExtEts"** at line 1010, ambiguous
  Russian spelling — same product) is **studio-owned cross-extension traffic
  resale**, routing users from high-user/low-revenue extensions to
  high-revenue extensions inside the studio network.
- *"У нас есть своя написанная система, называется ExtEts, из-за того, что в
  Викле Active Users мы эту трафику друг другу можем переливать, уже тоже
  проводим эксперименты, они довольно многообещающие."* (Lesson 243, lines
  1010–1011)
- *"ExtEts будет тоже полностью в вашем распоряжении. Вот, прямо сейчас мы
  уже его внедряем в кучу продуктов."* (line 1018)

**What Lesson 243 verifies:**
- ExtNet is a studio service, opt-in for bootcamp builders.
- It runs on Weekly Active User volume — high-WAU/low-revenue extensions
  donate traffic to high-revenue extensions; revenue is split.
- Rollout was "currently being deployed to many products" as of the final
  call (late 2024).

**What Lesson 243 does NOT verify:**
- **The "8% fee" cited in SKILL.md is the Paywall fee, NOT ExtNet's.** Lesson
  243 line 953: *"Мы берём сейчас 8 процентов, раньше было 10, сейчас
  продолжаемо снижать 8 процентов, значит, от вот этого оборота. Чисто как
  комиссия Paywallа."* — The 8% is explicitly labelled "чисто как комиссия
  Paywallа" (purely Paywall commission), not ExtNet.
- ExtNet's revenue split %, minimum WAU to participate, payout cadence,
  and exclusion rules are **NOT in Lesson 243.**

**TODO(operator): The "8% ExtNet fee" in SKILL.md is incorrect attribution.**
Fix one of two ways:
1. Update SKILL.md to clarify: *"Paywall takes 8% of revenue; ExtNet terms
   are negotiated separately with the studio — not published in bootcamp."*
2. Email curators for current ExtNet terms (rev-share %, min WAU, payout).

Until clarified, do NOT promise "8% ExtNet" to operators — only "8% Paywall."

### Tier-1 allowlist enumeration (gap backfill from Modules IV + V)

The bootcamp Tier-1 set IS explicitly enumerated, in Lesson 182
(html-extracts, Module IV — *"Зачем запускать платную рекламу"*):

> *"Как мы помним, нашими целевыми пользователями являются люди из TIER1
> countries (США, Канада, ЕС и т.д.) - именно они делают внутренние покупки
> с адекватной конверсией."* (Lesson 182, line 6)

Translated: **"Our target users are people from TIER1 countries (USA, Canada,
EU, etc.) — they are the ones who make in-app purchases at an adequate
conversion rate."**

The "и т.д." (etc.) is intentional — Lesson 182 does NOT close the set. UK
and AU are inferred from standard CWS practice but are NOT explicitly
enumerated in Module IV. Lesson 243 corroborates US/Canada/EU spend behavior
throughout (lines 332–333, 689–693, 745–747) without enumerating the full
set.

**Effective bootcamp Tier-1 allowlist (Lesson 182 explicit + studio operator
practice):**

```
EXPLICIT in Lesson 182:
  US, CA, all EU member states

OPERATOR-STANDARD (used by studio but not in Lesson 182's enumeration):
  UK, AU, NZ, CH, NO, IS  (English-speaking + non-EU European wealthy)

CURRENT SKILL.md WORDING ("US/UK/CA/AU + EN-EU"):
  Aligns with operator-standard; UK + AU are inferred from "etc." not explicit.
```

**Recommended canonical list for paywall geo-filter:**

```js
const TIER_1_PAYWALL_ALLOWLIST = [
  // Lesson 182 explicit:
  "US", "CA",
  // EU member states (Lesson 182 "ЕС" = EU bloc):
  "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE",
  "IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE",
  // Studio operator-standard additions (NOT in Lesson 182):
  "GB","AU","NZ","CH","NO","IS"
];
```

**Decision rule:**
- Default paywall geo-filter = above list.
- If the studio Paywall has its own published Tier-1 set, **use the Paywall's
  set as source of truth, not this list** (the Paywall is the bootcamp's
  reference implementation per Lesson 243 lines 660–662).
- Never paywall outside this set without first measuring per-country
  conversion (Lesson 243 line 837 mentions custom geo targeting is available).

TODO(operator): confirm UK + AU explicitly with curators. Lesson 182 only
enumerates "США, Канада, ЕС и т.д." — UK/AU are operator inference. If a
later bootcamp lesson enumerates the full set, replace the operator-standard
section above with the verified list.

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

