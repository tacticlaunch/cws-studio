# Stage 4 — Paid promotion & optimization

After publishing, buy the first 100–300 users to break the cold-start loop, then
let organic SEO take over.

## Why paid ads (the theory — read before configuring)

User count is a ranking factor: more users → higher ranking. At launch you're in
a loop: no users → low ranking → fewer users find you. Buy the first **100–300
users** via Facebook / Google / Yandex Ads to break it.

- Your **paying** audience is **Tier-1** (US, Canada, EU) — they convert on
  in-app purchases.
- But buy **cheap-country** installs (CIS, Asia, Africa) — ~3–10¢ per install.
  The algorithm boosts an extension worldwide (incl. Tier-1) once *any* live
  users appear. So don't overpay for Tier-1 ads.
- You buy paid users **not to earn from them** but to help Tier-1 users see you
  in organic search.
- Do this **once**, right after the extension appears in CWS. Each extra paid
  dollar is worth less. Builders spend on average **$30–150** (≈100–300
  installs); **don't exceed $300** — if organic doesn't follow, launch a
  different product instead.
- First organic traffic usually appears **1–2 months** after launch; 10–20
  organic installs/day after 2 months is a good result; full SEO power comes
  ~**6 months** in. Roughly **1 in 2** products get users, **1 in 3** get
  subscriptions — so launch a 2nd/3rd product rather than waiting.

## Which platform

| Platform | Plus | Minus | RU/BY access |
|---|---|---|---|
| **Facebook Ads** | unlimited audience reach | feed ads — user didn't ask, reacts worse; best for simple obvious products | strongest blocking of RU/BY advertisers — **not worth it from RU/BY** |
| **Google Ads** | ads in the same SERP as organic; user initiated the query | limited traffic volume on some queries | needs a foreign photo-ID document; ~95% of RU/BY builders pass with ID + foreign card + clean account + antidetect; ~30% aren't asked for documents at all |
| **Yandex Direct** | same as Google Ads | mainly CIS traffic — *not* a downside (live traffic from anywhere boosts worldwide) | works without restrictions |

Recommendation: run at least 1 platform, ideally test 2. Abroad → any of the
three. In RU/BY → start with **Yandex Direct**, optionally try Google Ads.

## Built-in Google Analytics

In the developer dashboard → your extension under **Items** → scroll to **Opt in
to Google Analytics**. Data shows after 24h; you can configure/launch ads
immediately.

## Facebook Ads (skip if in RU/BY)

**Facebook Page** — required to run ads, but ads barely drive traffic *to* it, so
don't over-invest. Its name + avatar appear in every ad post → make the name
general/simple/clear and the avatar contrasting. Add 1–2 topical posts so the
page doesn't look empty to moderation.

**Business account** — business.facebook.com/select: create a business, confirm
email, attach the Page, create an Ad Account, add yourself with max rights, set a
Payment Method with a foreign card and a matching foreign timezone. FB often
blocks new ad accounts on a false-positive — usually fixed by uploading a foreign
passport.

**Creatives** — FB initiative is *ours*: the user didn't ask. Write the clearest
possible text and banner; ignore SEO here, just get noticed/understood. Three
texts: **headline** (≤1 line — just the product name), **primary text** (≤2 lines
— product gist + one benefit), **description** (≤1 line). Simpler beats clever. A
reliably-working benefit for products built by this method: *"Simple <product
name>. Works in 2 clicks right in your browser."* Two banners per ad group:
square **2048×2048** and rectangular **1280×800** (reuse the CWS large banner),
**static, not video** — video underperforms.

**Campaign** — adsmanager.facebook.com. Optimize for **clicks**. Two ad groups:
(1) **no interests**; (2) **with interests** matching your topic (only if the
product is niche — e.g. JSON Formatter → programmers; skip this group for
universally-useful products). Each ad group: 2 ads (square + rectangular
creative). Add `?hl=en` to the extension URL.

After launch, **monitor comments** on ad posts and hide toxic ones ("you're
advertising a virus/scam") — visible hate raises click cost and risks losing the
account. Stop FB installs ~3–5 days after launch; most builders spend $30–90.

## Google Ads

**Texts**: 3 headlines (≤30 chars each — one of them the full product name), 3
descriptions (≤90 chars — rewrite the CWS short description via ChatGPT `correct
this text` for *people*, not search), display path (≈product name), 4 sitelinks
(≤25 chars), 4 callouts (≤25 chars). Sitelinks point at the same extension with a
unique `&sl=...` parameter; callouts are non-clickable sitelinks. Sitelinks +
callouts exist to make the ad bigger → more noticeable.

Avoid in ad text: exclamation marks in headlines; 2+ `!`/`?` in body; repeated
punctuation; odd symbol/number use (`@home`, `4sale`); superscripts; non-standard
symbols (asterisks, bullets, ellipses); emoji. Avoid words `download`, `free`,
`trial` to not provoke extra moderation. If the product name reads like a
sentence (`Convert HEIC to JPG`), put the name into the Descriptions too.

**Campaign**: ads.google.com → create account **without a campaign** (pro mode) →
matching timezone → attach foreign card → create campaign → Goal: Purchase or
Page View → extension URL with `?hl=en` → focus on **clicks** with a max
cost-per-click. Set **your own keywords** — Google's defaults are often
irrelevant; the best source is the keyword list gathered for the description in
Stage 2.

**After publishing the campaign** (these settings appear only post-publish):
- Lower the **mobile + tablet bid adjustment to −100%** — mobile users can't
  install extensions and would burn the budget.
- Add **negative keywords** — competitor brand terms (e.g. `DuckDuckGo`,
  `uBlocker`) so you don't pay for irrelevant traffic.
- In **Settings**, confirm Bidding = **Maximize clicks** with your max CPC.

Stop Google installs ~5–10 days after launch; most builders spend $30–90.

If moderation rejects the campaign citing **Free Desktop Software Policy** (a
false positive): don't use Appeal/Edit Ad — click **Read Policy**, find the
**Authoritative Distribution Site** registration form, and submit it. In the
extra-info field write that you promote a free Chrome extension hosted on the
Chrome Web Store (`chromewebstore.google.com`, owned by Google, an authoritative
distribution site). Field tips: End Customer Company Name → CWS domain; country →
the country you pay from; Your Company Name / Name of the Software → product
name; distribution domain + download link → CWS; "software publisher?" → Yes;
"free trial of paid software?" → No; verify the Google Ads Customer ID. Review ≈
1 day.

## Yandex Direct

**Keywords**: at wordstat.yandex.ru, build a list of **5–30 target phrases**
(more total traffic = better). Start from the Stage-2 keyword list but rethink it
in Russian — a literal translation often misses better Russian queries (`web to
pdf` → not literal `веб в пдф` but `сохранить страницу в pdf`).

**Campaign**: register at direct.yandex.ru → switch to **Директ Про** (extended
interface) → Add → Company → Мастер кампаний → expert mode → add extension URL
with `?hl=ru` → configure campaign and ad group. Quick links = same extension
with a unique `&sl=...` param; clarifications = non-clickable quick links — both
just enlarge the ad. Top up **3,000–4,000₽** for the first run (a small budget
limits damage from first-time mistakes). Ads/budget don't run until moderation
passes. In **Ставки и фразы**, raise bids gradually (every 5–10h, ~5–15₽) until
impressions/clicks start.

## UTM tags

UTM tags label each ad so analytics can attribute traffic per ad. Minimum per
platform:
- Facebook: `utm_source=facebook&utm_medium=cpc`
- Google: `utm_source=google&utm_medium=cpc`
- Yandex (campaign level, dynamic):
  `utm_source=yandex&utm_medium=cpc&utm_campaign={campaign_id}&utm_content={ad_id}&utm_term={keyword}`

Add `utm_campaign` and a per-ad `utm_content` to tell ads apart (Tilda's UTM
generator helps build long tags). Example:
`utm_source=facebook&utm_medium=cpc&utm_campaign=adblocker_interests&utm_content=1`.

## Analyzing installs — Google Analytics

Dev dashboard → **Go to Google Analytics** → Reports → Engagement → Events.
Key events: `first_visit` = unique users reaching the CWS page (**important**);
`install` = installs (**important**); `page_view` / `session_start` /
`user_engagement` = less important. **Conversion to install** = `install` ÷
`first_visit`. Normal conversion is **15–30%**.

FB ads quirk: after moderation FB sends **bots** to your CWS page (to check you
didn't swap the page) — they don't install. Create a segment excluding bots
(they usually visit from Linux). GA data is unreliable lately and ~1 in 5 times
doesn't load at all.

**If GA shows nothing**: in the dev dashboard, **Installs & Uninstalls** —
compare install counts on ad days vs. non-ad days (an uptick during weekends/
holidays, when installs normally dip, indicates ads worked); **Impressions** —
see views via your UTM tags. Rough conversion: `(installs − baseline_daily ×
days) ÷ clicks`. You don't need precision — just confirm ads gave a lift and
reach 100–300 installs.

## Umami Analytics (real-time alternative)

GA lags; Umami is real-time. Sign up at cloud.umami.is/signup, follow the docs,
and put the **tracking code on the Welcome Page** — since the Welcome Page opens
once per install, a unique visit ≈ an install. On a Tilda Welcome Page, add an
HTML block with the Umami code, save, re-publish.

## Reviews

Rating + reviews strongly affect ranking. Users who are satisfied rarely write
reviews; dissatisfied ones do. **"When haters type, grateful users stay
silent."** Don't let this distort your read of the product.

**Review widget** — add a rating widget to the extension UI: 4–5 stars → redirect
to the CWS review page; 1–3 stars → redirect to a Google Form where the user
vents directly to you (no public CWS review). Ready HTML/CSS star widget:
`references/review-widget.html` — swap in your CWS reviews URL and Google Form URL.

**First reviews** — add **4–5 reviews from real people** at launch. **Never write
your own reviews** (even from different accounts) — Chrome fights bot-driven
extensions. Ask 4–5 friends/relatives to leave English reviews, **max 1–2/day,
from different devices**, no VPN/proxy. Pro alternative (for those who launch
extensions professionally): ProfitTask — top up ~100₽, create a task ("open the
link, log into Google, in Reviews leave 5 stars + a short review in your own
words"), shorten the link (cutt.ly), price ~6₽, **limit to 1–2 reviews/day**,
manual screenshot verification, fund the task for only 1–2 completions at a time,
rewrite the review template each day so reviews aren't identical.

## Video-lesson nuances & mistakes

### Reading CWS / GA analytics correctly

- The CWS built-in Google Analytics measures **only the listing page**, not the
  extension. The **only** trustworthy metrics: `users` (weekly users *of the
  extension* — the one real extension metric), `install`, `first_visit`.
- **Ignore "Active Users", bounce rate, session length** — GA is built for
  websites; on a listing page a *fast exit is good* (the user understood quickly
  and went to install), yet GA flags it as a bounce. These metrics are noise.
- **Filter Facebook bots before computing conversion.** After moderation FB
  floods the listing with bots (you don't pay for them; they don't install).
  In GA create a segment with **Operating System "doesn't contain" Linux** —
  bots mostly come from Linux. Conversion on *real* first-visits is far higher
  (e.g. 5% → 15%).
- **Data lags:** the listing user counter lags ~5–7 days; the dev-console
  internal analytics ~2–3 days; UTM reports ~3–4 days. ~1 in 5 products has
  broken analytics — cross-check via a Welcome Page analytics counter.

### Ad-platform behavior

- **Ignore the platforms' "optimization recommendations."** FB/Google suggest
  filler (extra keywords, "add Chrome Web Store to the ad") from generic ML —
  irrelevant to this method, sometimes lowers CTR. Do only the minimal manual
  setup from this reference.
- **Yandex Direct vs Google Ads** (detail): Google has a far bigger, cheaper-
  click audience (access to cheap Asia/Africa), faster traffic onset, reacts to
  bid changes within ~3–4h, but can ban accounts and sometimes refuses to show
  ads where organic already satisfies the query. Yandex always shows if you pay,
  never blocks, simpler setup, but is slower — change bids only every ~half day.
- **Don't delay ads.** Run them right after launch (once bug-free) — ads act as
  **social signals**: Google sees users arriving without it and trusts the
  product more. After Google indexes you, social signals matter less. The first
  days post-launch are when Google's invisible tests run — fix bugs *now*.
- **More keywords beats higher bids.** To grow paid traffic, first add keywords —
  think how people search *indirectly* (`save site`, `print site` for a
  web-to-PDF product). Raise bids only "within reason" (~30–50₽) until traffic
  flows, then lower them — warmed campaigns keep delivering cheaper.

### Warm the ad account before launch

While the extension is in moderation, build the ad (text + graphics) and point
it at a **competitor's** URL with a tiny budget (~300₽) to warm the campaign.
When your product goes live, just swap the link — ads start instantly instead of
sitting in a launch-to-ads gap.

### Google account management

Multiple Google accounts are allowed; run them all from **one antidetect + proxy
profile** (many accounts per profile). Don't change the proxy often — buy it for
a long term and let the browser fingerprint warm up; risks fade over time.
Google Ads accounts ban easily (unlike CWS) — follow the Free Desktop Software
appeal steps exactly and don't over-appeal.

## Case-study insights from product reviews

### Why / when paid ads — additions

- **Run paid traffic immediately after listing live, not later.** The first
  ~24–72h post-launch are when Google runs invisible behavioral tests; delay
  ads or ship with bugs and those tests bake in a *bad* baseline — fixing bugs
  a month later is too late.
- **Don't over-tune CTR.** CTR is a vanity proxy; only `cost_per_install =
  clicks_to_install_conv × CPC` matters. Saving 1000₽ by 2 days of negative-
  keyword tweaking is a bad time trade-off.
- **Skip ads entirely on some products.** If both Google Ads accounts get
  banned and Yandex doesn't fit, ship without ads — products still grow
  organically; ads only *raise* the odds.
- **Stop tweaking once unit economics work.** If install ≈ $0.30 and you only
  need 100–200, let it run. Don't chase a better CTR.

### Facebook Ads — additions

- **Avoid unverifiable claim language** ("developers are shocked", "9 of 10
  devs make this mistake", unsourced statistics). First false-positive
  moderation flag is recoverable; the second can kill the ad account.
  Rhetorical questions are fine.
- **Don't reuse the CWS large banner as the FB rectangular creative.** A
  purpose-built FB banner is often higher-contrast — the CWS banner has to
  coexist with the icon/screens, the FB version can drop the logo and enlarge
  the product screenshot.
- **In the FB headline, just put the product name.** Pithier benefit lines can
  also work, but bare name often beats a clever one-liner.
- **Normal FB impression→click is 0.2–1%** (one-time spikes to 1.5%);
  **click→install is 10–20%.** Don't panic at 0.5% CTR — it's the median.

### Google Ads — additions

- **Multiple ad accounts banned at once is normal.** Some builders give up on
  Google Ads and run only Yandex. The Free Desktop Software appeal only works
  via Read Policy → Authoritative Distribution Site form; mis-submitting or
  re-appealing repeatedly is a fast path to permanent ban.
- **Normal Google Ads impression→click is 10–15% (max ~25–30%)**;
  **click→install 10–20%** — much higher than FB because the user typed the
  query themselves.
- **`app` is a safe keyword** in ad text; only `free`, `download`, `trial`
  trigger Free Desktop Software false-positives. `up` as a substring (e.g. in
  a product name) has caused false-positives.

### Yandex Direct — additions

- **Don't upload graphics with embedded buttons/UI elements** — Yandex
  rejects them. Yandex shows no images in search ads anyway, so skip image
  upload entirely.
- **The bid you set is a *cap*, not the price.** Actual CPC sits well below
  the cap (5₽ cap → 3.5₽ paid). Don't fear setting 10–20₽ caps; nothing will
  spend at that level if the auction is cheaper, and you won't overrun the
  daily budget.
- **Auto-targeting is a separate row.** Even if you set keyword bids,
  auto-targeting bid stays at minimum unless you explicitly select it in
  "Мастер ставок" with a manual bid. Forgetting this caps your traffic for no
  obvious reason.
- **Bid changes propagate slowly in Yandex — wait 5–10h between bumps; 3–5h
  in Google.** Bump up in 5–15₽ steps until traffic flows, then *lower* —
  a warmed campaign keeps delivering at a lower bid.
- **Daily budget cap of 10,000₽ is safe** — even with high bid caps Yandex
  rarely burns it during ramp because the auction doesn't price that high.
- **Reasonable max-bid ceiling: ~30–50₽.** Beyond that, find more keywords
  rather than raise bids.

### Keywords & translations (paid side)

- **Two keywords in name is OK on non-English locales, not OK on English** —
  low competition makes overspam penalties less aggressive on national
  languages.
- **10× volume rule for picking national vs English name keywords.** If the
  national keyword has at least 10% of the English keyword's volume, combine
  both with `−` or `|`. If less, drop to English only. If only national
  exists, drop to national only.
- **When Semrush shows 0 traffic on a national keyword, cross-check Yandex
  Wordstat in Russian for an *analogous* pattern**, then apply the pattern to
  the target language. Semrush systematically under-reports national-language
  volumes; Wordstat does not.
- **For zero-data locales, scrape competitor sites in that locale** (open
  them in the target country's Google SERP) and copy the phrasing they use —
  better than blind ChatGPT translation.
- **Don't make two locales identical** (e.g. Russian copy in the Ukrainian
  slot). Identical localized pages pessimize *both* via duplicate detection —
  worse than leaving one untranslated.
- **Keep English keywords visible inside national-locale descriptions** by
  quoting them in the translation prompt: `translate to Italian. Do not
  translate words in quotes`. Strip quotes afterward.
- **Localized screenshot uploads only pay off after you see real traffic
  from that locale** — hand-work not worth it until conversion data justifies.

### UTM tags

- **Yandex/Google "organic search" buckets in GA bleed paid traffic** — the
  GA4 acquisition source split is broken for CWS listings. Don't segment by
  source in GA at all.

### Analytics / metrics — additions

- **CWS built-in GA only measures the listing page**, not the extension. The
  single exception: the `Users` (weekly users over time) graph — the only
  real-extension number GA gives you. Everything else (Active Users, bounce,
  session length) is listing-page noise.
- **GA4 source attribution (Organic / Direct / Paid / Referral) is broken
  since the GA4 migration** — paid traffic shows up as organic, direct counts
  are impossibly high on new products. Don't read paid-vs-organic from this.
- **Compute conversion as `install / first_visit`, not `install / page_view`** —
  `first_visit` is the only trustworthy unique-user metric.
- **Listing-page bounce rate is inverted vs websites** — a fast exit means
  the user understood quickly and clicked Install. GA flags it red; ignore.
- **GA timezone is San Francisco** — comparing Yandex/Google Ads stats with
  GA will show phantom misalignment up to half a day. Don't reconcile by date.
- **GA tail-lags 2–3 days; the last 2 days are always incomplete.** Don't
  draw conclusions from "yesterday's zero".
- **For real product-internal analytics use Amplitude (preferred) or Mixpanel
  for extensions; Yandex Metrica for site-shaped extensions.** Don't bolt
  internal-event tracking onto CWS-provided GA — it can't see inside the
  extension.
- **Welcome-page-as-install-proxy**: put a separate Yandex Metrica counter on
  the Welcome Page; unique visits ≈ installs, with no GA lag.
- **In the dev dashboard, the per-country install CSV refreshes faster than
  the per-country users CSV** — use Installs for daily geo readings, Users
  only for slow trend tracking.
- **First weekly users counter on the listing lags ~5–7 days; users-by-
  country chart lags even more; install-by-country comes in fastest.**
- **Real conclusions about whether a product "works" need ~2 months;
  "is it growing" needs ~6 months; finals at ~1 year.** Don't kill or pivot
  earlier on metric noise.

### Reviews — additions

- **The star widget works through camouflage, not stars.** Label it "Rate us"
  and clickthrough collapses. Label it as a passing rating prompt with empty
  stars and the "unfinished task" reflex triggers massive click volume into
  the CWS review page — only ~1–2% of those click-throughs actually write a
  review, but absolute volume produces the 4–5⭐ average.
- **Static rate widget is weaker than event-triggered.** Show the prompt
  *after* a successful action (e.g. 5th use), in a full tab or sidebar with
  stars — review conversion jumps significantly.
- **ProfitTask (paid review service) is currently broken** — site up but
  tasks don't complete. Rely on 4–5 real friends, max 1–2 reviews/day, no
  VPN.
- **Never accept reviews that link to competitor extensions** (rare in
  practice). Respond politely if it happens; you can't delete reviews.
- **Hate reviews are a chance to demonstrate adequacy.** A calm, grammatically
  correct, on-substance reply out-performs no reply. The bad review stays;
  the *reply* converts the next reader.

### Conversion diagnostics — common low-conversion patterns

- **Filter Facebook bots out of CWS GA before computing conversion.** FB
  moderation-check bots flood the listing from Linux. Build a GA segment
  with `Operating System doesn't contain Linux` (exact casing). Real
  conversion often jumps **3×** after the filter.
- **Yandex/Google paid bots can't be filtered** — they look like real users
  in GA. Accept some noise.
- **Welcome-page screenshot too small = users click it.** Cropped tightly
  enough that it stops looking like a screenshot of *a browser*, users
  mistake it for live UI and click the image instead of finding the puzzle
  icon. Keep enough browser chrome visible, prefix a colon label ("Click on
  the extension icon:") above it, and enlarge the in-screenshot UI
  artificially (text 3× larger than reality) so it reads at thumbnail size.
- **Don't blur text inside Welcome-Page screenshots** — users read blur as
  "something hidden", not as "ignore this". Use skeleton bars or real
  placeholder text instead.
- **Filled, solid-color toolbar icons outperform line-art/outline icons.**
  Translucent or pattern-filled icons get lost against other browser icons;
  reinstall conversion suffers because returning users can't find them.
- **If the extension adds a widget to existing pages (YouTube, etc.), the
  widget MUST appear on pages opened BEFORE install** — otherwise users
  follow the Welcome Page instructions, can't find the widget, and
  uninstall. Either inject into pre-existing tabs via content scripts, or
  explicitly tell users to reload the tab.
- **Draggable widgets that only appear after page reload are conversion
  killers** when the Welcome Page points at them. They must show without
  reload.
- **Don't auto-detect interface language by browser locale + content** —
  auto-detection mis-fires (e.g. types a Latin word, gets Japanese TTS).
  Let users pick.
- **Auto-translation tools translate only `appName`, `shortDesc`,
  `storeDesc`** — every other `messages.json` key (button labels, tooltips)
  stays untouched. After auto-translate, manually add every other key to the
  *default English* locale or buttons render empty.
- **A missing localized string falls back to the default English value**,
  not to that language's locale — so you only need to populate non-default
  languages where you actually want different copy.
- **Watch for CSS conflicts when injecting into ChatGPT/Gmail/etc.** — host
  site styles override your widget (white text on white). Use Shadow DOM or
  scoped selectors.
- **Normal uninstall rate is 15–30%**; the most monetizable observed
  product had 40% uninstall — high uninstalls aren't disqualifying if
  paying users pay more.
- **Healthy listing→install conversion: 15–30% organic, 10–20% from ads, FB
  on the low end.** 12% from Yandex traffic is normal, not a problem.
- **Don't crop browser chrome out of Welcome-Page screenshots** — leaving
  full browser visible (with the screenshot region highlighted) is what
  makes the user recognize "ah, a screenshot" rather than "this is the UI".
- **Permissions with alerts (`<all_urls>` etc.) cost ~30–40% of existing
  users on update** — bake any future-needed alert-permission into the v1
  manifest, before you have users to lose. On a 100-user product losing 30
  is nothing; on a 100k product losing 40k matters.

