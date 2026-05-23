# Stage 3 — Store assets, translations & publishing

Banners, icons, Welcome Page, 50+ locale translations, pre-publish checks, and
uploading to CWS.

## Behavioral factors — the lens for this whole stage

Every asset here is judged by one question: does it reduce friction so a tested
user stays instead of bouncing back to Google? (Behavioral factors — see the
cws-launch SKILL.md core principles.) Bugs in
the main function, a product that breaks browser pages, a confusing banner or
Welcome Page — each tanks behavioral factors and can kill the launch before any
traffic shows. Full SEO emerges over ~6 months *if* the launch build tests well.

## Pre-launch testing (do before anything else)

- **Watch a non-developer use it.** Hand the unpacked extension to a relative /
  non-IT person, give them only the link, and watch them install and use it —
  **say nothing**. One hint and the test is void; restart with a different
  person. 2—5 such tests catch ~80% of UX problems.
- **Dogfood it 1—2 days** — keep the extension installed in your own browser and
  just browse normally. Bugs and broken pages surface fast (e.g. a JSON
  prettifier that breaks a local `.html` page).
- **No bugs in the main function**, and the product must **never break other
  browser pages** — both are behavioral-factor death. Don't rush to the store.

## Why graphics matter

The small banner, large banner and icon directly affect **conversion to
install**. A confusing element makes users bounce back to search — behavioral
factors and ranking drop. So graphics must be: **simple & clear**, **tidy**, **on
a contrasting background**. Don't be clever or over-creative.

## Small banner (440×280)

Shown in the search results app list — its job is to grab attention.
- Contrasting background (a nice gradient works well).
- A thematic flat icon from flaticon.com, centered.
- A short caption conveying what the extension does.
- Few words — non-native users must still get it.
- PNG, —¤800 KB.

## Large banner (1280×800)

Shown on the extension's page. Take a screenshot (or a single UI element) of the
product; if the raw screenshot already conveys the product, frame it with
browser UI; otherwise simplify it or enlarge key elements. Add a short caption,
place it on a tidy contrasting background. Avoid video (users study it, get
distracted, conversion drops). No complex words. PNG, —¤800 KB.

Banner mistakes to avoid:
- **Don't show every UI element.** Strip clutter (pins, close buttons, rating
  widgets, gears) — keep only the one core function, simplified beyond your real
  build, with a **bigger font**.
- **Don't show browser chrome unless it's essential.** It wastes precious banner
  space and conveys nothing. Show it only when the browser context *is* the
  point (e.g. a dark theme). Explain "works in the browser" on a *separate*
  screenshot if needed.
- **Caption = the product's essence, not how to use it.** Write "Summarize any
  text instantly", not "Copy, paste and summarize". The user learns interaction
  from the UI; the banner just states what the product does.
- **Background**: contrasting but roughly **mono-tone** — a gradient that drifts
  slightly within one color, not two clashing colors (looks unprofessional).

## Icons

Don't draw them — grab a tidy minimalist flat 128×128 icon from flaticon.com and
resize. Files: `16x16.png`, `48x48.png`, `64x64.png`, `96x96.png` (the 128 slot
uses a 96×96 image with a transparent margin), `128x128.png`. Transparent
background on all.

- The **128×128-with-transparent-margin** icon (96×96 image inside) goes to the
  **store**; it does **not** need to go into the extension archive.
- A good icon **contrasts** with other extensions and works on both dark and
  light backgrounds (black-and-white icons do this well).

## Welcome Page

CWS hides freshly installed extensions "under the puzzle icon", so many users
can't find an extension after installing — they bounce to search — ranking
drops. Fix it with a **Welcome Page** that opens right after install and explains
where to find the extension and how to use it. Bonus: it's the perfect place for
install-counting analytics (it opens exactly once per install).

Build it on Tilda or any host (GitHub Pages, Vercel). Good examples on own
hosting: study-timer.com/welcome, mp4-to-mp3.pro/welcome, heic-to-jpg.pro/welcome.
On Tilda: extract-text-from-image.tilda.ws, aipromptgenerator.tilda.ws,
font-identifier.tilda.ws/welcome, annotatepdf.io/welcome. Own hosting is
preferred.

In ~90% of cases the goal is "find and pin the extension". Exceptions: new-tab
extensions ask the user to accept the new-tab replacement; a YouTube transcriber
sends the user to YouTube to find its widget. If the product has an **artifact**
(a corner widget on every page), point the Welcome Page at the artifact — that's
a one-screen, one-click path, far simpler than "find the puzzle icon and pin".
Correct **all** copy via ChatGPT (`correct this text in the app UI: [text]`)
regardless of your English level.

### Welcome Page mistakes to avoid

- **Screenshots mistaken for the UI.** Users think the Welcome Page *is* the
  product. If a screenshot blends into the page background, is too large, or
  shows only a cropped piece (not the full browser window), users click the
  *screenshot* instead of going to find the extension — up to **30% of traffic
  lost**. Fix: frame each screenshot with a clear border on a contrasting
  background, keep it modestly sized, and shrink the screenshot while *enlarging*
  the element the user must find.
- **No video or GIF** — on the Welcome Page or as a CWS listing asset. Video
  forces study time, distracts, and measurably lowers conversion (to install,
  and to pin). Use a static screenshot.
- **One uninterrupted flow.** The Welcome Page should lead to a single
  unbroken action. Don't make a long multi-step flow — extra steps (e.g. "now
  paste the signature into Gmail") belong *inside the product*, not here. The
  shorter the page, the higher the behavioral factors.

Publish on Tilda, set page name + URL. Optionally buy/connect a domain (if you
already host the extension's server on a main domain, make a subdomain like
`ext.yourdomain.com` pointing an A-record at Tilda's IP — host all service pages
there: Welcome, Uninstall, "share" pages). With a custom domain, connect SSL and
set www—non-www and http—https redirects, then re-publish all pages.

Auto-open the Welcome Page after install — ask the developer to add to the
service worker:
```js
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === chrome.runtime.OnInstalledReason.INSTALL) {
    chrome.tabs.create({ url: "[YOUR WELCOME PAGE URL]" });
  }
});
```

## Translations — 50+ locales

Translating multiplies Google-ranking chances several-fold. Use **Chrome
Extension Localizer** (localize.camp) — supports ChatGPT/Google/DeepL per-language
with optimal model defaults, has a large built-in quota, and can emit a ready
`_locales` folder.

Request a Secret Key via t.me/localizer_manager_bot, paste it into Localizer, add
name + short + full description, **verify text structure isn't broken on paste**,
select all languages (languages where OpenAI struggles are flagged ð¨ and default
to Google Translate). A full run takes 30—40 min; failed translations are
highlighted for re-run. Export the locales folder, drop it into the extension
root, and in `manifest.json`:
```json
"name": "__MSG_appName__",
"description": "__MSG_shortDesc__",
"default_locale": "en"
```
`default_locale` is the fallback when a user's language lacks a string. The full
description (`storeDesc`) is **not** in the manifest — it's uploaded to CWS
separately (see auto-upload script below).

(BabelEdit was used before Localizer — now obsolete: —¬50, no ChatGPT, per-product
quota. Skip it.)

### Manual translation for important languages

Some languages are worth manual name/short-description work — rich countries +
much lower competition than English:
- **Latin-script, rich** (do all): German, French, Spanish, Italian, Dutch,
  Swedish, Danish, Norwegian, Finnish.
- **Huge speaker base** (do at least the first 3): Arabic, Indonesian, Russian,
  Portuguese, Japanese, Filipino, Vietnamese, Turkish, Thai, Korean.

The **name** matters most — invest there; less in the short description; just
ChatGPT-translate the full description. Find national-language name keywords the
same way as English: ask ChatGPT how the product would be searched in that
language, use Semrush with the target country selected (collect keywords from
national-language competitor sites in that country's SERP), and browse CWS in
that language (`?hl=es`, language codes per Chrome i18n docs). In low-competition
national languages you can safely **combine two popular keywords** in one name,
or join English + national via a dash (`Bloqueador de anuncios - Free
Adblocker`). For short/full descriptions in a national language, prompt ChatGPT
in that language using the name + 2 keywords; translate the full description from
your English one.

Transliteration nuance:
- **Don't literal-translate a "universal" English name** (`ai chat gpt`). Think
  how real people *search* in that language. In Russian, `ÑÐ°Ñ Ð³Ð¿Ñ` (transliter-
  ated) gets ~1M searches — a different, valuable keyword worth taking.
- **Non-Latin-script languages** (Cyrillic, Chinese, Arabic) — the *national*
  spelling usually dominates over the English one, and the gap widens as a tech
  goes mainstream. **Latin-script languages** (German etc.) — the English
  variant often dominates.
- Auto-translate (`localize.camp`) is **much better than nothing** even when it
  truncates the 132-char short description — other languages have far lower
  competition, so truncation is acceptable for the auto pass. Fix the short
  description only when you do the *manual* pass for an important language.
- **Anglicism naming pyramid** (best — worst), for a name that's an anglicism:
  (1) the keyword *as people search it*; (2) as people *say* it grammatically;
  (3) keep the anglicism if it has any traffic; (4) auto-translate; (5) — worst —
  no translation at all. Even a clumsy auto-translation beats none, because
  Google still tends to glue it to the real local search query.
- **One English locale only.** Spanish / Portuguese / Chinese near-duplicate
  locales are fine (low competition), but never create UK/US/AU English
  duplicates — duplicate English pages hurt English SEO. Localizer outputs one
  English locale by design.
- **Interface strings.** Auto-translate only handles `appName` / `shortDesc` /
  `storeDesc`. If the extension UI has *other* strings in
  `_locales/en/messages.json`, you must fill those manually in the **en** locale
  — otherwise buttons render empty. Other locales fall back to `en`, so you only
  need the English ones complete.

## Pre-publish checks

1. **Differ from the competitor** — different icon, new banners, different
   name/short/full description, optimized text. A full copy-paste gets rejected.
   Name-similarity rules: identical name OR name differing only by word order /
   1—2 letters — use **only if** the competitor is **not** optimized (not 30+
   languages and/or not 3,000+ char description). Differ by 1 word — much better.
   Differ by 2 words or fully — ideal.
2. **Spam check** the texts (Stage 2).
3. **Translate** (above).
4. **Antivirus** — upload the extension archive to virustotal.com. A
   false-positive once got an extension banned. If flags appear (rare),
   investigate what triggers them, rework, rebuild, re-check.
5. If for some reason you publish English-only (not recommended), remove **all**
   `_locales` folders except `en` first (save them) — otherwise CWS fills empty
   descriptions for every language and heavily pessimizes ranking.
6. **2FA** — Google may require it before upload (Stage 0).

## Uploading to CWS

1. Set the Google account interface language to **English (United States)**
   (account settings — Personal info).
2. Go to the developer dashboard
   (chrome.google.com/webstore/developer/dashboard), upload the extension archive.
3. Fill the store card per language — name and short description pull from the
   archive; **full description must be pasted manually** (CWS can't pull it).
4. Auto-upload all locale full descriptions with `references/cws-locale-uploader.js`:
   on the extension's **Store Listing** page, refresh, open DevTools — Console
   (type `allow pasting` if blocked), paste the uploader script, click **Choose
   Files** in the green box, select your `_locales` folder; it loads `storeDesc`
   for every locale. Then **Save draft**, refresh, verify each language loaded.
   (The script lives at `references/cws-locale-uploader.js` — it reads
   `_locales/<code>/messages.json` — `storeDesc.message` and drives the CWS
   language dropdown + 16,000-char textarea — see `references/cws-locale-uploader.js`.)
5. Upload graphics carefully.
6. **Save Draft** — **Privacy** tab: set **Single Purpose** (one short sentence);
   set **No, I am not using remote code**.
7. **Justify every permission** briefly. Examples: `storage` — store user
   settings; `tabs` — control sound capturing in tabs; `activeTab` — control sound
   capturing in active tab; `downloads` — download sound file; host permissions —
   show extension action button on any website. Requesting permissions the
   functionality doesn't need = rejection regardless of justification.
8. Mark collected data (mark nothing if you collect nothing), tick the 3
   confirmation boxes, add a **Privacy Policy** URL (the studio template doc with
   `[COMPANY NAME]`/`[EMAIL ADDRESS]`/`[DATE]` replaced; COMPANY NAME = your
   extension's English name; publish it and paste the public link).
9. Save and submit for moderation.

## Launch-time decisions

- **Extension ID** is shown in the dashboard (top-left) right after you upload
  the first **draft** — before publishing. Grab it then to wire up the review
  widget (built in the cws-promote stage), then re-upload the draft.
- **No auth at launch** for a no-cost product. Auth cuts product usage by
  **60—80%** in measurements and wrecks behavioral factors. Add auth only later,
  *together* with monetization (Stage 5) — auth must be Google sign-in, needed to
  tie payments to a real account. Count users via analytics instead, not auth.
- **Analytics by extension type:**
  - *Site-wrapped* extension — you can drop a normal analytics script on the site
    (and Yandex Webvisor) — fast, rich.
  - *Local-page / popup* extension — no script allowed; use event-based analytics
    — GA4 Measurement Protocol, or better **Amplitude** (cleaner, richer
    out-of-the-box; Mixpanel is an alternative).
- **Don't disable the product in cheap locations.** Google tests across random
  countries; a product that's broken/blocked in Tier-2/3 kills behavioral factors
  *globally*, including Tier-1. For a product **with running costs**, you must
  serve (and later monetize) **all** countries. For a product **without costs**,
  give it free everywhere and paywall only Tier-1 later.
- **A/B tests** — skip real A/B infrastructure for simple products (bugs, dev
  time, maintenance). Do a **quasi A/B**: ship version A for a week, then version
  B, compare metrics. Real A/B only for risky monetization changes on large
  products (scope it by country / install-date / time window).
- **Auxiliary buttons** (settings, support, rate-us) — add only if they don't
  overload the main function; hide settings under a gear. Only ~1% of users ever
  click hidden buttons, so deep-buried buttons add little — the trade-off favors
  a clean main UI.


## Case-study insights from product reviews

### Banners — additions

- **60% conversion is the ceiling.** Highest-converting large banner ever
  measured was a plain dark-theme product screenshot showing browser chrome
  where the dark theme *is* the point. Average organic conversion is 15–30%;
  treat 60% as the ceiling.
- **Failed creative experiments worth knowing.** A black-cat-on-black banner
  and a woman-in-a-bathtub creative for the same dark-theme product both got
  high ad-CTR but tanked install conversion. Every non-screenshot creative
  tested historically underperformed the raw screenshot.
- **For nano-products without UI, draw a skeleton browser around the widget.**
  BPM Finder's screenshot keeps a faded "skeleton" music player + simplified
  browser chrome (no tab text, no other extensions, no non-English text
  anywhere). Justified only for sub-product extensions with tiny popups.
- **Single key on banner #1**, every time. Splitting weight across two keys on
  the first screenshot is acceptable only after ~10K users.
- **Sidebar with competitors steals ~15% of your conversion** when CWS does
  not give you the **Featured** badge. Featured removes the sidebar but is
  awarded ~50/50; **do not apply manually** — a failed application can block
  re-application for ~6 months.
- **Build screenshot #1 assuming you'll be alone in a carousel, not paired.**
  Without Featured, only one banner shows; splitting product essence across
  two banners means half the message disappears.
- **Artificially enlarge core controls on the banner, shrink the browser UI.**
  Devs render at full screen size, but check at actual CWS display
  dimensions — what looks fine at full size becomes illegible at listing
  size.
- **Strip pin/close/gear/rating widgets from the screenshot** even if they
  exist in the real UI — clutter.
- **Per-feature caption bullets on subsequent banners are neutral**, not a
  boost. Don't spend effort writing clever bullet captions; users don't read.
- **Banner background gradient: never two-color** (green→purple→blue =
  "banner blindness" + amateurish). A subtle one-color gradient with slight
  tonal shift is the maximum non-designers should attempt; pure flat color is
  safer.
- **Black on white is one of the strongest banner backgrounds** — CWS UI is
  white, dark mode is only used by devs, so dark banners "pull all focus
  from competing tiles."
- **For "known platform" banners** (Instagram/Facebook UI clones), keep the
  original UI clutter — familiarity > simplification. The strip-everything
  rule reverses when the screenshot is of a universally recognized interface.

### Icons — additions

- **Reject outlined / dotted-line / thin-stroke icons.** They fail at 16×16
  and disappear in the tab strip.
- **Skip flaticon attribution on launch.** Required by flaticon TOS but
  irrelevant at 0 users; add the credit only after ~1,000 users.
- **Icon and banner must match form-factor.** Two visually different icons
  (one for store, one for tab) is allowed but kills recall — users install
  based on one icon, then hunt for a different one and bounce.
- **Black-and-white minimal icons stand out best** against the typical 3–4
  other extensions a user has pinned. Color icons get lost in a row of
  colored competitors.
- **If the icon "looks too simple," that's the signal to use it.** Devs
  gravitate toward 3D / multi-element icons that vanish at 16px; the
  "too plain" instinct is wrong.
- **Icon-vs-banner aesthetic harmony is not a real conversion factor.** Don't
  waste time matching styles.

### Welcome Page — additions

- **The "arrow + number" combo is non-optional.** Without bright (ideally
  red) numbered arrows pointing at the pin, banner-blindness kicks in within
  ~2 seconds and users hit the tab close button. Arrows trigger a "primitive
  metro-sign" recognition response.
- **A misleading arrow is worse than no arrow.** A decorative arrow pulled
  focus *away* from the pin icon in a recorded user test; the user stared at
  the unmarked area, opened tabs, searched bookmarks, never found the
  puzzle icon until hinted.
- **The puzzle icon shape on the Welcome Page must match Chrome's exactly.**
  Different stylization of the same symbol breaks recognition.
- **Period vs colon at end of `Click the puzzle:` matters.** The colon
  visually ties the text to the screenshot below; a period reads as a
  closed sentence and users don't connect instruction to image.
- **Don't auto-hide the artifact when teaching it.** If the Welcome Page
  tells users to click an on-page artifact, disable the artifact's
  "hide-when-idle" behavior specifically on that page so it stays visible.
- **Welcome-Page screenshot needs the full browser frame, not a cropped
  slice.** Cropping breaks spatial orientation — users can't place the pin
  and start clicking the screenshot itself.
- **Numbering placement: 1+2 on the first screenshot, 3 on the second.**
  Don't restart numbering per screenshot; one continuous numbered sequence
  is what users follow.
- **For Russian/Spanish/etc. installs, the English store name on the
  Welcome Page does not break recognition** — the icon stays identical and
  the user's brain still maps the local-language tab name to the English
  Welcome-Page name. Don't over-engineer per-locale Welcome Pages.
- **Tilda's branded footer on a `tilda.ws` subdomain is fine for English-
  market launches** — foreign users don't recognize the Tilda brand. Don't
  waste time hiding it on V1.

### Translations — additions

- **The 10× rule for name keywords in a locale.** `English_searches ≥ 10×
  local_searches` → use English in the local locale. `Local ≥ 10× English` →
  use local. Anything between → combine both with `−` or `|` (allowed on
  non-English locales because competition is low enough that 2-key dilution
  is acceptable).
- **GPT-4 (with proper prompts) translates better than DeepL or Google
  Translate** for everything except a flagged list of ~10 languages
  (Amharic, Kannada, Gujarati, Norwegian, etc.) — for those, run Google
  Translate; GPT mangles them.
- **Auto-translated short descriptions overflowing 132 chars is acceptable
  on non-English locales.** Constraining the prompt to fit 132 chars makes
  GPT cut content too aggressively; let it overflow, CWS truncates
  harmlessly. Fix only when doing the manual pass for an important locale.
- **Russian must be done manually even though Russia doesn't pay.**
  Russian-speaking traffic (10–15% of launch traffic) is a *trigger* for
  Google to expand testing into Tier-1 paying geos — investing in the largest
  non-paying locales is a deliberate ranking strategy.
- **Yandex Wordstat for Russian keyword research, not Semrush.** Wordstat is
  owned by Yandex; Semrush guesses Russian traffic.
- **For Spanish keyword research: target Spain in Semrush, follow competitor
  sites from the Spain SERP, and feed those local-language keywords back
  into Semrush** — the only way to surface keyword translations for
  languages without national tools.
- **Tech-vertical extensions (JSON formatter, regex tools) usually keep the
  English name in every locale** — devs everywhere search in English. Verify
  per-product, but don't auto-localize names of dev tools.
- **Never duplicate the English locale.** `en`, `en_US`, `en_GB`, `en_AU` —
  pick ONE. Four English duplicates pessimize SEO on the most competitive
  locale. Spanish/Portuguese/Chinese near-duplicates are fine (weak
  competition).
- **The Localizer Telegram-bot key issues quotas large enough for multiple
  extensions, not just one** — keep the key for future products.

### Behavioral factors at launch — additions

- **Pin conversion cannot be measured precisely** — Chrome fires no pin
  event. Welcome-Page → product-open conversion is the proxy; the
  artifact-button path has cleaner measurability than the pin path.
- **Google's launch test traffic is invisible.** First experiments ship as
  single-digit installs across random geos; "I don't see myself in search
  yet" doesn't mean anything for weeks.
- **Tier-3 country traffic is NOT discardable** even for paid products.
  Disabling the product in cheap geos creates negative behavioral signals
  Google extrapolates *globally*, including Tier-1. For products with
  running costs, paywall every country; for products without costs, ship
  everywhere free.
- **Login auth drops product activation 60–80%** in measured A/B tests.
  Pre-monetization auth is a launch killer.
- **Auth-before-product (blank login screen first) is the worst pattern.**
  If auth is unavoidable, let users into the product first and pop the
  auth modal only when they hit a paid action.
- **One verbal hint from the watcher invalidates the non-developer test** —
  restart with a different person. 2–5 such tests catch ~80% of UX failures.
- **Dogfood the unpacked extension for 1–2 days before upload.** Real
  launch-killing bugs (extension breaking arbitrary pages like local
  `example.html`) surface only during normal browsing, not scripted self-
  testing.
- **Long Welcome Pages get scrolled-then-closed like washing-machine
  manuals.** Users skim to the bottom, decide it's too long, close. Hard
  cap: 2 blocks; never add "how to use the product" sections to the
  Welcome Page — those belong inside the product.
- **Each context switch (popup → sidebar → auth → main UI) drops behavioral
  factors.** Aim for one unbroken flow from install → Welcome Page → core
  feature. Popup is "outdated form-factor" but launch-acceptable; **side
  panel** (added to Chrome ~1 year before recording) is preferable when the
  product is content-reading.
- **Prefer `chrome.storage.sync` over `chrome.storage.local`.** Sync syncs
  settings across the user's Chrome profiles automatically — better
  behavioral factor on multi-device users. Falls back gracefully if sync
  unavailable.
- **`unlimited_storage` permission exists** for products that exceed the
  default storage cap (relevant for embedded image / HTML-signature
  generators) — use it instead of falling back to clipboard hacks.
- **Don't strip user-facing controls present in top-3 competitors.** For AI
  extensions, the launch baseline is: streaming output, stop button,
  regenerate, model selector. Voice input optional.
- **Quasi A/B testing is the default** — ship variant A for a week, B the
  next week, compare metrics. Real A/B only when changes can lose users
  (monetization rollouts), scoped by country / install-date / time window.

### Pre-publish — additions

- **Name collision (refined):** identical name OR difference of word-order /
  1–2 letters is acceptable *only if* the existing competitor is NOT
  optimized (lacks 30+ locales AND/OR lacks 3,000+ char description). If the
  existing competitor IS optimized, your clone gets dragged down by SEO
  clone penalties — pick a different name.
- **Don't ship two near-identical keywords adjacent in title or short
  description** (e.g. `Convert PDF Converter`). Triggers human moderation
  flags AND ranking pessimization. Same root word can appear elsewhere in
  the description if separated by ≥5 words.
- **Singular vs plural and `.` vs no-`.` are treated as distinct queries by
  Google** despite Google's public claim. Cover variations: `pdf.` and `pdf`
  in different sentences of the long description.
- **Upload as a draft to get the extension ID early.** ID appears top-left
  the moment a draft uploads — grab it, wire it into the rating widget /
  paywall URL / Welcome Page, then re-upload the draft. Don't publish, just
  upload-as-draft.
- **`short_name` in manifest is unreliable on current Chrome.** Several
  participants set it but Chrome didn't respect it; don't rely on it for the
  tab-strip name.
- **Storage permission justifications get verbose-rejected if one-word.**
  "Storage — to store data" gets flagged; "storage — to persist user-
  selected language and theme preferences across sessions" passes. Be
  specific per permission.

### Moderation — additions

- **Moderation re-checks the entire submission on every update**, including
  previously-approved metadata. A short description that passed v1 can fail
  v2 even unchanged — rare but happens.
- **Repeated re-submissions attract stricter scrutiny.** If moderation
  rejects once, the second pass examines your text "with prejudice" — fix
  the underlying spam pattern aggressively, not incrementally.
- **Obfuscation is banned; minification is mandatory** — and they're
  distinct. Variable-name shortening to a/b/c + whitespace removal =
  minification (allowed). Replacing characters with non-ASCII glyphs to
  hide code = obfuscation (banned).
- **Adding "just in case" permissions guarantees rejection.** Strip the
  manifest to the actual surface used.
- **Privacy Policy company name must match the extension's English name
  exactly** — mismatches get caught.
- **Don't pass moderation "early just to get the ID" and leave the listing
  approved-but-unpublished.** Plausibly CWS adds the approved URL to its
  sitemap and indexes a poor version. Upload as draft only — don't submit
  for review until the full launch package is ready.

### Analytics setup at launch — additions

- **Site-wrapped extensions get full script-based analytics** on the Welcome
  Page itself: **Yandex Metrica + Webvisor**, GA4, Amplitude (preferred).
- **Yandex Webvisor click-maps on the Welcome Page surfaced the
  "users click the screenshot thinking it's UI" insight.** Install Webvisor
  there specifically to validate before optimizing.
- **For local-page / popup extensions use event-based analytics**: GA4
  Measurement Protocol or Amplitude / Mixpanel — send events from the
  extension to the analytics endpoint via HTTP.
- **Unique-user counting does NOT require auth.** IP attribution is accurate
  enough at pre-monetization volumes. Adding auth purely to count users is
  behavioral-factor self-injury.
- **Track conversions for the Welcome-Page → activation funnel separately.**
  Average is ~60% (with a good Welcome Page), drops to 10–15% without one.
  Early Welcome Pages hit 20–25%; reaching 60% needs iteration on
  screenshot framing, arrows, and puzzle-icon matching.
- **Free-action count cap target: ~10–15 free conversions** for products
  with per-call costs (~$0.02 each) — aim for "burn $100–200 of free
  actions" before paywall is added. That's the cap at which behavioral
  factors should be stable enough to switch on monetization across all geos.
- **No "track-only-paying-geos" splits at launch.** Track everyone; the
  Tier-3 cohort that doesn't pay is the cohort that triggers Google's
  Tier-1 expansion experiments.
- **For extensions injecting widgets into third-party sites, keep the
  target selector in a server-side config**, not hard-coded. Add a server
  alert when the selector returns null — third-party sites change DOM;
  without remote config you wait days for re-moderation to ship a fix.
