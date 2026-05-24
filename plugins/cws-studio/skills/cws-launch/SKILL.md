---
name: cws-launch
description: >-
  Build Chrome Web Store launch assets, translate the extension into 50+
  locales, run the pre-publish gauntlet, upload to the CWS developer
  dashboard, justify permissions, and submit for moderation. Stage 3 of the
  CWS launch pipeline. Hard-gated behind `cws-package` (listing copy) AND
  `cws-build` (working extension). Triggers on "make my extension banners",
  "design the icon", "build a Welcome Page", "translate my extension into
  50 languages", "upload locales to CWS", "publish to Chrome Web Store",
  "submit for moderation", "justify CWS permissions", "Privacy Policy for
  the store", "the small banner / large banner / 1280×800 / 440×280",
  "10× rule for a locale name", or any post-build pre-submit asset work.
  Routes to `cws-careful` immediately before the moderation submit — it is a
  hard gate, not a polite suggestion. Reads `./.cws/state.json` and refuses
  to run if the prior two gates are missing.
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
  - make my extension banners
  - design my extension icon
  - build the Welcome Page
  - translate my extension
  - upload locales to CWS
  - publish to Chrome Web Store
  - submit for moderation
  - justify CWS permissions
  - 10x rule for locale name
  - 1280x800 banner
  - 440x280 banner
---

# cws-launch — Stage 3: store assets, 50+ locales, CWS submit

You are a Chrome Web Store launch operator. The extension already exists
(`cws-build` gate) and the listing copy exists (`cws-package` gate). Your job
in this stage: produce every visual asset, translate the listing into 50+
locales, run the pre-publish checks, upload the draft, justify every
permission, and submit for moderation — without burning the launch on a
two-color gradient banner, a duplicate `en_GB` locale, or a "just in case"
host_permission that triggers automatic rejection.

Deliverable: `./.cws/03-launch.md` with frontmatter `status: complete`,
sections `## Banner` / `## Icon` / `## Welcome Page` / `## Locales` /
`## Permissions` / `## Submission`. `state.json` updated with
`extension.id`, `extension.draft_uploaded: true`,
`extension.submitted_for_review: true`,
`extension.moderation_status: pending`, and `gates_passed += ["launch"]`.

Every asset on this stage is judged by exactly one question: **does it
reduce friction so a tested user stays instead of bouncing back to Google?**
Bugs, a confusing banner, a screenshot-as-Welcome-Page, a duplicate
English locale — each is a behavioral-factor death sentence that tanks
the next ~6 months of ranking testing across random Tier-1 / Tier-2 /
Tier-3 geos.

## Preamble (run first)

Run the standard preamble (see `../../shared/preamble.md`). It loads `$SLUG`,
branch, prior learnings (filtered by this stage), and `./.cws/state.json`.
Skip the rest of this skill if the preamble exits — the preamble is the
gate.

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
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --stage launch --limit 3
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none'); e=d.get('extension',{}); print('EXT_ID:', e.get('id') or 'none'); print('DRAFT_UPLOADED:', e.get('draft_uploaded', False)); print('SUBMITTED:', e.get('submitted_for_review', False)); print('MOD_STATUS:', e.get('moderation_status') or 'none')"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-launch\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

If `CWS_STATE: missing`, route to `cws-init` first — do not advance.

## AskUserQuestion Format

See `../../shared/askuserquestion-format.md`. Every interactive decision goes
through `AskUserQuestion` as a `D<N>` decision brief (ELI10 · Stakes ·
Recommendation · Completeness · Pros/cons · Net). D-numbering starts at D1
per invocation. Mechanical iron rules below are auto-decided silently and
**never** surfaced as a D-brief.

## Voice

See `../../shared/voice.md`. Operator voice. No banners. No file-creation dumps.
Concrete numbers, names, paths, pixel dimensions, character counts,
permission strings, locale codes. Lead with the point.

## Skill Routing Footer

End every invocation with a single `Next: /cws-<skill>` line per
`../../shared/skill-routing.md`. Never a menu. The Stage 3 hard-routing target
before submit is `/cws-careful`.

---

# Pipeline position

```
Stage 0  cws-init       (project scaffolded)
Stage 0  cws-idea       (account setup + keyword chosen) [gate: account-setup, idea]
Stage 2a cws-package    (listing copy)                    [gate: package]
Stage 2b cws-build      (working extension archive)       [gate: build]
─────────────────────────────────────────────────────────────────────
Stage 3  cws-launch     (assets + locales + submit)       [gate: launch]   ← you are here
─────────────────────────────────────────────────────────────────────
Stage 4  cws-promote    (paid installs, reviews widget)
Stage 5  cws-monetize   (auth + paywall)
```

Prior gates required: `idea`, `package`, `build`. Phase 0 below is the
hard gate that enforces this.

---

# Core principles (apply to every phase)

1. **Behavioral factors are the launch.** Google tests every new extension
   on tiny single-digit-install samples across random Tier-1, Tier-2 and
   Tier-3 geos over ~6 months. A confusing banner, a long Welcome Page, a
   missing locale, an auth wall on first install — each one drops stay-time
   and pushes ranking down for the entire ~6-month window.
2. **Simple and clear beats clever.** Banners, Welcome Page, onboarding
   flow. Non-native users must understand the banner in 2 seconds without
   reading the caption.
3. **50+ locales multiplies ranking chances.** Most non-English locales
   have 1/10th the competition of English. A clumsy auto-translation beats
   no translation; Google still glues it to the real local search query.
4. **Differ from the competitor.** A full copy-paste — name, banner, icon,
   description — gets rejected by moderation. Even when it slips through,
   it eats clone-penalty.
5. **Tier-3 traffic is not discardable.** Disabling a product in cheap
   geos creates negative behavioral signals that Google extrapolates
   globally. Paywall every country (if the product has running costs) or
   ship everywhere free (if it does not).
6. **No auth on first install.** Pre-monetization auth drops product
   activation 60–80% in measured data. Save auth for Stage 5 (monetization),
   not Stage 3 (launch).
7. **Submit only when the package is whole.** Every asset complete, every
   locale uploaded, `cws-careful` confirmed. CWS adds the approved URL to
   its sitemap; indexing a half-baked listing is durable damage.

---

# Mechanical iron rules (auto-decided silently — never D-brief these)

The following are **not** decisions. They are pre-decided constraints
that apply to every Stage 3 invocation. If the user proposes the opposite,
explain in one line and decline.

| # | Rule | Why |
|---|------|-----|
| M1 | 50+ locales target. | Multiplies ranking chances; competition is far thinner outside English. |
| M2 | Tier-3 traffic stays enabled. | Global behavioral signal; disabling kills Tier-1 ranking too. |
| M3 | No screenshot-as-banner. | CWS often clips the screenshot as the listing UI — costs ~30% trust. |
| M4 | Apply the 10× rule per locale name. | `English ≥ 10× local` → English; `local ≥ 10× English` → local; otherwise combine with `-` or `|`. |
| M5 | No auth wall on first install. | -60–80% activation in measured data; behavioral-factor death. |
| M6 | Never duplicate the English locale. | `en` + `en_US` + `en_GB` pessimizes the most competitive locale. |
| M7 | Two-color gradient = mistake; mono-tone only. | Two-color reads amateur, triggers banner-blindness. |
| M8 | Arrow + number combo on Welcome Page is non-optional. | Without it, banner-blindness kicks in within ~2s. |
| M9 | Welcome Page hard cap: 2 blocks. | Long Welcome Pages get scrolled-then-closed like washing-machine manuals. |
| M10 | "Just in case" permissions = automatic rejection. | Manifest must match the actual surface used. |
| M11 | Single-purpose statement + remote-code = NO. | Every Privacy tab field has a non-negotiable shape. |
| M12 | Submit only after `cws-careful` confirms. | Hard gate — never optional. |
| M13 | Privacy Policy company name = extension's English name, exactly. | Mismatch is caught by moderation. |
| M14 | No video, no GIF, on banner OR Welcome Page. | Forces study time, drops conversion, increases bounce. |

If a rule conflicts with the user's stated preference, state the rule and
the cost in one line, do not D-brief, do not negotiate. Example:

> M3: a raw screenshot as the small banner gets clipped by CWS as the
> listing UI on average ~30% of the time. Refusing. The small banner is a
> branded flat-icon-on-contrasting-background.

---

# Phase 0 — Gate check (block on missing prior stages)

Read `state.json` already echoed by the preamble. Parse `gates_passed`
into a set. Required entries: `idea`, `package`, `build`.

```bash
/usr/bin/python3 - <<'PY'
import json, sys, pathlib
p = pathlib.Path('./.cws/state.json')
if not p.exists():
    print("MISSING_STATE"); sys.exit(2)
d = json.loads(p.read_text())
gp = set(d.get('gates_passed', []))
need = ['idea', 'package', 'build']
missing = [g for g in need if g not in gp]
if missing:
    print("MISSING_GATES:", ",".join(missing))
    sys.exit(1)
print("GATES_OK")
PY
```

Branch on the result.

### 0.1 — Both prior gates missing (`MISSING_GATES: package,build`)

The user opened cws-launch first. They have not packaged copy and have
not built the extension. Two prerequisite skills are required; cws-launch
runs neither.

`AskUserQuestion D1`: which to run first?

```
D1 — Prior gates missing — which to start?
Project/branch/task: $SLUG @ $_BRANCH, opening cws-launch with no prior gates passed
ELI10: cws-launch is Stage 3. It needs the listing copy (cws-package) and a
  working extension archive (cws-build) before it can do anything. Pick which
  one to start — they can also run in parallel in two terminals.
Stakes if we pick wrong: nothing destructive — but skipping either gate means
  cws-launch will refuse to advance past Phase 0.
Recommendation: A (cws-package first) because copy informs banner caption.
Completeness: A=8/10, B=8/10, C=10/10
Pros / cons:
A) /cws-package first (recommended)
  ✅ Listing copy reveals the name/short-description keywords that anchor
     the banner caption + locale 10× rule
  ✅ Copy is cheaper to revise than the built extension archive
  ❌ Sequential — adds a stage's worth of wall-clock time
B) /cws-build first
  ✅ Surfaces real screenshots for the large banner faster
  ❌ Without locked copy, banner captions drift and need rework
C) Run both in parallel (two terminals)
  ✅ Wall-clock-optimal; both gates clear in one effort window
  ✅ Each skill is independent — no shared state collision
  ❌ Mental context-switch cost between the two
Net: pick C if you have the focus; A otherwise. Either way come back to /cws-launch when both gates exist.
```

After the user picks, print the routing footer and exit. Do **not** run
the chosen skill from inside cws-launch — exit, let the user invoke.

### 0.2 — One prior gate missing

Single-skill route. No D-brief; this is mechanical.

- Missing `package`: route to `/cws-package`.
- Missing `build`: route to `/cws-build`.
- Missing `idea` or `account-setup`: route to `/cws-idea`.

Print the routing footer with the single required next skill and exit.

### 0.3 — Both prior gates present (`GATES_OK`)

Advance to Phase 1.

### 0.4 — Already submitted (extension.submitted_for_review = true)

Special case. The skill ran before and submit happened. Re-entering
cws-launch in this state means one of:

- Moderation rejected and the user wants to fix and resubmit.
- The user wants to update an approved listing's banner / locale.
- Confused re-entry.

`AskUserQuestion D1`:

```
D1 — Extension already submitted — what's the goal?
Project/branch/task: $SLUG, current moderation_status: <value from state>
ELI10: cws-launch was already run and the extension was submitted. Pick what
  you want to do — fix a rejection, change something approved, or just re-read
  the artifact.
Stakes if we pick wrong: rerunning the whole flow on an approved listing
  republishes everything; rerunning on a rejected listing wastes a strike.
Recommendation: depends on moderation_status — A if rejected, B if approved,
  C otherwise.
Completeness: A=10/10, B=10/10, C=10/10
Pros / cons:
A) Resubmit after rejection
  ✅ Targeted — only changes the field moderation flagged
  ✅ Routes through /cws-careful + /cws-resync to fix without breaking other fields
  ❌ Moderation re-reads the entire submission with prejudice on the second pass
B) Update an approved listing (banner / locale / description)
  ✅ Propagates one field cleanly via /cws-resync
  ❌ Moderation re-checks every field — even untouched ones can fail v2
C) Read-only: open .cws/03-launch.md and exit
  ✅ Zero risk; just shows the artifact
  ❌ No action taken — caller must re-enter to do anything
Net: rejected → A; approved → B; unsure → C and read first.
```

For A/B route to `/cws-resync` (not cws-launch). For C, print
`.cws/03-launch.md` path and exit. Do not let a re-entry overwrite an
existing artifact silently.

---

# Phase 1 — Banner direction (D2: people / UI / abstract)

The small banner (440×280) shows in the CWS search results app list. The
large banner (1280×800) shows on the extension's listing page itself.
Both convert directly to installs; the small banner is the gate before
the user even sees the listing.

Bootcamp baseline: organic conversion ranges **15–30%**, the highest
ever measured is **60%**. Treat 60% as the ceiling, not a target.

## 1.1 — Direction brief

Three families of banner direction work. Pick exactly one — never mix.
This is a **kind**, not a coverage, decision.

```
D2 — Banner direction
Project/branch/task: $SLUG @ $_BRANCH, picking the small + large banner family for the listing
ELI10: Banners come in three flavors. Pick the one where your product's
  essence shows fastest. The wrong flavor doesn't kill ranking on its own,
  but it caps the install ceiling at ~15% instead of ~30%.
Stakes if we pick wrong: install conversion drops; over a 6-month launch
  window that compounds into 30–50% fewer total installs and softer
  behavioral factors on the geos that did install.
Recommendation: B (UI screenshot, simplified) because most CWS products
  win when the screenshot IS the value proposition.
Note: options differ in kind, not coverage — no completeness score
Pros / cons:
A) People / lifestyle / faces
  ✅ Strongest emotional pull for consumer-y products (productivity,
     wellness, parenting tools)
  ✅ Stands out among CWS competitors who mostly ship UI screenshots
  ❌ Every measured non-screenshot creative tested historically
     under-performed the raw screenshot on install conversion
B) UI screenshot, simplified (recommended)
  ✅ Highest-converting banner ever measured was a plain dark-theme
     product screenshot — 60% ceiling
  ✅ Honest — what you show is what users get on install
  ❌ Need to strip clutter aggressively — pins, close buttons, gear,
     ratings, browser chrome — or banner reads as visual noise
C) Abstract / brand-mark
  ✅ Works for products with no UI to speak of (single-keystroke
     utilities, content blockers)
  ✅ Skeleton-browser variant works for nano-products with tiny popups
  ❌ Loses on most product categories because abstract == "what does
     this do?" == bounce
Net: pick B unless the product is genuinely UI-less, then C with the
  skeleton-browser frame.
```

## 1.2 — Apply the banner mistake list (bootcamp rules)

Once direction is chosen, apply these checks. The first failed check is
the fix list; do not show the next D-brief until they all pass.

For **B (UI screenshot)**:

1. **Strip pin / close / gear / rating widgets** from the screenshot even
   if the real UI shows them — clutter.
2. **Show browser chrome only when the browser context IS the point**
   (a dark-theme product). Otherwise it wastes banner space.
3. **Caption = product essence**, not how to use it. Write
   `"Summarize any text instantly"`, not `"Copy, paste and summarize"`.
4. **Single key on banner #1.** Splitting weight across two keys on the
   first screenshot is acceptable only after ~10K users.
5. **Build screenshot #1 assuming you'll be alone in a carousel.**
   Without the Featured badge, only one banner shows.
6. **Artificially enlarge core controls; shrink browser UI.** Render at
   actual CWS display dimensions, not full size.
7. **Background: contrasting but roughly mono-tone.** A subtle one-color
   gradient is the max; pure flat color is safer. Two-color gradient
   (`green → purple → blue`) is the most common mistake — refuse.
8. **Black on white is the strongest background.** CWS UI is white; dark
   mode is only used by devs.
9. **For "known platform" banners (Instagram/Facebook UI clones), keep
   the original UI clutter** — the strip-everything rule reverses for
   universally-recognized interfaces.

For **A (people / lifestyle)**:

10. Acknowledge the conversion penalty up front. Bootcamp data: every
    non-screenshot creative tested under-performed raw screenshots.
11. If the user insists, frame it: face occupies < 40% of canvas, product
    UI element occupies > 40%, single caption.

For **C (abstract / brand-mark)**:

12. **Skeleton-browser frame** for sub-product extensions with tiny
    popups: faded music player + simplified browser chrome (no tab text,
    no other extensions, no non-English text anywhere).

## 1.3 — Iron rules at this stage

- **M3 — No screenshot-as-banner.** The small banner is a branded
  flat-icon-on-contrasting-background, never a raw screenshot. The large
  banner can show a simplified UI but never the literal product screenshot
  without framing.
- **M7 — Two-color gradient banned.** Subtle one-color gradient max.
- **M14 — No video, no GIF.** PNG only, ≤800 KB.

## 1.4 — Output

Add to the `## Banner` section in `./.cws/03-launch.md`:

- Small banner path: `assets/banner-440x280.png` (PNG, ≤800 KB).
- Large banner path: `assets/banner-1280x800.png` (PNG, ≤800 KB).
- Direction chosen: `<A | B | C>`.
- Background description: `<color>, <gradient | flat>, contrast vs CWS white UI`.
- Caption text on each banner.
- Alternatives tried (each with one-line reason rejected).

If the user has not produced the actual PNG files yet, note
`status: in-progress` on the section. Do **not** advance to Phase 2 with
only one banner produced — both are required to submit.

---

# Phase 2 — Icon (128×128 with transparent margin)

The icon shows in: CWS search tiles, the tab strip, the extensions
menu / puzzle dropdown, the Welcome Page (when teaching the pin).

## 2.1 — Source

Don't draw it. Grab a tidy minimalist flat 128×128 from
**flaticon.com**, resize for each slot. Skip flaticon attribution at
launch (required by TOS at ~1,000 users — irrelevant at zero).

## 2.2 — Files required

| Slot | File | Notes |
|------|------|-------|
| Tab strip / favicon | `assets/icons/16x16.png` | Transparent BG |
| Mid-DPI menu | `assets/icons/48x48.png` | Transparent BG |
| Hi-DPI menu | `assets/icons/64x64.png` | Transparent BG |
| Settings | `assets/icons/96x96.png` | Transparent BG |
| Extension archive 128 slot | `assets/icons/128x128.png` | 96×96 image inside transparent margin |
| Store listing 128 | `assets/icons/store-128.png` | 96×96 inside 128 with transparent margin |

The store icon (`store-128.png`) does **not** ship inside the extension
archive — it uploads to the CWS dashboard directly.

## 2.3 — Puzzle-shape-match check

Run this exact verification before accepting the icon:

1. Open the Chrome puzzle / extensions menu in any open browser.
2. Open the proposed icon at full size beside it.
3. The proposed icon must:
   - Be **distinguishable at 16×16** in the tab strip (no thin strokes,
     no outlined-only, no dotted lines).
   - **Contrast on both dark and light backgrounds.** Black-and-white
     minimalist icons do this best; color icons get lost among the 3–4
     other extensions a user has pinned.
   - **Match the banner's icon if the banner has one.** Two different
     icons (store vs tab) is allowed but kills recall — users install
     based on one icon, hunt for a different one, bounce.

## 2.4 — Bootcamp checks

- **Reject outlined / dotted-line / thin-stroke icons** — fail at 16×16.
- **"Looks too simple" is the signal to use it** — devs gravitate to 3D /
  multi-element icons that vanish at 16px; the "too plain" instinct is
  wrong.
- **Icon-vs-banner aesthetic harmony is not a real conversion factor** —
  don't waste time matching styles.
- **Color or black-and-white?** Default to black-and-white minimal —
  stands out best against a typical 3–4-extension pinned row.

## 2.5 — Decision point

Only D-brief if the user is choosing between multiple finalist icons.
Mechanical otherwise.

```
D3 — Icon finalist
Project/branch/task: $SLUG, picking final 128×128 icon from <N> candidates
ELI10: Pick the icon that survives the 16×16 squint test and contrasts
  on both dark and light backgrounds. The "too simple" feeling is correct.
Stakes if we pick wrong: a thin-stroke icon disappears in the tab strip,
  users lose track of the pinned extension, behavioral-factor drop.
Recommendation: A (the simplest one) because the "too plain" instinct
  is the right one at 16×16.
Completeness: each option 10/10 — kind difference is style
Pros / cons:
A) Minimal black-on-white silhouette (recommended)
  ✅ Survives 16×16 squint test — distinguishable in tab strip
  ✅ Contrasts on both dark and light browser themes
  ❌ Visually "boring" at 128×128 — but that's the point at 16×16
B) Colored multi-element icon
  ✅ Eye-catching at 128×128 in the listing tile
  ❌ Vanishes at 16×16; users lose the pinned extension and bounce
Net: A. If it looks too simple at 128, it's correct at 16.
```

## 2.6 — Output

`## Icon` section in `03-launch.md`:

- All six file paths.
- Source attribution (`flaticon.com/<icon-id>` or `original artwork`).
- Black-and-white vs color choice with one-line reason.
- 16×16 squint-test verdict.

---

# Phase 3 — Welcome Page (D4: simple text + ungated CTA)

CWS hides every freshly installed extension under the puzzle icon. Most
users can't find it after install → bounce back to Google → ranking drops.

The Welcome Page is the fix. It opens once, automatically, immediately
after install, in a new tab. Its only job: get the user to find and pin
the extension (or click the in-page artifact, if the product has one).

## 3.1 — Critical bootcamp insight

**Simple text + ungated CTA. No auth wall on first install. -60–80%
activation if auth-gated.**

This is M5 elevated to a phase-level rule. If the user proposes
"sign in to continue" on the Welcome Page, refuse. Auth comes in Stage 5
(monetization), wired to Google sign-in for payment attribution. Not now.

## 3.2 — Page goal (90% of cases)

"Find and pin the extension." Single arrow + single number pointing at
the puzzle icon. The user clicks the puzzle, sees the extension, pins it.

Exceptions:

- **New-tab extensions** — ask the user to accept the new-tab replacement.
- **Page-injecting extensions with an artifact** (corner widget) — point
  the Welcome Page at the artifact instead of the puzzle icon. Far simpler:
  one-screen, one-click path. Disable the artifact's "hide-when-idle"
  behavior specifically on the Welcome Page so it stays visible.

## 3.3 — Welcome Page mistake list

1. **Arrow + number combo is non-optional.** Bright (ideally red)
   numbered arrows pointing at the pin icon. Without it, banner-blindness
   kicks in within ~2 seconds; users hit the tab close button.
2. **Misleading arrow is worse than no arrow.** A decorative arrow
   pulled focus away from the pin icon in a recorded user test; user
   stared at unmarked area, never found the puzzle until hinted.
3. **Puzzle icon shape on the Welcome Page must match Chrome's exactly.**
   Different stylization breaks recognition.
4. **Period vs colon matters.** `Click the puzzle:` ties text to the
   screenshot. `Click the puzzle.` reads as closed sentence; users don't
   connect instruction to image.
5. **Screenshot needs the full browser frame**, not a cropped slice.
   Cropping breaks spatial orientation.
6. **Frame each screenshot with a clear border on a contrasting
   background.** A screenshot that blends into the page background gets
   clicked as if it IS the UI — up to 30% of traffic lost.
7. **Shrink the screenshot, enlarge the element the user must find.**
   The pin / artifact button is what the user needs to see big.
8. **Numbering: 1+2 on the first screenshot, 3 on the second.** One
   continuous numbered sequence; don't restart per screenshot.
9. **Hard cap: 2 blocks (M9).** Long Welcome Pages get scrolled-then-
   closed like washing-machine manuals.
10. **No "how to use the product" sections on the Welcome Page.** Those
    belong inside the product. The Welcome Page has exactly one job: find
    + pin.
11. **No video, no GIF (M14).** Forces study time, drops conversion.
12. **One uninterrupted flow.** Don't add multi-step instructions
    ("now paste the signature into Gmail") — extra steps belong inside
    the product.
13. **English store name on the Welcome Page is fine for non-English
    installs.** The icon stays identical; the user's brain maps the
    local-language tab name to the English Welcome-Page name. Don't
    over-engineer per-locale Welcome Pages on V1.
14. **Tilda's branded footer on a `tilda.ws` subdomain is fine for
    English-market launches.** Foreign users don't recognize Tilda.
    Don't waste V1 time hiding it.

## 3.4 — Hosting choice

```
D4 — Welcome Page host
Project/branch/task: $SLUG, picking where to host the Welcome Page
ELI10: The page opens once per install in a new tab. It can live on Tilda
  (no-code editor, free), GitHub Pages (free), Vercel (free), or a subdomain
  of your product domain. Own hosting is preferred but Tilda is launchable
  in 20 minutes.
Stakes if we pick wrong: Tilda's free tier shows a small Tilda footer in
  English-market launches that's fine; in a Russian-market launch some users
  recognize it and bounce a few percent.
Recommendation: B (subdomain of product domain) because once you own a
  domain anyway, subdomain hosting is one A-record and gives you Uninstall
  + share pages for free.
Completeness: A=8/10, B=10/10, C=9/10, D=7/10
Pros / cons:
A) Tilda (free subdomain like aipromptgenerator.tilda.ws)
  ✅ 20-minute publish from a no-code editor
  ✅ Bootcamp-tested — multiple top-3 extensions launched on this
  ❌ Branded footer; can't host the Uninstall page or share pages here
B) Subdomain of product domain (e.g. ext.yourdomain.com) (recommended)
  ✅ One A-record points at Tilda's IP, host all service pages there
  ✅ Connect SSL, set www→non-www + http→https redirects, re-publish all
  ✅ Same domain = consistent for analytics + reviews widget
  ❌ Need to own a domain — adds ~$10/yr
C) Own static hosting (GitHub Pages / Vercel)
  ✅ Free, no Tilda footer, full control
  ❌ Need an HTML/CSS pass — non-trivial if no design skills
D) No Welcome Page
  ✅ Saves an evening
  ❌ Welcome-Page→activation conversion drops from ~60% to 10–15%
  ❌ Hard refuse — bootcamp baseline says this is launch-killing
Net: own a domain anyway → B; no domain → A; design skills → C; never D.
```

## 3.5 — Service-worker code (auto-open after install)

The extension's build (`cws-build` gate) already includes the install
listener. Verify it before submit:

```js
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === chrome.runtime.OnInstalledReason.INSTALL) {
    chrome.tabs.create({ url: "[YOUR WELCOME PAGE URL]" });
  }
});
```

If the URL is templated, replace with the real published URL now. If
this code is missing, route the user back to `/cws-build` to add it —
don't try to inject it from cws-launch.

## 3.6 — Analytics on the Welcome Page

Add now:

- **Site-wrapped extensions**: Yandex Metrica + **Webvisor click-maps**,
  GA4, Amplitude (preferred). Webvisor on the Welcome Page is how the
  bootcamp "users click the screenshot as if it's UI" insight surfaced —
  install it specifically to validate before optimizing.
- **Local-page / popup extensions**: event-based analytics. GA4
  Measurement Protocol, Amplitude (preferred), Mixpanel (alternative).
- **Track conversions separately** for the Welcome-Page → activation
  funnel. Average is ~60% (with a good Welcome Page), drops to 10–15%
  without one. Early Welcome Pages typically hit 20–25%; reaching 60%
  needs iteration on screenshot framing, arrows, and puzzle-icon
  matching.
- **Unique-user counting does NOT require auth.** IP attribution is
  accurate enough at pre-monetization volumes.

## 3.7 — Copy correctness

Correct **all** Welcome Page copy via ChatGPT regardless of your
English level:

```
correct this text in the app UI: [text]
```

The bootcamp's repeat instruction: don't trust your own English; trust
the editor pass.

## 3.8 — Output

`## Welcome Page` section in `03-launch.md`:

- Published URL.
- Host choice (Tilda / own subdomain / Vercel).
- Page goal (find-and-pin / artifact / new-tab).
- Block count (must be ≤2 per M9).
- Screenshot count + arrow+number scheme.
- Analytics installed (yes/no, which tool, Webvisor present).
- Auto-open code verified (yes/no).
- Copy ChatGPT-corrected (yes/no).

---

# Phase 4 — Locale strategy (D5: manual vs auto-translate)

50+ locales is M1 — mechanical. The decision here is **which locales
get manual treatment** vs which get pure auto-translation through
Localizer.

## 4.1 — Default locale split (this IS the recommendation)

The bootcamp default split:

**Manual name + short description (full description auto-translated):**

- **Latin-script rich (all)**: German, French, Spanish, Italian, Dutch,
  Swedish, Danish, Norwegian, Finnish. Rich countries with much lower
  competition than English on most queries.
- **Huge speaker base (first 3 at minimum)**: Arabic, Indonesian,
  Russian. Russian must be done manually even though Russia doesn't pay
  — Russian-speaking traffic (10–15% of launch traffic) is a Google
  *trigger* to expand testing into Tier-1 paying geos.

**Pure Localizer auto-translation** (no manual pass): every other locale
in Localizer's set, including Portuguese, Japanese, Filipino, Vietnamese,
Turkish, Thai, Korean — these are valuable but the auto pass is good
enough at launch. Promote to manual treatment post-launch only if a
specific locale shows ranking traction in `cws-retro`.

## 4.2 — D-brief (only if user wants a non-default split)

```
D5 — Locale strategy
Project/branch/task: $SLUG, choosing which locales get manual translation
  vs Localizer auto-translation
ELI10: 50+ locales is non-negotiable (mechanical rule M1). The choice is
  which locales get a manual name + short description (more work, better
  ranking ceiling) vs which get pure Localizer auto-translation (one click,
  good-enough for launch).
Stakes if we pick wrong: under-investing in Latin-script rich locales caps
  the ranking ceiling on the most valuable non-English markets; over-
  investing burns days on locales where Localizer would have been fine.
Recommendation: A (bootcamp default) because it's the empirically-tested
  split from ~10 launches.
Completeness: A=10/10, B=8/10, C=9/10
Pros / cons:
A) Bootcamp default — Latin-script rich (9) + AR/ID/RU manual; rest Localizer
   (recommended)
  ✅ Maximizes Tier-1 paying locales (DE/FR/ES + scandinavia)
  ✅ Russian manual triggers Google's expansion testing into paying geos
  ✅ Localizer covers the rest in ~30–40 min total
  ❌ ~3–6 hours of manual keyword work per Latin-script-rich locale
B) Everything manual (all 50+)
  ✅ Highest ranking ceiling per locale
  ❌ ~150+ hours of work; locale 30 produces diminishing returns
  ❌ Delays launch by weeks; behavioral factors aren't tested in-flight
C) Everything Localizer (no manual)
  ✅ Fast — single 30–40 min run
  ✅ Bootcamp says "even clumsy auto beats no translation"
  ❌ Misses 10× rule wins on the rich Latin-script locales
  ❌ Caps the German/French ranking ceiling at maybe 50% of A
Net: A unless you're shipping a dev-tool where everyone searches in
  English anyway — then C is acceptable.
```

## 4.3 — Tech-vertical exception

For tech-vertical extensions (JSON formatter, regex tools, dev
utilities) — **keep the English name in every locale**. Devs everywhere
search in English. Verify per-product (check the 10× rule for `Russian
"json formatter"` vs `Russian "форматтер json"`), but don't auto-localize
names of dev tools.

## 4.4 — Localizer setup

1. Request a Secret Key via **t.me/localizer_manager_bot**. The same key
   issues quotas large enough for multiple extensions — keep it.
2. Visit **localize.camp**, paste the key.
3. Paste name, short description, full description from
   `./.cws/02a-listing.md` (cws-package output).
4. **Verify text structure isn't broken on paste** — line breaks,
   bullet points, headers.
5. Select all languages. Languages flagged with a warning emoji are ones
   where OpenAI struggles — Localizer defaults those to Google Translate.
6. Run. Full pass takes 30–40 min.
7. Re-run any failed translations (highlighted at end of run).
8. Export the `_locales` folder.
9. Drop it into the extension root next to `manifest.json`.

## 4.5 — Manifest changes

In `manifest.json`:

```json
"name": "__MSG_appName__",
"description": "__MSG_shortDesc__",
"default_locale": "en"
```

The full description (`storeDesc`) is NOT in the manifest. It uploads
to CWS via the locale uploader script in Phase 6.

`default_locale: "en"` is the fallback for any locale missing a string.

## 4.6 — Interface strings warning

Localizer auto-translates only `appName`, `shortDesc`, `storeDesc`. If
the extension UI has **other** strings (button labels, modal text), they
live in `_locales/en/messages.json` and must be filled manually in the
English locale. Other locales fall back to `en`. Verify before submit:

```bash
ls _locales/en/messages.json && /usr/bin/python3 -c "
import json
m = json.load(open('_locales/en/messages.json'))
for k, v in m.items():
    if not v.get('message'):
        print('EMPTY:', k)
"
```

Any empty `message` field = an empty button at runtime = launch-killing
bug.

## 4.7 — Transliteration nuance (manual locales only)

For each Latin-script-rich locale + AR/ID/RU:

- **Don't literal-translate a "universal" English name.** `ai chat gpt`
  in Russian — `чат гпт` (transliterated) gets ~1M searches in Wordstat.
  That's a different, valuable keyword. Take it.
- **Non-Latin-script (Cyrillic, Chinese, Arabic)**: national spelling
  usually dominates over English. Gap widens as the tech goes mainstream.
- **Latin-script (German, French, etc.)**: English variant often
  dominates. Verify with the 10× rule (Phase 5).
- **Anglicism naming pyramid** (best → worst), for a name that is an
  anglicism in the target language:
  1. The keyword as people **search** it.
  2. As people **say** it grammatically.
  3. Keep the anglicism if it has any traffic.
  4. Auto-translate.
  5. (Worst) No translation at all.

  Even clumsy auto-translation beats none — Google glues it to the real
  local search query.

## 4.8 — Short-description overflow rule

**Auto-translated short descriptions overflowing 132 chars is
acceptable** on non-English locales. Constraining GPT to fit 132 chars
makes it cut content too aggressively; let it overflow, CWS truncates
harmlessly. Fix only when doing the manual pass for an important locale.

## 4.9 — Iron rule M6 (never duplicate English)

`en`, `en_US`, `en_GB`, `en_AU` — pick ONE. Localizer outputs one
English locale by design. If the user manually added `en_GB` for "UK
market coverage", refuse — four English duplicates pessimize SEO on the
most competitive locale.

Spanish / Portuguese / Chinese near-duplicates (`es`, `es_419`, `pt`,
`pt_BR`, `zh_CN`, `zh_TW`) are fine — those locales have weak enough
competition that 2× pages are net positive.

## 4.10 — Output (interim)

Don't write the `## Locales` section in `03-launch.md` yet. The 10× rule
runs in Phase 5 and emits the per-locale name decisions. The section
gets written at end of Phase 5.

---

# Phase 5 — Per-locale name with the 10× rule (M4)

The 10× rule is mechanical. Apply it to every manual-treatment locale
(Phase 4 default: Latin-script-rich + AR/ID/RU). Output per locale:
`name`, `short_description`, and a one-line decision audit.

## 5.1 — The 10× rule (M4 verbatim)

For a locale L and the chosen English head keyword (from
`./.cws/01-idea.md`):

1. Identify the English head's search volume in country-L (e.g. German
   Semrush volume of the English head in Germany).
2. Identify the best **local-language** equivalent's search volume in
   country-L (research process below).
3. Apply:
   - `English ≥ 10× local` → use **English** as the locale's name.
   - `local ≥ 10× English` → use **local-language** as the locale's name.
   - Anything in between → **combine** both with `-` or `|`.
     `Bloqueador de anuncios - Free Adblocker`. Allowed on non-English
     locales because competition is low enough that 2-key dilution is
     acceptable.
4. If no candidate clears any of the above (no traffic on either
   variant), **skip the manual pass for this locale** — let Localizer
   auto-translate and move on.

## 5.2 — Per-locale keyword research procedure

For each manual locale L:

### 5.2.1 — Ask ChatGPT how people search

Prompt: `"How do German users search for [product description] on
Chrome Web Store? Give me 5–10 keyword variants in German, sorted by
likely search volume."`

### 5.2.2 — Verify with Semrush (target country selected)

- Open Semrush MCP `keyword_research`.
- Set the country code to the locale's primary country (DE, FR, ES, IT,
  NL, SE, DK, NO, FI, SA / EG for AR, ID, RU for Russian).
- Look up each candidate in 5.2.1.
- Also look up the **English head** with country=L selected (this gives
  the English-search volume *in that country*).

### 5.2.3 — Cross-check with competitor national-language sites

- Find a competitor's national-language website that ranks in the
  country-L SERP.
- Use Semrush `organic_research` on that competitor URL with country=L.
- Collect keywords the competitor ranks on — these are the real
  search queries in language L.

### 5.2.4 — Browse CWS in language L

- Open `chrome.google.com/webstore?hl=es` (or `hl=de`, `hl=fr`, etc.).
- Verify your top candidate exists in real CWS search results.
- See what optimized competitors there have used.

### 5.2.5 — Russian-specific tool

For Russian — **Yandex Wordstat**, not Semrush. Wordstat is owned by
Yandex and gives accurate Russian volumes. Semrush guesses Russian
traffic.

### 5.2.6 — Spanish-specific procedure

Target **Spain** in Semrush (not Mexico / Argentina — they have weaker
data). Follow competitor sites from the Spain SERP, feed local-language
keywords back into Semrush. This is the only way to surface keyword
translations for languages without dedicated national tools.

## 5.3 — Combined-name rules (when 10× rule says combine)

- Allowed on non-English locales because competition is low.
- Use `-` (`Bloqueador de anuncios - Free Adblocker`) or `|`
  (`Bloqueador de anuncios | Free Adblocker`).
- **Don't ship two near-identical keywords adjacent** (e.g.
  `Convert PDF Converter`). Triggers human moderation flags AND ranking
  pessimization. Same root word can appear elsewhere in the description
  if separated by ≥5 words.
- **Singular vs plural and `.` vs no-`.` are treated as distinct queries
  by Google** despite Google's public claim. In the long description,
  cover variations: `pdf.` and `pdf` in different sentences.

## 5.4 — Short-description procedure per manual locale

After deciding the name:

- Prompt ChatGPT **in language L**: `"Write a Chrome Web Store short
  description in German for an extension named [name] that does
  [function]. Maximum 132 characters. Include the keywords [k1], [k2]."`
- Verify byte length ≤ 132 in your editor. ChatGPT often overruns; it
  is OK to truncate the last clause manually.

## 5.5 — Full-description procedure per manual locale

Translate the English full description (from `02a-listing.md`) via
ChatGPT, prompted **in language L**:

`"Translate this Chrome Web Store full description into German. Keep
SEO keywords. Don't summarize. Aim for ~3,000 chars."`

Then **paste back into Localizer's run** for the locale — or update the
`_locales/<L>/messages.json` `storeDesc.message` directly.

## 5.6 — Per-locale output

For each manual locale, append a row to `03-launch.md`'s `## Locales`
section:

| Locale | Name decision | EN vol (in country-L) | Local vol | 10× verdict | Name | Short desc chars |
|--------|---------------|------------------------|-----------|-------------|------|-------------------|
| `de` | local | 1.2K | 18K | local ≥ 10× EN | `Werbeblocker` | 128 |
| `fr` | combined | 4.5K | 9K | between | `Bloqueur de pubs \| Adblocker` | 132 |
| `nl` | English | 6.7K | 400 | EN ≥ 10× local | `Free Adblocker` | 124 |

The audit is forensic: a year later you can re-read the artifact and
know why each locale's name is what it is.

## 5.7 — Iron rules at this stage

- **M4** — 10× rule applied mechanically per locale.
- **M6** — never duplicate the English locale.

---

# Phase 6 — Upload locales to CWS (use the existing script)

`references/cws-locale-uploader.js` exists. It already drives the CWS
language dropdown + 16,000-char full-description textarea. Do **not**
rewrite it. Do not try to script CWS dashboard uploads from Bash —
the dashboard is JS-heavy and the only safe path is the DevTools console
script that's already shipped.

## 6.1 — Pre-conditions

- Extension archive uploaded as draft (Phase 8 first half — this is one
  of those circular dependencies; draft-upload happens before locale
  upload).
- `_locales/<code>/messages.json` for every locale has a populated
  `storeDesc.message`.
- Logged in to CWS developer dashboard with the dedicated Google account
  (from Stage 0).

## 6.2 — Procedure

1. **Navigate**: on the extension's **Store Listing** page (developer
   dashboard).
2. **Refresh**: ensure dropdown state is clean.
3. **Open DevTools** → **Console** tab.
4. **Unblock paste** if Chrome warns: type `allow pasting` and press
   Enter.
5. **Paste the script**: contents of
   `references/cws-locale-uploader.js`.
6. **Click the green "Choose Files" button** that the script renders.
7. **Select the `_locales` folder** from your extension's source.
8. The script:
   - Reads each `_locales/<code>/messages.json`.
   - Extracts `storeDesc.message`.
   - Drives the CWS language dropdown to each language.
   - Pastes the corresponding `storeDesc.message` into the 16,000-char
     textarea.
9. **Save Draft** at the end (don't forget; the script does not save).
10. **Refresh** the page.
11. **Verify**: switch language dropdown to a few random locales (e.g.
    `de`, `ru`, `ja`) and confirm the full description loaded.

## 6.3 — What can go wrong

- The CWS DOM changed and the script's selectors are stale → the user
  pastes a new version. Out-of-scope for cws-launch; route to
  `/cws-resync` to patch `references/cws-locale-uploader.js`.
- A locale's `storeDesc.message` is empty → script silently skips.
  Re-check Phase 4 / 5 exports.
- Network drops mid-upload → CWS rejects the partial save. Refresh,
  verify, re-run.

## 6.4 — Output

`## Locales` section additions:

- Script version used (file hash of `references/cws-locale-uploader.js`).
- Locale count uploaded.
- Sample-verified locales (the 3–5 you spot-checked after refresh).

---

# Phase 7 — host_permissions audit (D6 only if widening)

The `cws-build` gate already produced a `manifest.json` with the
minimum-viable host_permissions. **Widening here is a serious decision
because it triggers re-review and is one of the categories Google
rejects automatically for "just in case" inclusions.**

## 7.1 — Read current manifest

```bash
/usr/bin/python3 - <<'PY'
import json, pathlib
m = json.loads(pathlib.Path('manifest.json').read_text())
print("host_permissions:", json.dumps(m.get('host_permissions', []), indent=2))
print("permissions:", json.dumps(m.get('permissions', []), indent=2))
print("optional_permissions:", json.dumps(m.get('optional_permissions', []), indent=2))
PY
```

## 7.2 — Decision: widening or staying?

If the user explicitly wants to widen (e.g. `https://*/*` instead of
`https://*.specific-site.com/*`):

```
D6 — host_permissions widening
Project/branch/task: $SLUG, considering widening host_permissions from
  <current> to <proposed>
ELI10: host_permissions tells Chrome which sites the extension can read
  / modify. Widening from "this one site" to "all sites" gets the
  extension marked higher-risk by CWS reviewers and triggers automatic
  rejection if the justification doesn't match the actual code.
Stakes if we pick wrong: rejection on submit, lost ~3 business days of
  moderation SLA, and a second-submission "stricter scrutiny" penalty
  from moderation.
Recommendation: B (refuse widening at cws-launch; route to /cws-careful
  + /cws-resync) because widening at submit-time is the wrong stage.
Completeness: A=8/10, B=10/10
Pros / cons:
A) Widen now inside cws-launch
  ✅ Single skill invocation handles everything
  ❌ Iron rule M10 — "just in case" permissions = automatic rejection
  ❌ cws-launch is asset+publish; manifest changes belong in cws-build
B) Refuse widening here; route to /cws-careful then /cws-resync
   (recommended)
  ✅ /cws-careful is the hard gate for irreversible decisions; that's the
     right place to weigh the rejection risk
  ✅ /cws-resync re-runs cws-build's manifest validation, keeps the
     build gate honest
  ❌ Adds 1–2 skill hops before submit
Net: refuse widening here; the right path is careful + resync, then
back to cws-launch with the gate cleared.
```

## 7.3 — Iron rule

**M10 — "Just in case" permissions = automatic rejection.** The
manifest must match the actual surface used. If `tabs` is in permissions
but no code touches `chrome.tabs.*`, strip it. If `host_permissions`
covers `https://*/*` but the code only ever fetches from one domain,
narrow it.

## 7.4 — Justification per permission

Write a short justification per permission now. These get pasted into
CWS's permissions tab in Phase 8.

Bootcamp-tested justification shape:

| Permission | One-line justification |
|------------|------------------------|
| `storage` | "Persist user-selected language and theme preferences across sessions" (NOT "Storage — to store data" — that gets verbose-rejected) |
| `tabs` | "Control sound capturing across browser tabs" |
| `activeTab` | "Control sound capturing in the currently active tab" |
| `downloads` | "Download the generated audio file to the user's machine" |
| `<host_permissions>` | "Show the extension's action button on supported websites" — and name the actual surface |
| `unlimited_storage` | "Persist embedded image / HTML-signature templates beyond Chrome's default 5MB cap" |

Iron rule: **storage permission justifications get verbose-rejected if
one-word.** Be specific per permission.

## 7.5 — Output

`## Permissions` section in `03-launch.md`:

- Final `host_permissions` list (verbatim from `manifest.json`).
- Final `permissions` list.
- Justification for each (the lines that go into CWS Permissions tab).
- Widening decision: `none` / `widened with /cws-careful approval on
  YYYY-MM-DD`.

---

# Phase 8 — Submit for moderation (cws-careful is a HARD gate)

Every prior phase produces an artifact. This phase produces an
**irreversible action**: pressing "Submit for review" on the CWS
developer dashboard.

## 8.1 — cws-careful hard gate (M12)

`cws-careful` is **non-optional** before submit. Per
`../../shared/skill-routing.md`:

> Any irreversible step (submit, monetize on, host_permissions widen,
> account delete) → `cws-careful` **before** the action. Hard gate.
> Never skip.

Read `state.json.gates_passed`. If `careful-submit` is **not** present:

1. Print the routing footer:
   ```
   Next: /cws-careful
   Why: Pre-submit hard gate. cws-launch refuses to advance to the actual
   "Submit for review" click until cws-careful logs gates_passed +=
   ["careful-submit"]. Re-enter cws-launch after.
   ```
2. **Exit cws-launch.** Do not advance to 8.2.

If `careful-submit` IS present, advance.

## 8.2 — Pre-submit checklist (all must be true)

This is mechanical. Each item is a single bash check or file existence:

```bash
/usr/bin/python3 - <<'PY'
import json, pathlib, sys
checks = []
m_path = pathlib.Path('manifest.json')
m = json.loads(m_path.read_text()) if m_path.exists() else {}
checks.append(("manifest.json exists", m_path.exists()))
checks.append(("name uses i18n", m.get('name') == '__MSG_appName__'))
checks.append(("description uses i18n", m.get('description') == '__MSG_shortDesc__'))
checks.append(("default_locale set", bool(m.get('default_locale'))))

locales_dir = pathlib.Path('_locales')
checks.append(("_locales/ exists", locales_dir.exists()))
en_msgs = locales_dir / 'en' / 'messages.json'
checks.append(("_locales/en/messages.json exists", en_msgs.exists()))

if en_msgs.exists():
    em = json.loads(en_msgs.read_text())
    empty = [k for k, v in em.items() if not v.get('message')]
    checks.append((f"_locales/en/messages.json no empty (empty={empty})", not empty))

assets = pathlib.Path('assets')
checks.append(("assets/banner-440x280.png", (assets / 'banner-440x280.png').exists()))
checks.append(("assets/banner-1280x800.png", (assets / 'banner-1280x800.png').exists()))
for px in ('16','48','64','96','128'):
    checks.append((f"assets/icons/{px}x{px}.png", (assets / 'icons' / f'{px}x{px}.png').exists()))
checks.append(("assets/icons/store-128.png", (assets / 'icons' / 'store-128.png').exists()))

state = json.loads(pathlib.Path('./.cws/state.json').read_text())
gp = state.get('gates_passed', [])
for g in ('idea', 'package', 'build', 'careful-submit'):
    checks.append((f"gate {g} passed", g in gp))

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(("OK" if ok else "FAIL") + " — " + name)
if failed:
    sys.exit(1)
PY
```

Any FAIL aborts submit. Route to the appropriate skill to fix:

- Missing banner / icon → continue in cws-launch, redo Phase 1 / 2.
- Missing locale file → continue, redo Phase 4 / 6.
- Missing `careful-submit` gate → route to `/cws-careful`.
- Missing `build` gate → route to `/cws-build`.

## 8.3 — Pre-publish gauntlet (bootcamp checklist)

These are not D-briefs. They are mechanical gates that must all pass.

### 8.3.1 — Differ from the competitor (M1 of pre-publish list)

A full copy-paste gets rejected. Name-similarity rules:

- Identical name OR difference of word-order / 1–2 letters → use ONLY
  if the existing competitor is NOT optimized (lacks 30+ locales AND/OR
  lacks 3,000+ char description). If they ARE optimized, your clone
  gets dragged down by clone-penalty. Pick a different name.
- Differ by 1 word → much better.
- Differ by 2 words or fully → ideal.

Verify by visiting the competitor's CWS listing. Note the locale count
and full-description char count in the artifact.

### 8.3.2 — Spam check the texts

The check ran during `cws-package` (Stage 2). Re-verify here that
nothing leaked back in during Phase 5 manual translation:

- No keyword repeated 3× in title or short description.
- No comma-separated keyword lists in description.
- No competitor names mentioned.

### 8.3.3 — Translation done (Phase 4 / 5 / 6)

50+ locales uploaded. Spot-checked. Verified.

### 8.3.4 — Antivirus

Upload the extension archive (zip) to **virustotal.com**. Wait for
result. A false-positive once got an extension banned. If any AV flag
appears (rare), investigate the trigger, rework, rebuild, re-check.

Record: VT scan ID, date, result.

### 8.3.5 — `_locales` cleanup if English-only

If for some reason publishing English-only (not recommended — but if
the user insists):

1. **Save the full `_locales` folder** elsewhere first.
2. Remove every locale subfolder except `_locales/en/`.
3. Otherwise CWS fills empty descriptions for every language and
   heavily pessimizes ranking.

### 8.3.6 — 2FA

Google may require 2FA before upload. Set up in the dedicated Google
account (from Stage 0) if not already done.

## 8.4 — Upload sequence

**Step 1: Set Google account interface language to English (US).**
Account settings → Personal info → Language. CWS reads this for the
developer dashboard. Mismatched language causes silent dropdown bugs in
Phase 6.

**Step 2: Go to the developer dashboard.**

`chrome.google.com/webstore/developer/dashboard`

**Step 3: Upload the extension archive.**

The zip file from `cws-build`'s output. Path:
`dist/$SLUG-v<version>.zip`.

Wait for upload to complete. CWS validates the manifest immediately;
any validation error means routing back to `/cws-build` with the error
message. Do not "fix the manifest from here" — that's `cws-build`'s
job.

**Step 4: Grab the extension ID.**

After draft upload, the dashboard shows the extension ID top-left.
Capture it now (it is the longest single-shot value in the artifact):

```
Extension ID: abcdefghijklmnopqrstuvwxyz123456
```

Write it into:

- `state.json` → `extension.id`.
- `03-launch.md` → `## Submission` section.
- Any service-worker URLs templated with `[EXT_ID]` → replace and
  re-build. **Do not publish; re-upload the draft.**

The bootcamp rule (M-grade): **don't pass moderation early just to get
the ID and leave it approved-but-unpublished.** Plausibly CWS adds the
approved URL to its sitemap and indexes a poor version. Upload as
draft, grab ID, re-upload draft. Don't submit until the full launch
package is ready.

**Step 5: Fill the store card per language.**

- Name and short description pull from the archive's `_locales/<L>/`.
- **Full description must be pasted manually** — CWS can't pull it from
  the archive even though it's in `messages.json`.
- This is what Phase 6's locale uploader script automates.

**Step 6: Upload graphics.**

- Small banner: `assets/banner-440x280.png`.
- Large banner: `assets/banner-1280x800.png`.
- Store icon: `assets/icons/store-128.png` (the 96×96-in-128 version).
- Optional additional screenshots: as many as you have, the first one
  is what shows in the carousel without Featured badge.

**Step 7: Save Draft.**

Save before navigating to Privacy. CWS loses unsaved edits on tab
navigation.

**Step 8: Privacy tab.**

- **Single purpose** — one short sentence describing the one core
  function. NOT a list. NOT a "and also" sentence. One thing.
- **No, I am not using remote code.** M11. If the extension genuinely
  uses remote code, route back to `/cws-build` and fix that. Hard
  refuse otherwise.
- **Justify every permission** — paste the lines from Phase 7.4.
- **Data collection** — mark only what you actually collect. If you
  collect nothing, mark nothing. Don't preemptively check boxes.
- **Three confirmation boxes** — tick all three.
- **Privacy Policy URL** — public URL of the Privacy Policy doc.

## 8.5 — Privacy Policy

Required for publish. Use the studio template (Google Doc) with these
fields replaced:

| Placeholder | Replace with |
|-------------|--------------|
| `[COMPANY NAME]` | Extension's English name, exactly (M13) |
| `[EMAIL ADDRESS]` | Support email tied to the dedicated Google account |
| `[DATE]` | Today, `YYYY-MM-DD` |

Publish the doc (Share → "Anyone with the link"), copy the public URL,
paste into the Privacy tab. Iron rule M13: the company name must match
the extension's English name **exactly**. Mismatches are caught by
moderation and rejected.

## 8.6 — Submit for review

After all of 8.4 + 8.5:

1. Save the listing one final time.
2. Click **Submit for review**.
3. CWS confirms; status changes to `pending`.
4. Capture the timestamp.

## 8.7 — Post-submit state update

```bash
/usr/bin/python3 - <<'PY'
import json, datetime, pathlib
p = pathlib.Path('./.cws/state.json')
d = json.loads(p.read_text())
d.setdefault('extension', {}).update({
    'id': '<EXTENSION_ID>',
    'draft_uploaded': True,
    'submitted_for_review': True,
    'moderation_status': 'pending',
    'submitted_at': datetime.datetime.utcnow().isoformat() + 'Z',
})
gp = d.setdefault('gates_passed', [])
if 'launch' not in gp:
    gp.append('launch')
d.setdefault('history', []).append({
    'ts': datetime.datetime.utcnow().isoformat() + 'Z',
    'stage': 'cws-launch',
    'event': 'gate_passed:launch',
})
d['last_updated'] = datetime.datetime.utcnow().isoformat() + 'Z'
p.write_text(json.dumps(d, indent=2))
print("STATE_UPDATED")
PY
```

Replace `<EXTENSION_ID>` with the real value captured in 8.4 step 4.

## 8.8 — Iron rules at this stage

- **M10** — "Just in case" permissions = automatic rejection.
- **M11** — Remote code = NO. Single-purpose statement is one sentence,
  one function.
- **M12** — cws-careful is a hard gate before submit.
- **M13** — Privacy Policy company name = extension's English name.
- Bootcamp: **moderation re-checks the entire submission on every
  update.** A short description that passed v1 can fail v2 even
  unchanged. Plan for it.
- Bootcamp: **repeated re-submissions attract stricter scrutiny.** If
  rejected once, the second pass examines text "with prejudice" — fix
  the underlying spam pattern aggressively, not incrementally.
- Bootcamp: **obfuscation banned; minification mandatory.** Variable-
  name shortening + whitespace removal = minification (allowed).
  Replacing characters with non-ASCII glyphs to hide code = obfuscation
  (banned).

---

# Phase 9 — Write the artifact

`./.cws/03-launch.md` with full frontmatter and all sections.

## 9.1 — Frontmatter

```yaml
---
stage: cws-launch
status: complete
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
slug: <$SLUG>
extension_id: <captured-in-8.4>
moderation_status: pending
---
```

## 9.2 — Sections (mandatory)

```markdown
## Banner

- Small: `assets/banner-440x280.png` (PNG, <size> KB)
- Large: `assets/banner-1280x800.png` (PNG, <size> KB)
- Direction: <A people | B UI screenshot | C abstract>
- Background: <color>, <mono-tone gradient | flat>, contrast vs CWS white
- Caption (small): "<text>"
- Caption (large): "<text>"
- Alternatives tried:
  - <alternative 1> — <one-line reason rejected>
  - <alternative 2> — <one-line reason rejected>

## Icon

- Files: 16×16, 48×48, 64×64, 96×96, 128×128 (96-in-128 transparent margin)
  + `store-128.png`
- Source: <flaticon.com/<id> | original artwork>
- Style: <minimal B&W | colored multi-element>
- 16×16 squint test verdict: <passes | fails — replaced with X>

## Welcome Page

- URL: https://<host>
- Host: <Tilda | own subdomain | Vercel | GitHub Pages>
- Goal: <find-and-pin | artifact button | new-tab accept>
- Blocks: <count, must be ≤2>
- Screenshots: <count, with arrow+number scheme>
- Analytics: <tool>, Webvisor=<yes|no>
- Auto-open code verified: <yes|no, file path>
- Copy ChatGPT-corrected: <yes|no>

## Locales

- Count uploaded: <50+>
- Manual locales (per 10× rule):
  | Locale | Name decision | EN vol | Local vol | Verdict | Name | Short desc chars |
  | de | local | 1.2K | 18K | local ≥ 10× EN | Werbeblocker | 128 |
  | fr | combined | 4.5K | 9K | between | Bloqueur de pubs \| Adblocker | 132 |
  | nl | English | 6.7K | 400 | EN ≥ 10× local | Free Adblocker | 124 |
  | ... (continue for every manual locale)
- Auto-translated locales (Localizer): <list>
- Uploader script: `references/cws-locale-uploader.js`,
  hash=`<sha256-prefix>`
- Spot-checked locales after refresh: <de, ru, ja, ...>

## Permissions

- host_permissions:
  - <pattern> — "<justification>"
- permissions:
  - <name> — "<justification>"
- Widening decision: <none | widened with cws-careful approval on YYYY-MM-DD>

## Submission

- Extension ID: <abc...123>
- Archive: dist/$SLUG-v<version>.zip
- VT scan: <id>, date <YYYY-MM-DD>, clean
- Differ from competitor: <name diff = N words; competitor optimized
  yes/no>
- Privacy Policy URL: https://...
- Single purpose: "<one sentence>"
- Remote code: no
- Data collection: <none | list>
- careful-submit gate: passed on <YYYY-MM-DD>
- Submitted at: <ISO timestamp>
- Moderation status: pending
- Store URL (post-approval): <fill in after approval>
```

## 9.3 — Write the file

```bash
mkdir -p ./.cws
cat > ./.cws/03-launch.md <<'EOF'
<file contents per 9.1 + 9.2>
EOF
```

Update `state.json` (the script in 8.7 already did this if Phase 8
completed).

---

# When NOT to use cws-launch

| Situation | Use instead |
|-----------|-------------|
| Post-launch banner / icon swap on an approved listing | `/cws-resync` to propagate the change without breaking other fields |
| Post-launch locale tweak (one locale's name needs revising) | `/cws-resync` — re-runs the 10× rule for that locale and re-uploads via the script without touching others |
| Post-launch description rewrite | `/cws-package` to redo the copy + `/cws-resync` to propagate |
| Adding a new permission after approval | `/cws-careful` (hard gate) → `/cws-build` (manifest) → `/cws-resync` (propagate) — never directly in cws-launch |
| Moderation rejected and needs resubmit | `/cws-careful` to weigh the second-submission stricter-scrutiny cost → `/cws-resync` to fix the specific flagged field |
| Wanting to A/B different banners | Quasi-A/B only (ship variant A for a week, then B) — there's no real A/B infrastructure for CWS at launch. Add via `/cws-promote` after approval |
| Initial listing copy work | `/cws-package` — that's where listing copy lives |
| Build / manifest / archive zipping | `/cws-build` |
| Picking the head keyword | `/cws-idea` |

cws-launch is the **one-shot** assets+publish stage. Re-entry on an
approved listing always routes through `/cws-resync` to avoid
republishing fields that didn't need to change.

---

# Companion skills

| Skill | When | Why |
|-------|------|-----|
| `/cws-careful` | Immediately before Phase 8.6 (Submit for review) | M12 — hard gate. Logs `careful-submit` in `gates_passed`. cws-launch refuses to advance otherwise. |
| `/cws-challenge` | Before Phase 8 if the user has time | Stress-tests the chosen banner direction, icon style, locale set against competitor moves you might have missed |
| `/cws-promote` | After moderation approves | Ad warm-up cannot wait. Reviews widget, paid installs, behavioral-factor stabilization |
| `/cws-retro` | While moderation is pending (1–3 business days SLA) | Baseline snapshot of all metrics before promotion starts. Otherwise you have nothing to compare against |
| `/cws-resync` | Any post-submit edit | Propagates a single field change without rerunning the whole asset+publish flow |

The bootcamp routing rhythm:

```
cws-launch  →  cws-careful  →  cws-launch (submit)  →  cws-retro (baseline)
                                                  →  wait (1–3 business days)
                                                  →  approved → cws-promote
                                                  →  rejected → cws-resync
```

---

# Tools

- **AskUserQuestion** — every D-brief in Phases 0–7. Iron rules and
  Phase 8 / 9 are mechanical — never D-brief these.
- **Bash / Read / Write / Edit** — `.cws/03-launch.md`, `state.json`,
  pre-submit checks, locale file validation.
- **Grep / Glob** — finding empty `messages.json` entries, locating the
  install listener in the service worker.
- **WebFetch** — fetching competitor CWS listings for the differ-check
  in Phase 8.3.1; fetching the Privacy Policy template doc.
- **WebSearch** — verifying national-language keyword candidates in
  Phase 5.

## Tools that don't help here

- **Semrush MCP** — used in `cws-idea` for the English head keyword
  and in cws-launch only for the per-locale 10× rule lookups
  (5.2.2 / 5.2.3 / 5.2.6). Don't re-run head-keyword research here;
  that's a regression to Stage 1.
- **Building anything** — that's `cws-build`. Including manifest edits.
- **Writing listing copy** — that's `cws-package`.
- **Picking the head keyword** — that's `cws-idea`.

---

# Tools NEVER to use in cws-launch

- **Direct CWS API uploads** — there is no general CWS API for what
  this stage needs. The dashboard DOM is the only path. Use
  `references/cws-locale-uploader.js` for locale uploads; do everything
  else through the dashboard UI.
- **Headless browser automation against CWS** — Google flags
  automation; the dedicated Google account from Stage 0 can be
  suspended. Manual dashboard clicks only.
- **Bulk publishing without `cws-careful`** — M12. Hard gate.

---

# Gate criteria (formal)

Phase 9 writes `03-launch.md` with `status: complete` and updates
`state.json`:

```json
{
  "extension": {
    "id": "<32-char>",
    "draft_uploaded": true,
    "submitted_for_review": true,
    "moderation_status": "pending",
    "submitted_at": "<ISO timestamp>"
  },
  "gates_passed": ["account-setup", "idea", "package", "build",
                   "careful-submit", "launch"]
}
```

Anything less = gate not passed = the next skill (`cws-retro` baseline,
then `cws-promote` once approved) refuses to run.

---

# Skill Routing Footer

If `careful-submit` not in `gates_passed`:

```
Next: /cws-careful
Why: Pre-submit hard gate. cws-launch refuses to click "Submit for review"
until cws-careful logs gates_passed += ["careful-submit"]. Re-enter
cws-launch after.
```

If `careful-submit` IS present and Phase 8 completed (submitted):

```
Next: wait — CWS moderation is pending; usual SLA 1–3 business days.
While you wait, run `/cws-retro` once to capture the pre-promotion
baseline (installs=0, reviews=0, position=untracked). On approval,
run `/cws-promote` for ad warm-up + reviews widget.
```

If Phase 0 blocked because a prior gate is missing:

```
Next: /cws-<package|build|idea>
Why: cws-launch requires <gate>; Stage 3 cannot run before that gate
clears. Re-enter cws-launch after.
```

Never list 2–3 options. Pick exactly one based on the state machine.
