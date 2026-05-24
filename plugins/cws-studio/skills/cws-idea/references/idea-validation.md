# Stage 1 — Idea validation (the 10-step workflow)

Score and rank ideas for launching CWS extensions the way an SEO-driven studio
does. Produce a single ranked **Markdown scoring table** of the candidate
hypotheses plus a short recommendation, in **English**.

Aim for **5–10 hypotheses** before deciding — single-idea requests are fine, but
suggest gathering a few more to compare. Work one hypothesis at a time through
steps 1–9, then compile step 10. Each step yields a **0–10 score** (relative —
compare candidates against each other) or a **gate** (YES/NO that can disqualify
the idea). KD has fixed tiers. See `scoring-rubric.md` for the column set and
output template; `semrush-playbook.md` for exact Semrush reports.

## 1. Source the idea — record only

Find a real CWS extension to base the hypothesis on. A good seed: a theme you
understand, you can tell what it does, and it has **≥10K users**. Exclude giant
brand extensions (Cisco, Grammarly, Avast, Adobe, Zoom…) — their installs come
from brand/budget, not SEO. Browse different CWS categories, use "related
extensions", and CWS search. Take seeds from the *middle* of any sorted list
(page 7/10/20), not pages 1–3, to avoid colliding with other builders.

Any web *service/tool* site (calculator, converter, etc.) can be ported into an
extension; article sites and marketplaces cannot — Google treats those queries
as non-software. Check a service's traffic via similarweb.com.

Record: name, store link, theme, user count, notes.

A good donor is either **≥100K users without a subscription** (monetize later by
ads/resale/sale) or **≥10K users with a subscription** (monetize by in-app
purchases — the highest-converting model on average).

## 2. Revenue potential — score 0–10

Rough heuristics (USD): one-time-sale revenue ≈ users / 10; in-app-purchase
revenue ≈ (users / 100) × $3 (≈1% of Tier-1 users convert at a ~$3 floor).
Crucially, **check whether it sells a subscription** and at what price — products
with paid subscriptions (especially "help me do my job" tools: writing, code,
design) earn far more. Higher subscription price → higher score. Verify via the
store page ("In-app purchases" label) and, ideally, by installing it (some devs
omit the label even though subscriptions exist).

## 3. Reduce to one function + simplicity — gate + score 0–10

Can the product collapse to **one simple function**? **No → drop this
hypothesis.** Two reminders: you may take a *secondary* feature (not the headline
one); an already-simple product is fine to clone (differentiate via name +
optimization later).

Then check for **open-source prior art**: Google `[function] chrome github`
(e.g. `track email chrome github`). Open, un-obfuscated source makes the build
far easier → raise the simplicity score. Score implementation simplicity 0–10
relative to the other candidates.

## 4. Find the name keyword + its volume — score 0–10

The keyword in the name is the ranking lever (~70% of SEO). Use Semrush
`phrase_this` (US database) for **exact US volume** (no long tails);
`phrase_fullsearch` for volume *with* variations; gauge worldwide reach via the
US-share proportion.

Thresholds (US, exact, no long tails):
- **Broad niche** (`site blocker`, `adblocker`, `focus mode`): **≥ 2,000/mo**.
- **Narrow/working niche** (`color picker`, `chatgpt for linkedin`, `crm for
  email`): **≥ 500/mo**.

If Semrush reports ~zero volume for a keyword you suspect has SEO traffic, don't
gamble — prefer a keyword with *confirmed* volume.

**Always generate a candidate set — never evaluate only the user's first guess.**
Expand into 5–8 alternative name keywords with `phrase_related` and
`phrase_fullsearch`, plus: pairing a super-popular word with a niche modifier
(this is how `bing chatgpt` was found), Google SERP terms not owned by
extensions, and ChatGPT synonym brainstorming (`Find 10 synonyms to: site
blocker, block website`). In Keyword Magic Tool, sort by volume and read popular
words in the long-tail column; use Related + By volume for the fattest adjacent
queries. Run `phrase_these` to get volume+KD for the whole set at once and pick
the strongest. The user's first keyword is frequently occupied or red-zone; a
generated sibling often has *better* traffic and a freer SERP.

## 5. Confirm "softness" (non-noisy) — gate YES/NO

The keyword must read as a *software* query. Pull the SERP with `phrase_organic`
(US). Classify each top result:
- **Software** = service sites, mobile apps, plugins/extensions, app round-ups.
- **Non-software (noise)** = article sites, Wikipedia, physical-goods
  marketplaces (Amazon, eBay), directories, classifieds, service listings.

Rule: **>50%** of top results software → soft → **YES (good)**. **>30%**
non-software → noisy → **NO**, drop the keyword. Cross-check with a Google search
via web_search if ambiguous.

## 6. Can we rank for the long tails too?

Inspect long tails (`phrase_fullsearch` / `phrase_questions`). If most variations
are on-topic → good, you capture tail traffic. If the query is **noisy**, count
on the head term *only* and require enough volume on the head alone (e.g. `bing
chatgpt` ranked only for the exact ~14.8K head term).

## 7. Is the keyword occupied by an optimized competitor? — gate (RED FLAG)

Check three ways: (a) Google `[keyword] chrome` — extensions surface first if
present; (b) `phrase_organic` SERP — note any `chromewebstore.google.com`
results, **their position**, open them; (c) the user's own list.

**Position matters: judge occupation by the prime top-10 (especially top-5).** An
extension buried at #19 while page 1 is all websites does **not** count as
occupied — extensions outrank sites for software queries, so those slots are
winnable. (`math ai` had a CWS extension at #7 → occupied; `ai math solver` had
its first extension at #19 → free and winnable.)

A competitor is **well-optimized** if: name **contains all** the same words as
your intended name; description **> 3,000 chars**; **> 30 translations**.
- Owned by a well-optimized extension → **RED FLAG → drop this keyword**, find
  another (the same idea usually has many alternative names, often better).
- Owned only by *un*-optimized extensions (weak name, short description, no
  translations) → still winnable on every query including their head term.

Name nuances: reusing *individual words* an optimized competitor uses is OK
(`site blocker` taken → try `web site blocker`); a **fat unowned keyword from
entirely different words** (`focus mode`) wins with far higher odds. For very fat
queries (`grammar check`), prefer a **niched** variant (`grammar check for
Gmail`) — less traffic is fine, **don't lower the score for niching**.

## 8. Keyword Difficulty (KD) — score by zone

Get KD from `phrase_this` (`Kd`) or `phrase_kdi`. KD mostly describes *site*
difficulty; optimized extensions climb even at very high KD (`bing chatgpt` KD
91, extension ranked #2). All else equal, lower KD is better.

| KD % | Semrush zone | Points |
|------|--------------|--------|
| 0–49 | green / yellow | 10 |
| 50–69 | orange | 7 |
| 70–84 | red | 6 |
| 85–100 | scarlet (very hard) | 5 |

For a *noisy* keyword you only rank on the exact head term regardless of KD.

## 9. Users / popularity proxy — score 0–10

Score the seed's user count 0–10 relative to the other candidates. Don't
over-reward giant brand extensions (already excluded in step 1).

## 10. Compile the scoring table

Sum the numeric scores. Any **RED FLAG / failed gate** (No on step 3, NO softness
on step 5, occupied-by-optimized on step 7) disqualifies that *keyword* — mark it
**DROP**. **But don't declare the whole idea dead just because the obvious head
keywords are occupied:** loop back to step 4, generate fresh candidates, re-check
softness + occupation. Only conclude "no viable name" after that set also fails.

Recommend launching the surviving hypothesis with the **highest total**. If torn
between a fat/high-KD keyword and a niche/low-KD one, the honest answer is **test
both**, but **start with the niche/low-KD one** — if low competition doesn't
convert, high competition won't either.

## Common mistakes (avoid these)

1. **Calling a niche "no money" from one product.** A donor's missing subscription
   label means nothing — judge the **whole industry**: Google the keyword, open
   the top results (sites, mobile apps too) and check their pricing pages. Money
   in the niche anywhere ⇒ don't lower the revenue score.
2. **Treating a noisy keyword as soft.** A keyword can *look* software-y yet have
   an article/blog-heavy SERP. Be strict — weak softness = red flag. Risk it only
   if the product is genuinely trivial to build.
3. **Software SERP, but the wrong software.** The top SERP can be all software
   yet for a *different* function than you intend (e.g. `text replace` SERP =
   find-and-replace tools, not the shortcut-expander you planned). Building the
   wrong software type tanks behavioral factors. Open the keyword's SERP and your
   donor side by side — the software must be the **same type**.
4. **Overcomplicating** (especially as a non-developer). There is **zero
   correlation** between product complexity / dev time and revenue; longer dev
   only lowers the odds you ever launch. Launch the simplest version fast — you
   can always add complexity later.
5. **`free` in the name.** Moderation may reject it; later it attracts a
   non-paying audience and collapses behavioral factors when you add
   monetization. (A little `free` in the *description* is OK — Stage 2.)
6. **Multiple keywords in the name at launch.** Two keywords defocus SEO — each
   loses more than half its weight. Don't add brand names or symbols/brackets
   either. Mixing two keywords is OK only **after** the product is established on
   one keyword (then separate with ` | ` or ` - `).
7. **Adding extras to the name.** Add nothing that isn't in the keyword. The
   three "ubiquitous" CWS words — `Google`, `Chrome`, `Extension` — may be added
   *only if they're in the keyword* (and carry less weight). Same for articles
   `the`/`a` — include only if the keyword contains them (rare).
8. **Hunting the *perfect* keyword.** It doesn't exist — every launch compromises
   on something (KD zone, volume, softness). Minimize the number of compromises;
   don't refuse to launch over one red-zone metric.
9. **Counting on donations.** Donations earn ~2–3 orders of magnitude less than
   in-app purchases. Never base monetization on them.

## Extra nuances (from video lessons)

- **Competitors can be sites, not just extensions.** Any site/web-service can be
  wrapped into an extension. If the keyword's competition is sites (no
  extensions), that's *good* — the keyword-occupation gate auto-passes. Verify a
  site's traffic in Semrush Organic Research by **exact URL** (`phrase` = the
  specific page URL, not domain/subfolder).
- **Match the top competitors' implementation.** Build the product in the same
  format as the products ranking in the top 5 of your keyword's SERP, just
  simpler and clearer. A novel format at launch risks worse behavioral factors.
- **More words in the name rank better** (statistically). 2–3-word names beat
  1-word names — lower competition. Don't exceed ~3–5 words and never mix
  keywords. Compare KD only between names of **equal word count** (74% KD on one
  word ≫ 74% on two words).
- **Turn a non-soft keyword soft with an `-er` suffix** (`api testing` → `api
  tester`) — works in most cases, slightly raises competition and lowers volume.
- **KD jumps month to month** — judge it by color zone only, ignore exact numbers.
- **CPC = 0 is fine for launch** — not a red flag (just means no ads on that
  query). High CPC is an *extra* positive money signal, not a requirement.
- **Semrush under-reports** — it extrapolates from tracker data, so it swallows
  traffic, worst on small volumes and non-English languages.
- **Ignore Semrush "Intent"** — its informational/commercial/transactional tags
  are unreliable. The only reliable signal: how-to question keywords are
  informational — and never build a how-to extension.
- **Open-source red flags** (skip the repo): front-end only / no backend, no
  live link, login forms (= complex site), old/stale repo. Non-devs: prefer a
  repo with a direct working extension link, or a simple service site.
- **Niches that monetize well:** ChatGPT/AI (vast — email/text generation,
  rewriting, images, summaries, translations), PDF & file tools, spreadsheets/
  Excel, developer tools (JSON etc.), designer tools (color/pixel/font), and
  anything that **saves work time** (especially summarization).
- **Niche query vs niche topic** — narrowing the *query* (`screen recorder` →
  `chrome screen recorder`) doesn't narrow the *topic*. Start with the narrower
  query (lower competition); widen later if it works.
- **Start simple, expand later.** You may launch several micro-function
  extensions on one theme as separate entry points, then merge into a bigger
  product once you see what users want.

## Case-study insights from product reviews

Decision heuristics and anti-patterns surfaced when hypotheses get rejected.

### Idea sourcing & niche choice

- **Google Workspace Marketplace** (Slides/Docs/Sheets add-ons) is a valid
  secondary marketplace with the same promotion mechanics as CWS; competition
  is far lower. Trade-off: the Workspace API typically constrains UX to a
  sidebar but gives easier Slides/Docs/Sheets integration.
- **Niche topic vs niche keyword** — a hyper-specific keyword like
  `chatgpt for sheets` (small volume) can clear because the product so narrowly
  matches the query that ranking is easy. Micro-volume works if the keyword is
  unowned.
- **Acquirer-availability is a hidden revenue gate.** Brand-piracy-style tools
  (YouTube/Instagram downloaders, contact scrapers) pass CWS moderation but
  most mainstream acquirers (Stripe-class) refuse — you get pushed to
  high-risk processors with much lower conversion. Score revenue down on such
  ideas.
- **VPN niche**: huge demand but server bandwidth forces immediate
  monetization, and most acquirers refuse VPN merchants. Viable only with an
  existing high-risk payment plan.
- **Image/video downloaders** skew Asia/Africa/LATAM/CIS traffic — depressed
  conversion vs Western traffic; monetize via ads / resale / traffic-redirect,
  not subscriptions.
- **Over-saturated niches** (screenshots ~1,800 CWS extensions, ads 1,800+,
  VPN ~270 named, AI tools, shopping tools, converters) — the whole vertical
  is harder, not just the keyword. Verify niche saturation with a CWS-DB
  name-search of just the topic word and a count of optimized rivals.
- **Workspace-default niches** (slides, sheets, docs, PDFs, file-shaped work)
  carry a structural advantage — by-default work intent → better monetization
  regardless of keyword choice.
- **Domain-specific niches (music/audio, JSON dev tools) are a no-go unless
  you're a domain practitioner** — researching user intent eats the 10-day
  budget and behavioral factors tank from misunderstanding. Exception:
  domain-adjacent "banal" products (voice recorder, equalizer) are fine
  without expertise.

### Keyword research & candidate generation

- **Read the SERP's form factor, not just whether it's "software".** Example:
  `hashtag finder` SERP is dominated by tools that *generate* hashtags from a
  seed, not tools that *scrape* hashtags from a page — building a page-scraper
  tanks behavioral factors. Open the top 3 SERP results and confirm they
  implement the same form-factor you plan to ship.
- **For each rejected head keyword, expand by pairing its word with adjacent
  ones** (e.g. `epub` + `pdf`/`reader`/`converter` via Keyword Magic). Surfaces
  the same product idea in a freer query.
- **Word-form differences (singular/plural, `-er` suffix, word order) don't
  break occupation.** If `font detect` looks free but `font detector` is owned
  by an optimized extension, the keyword *is* occupied. Check by searching the
  CWS DB with both words required *separately* (not as a phrase), sort by
  translation count + long-description length.
- **Always run the all-words-required search** (`any → all`, individual words,
  not the joined phrase) to catch optimized rivals you'd otherwise miss to
  reordering or morphology. Phrase-only search hides them.
- **Google substituting a near-synonym in the SERP** (you query `SMS checker`,
  results show `SMS detector`) is a *positive* signal — no well-optimized
  `SMS checker` exists yet; the substitute form is more saturated. Take the
  under-saturated form *because* its KD is lower.
- **Skip `how to ...` keywords** — Google classifies them informational; the
  extension can't satisfy them.
- **If a keyword shows ~0 US volume but normal volume in India/Philippines**,
  the term is non-English-native (Indian-English construction). Drop it — you
  can't rank on Tier-1 audiences.
- **Brand-suffixed Google queries**: include `Google` in the search seed (e.g.
  `Google slides templates`) to surface candidates; the seed word can be
  dropped from the actual name if Google would flag impersonation.
- **CPC > 0 but no live ads in the SERP** — walk historical months in the
  Semrush CPC chart; past advertisers indicate sustained commercial interest
  even if currently dark.
- **CPC fluctuates month-to-month** — check multiple months before scoring
  "no commercial interest"; absence in a single month means little.

### Softness — beyond the 50/30 rule

- **"Software in SERP, but the wrong software"** is its own failure mode. Top
  SERP can be 100% software yet for a *form-factor* incompatible with your
  product (e.g. `text replace` shows find-and-replace tools, not shortcut-
  expanders). Behavioral factors collapse if you ship the wrong form.
- **For "almost-soft" SERPs** (one extension at ~#15 amid articles), launch
  is allowed *only if the product is truly trivial to build* — dev-budget
  risk has to be near-zero because the keyword is risky.
- **Some queries that read as obviously software still come up articles**
  (e.g. `clear browser cache`, `clean browser cache` — both noisy). Don't
  pre-judge from intuition; pull the SERP every time.
- **Edge-suffixed keywords inherit Chrome extensions** — `clear cache edge`
  is a valid Chrome-extension keyword because Edge installs Chrome extensions.

### Keyword occupation — finer rules

- **Word-form leniency is asymmetric.** `adblock for youtube` and
  `youtube adblocker` count as the same optimized competitor (word order +
  `-er`). But entirely different words (`adskipper` vs `adblocker`) do *not*
  count as occupied even in the same niche.
- **Hyper-saturated optimized niches** (ad blockers, font detectors) — even
  if your exact phrase is free, the abundance of *near-form* optimized rivals
  drops odds enough to recommend a different keyword.
- **Tie-breaker at parity**: when two candidates both pass occupation, prefer
  the one with **fewer overall** same-niche extensions in CWS — not just fewer
  *optimized* ones. Less near-form crowding still helps.
- **One optimized competitor crushes second-movers fast.** A font-detector
  launched a few days after the first one (also optimized) sat at near-zero
  users vs the first's 9K. Being second-optimized inside an occupied keyword
  is essentially a write-off.

### KD nuance

- **KD ranking only applies within the same word-count names** — 74% KD on a
  1-word name ≫ 74% KD on a 2-word name. Normalize by word count before
  reading the zone.
- **KD essentially counts well-optimized competing pages** — when you've
  manually counted optimized rivals in the CWS DB, you've recomputed KD by
  hand for the extension layer. Trust your manual count when it disagrees
  with Semrush.

### Pricing & revenue scoring

- **Don't discount your subscription because competitors offer 50 features
  for the same price.** Users find converters per specific use case, not as
  suites. You can match iLovePDF-class $4–7/mo on a single-format converter,
  including against free competitors — installed users who get the value
  on first run convert at a few-percent floor regardless. **Non-critical**
  scoring factor — don't reduce revenue score for it.
- **AI/summarization niches over-monetize** vs average — bump revenue when
  the donor's vertical is AI-powered text/email/code work.
- **Designer-tool niches monetize** at lower price points than work-doc
  niches — pricing is suppressed because builders are too timid, not because
  users won't pay. Price above the niche median.
- **Recorder/dictaphone-class extensions monetize fine** — simple
  "record audio in browser" donors at 60K users with subscriptions exist;
  don't dismiss as "too simple to charge."

### Implementation simplicity

- **Manifest V2 vs V3 is an idea-validation gate.** Donors must be V3 (or
  willingly portable). ~43% of current store is V2 and Chrome is delisting
  V2 — non-devs should *only* take V3 donors; devs can port but it costs
  days. Check via the donor's `manifest.json` on GitHub.
- **Mass V2 delisting is a tactical advantage** — saturated niches will free
  slots as legacy extensions are removed; one-time window.
- **Open-source repo red flags** (reinforced): stale repos (last commit years
  old), no live install link, login forms (= back-end-heavy), broken-when-
  tested donors. **Always install the donor and confirm it works** before
  scoring simplicity.
- **For AI-wrapper products**, ~$100/mo of personal API spend is the typical
  pre-monetization burn; budget it explicitly and add IAP early.

### Name-keyword construction (reinforced)

- **More words rank better** — 2–3 word names beat 1-word names; 4 words is
  fine; 5+ is the cap. Service words (articles, prepositions) don't count.
- **Optimization of a competitor needs ALL three** simultaneously: same words
  in the name + long description > 3,000 chars + > 30 translations. Missing
  *any one* → competitor is "unoptimized" and the keyword is winnable.

### Process / workflow

- **Read the validation table right-to-left** even though it's filled
  left-to-right. The keyword cluster (volume / KD / softness / occupation) is
  decisive; user-count and donor revenue are secondary. Reject early on the
  right-hand cluster.
- **Don't reject a niche just because *you* couldn't find a keyword.** Retry
  with: a base-word in Keyword Magic, related/variations sort, and ChatGPT
  synonym brainstorm before declaring dead.
- **Don't trust Google Trends for final decisions** — it aggregates *all*
  phrases containing your two words, not just the exact phrase. Semrush
  exact-volume is the only reliable number at validation depth.

### Reality calibration

- The largest launches ran on keywords with ~1,500 US searches; most
  successful launches sit on 1–2K-volume keywords with thousands-to-tens-of-
  thousands of users. **Calibrate volume expectations to the 500–2,000
  sweet spot, not 10K+.**
- **No perfect keyword exists** — every successful launch compromises on one
  of {KD zone, head volume, softness purity}. Minimize the *number* of
  compromises; don't refuse the launch over any single red-zone metric.

## Idea-selection FAQ (from playbook)

- Compare **unoccupied fattest keywords across niches**, but only niches of
  roughly equal breadth (don't compare `dark mode` with `crm for gmail`).
- Brand-adjacent products: OK only if you *help* the platform (summarize a
  YouTube video, 1-click open Google Docs), not if you harm it (download
  videos/stories = piracy, won't pass moderation). Some brands dislike any use of
  their name in titles: Meta, LinkedIn, Claude (Anthropic), Bing (Microsoft).
- Dev tools you don't understand → don't pick them. Pick something that excites
  you and fits the table.
- A 1-feature donor app is fine — just find a *different* name keyword and build
  a similar, heavily optimized product.
- For ad-only monetization, ~30–40K users ≈ $1,000/mo; in-app purchases earn far
  more per user.
- Don't try to launch >1 product during a first run — builders spread thin and
  quality drops. Validate and run 1 idea fully first.

