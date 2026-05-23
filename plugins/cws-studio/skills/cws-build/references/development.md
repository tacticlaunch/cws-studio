# Stage 2 — Development (building the minimal extension)

Goal: ship a CWS build that meets four points, **before** monetization or extra
features. The job is to launch fast and test installs — not to build a beautiful
multi-feature product.

## The four-point target

1. **Functionality matches the name keyword.** Before building, Google your name
   keyword — your core function must match the products ranking on top of that
   SERP.
2. **Simple** — usually one screen or one key function.
3. **Looks tidy** — not necessarily beautiful.
4. **No bugs.**

Reference of a product hitting all four: Audio & Voice Recorder
(chromewebstore.google.com/detail/audio-voice-recorder/deadjnaenmndpdpakgchpbedlcdmmoai).

**Match the top SERP competitors.** Google your name keyword, open the top 3–5
software results, and build the **same core function in the same format**, just
simpler. **Extra functions are fine** — even ones competitors lack — *as long as
they don't disturb perception of the main function*. Put the main function as a
bright, obvious first item; secondary functions sit beside it without getting in
the way (e.g. "Delete Google Search History" also clears cookies/cache).

## Build strategy — in priority order

1. **Look for a full open-source extension on your topic.** Google `<topic>
   extension github` / `<topic> chrome github`. Open-source code can be used
   legally and dramatically simplifies the launch.
2. **Look for open-source pieces/functions** — `<function name> github`.
3. **A site or web-service can be the base** — build a web service, then wrap it
   into an extension (see "site-service extension" type below).
4. **Otherwise build a simple product from scratch** meeting the four points.

## Manifest version

CWS no longer accepts **new** extensions on **manifest v2** — only **v3**. Many
v2 extensions still sit in CWS but Chrome is phasing them out (clearing up to ~⅓
of CWS, including big extensions). Check `manifest_version` in `manifest.json`.
**Pick a v3 donor** — porting v2→v3 is hard for complex architectures. Core v3
difference: a v2 background script (always-on) is replaced by a v3 **service
worker** (wakes on demand) — safer for users, slightly harder to build.

## Cloning an open-source donor — make the build pass moderation

Goal: the final product should look as **un-like the donor as possible
visually**; in code, change only basic things (text, CSS).

1. Download the donor's source.
2. Delete the `_metadata` folder if present (technical info about the copied
   extension).
3. In `_locales`, delete every folder except `en` (distances your build from the
   donor).
4. Search the whole folder for and replace: the donor's **name**, its **CWS
   URL**, its **official site URL**, any other obvious branding. Replace what's
   easy; don't bother with hard things like code variable names.
5. Replace all branding graphics and icons with your own (flaticon.com is the
   best source for icons/images).
6. Change `name` and `description` in `manifest.json` (if they read like
   `__MSG_appName__`, the strings live in `_locales/en/messages.json` — change
   them there).
7. Lightly change the donor's CSS — colors, fonts, button radii; remove a couple
   of elements.
8. Manifest cleanup: `name` ≤75 chars, `description` ≤132 chars; remove
   `default_title` (falls back to `name`), remove `author`, remove `fingerprint`
   and `key` (they hold info about the source extension). Full description is
   **not** in the manifest — it's uploaded in CWS.

If a donor is hard to modify, just find another — in ~90% of cases you can find
one editable in 2–3 hours.

## Minification

Minify the `.js` files (e.g. toptal.com/developers/javascript-minifier) so others
can't easily edit a copy of your code. Replace the originals with minified
versions; verify the extension still works by loading it in developer mode.
Complex multi-file `.js` structures need a developer minifying with a proper
library. If you later re-upload the extension on another account, redo the
distancing steps **and** re-minify with slightly different settings so the
duplicate's code differs from the existing CWS version — otherwise it may be
rejected.

## Extension types (pick the simplest that fits)

| Type | Use when | Pass moderation? |
|---|---|---|
| **No-UI** | one trivial action on icon/context-menu click | yes |
| **Site-service in a tab** | universal; opens a remote web service in a new tab | needs an extra widget — see below |
| **Local page in a tab** | universal; opens a local extension page in a new tab | yes, no extra module needed |
| **Popup** | small UI that fits a popup rectangle; often over a site | yes, no extra module needed |
| **Content-script injector** | must add a widget / change a third-party site | yes |
| **Hybrid** | combine the above (most real extensions are hybrid) | depends on parts |

### No-UI extension
Nano-products doing one action on icon click or context-menu click (`browser
action`). Examples: Reopen Closed Tab, Right Click Enable. Simple enough to
generate with ChatGPT — prompt: `code chrome extension (manifest v3), that opens
last closed tab by clicking in context menu or by clicking on extension icon`.
Minimal shape: a `manifest.json` (v3, `background.service_worker`, `action`,
`permissions`) + a `background.js` registering `contextMenus` and
`action.onClicked` handlers.

### Site-service in a separate tab
Any site/web-app can be wrapped into an extension — code the service yourself or
find an open-source web service. Bonuses: you can ship site updates without CWS
moderation, and use standard web analytics.
```json
{ "manifest_version": 3, "name": "Example", "version": "1.0",
  "background": { "service_worker": "background.js" },
  "action": { "default_popup": "" } }
```
```js
chrome.action.onClicked.addListener((tab) => {
  chrome.tabs.create({ url: "https://example.org" });
});
```
**Moderation will NOT pass an extension whose only function is "open a site".**
Add a simple extra module — e.g. Annotate PDF adds an artifact on every `.pdf`
page that loads the file into its editor.

### Local page in a separate tab
Same as above but opens a **local** extension page (`chrome.tabs.create({ url:
"hello.html" })`). Bonus: no extra module needed for moderation. Downside: no
out-of-band updates. All libraries/scripts must be local — moderation forbids
remote-hosted scripts in local files.

### Popup
`action.default_popup` points at `popup.html`. Like the local-page type
(libraries must be local; no extra moderation module needed). Often pairs with
content scripts to render widgets over the underlying site. Examples: Convert
WebP to JPG, Audio & Voice Recorder, Make QR Code, BPM Finder.

### Content-script injector
Adds scripts/widgets to any site. Strong, used to insert a widget into a
third-party site's UI. **Critical nuance:** also inject into pages opened
*before* install — otherwise a user who installs while on a YouTube tab sees no
widget, assumes the extension is broken, removes it, and returns to search →
Google reads that as an unsatisfied query → behavioral factors and ranking drop.
Inject into existing tabs on `runtime.onInstalled` (query open `http(s)` tabs and
`scripting.executeScript`) **and** new tabs on `tabs.onUpdated` (`status ===
'complete'`). Needs `"permissions": ["scripting","tabs"]` and `"host_permissions":
["<all_urls>"]`.

### Hybrid
Combines types — e.g. Extract Text from Image (popup + site injection), Math AI
(popup + site injection), ChatGPT PDF (popup + opens a site).

## Prototype spec (TЗ) before development

Write a short text spec — how you'll build the product, step by step (e.g. "1.
Take open-source code at *link*, change feature X like so…"). Usually a few lines
to one A4 page. Even if building solo, it structures your thinking and becomes
the brief for designer/developer. If UI changes are needed, sketch them (Figma
recommended). Include **all UI text strings** so the designer doesn't invent
them — and run every string through ChatGPT (`correct this text used in the app
UI: [text]`) regardless of your English level; the paying audience are native
speakers who notice article/preposition errors.

## Hiring (if needed)

**Designer** (UI, ~3,000–5,000₽ for a simple extension UI; banners/icons
similar): post on fl.ru etc. Work with Russian-speaking designers. Vetting that
gives 80% result for 20% effort — they must show **real cases**; you must feel
"I want the same". Refusal to show cases = walk away.

**Developer**: easiest is a colleague. Make the product *simpler*, plan a
few-days build, sketch a Figma prototype, offer hourly (~$30/h) or a 50/50
partnership (you: concept, packaging, design, translations, promotion, paid
boost; them: development). Marketplaces: fl.ru / kwork.ru / youdo.ru (RU),
fiverr / freelancer / upwork (intl). Post a "React + Node.js (TypeScript)
developer for upgrading a simple Chrome extension" vacancy with the prototype
spec. Location priority: Russian-speaking CIS → Eastern Europe → Philippines/
Vietnam → Latin America. Vet by **real live cases** (clickable, not GitHub code),
the "I want the same" feeling, and how structured/literate their plain messages
are — structured writing usually predicts structured code.

## Install in developer mode (to test)

Unpack the extension zip → Chrome `chrome://extensions` → enable Developer mode →
Load unpacked (the folder containing `manifest.json`). Test by clicking the
extension icon / using its UI.

## View any extension's source code

Install the source-viewer extension
(chromewebstore.google.com/detail/chrome-extension-source-v/hkeikabhdaoiddhmbhbhmfnpakdbcell;
backup: .../jifpbeccnghkjeaalbbjmodiffmgedin), open a competitor's page, click
**View Source Code** — you can read and download the source.

## Is the donor's code obfuscated?

Look at variable names in `.js` files (after `var =` / `let =` / `const =`):
- **Obfuscated** — single-letter, meaningless names. Hard to reuse → skip.
- **Open** — word-based names you can read. Good donor.
- **Libraries** are always obfuscated — recognizable by a multi-line `/* license
  / author … */` comment at the file top. Ignore those.
Also re-check `manifest_version`: prefer v3 donors.


## Case-study insights from product reviews

### Build strategy & approach — additions

- **Match the SERP, including the dominant format.** Open the top 3–5 results
  for the name keyword and copy the *core interaction pattern* (textarea +
  button, file upload, etc.). Even if your dev experience says nobody uses
  that pattern, build it — Google has already validated that pattern as the
  one searchers expect.
- **Build the SERP-matching function first**, even if you have a better
  alternative on the side. Side functions are fine when they don't disturb
  perception of the main one — load the main function as the first, bright
  element and keep secondary functions accessible but not in the way.
- **Replication is encouraged for proven SERP patterns.** If every top
  competitor lets you paste text and hit a button, build that even if you
  ship an additional hybrid (e.g. "summarize current page"). Don't only
  ship the alternative form — most common cause of failed launches.
- **A v3 nano-product (one icon-click action, ~50–100 LOC) is a valid first
  build** even for non-developers; ChatGPT can generate it (e.g. Reopen
  Closed Tab, Right Click Enable). Don't pad nano-products with arbitrary
  settings — they convert by being one button.
- **Self-finance API costs for the first ~$150–300.** Instead of attaching
  monetization on day one (which kills behavioral factors before you've
  ranked), pay the OpenAI/etc. bills yourself for ~1,000 free actions per
  user until 2,000–3,000 users accumulate. Then flip monetization on for
  new users only (Paywall supports this).
- **Don't enable monetization until ~2,000–5,000 users.** SEO depends on
  behavioral signals which crash hard when an unranked product shows a
  paywall (users bounce to free competitors → Google sees query unsatisfied).
- **Don't delete an underperforming extension.** First 6 months are normal
  warmup; year-1 verdicts are tentative. Better to launch a sibling product
  on the same topic with a different name than to modify or remove.

### Developer hiring & partnership — additions

- **Skip seniors for micro-products** — seniors can't bring themselves to
  ship "simple," over-engineer, and add corner cases. Mid / mid-plus is the
  sweet spot for both dev and design. Same for designers — junior-plus / mid
  designers ship cleaner micro-product UIs than seniors who reach for arty
  layouts.
- **Vet by structure of plain messages.** When a freelance dev writes
  structured, grammatically clean prose in their text intro, their code
  tends to match. Disorganized DMs predict disorganized code.
- **Demand live demos, not GitHub.** A working installable extension/site
  you can poke is the only proof. "Code is under NDA" / GitHub-only
  candidates are walk-aways.
- **50/50 partnership beats hourly** for micro-products with ongoing
  maintenance — never give the dev only 10% and then wonder why they don't
  engage. One side gets 51% only to break tie votes, not as a power play.
- **Average dev cost target**: ~$30/h, ~$300 total for a simple
  micro-product, finished in ~1 working day; if a non-developer is scoping,
  plan a 3-day build that realistically takes ~10 calendar days with
  communication overhead.
- **No legal contracts for micro-product partnerships** — agreement
  screenshot in a chat + two thumbs-up is the norm. Any malicious party can
  violate any contract; trust on the front end matters more.

### Behavioral risks of UI choices — additions

- **Popup vs site-in-tab vs local-page-in-tab — choose by use case, not
  preference.**
  - **Popup** wins when the extension interacts with the current site context
    (dark theme toggle, site-scoped passwords, BPM finder, dictation).
  - **Site-in-tab** wins when the user needs to upload a file, take a
    multi-step action, or might accidentally click away (popup closes on
    outside-click — devastating UX for long-form work).
  - **Local-page-in-tab** is the middle ground — no extra moderation module
    needed, but no out-of-band updates and all libs must be local.
- **Hybrid popup + over-site widget** (content-script injected) is the
  strongest behavioral-factor amplifier — but support is harder due to host-
  site CSS/JS conflicts. Shadow DOM helps isolate but the host element still
  sits in the page tree. Plan extra dev time.
- **Streaming + cancel buttons are mandatory** for any LLM-backed UI from
  launch — users bounce on a static spinner. Copy and regenerate buttons are
  standard.
- **ChatGPT-clone layout convention**: chat on top, prompt textbox at the
  bottom. The Building Blocks default has prompt-on-top — always rearrange
  before shipping.
- **Watermark removal / interface-unlock are valid Paywall hooks** for
  nano-products that don't naturally have "actions to limit."

### Moderation-passing nuances — additions

- **Site-wrapper extras to pass moderation** (an extension that only opens a
  site fails):
  - **Inject a small artifact into search-engine SERP / target-domain pages**
    that captures the target file or URL and forwards it into your wrapped
    site (Annotate PDF injects a button next to every PDF link in Google
    search + on direct PDF pages, forwarding the file into the editor).
  - **A second over-site widget** activated via "deep settings" toggle that
    duplicates the site's core function via content script (BPM Finder ships
    an on-page widget purely for moderation; once shipped, it counts as
    "extension-only functionality"). Add a feature flag in advanced settings
    so real users never trip over it.
  - The criterion: at least one capability must be **impossible without an
    extension API** (`tabs.create`, `scripting.executeScript`, `contextMenus`,
    `chrome.action`).
- **Local-page-in-tab variant has zero extra-module requirement** —
  moderation accepts it as self-contained. Cost: no out-of-band updates, all
  libraries must be bundled locally, no standard web analytics.
- **Content scripts must inject into pages opened BEFORE installation**, not
  just new tabs. Pattern: on `runtime.onInstalled`, query all open http(s)
  tabs and `chrome.scripting.executeScript` into each; then handle new tabs
  on `tabs.onUpdated` (`status === 'complete'`). Otherwise users who install
  on a YouTube tab see no widget → bounce → ranking dies. Requires
  `permissions: ["scripting","tabs"]` and `host_permissions: ["<all_urls>"]`.
- **Don't use ChatGPT / branded icons** — keep the brand name in text if
  relevant (e.g. "ChatGPT-style") but draw a unique icon. Using a copyrighted
  icon is an instant rejection.
- **Don't add `default_title`, `author`, `fingerprint`, `key` in
  `manifest.json`** when cleaning a cloned donor — they carry source-
  extension fingerprints; `default_title` falls back to `name` if removed.
- **Delete `_metadata` folder and all `_locales/*` except `en`** after
  cloning a donor — distances your build from the original at file-tree
  level.
- **Re-minify with different settings when relaunching on a second account**
  — identical minified bundles trip duplicate detection; tweak variable-name
  strategy / mangling level so the output diff is non-trivial.
- **If donor's `.js` is obfuscated** (single-letter variable names
  everywhere), abandon it — too costly to modify. Library files always look
  obfuscated (recognizable by `/* license / author */` header comment);
  ignore those when judging.
- **CSS / text / icon-only changes are sufficient code-side**; don't try to
  rename internal variable names — too brittle, not required by moderation.
- **Manifest v2 builds are no longer accepted for new extensions**; existing
  v2 extensions are being purged (~20–30% of the store, freeing 50K+ keyword
  slots). Always pick a v3 donor — porting v2 → v3 is non-trivial because
  v2's persistent background script becomes a v3 service worker that wakes
  on demand.
- **If moderation triggers on overspammed text once, subsequent re-uploads
  are scrutinized harder** — they may force progressively tighter keyword
  cuts. Better to ship clean Turgenev results the first time than to
  negotiate down from a flagged baseline.
- **Comma-separated lists of homogeneous items (brand names, file formats)
  are the most predictable moderation trigger** — even when accurate to your
  product. Distribute these inline across paragraphs rather than enumerating.
- **Don't enumerate file formats the extension doesn't actually handle** —
  moderation occasionally cross-references listing claims with the running
  build for "obvious" claims (file formats, integrations).
- **For products with running costs, the safer pre-monetization path is huge
  free quotas (e.g. 1,000 actions) via Paywall auth-only flow**, not an
  unauthenticated free extension. Paywall already collects auth → when you
  flip monetization later, the user base is enrolled and the switch is just
  a toggle, not re-onboarding.
