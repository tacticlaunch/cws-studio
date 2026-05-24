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

## Seeding reviews when ProfitTask is broken — operator workflow

(Source: Module IV review-walkthrough lesson 203 "Разборы ошибок — ЧАСТЬ 1"
explicitly confirms ProfitTask "doesn't work, the site is up but people in
Telegram complain it's broken." The lesson redirects everyone back to
real-friend reviews for the first launch. Module IV lesson 202 "Добавляем
первичные отзывы" is the canonical ProfitTask walkthrough — kept here as
the on-disk reference even though the service is currently broken.)

**Default path for V1 (what playbook actually recommends right now):**
1. Recruit **4–5 real people** — relatives, friends, anyone willing to log
   into their own Google account.
2. Each leaves an English review on the CWS listing, **max 1–2 per day per
   account, distributed across multiple calendar days**, from **different
   physical devices**, **no VPN / no proxy / no antidetect**.
3. Rewrite the review template every day so reviews don't look templated.
4. The first reviewer can be you — but only one, only from your own real
   account on your real device, and only the very first review.

**ProfitTask (currently broken — keep as future-restore path):** see the
existing "Reviews" section above for the full setup (~6₽ per task, 100₽
top-up, manual screenshot verification, 1–2 reviews/day cap, rewrite
template each day). When the service comes back online this is the
"professional launchers, multi-product" workflow.

### kwork.ru workflow — alternative seeding channel

> **TODO — not covered in source transcripts; pattern from operator
> practice. The playbook explicitly lists ProfitTask as the only
> paid-seeding tool, and currently broken. The kwork.ru pattern below is
> documented from external operator playbooks for parity, not from the
> source transcripts.**

The pattern, when used externally:
1. **Task wording.** Post a "Микрозадание" / micro-task: "Open the
   shortened link, sign into your own Google account, leave 5 stars and a
   short organic review on a Chrome extension." Provide the shortened
   `cutt.ly` link plus a 1-sentence review-seed the executor should
   rephrase in their own words.
2. **Price band.** ~6₽ per completed review on the Russian platforms
   (mirrors the ProfitTask price band documented in lesson 202). On
   kwork.ru proper, tasks typically start at 500₽ for a small batch
   (5–10 reviews) — significantly more expensive per review than
   ProfitTask, which is why playbook doesn't recommend it as the default.
3. **Distribution via Telegram (when on-platform tools fail).** Post the
   task spec + shortened link into Russian-language micro-task Telegram
   channels (look for `@microtask`-style groups). Cap incoming reviews at
   1–2/day via manual approval to avoid the rate-spike that triggers CWS
   bot-review detection.
4. **Verification.** Same as ProfitTask — request a screenshot of the
   posted review, manually approve, top up the task for only 1–2 more
   completions at a time.
5. **Same hard rules apply:** no VPN, no proxy, different devices, English
   reviews only, rewrite template daily.

Because kwork is not validated in the playbook transcripts, treat it as a
fallback when ProfitTask is down and your friend network is exhausted.
The default for V1 stays: **4–5 real-friend reviews**.

## install_id propagation pattern

> **TODO — not covered in source transcripts. The playbook recommends
> Amplitude (and falls back to Mixpanel) for popup/local-page extensions
> via the Measurement Protocol pattern (lessons 177 "Нюанс 27" and 221
> "Нюанс 11"), but never documents a specific user-id generation scheme.
> The pattern below is the working operator pattern — use it to tie
> Welcome Page first-visits to downstream in-extension Amplitude events
> without auth.**

The problem the pattern solves: the Welcome Page opens once per install
(perfect install-counter), but the events fired *inside* the extension
(activation, paid action, retention return) come from a different origin
and have no shared cookie or session. Without a stable user-id, Amplitude
sees the Welcome Page visit and the in-extension events as two unrelated
users — the funnel splits in half.

The fix: generate a UUID on first Welcome Page load, persist it in
`localStorage` on the Welcome Page **and** mirror it into
`chrome.storage.sync` from the extension, then pass it as the user-id on
every analytics call from both sides.

**Welcome Page side** (the page opened by `chrome.tabs.create` in the
service-worker `onInstalled` handler):

```javascript
// Welcome Page — runs once on first install (page opens once per install)
let installId = localStorage.getItem('cws_install_id');
if (!installId) {
  installId = crypto.randomUUID();
  localStorage.setItem('cws_install_id', installId);
}

// Pass installId as user_id to every analytics call from the Welcome Page
amplitude.setUserId(installId);
amplitude.track('welcome_page_view', {
  install_id: installId,
  // utm_* params from the install referrer if available
});
```

**Extension side** (popup / sidepanel / content script):

```javascript
// On first activation, read the installId out of the Welcome Page's
// localStorage via a content script injected onto the Welcome Page URL,
// then persist it in chrome.storage.sync for cross-device continuity.
async function getOrCreateInstallId() {
  const stored = await chrome.storage.sync.get('cws_install_id');
  if (stored.cws_install_id) return stored.cws_install_id;

  // Fall back: mint a fresh UUID inside the extension if the Welcome
  // Page handoff failed (rare, but happens when users clear site data
  // between install and first activation).
  const fresh = crypto.randomUUID();
  await chrome.storage.sync.set({ cws_install_id: fresh });
  return fresh;
}

// Pass it as user_id on every Amplitude / GA4 event from the extension
const installId = await getOrCreateInstallId();
amplitude.setUserId(installId);
amplitude.track('feature_used', { install_id: installId });
```

**Why `chrome.storage.sync` not `chrome.storage.local`:** sync survives
profile resets and follows the user across Chrome installs on other
devices — the retention story stays intact even when the user reinstalls.
The behavioral-factor case for `sync` over `local` is already documented
in the cws-launch assets-and-publish.md "Behavioral factors — additions"
section.

**Why mint client-side, not server-side:** no auth at launch (per the
"60–80% activation drop" rule from lesson 170 "Нюанс 20"). A
client-generated UUID gives you a stable user-id without a sign-in flow.

## 1000-install milestone benchmarks

> **TODO — not covered in source transcripts at the per-milestone level.
> Module IV sources finish around the 100–300 install range (the cap
> set by the $30–150 paid-promo budget). Module V "Финальный созвон"
> (lesson 243) and the Module IV group call (lesson 181) reference
> products with thousands of users in passing but do not enumerate
> healthy benchmarks at 1000 installs specifically. The numbers below are
> the working operator pattern, calibrated to the playbook's stated
> overall conversion bands.**

By the time an extension crosses **1000 cumulative installs**, the
behavioral factors that determined whether organic SEO would kick in
have already played out — at this point you're reading the trend, not
the launch. Healthy benchmarks at this stage:

| Metric | Healthy band at 1000 installs | Source |
|---|---|---|
| **Weekly retained users** (from CWS dashboard `Users` graph) | ≥ 60% of installs from the same 28-day window (so ≥ 600 if the 1000 came in over the last month) | Inverse of the "normal uninstall rate 15–30%" band from the existing "Conversion diagnostics" section above; sources do not state the retained-user benchmark directly |
| **Organic share of new installs** | ≥ 50% (paid spend is capped at $30–150 → ~100–300 paid, so anything past install ~300 is organic by definition) | Derived from the playbook's $300 paid-spend ceiling rule |
| **Review count target** | 5–10 organic reviews + your initial 4–5 seeded = 10–15 total at 1000 installs | Pattern from the "review widget converts ~1–2% of users to actual reviewers" insight in the existing "Reviews — additions" section |
| **Average rating** | ≥ 4.5★ (review widget filters 1–3★ to your Google Form, so public CWS reviews skew 4–5★ by design) | Mechanical consequence of the review widget — see the existing "Reviews" section |
| **CWS listing-page conversion** (`install / first_visit`) | Stable 15–30% organic, 10–20% from ads — should not be degrading | Existing "Analyzing installs" section |
| **Listing-page weekly user count growth** | Week-over-week growth ≥ 10% | The playbook's "10–20 organic installs/day after 2 months is a good result" baseline |

**What 1000 installs unlocks:**
- **Monetization is now safe to add** for products with running costs —
  enough volume that the paying tail can cover infra (recall: playbook
  states ~60% of paying purchases come from US across all playbook
  products — lesson 181). At sub-1000 the paying tail is too sparse to
  read signal.
- **Add the flaticon attribution** to the listing (required by flaticon
  TOS — the existing "Icons — additions" section says to skip it at 0
  users and add it after ~1000).
- **Switch from monitoring-by-install to monitoring-by-retention** — the
  CWS `Users` graph (weekly users) becomes the primary metric instead of
  the install counter.

**What 1000 installs does NOT unlock:**
- Real conclusions about the product. Per Module V lesson 243, the
  playbook position is: ~2 months for "does it work", ~6 months for "is
  it growing", ~1 year for finals. 1000 installs hit before any of those
  windows for healthy launches.
- A second product launch from the same operator account on the same day
  — see the "Second-platform unlock criteria" section below for the
  unlock gate.

## Second-platform unlock criteria

> **TODO — not covered in source transcripts as an explicit gate.
> Module IV source lesson 182 "Зачем запускать платную рекламу"
> recommends testing 2 ad platforms but does not formalize a CPI-stability
> trigger for "platform 2 is safe to add." The criteria below are the
> working operator pattern, calibrated to the playbook's stated 100–300
> install paid-spend window.**

**Default position from playbook:** run at least 1 ad platform, ideally
test 2 in parallel from day 1 if budget allows (Yandex + Google, or FB +
Google depending on geo / RU-BY status). The "test 2 platforms" stance is
explicit in lesson 183.

**Operator gate for adding a second platform *sequentially* (when budget
or account-warming forced a single-platform start):**

A second ad platform is safe to add when the first platform has cleared:
- **≥ 100 installs** attributed to the first platform.
- **CPI variance < 30% over a 7-day window** (compute as
  `(max_daily_CPI − min_daily_CPI) / mean_daily_CPI` over the last 7
  days of spend). If CPI is still bouncing 2–3× day to day, the first
  platform's targeting / bid / keyword setup is not stable yet — adding
  a second platform now just splits attention across two unstable
  campaigns.
- **GA listing-page conversion ≥ 10%** *after* the Facebook-bot filter
  (see "Conversion diagnostics" above) — confirms ads are reaching real
  users, not just bots. If conversion is sub-10% on filtered traffic,
  the listing itself needs work before more ad channels stack on.
- **No moderation issues open** on the first platform (no pending Free
  Desktop Software appeal, no rejected ads, no payment-method block).
  Adding a second platform while the first is in a rejection queue
  hides which platform is responsible when something breaks.

When all four clear, the second platform's purpose is to **diversify
attribution risk** (one platform banning the ad account doesn't kill the
launch) and **expand reachable audience** (Google's cheap-Asia/Africa
inventory vs Yandex's pure CIS inventory, etc.) — not to scale spend.
Keep the total $30–150 budget intact; split it across both platforms
rather than doubling it.

**What disqualifies a second-platform launch:**
- The first platform is mid-ban or mid-appeal.
- You haven't yet built the basic creative + keyword list (the
  "warm the ad account before launch" workflow assumes you already have
  text + graphics, just pointed at a competitor URL for warm-up).
- You're at <100 installs total — you don't know yet whether the listing
  itself converts; adding a second platform won't fix a listing problem.

## Negative-keyword starter lists per donor category

> **TODO — partial coverage in source transcripts. Module IV lesson
> 235 "Быстрый чекап 3 Оптимизация рекламы" covers the *principle* of
> negative-keywording (only negate keywords that have ≥100–200
> impressions AND are clearly off-topic AND are burning meaningful
> budget — don't waste time negating long-tail noise). The playbook
> does NOT publish per-category starter lists. The lists below are the
> working operator pattern — paste them into Google Ads / Yandex Direct
> as a starting negative list, then prune based on impression data per
> your actual product.**

The point of seeding negative keywords *before* the campaign runs is to
prevent Google Ads' default broad-match from burning the first day's
budget on competitor brand searches that will never convert. Once
impressions start flowing (and you can see what's actually wasting your
spend), use lesson 235's rule: negate only what has ≥100–200 impressions
and is clearly off-topic.

### Adblockers / privacy / tracker blockers

Most ad-tech and privacy-tool brand terms — users searching these are
loyal to those brands, not shopping. Common negatives:
```
adblock plus, adblock pro, ublock origin, ublock, ghostery, privacy badger,
adguard, brave browser, duckduckgo, pi-hole, pihole, adaway, blokada,
disconnect, malwarebytes, kaspersky, bitdefender, norton, mcafee, eset,
1blocker, wipr, adblocker for safari, opera adblock
```

### PDF tools / converters

PDF-reader brands and the "Adobe" ecosystem dominate searches that look
adjacent but don't convert. Common negatives:
```
adobe acrobat, adobe reader, foxit, foxit reader, sumatra, sumatra pdf,
nitro pdf, nitro reader, smallpdf, ilovepdf, pdf24, sejda, soda pdf,
pdf-xchange, pdfsam, pdfescape, evince, okular, preview pdf,
microsoft edge pdf, google drive pdf, pdf to word free, online pdf editor
```

### Screenshot tools / screen recorders

Screen-recorder brand searches eat screenshot-tool budgets. Common
negatives:
```
loom, screencast-o-matic, snagit, camtasia, obs, obs studio, bandicam,
fraps, screenflow, quicktime, zoom recording, teams recording, gif
recorder, screencastify, vimeo record, awesome screenshot, lightshot,
greenshot, sharex, picpick, gyazo, monosnap, droplr, cleanshot,
nimbus screenshot, fireshot, full page screen capture
```

### AI assistants / LLM chat extensions

Major LLM brands; users searching these usually want the canonical
product, not a wrapper. Common negatives:
```
chatgpt, chat gpt, gpt-4, gpt-5, openai, claude, anthropic, gemini,
google bard, bard, copilot, github copilot, microsoft copilot, perplexity,
poe, character.ai, character ai, midjourney, dall-e, stable diffusion,
llama, mistral, you.com, phind, cursor, codeium, tabnine, jasper,
copy.ai, writesonic, notion ai, grammarly, quillbot
```

### Translation / language tools

Translator brand searches. Common negatives:
```
google translate, deepl, deepl translator, microsoft translator,
bing translate, yandex translate, papago, reverso, linguee, wordreference,
duolingo, busuu, babbel, rosetta stone, memrise, lingoda, italki, preply,
itranslate, translate.com, smartcat
```

### Video / YouTube tools

YouTube-adjacent searches and major video platforms. Common negatives:
```
youtube premium, youtube music, youtube vanced, vanced, newpipe,
piped, invidious, freetube, kodi, jellyfin, plex, vlc, mpv, twitch,
tiktok, instagram reels, snapchat, netflix, hulu, disney plus, hbo max,
amazon prime video, peacock, vimeo, dailymotion, rumble, odysee
```

### Email / productivity (Gmail, Outlook, Slack helpers)

Major email/productivity platforms. Common negatives:
```
gmail app, outlook app, yahoo mail, proton mail, protonmail, thunderbird,
mailbird, spark mail, superhuman, hey email, fastmail, zoho mail,
microsoft teams, slack, discord, zoom, google meet, webex, skype, telegram,
whatsapp, signal, viber, wechat, line
```

### Universal negatives (apply to every campaign regardless of category)

```
free download, crack, cracked, torrent, pirated, illegal, hack, hacked,
mod apk, modded, alternative to, vs, review, reviews, comparison, best
free, top 10, list of, what is, how to use, tutorial, course, jobs,
salary, career, internship, training, certification, login, sign in,
sign up, password reset, deleted account, cancel subscription, refund,
unsubscribe
```

**How to apply:**
1. Paste the category list + universal negatives into your Google Ads
   campaign as **Negative Keywords → Campaign-level → Phrase match**.
2. After 3 days of impressions, pull the search-terms report and add any
   query with ≥100 impressions, ≥0.5% CTR, and clearly off-topic to the
   negative list (lesson 235's rule).
3. Do **not** add long-tail negatives proactively — per lesson 235, this
   is a time sink with sub-1000₽ savings. Only negate what's actively
   burning meaningful budget.

