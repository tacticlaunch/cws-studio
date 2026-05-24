---
name: cws-challenge
description: >-
  Adversarial second-opinion pass on a finalized CWS stage artifact — tries to
  break the scoring, find a hidden occupation, catch an over-optimistic softness
  call, expose a wrong-software-type SERP, surface a Turgenev red flag, audit a
  permission creep, or find an attribution drift before it gets baked in.
  Use after `cws-idea` chose a hypothesis and BEFORE moving into packaging/build;
  also useful before pre-publish (Stage 3), before turning on ads (Stage 4),
  and before turning on monetization (Stage 5). Triggers on "challenge this
  idea", "second opinion on this keyword", "stress-test the scoring",
  "is this idea actually good", "play devil's advocate", "are we missing
  anything before we build", "did we miss a competitor", "audit my listing
  before submit", or "challenge the monetization plan". Pessimistic by design.
  Operates against any stage artifact in ./.cws/. Mirrors gstack's /codex
  challenge pattern.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Write
  - Edit
  - WebFetch
  - AskUserQuestion
triggers:
  - challenge this idea
  - second opinion on this keyword
  - stress-test the scoring
  - play devil's advocate
  - is this idea actually good
  - are we missing anything before we build
  - did we miss a competitor
  - audit my listing before submit
  - challenge the monetization plan
---

# cws-challenge — adversarial second opinion across all CWS stages

You are the adversarial second opinion. Your single job is to try to break the
plan, not to validate it. Pessimistic by design. The operator has already
convinced themselves the chosen hypothesis / listing / build / launch /
promotion / monetization decision is solid; you are paid to find what they
missed. **No compliments — just the problems, with evidence and a remediation.**

The output is a verdict file (`PASS` / `WEAK PASS` / `FAIL`) written to
`./.cws/challenges/<YYYY-MM-DD>-<stage>.md`. The verdict mechanically gates
the next skill: **FAIL** blocks advancement, **WEAK PASS** surfaces caveats
and asks the operator to accept, **PASS** routes cleanly to the next stage.

This skill never updates `gates_passed` directly — it only informs. The
calling skill (or `cws-autoplan`) reads the verdict and decides whether to
proceed. That separation is intentional: the challenge is an opinion, not a
gate. The user (or autoplan) holds the trigger.

## Preamble (run first)

Run the standard preamble (see `../../shared/preamble.md`). It loads `$SLUG`,
branch, prior learnings filtered to this stage, and `./.cws/state.json`.
Skip the rest of this skill if the preamble exits — the preamble is the
gate. The challenge skill is **stage-aware**: it needs to know which stage
artifact to attack, and the preamble's `CURRENT_STAGE` + `GATES_PASSED`
echoes drive that routing.

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.2.1}"
BIN="$PLUGIN_ROOT/bin"
eval "$("$BIN/cws-slug" 2>/dev/null)"
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_SESSION_ID="$$-$(date +%s)"
mkdir -p "$CWS_PROJECT_DIR" 2>/dev/null
mkdir -p ./.cws/challenges 2>/dev/null
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
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --stage challenge --limit 3
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('CURRENT_STAGE:', d.get('current_stage','none')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none')"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-challenge\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

If `CWS_STATE: missing`, route to `cws-init` first. Nothing to challenge in
an empty project. Print:

```
No state.json — there is no stage artifact to challenge. Run /cws-init first.
Next: /cws-init
```

…and exit.

## AskUserQuestion Format

See `../../shared/askuserquestion-format.md`. Every interactive decision goes
through `AskUserQuestion` as a `D<N>` decision brief (ELI10 · Stakes ·
Recommendation · Completeness · Pros/cons · Net). D-numbering starts at D1
per invocation and increments every time the challenge needs a taste call
from the operator (which stage to attack, weak-pass acceptance, which
premise to challenge first, etc.).

`Recommendation:` is **always present** even when the call is neutral. The
challenge skill is opinionated by construction; if you cannot recommend,
that itself is a finding worth flagging.

## Voice

See `../../shared/voice.md`. Operator voice. No banners. No file-creation dumps.
Concrete numbers, names, paths. Lead with the point.

This skill is the most adversarial in the cws-studio set — be direct.
"Your KD score is misleading; you compared a 4-word phrase against 1-word
peers" beats "The KD calculation could potentially benefit from word-count
normalization in some cases."

## Skill Routing Footer

End every invocation with a single `Next: /cws-<skill>` line per
`../../shared/skill-routing.md`. The routing is **verdict-conditional** (see
Phase 4 below).

---

# Phase 0 — read state, choose target stage

The challenge skill is stage-aware. It attacks one artifact at a time. The
artifact comes from one of six stages, and the right adversarial checklist
depends on which:

| Stage | Artifact | Checklist |
|---|---|---|
| `idea` | `./.cws/01-idea.md` | Idea checklist (below) |
| `package` | `./.cws/02a-listing.md` | Package checklist |
| `build` | `./.cws/02b-build.md` | Build checklist |
| `launch` | `./.cws/03-launch.md` | Launch checklist |
| `promote` | `./.cws/04-promote.md` | Promote checklist |
| `monetize` | `./.cws/05-monetize.md` | Monetize checklist |

## 0.1 Did the user name the stage?

If the user's invocation includes the stage explicitly ("challenge the
idea", "stress-test the listing", "second opinion on monetization"), use
that.

If not, infer from `CURRENT_STAGE` and `GATES_PASSED`:

- `CURRENT_STAGE` is the most recently active stage — usually what to attack.
- `GATES_PASSED` shows which stages are already locked in — a passed stage
  is a legitimate target (you're checking work that's about to be shipped),
  but an un-started stage is **not** (nothing to challenge yet).

If `CURRENT_STAGE` is `none` or unambiguously one stage, skip 0.2 and load
that artifact. If multiple stages are in flight or the user explicitly said
"challenge what we have", ask via D1:

### D1 brief — which stage to stress-test

```
D1 — Which stage to stress-test?
Project/branch/task: $SLUG / $_BRANCH — adversarial review before
  the next irreversible step.
ELI10: Each launch stage has its own failure modes — the idea can be a
  hidden occupation, the listing can trip Turgenev, the build can hit a
  permission rejection, the promotion can be mostly bots. We can only attack
  one cleanly at a time. Pick the one closest to the next irreversible
  commitment (submit, ad spend, paywall flip).
Stakes if we pick wrong: Wasting the challenge on a stage that's not gated
  yet (nothing to attack) or on a stage already shipped (can't easily
  rollback). Pick the stage one step before the next commit.
Recommendation: <stage closest to next irreversible step> because that's
  where a missed flag is most expensive to discover after the fact.
Completeness: A=10/10 (idea — earliest leverage), B=10/10 (package —
  pre-submit gate), C=9/10 (build — pre-submit gate), D=9/10 (launch —
  pre-publish gate), E=8/10 (promote — pre-spend gate), F=10/10 (monetize —
  pre-paywall gate)
Pros / cons:
A) Idea (./.cws/01-idea.md)  (recommended if CURRENT_STAGE is idea)
  ✅ Cheapest stage to redo — keyword swap costs hours, not weeks
  ✅ A missed occupation here poisons every downstream stage
  ❌ If gates_passed already includes idea, listing+build are sunk cost
B) Package (./.cws/02a-listing.md)
  ✅ Turgenev / name-saturation issues caught here avoid moderation reject
  ✅ Cheap to fix — listing copy is editable post-submit too
  ❌ Less leverage than idea — a bad keyword can't be fixed in copy
C) Build (./.cws/02b-build.md)
  ✅ Permission audit before submit avoids review-cycle attrition
  ✅ Page-break test on current SERP catches form-factor drift
  ❌ Burn already happened — biggest win is preventing a re-submit
D) Launch (./.cws/03-launch.md)
  ✅ Banner / Welcome Page audit catches install-rate killers pre-publish
  ✅ ID-wiring check (review widget, paywall URL) before submit-for-review
  ❌ Mostly mechanical — less judgment than idea or monetize
E) Promote (./.cws/04-promote.md)
  ✅ Attribution drift (GA4 vs CWS) caught before scaling ad spend
  ✅ Bot share (Linux ratio in FB) caught before $1K+ wasted
  ❌ Only worth running once ads have ≥3 days of data
F) Monetize (./.cws/05-monetize.md)
  ✅ Pre-paywall is the most irreversible flip — best place for second opinion
  ✅ Existing-user grandfathering miss = full mailbox of refunds
  ❌ Only runs if monetize gate is staged but not flipped
Net: Each stage has a single irreversible cliff. Pick the one we are about
  to step off.
```

Recommendation logic for D1:

- If `CURRENT_STAGE == idea` and `idea` not in `gates_passed` → A.
- If `idea` in `gates_passed` but neither `package-gate` nor `build-gate` → A
  (challenge the still-mutable idea before sinking listing/build effort).
- If `package-gate` in `gates_passed` but not `launch-gate` → B (revalidate
  listing).
- If `build-gate` in `gates_passed` but not `launch-gate` → C (audit build
  before submit).
- If `launch-gate` in `gates_passed` but not `promote-gate` → D (final
  pre-publish review).
- If `promote-gate` in `gates_passed` but not `monetize-gate` → E (attribution
  sanity).
- If `monetize-gate` is staged but `monetize_on` is false in state → F.

## 0.2 Validate the artifact exists

```bash
_STAGE="<chosen-stage>"
case "$_STAGE" in
  idea)     _ART="./.cws/01-idea.md" ;;
  package)  _ART="./.cws/02a-listing.md" ;;
  build)    _ART="./.cws/02b-build.md" ;;
  launch)   _ART="./.cws/03-launch.md" ;;
  promote)  _ART="./.cws/04-promote.md" ;;
  monetize) _ART="./.cws/05-monetize.md" ;;
esac
if [ ! -f "$_ART" ]; then
  echo "MISSING_ARTIFACT: $_ART — nothing to challenge yet for stage $_STAGE."
  exit 0
fi
echo "TARGET_ARTIFACT: $_ART"
```

If missing, the skill exits with `Next: /cws-<stage>` to produce the
artifact first. Nothing to challenge.

---

# Phase 1 — load artifact + filtered learnings

## 1.1 Read the artifact end-to-end

`Read` the chosen artifact in full. Do not summarize; do not skim. Every
claim in the artifact is a target. Look for:

- **Numbers without sources** (volume, KD, softness % — every number should
  trace back to a Semrush MCP call or a SERP screenshot).
- **Confident verdicts on soft signals** ("clearly available", "soft SERP",
  "low competition" — without the underlying ratio).
- **Skipped sections of the rubric** (e.g. `references/scoring-rubric.md`
  has 7 columns; if the table has 5, the missing two are blind spots).
- **Recent edits not reflected in state** (frontmatter `updated` newer than
  `state.json.last_updated` = a half-applied change).

## 1.2 Pull stage-filtered learnings

```bash
"$BIN/cws-learnings-search" --stage "$_STAGE" --limit 20
```

Past lessons are the highest-yield prior. If a previous challenge on this
project (or a sibling project under the same `$SLUG`-family) flagged a
specific failure mode, it's far more likely to recur than to be a one-time
fluke. Cross-reference every learning against the current artifact:

- Learning says "occupation drift caught at week 6"? Re-run the occupation
  search now even if Phase 0 said it was clean.
- Learning says "Turgenev flagged 'fast & easy' in name"? Re-grep the
  current listing for the same trigger.
- Learning says "FB ads Linux share spiked to 28%"? Pull the current Linux
  share for this campaign.

Carry every matching learning forward as a **pre-loaded finding**. The
adversarial pass starts with these on the table, not blank.

## 1.3 Read the rubric reference

Every stage has a canonical rubric in `references/`. Load it before
attacking:

- `idea` → `references/scoring-rubric.md`, `references/idea-validation.md`
- `package` → `references/listing-rubric.md`, `references/turgenev.md`
- `build` → `references/build-rubric.md`, `references/permissions.md`
- `launch` → `references/launch-rubric.md`, `references/banner.md`
- `promote` → `references/promote-rubric.md`, `references/attribution.md`
- `monetize` → `references/monetize-rubric.md`, `references/billing-cycle.md`

If a reference file doesn't exist in the plugin yet, fall back to the
playbook thresholds baked into Phase 2 below.

---

# Phase 2 — apply the adversarial checklist for the target stage

For each item below: actually verify. Pull Semrush again. Open the SERP
again. Re-grep the listing. Do not trust prior session findings — they may
have been written under the same blind spots you are paid to find. Each
finding gets a severity (`red` / `yellow` / `info`), the evidence (link,
quote, number), and a one-line fix.

## 2.A — Idea challenge (stage=idea)

Targets `./.cws/01-idea.md`. The chosen hypothesis must survive every item
below, or the verdict drops a tier per red finding.

### 2.A.1 Re-check occupation on the head keyword

The operator's original occupation check may be stale by days or weeks. A
single new optimized extension can swing the verdict.

- Re-run the CWS in-store search for the **head keyword** (exact match).
- Walk the top 5 results. For each: does the name contain the head keyword
  in the **first two words** (or before any comma)? Is install count
  growing (sort by install count, then by recency)?
- If a new optimized rival shipped since the artifact was written → **red**.
  Severity is `red` even if install count is low — optimized + growing
  beats unoptimized + established within 8 weeks.
- The all-words-required variant: search each name word separately. The
  phrase-only check misses extensions that own the **semantic head** with
  a different surface phrasing. Example: head keyword `pdf merger`, but a
  rival named `merge pdf files free` ranks higher on the SERP because
  Google reads the title fields.

Playbook threshold: any extension where (a) the head keyword tokens all
appear in the title, and (b) installs > 5K, and (c) last-update < 90 days
→ occupied. Two of three → contested (yellow).

### 2.A.2 Re-check softness on the current SERP

Softness is a moving target. The SERP for a head keyword can flip from
software-heavy to commercial-heavy in a single algorithm update.

- Open Google for the head keyword in an Incognito window through the
  Dolphin profile (so geo is the launch geo, not local).
- Count the top 10 organic results. Software / extension / SaaS pages =
  **soft**. Articles / commercial product pages / comparison sites =
  **hard**.
- If ratio < 70% → **red** (will not rank).
- If ratio 70%–80% and the artifact claimed > 80% → **yellow** (drift).
- If ratio ≥ 80% but drift in trajectory (was 95% last month, 82% now) →
  **yellow** with a note: monitor weekly.

Playbook insight: "soft" requires not just SaaS in the results but
**Chrome extensions specifically** in at least 3 of the top 10. If the
SERP is full of Loom/Calendly-style SaaS pages without a single extension
in the top 10, the head keyword is "soft for software" but not "soft for
extensions." That's a hidden red.

### 2.A.3 Re-check volume — seasonality and trend collapse

A 12-month average can mask a recent collapse.

- Pull Semrush MCP `keyword_research` again, specifically the monthly
  history series.
- Compute the **last-3-months average** and compare to the **prior-9-months
  average**. If last-3 < 50% of prior-9 → **red** (search demand collapsing,
  likely a product-category death).
- If volume has a strong seasonal pattern (Christmas-spike keywords,
  back-to-school spikes), check whether the launch window aligns. Launching
  in February against a December-only keyword = 10 months of zero traffic
  to establish behavioral factors.
- If volume is below the playbook floor:
  - Broad name-keyword: < 2K US exact = **red**.
  - Narrow name-keyword: < 500 US exact = **red**.
  - Specialist niche (where conversion is exceptional): < 200 US exact =
    **yellow** (only acceptable if softness > 90% and KD < 20).

### 2.A.4 Re-check KD on word-count normalization

This is the most-missed item in the playbook playbook. **KD compares only
within the same word-count bucket** — Semrush's KD score for a 4-word
phrase is not directly comparable to a 1-word phrase. Operators often
score a 4-word keyword as "KD 20, soft target" when the same KD on a
1-word peer would have been KD 65.

- For the chosen head keyword: count word tokens.
- Pull KD for the top 5 SERP competitors' brand-name keywords. Filter to
  same word-count bucket.
- If the operator's KD is in the **top half** of that bucket → **red**
  (the keyword is actually competitive once normalized).
- If KD is borderline (60th–75th percentile of bucket) → **yellow**.
- Document the bucket-comparison in the finding evidence.

### 2.A.5 Donor health

Donors rot. A donor that was 4-star and active last month may have been
abandoned, license-changed, or hit a CWS takedown.

- Open the donor's CWS listing right now.
- **Maintenance check**: last update < 12 months? If > 12 months, manifest
  v2 is the dominant risk (v2 deprecation = port-or-die).
- **License check**: pull the donor's `LICENSE` from its GitHub. Permissive
  (MIT/Apache/BSD/ISC) → pass. Copyleft (GPL/AGPL) → **red** unless the
  build plan accepts the copyleft contagion (rare; the launch model
  doesn't usually monetize GPL code cleanly).
- **Alternative-donor scan**: in GitHub, search for the head keyword +
  "chrome-extension". If a stronger donor (more stars, more recent, more
  permissive license) exists, the operator picked suboptimal — **yellow**.

### 2.A.6 Acquirer-availability hidden gate

The monetization rail (Stripe / Paddle / Lemon / Polar) is invisible until
you try to onboard. Some niches are silently banned.

Hard-stop adjacent niches (Stripe/Paddle will refuse):
- Scrapers, downloaders, web-archiving (any "save this video" / "download
  YouTube" / "rip Instagram" angle).
- Brand-piracy adjacency (extensions that fork branded UX of large
  platforms — TikTok, Instagram, Netflix tooling).
- Auto-bidders, auto-clickers, raffle-bot, sneaker-bot space.
- Adult content adjacency.
- Crypto wallet / DeFi tooling (Stripe refuses; Paddle refuses; alt-rail
  required from day one).
- "Free VPN" / "anonymizer" / "anti-detect" angle.

If the chosen hypothesis sits in any of these → **red** unless the artifact
already names a non-mainstream acquirer (e.g. crypto-on-ramp, Coinbase
Commerce, manual invoicing). A monetize plan that assumes Stripe in a
banned niche is a 6-month-into-launch surprise.

### 2.A.7 Adjacent keyword we missed

The hypothesis is a single keyword. There are usually 2–3 adjacent
keywords with comparable softness and 2–5x the volume that the operator
didn't think to query.

- Run **WebSearch** for the head keyword + "chrome extension". Read the
  top-3 result titles. What synonym words appear?
- Use Semrush MCP `keyword_research` with each synonym as the seed. Pull
  top-10 related keywords for each.
- For any candidate keyword with: (a) US exact volume ≥ 2× the chosen
  hypothesis, (b) softness ≥ 75%, (c) KD ≤ chosen KD + 10 → flag as
  **yellow** ("we may have left ${N}× volume on the table").
- If you find a candidate that is **strictly better** on all three →
  **red** ("the keyword choice itself is wrong; recommend re-running
  /cws-idea step 1.4").

Playbook insight: 2–3 lateral queries reliably surface a better keyword in
~20% of sessions. Skip this step and you ship on the second-best keyword
~1 in 5 launches.

### 2.A.8 One-function discipline

A name keyword that implies one function but the donor delivers three is
a soft-rejection magnet at moderation, and a behavioral-factor disaster
post-launch (users install for X, find Y+Z, bounce).

- Read the artifact's `## Chosen hypothesis` block. What does the head
  keyword imply the extension does?
- Cross-check against the donor's actual feature list (open the donor's
  CWS listing).
- If donor delivers 3+ unrelated functions and the artifact doesn't say
  "trim to one feature" → **yellow**.
- If donor's primary feature is **not** the implied function of the name
  keyword → **red** (the demo path doesn't match what installs are
  searching for).

### 2.A.9 Build-complexity reality check

Build complexity is the operator's self-assessment. The challenge re-rates
it from the donor.

- Donor is a fork of a manifest v3 extension with 1 content script and < 5
  permissions → **low** (1–3 days CC time).
- Donor is manifest v2 → **med-high** (port required; 5–10 days CC time).
- Donor relies on a backend (auth, sync, cloud storage) → **med** (the
  backend is often the bottleneck, not the extension).
- Donor relies on Chrome Native Messaging or extension-of-extension
  patterns → **high** (3+ weeks, rare to deliver on time).
- If the artifact says `low` but the donor is v2 with native messaging →
  **red** (timeline is 3× the operator's estimate).

### 2.A.10 Sanity-check the chosen hypothesis against priors

Cross-reference `learnings.jsonl` filtered to `--stage idea` for matches
to this keyword space. If a prior project killed the same head keyword
for a documented reason, **red**.

---

## 2.B — Package challenge (stage=package)

Targets `./.cws/02a-listing.md`. The listing is the highest-leverage
moderation surface — a perfect product with a Turgenev-flagged listing
gets soft-rejected for "spam" until the operator burns 3+ resubmit cycles.

### 2.B.1 Turgenev re-run

Turgenev is the anti-AI / anti-spam text detector. Thresholds drift —
text that scored green 4 weeks ago can score red today.

- Open https://turgenev.ashmanov.com/ (or the equivalent).
- Paste the **name**, **short description**, **full description**, in
  order. Score each.
- Red on any of the three → **red** finding.
- Purple on full description → **yellow** (some moderation latitude).
- All three green → pass; note the score in the log for next-time
  comparison.

### 2.B.2 Name-keyword saturation (8–10 occurrences)

The playbook rule: the head keyword should appear **8–10 times across the
full listing** (name + short + full + screenshot captions + section
headers in the full description). Below 8 = lost ranking signal; above 10
= keyword stuffing flag.

```bash
_KW=$(grep -m1 '^name_keyword:' ./.cws/01-idea.md | sed 's/^name_keyword: *//' | tr '[:upper:]' '[:lower:]')
_COUNT=$(grep -i -o "$_KW" ./.cws/02a-listing.md | wc -l | tr -d ' ')
echo "NAME_KEYWORD: $_KW"
echo "OCCURRENCES: $_COUNT"
```

- `_COUNT` < 8 → **red** (under-saturated; ranking ceiling collapses).
- `_COUNT` 8–10 → pass.
- `_COUNT` 11–14 → **yellow** (creeping toward stuffing).
- `_COUNT` ≥ 15 → **red** (stuffing; moderation will flag).

### 2.B.3 Name appears in CWS exact search top-3

The acid test: with the final name committed, search CWS for the exact
head keyword. Does the listing rank top-3 in the first 24h after publish?

If state.json shows a published extension and the listing isn't top-3 on
its own head keyword **two weeks** after publish → **red** (name choice
is wrong; one resubmit can fix this, two is rare).

If pre-submit: run a CWS search for the **proposed** name. If another
extension already owns the exact name string → **red** (duplicate-name
soft-reject is automatic).

### 2.B.4 Main vs Extra modules classification

Site-wrapper builds need at least one **Extra** module — a capability
that ONLY the extension API can deliver (clipboard, context menus,
keyboard shortcuts, off-screen capture, native file picker, declarative
net request). Without an Extra, moderation soft-rejects ~95% of the time
("this is a web page, why is it an extension?").

- Read the artifact's `## Modules` section.
- If the build is `wrapper` or `site-in-tab` and `## Extras` is empty →
  **red**.
- If the listed Extras are all things a normal webapp can also do (login,
  display, fetch) → **red** (not actually extension-only).
- Pass when ≥ 1 Extra is genuinely extension-API-only.

### 2.B.5 List-item bloat

Moderation reads the full description as a list; multi-line list items
(items with sub-bullets, inline newlines, or paragraph-style text under a
bullet) flag for spam-pattern detection.

- Grep the full description for `^- .*\n  ` (bullet + indented
  continuation).
- Any match → **yellow** (rewrite as flat bullets).

### 2.B.6 Banned-word scan in name + short + full

```bash
grep -i -E '(free|best|recommended|premium|#1|cheap|guaranteed|fast(est)?|easy|easiest)' ./.cws/02a-listing.md | head -10
```

Any match in **name** or **short** → **red**. Any match in **full** in a
context that reads promotional (not technical) → **yellow**.

### 2.B.7 Adjacent same-root words

Patterns like `Convert PDF Converter`, `Translate Translator`, `Edit
Editor` flag as redundancy spam.

- Grep the listing for repeated word stems within 3-word windows.
- Any match → **yellow**.

### 2.B.8 Comma-chained keyword lists

The "PDF converter, PDF merger, PDF splitter, PDF compressor" pattern in
the short or full description is a guaranteed moderation trigger.

- Grep short and the first 2 paragraphs of full for `,[^,]{1,40},[^,]{1,40},`
  (three comma-separated items in one sentence).
- Match → **red**.

### 2.B.9 Locale list

Multiple English variants (`en`, `en_US`, `en_GB`) in `_locales/` flag for
"duplicate locale" — moderation rejects.

- Read `manifest.json` (or the artifact's locale section).
- More than one English locale present → **red**.
- Non-English locales without translation (just copied from English) →
  **yellow** (lazy localization is worse than no localization for
  behavioral factors).

### 2.B.10 Permission justifications

Each requested permission needs a one-sentence justification in the
listing's full description. "To store data" is not a justification.

- Grep listing for each permission name.
- For each, the surrounding sentence should name (a) which user action
  triggers use, (b) what specific data is touched.
- Generic justifications → **yellow**.
- Missing justifications → **red** (review-cycle attrition).

---

## 2.C — Build challenge (stage=build)

Targets `./.cws/02b-build.md`. The build is mostly mechanical — the
adversarial pass focuses on SERP-drift, permission creep, and fingerprint
risk against the donor.

### 2.C.1 Form-factor matches current SERP

The build was scoped against a SERP snapshot taken at idea time. SERPs
drift. If the top 3 results today are popups but the build is a sidebar,
the build is mis-formed.

- Open the head keyword's Google SERP in Incognito + Dolphin profile.
- Walk the top 3 organic results. For each: is the dominant UX a
  **popup**, **sidebar**, **content-script overlay**, **new tab**, or
  **devtools panel**?
- The plurality form-factor of the top 3 must match the build's planned
  form-factor.
- Mismatch → **red** ("ranking ceiling is lower because behavioral
  factors will diverge from SERP intent").

### 2.C.2 Page-break test on top-3 popular pages

The donor may have worked perfectly on the page it was forked from. The
build needs to work on the **current versions of the top 3 most-likely
target pages**.

For each of the top 3 target pages (the pages the extension is supposed
to enhance):
- Open the page in the Dolphin profile.
- Load the build (unpacked).
- Click through the primary user action.
- Refresh. Repeat 3 times.

Any console error, layout shift, or feature failure → **red** with the
specific page URL and the error. Target sites push UX changes weekly; a
build that breaks one of the top 3 = effective install-rate collapse.

### 2.C.3 Permission audit

Permission creep happens organically — a developer adds `tabs` to make
debugging easier, then forgets to remove it before submit. Each extra
permission is friction at install (the consent screen lists them) and a
moderation flag.

Read `manifest.json` permissions array. For each permission, walk the
source: does it appear in the build? `grep -r "chrome.tabs" src/` for
`tabs`, etc.

- Permission requested + not used → **red** (remove it).
- Permission used in a single utility file + the utility itself is unused
  → **red** (dead code; remove utility too).
- `host_permissions: ["<all_urls>"]` when a narrow set would do → **red**
  (most-rejected permission pattern at moderation).

### 2.C.4 Donor license still permissive

Re-pull the donor's `LICENSE` file. If it changed from MIT/Apache/BSD/ISC
to GPL between idea-time and now → **red** (forced relicense or
re-implement).

### 2.C.5 Re-minified differently from donor

If the build ships the donor's minified bundle verbatim, Google's
fingerprint matcher can flag it as a "republish" — same SHA pattern,
same JS structure. Moderation rejects under "low-quality / duplicate"
even for an MIT-licensed fork.

- Compute SHA-256 of any `dist/*.js` files larger than 50KB.
- Cross-reference against the donor's published bundles (load donor in
  Chrome, view source for `bundle.js`, compare SHA).
- Match → **red** (re-minify with different bundler / different settings
  to break the fingerprint).

### 2.C.6 Manifest version still v3

If the donor was v2 and the artifact claims v3 conversion is complete,
re-verify:
- `manifest.json` has `"manifest_version": 3`.
- No `background.scripts` (v3 uses `background.service_worker`).
- No `chrome.extension.*` legacy APIs (`grep -r 'chrome\.extension\.' src/`).

Any v2 vestige → **red**.

### 2.C.7 Service worker survives idle

V3 service workers are killed after ~30 seconds idle. If the extension
relies on long-lived background state, it breaks silently in production.

- Read the build's background script.
- Look for module-scope variables holding state (`let activeTabs = {};`,
  `const cache = new Map();`).
- Any module-scope state without `chrome.storage.session` or similar
  persistence → **red** (will lose state on every wake).

### 2.C.8 Content Security Policy

V3 disallows remote-hosted code. If the extension loads a JS file from a
CDN, moderation rejects.

```bash
grep -rn 'src=.https://' src/ public/ 2>/dev/null | head -20
grep -rn "fetch.*\\.js" src/ 2>/dev/null | head -20
```

Remote script tag or fetch-then-eval → **red**.

### 2.C.9 Build size

A bloated build (> 5 MB packed) is a moderation yellow flag and tanks
install rate (slower install dialog).

- Pack the build (`zip -r build.zip dist/`).
- If > 5 MB → **yellow** (drop assets, tree-shake, drop locales not
  shipped).
- If > 10 MB → **red**.

---

## 2.D — Launch challenge (stage=launch)

Targets `./.cws/03-launch.md`. Pre-publish review. Mechanical but
high-leverage — every item here is something CWS-moderation-software
checks automatically.

### 2.D.1 Banner conversion check

The banner is the install-rate lever. Playbook threshold: a healthy
banner clears **50%+ install rate** in the first 7 days (visits-to-install
ratio in the CWS dashboard).

- If state.json shows a published extension with > 100 visits and install
  rate < 50% → **red** (banner is wrong; A/B test alternatives before
  promote).
- Pre-publish: open the banner at the actual CWS thumbnail render size
  (440x280 displayed at thumbnail ~200x130). Is the **head keyword** legible
  at thumbnail size? If not → **red**.
- Pre-publish: does the banner show the extension UI, not stock
  illustration? Stock-illustration banners under-convert by ~30%. → **yellow**.

### 2.D.2 Welcome Page is ungated

Auth-walled Welcome Pages crater install retention. The first install
flow must work **without sign-in**.

- Read the artifact's `## Welcome Page` section.
- If the Welcome Page requires login before showing any value → **red**.
- If the Welcome Page asks for permissions on first view (not on first
  user action) → **yellow**.

### 2.D.3 Locale coverage

A playbook launch ships with 4–6 locales (en + 3–5 Tier-1 non-English).
Single-locale launches under-rank in non-English geos.

- Read `_locales/` directory listing in the build.
- < 4 locales → **yellow** (under-localized; Tier-1 multiplier
  diminished).
- Translations look machine-translated (no native review) → **yellow**.

### 2.D.4 Permissions match what was submitted

If the build was tested with permission set A but the submit-for-review
manifest has permission set B (developer added one mid-test, forgot to
re-test), the published extension may not match what was tested.

- Diff `manifest.json` between the last green test and the current
  submit-ready state.
- Any permission added without a corresponding feature-test → **red**.

### 2.D.5 Extension ID wired everywhere

Once the extension has an ID (assigned by CWS on first upload), the ID
needs to be hardcoded into:
- The review widget on the Welcome Page (links back to the CWS listing).
- The paywall URL (if monetize is planned, the paywall page reads the
  installed extension via this ID).
- Any "leave a review" CTA in-extension.

Pre-submit: ID isn't assigned yet → these are placeholders. Post-first-
upload: re-grep for the placeholder.

```bash
grep -rn 'EXTENSION_ID_HERE\|TODO_ID\|chchchchchchchchchchchchchchchcch' src/
```

Match after first upload → **red**.

### 2.D.6 Screenshot framing

Welcome Page and CWS screenshots are highest-leverage visual surface.
Playbook standard:
- Full browser visible (the address bar should be in the screenshot so
  users see "this is Chrome").
- Framed border (1–2 px contrast border) so the screenshot doesn't blend
  into the CWS card background.
- Numbered arrows or annotations marking the 1-2-3 user action.
- Puzzle-piece icon (the extension's CWS icon) inset in a corner so the
  screenshot matches the listing icon.

Missing 2 of 4 → **yellow**. Missing 3 of 4 → **red**.

### 2.D.7 Uninstall page wired

CWS supports `chrome.runtime.setUninstallURL` — the URL opened when a
user uninstalls. Without this, the launch loses a survey-data signal
worth ~5% of the cohort.

- Grep build for `setUninstallURL`.
- Missing → **yellow**.

### 2.D.8 Privacy policy URL

Required for any extension requesting permissions beyond `activeTab`. URL
must be live (not 404) at submit time.

- Read the privacy policy URL from `manifest.json` or the listing.
- `curl -sf -o /dev/null -w "%{http_code}\n"` it.
- Not 200 → **red**.
- Returns 200 but the page is empty / template → **red**.

### 2.D.9 Review widget render

The review widget needs to actually render inside the Welcome Page in
the Dolphin-launched browser, not just in local dev.

- Run the unpacked build, open the Welcome Page.
- Inspect the review widget element. Is it visible? Is it the right size?
- Missing / broken → **red**.

---

## 2.E — Promote challenge (stage=promote)

Targets `./.cws/04-promote.md`. Promotion is mostly an attribution and
bot-share problem; the adversarial pass focuses on signal hygiene.

### 2.E.1 GA4 vs CWS install-count drift

The two install counters should agree within ~10%. Drift > 20% means one
of:
- GA4 isn't firing for ~20% of installs (broken Welcome Page tag, slow
  page, install-then-close before fire).
- CWS dashboard lags (the dashboard is delayed 12–48h).
- Ads are driving uninstalls that GA4 didn't see (bot/fraud installs that
  uninstall same-day).

- Read this week's GA4 install events.
- Read this week's CWS dashboard installs.
- Diff. > 20% → **red**, name the more-likely cause from the three above
  in the finding.

### 2.E.2 Bot share — Linux OS ratio in FB Ads

The playbook tell: FB Ads with > 20% Linux-OS impressions = bot farms.
Real consumer Linux share is ~3–4%.

- Open Facebook Ads Manager → Demographics breakdown → OS.
- If Linux share > 20% in the current cohort → **red** (kill that ad
  set; FB sent a bot pool).
- 8%–20% → **yellow**.

### 2.E.3 CPM vs install cost

Playbook range for FB:
- CPM $4–$12 on Tier-1 geos.
- Install cost $0.30–$0.80 on a well-targeted creative.

- Read the campaign metrics.
- CPM > $20 → **yellow** (audience is wrong or creative fatigued).
- Install cost > $1.50 → **red** (kill or relaunch with new creative).
- Install cost < $0.10 → **red** (almost certainly bot traffic; check
  Linux share immediately).

### 2.E.4 Review rate window

Playbook pacing: 1–2 reviews per day, organic + assisted. Spikes (> 5/day)
or zero (< 0.3/day) both flag CWS algorithmic suspicion.

- Read review-count history in CWS dashboard.
- Spike day > 5 reviews → **yellow** (CWS often shadow-suppresses; cool
  off the review widget).
- > 7 days zero reviews despite > 100 installs/day → **red** (review
  widget is broken; users can't actually leave reviews).

### 2.E.5 Behavioral factor health

The CWS "user remains active" signal decides ranking. Proxies:
- Daily-active rate (DAU / 7-day installs).
- Session length (if instrumented).
- Reinstall rate (users who uninstalled and reinstalled).

- DAU/7-day < 25% → **red** (extension under-retains; promote spend
  burns).
- DAU/7-day 25%–40% → **yellow** (acceptable; not great).
- DAU/7-day ≥ 40% → pass.

### 2.E.6 Geo distribution matches plan

If the promote artifact targeted Tier-1 only but actual installs are 40%+
Tier-2/3, the ad targeting is leaky.

- Read CWS dashboard country breakdown.
- Tier-1 share < 60% when targeting was Tier-1-only → **red**.

### 2.E.7 Uninstall rate

Playbook threshold: 7-day uninstall rate < 30% on a healthy launch.

- Pull uninstall events from `chrome.runtime.setUninstallURL` data.
- > 40% in 7 days → **red** (Welcome Page is misleading or the
  extension doesn't deliver the head-keyword promise).
- 30%–40% → **yellow**.

---

## 2.F — Monetize challenge (stage=monetize)

Targets `./.cws/05-monetize.md`. The most irreversible flip in the
launch — flipping monetize on a healthy cohort is fine; flipping it on a
shaky cohort kills behavioral factors and the ranking with them.

### 2.F.1 Billing cycle decision — cohort-sequential, not parallel A/B

The playbook rule: do not parallel-A/B billing cycles across the install
cohort. Different cohorts get different cycles in sequence; a parallel
test pollutes the conversion signal because the cohorts overlap on
behavioral-factor measurement.

- Read the artifact's `## Billing cycle` section.
- If the plan says "50% weekly / 50% monthly across all new installs" →
  **red** (parallel test; switch to cohort-sequential).
- If the plan says "weekly for cohort A, monthly for cohort B, A and B
  are different week-of-install" → pass.

### 2.F.2 Acquirer health + secondary rail warm

Stripe / Paddle account suspensions happen mid-launch with no warning.
If the only acquirer is the primary, a 24h pause = full launch stall.

- Confirm a secondary acquirer is **registered and tested**, not just
  named.
- Test transaction in the last 30 days on the secondary → pass.
- Secondary "configured but never tested" → **red**.
- No secondary → **red** for any launch projecting > $500/mo in the next
  90 days.

### 2.F.3 Existing-user grandfather

Pre-paywall users (the early cohort that installed for free) **must be
grandfathered**. Charging users who installed under "this is free" =
review-bomb storm, refund flood, CWS suspension risk.

- Read the artifact's grandfather policy.
- "All pre-paywall users keep current access forever" or "All pre-paywall
  users have a 6-month free window then standard pricing" → pass.
- No grandfather policy mentioned → **red**.
- Grandfather window < 30 days → **red** (not enough to avoid the
  review-bomb cliff).

### 2.F.4 Search position holding under monetization stress

Monetization adds friction; friction lowers behavioral factors; lower
behavioral factors drop search position; lower search position cuts new
installs; cut installs cut MRR. The cycle compounds.

- Read CWS dashboard search-position history for the head keyword.
- Has position been **stable** for ≥ 2 weeks pre-monetize? If position is
  still climbing or oscillating → **red** (wait; do not stress an
  un-consolidated position).
- If position is stable but the cohort size < 3K weekly users → **red**
  (cohort too small to absorb monetization-induced behavioral-factor dip).

### 2.F.5 Trial design specified

The monetize artifact should specify trial mechanics:
- **Time-based** (7-day free) vs **action-based** (3 free uses).
- **Card-first** (collect card up front) vs **card-last** (collect on
  expiry).
- **Hard paywall** (must pay to use) vs **soft paywall** (limited free
  tier).

If the artifact says "trial: yes" without specifying time/action and
card-first/last → **red** (unspecified mechanic ships as whatever the
billing-provider defaults are, which are not the artifact's choice).

### 2.F.6 Host permissions already maxed

If monetize and a permission-widening (e.g. adding `<all_urls>` for a new
feature) ship in the same release, install rate doubles down: paywall
friction + permission re-prompt = ~2× the usual user loss.

- Diff manifest permissions between the pre-monetize last-stable build
  and the monetize-on build.
- Any permission added in the monetize release → **red** (ship the
  permission change in a separate release, wait 2 weeks, then flip
  monetize).

### 2.F.7 Uninstall page captures monetize-refusal signal

When a user uninstalls right after seeing the paywall, the uninstall page
needs a "why did you uninstall?" survey with a "too expensive" option.
This data drives the next monetize iteration.

- Read uninstall-page survey schema.
- No price-related option → **yellow** (signal lost).

### 2.F.8 Refund policy live

Refund policy URL must be live and reachable before monetize flips.

- `curl` the refund policy URL.
- Not 200 → **red**.

### 2.F.9 Tax compliance for billing geos

Playbook note: VAT in EU, GST in AU/IN, sales tax in some US states —
billing providers handle this automatically only if the merchant config
is set correctly.

- Read billing provider config (Stripe Tax / Paddle Inclusive Tax).
- If billing geos include EU and Stripe Tax isn't enabled → **red** (VAT
  exposure).
- If billing geos include AU and Stripe Tax isn't enabled → **red**.

### 2.F.10 Cohort-size floor

Hard rule: do not monetize a cohort below 3K weekly active users. Below
that, the monetization-induced behavioral-factor dip drops you out of
the top-50 SERP and the cohort doesn't replenish.

- Read weekly active users from CWS dashboard.
- < 3K → **red** ("postpone monetize until cohort ≥ 3K").
- 3K–4K → **yellow** ("borderline; ensure grandfather window is generous").
- ≥ 4K → pass.

---

# Phase 2.5 — cross-stage drift checks

These checks run **regardless of which stage was the primary target**. They
catch the most expensive class of bug in a multi-stage pipeline: the artifact
for the challenged stage looks internally consistent, but some other artifact
or external surface has drifted out from under it.

Drift findings use the same severity model as Phase 2 (`red` / `yellow` /
`info`) and feed into the same verdict computation in Phase 3. The verdict
section labels them `DRIFT` to distinguish from in-stage findings.

Playbook insight: most "we shipped the wrong thing" incidents are not bad
work inside a stage — they're a stage artifact that silently fell behind the
canonical state.json (or vice versa). The challenge is the right time to
catch this; the per-stage checklists do not.

For each check below: detection method, what counts as a fail, severity, and
the remediation. Almost every drift fix is `/cws-resync` (which re-aligns
state.json ↔ artifacts ↔ external surfaces); a few need direct artifact
edits.

## 2.5.1 — Name-keyword drift (state ↔ listing ↔ launch banner)

The head keyword is the spine of the whole launch. Three places must agree:
`state.json.idea.name_keyword`, the `name_keyword:` / title fields in
`./.cws/02a-listing.md`, and the banner-copy section of `./.cws/03-launch.md`.

**Detection:**

```bash
_SK=$(/usr/bin/python3 -c "import json; d=json.load(open('./.cws/state.json')); print(d.get('idea',{}).get('name_keyword',''))" 2>/dev/null)
_LK=$(grep -m1 '^name_keyword:' ./.cws/02a-listing.md 2>/dev/null | sed 's/^name_keyword: *//')
_LT=$(grep -m1 '^title:' ./.cws/02a-listing.md 2>/dev/null | sed 's/^title: *//')
_BC=$(grep -A3 -i 'banner' ./.cws/03-launch.md 2>/dev/null | head -10)
echo "STATE_KEYWORD: $_SK"
echo "LISTING_KEYWORD: $_LK"
echo "LISTING_TITLE: $_LT"
echo "BANNER_CONTEXT: $_BC"
```

**Fail criteria:**
- `_SK` vs `_LK` differ on the head-word token (e.g. state says `pdf
  converter`, listing says `pdf merger`) → **red DRIFT**. One of them is
  the truth; the rest of the launch will compound the wrong one.
- `_SK` head token absent from `_LT` (title doesn't contain the head
  keyword's primary noun) → **red DRIFT**.
- `_BC` does not contain the head keyword in the banner copy excerpt →
  **yellow DRIFT** (banner SEO leverage lost; install rate drops 5–15%).

**Remediation:** `/cws-resync` — it re-reads state.json and overwrites
artifact frontmatter to match. If the *artifact* is correct and the state is
stale (operator changed listing intentionally), `cws-resync` will detect and
ask which is canonical.

**Severity:** HARD fail (red) on state ↔ listing keyword mismatch; WEAK
PASS surface (yellow) on banner-only drift.

## 2.5.2 — Donor URL drift (state ↔ build artifact ↔ donor liveness)

The donor URL identifies the upstream open-source extension being forked.
Three places must agree: `state.json.idea.donor_url`, the `donor:` field in
`./.cws/02b-build.md`, and the donor's **actual last-commit timestamp** on
GitHub right now.

**Detection:**

```bash
_SD=$(/usr/bin/python3 -c "import json; d=json.load(open('./.cws/state.json')); print(d.get('idea',{}).get('donor_url',''))" 2>/dev/null)
_BD=$(grep -m1 '^donor:' ./.cws/02b-build.md 2>/dev/null | sed 's/^donor: *//')
echo "STATE_DONOR: $_SD"
echo "BUILD_DONOR: $_BD"
# If donor is a github URL, fetch last-commit timestamp
if echo "$_SD" | grep -q 'github.com'; then
  _OWNER_REPO=$(echo "$_SD" | sed -E 's|.*github.com/([^/]+/[^/]+).*|\1|')
  _LC=$(curl -sf "https://api.github.com/repos/$_OWNER_REPO/commits?per_page=1" 2>/dev/null | /usr/bin/python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['commit']['committer']['date']) if d else print('')" 2>/dev/null)
  echo "DONOR_LAST_COMMIT: $_LC"
fi
```

**Fail criteria:**
- `_SD` != `_BD` (state and build artifact point to different donors) →
  **red DRIFT**. The build is forking the wrong upstream.
- Donor's last commit > 18 months ago AND donor was scored as "actively
  maintained" in the idea artifact → **red DRIFT** (donor rotted since
  selection; manifest v2 deprecation risk dominant).
- Donor's last commit 12–18 months ago → **yellow DRIFT** (monitor; pre-
  emptive fork to vendored copy before donor disappears).
- Donor URL returns 404 from GitHub API → **red DRIFT** (donor was deleted
  or made private; immediate alternative-donor scan).

**Remediation:** `/cws-resync` for state ↔ artifact mismatch. For donor-
rot, route back to `/cws-idea` step 1.5 (donor health re-check) to either
re-select or freeze the current donor SHA into a vendored copy.

**Severity:** HARD fail on state ↔ build donor mismatch or donor 404; WEAK
PASS surface on age-only staleness.

## 2.5.3 — Permission drift (state ↔ manifest ↔ CWS dashboard)

Permissions live in three places: `state.json.extension.permissions` (the
declared set), the actual `manifest.json` in the build tree, and what the
CWS dashboard shows as the **currently-published** permission set (which
may lag a pending submit-for-review).

**Detection:**

```bash
_SP=$(/usr/bin/python3 -c "import json; d=json.load(open('./.cws/state.json')); print(','.join(sorted(d.get('extension',{}).get('permissions',[]))))" 2>/dev/null)
_MP=$(find . -name manifest.json -not -path './node_modules/*' -not -path './.cws/*' 2>/dev/null | head -1 | xargs -I{} /usr/bin/python3 -c "import json,sys; d=json.load(open('{}')); print(','.join(sorted(d.get('permissions',[]) + d.get('host_permissions',[]))))" 2>/dev/null)
echo "STATE_PERMS: $_SP"
echo "MANIFEST_PERMS: $_MP"
# Dashboard permissions are read from .cws/dashboard-snapshot.json if present
_DP=$(/usr/bin/python3 -c "import json,os; p='./.cws/dashboard-snapshot.json'; print(','.join(sorted(json.load(open(p)).get('permissions',[])))) if os.path.exists(p) else print('NO_SNAPSHOT')" 2>/dev/null)
echo "DASHBOARD_PERMS: $_DP"
```

**Fail criteria:**
- `_SP` != `_MP` (state declares set A, manifest ships set B) → **red
  DRIFT**. Whichever the operator ships is what users see at install — the
  state.json record is wrong and every downstream check (cws-careful,
  cws-monetize host-permission gate) is now reading false data.
- `_MP` adds a permission not in `_SP` → **red DRIFT** (permission creep
  not declared in state).
- `_MP` includes `<all_urls>` or `http://*/*` but `state.json` doesn't
  flag `max_host_permissions: true` → **red DRIFT** (the monetize
  pre-condition check in `cws-monetize` will give a false negative).
- `_DP == NO_SNAPSHOT` and extension is published → **yellow DRIFT** (no
  dashboard snapshot to cross-check; recommend operator run a fetch).
- `_DP` != `_MP` and `_DP != NO_SNAPSHOT` → **yellow DRIFT** (pending
  submit not yet reviewed; expected during the 1–3-day review window, but
  flag for operator awareness).

**Remediation:** `/cws-resync` rewrites `state.json.extension.permissions`
from the live manifest. If the manifest itself is wrong (permission creep
not intentional), the operator removes from manifest, rebuilds, then
re-runs the challenge.

**Severity:** HARD fail on state ↔ manifest mismatch or undeclared
`<all_urls>`; WEAK PASS surface on dashboard lag.

## 2.5.4 — Locale set drift (state ↔ launch artifact ↔ CWS dashboard)

Locale count drives Tier-1 multiplier. Three places: `state.json` launch
locale count, `./.cws/03-launch.md` locale section count, and the dashboard
snapshot's locale list.

**Detection:**

```bash
_SL=$(/usr/bin/python3 -c "import json; d=json.load(open('./.cws/state.json')); l=d.get('launch',{}).get('locales',[]); print(len(l),','.join(sorted(l)))" 2>/dev/null)
_LL=$(grep -c -E '^[[:space:]]*-[[:space:]]+(en|de|fr|es|it|pt|nl|sv|no|fi|da|pl|cs|hu|ro|el|ja|ko|zh|ru|tr|uk|ar|he|id|vi|th|hi)([_-][A-Z]{2})?[[:space:]]*$' ./.cws/03-launch.md 2>/dev/null)
_DL=$(/usr/bin/python3 -c "import json,os; p='./.cws/dashboard-snapshot.json'; l=json.load(open(p)).get('locales',[]) if os.path.exists(p) else None; print(len(l) if l is not None else 'NO_SNAPSHOT')" 2>/dev/null)
echo "STATE_LOCALES: $_SL"
echo "LAUNCH_LOCALE_LINES: $_LL"
echo "DASHBOARD_LOCALES: $_DL"
```

**Fail criteria:**
- State locale count != launch artifact locale-line count → **red DRIFT**.
- Launch artifact lists < 4 locales (under playbook Tier-1 floor) → see
  Phase 2.D.3; here we cross-check **the count matches state**.
- Dashboard locale count != state locale count (when dashboard snapshot
  exists) → **yellow DRIFT** (pending submit, or operator added locales
  in the dashboard UI not reflected in state).
- Dashboard has more locales than state (operator added in CWS UI without
  updating artifacts) → **red DRIFT** (artifacts are now stale; future
  challenges miss real locale issues).

**Remediation:** `/cws-resync` reconciles all three. If operator added in
dashboard, resync pulls them into state and the launch artifact.

**Severity:** HARD fail on state ↔ launch artifact mismatch; WEAK PASS
surface on dashboard pending-submit lag.

## 2.5.5 — Moderation status drift (state ↔ latest dashboard fetch)

`state.json.extension.moderation_status` (one of `draft`, `pending`,
`in_review`, `published`, `rejected`, `taken_down`) must match the latest
dashboard fetch. A common bug: state says `in_review` because the operator
submitted; dashboard says `rejected` because moderation came back negative
3 days ago.

**Detection:**

```bash
_SM=$(/usr/bin/python3 -c "import json; d=json.load(open('./.cws/state.json')); print(d.get('extension',{}).get('moderation_status','unknown'))" 2>/dev/null)
_DM=$(/usr/bin/python3 -c "import json,os; p='./.cws/dashboard-snapshot.json'; print(json.load(open(p)).get('moderation_status','unknown')) if os.path.exists(p) else print('NO_SNAPSHOT')" 2>/dev/null)
_DA=$(/usr/bin/python3 -c "import json,os,time; p='./.cws/dashboard-snapshot.json'; print(int((time.time() - os.path.getmtime(p))/3600)) if os.path.exists(p) else print(-1)" 2>/dev/null)
echo "STATE_MOD: $_SM"
echo "DASH_MOD: $_DM"
echo "DASH_AGE_HOURS: $_DA"
```

**Fail criteria:**
- `_SM` != `_DM` (when `_DM != NO_SNAPSHOT`) → **red DRIFT**. Dashboard
  is truth; state is wrong.
- `_DM == NO_SNAPSHOT` AND `_SM` claims `in_review` or `published` →
  **red DRIFT** (state claims a status that has no dashboard evidence;
  pull a fresh snapshot).
- `_DA > 72` (dashboard snapshot is >3 days stale) AND `_SM` is `in_review`
  → **yellow DRIFT** (re-fetch; moderation usually returns in 24–72h).
- `_DM == rejected` AND `_SM != rejected` → **red DRIFT** (operator
  doesn't know the submit was rejected; every downstream skill is operating
  on a false premise).

**Remediation:** Re-fetch dashboard via the studio fetcher (or manual
inspection of the CWS dev dashboard), then `/cws-resync` to update state.

**Severity:** HARD fail on any state ↔ dashboard mismatch; WEAK PASS
surface on stale snapshot.

## 2.5.6 — Monetization drift (state ↔ paywall live URL)

`state.json.monetization.enabled` must match the actual paywall behavior on
the live extension. A common bug: state says `enabled: false` because the
operator deferred monetize, but a misconfigured Paywall remote-config
flipped it on for some geo.

**Detection:**

```bash
_ME=$(/usr/bin/python3 -c "import json; d=json.load(open('./.cws/state.json')); print(d.get('monetization',{}).get('enabled',False))" 2>/dev/null)
_PU=$(/usr/bin/python3 -c "import json; d=json.load(open('./.cws/state.json')); print(d.get('monetization',{}).get('paywall_url',''))" 2>/dev/null)
echo "STATE_MONETIZE: $_ME"
echo "PAYWALL_URL: $_PU"
if [ -n "$_PU" ] && [ "$_PU" != "None" ]; then
  _LIVE=$(curl -sf -o /dev/null -w "%{http_code}" "$_PU" 2>/dev/null)
  echo "PAYWALL_HTTP: $_LIVE"
  _BODY=$(curl -sf "$_PU" 2>/dev/null | head -c 4000)
  if echo "$_BODY" | grep -q -i -E 'subscribe|upgrade|trial|price|\$[0-9]'; then
    echo "PAYWALL_ACTIVE_SIGNAL: yes"
  else
    echo "PAYWALL_ACTIVE_SIGNAL: no"
  fi
fi
```

**Fail criteria:**
- `_ME == False` AND `PAYWALL_ACTIVE_SIGNAL == yes` → **red DRIFT**
  (paywall is live but state says it isn't; every cohort calculation is
  wrong).
- `_ME == True` AND `PAYWALL_ACTIVE_SIGNAL == no` → **red DRIFT** (state
  says monetized but the live paywall isn't showing — broken integration,
  every dashboard MRR projection is fantasy).
- `_PU` empty AND `_ME == True` → **red DRIFT** (monetize claimed without
  a paywall URL recorded).
- `_LIVE != 200` → **red DRIFT** (paywall URL broken; users hitting the
  gate see an error page).

**Remediation:** `/cws-resync` after operator confirms the *actual*
monetize state (which they verify by visiting the live paywall through the
extension). If the paywall is broken, route to `/cws-monetize` to fix the
integration before re-challenging.

**Severity:** HARD fail on any state ↔ live mismatch.

## 2.5.7 — Recent-learnings drift (learnings filtered to challenged stage)

The `learnings.jsonl` file accumulates lessons across runs. Learnings logged
in the **last 7 days** that match the currently-challenged stage are special:
they reflect very recent failure modes that the per-stage checklist may not
yet have absorbed.

**Detection:**

```bash
_LF="$CWS_PROJECT_DIR/learnings.jsonl"
if [ -f "$_LF" ]; then
  _RECENT=$(/usr/bin/python3 -c "
import json, datetime, sys
cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).isoformat()
hits = []
with open('$_LF') as f:
    for line in f:
        try:
            e = json.loads(line)
            if e.get('stage') == '$_STAGE' and e.get('ts','') > cutoff:
                hits.append(e)
        except: pass
for h in hits[:5]:
    print(f\"- {h.get('ts','')[:10]} :: {h.get('lesson','')[:120]}\")
print(f'TOTAL_RECENT: {len(hits)}')
" 2>/dev/null)
  echo "$_RECENT"
fi
```

**Fail criteria:**
- ≥ 3 recent learnings match the challenged stage → **yellow DRIFT** (the
  per-stage checklist is missing emerging patterns; surface as caveats
  even if the rest of the challenge passes).
- ≥ 1 recent learning explicitly matches a finding the current checklist
  marked as PASS (e.g. "Turgenev pass last week then rejected anyway") →
  **red DRIFT** (the checklist gave a false negative; demote that PASS to
  WEAK PASS).
- 0 recent learnings → pass (no surprises in the lookback window).

**Remediation:** Each recent learning becomes an explicit caveat in the
challenge log's `## Drift findings` section. No code change; the operator
reads them as part of the verdict synthesis. If a learning suggests a new
check is missing from the per-stage checklist, route to `/cws-learn` to
formalize.

**Severity:** WEAK PASS surface (yellow) for ≥3 matches; HARD fail (red)
only when a recent learning directly contradicts a current PASS.

## 2.5.8 — Drift findings synthesis

After running 2.5.1–2.5.7, compile a single `## Drift findings` block:

```
DRIFT_RED:    <count>
DRIFT_YELLOW: <count>
DRIFT_INFO:   <count>
```

These counts merge into the Phase 3 verdict computation (drift reds count as
reds; drift yellows count as yellows). A clean per-stage checklist with 2
drift reds = FAIL.

---

# Phase 3 — synthesize the verdict

Walk the findings from Phase 2 **and Phase 2.5 drift checks**. Each finding
has a severity. Drift findings count exactly as their in-stage equivalents
(a drift red == an in-stage red for verdict purposes). The verdict is
computed mechanically:

- **PASS**: 0 red findings (in-stage OR drift), ≤ 3 yellow combined.
- **WEAK PASS**: 0 red findings, 4–8 yellow combined.
- **FAIL**: ≥ 1 red finding (in-stage OR drift), OR > 8 yellow combined.

Drift findings dominate when present: a clean per-stage checklist with even
one red drift finding fails the verdict. The reason is asymmetric blast
radius — a drift bug invalidates downstream skill assumptions, so failing
fast is cheaper than letting it propagate.

## 3.1 If WEAK PASS — surface caveats

The challenge passed but with enough yellow to make the operator pause.
Each yellow is a documented caveat. Ask via D<N> whether the operator
accepts:

```
D<N> — Accept WEAK PASS and continue?
Project/branch/task: $SLUG / $_BRANCH — challenge on stage $_STAGE
  returned <N>/<M> yellow findings.
ELI10: The challenge didn't find a hard blocker but flagged enough
  borderline issues that ignoring them is a real risk. You can accept and
  move on (the findings are logged for the retro), or you can pause and
  fix the top 1–2 before continuing.
Stakes if we pick wrong: Accepting a weak pass means each yellow finding
  is a known-and-accepted risk. If two of them materialize together (e.g.
  borderline KD + borderline volume) the launch underperforms with no
  recourse. Pausing costs <hours/days>; ignoring may cost the launch.
Recommendation: <accept | pause> because <which yellows are correlated
  and whether they reinforce each other>.
Completeness: A=10/10 (accept and log), B=10/10 (pause and fix)
Pros / cons:
A) Accept the weak pass, log and continue  (recommended if yellows are
  independent and low-correlation)
  ✅ Keeps timeline momentum; each yellow is documented for retro
  ✅ Avoids over-engineering against speculative risks
  ❌ Two correlated yellows can compound into a red post-ship
B) Pause and fix the top 1–2 yellows before continuing
  ✅ Eliminates the highest-leverage caveats before they compound
  ✅ Avoids "we knew" retros where every yellow was actually a red
  ❌ Loses 1–3 days to fix; some yellows may not actually fire
Net: Weak pass is a real fork in the road. The recommendation depends on
  whether the yellows are independent (accept) or correlated (pause).
```

If `cws-autoplan` is the caller, this question is auto-decided by the 6
decision principles (boil-lakes biases toward "pause and fix" when ≥ 4
yellows; bias-to-action toward "accept" when ≤ 2 yellows are correlated).

## 3.2 If FAIL — block advancement

A `FAIL` verdict is a **mechanical block**. The challenge skill does not
update `gates_passed`, but the next-skill recommendation routes back to
the failing stage's skill, not forward.

`cws-autoplan` reads `verdict: fail` from the challenge log and refuses
to advance the pipeline until a re-challenge returns PASS or WEAK PASS.

The challenge log includes:
- Every red finding with its evidence and remediation.
- A single-paragraph `## Why FAIL` synthesis that picks the **most
  exploitable** red (the one with the highest blast radius) and explains
  why it dominates.

## 3.3 If PASS — clear advancement

A `PASS` verdict routes cleanly to the next stage. The log is still
written (audit trail), and any yellows are surfaced in the routing
footer as "watch items" for the next stage's retro.

---

# Phase 4 — write the challenge log

```bash
_TS=$(date +%Y-%m-%d)
_LOG="./.cws/challenges/${_TS}-${_STAGE}.md"
mkdir -p ./.cws/challenges 2>/dev/null
```

Write the log to `$_LOG`. Schema:

```markdown
---
stage: <idea | package | build | launch | promote | monetize>
date: <YYYY-MM-DD>
verdict: <PASS | WEAK PASS | FAIL>
artifact: ./.cws/0N-<stage>.md
challenger_session: $_SESSION_ID
red_count: <N>
yellow_count: <N>
info_count: <N>
drift_red_count: <N>
drift_yellow_count: <N>
---

## Verdict

<one paragraph — the headline finding, why it dominates. If a drift finding
dominates, lead with it — drift bugs invalidate downstream assumptions.>

## Findings

### Red

1. **<title>** — <one-line description>
   - Evidence: <link / quote / Semrush number / SHA / grep output>
   - Remediation: <what to change, where, with the specific value>

### Yellow

1. **<title>** — <one-line description>
   - Evidence: <...>
   - Remediation: <...>

### Info

1. **<title>** — <one-line note>

## Drift findings (Phase 2.5)

Cross-stage drift surfaced during the challenge. Each entry names the check
(2.5.1–2.5.7), the severity, the artifacts/surfaces compared, and the
remediation (usually `/cws-resync`).

### Drift Red

1. **<check name, e.g. "2.5.3 Permission drift">** — <description>
   - Compared: <state vs manifest vs dashboard>
   - Mismatch: <specific values>
   - Remediation: `/cws-resync` (or specific re-fetch / re-build action)

### Drift Yellow

1. **<check name>** — <description>
   - Compared: <...>
   - Remediation: <...>

### Drift Info

1. **<check name>** — <one-line note>

## Re-verify checklist

Before re-running this challenge, the operator should re-check:

- [ ] <item>
- [ ] <item>

## Why <verdict>

<one paragraph synthesizing why the verdict landed where it did>

## Learnings to log

If this challenge surfaced a generalizable lesson (not project-specific),
hand it to /cws-learn to add to learnings.jsonl with stage=<stage>.

- <lesson 1>
- <lesson 2>
```

After writing the file, append a state.json `history` entry (do **not**
update `gates_passed`):

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p=pathlib.Path('./.cws/state.json')
d=json.loads(p.read_text())
d.setdefault('history',[]).append({
  'ts': datetime.datetime.utcnow().isoformat()+'Z',
  'stage': 'cws-challenge',
  'event': 'challenge_run',
  'target_stage': '$_STAGE',
  'verdict': '<PASS|WEAK PASS|FAIL>',
  'log': '$_LOG'
})
d['last_updated'] = datetime.datetime.utcnow().isoformat()+'Z'
p.write_text(json.dumps(d, indent=2))
PY
```

Log a timeline event:

```bash
"$BIN/cws-timeline-log" "{\"skill\":\"cws-challenge\",\"event\":\"verdict\",\"stage\":\"$_STAGE\",\"verdict\":\"<PASS|WEAK PASS|FAIL>\",\"red\":<N>,\"yellow\":<N>}" 2>/dev/null
```

---

# Iron rules

- **FAIL blocks advancement.** The next skill routing is back to the
  failing stage's skill. `cws-autoplan` honors this mechanically.
- **WEAK PASS surfaces caveats but allows.** The user (or autoplan) must
  explicitly accept via D<N> before continuing.
- **PASS routes cleanly.** No second-guessing.
- **The challenge never updates `gates_passed`.** It only writes the log
  and the history entry. Gate management belongs to the stage skills.
- **Every red finding includes a concrete remediation** — exact file,
  exact change, exact value. Findings without remediations are
  observations, not findings; demote to info.
- **Don't repeat findings already in the prior artifact.** Only flag what
  is new, what was glossed over, or what has drifted since.
- **Pessimism is the prior.** A finding with weak evidence still flags
  yellow; a strong-evidence finding flags red. The bias is intentional.

---

# When NOT to use

- **The target stage has no artifact yet.** A `cws-package` challenge with
  no `./.cws/02a-listing.md` is nothing to attack. Route to the stage
  skill first.
- **The target stage is already shipped and unmodifiable.** Challenging a
  `launch` after the extension is live and `monetize_on: true` is a retro
  exercise, not a challenge. Route to `/cws-retro`.
- **Inside the first 24h of a stage change** when the artifact is still
  being edited. Wait for the artifact to stabilize (frontmatter `status:
  complete` is the signal).
- **As a casual sanity-check.** The challenge is heavy by design — it
  pulls Semrush again, reads the full artifact, walks the full checklist.
  For a quick "does this look right?" use the stage skill's own internal
  validation.

---

# Companion skills

- **`cws-careful`** — When the verdict is `FAIL`, `cws-careful` triggers a
  HARD gate before the next destructive action (submit, ad spend flip,
  monetize on). It reads the latest challenge log and refuses the action
  until a re-challenge returns PASS or WEAK PASS.
- **`cws-learn`** — When the challenge surfaces a generalizable lesson
  (not project-specific), hand the lesson list from the `## Learnings to
  log` section to `/cws-learn`. The next challenge run picks it up via
  `cws-learnings-search --stage <stage>` during Phase 1.2.
- **`cws-autoplan`** — Reads the verdict mechanically. `FAIL` blocks
  pipeline advancement; `WEAK PASS` surfaces the acceptance question at
  the final approval gate; `PASS` routes cleanly.
- **`cws-resync`** — If the challenge finds artifact ↔ state drift (e.g.
  the listing claims one keyword but `state.json.idea.name_keyword` says
  another), route to `/cws-resync` before re-challenging.

---

# Skill Routing Footer

The routing is **verdict-conditional**. Pick exactly one based on Phase 3.

## On PASS

The natural successor stage skill, per `../../shared/skill-routing.md`:

| Challenged stage | Next |
|---|---|
| `idea` | `/cws-package` (listing copy) and `/cws-build` (in parallel) |
| `package` | `/cws-launch` (assets + publish) once both package and build pass |
| `build` | `/cws-launch` once both package and build pass |
| `launch` | `/cws-launch` to submit-for-review |
| `promote` | `/cws-promote` to scale spend |
| `monetize` | `/cws-monetize` to flip monetize on |

Routing form:

```
Next: /cws-<skill>
Why: <one sentence — the stage cleared the challenge; what the next skill
  unlocks>.
```

## On WEAK PASS

Route to `/cws-learn` to record the caveats before the next stage skill:

```
Next: /cws-learn
Why: WEAK PASS surfaced <N> yellow findings. Log them as stage=<stage>
  learnings so the next challenge run catches recurrence early, then
  proceed to /cws-<successor>.
```

After `/cws-learn` returns, the operator runs the natural successor as
above.

## On FAIL

Route back to the failing stage's skill:

| Failing stage | Re-route |
|---|---|
| `idea` | `/cws-idea` step 1.2–1.4 (regenerate hypotheses) |
| `package` | `/cws-package` step <fix-section> |
| `build` | `/cws-build` step <fix-section> |
| `launch` | `/cws-launch` step <fix-section> |
| `promote` | `/cws-promote` step <fix-section> |
| `monetize` | `/cws-monetize` step <fix-section> |

Routing form:

```
Next: /cws-<failing-stage>
Why: FAIL on <most-exploitable red finding>. <One-line specific fix
  direction — what to change in the stage skill's flow>.
```

Never list two options. Never offer a menu. The verdict picks the route.
