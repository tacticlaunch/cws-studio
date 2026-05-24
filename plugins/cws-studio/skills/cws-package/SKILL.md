---
name: cws-package
description: >-
  Stage 2a of the CWS launch pipeline — write the listing copy that ranks. Sets
  the extension name, the 132-char short description, and the ~4,500-char full
  description, with the chosen name keyword saturated 8–10 times across the
  meta and the whole text cleared through the Turgenev anti-spam check
  (overall risk low/insignificant, no red repeats, name words top of word and
  phrase tabs). Use when the user wants to write or rewrite store listing copy,
  pick the final display name, optimize keyword saturation, run a Turgenev
  pass, sanity-check copy against competitors, or verify name-keyword
  saturation. Triggers on "write my extension description", "optimize my CWS
  listing", "check my listing for spam", "pick a name for my extension",
  "how long should my description be", "rewrite my store copy", or a pasted
  Turgenev report. Reads `./.cws/01-idea.md` for the chosen name keyword and
  the Main/Extra keyword set; writes `./.cws/02a-listing.md`. Hard prerequisite:
  `gates_passed` must include `idea` (and therefore `account-setup`). Leans on
  the Semrush MCP and Turgenev.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - WebFetch
  - WebSearch
  - AskUserQuestion
triggers:
  - write my extension description
  - optimize my CWS listing
  - check my listing for spam
  - pick a name for my extension
  - how long should my description be
  - rewrite my store copy
  - run turgenev on my listing
---

# cws-package — Stage 2a (listing copy)

You are the studio operator writing the **meta-information** of a Chrome Web
Store listing: `name`, `description` (short, 132 chars), and the long-form
listing body (~4,500 chars). Your single job in this stage is to ship copy
that **(a)** carries the Stage-1 name keyword 8–10 times across the meta
without tripping CWS moderation or Google's anti-spam pessimization, **(b)**
sits at the top of Turgenev's word and phrase frequency tables, and **(c)**
reads like a native-English-speaking human wrote it. Everything else (assets,
icon, screenshots, translations) belongs to cws-launch. Everything before
this (idea, keyword, donor) belongs to cws-idea.

Deliverable: `./.cws/02a-listing.md` with frontmatter `status: complete`, a
chosen name, short description, full description, the Turgenev verdict, a
name-occurrence audit table, and the Main vs Extra keyword tables. On gate
pass, `state.json.gates_passed` gains `"package"` and `state.json.package.*`
is populated.

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
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --stage package --limit 3
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "
import json
d=json.load(open('$_STATE_FILE'))
print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none')
idea=d.get('idea',{})
print('NAME_KEYWORD:', idea.get('name_keyword','-'))
print('US_VOLUME_EXACT:', idea.get('us_volume_exact','-'))
print('KD_ZONE:', idea.get('kd_zone','-'))
print('DONOR_URL:', idea.get('donor_url','-'))
pkg=d.get('package',{})
print('PACKAGE_PREV_NAME:', pkg.get('name','-'))
print('PACKAGE_TURGENEV_CLEAN:', pkg.get('turgenev_clean','-'))
"
else
  echo "CWS_STATE: missing"
fi
_IDEA_FILE="./.cws/01-idea.md"
if [ -f "$_IDEA_FILE" ]; then
  echo "IDEA_ARTIFACT: present"
else
  echo "IDEA_ARTIFACT: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-package\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

Branch off the echoed values:

- `CWS_STATE: missing` → stop. Route the user to `/cws-init` then re-enter.
- `GATES_PASSED` does **not** contain `idea` → stop. Route to `/cws-idea`. The
  name keyword, US-exact volume, and donor URL must be locked before any copy
  is written. Writing copy first and back-filling a keyword later is how
  studios produce listings that look fine and rank for nothing.
- `IDEA_ARTIFACT: missing` even though the `idea` gate is passed → read
  `state.json.idea` directly, but flag it: someone deleted the artifact and
  the Main/Extra keyword tables will need to be regenerated from Semrush
  before Phase 4.
- `LEARNINGS: <n> entries loaded` with stage-filtered hits → surface the 3
  printed lines verbatim before Phase 1's first decision. Past Turgenev
  fights and rejected names live here.
- `EXPLAIN_LEVEL: terse` → drop the glosses below; emit shorter prose around
  each `D<N>`.
- `PROACTIVE: false` → do not auto-route to the next skill at the end; ask.

## AskUserQuestion format

See `../../shared/askuserquestion-format.md`. Every interactive decision in this
skill is a `D<N>` brief: header, ELI10, stakes-if-wrong line, recommendation
with reason, completeness scores (or kind-note), pros/cons with at least 2 ✅
and 1 ❌ per option (each ≥40 chars), net synthesis. D-numbering starts at D1
per invocation.

## Voice

See `../../shared/voice.md`. Operator-to-operator. No banners. No "I'll now write
the…" preambles. Concrete numbers: chars, keyword counts, Turgenev scores,
percentages. Lead with the verdict; the reasoning follows.

## Skill routing footer

See `../../shared/skill-routing.md`. End with a single `Next: /cws-<skill>` line +
one-line `Why:`. Never a menu.

---

## Why this stage is its own gate

Stage 2 splits in two:

- **2a (this skill, `cws-package`)** — listing copy: name, short, full
  description, Turgenev.
- **2b (`cws-build`)** — the actual extension code, manifest, icons,
  permissions.

They run in parallel because copy and code don't depend on each other. But
both must gate before `cws-launch` can submit. If you arrived here via
`/cws-autoplan`, copy runs first because it forces the keyword sanity-check
one more time before the code burns hours implementing the wrong product.

## The iron rules — these are Mechanical, never asked

Apply silently. If a `D<N>` would be raised only to confirm one of these, do
not raise it. Log it to the audit trail (if cws-autoplan is driving) and
advance.

1. **Name keyword count: 8–10 occurrences across the meta.** Across the union
   of `name` + short description + full description. Below 8 = under-indexed,
   doesn't rank. Above 10 = overspam, Turgenev red, Google pessimization.
   When trimming to fit, cut Extra keywords first, then Main tail keywords;
   never cut the name below 8.
2. **Short description hard cap: 132 chars.** Aim 120–130. Extra symbols
   space the keywords apart and lower moderation trigger risk.
3. **Full description target length: ~4,500 chars (with spaces).** Range
   4,300–4,700. Below 4,300 the keyword density spikes; above 4,700 the
   absolute count of any keyword must climb to keep proportion and Turgenev
   reds bloom. The newer Turgenev counter shows non-space chars — always
   read the with-space number.
4. **Main = Semrush Broad Match results.** Including phrases where another
   word interrupts the name (`convert pages file to word` for name
   `convert pages to word`). Plus on-topic how-to question phrases.
5. **Extra = Semrush Related results.** Synonyms, swapped words, adjacent
   topics. Keyword-by-letter / by-article / by-word-form variants count as
   **separate** keywords — take both.
6. **Drop keywords with wrong SERP.** A Semrush keyword that returns a
   different product format in Google is poison — it muddles your behavioral
   signals. Click each candidate through; if top results are off-product,
   drop or use ≤1×.
7. **Lowercase ~50% of keyword occurrences in short + full.** All-caps every
   time slightly pessimizes; people search lowercase.
8. **Capitalize the `name` field with English title case.** Capitalize every
   content word. Lowercase only articles/prepositions/conjunctions. Acronyms
   uppercase. Native-speaker conversion lever — bad case kills trust.
9. **Banned anywhere in meta:** `best`, `recommended`, `premium`, `#1`. Hard
   CWS moderation block. No exceptions.
10. **`free` is rationed:** never in name, ≤1 in short, ≤2–3 in full. More
    than that and Google clusters you with the bargain audience; when you
    later monetize the behavioral signals collapse.
11. **No fake reviews in the description.** No "coming soon" features.
    Asking for a review in the last paragraph is fine; quoting fake reviews
    is a moderation flag.
12. **List items: ≤1 line each.** Multi-line items degrade the list to a
    paragraph in Google's parser and you lose the structured-content boost.
13. **List length: 3–6 items.** Two items isn't a list. Ten items is a wall.
14. **Vary list length BETWEEN lists, keep length consistent WITHIN a list.**
    Uniform inside one list = "structured content" signal. Varied across
    lists = "human wrote this" signal.
15. **One emoji per line, prefix only.** Trailing emojis read as decoration
    to Google's parser and risk a robotic-spam score. Within one list use
    the same lead-emoji; vary only across lists.
16. **Always a space between emoji and word.** Some parsers fail to
    tokenize otherwise.
17. **Headers above lists separated by exactly one blank line.** CWS strips
    everything except `\n` and `\n\n`. No tabs, no indent.
18. **Comma-chained keyword lists are the #1 moderation trigger.** Never
    `AI, Description, Generator, Tool`. Insert a period and start a new
    sentence.
19. **Per-paragraph density.** First two paragraphs: ≤3 occurrences of the
    same keyword. From the third paragraph onward: ≤2.
20. **Turgenev pass criteria:** overall pessimization risk = low or
    insignificant, repeats column shows zero red flags (purple counts as
    red), name words sit at the top of both the Words tab and the Phrases
    tab (counting service-marked words like `youtube`, `html`, `temp` by
    hand).
21. **Paste name + short + full together into Turgenev.** They are jointly
    indexed; running only the full description gives the wrong percentages.

These are the bootcamp's non-negotiables. Do not ask the user to vote on
them.

---

## Phase 0 — Read state and refuse to start without prerequisites

Already done in the preamble. Restate the verdict in one sentence so the
user sees it.

**If `gates_passed` lacks `account-setup`:** stop. Two things are wrong, not
one. The Stage 0 setup gate (proxy, antidetect profile, Google account)
governs every downstream account safety check. Route to `/cws-idea` (which
handles Stage 0).

**If `gates_passed` lacks `idea`:** stop. You have no name keyword. Route to
`/cws-idea`.

**If `gates_passed` already contains `package`:** the user is re-running.
Confirm intent with D1 (below). The artifact from the previous run is at
`./.cws/02a-listing.md`. Treat re-runs as a rewrite, not a fresh start —
keep what passed Turgenev, fix the parts that didn't.

### D1 — Confirm intent on re-entry

Only emit if `gates_passed` already contains `package`. Otherwise skip.

```
D1 — Are we rewriting an already-gated listing?
Project/branch/task: $SLUG on $_BRANCH — package gate previously passed.
ELI10: The listing copy for this extension already cleared Turgenev and we
recorded the verdict. If we rewrite now and the extension is live, Google
will re-index and may shuffle your ranking. If it's not live yet, rewriting
is cheap. The right answer depends on whether the extension is in the
Chrome Web Store already.
Stakes if we pick wrong: a needless rewrite on a live listing nukes the
current ranking and forces a 2–6 week reconvergence on the new copy. A
needed rewrite skipped means we ship a known-bad listing.
Recommendation: A because the package gate was passed but the user invoked
cws-package again — they have a concrete reason to rewrite.
Completeness: A=8/10 (rewrite path), B=6/10 (re-validate only)
Pros / cons:
A) Rewrite full copy (recommended)
  ✅ Lets us apply new keyword research or fix a Turgenev regression
  ✅ Re-locks the gate cleanly with a fresh artifact
  ❌ If the extension is live, Google re-indexes and ranking briefly drops
B) Re-validate only (run Turgenev on current copy, no rewrite)
  ✅ Zero risk to a live ranking
  ✅ Catches a regression in Turgenev's algorithm side
  ❌ Misses any copy issue the operator may have noticed manually
Net: rewrite if pre-launch, re-validate only if live and the user did not
flag a specific problem.
```

If the user picks B, jump to Phase 5 (Turgenev) on the existing artifact.
If A, continue to Phase 1.

---

## Phase 1 — Confirm the name keyword

The name keyword was chosen in cws-idea and lives in
`state.json.idea.name_keyword`. Phase 1 is a 30-second sanity check, not a
re-pick. If the keyword visibly looks wrong on read-in, surface D2 below.
Otherwise emit one line ("Name keyword: `<keyword>` — locked from Stage 1.
Carrying forward.") and continue.

### Reasons the keyword can look wrong on read-in

- It contains a banned token (`free`, `best`, `premium`, `#1`).
- It's three or more words. Three-word names ship only after the extension
  has crossed ~10K users; mid-launch they split weight and rank for nothing.
- US-exact volume is < 200 and the donor isn't a clean long-tail play.
- The keyword has shifted product meaning since Stage 1 (rare — happens if
  the donor changed).
- It's a brand or trademarked-looking compound (two ordinary English words
  with no natural meaning together — e.g. "Content Keeper" — that a native
  speaker can't immediately decode as a product).

### D2 — Override the locked name keyword?

Only emit if one of the above flags fires. Otherwise skip.

```
D2 — Override the locked name keyword?
Project/branch/task: $SLUG on $_BRANCH — Stage-1 keyword <X> looks <reason>.
ELI10: We picked the name keyword last stage. Looking at it again before we
write the listing, it has a problem: <name the flag>. We can either push
ahead and write the listing around it anyway, or back to Stage 1, regenerate
candidates, and pick a clean replacement. The full listing is 4–6 hours of
work — better to spend an extra 30 minutes on the keyword.
Stakes if we pick wrong: ship copy around a flagged keyword and you either
trip CWS moderation (banned token) or rank for nothing (low volume, wrong
form factor). Either case = relaunch under a new name later, which means a
new extension ID and zero install carry-over.
Recommendation: B because <reason> is one of the keyword-killer flags from
the bootcamp.
Completeness: A=4/10, B=9/10
Pros / cons:
A) Use the locked keyword anyway
  ✅ Saves the 30 minutes of regeneration
  ✅ Keeps the donor / build plan aligned with Stage 1
  ❌ Locks in the flagged problem — re-emerges in moderation or ranking
B) Back to /cws-idea, regenerate name candidates (recommended)
  ✅ Clean keyword before any copy is written
  ✅ Stage 1's scoring rubric catches edge cases this skill won't
  ❌ Adds 30–60 minutes; small chance the rerun picks the same keyword
Net: every hour spent on Stage-1 keyword fixes saves a week of Stage-3
ranking work.
```

If B: stop. Route to `/cws-idea` with the flag reason. Do not write any
copy.

If A: continue, but record the override in the artifact ("Override accepted:
Stage-1 flag X; user decision.") so the retro stage can revisit.

---

## Phase 2 — Generate candidate display names

The name keyword and the display name are different objects. The **keyword**
is what Google sees in the indexed name field. The **display name** is what
the user reads in the store. They overlap: the display name *contains* the
keyword, in proper English title case, and usually one or two extra words
that humanize it.

Rules for the display name:

- Contains the name keyword as a whole phrase, exactly once.
- English title case applied (Capitalize Every Content Word). Lowercase only
  articles, prepositions, conjunctions. Acronyms uppercase (`PDF`, `SMS`,
  `BPM`).
- ≤ 75 characters total (manifest cap).
- Includes at most one extra "humanizing" word (`Tool`, `Manager`, `Pro`,
  `App`, `Studio`, `Maker`, `Finder`). Two-word keyword + one humanizer is
  the bootcamp's preferred shape (`Color Code Picker Tool`).
- No `best`, `recommended`, `premium`, `free`, `#1`.
- No brand of a competitor.
- Optional: mix two popular queries (`Free and Fair Adblocker`) only in
  low-competition niches and non-English markets, and only if a native
  speaker reads it cleanly.

Generate **3–5 candidate display names**. Score each against:

1. Reads cleanly to a native speaker (yes/no).
2. Carries the exact keyword as a contiguous phrase (yes/no — required).
3. Character count (target 25–55).
4. Title case applied correctly (yes/no — required).
5. Avoids banned tokens (yes/no — required).

Drop any candidate that fails (2), (4), or (5). Score the rest.

### D3 — Pick the display name

If exactly one candidate passes the hard requirements, do not emit D3. Just
say "Display name: `<X>` — only candidate that cleared the hard requirements"
and carry forward.

If two or more candidates pass:

```
D3 — Which display name to ship?
Project/branch/task: $SLUG on $_BRANCH — display name carries keyword <K>.
ELI10: The display name is the human-readable headline of the store
listing. It must include the name keyword as one whole phrase, in proper
English title case, and read clean to a native speaker. We have <N>
candidates that meet the hard rules. Between them, the difference is one
extra word (or none) and how the name reads aloud. Try saying each aloud —
the one that sounds least like marketing copy usually wins.
Stakes if we pick wrong: a stiff or marketing-tinged display name reduces
click-through from the search results, which silently caps your install
ceiling. Title-case errors also leak into screenshot copy and the support
landing page later.
Recommendation: <A/B/C> because it reads most naturally and uses the
keyword as a contiguous phrase without padding.
Completeness: A=9/10, B=8/10, C=7/10
Pros / cons:
A) "<candidate A>" (recommended)
  ✅ Keyword sits in the middle of the name — humans don't read it as SEO
  ✅ <other concrete pro, ≥40 chars>
  ❌ <honest con, ≥40 chars>
B) "<candidate B>"
  ✅ <pro>
  ✅ <pro>
  ❌ <con>
C) "<candidate C>"
  ✅ <pro>
  ❌ <con>
Net: native-speaker readability wins ties.
```

Once the user picks, **lock the display name**. Every keyword count below
counts the keyword inside the display name as the first occurrence.

---

## Phase 3 — Write the short description (132 chars)

The short description is the second line a CWS visitor reads. Google indexes
it. Its job: carry the name keyword **3 times** (in mixed case forms) and
two other Main keywords once or twice each, padded to ~120–130 chars with
ordinary connective words.

### Construction rules (Mechanical, applied silently)

- The single most important word of the name keyword: 3×. Any other word:
  ≤2×. If two different words both hit 3×, reduce one to 2× — overspam
  trigger.
- A morphologically varied third hit reads cleaner than three identical
  hits. `Summarize / Summarizer / Summarized` lands ~2.5× to moderation
  rather than 3, and saves overspam risk.
- Two main-keyword phrases adjacent to each other (no separator words)
  is a high-risk moderation trigger. Push them apart with intermediate
  words.
- Never comma-chain keywords. Period and a new sentence.
- One sentence is too dense. Two sentences is the safe shape.
- Lowercase the keyword in at least one of its three occurrences.

### Draft → count → tighten

Draft a candidate. Count name-keyword occurrences. Count other Main keyword
occurrences. Check char length. Tighten.

Output goes to the artifact as one literal block (no quotes around it).

Example shape (do not copy verbatim — derive from `state.json.idea`):

```
<DisplayName>: <one-sentence value prop using main keyword in lowercase>.
<Second sentence with a tail variation of the keyword> and <Extra keyword>.
```

131 chars target. Verify with `wc -m`.

### D4 — Short description draft check

Only emit if the first draft fails a hard rule (over 132 chars, contains a
banned token, comma-chains keywords, or has two adjacent keyword phrases
with no separator). If the draft cleared all rules: skip D4, show the
candidate to the user as a one-line "Short description: `<text>` — 128
chars, name keyword ×3, no flags." and continue.

```
D4 — Short description: keep this draft or rewrite?
Project/branch/task: $SLUG on $_BRANCH — first draft is <X> chars and trips
<flag>.
ELI10: Our first attempt at the 132-char short description triggered a
specific moderation rule. We can either rewrite to clear it, or keep
because the trigger is borderline. Borderline triggers (e.g. 133 chars,
4× name keyword but one is morphologically varied) sometimes pass CWS
moderation but cap how aggressively Google ranks the listing. Almost
always the right call is to rewrite — 132 chars is plenty of room.
Stakes if we pick wrong: a borderline short description that passes
moderation but caps ranking is the worst outcome — you can't see it,
you just don't rank.
Recommendation: A because the rule trips are fixable in one rewrite pass.
Completeness: A=9/10, B=5/10
Pros / cons:
A) Rewrite to clear the flag (recommended)
  ✅ Clean Turgenev pass in Phase 5 without further iteration
  ✅ No ranking ceiling from a borderline trigger
  ❌ Adds 5 minutes of rewriting
B) Keep the borderline draft
  ✅ Saves 5 minutes now
  ❌ Caps ranking invisibly; harder to diagnose later
Net: never ship borderline meta — fix it now.
```

---

## Phase 4 — Write the full description (~4,500 chars)

This is the meat of the stage. It carries 5–7 of the name keyword's 8–10
total occurrences, 15–20 Main keyword occurrences (across ~10–15 distinct
Main phrases), 15–20 Extra keyword occurrences (across ~10–15 distinct
Extra phrases), and reads as a structured human-written page.

### 4.1 Assemble the Main / Extra keyword tables

If the cws-idea artifact has them, read them in. Otherwise fetch from
Semrush MCP (`keyword_research`) for the locked name keyword. Use the
**Broad Match** tab for Main and the **Related** tab for Extra.

Filter rules:

- Drop any keyword whose top Google SERP is the wrong product format. Open
  each candidate's SERP via WebFetch and confirm at least 3 of the top 5
  results match your product type (browser extension or web tool, not
  desktop app or mobile-only).
- Drop any keyword that refers to a different product even if it shares
  words (e.g. `pdf pages` when your product is `pages file to word`).
- Keep separate variants that differ by one letter, by article, by word
  form (`youtube to text`, `youtube to texts`, `youtube-to-text`) — they
  count as distinct keywords.
- Keep ≥1 keyword that **nests** the name keyword (e.g.
  `text to speech reader app` nests `text to speech` and contributes to
  both the Main count and the name count).
- Acronym niches: capitalized and non-capitalized forms count as separate
  keywords (`SMSChecker` vs `SMS Checker`). Take both.

Target table size: 15 Main rows, 15 Extra rows. The full description will
not use all 30 — Phase 5 trims from the bottom.

### D5 — Main / Extra split looks off?

Only emit if the assembled tables fail one of these:

- Fewer than 8 Main rows total (will fail to hit 15–20 Main occurrences).
- Fewer than 5 Extra rows total (text will sound monotone).
- More than 5 SERP-rejected candidates (likely the niche has Semrush noise
  and a manual broaden pass is needed).

If the tables are clean: skip D5 and continue.

```
D5 — Keyword tables are under-stocked — broaden or push through?
Project/branch/task: $SLUG on $_BRANCH — Main has <N> rows, Extra has <M>.
ELI10: To fill ~4,500 chars with the right keyword density, we need about
15 Main and 15 Extra keyword phrases. Right now we have fewer. We can
either pull from Semrush's Phrase Match + Exact Match tabs (broader, more
noisy keywords), or push through with what we have and let the name
keyword absorb the spare occurrence budget. Broadening is usually right
when Main is thin; pushing through is right when Extra is thin and the
niche is naturally narrow.
Stakes if we pick wrong: ship a description with too few keyword anchors
and Turgenev shows artificial repetition; ship with too many noisy
keywords and the SERP-mismatch rule drops your behavioral signals once
visitors land.
Recommendation: A because the keyword set drives the entire structure
of the description.
Completeness: A=9/10, B=6/10
Pros / cons:
A) Broaden via Phrase + Exact Match tabs (recommended)
  ✅ Recovers nesting keywords that Broad Match missed
  ✅ Lets Phase 5 trim from the bottom without going below the target
  ❌ Adds 15 minutes of Semrush + SERP verification
B) Push through with current tables
  ✅ Faster; preserves momentum
  ❌ Phase 5 may need to invent name occurrences to hit 8–10
Net: broaden if the niche has room; push through only for genuinely
narrow niches.
```

### 4.2 Generate the body

Use ChatGPT (or in-skill drafting) with this prompt as the base. Edit by
hand after — generators swallow keywords, drop list items, and add em
dashes that you will need to strip.

```
Work as a professional SEO specialist. Write a description for a Google
Chrome extension: about 4,500 characters, 10–16 paragraphs. Sometimes use
emojis, but not more than one per line. Don't use quotation marks. Use
lists at least 5 times, for example: 1, 2, 3 and 1️⃣, 2️⃣, 3️⃣ and -, ➤,
▸, •. Separate paragraphs with blank lines. Use the following keywords
exactly as written and as often as possible.

Main keywords:
<one per line, ~15>

Extra keywords:
<one per line, ~15>

Name keyword (must appear 5–7 times in this text alone, as a contiguous
phrase): <keyword>
```

Generate the draft 2–3 times. Cherry-pick the best paragraphs from each
generation. Assemble manually.

### 4.3 Required structural elements

The description below must include all of:

- **Emoji-marked H1-style header** on the first line (one emoji + the
  display name + a 4–6 word value prop).
- **3–6 lists** of mixed types: at least one numbered list (`1.` or
  `1️⃣`), at least one bullet list (`➤`, `▸`, or `•`), at least one
  emoji-marker list (`💡`, `📌`, `🔹`, `◆`). Each list 3–6 items, items
  ≤1 line, length consistent within a list.
- **FAQ block** near the end — 3–5 question/answer pairs. Each question
  starts with an emoji marker (`❓`, `🔒`, `💸`, `🧐`); each answer starts
  with a different emoji marker (`🔹`, `💡`). FAQ blocks absorb long-tail
  question keywords cleanly.
- **Closing paragraph** with a polite review nudge ("If <name> helped, a
  short rating in the store helps other people find it."). Never quote
  reviews. Never write fake reviews.
- **Alternation:** never >3 paragraphs in a row, never >2 lists in a row.
- **Above-the-fold weighting:** the first ~600 chars (visible before CWS
  "Read more") carry 1–2 extra name-keyword occurrences and ≥1 list.

### 4.4 Count occurrences mechanically

After assembly, count:

- Name keyword: exact-form occurrences only (case-insensitive). Must land
  in 5–7. Plus the 1 in the display name and 3 in short = 9–11 total
  meta. Aim for total 8–10. If total is 11, drop one full-description
  occurrence. If 7, add one in the second paragraph above the fold.
- Each Main keyword: 1–3 occurrences. Total Main occurrences: 15–20.
- Each Extra keyword: 1–2 occurrences. Total Extra: 15–20.

When counting a keyword's uses, also count it inside longer keywords:
`incognito mode` counts inside `chrome incognito mode`.

Per-paragraph density: first two paragraphs ≤3 of any one keyword, after
that ≤2.

Output a counting table into the working notes:

```
| Keyword | Form | Display | Short | Full | Total | Cap |
|---|---|---|---|---|---|---|
| <name-keyword>             | exact   | 1 | 3 | 6  | 10 | 8–10 |
| <name-keyword>             | varied  | 0 | 0 | 2  | 2  | flex |
| <Main #1>                  | exact   | 0 | 1 | 2  | 3  | ≤3   |
| ...                        | ...     |   |   |    |    |      |
```

### 4.5 Hand-edit pass

The generator output has predictable problems. Fix all of them:

- Strip em dashes. Replace with periods or commas.
- Strip "delve", "robust", "comprehensive", "nuanced", "multifaceted",
  "furthermore", "pivotal", "landscape", "tapestry", "underscore",
  "foster", "showcase", "intricate", "vibrant", "fundamental",
  "significant". Replace with concrete verbs/nouns.
- Strip every comma-chained keyword list. Re-cast as two sentences.
- Strip trailing emojis from list items (emoji prefix only).
- Verify list items are ≤1 line each. Re-wrap or split if any exceed.
- Verify the same emoji marker is used within each list. Vary only
  between lists.
- Verify space between every emoji and the next character.
- Verify lowercase occurrences of the name keyword in roughly half of
  the full-description uses.
- Verify headers above lists separated by exactly one blank line.

### D6 — Description draft has unresolved structural issues

Only emit if after the hand-edit pass the draft still has one of:

- Char count outside 4,300–4,700.
- Name keyword total outside 8–10.
- A list still has items > 1 line.
- Any paragraph still has >3 of one keyword (first two paragraphs) or >2
  (after).
- Comma-chained keyword list still present.

```
D6 — Draft has unresolved structural issues — fix now or accept risk?
Project/branch/task: $SLUG on $_BRANCH — draft is <X> chars, name
keyword <Y> total, with <list of unresolved issues>.
ELI10: The draft is close to shippable but still has structural problems
that the bootcamp flags as moderation-rejection or Turgenev-overspam
risks. We can either fix each one (one more 15-minute editing pass) or
accept the borderline shape and let Turgenev verdict (Phase 5) drive a
forced rework. Almost always: fix now. Turgenev rework usually surfaces
the same issues but takes longer because you've already paste-counted.
Stakes if we pick wrong: accept now → Phase 5 fails → forced rework =
30+ minutes vs 15. Or it passes Phase 5 but moderation flags it = 3-day
turnaround on a resubmit.
Recommendation: A.
Completeness: A=9/10, B=4/10
Pros / cons:
A) One more editing pass to clear each issue (recommended)
  ✅ Phase 5 is more likely to clear cleanly
  ✅ Moderation risk drops to baseline
  ❌ Adds 15 minutes
B) Accept the draft, run Phase 5 as-is
  ✅ Saves the editing pass if Turgenev surprises us
  ❌ Almost always forces a longer rework loop
Net: pay 15 minutes now to avoid 30+ minutes later.
```

---

## Phase 5 — Turgenev anti-spam check

URL: `https://turgenev.ashmanov.com/`. Free account needed. Paste **name +
short description + full description as one text** (in that order, with one
blank line between each).

### Read these columns; ignore everything else

- **Overall pessimization risk** (left sidebar, "общий риск пессимизации"):
  must read **insignificant** or **low**. This is the headline pass/fail.
- **Repeats column** ("повторы"): must show zero red flags. Purple counts
  as red.
- **Words tab**: the most-frequent words. The individual words of your
  name keyword must appear in the top, above the noise floor. Turgenev
  silently treats some real words as "service words" (`youtube`, `html`,
  `temp`) and grays them out — hand-count those, they still need to be
  top.
- **Phrases tab**: the most-frequent 2-word and 3-word phrases. The name
  keyword as a phrase must be at the top of its bucket. Turgenev compares
  only within the same word-count bucket; 3-word phrases don't compete
  with 2-word phrases.

### Ignore

- Academic nausea (тошнота). Site metric, not relevant to extensions.
- Word-combination nausea. Same.
- Linkbuilding. Not relevant.

### Score interpretation

| Repeats red count | Overall risk | Verdict |
|---|---|---|
| 0 | insignificant or low | **Pass.** Lock the gate. |
| 0 | medium | **Borderline.** Try one density trim — drop the lowest-count Extra keywords first. Re-run. |
| 1–2 | low | **Borderline.** Re-do paragraphs containing the red word; cut keyword count in those paragraphs to 1. |
| 1–2 | medium or high | **Fail.** Major rework. Drop bottom 3 Extra keywords; cut occurrences of the worst-offender Main keyword from 3→2. |
| ≥3 | any | **Fail.** Drop bottom 5 Extra keywords; cut all Main keyword counts to ≤2 per phrase; consider lengthening text toward 4,700 (more chars = lower per-word %). |

### D7 — Turgenev result is borderline

Only emit on a borderline result (one row above) — not on a pass, not on a
hard fail. A hard fail does not get a brief; just rework silently.

```
D7 — Turgenev borderline (<repeats=X, risk=Y>) — trim or accept?
Project/branch/task: $SLUG on $_BRANCH — first Turgenev pass came back
borderline (<exact numbers>).
ELI10: Turgenev's verdict is in the gray zone — not a clean pass, not a
clear fail. We can either run one more density trim (cut the
lowest-count Extra keywords and re-run) or accept the borderline result.
Google's pessimization signal is probabilistic; borderline copy
sometimes ranks fine, sometimes silently loses 20–30% of its ceiling.
The cost of one more trim is 10 minutes.
Stakes if we pick wrong: accept borderline → invisible ranking cap. Trim
unnecessarily → drop two unused Extra keywords you didn't need anyway.
Asymmetric: trim is almost always free.
Recommendation: A.
Completeness: A=9/10, B=5/10
Pros / cons:
A) One density trim and re-run (recommended)
  ✅ Almost always converts borderline to clean pass
  ✅ Drops only the lowest-value Extra keywords (no ranking impact)
  ❌ Adds one Turgenev iteration (~10 minutes)
B) Accept the borderline result
  ✅ Saves the iteration
  ❌ Caps Google ranking invisibly
  ❌ Future retros can't easily distinguish "ranking is slow" from
     "ranking is capped"
Net: trim now; the cost of trimming is zero, the cost of not trimming
is invisible-and-unfixable later.
```

If A: trim, re-run Turgenev, re-evaluate against the same table. Loop until
verdict is clean pass.

### After a clean pass

Record:

- Repeats red count: 0
- Overall pessimization risk: low / insignificant (exact word from
  Turgenev)
- Name keyword position in Words tab: 1st / 2nd / 3rd (must be top)
- Name keyword position in Phrases tab (for its word-count bucket): 1st /
  2nd / 3rd (must be top)
- Purple words flagged: none

---

## Phase 6 — Write the artifact and update state

### 6.1 Write `./.cws/02a-listing.md`

Use this exact structure. Every section is required.

```markdown
---
stage: cws-package
status: complete
created: <ISO8601>
updated: <ISO8601>
slug: <SLUG>
branch: <_BRANCH>
---

# Listing copy

## Chosen name

- Display name: `<exact display name as it goes into manifest.json name>`
- Name keyword (locked from Stage 1): `<keyword>`
- Char count: <N>
- Title case verified: yes

## Short description

```
<exact 132-char-cap short description, one literal block>
```

- Char count: <N>
- Name-keyword occurrences: <count>
- Other Main keywords used: <list>

## Full description

```
<full ~4,500-char description, exact text, ready to paste into CWS>
```

- Char count (with spaces): <N>
- Paragraph count: <N>
- List count: <N> (numbered: <a>, bullet: <b>, emoji: <c>)
- FAQ block present: yes
- Above-the-fold (first ~600 chars) carries: <list count> + <name
  occurrences in that window>

## Name-keyword occurrence audit

| # | Location | Form | Context (5 words) |
|---|---|---|---|
| 1 | display name           | exact       | "<snippet>" |
| 2 | short, sentence 1      | lowercase   | "<snippet>" |
| 3 | short, sentence 2      | exact       | "<snippet>" |
| 4 | short, sentence 2 tail | varied form | "<snippet>" |
| 5 | full, para 1           | exact       | "<snippet>" |
| 6 | full, para 2           | lowercase   | "<snippet>" |
| 7 | full, para 4 (above fold) | exact    | "<snippet>" |
| 8 | full, list block       | lowercase   | "<snippet>" |
| 9 | full, FAQ              | exact       | "<snippet>" |

Total: 9 (target 8–10)

## Main keyword table

| Keyword | Source | Display | Short | Full | Total |
|---|---|---|---|---|---|
| <main #1> | Broad Match | 1 | 1 | 2 | 4 |
| <main #2> | Broad Match | 0 | 0 | 3 | 3 |
| ... | ... | ... | ... | ... | ... |

Total Main occurrences: <sum>
Target: 15–20

## Extra keyword table

| Keyword | Source | Full | Total |
|---|---|---|---|
| <extra #1> | Related | 2 | 2 |
| <extra #2> | Related | 1 | 1 |
| ... | ... | ... | ... |

Total Extra occurrences: <sum>
Target: 15–20

## SERP-rejected keywords

Keywords that Semrush returned but were dropped because their top Google
SERP did not match the product format.

- `<keyword>` — top SERP returned <product type> instead of <our format>.
- ...

## Turgenev verdict

- URL submitted: name + short + full as one text.
- Repeats red flag count: 0
- Overall pessimization risk: <insignificant | low>
- Words tab top entry: `<name word>` (rank 1)
- Phrases tab top entry (2-word bucket): `<name 2-word phrase>` (rank 1)
- Purple words flagged: none
- Iterations needed: <N>
- Pasted Turgenev output (textual excerpt below):

```
<paste the repeats column, the words tab top 10, the phrases tab top 10>
```

## Notes for cws-launch

- Translations targets (rough): name + short + full to all 30+ CWS
  supported locales. Use Localizer or equivalent for the bulk pass; hand-
  translate the locales matching Tier-1 traffic (US/UK/CA/AU/DE/FR English
  + DE/FR/ES/IT/PT/JA/KO).
- Within each manual locale, the name keyword still needs to land 8–10
  times in the local-language equivalent. Localizer-grade machine
  translation does not preserve the count — hand-tune.
- Above-the-fold weighting carries through translations; verify each
  manual locale's first ~600 chars still leads with a list and ≥1 name
  occurrence.

## Notes for cws-challenge

If cws-challenge is run after this stage, the highest-leverage attacks:

- Can a competitor cluster against your description and steal traffic on
  the name keyword?
- Does the SERP for the name keyword now show another extension already
  using 4+ of your Main keywords? If so, your description anchors are
  not differentiating.
- Has the donor / competitor been updated since Stage 1, and does their
  new copy structure beat yours on length / list count / FAQ depth?
```

### 6.2 Update `./.cws/state.json`

```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p = pathlib.Path('./.cws/state.json')
d = json.loads(p.read_text())
pkg = d.setdefault('package', {})
pkg['name'] = '<display name>'
pkg['name_keyword'] = '<keyword>'  # mirror from idea for cross-skill reads
pkg['short_desc'] = '<short description text>'
pkg['short_desc_chars'] = <N>
pkg['full_desc_chars'] = <N>
pkg['name_occurrences_total'] = <8..10>
pkg['main_keyword_occurrences_total'] = <N>
pkg['extra_keyword_occurrences_total'] = <N>
pkg['turgenev_clean'] = True
pkg['turgenev_risk'] = '<insignificant|low>'
pkg['turgenev_repeats_red'] = 0
pkg['turgenev_iterations'] = <N>
gp = d.setdefault('gates_passed', [])
if 'package' not in gp:
    gp.append('package')
d.setdefault('history', []).append({
    'ts': datetime.datetime.utcnow().isoformat() + 'Z',
    'stage': 'cws-package',
    'event': 'gate_passed:package',
})
d['last_updated'] = datetime.datetime.utcnow().isoformat() + 'Z'
p.write_text(json.dumps(d, indent=2))
print('state.json updated; gates_passed=', d['gates_passed'])
PY
```

### 6.3 Timeline log

```bash
"$BIN/cws-timeline-log" "{\"skill\":\"cws-package\",\"event\":\"gate_passed\",\"name\":\"<display>\",\"keyword\":\"<keyword>\",\"name_occurrences\":<N>,\"turgenev_risk\":\"<insignificant|low>\"}" 2>/dev/null
```

---

## Stage exit summary (printed at the end)

```
PACKAGE COMPLETE for <SLUG> (<_BRANCH>)
Display name:         <name>            (<chars> chars, title-cased)
Short description:    <chars> chars     (name keyword ×<count>)
Full description:     <chars> chars     (name keyword ×<count>)
Total name occurrences across meta: <8..10>
Main keyword phrases:  <N> distinct, <total> occurrences
Extra keyword phrases: <N> distinct, <total> occurrences
Turgenev:             repeats red=0   overall risk=<insignificant|low>   iterations=<N>
Artifact:             ./.cws/02a-listing.md
Gates passed:         <list>
```

---

## When NOT to use cws-package

This skill is for **first-time listing copy** and pre-launch rewrites.

If the extension is **already live** in the Chrome Web Store and the user
wants to rewrite the copy: stop. Route to **`/cws-resync`** instead.
cws-resync handles the re-index ranking-shuffle risk, the timing of when
to push a rewrite, and the A/B-style comparison against the old copy. A
naive rewrite on a live listing without that protocol can nuke 2–6 weeks
of ranking work in a single update.

If the user is asking to translate an already-gated listing to additional
locales: stop. That belongs to **`/cws-launch`** (which owns the 30+ locale
manual-and-machine translation pass).

If the user wants to stress-test the copy adversarially (e.g. "can a
competitor displace us on this keyword with a better-structured listing?"):
finish cws-package's gate first, then route to **`/cws-challenge`**.

---

## Companion skills

- **`/cws-challenge`** — stress-test the locked copy adversarially before
  submit. Asks: does the SERP still favor our angle, has a competitor's
  copy improved since Stage 1, are our Main keyword anchors still
  differentiating?
- **`/cws-careful`** — hard gate before any change to an already-live
  listing. Listing changes after launch trigger Google re-index; cws-careful
  forces an explicit decision and snapshots state for rollback.
- **`/cws-build`** — Stage 2b, the actual extension code. Runs in parallel
  with this skill; both gates required before cws-launch.
- **`/cws-learn`** — record bootcamp-novel lessons from this run. Surfaced
  via `cws-learnings-search --stage package` on the next invocation.
- **`/cws-resync`** — handles copy rewrites on already-live listings.
- **`/cws-retro`** — post-launch ranking baseline. Reads
  `package.name_occurrences_total` and `package.turgenev_risk` to validate
  that listing-side health matches ranking trajectory.

---

## Hard refusals (cws-package never auto-decides these)

- Banned tokens (`best`, `recommended`, `premium`, `#1`) in any meta
  field. If the user insists, route to `/cws-careful` to force an
  explicit override decision and snapshot state.
- Display name without the name keyword as a contiguous phrase. The
  whole stage is built around it.
- Shipping copy when `gates_passed` lacks `idea`. Hard route to
  `/cws-idea`.
- Turgenev result with ≥1 red repeat shipping as-is. The stage loops
  until the verdict is clean, no matter how many iterations.
- Description below 4,300 chars or above 4,700 chars on gate pass.
- Name-keyword count below 8 or above 10 on gate pass.

---

## Filesystem boundary

This skill writes only to:

- `./.cws/02a-listing.md`
- `./.cws/state.json` (mutating `package.*` and `gates_passed`)

It reads from:

- `./.cws/state.json` (`idea.*`, `gates_passed`, `package.*` for re-entry)
- `./.cws/01-idea.md`
- `$CWS_PROJECT_DIR/learnings.jsonl` (stage-filtered)
- `references/listing-copy.md`
- `references/listing-examples.md`

It does **not** touch `./extension/`, `./src/`, or any build output. Those
belong to cws-build.

---

## Skill routing footer

If `gates_passed` does **not** include `build`:

```
Next: /cws-build
Why: build runs in parallel with package; both gates required before
cws-launch can submit. Pop a second session and start now.
```

If `gates_passed` already includes `build`:

```
Next: /cws-launch
Why: package and build are both gated. Launch handles assets, the 30+
locale translation pass, and the CWS moderation submit.
```

If the user originally invoked this skill via `/cws-autoplan` and the run
was a Taste-buffered approval cycle, route per the autoplan transition
table (`../../shared/skill-routing.md`) instead.

Never list more than one Next: line.
