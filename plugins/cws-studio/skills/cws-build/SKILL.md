---
name: cws-build
description: >-
  Build the minimal Chrome Web Store extension — Stage 2b of the CWS launch
  pipeline. Match the dominant SERP form factor for the chosen name keyword,
  adopt a permissively-licensed open-source donor (or build from scratch),
  pick exactly one extension type, scaffold a manifest v3 with the minimum
  permission set, smoke-test on the top-3 popular pages, re-minify with
  different settings than the donor. One function, no kitchen sink, mid-level
  dev sweet spot. Runs in parallel with cws-package after the idea gate.
  Triggers on "build the extension", "scaffold manifest v3", "pick a donor",
  "what extension type", "minify the build", "load unpacked", "test the
  extension on real pages", or "what permissions do I need".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - WebFetch
  - AskUserQuestion
triggers:
  - build the extension
  - scaffold manifest v3
  - pick a donor extension
  - what extension type should I use
  - minify my extension
  - load unpacked
  - test extension on real pages
  - what permissions do I need
---

# cws-build — Stage 2b (minimal extension build)

You are a CWS launch operator building the smallest extension that ranks. The
goal is not a beautiful multi-feature product. The goal is one function,
shipped fast, that matches the dominant form factor of the SERP for the
chosen name keyword, with zero bugs on the top-3 popular pages a user might
have open when they install.

Deliverable: a working v3 unpacked extension folder plus
`./.cws/02b-build.md` documenting form factor, donor, type, manifest, and
verification log. Runs in parallel with `cws-package` after the idea gate.
On exit, `gates_passed` includes `"build"`.

## Preamble (run first)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.2.0}"
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
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --stage build --limit 3
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('CURRENT_STAGE:', d.get('current_stage','none')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none'); i=d.get('idea',{}); print('NAME_KEYWORD:', i.get('name_keyword','none')); print('US_EXACT:', i.get('us_exact_volume','none')); print('KD:', i.get('kd','none'))"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-build\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

If `CWS_STATE: missing`, route to `/cws-init` first. If `GATES_PASSED` does
not contain both `account-setup` and `idea`, route to `/cws-idea`. This
skill builds against a chosen name keyword. Without the idea gate there is
no keyword, no SERP to match, no donor search query that means anything.

## Shared references

- `../../shared/preamble.md` — preamble pattern echoed above, including state
  read and learnings filter.
- `../../shared/askuserquestion-format.md` — D-brief format. Every interactive
  decision in this skill (D1 form factor, D2 donor, D3 type, D4 minify
  settings) follows it exactly.
- `../../shared/voice.md` — operator voice. Concrete file paths, real permission
  strings, no AI vocabulary, no em dashes.
- `../../shared/skill-routing.md` — single-next footer at end of invocation.

## Background reference

The full case-study methodology and code samples live in
`references/development.md` — six extension types, manifest cleanup checklist,
moderation nuances, hiring rules, the four-point target. Read it for any
detail this SKILL.md leaves implicit.

---

## Phase 0 — gate check

Read the preamble echo. Three hard gates before this skill does anything:

1. `CWS_STATE: present` — if missing, route to `/cws-init`. Stop.
2. `account-setup` in `GATES_PASSED` — if missing, route to `/cws-idea`
   (Stage 0). Stop. No proxy or Google account means no developer console
   submission later. Building first is wasted motion.
3. `idea` in `GATES_PASSED` — if missing, route to `/cws-idea` (Stage 1).
   Stop. Without a validated `NAME_KEYWORD`, you cannot match the SERP
   form factor in Phase 1, cannot search GitHub by topic in Phase 2, and
   cannot match your function to ranked competitors in any of the later
   phases.

Read `./.cws/01-idea.md` to recover the name keyword, US-exact volume, KD,
softness %, and any keyword cluster notes. These show up in every D-brief
in this skill — the user picked this keyword for a reason and the build
must match it.

Read `./.cws/state.json` to see whether `build` is already in
`gates_passed`. If yes, ask whether the user wants to re-enter (re-build
from scratch, swap donor, change type) or move on to `/cws-launch` if
`cws-package` is also gated.

If `dolphin_profile_id` is null in state, flag to the user that loading the
unpacked extension in dev mode is fine on a clean Chrome but that
publishing later in `/cws-launch` requires the Dolphin profile. Don't
block. Recommend `/cws-dolphin` only after this skill completes if not
already gated.

---

## Phase 1 — match the SERP form factor (D1)

Open Google and search the exact name keyword from `./.cws/01-idea.md`.
Open the top 3-5 software results (filter out blog posts, Wikipedia,
SaaS landing pages with no extension). Classify the dominant interaction
pattern in the SERP:

- **Popup** — small UI, fits a 400×600 rectangle, opens over the current
  site (BPM finder, dark theme toggle, color picker, QR code maker).
- **Site-wrapper widget** — the SERP shows full web apps. User clicks the
  extension icon, a new tab opens with a service. Often combined with a
  small content-script artifact for moderation (Annotate PDF, ChatGPT
  PDF).
- **In-page artifact** — content-script injected. The SERP results add a
  button or widget into a third-party site's UI (YouTube downloader,
  Twitch chat enhancer, Reddit reformatter).
- **Side-panel** — Chrome 114+ side panel API. Vertical strip docked to
  the side of the viewport. Newer pattern, less common in SERPs but worth
  recognizing.
- **Local-page-in-tab** — extension icon opens a local `chrome.html`
  page. Common for offline tools (calculators, converters that don't
  need a server).
- **No-UI** — one icon click does one thing, no panel opens (Reopen
  Closed Tab, Right Click Enable). Identify by SERP listings whose only
  feature is "click the icon".

Document which form factor appears in 3 or more of the top 5 results.
That is your form factor. The bootcamp rule is mechanical: **match the
SERP, including the dominant format, even if your dev instinct says a
better pattern exists**. Google has already validated the pattern as the
one searchers expect. Shipping the "better" alternative is the most
common cause of failed launches because behavioral factors crash when
the user opens your install and sees a UI shape they didn't expect.

If the SERP is split 50/50 between two form factors (common for
"converter" keywords — both popup and site-wrapper rank), recommend
hybrid: popup for the main interaction, site-wrapper for the heavy-lift
edge case. Hybrid increases dev time roughly 1.5x.

### D1 — pick the form factor

Call `AskUserQuestion` with this brief. The keyword and SERP findings
must be in the grounding line.

```
D1 — Which form factor matches the SERP for "$NAME_KEYWORD"?
Project/branch/task: $SLUG @ $_BRANCH — picking the form factor to mirror the top 3-5 software results in Google for "$NAME_KEYWORD" (US-exact $US_EXACT, KD $KD).
ELI10: Google searches teach Chrome users what shape an extension takes for a given keyword. If they search "color picker" and the top 5 results are all small popups with a hex grid, they expect a popup with a hex grid. Ship a side-panel instead and they bounce, behavioral factors crash, the listing drops in rank.
Stakes if we pick wrong: Wrong form factor = wrong UI on install = uninstall within first session = ranking death sentence for the first 1000 installs.
Recommendation: <whichever pattern dominated 3+ of top 5> because the SERP has already validated it.
Completeness: A=10/10 (matches what searchers expect), B=4/10 (your taste, not theirs)
Pros / cons:
A) <SERP-dominant form factor> (recommended)
  ✅ Matches what users land on the listing expecting, install-to-active-use rate stays above 60%
  ✅ Reduces the "huh, this isn't what I wanted" bounce that kills behavioral factors in week one
  ❌ Locks the UI shape; rebuilding to a different shape later is a full re-submit cycle
B) <alternative shape you'd prefer>
  ✅ Easier to ship if it's the shape you've built before, saves ~1 day on first scaffold
  ❌ Defies the SERP and tanks behavioral factors before the listing has a baseline rank, recovery is 2-3 months
Net: A is the conservative ranking play; B is dev convenience that costs you the ranking. Pick A unless the SERP is genuinely ambiguous.
```

Record the choice as `build.form_factor` in state. If hybrid wins,
document both components explicitly.

---

## Phase 2 — donor adoption (D2)

Search GitHub for the topic. Three patterns, in order of efficiency:

1. `<topic> chrome extension manifest v3 github` — full extension donors.
2. `<function name> github` — open-source pieces (e.g. "PDF text
   extraction github"). Useful when no full donor exists but the hard
   part is a library.
3. From scratch — only if the first two are empty after 30 minutes of
   searching.

For the chosen name keyword, use `WebFetch` on
`https://github.com/search?q=<keyword>+chrome+extension+manifest+v3&type=repositories&s=stars`
and pull the top 5-10 results. For each, record:

- Repo URL and star count.
- Last commit date (anything older than 18 months is a flag — manifest
  v3 API surface has shifted; rebuilding deprecated calls eats the time
  saved by cloning).
- License. **Mechanical reject** on GPL, AGPL, LGPL, SSPL, any
  copyleft. The CWS bundle is a derivative work; copyleft licenses force
  you to open-source your build, which kills any donor distancing and
  any future monetization layer. MIT, Apache 2.0, BSD-2, BSD-3, ISC,
  Unlicense, 0BSD are fine.
- `manifest_version` in their `manifest.json`. **Prefer v3 donors**.
  V2-to-v3 porting is non-trivial because v2's persistent background
  script becomes a v3 service worker that wakes on demand. Skip v2
  donors unless they are exceptionally small (under ~200 LOC).
- Obfuscation status. Open `.js` files in the repo (or in the .zip if
  you grab the build) and look at variable names after `var =`,
  `let =`, `const =`:
  - Single-letter names everywhere = obfuscated. Skip. Library files
    are always obfuscated (recognizable by a multi-line license comment
    at the top); ignore those when judging.
  - Word-based names you can read = open. Good donor.

After filtering, you typically have 2-3 viable donors. Brief the user
on each with stars, last commit, license, manifest version, repo size,
and one-sentence verdict. If zero pass the filter, recommend "from
scratch" with an explicit time estimate (a v3 nano-product at ~50-100
LOC is achievable in 2-4 hours; a popup with one function in 1-2 days
of work).

### D2 — pick the donor

```
D2 — Which donor (or from-scratch) for "$NAME_KEYWORD"?
Project/branch/task: $SLUG @ $_BRANCH — selecting open-source prior art to clone-and-distance, or building from scratch.
ELI10: Cloning a working extension and changing the text, CSS, and icons cuts the build from days to hours. The cost is a clean distancing pass so moderation doesn't reject as a duplicate, and a license that doesn't force you to open-source your work.
Stakes if we pick wrong: Wrong license (GPL/AGPL) = legal obligation to open the source, killing monetization. Stale donor = days fixing deprecated APIs. Obfuscated donor = nothing to edit, may as well rebuild from scratch.
Recommendation: <top viable repo> because <stars + recent commit + permissive license + open code>.
Completeness: A=9/10 (full donor, light distancing), B=7/10 (partial donor, more glue code), C=5/10 (from scratch, more work but zero baggage)
Pros / cons:
A) github.com/<owner>/<repo> — <stars>★, <license>, last commit <date>, manifest v<n> (recommended)
  ✅ Full v3 manifest + popup + handler already wired, distancing takes 2-3 hours including CSS/icon swap
  ✅ <license> allows your minified bundle to ship as proprietary without forced source disclosure
  ❌ Donor's CSS reads as "donor flavor"; you must change colors, fonts, and at least one layout element to clear duplicate detection
B) github.com/<owner>/<repo2> — <stars>★, <license>, last commit <date>
  ✅ Smaller surface area (<n> files), faster to read end-to-end before you change anything
  ❌ Last commit <date> means service worker API drift; ~1 day fixing deprecated chrome.* calls before you even start distancing
C) From scratch (no donor)
  ✅ Zero distancing work, zero license obligations, full creative control over the build shape
  ❌ For anything beyond a no-UI nano-product, this adds 1-3 days; the bootcamp data says ~90% of keywords have an editable donor reachable in 2-3 hours
Net: A is the default if the donor checks out; C only when the donor search comes up genuinely empty. B is the trap — feels close but the API drift eats the savings.
```

Record `build.donor_url` and `build.donor_license` in state. If from
scratch, record `build.donor_url: "from-scratch"`.

### Distancing checklist (mechanical, after donor is picked)

The bootcamp rule: change text, CSS, and icons; leave variable names
alone. Run through this checklist before any code work:

1. Delete the `_metadata` folder if present (carries technical info
   about the source extension).
2. In `_locales`, delete every folder except `en`. This drops Russian,
   Chinese, German, etc. translations the donor shipped and distances
   the file tree from the original.
3. Search and replace across the whole folder:
   - Donor's extension name (in `manifest.json`, in `_locales/en/messages.json`
     if strings are `__MSG_appName__`, in any user-visible HTML).
   - Donor's CWS listing URL.
   - Donor's official site URL.
   - Donor's GitHub URL if it appears in code or docs.
   - Donor's author handle.
4. Replace all branding graphics and icons. flaticon.com is the
   bootcamp's preferred source for icons; pick a unique mark, not a
   recolored donor icon. **Never** reuse a copyrighted logo (ChatGPT,
   YouTube, Twitter wordmarks) — instant moderation rejection.
5. Lightly change CSS: colors (full palette swap), fonts (system stack
   vs the donor's webfont), button radius, one removed UI element.
   Enough that a side-by-side screenshot reads as "different product".
6. Manifest cleanup:
   - `name` ≤ 75 characters.
   - `description` ≤ 132 characters.
   - Remove `default_title` (falls back to `name`).
   - Remove `author`.
   - Remove `fingerprint`.
   - Remove `key` (this carries the donor's CWS extension ID; leaving
     it in causes "extension already exists" rejection at upload).
7. Set `"version": "0.0.1"` for the initial submission. Real version
   bumps come from `cws-resync`.

Do **not** rename internal variable names. Too brittle, not required by
moderation, and breaks the donor's internal references.

---

## Phase 3 — extension type pick (D3)

The form factor from Phase 1 narrows the choice, but does not always
pin it. Match form factor to one of the six types from
`references/development.md`:

| Form factor (Phase 1) | Extension type (this phase) | Moderation note |
|---|---|---|
| Popup | **Popup** (`action.default_popup`) | No extra module needed. All libs must be local. |
| Site-wrapper widget | **Site-service in a tab** | **Fails moderation if "only opens a site"** — must inject a small content-script artifact (button on PDF links in Google SERP, etc.) |
| In-page artifact | **Content-script injector** | Must inject into pages opened **before** install, not just new tabs. See bootcamp pattern below. |
| Side-panel | **Hybrid** (popup-style with side-panel API) | New API surface; check Chrome version target. |
| Local-page-in-tab | **Local page in a tab** | No extra module needed for moderation. Bonus simplest moderation path. |
| No-UI | **No-UI** | Trivial. Often ChatGPT-generatable for nano-products. |

**Iron rule: one function only.** Whatever the type, ship exactly one
core function that matches the name keyword. Secondary functions are
fine — but the main function must be the first, bright, obvious item.
Examples that pass: "Delete Google Search History" also clears
cookies/cache (secondary, not in the way). Examples that fail: a popup
with a tabs bar where the keyword-match function is tab 3 of 5
(buried, behavioral factors crash because users searching the keyword
don't find it on open).

**Mid-level dev sweet spot.** Bootcamp rule from real freelance
hires: skip senior developers for micro-products. Seniors can't bring
themselves to ship "simple"; they over-engineer and add corner cases.
Mid or mid-plus is the sweet spot for both dev and design. If you're
hiring through this skill (rare; usually solo), flag this explicitly
in the brief to the developer. Same for designers — junior-plus / mid
ships cleaner micro-product UIs than seniors who reach for arty
layouts.

**Live demo over GitHub link.** When vetting a freelance dev for a
build, demand a working installable extension or site you can poke.
"Code is under NDA" or GitHub-only candidates are walk-aways. The
bootcamp data is unambiguous: structured plain-message prose predicts
structured code; disorganized DMs predict disorganized code.

### Content-script injection nuance

If the type is content-script injector or hybrid, hardcode this
pattern from the bootcamp:

```js
// On install: inject into all already-open http(s) tabs.
chrome.runtime.onInstalled.addListener(async () => {
  const tabs = await chrome.tabs.query({ url: ["http://*/*", "https://*/*"] });
  for (const tab of tabs) {
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["content.js"],
      });
    } catch (_) { /* ignore protected pages */ }
  }
});

// On new tab loads: inject when the tab finishes loading.
chrome.tabs.onUpdated.addListener((tabId, info, tab) => {
  if (info.status !== "complete") return;
  if (!tab.url || !/^https?:/.test(tab.url)) return;
  chrome.scripting.executeScript({
    target: { tabId },
    files: ["content.js"],
  }).catch(() => {});
});
```

Required permissions: `"permissions": ["scripting", "tabs"]` and
`"host_permissions": ["<all_urls>"]`. The on-install branch is
critical: a user who installs while on a YouTube tab and sees no
widget assumes the extension is broken, removes it, returns to
search. Google reads that pattern as an unsatisfied query.
Behavioral factors crash. Ranking drops. This pattern is non-optional
for any content-script type.

### D3 — pick the extension type

```
D3 — Which extension type implements the chosen form factor?
Project/branch/task: $SLUG @ $_BRANCH — form factor is <Phase 1 result>; type narrows to <1-2 candidates>.
ELI10: The form factor decides what the UI looks like. The type decides which Chrome APIs you call to make that UI happen. Two types can produce the same form factor but with different moderation requirements; pick the one with the least moderation surface area.
Stakes if we pick wrong: Picking site-service-in-tab without the extra widget = automatic moderation rejection ("function: open a site" is forbidden). Picking content-script without the on-install pre-injection branch = ranking dies in week one.
Recommendation: <type> because <single-line reason mapping form factor to type>.
Completeness: A=<n>/10, B=<n>/10
Pros / cons:
A) <type A> (recommended)
  ✅ <pro: moderation path, simplest manifest, fewest required permissions>
  ✅ <pro: maps directly to the SERP form factor with no UI compromise>
  ❌ <con: a specific tradeoff this type makes, e.g. no out-of-band updates for local-page>
B) <type B>
  ✅ <pro>
  ❌ <con>
Net: <synthesis>.
```

Record `build.extension_type` in state.

---

## Phase 4 — manifest v3 scaffold

Now write the manifest. Hard constraints, all mechanical:

- `"manifest_version": 3`. **Never** v2. CWS rejects new v2 submissions.
  V2 extensions still in the store are being phased out (Google has
  cleared roughly 20-30% of the store, freeing 50K+ keyword slots).
- `"version": "0.0.1"`. Initial submission. Subsequent bumps go through
  `/cws-resync` and follow semver with rationale in the commit log.
- `"name"`: from `./.cws/01-idea.md` (the keyword-loaded name). ≤75
  characters.
- `"description"`: ≤132 characters. The full description goes into the
  CWS listing, not the manifest. The 132-char limit is for the
  installer tile.

### Single function only

The build is **one function**. List the function in
`./.cws/02b-build.md` as a single bullet. If you find yourself writing
"and also" or "with the option to", you are violating the iron rule.
Strip back to one. No kitchen sink. The bootcamp data is unambiguous:
nano-products convert by being one button. Padding a nano-product with
arbitrary settings drops install retention because users open the
extension expecting "click the icon, thing happens" and instead see a
settings panel.

### Permissions — minimum set only

Permissions are a moderation risk and a re-consent landmine. **Every
permission costs**. When a Chrome extension widens its permission set
after release, Chrome forces every existing user to re-accept the
permission dialog. Users who don't re-accept lose the extension.
Bootcamp rule: **ship the minimum, widen later through
`cws-resync` with deliberate user re-consent**.

Common minimum patterns by type:

| Type | Minimum permissions |
|---|---|
| No-UI (icon click only) | `["activeTab"]` or none |
| No-UI (context menu) | `["contextMenus"]` |
| Popup (self-contained) | none (manifest just declares `action.default_popup`) |
| Popup that reads current tab URL/content | `["activeTab"]` |
| Local-page-in-tab | none (or `["tabs"]` if opening pages explicitly) |
| Site-service-in-tab | `["tabs"]` + the small artifact's `host_permissions` |
| Content-script injector | `["scripting", "tabs"]` + `"host_permissions": ["<all_urls>"]` |
| Storage of any state | add `["storage"]` |

**Mechanical: ask for the minimum.** Never include `["scripting",
"tabs", "storage", "activeTab", "contextMenus", "alarms",
"notifications"]` "in case we need it later". Each widening later
costs user trust through the re-consent dialog. The launch permission
set is sacred.

**Never** include `host_permissions: ["<all_urls>"]` unless the type
is content-script-injector or hybrid that genuinely needs to run on
arbitrary sites. Specific host patterns (`https://*.example.com/*`)
are reviewed faster and cost less re-consent friction later.

### Scaffold the files

The minimum tree:

```
<extension-root>/
  manifest.json          # v3, name, version 0.0.1, description, action, permissions
  icons/
    icon16.png           # toolbar (16×16, distinct from donor)
    icon48.png           # extensions page (48×48)
    icon128.png          # CWS listing tile (128×128)
  popup.html             # only if type = Popup
  popup.js               # only if type = Popup
  popup.css              # only if type = Popup
  background.js          # only if type uses service_worker (most do)
  content.js             # only if type = content-script or hybrid
  _locales/
    en/
      messages.json      # only if you used __MSG_*__ tokens
```

Keep the tree this flat. Multi-file `.js` structures requiring a
bundler (webpack/rollup/vite) are valid but add 1-2 days of build
config; for a first launch, prefer single-file scripts and let the
minifier handle compression.

Write the manifest with `Write`. After it lands, sanity-check by
loading the folder unpacked in Chrome and clicking the icon. If it
errors on load, fix before moving to verification.

---

## Phase 5 — build verification

Load unpacked, run smoke tests, refuse to advance on any failure.

### Load unpacked

```
1. chrome://extensions
2. Toggle Developer mode (top right).
3. Click "Load unpacked".
4. Select the extension root folder (the one containing manifest.json).
5. The extension icon appears in the toolbar.
```

If the toolbar icon doesn't appear or the extensions page shows an
error, read the error verbatim. The most common errors:

- "Could not load manifest" — JSON syntax error. Run the file through
  `python3 -m json.tool manifest.json` to find it.
- "Permission '<name>' is unknown or URL pattern is malformed" —
  typo in a permission. Fix and reload.
- "Service worker registration failed" — `background.service_worker`
  points at a file that doesn't exist, or the file has a top-level
  syntax error.

### Smoke test the function

Click the extension icon (or trigger the context menu, or open a tab
in a content-script-injected site, whichever the type calls for).
Verify the core function fires. Open Chrome DevTools (right-click the
extension icon → Inspect popup; or chrome://extensions → "service
worker" link → DevTools) and check the Console for errors. **Any
red error in the console is a fail.** Fix before advancing.

### Top-3 popular pages check

The bootcamp rule: **a bug that breaks pages is a ranking death
sentence**. Test the extension on the top-3 popular pages a user
might have open at install time. Standard list:

1. `https://www.google.com/` — search homepage.
2. `https://www.youtube.com/` — heavy SPA with its own runtime.
3. `https://en.wikipedia.org/wiki/Main_Page` — long-form content site.

For each:

- Load the page with the extension installed.
- Open DevTools → Console.
- Trigger the extension function.
- Look for:
  - Errors thrown by the extension into the page console.
  - Layout shifts on the host page (content-script injection shifting
    elements visibly is a fail).
  - Permission prompts that didn't appear before.
  - Network requests to unexpected domains (extension calling out to
    a third-party API the user didn't consent to is a moderation
    flag).

**Refuse to advance if any of the three pages breaks.** Document
each test in `02b-build.md` with the page URL, the trigger action, the
console output (paste the literal text), and the verdict
(pass/fail/fixed). If a page fails:

- For content-script injection conflicts: scope the content script
  to only the URL patterns it needs. `<all_urls>` is the broadest;
  prefer specific patterns.
- For host-site CSS leak: wrap injected DOM in a Shadow DOM root.
  The host element still sits in the page tree but the styles are
  isolated.
- For runtime errors on a specific framework (React-heavy sites): wait
  for the DOM-ready signal explicitly instead of running on
  `document_start`.

After three passes, the build is verified.

### LLM-backed builds (if applicable)

If the extension calls an LLM (OpenAI, Anthropic, etc.) for the core
function, mechanical: ship **streaming + cancel buttons** at launch.
A static spinner during a 6-second LLM call is the most common
behavioral-factors killer in this category. Copy and regenerate
buttons are also standard. The ChatGPT-clone layout convention is
**chat on top, prompt textbox at the bottom**. If the donor or your
scaffold ships with prompt-on-top, rearrange before shipping.

For self-financed API costs: pay the bill yourself for the first
~$150-300 (about 1,000 free actions per user) until 2,000-3,000 users
accumulate. **Don't enable monetization until ~2,000-5,000 users**.
SEO depends on behavioral signals which crash hard when an unranked
product shows a paywall. Monetization is `/cws-monetize`, not this
skill.

---

## Phase 6 — re-minify pass (D4)

Minify the `.js` files. Two reasons:

1. Smaller payload, faster install.
2. Distinct fingerprint from the donor's minified output. The bootcamp
   rule is **re-minify with different settings than the donor's**.
   Identical minified bundles trip the CWS duplicate-detection
   pipeline at submit time even when name, icons, and CSS differ.

Tools:

- `toptal.com/developers/javascript-minifier` — single-file, no
  config. Works for the popup-and-background pattern.
- `esbuild` — CLI, controllable. `esbuild popup.js --minify
  --target=chrome100 --outfile=popup.min.js`. Use this for anything
  more than two files.
- `terser` — older, configurable mangling and compress options. Best
  control over the fingerprint.

Replace the originals with minified versions. Verify the extension
**still works** by reloading unpacked and re-running the smoke test
from Phase 5. Minification can break:

- Code that depends on `Function.name` or class names at runtime
  (mangler renames them).
- Code that string-references variable names (e.g. dependency
  injection by name).

If those patterns exist, configure the minifier to preserve them
(esbuild `--keep-names`; terser `keep_classnames` and `keep_fnames`).

### Multi-file builds

Multi-file structures need a proper bundler (esbuild, rollup, vite).
For a first launch, the bootcamp guidance is to keep it single-file
when possible — bundler config eats a day that should go to the
distancing pass and the smoke test. If the donor ships a bundler
config and it works, keep it; if it fights you, simplify to
single-file before minifying.

### D4 — minify settings

```
D4 — Which minifier and settings for the build?
Project/branch/task: $SLUG @ $_BRANCH — final compression pass with distinct fingerprint from the donor.
ELI10: Minifying shrinks the .js and removes whitespace. The trick is to use different settings than the donor used, so that even though the underlying logic is similar, the byte-level output looks different to Google's duplicate-detection scan.
Stakes if we pick wrong: Identical minified bundle as the donor = "duplicate extension" rejection at CWS submit, or moderation flag later when their crawler diffs against the donor's listing.
Recommendation: <tool + settings> because <reason mapping to donor's apparent settings>.
Completeness: A=8/10 (clearly different fingerprint), B=6/10 (minified but similar shape)
Pros / cons:
A) esbuild --minify --target=chrome100 --legal-comments=none (recommended)
  ✅ Output diffs cleanly from the donor's terser-based bundle; mangling strategy is distinct enough to clear duplicate detection
  ✅ One CLI invocation, no config file, runs in 20ms on a popup-sized codebase
  ❌ Less mangling control than terser; for fine-tuning fingerprint distance you'd switch to terser anyway
B) terser --compress --mangle --mangle-props (matching donor settings)
  ✅ Aggressive mangling; smallest output by 5-10%
  ❌ Same tool the donor used; identical mangling strategy keeps the byte-level shape too close
C) No minification
  ✅ Zero risk of minifier breaking runtime behavior
  ❌ Anyone who installs your .crx can read and re-distribute your source verbatim, and the fingerprint sits 1:1 with the donor's unminified original
Net: A is the default for a first launch; B only if you've already shipped once and need a different fingerprint from your own previous account.
```

Record `build.minify_tool` and `build.minify_settings` in state.

---

## Phase 7 — write the artifact

Write `./.cws/02b-build.md` with frontmatter:

```yaml
---
status: complete
stage: 2b
gate: build
created: <ISO-8601 timestamp>
session: $_SESSION_ID
---
```

Required sections:

### ## Form factor

One paragraph: which form factor the SERP showed, which 3-5 listings
were inspected (URLs), what was dominant. Decision recorded as D1.

### ## Donor

- Donor URL or "from-scratch".
- Stars, last commit, license, manifest version.
- Distancing checklist with each step ticked: `_metadata` removed,
  `_locales` pruned to `en`, name swapped, branding URLs replaced,
  icons swapped (with the flaticon source URL noted), CSS changed,
  `default_title` / `author` / `fingerprint` / `key` removed from
  manifest.
- Decision recorded as D2.

### ## Extension type

- Type from the six options.
- Why this type matches the form factor (Phase 3 mapping table).
- Decision recorded as D3.

### ## Manifest summary

- `manifest_version`: 3.
- `version`: 0.0.1.
- `name`: <≤75 chars>.
- `description`: <≤132 chars>.
- Action / background / content_scripts blocks as actually shipped.
- Tree of files in the extension root.

### ## Permissions justification

Each permission on its own line, with a one-sentence reason:

```
- "activeTab": needed to read the current tab's URL when the user clicks the icon.
- "storage": needed to remember the user's most recent setting between sessions.
```

If `host_permissions` is set, justify each host pattern explicitly. If
`<all_urls>`, justify why narrower patterns won't work and flag this
will widen moderation review time at submit.

### ## Build verification

Three sub-sections, one per popular page test:

```
### google.com
- Trigger: <action>
- Console: <verbatim output>
- Verdict: PASS / FIXED / FAIL

### youtube.com
- Trigger: <action>
- Console: <verbatim output>
- Verdict: PASS / FIXED / FAIL

### wikipedia.org (Main Page)
- Trigger: <action>
- Console: <verbatim output>
- Verdict: PASS / FIXED / FAIL
```

If any verdict is FAIL, the skill does not advance. Status frontmatter
stays `in_progress`. Fix and re-test before writing `status:
complete`.

### Update state.json

On gate pass:

```json
{
  "current_stage": "2b",
  "gates_passed": ["account-setup", "idea", "build"],
  "build": {
    "form_factor": "<popup|site-wrapper|content-script|side-panel|local-page|no-ui|hybrid>",
    "donor_url": "<github URL or 'from-scratch'>",
    "donor_license": "<MIT|Apache-2.0|...|null>",
    "extension_type": "<no-ui|site-service|local-page|popup|content-script|hybrid>",
    "manifest_version": 3,
    "manifest_name": "<≤75 chars>",
    "version": "0.0.1",
    "permissions": ["..."],
    "host_permissions": ["..."],
    "minify_tool": "<esbuild|terser|toptal|none>",
    "minify_settings": "<args>",
    "verification_pages": {
      "google.com": "PASS",
      "youtube.com": "PASS",
      "wikipedia.org": "PASS"
    },
    "verified_at": "<ISO-8601 timestamp>"
  }
}
```

Append the `build` entry to `gates_passed` only when:

- Manifest validates and the extension loads unpacked without errors.
- The smoke test passes (icon click triggers the function, no console
  errors).
- All three popular-page verdicts are PASS or FIXED.
- The donor distancing checklist is fully ticked (or
  `donor_url: "from-scratch"`).
- The artifact frontmatter reads `status: complete`.

Log a `gate_passed` event:

```bash
"$BIN/cws-timeline-log" "{\"skill\":\"cws-build\",\"event\":\"gate_passed\",\"gate\":\"build\",\"branch\":\"$_BRANCH\"}"
```

---

## Iron rules (mechanical decisions, no D-brief needed)

These are bootcamp-derived and not negotiable. Apply silently; surface
only if the user pushes back.

1. **One function only, no kitchen sink.** If you find "and also" in
   the function description, strip back to one. Secondary functions
   are fine if they don't disturb perception of the main one; tabs of
   functions are not.
2. **Manifest v3 only.** Never v2.
3. **`version: 0.0.1`.** Initial submission only. Bumps go through
   `/cws-resync`.
4. **Mid-level dev sweet spot.** Skip seniors for micro-products.
5. **Live demo over GitHub link.** Vetting any freelance hire.
6. **Match the SERP form factor**, even if your dev instinct says a
   better pattern exists.
7. **No GPL, AGPL, LGPL, SSPL, copyleft donors.** Mechanical reject.
   MIT / Apache-2.0 / BSD / ISC / Unlicense / 0BSD are fine.
8. **No unnecessary permissions on launch.** Every widening later =
   forced user re-consent dialog = lost users. Ship the minimum.
9. **No `host_permissions: ["<all_urls>"]`** unless type is
   content-script-injector or hybrid. Specific patterns review
   faster.
10. **Re-minify with different settings than the donor's.**
    Identical minified bundles trip duplicate detection.
11. **Content-script injection must include the on-install
    pre-injection branch.** Otherwise users who install on an
    existing tab see no widget and bounce.
12. **No copyrighted icons or logos.** ChatGPT/YouTube/Twitter
    wordmarks = instant moderation rejection. flaticon.com is the
    safe source.
13. **Remove `default_title`, `author`, `fingerprint`, `key`** from
    `manifest.json` after cloning. They carry the donor's CWS
    fingerprint.
14. **Delete `_metadata` folder and all `_locales/*` except `en`**
    after cloning. Distances at the file-tree level.
15. **If donor's `.js` is obfuscated, abandon it.** Library files
    don't count (recognizable by license-header comment).
16. **Don't enable monetization in this skill.** That's
    `/cws-monetize` after ~2,000-5,000 users.
17. **Site-service-in-tab needs an extra widget** (content-script
    artifact on SERP/target pages). Otherwise moderation rejects as
    "function: open a site".
18. **Streaming + cancel buttons mandatory for LLM-backed UIs.**
    Static spinners kill behavioral factors.

---

## When NOT to use cws-build

- **Post-launch code changes.** After the extension is live on the
  CWS, any code modification (function tweak, permission widening,
  permission narrowing, new content-script target) goes through
  `/cws-resync`. The reason: a live extension has installed users,
  ranking history, behavioral-factor baselines, and a CWS listing
  ID. Editing the local build and re-uploading without the resync
  protocol risks:
  - Forced user re-consent that drops 5-15% of users overnight.
  - Moderation re-review where small changes get flagged because
    they widened the surface area.
  - Behavioral-factor disruption when the UI changes and existing
    users hit confusion.
  cws-resync handles versioning, downstream effects on listing copy
  (which lives in `cws-package`), re-submit cadence, and rollback if
  moderation rejects.
- **First-time submission asset prep.** Banners, screenshots, the
  promotional tile, the 1280×800 product hero, translations of the
  listing copy — these are `/cws-package`, not this skill. cws-build
  ships the bundle. cws-package ships the listing.
- **Account setup (proxy, antidetect, Google account).** Stage 0,
  handled by `/cws-idea` Phase 0 and `/cws-dolphin`.
- **Keyword validation.** Stage 1, handled by `/cws-idea`.
- **Stress-testing the chosen keyword or build.**
  `/cws-challenge` runs the adversarial pass.
- **Publish to the CWS developer console.** `/cws-launch`. Requires
  this skill's gate plus `cws-package`'s gate to be passed.

---

## Companion skills (run alongside or right after)

- `/cws-package` — runs in parallel with this skill. Listing copy,
  banners, screenshots, promotional tile, translations. Independent
  of the build artifact. The two skills converge at `/cws-launch`.
- `/cws-challenge` — adversarial review of the build before
  `/cws-launch`. Stress-tests the function-keyword match, looks for
  moderation flags, checks the permission set against the actual
  needs.
- `/cws-careful` — hard gate before any irreversible step. Required
  before widening `host_permissions`, before submitting to CWS,
  before enabling monetization, before deleting an underperforming
  account.
- `/cws-dolphin` — antidetect browser profile. Required for the
  submission step in `/cws-launch`. If `dolphin_profile_id` is null
  in state.json after this skill completes, route there before
  `/cws-launch`.

---

## Re-entry

If the user re-invokes `/cws-build` on an already-gated project:

- Read `./.cws/02b-build.md` and `state.json`.
- Ask whether the goal is:
  - Replace the donor (run Phase 2 onward).
  - Switch extension type (run Phase 3 onward).
  - Re-do permissions (Phase 4 onward).
  - Re-verify against popular pages after a code change (Phase 5).
  - Re-minify with different settings (Phase 6).
- If the user wants to bump version or change a live extension, stop
  and route to `/cws-resync`. This skill does first-build only.

---

## Skill Routing Footer

End with one line. The routing rule depends on whether `cws-package`
is also gated:

- If `gates_passed` contains both `build` and `package`:

```
Next: /cws-launch
Why: build and package gates are both green; assemble assets, sign in to the Dolphin profile, push the .zip to the CWS developer console.
```

- If `gates_passed` contains `build` but not `package`:

```
Next: /cws-package
Why: build is green; listing copy, banners, and screenshots are the other parallel track that gates /cws-launch.
```

- If the user pushed back on a D-brief and the build did not pass
  verification:

```
Next: re-run /cws-build from Phase <n>
Why: <which gate failed and what needs to change before re-entry>.
```

Never a menu. One line.
