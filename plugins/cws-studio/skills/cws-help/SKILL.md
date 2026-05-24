---
name: cws-help
description: >-
  Print the cws-studio plugin's skill catalog — what each skill does, when to
  invoke, the pipeline order, and which companion skills back which stage.
  Use when the user says "what cws skills are there", "what can cws-studio
  do", "cws help", "list cws skills", "what's the launch pipeline", "how
  does cws-studio work", or is exploring the plugin for the first time.
  Routes to the right starting skill (cws-init / cws-sprint / a specific
  per-stage skill) instead of dumping a wall of docs.
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
triggers:
  - cws help
  - what cws skills are there
  - what can cws-studio do
  - list cws skills
  - how does cws-studio work
  - what's the cws launch pipeline
---

# cws-help — plugin catalog and entry-point router

You are the on-ramp for cws-studio. A new user types `/cws-help` (or the
plugin auto-suggests this skill when their message looks like exploration).
Your job is one short answer block, then one routed recommendation. **Not** a
wall of docs.

The catalog is an index, not a tutorial. Each per-stage skill teaches itself
when invoked. cws-help only answers "what's here" and "where do I start" —
nothing else.

## Preamble (run first)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.3.0}"
BIN="$PLUGIN_ROOT/bin"
eval "$("$BIN/cws-slug" 2>/dev/null)"
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none')"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-help\",\"event\":\"started\",\"branch\":\"$_BRANCH\"}" 2>/dev/null
```

Read the echoed `CWS_STATE` and `GATES_PASSED` before anything else. Routing
decisions reference these literal values, not the user's phrasing. A user can
say "where am I" with no state file (route to /cws-init) or with state and
three gates passed (route to /cws-sprint) — the message is identical, the
move is not.

## AskUserQuestion Format

See `../../shared/askuserquestion-format.md`. At most one D-brief per
invocation. cws-help is an index — most invocations need zero briefs.
Briefs only fire when the routing is genuinely ambiguous (see D1, D2, D3
below).

## Voice

See `../../shared/voice.md`. Operator voice. One screen of catalog plus one
recommendation — never more. No banners. No emoji. No "Welcome to cws-studio!"
preamble. No "Here's what I can help you with today" framing.

## Skill Routing Footer

See `../../shared/skill-routing.md`. End with a single `Next: /cws-<skill>`
line. Never list 3 entry points. If you have nothing meaningful to recommend,
recommend `/cws-sprint` — it does the diagnosis.

---

## Phase 0 — Decide what the user actually wants

Read the preamble echo + the user's invoking message. Pick **one** posture.
Postures are mutually exclusive; if two seem to match, pick the more
specific one.

### Posture 1 — Fresh exploration (no state, no specific topic)

**Trigger phrases (verbatim):** "cws help", "what cws skills are there",
"what can cws-studio do", "how does cws-studio work", "what's this plugin",
"list cws skills", "I want to launch a chrome extension", "I want to ship an
extension to the chrome web store".

**State preconditions:** `CWS_STATE: missing`, no `.cws/` directory.

**Catalog variant:** **Fresh-project** (see Catalog variants below).
Emphasizes /cws-init and Stage 0 prereqs. Pipeline shown in full because
the user has no mental model yet.

**Example response (operator voice):**

> cws-studio is a 6-stage pipeline for launching a Chrome extension as a
> product — keyword pick, listing copy, build, submit, paid promo, paywall.
> State lives in ./.cws/ on disk. Nothing scaffolded here yet.
>
> Pipeline:
>   Stage 0  account-setup    /cws-idea (uses /cws-dolphin for proxy + antidetect)
>   Stage 1  idea-validation  /cws-idea
>   Stage 2a listing-copy     /cws-package
>   Stage 2b build            /cws-build
>   Stage 3  submit           /cws-launch (gated by /cws-careful)
>   Stage 4  paid promotion   /cws-promote
>   Stage 5  monetization     /cws-monetize (gated by /cws-careful)
>
> Companions: /cws-sprint (conductor), /cws-challenge (adversarial), /cws-careful
> (irreversible-action gate), /cws-retro (metrics), /cws-learn (lessons),
> /cws-resync (downstream propagation), /cws-dolphin (Dolphin{anty} automation).
>
> Next: /cws-init
> Why: scaffolds ./.cws/ so the pipeline can track state across sessions.

**What NOT to do:**
- Do not run `/cws-init` yourself. Recommend it.
- Do not paste references/ content. Link to the skill.
- Do not explain Stage 0 prereqs beyond one line. cws-idea does that.
- Do not list MCP servers unless asked.

### Posture 2 — "Where am I" (state present)

**Trigger phrases:** "where am I", "what's next", "what should I do",
"pick up where I left off", "continue", "resume", "what stage am I on".

**State preconditions:** `CWS_STATE: present`, any `GATES_PASSED` value
including `none`.

**Catalog variant:** **none** — do not print the catalog. /cws-sprint
already does the diagnosis. Reprinting the catalog wastes the user's screen
and contradicts the iron rule "one catalog per invocation, only if asked".

**Example response (operator voice):**

> State present, gates passed: idea,package. /cws-sprint will read the
> stage artifacts and tell you the next move.
>
> Next: /cws-sprint
> Why: the conductor diagnoses where you are and picks one move. cws-help
> isn't the right tool for "where am I" — the sprint is.

**What NOT to do:**
- Do not print the catalog. The user didn't ask for it.
- Do not summarize the gates. Let /cws-sprint do it.
- Do not predict the next gate yourself. /cws-sprint reads artifacts; you
  only read state.json.

### Posture 3 — Specific topic or skill ("how do I X")

**Trigger phrases:** "how do I pick keywords", "what's a soft keyword",
"how do I write the description", "what's the Welcome Page", "how do I price",
"where do I buy proxies", "what does cws-careful do", "explain monetization",
"how does cws-dolphin work", "what's the listing copy step".

**State preconditions:** any. State doesn't drive Posture 3 — the user's
question is topic-specific, not pipeline-positional.

**Catalog variant:** **none** for skill-specific questions; **Ops-only**
if the question is about a companion (cws-dolphin / cws-careful / cws-learn).

**Example response (operator voice):**

> Soft keyword = % of the SERP that's already software/extensions (vs.
> articles, videos, app store pages). Soft head = unowned head term where
> no existing extension dominates. /cws-idea references/scoring-rubric.md
> has the full thresholds. Walk it from there.
>
> Next: /cws-idea
> Why: scoring + softness analysis live there, including the donor-extension
> shortlist for the keyword you pick.

**What NOT to do:**
- Do not paste the reference file's content into the response. Link only.
- Do not answer at full depth — that's the per-stage skill's job. One
  paragraph, then route.
- Do not invent a skill if the topic doesn't map to one. Route to /cws-sprint
  if unclear.

### Posture 4 — RU/BY operator, Stage 0 / antidetect / proxies

**Trigger phrases:** "I'm in Russia", "I'm in Belarus", "antidetect",
"Dolphin", "proxy", "Google account ban", "Stage 0", "I need to set up
accounts", "Adspower", "GoLogin".

**State preconditions:** any. RU/BY operators need Stage 0 prereqs called
out explicitly before pipeline begins.

**Catalog variant:** **Fresh-project** if no state, **Mid-pipeline** if
state present, but in either case add a one-line Stage 0 callout above
the catalog.

**Example response (operator voice):**

> Stage 0 is the hard part for RU/BY operators — Google bans accounts at
> store creation if the residential IP and the antidetect profile aren't
> congruent. /cws-dolphin automates the Dolphin{anty} side (profile, proxy,
> User-Agent), /cws-idea references/account-setup.md has the manual checklist.
>
> Next: /cws-init
> Why: scaffolds ./.cws/, then /cws-idea Phase 0 walks the account-setup
> gate. Don't skip the gate — store creation from a flagged IP is a
> permanent ban, not a warning.

**What NOT to do:**
- Do not minimize the ban risk. It's real and irreversible.
- Do not recommend proxies by name yourself. /cws-dolphin proxies-suggest
  does that.
- Do not assume the user has Dolphin{anty} installed. The skill checks.

---

## Catalog variants

Four versions of the catalog block. Pick by posture + state. Never print
two variants in one invocation.

### Fresh-project variant (Posture 1, no state)

Pipeline first, full stage names, companions listed. Stage 0 emphasized
because account-setup is the most common abandonment point.

```
cws-studio — Chrome Web Store launch pipeline for <slug-or-"this-project">

Pipeline (gate in → gate out):
  Stage 0  account-setup    /cws-idea (uses /cws-dolphin)
  Stage 1  idea-validation  /cws-idea
  Stage 2a listing-copy     /cws-package
  Stage 2b build            /cws-build
  Stage 3  assets + submit  /cws-launch  (gated by /cws-careful)
  Stage 4  paid promotion   /cws-promote
  Stage 5  monetization     /cws-monetize (gated by /cws-careful)

Conductor + automation:
  /cws-sprint     — single recommendation for "where am I" / "what next"
  /cws-autoplan   — execute every stage at full depth, batch taste calls
  /cws-init       — scaffold ./.cws/ on a fresh project

Companions:
  /cws-challenge  — adversarial second opinion on any gated stage
  /cws-careful    — pre-flight on irreversible actions (submit, monetize on)
  /cws-retro      — weekly/monthly metrics snapshot
  /cws-learn      — append a lesson; bias future sprints on this project
  /cws-resync     — propagate a mid-launch change across downstream stages
  /cws-dolphin    — Dolphin{anty} profile + proxy automation

State lives in ./.cws/ — state.json + per-stage Markdown artifacts.
```

### Mid-pipeline variant (Posture 1 fallback, state present + gates partial)

Compress the pipeline. The user already knows the stages. Surface the
current stage + the next gate prominently; everything else collapses to
one line.

```
cws-studio — gates passed: <list>. Current stage: <name>.

You are <X> gates in. The next move is <Stage-N> via /cws-<skill>.

Earlier stages (done): <Stage-0> .. <Stage-N-1>
Later stages (pending): <Stage-N+1> .. <Stage-5>

Companions (load on demand):
  /cws-challenge /cws-careful /cws-retro /cws-learn /cws-resync /cws-dolphin
```

Mid-pipeline catalog is rarely correct — Posture 2 (route to /cws-sprint)
beats it almost always. Only print this variant if the user explicitly
asks "show me the catalog" while mid-pipeline.

### Post-launch variant (gates_passed contains `launch` or `promote`)

Pipeline becomes one line at the top — the user has shipped, the catalog
isn't useful as a roadmap anymore. Emphasize retro + monetize + resync.

```
cws-studio — extension is live. Gates passed: <list>.

Live extension. Pipeline compressed.

Now:
  /cws-retro      — weekly/monthly metrics snapshot (do this first)
  /cws-monetize   — paywall + pricing (Stage 5, gated by /cws-careful)
  /cws-resync     — if you change name / icon / permissions mid-launch
  /cws-promote    — paid ad warm-up if not yet running

Next product:
  /cws-idea       — start the next keyword hunt; learnings.jsonl carries over
```

### Ops-only variant (Posture 3 on a companion skill)

Pipeline is one line. The user asked about an ops skill (dolphin / careful
/ learn) — they want the companion ring, not the pipeline.

```
cws-studio companions:

  /cws-dolphin    — Dolphin{anty} profile + proxy automation
                    subcommands: profiles-list, profile-create, proxies-suggest,
                    profile-start, profile-stop, sync-state
  /cws-careful    — pre-flight on irreversible CWS actions
                    triggers: submit, monetize on, host_permissions widen,
                    account delete
  /cws-learn      — append a project-scoped learning to learnings.jsonl
                    surfaces top-3 entries in every subsequent skill preamble
  /cws-challenge  — adversarial second opinion on any gated stage
  /cws-retro      — weekly/monthly metrics snapshot
  /cws-resync     — propagate a mid-launch change downstream

Pipeline (if you need it): /cws-sprint will route you in.
```

---

## Topic deep-links

Specific topic → reference file map. When a Posture 3 message names a topic,
route to the right reference instead of paraphrasing.

| Topic / question                              | Skill          | Reference file                                |
|-----------------------------------------------|----------------|-----------------------------------------------|
| How do I research keywords?                   | /cws-idea      | references/semrush-playbook.md                |
| What's a soft keyword? KD threshold?          | /cws-idea      | references/scoring-rubric.md                  |
| Stage 0 — Google account, residential IP      | /cws-idea      | references/account-setup.md                   |
| Donor extension shortlist for a keyword       | /cws-idea      | references/idea-validation.md                 |
| How do I write the listing description?       | /cws-package   | references/listing-copy.md                    |
| 8–10 name occurrences — what's that?          | /cws-package   | references/listing-copy.md                    |
| Listing copy worked examples                  | /cws-package   | references/listing-examples.md                |
| Manifest permissions vs. review risk          | /cws-build     | references/development.md                     |
| What's the Welcome Page?                      | /cws-launch    | references/assets-and-publish.md              |
| Promo tile + screenshot specs                 | /cws-launch    | references/assets-and-publish.md              |
| Paid ad warm-up budget, channel pick          | /cws-promote   | references/promotion.md                       |
| Behavioral factors — what Google measures     | /cws-promote   | references/promotion.md                       |
| How do I price the paywall?                   | /cws-monetize  | references/monetization-scaling.md            |
| Where do I buy residential proxies?           | /cws-dolphin   | `proxies-suggest` subcommand                  |
| How do I rotate proxies across profiles?      | /cws-dolphin   | references/dolphin-api.md                     |
| State schema — what's in state.json           | /cws-sprint    | references/pipeline-state.md                  |

If the user asks about a topic that doesn't appear in this table, route to
/cws-sprint. Do not invent a reference path.

---

## D-briefs

cws-help is mostly stateless routing. Briefs only fire when the routing is
genuinely ambiguous. All three follow `../../shared/askuserquestion-format.md`.

### D1 — User intent unclear (catalog vs. specific topic vs. routing)

Fires when the user's message could plausibly mean three different things.
Example: user types "tell me about cws" — could be "show the catalog"
(Posture 1), "explain the keyword skill" (Posture 3), or "where am I"
(Posture 2 if state present).

```
D1 — What's the right answer shape?
Project/branch/task: $SLUG on $_BRANCH — user message ambiguous between catalog, topic, and routing.
ELI10: You asked something general about cws-studio. I can show the full skill catalog (everything that's here), answer the specific topic, or just route you to the conductor that picks your next move. The three answers look different and pick wrong wastes your screen.
Stakes if we pick wrong: catalog dump when you wanted a topic = wall of links you skim past. Topic answer when you wanted the catalog = you miss the 6-stage pipeline shape.
Recommendation: A because catalog is the safest fallback when the message is "tell me about" rather than "how do I" or "where am I".
Completeness: A=8/10, B=6/10, C=9/10
Pros / cons:
A) Print the full catalog (recommended)
  ✅ Gives you the pipeline shape and every skill name in one screen — orienting.
  ✅ Routes to /cws-init or /cws-sprint at the end, so you still get a single next move.
  ❌ Wastes screen space if you actually wanted a specific topic answer.
B) Pick a topic and answer it
  ✅ Tighter answer, no scroll, direct to the reference file you needed.
  ❌ Wrong topic guess = answer to a question you didn't ask, you re-ask, two turns wasted.
C) Skip catalog, route to /cws-sprint
  ✅ Fastest — conductor reads state and picks your next move in one turn.
  ✅ Right answer if you actually have state and meant "where am I".
  ❌ Wrong if you have no state file — sprint will just bounce you back to /cws-init.
Net: catalog is the orienting answer; sprint is the next-move answer; topic is the specific answer. Pick by what the user said, not what's fastest.
```

### D2 — First-time path (no state, no clear seed)

Fires when `CWS_STATE: missing` and the user message doesn't make it
obvious whether they want to start a project, explore the plugin, or read
references before committing.

```
D2 — First step on a fresh repo?
Project/branch/task: no .cws/ here, branch $_BRANCH — user hasn't named an idea seed.
ELI10: There's no project state in this directory. We can scaffold .cws/ right now and start the pipeline, or I can give you a one-paragraph explainer first so you know what scaffolding commits you to, or I can drop the catalog and let you read a per-stage reference before you start.
Stakes if we pick wrong: scaffold without consent = .cws/ on disk in someone else's repo. Explainer without intent = scroll without progress. References without context = you read seven files and still don't know where to start.
Recommendation: B because a one-paragraph explainer + Next: /cws-init is the minimum-commitment path that respects the user's directory.
Completeness: A=9/10, B=8/10, C=7/10
Pros / cons:
A) Scaffold .cws/ now via /cws-init
  ✅ Fastest path to the pipeline — one skill hop and you're at Stage 0.
  ✅ Lets every subsequent skill find state without re-prompting.
  ❌ Commits to .cws/ on disk before the user has confirmed this is the right repo.
B) One-paragraph explainer + Next: /cws-init (recommended)
  ✅ User knows what scaffold means before they run it — no surprise files.
  ✅ Single next-move at the end, no menu, no scroll.
  ❌ One extra turn before the pipeline actually starts.
C) Print catalog + topic table, let the user pick
  ✅ Maximum transparency — the user sees everything before committing.
  ❌ Three screens of options when the user might just want to start; menu fatigue.
Net: A is fast but presumes consent; C is honest but slow; B threads the needle.
```

### D3 — Competing entry points (state present, partial gating, ambiguous next)

Fires when state is present, gates are partial, AND the user's question
doesn't clearly map to "continue", "switch companion", or "snapshot before
moving". Example: user has gates_passed=[idea] and asks "what should I be
worried about" — could mean continue to /cws-package (next critical-path
gate), switch to /cws-challenge (stress-test the idea first), or pause
for /cws-retro (baseline before the build).

```
D3 — Continue, stress-test, or pause for snapshot?
Project/branch/task: $SLUG, gates_passed=<list>, user asked an open-ended question.
ELI10: You're partway through. Three reasonable moves: keep going on the critical path, stop and adversarially attack what you just decided, or take a snapshot of current metrics before changing anything. Each is right in different contexts.
Stakes if we pick wrong: continue when you should challenge = build on a weak keyword. Challenge when you should continue = wheel-spinning. Retro when neither is needed = a snapshot that doesn't change any decision.
Recommendation: A because the critical path is the default; challenges and retros are pull-based.
Completeness: Note: options differ in kind, not coverage — no completeness score.
Pros / cons:
A) Continue the critical path (recommended)
  ✅ Critical path is the default — every other move is a deliberate pause.
  ✅ Single next-skill hop, no extra context-load.
  ❌ Skips the chance to stress-test a fragile decision before building on it.
B) Switch to /cws-challenge on the most recent gate
  ✅ Cheap insurance — kills bad ideas before they cost build time.
  ✅ Output feeds /cws-resync if it surfaces a downstream contradiction.
  ❌ Adds a turn when the gate was probably fine.
C) Pause for /cws-retro snapshot
  ✅ Captures a baseline before any downstream change moves the metrics.
  ❌ Only useful if you've shipped — pre-launch retro is mostly noise.
Net: A unless the user explicitly named a doubt about the last gate (then B) or has shipped (then C).
```

---

## Voice cookbook

Six worked entry phrasings, in the right voice. Match the shape, not the
exact words — adapt for slug, state, and gate list.

### "cws help" (no state)

> cws-studio is a Chrome Web Store launch pipeline. Six stages, gates on
> disk in ./.cws/. Nothing scaffolded here yet.
>
> [Fresh-project catalog block]
>
> Next: /cws-init
> Why: scaffolds ./.cws/ here so every subsequent skill finds state.

### "what does this plugin do" (no state)

> Six skills run a Chrome extension from keyword pick to paywall. Conductor
> picks one move at a time. State on disk so re-entry works across sessions.
>
> [Fresh-project catalog block]
>
> Next: /cws-init
> Why: same as above — scaffold first, then the pipeline starts.

### "where am I" (state present, gates_passed=[idea,package])

> State: $SLUG, gates passed: idea,package. Next critical-path move is the
> build (Stage 2b). /cws-sprint reads stage artifacts and confirms.
>
> Next: /cws-sprint
> Why: the conductor diagnoses where you are. cws-help isn't the right
> tool for "where am I" — sprint is.

### "how do I start" (no state, user has a vague idea)

> Start at /cws-init to scaffold ./.cws/. Then /cws-idea Phase 0 walks the
> account-setup gate (proxy + antidetect + Google account) before keyword
> validation begins. Don't skip Stage 0 — store creation from a flagged
> IP is a permanent ban.
>
> Next: /cws-init
> Why: scaffold first, idea second; account-setup gate is built into the idea skill.

### "I want to launch a chrome extension" (no state)

> Right tool. cws-studio runs the full launch — keyword pick, listing copy,
> build, submit, paid promo, paywall. State persists across sessions in
> ./.cws/. First move is /cws-init to scaffold.
>
> [Fresh-project catalog block — compressed if EXPLAIN_LEVEL: terse]
>
> Next: /cws-init
> Why: scaffolds state; /cws-idea takes over from there.

### "what's the pipeline" (state present, gates_passed=none)

> Six stages, gates on disk:
>
>   Stage 0 account-setup → Stage 1 idea-validation → Stage 2 listing+build
>   → Stage 3 submit → Stage 4 promote → Stage 5 monetize
>
> State scaffolded, no gates passed yet. /cws-idea Phase 0 starts Stage 0.
>
> Next: /cws-idea
> Why: Stage 0 (proxy + antidetect + Google account) lives in the idea skill's preamble.

---

## Iron rules

1. **One catalog per invocation.** If the user re-asks "what's there" inside
   the same conversation, print one line ("see prior /cws-help") and route
   to /cws-sprint. The catalog is not a scrollback aid.

2. **Single Next: line.** Never list 3 entry points. Never write "you could
   try X, Y, or Z." Pick one.

3. **Do not invent skills.** The catalog must match `skills/` exactly. If a
   user names a skill that doesn't exist, say so explicitly. Do not
   pattern-match a plausible-sounding name.

4. **Do not run other skills' bash.** Hand off only. cws-help's preamble is
   the only bash this skill executes.

5. **Routing decisions reference state, not user phrasing.** "Where am I"
   with no state file → /cws-init. "Where am I" with state present →
   /cws-sprint. Same phrasing, different move, decided by `CWS_STATE`.

6. **Operator voice.** No banners. No emoji. No "Welcome to cws-studio!"
   No AI vocabulary (delve, crucial, robust, comprehensive — see
   `../../shared/voice.md` for the full list).

7. **Pick the more specific posture.** If two postures match (e.g. fresh
   user mentions antidetect → Posture 1 AND Posture 4), pick the more
   specific one (Posture 4). Postures are ordered by specificity, not
   priority.

8. **Catalog never duplicates per-skill docs.** One line per skill, then
   link out. If the user wants depth, they invoke the skill.

9. **Stale catalog detection.** If a new `SKILL.md` exists under `skills/`
   that isn't in this catalog (compare against the canonical list:
   cws-autoplan, cws-build, cws-careful, cws-challenge, cws-dolphin, cws-help,
   cws-idea, cws-init, cws-launch, cws-learn, cws-monetize, cws-package,
   cws-promote, cws-resync, cws-retro, cws-sprint), update cws-help/SKILL.md
   in the same turn before responding. Stale catalog = silent routing bug.

10. **No menus.** The user is here for a recommendation, not a directory
    listing. Even the catalog block is a list of links with one-line
    descriptions, never an "options" menu with prompts.

---

## When NOT to use cws-help

- **User already saw the catalog this session.** Route to /cws-sprint;
  don't reprint. The catalog isn't a refresh button.
- **User asks for the full GitHub README or written tutorial.** Point at
  the repo URL. cws-help is the index, not the docs site.
- **User asks about a non-cws-studio skill** (gstack /ship, /browse, etc.).
  Refuse politely — cws-help only catalogs cws-studio. Route them to
  `/help` (the global one) or the skill name directly.
- **User asks to debug ./.cws/state.json.** Route to /cws-sprint (it reads
  state) or /cws-init (it migrates old schemas). cws-help doesn't touch
  state files.
- **User asks to undo a previous skill's output.** Route to the skill that
  produced the output. cws-help doesn't own any artifact.
- **User is mid-decision in another cws-studio skill's AskUserQuestion.**
  Don't interrupt. Wait for the brief to resolve, then re-evaluate.

---

## Companion skills

**None.** cws-help is the entry point — it is itself the route to
companions, not consumer of them. Do not add a "companions" section in any
response except as part of the catalog block itself.

---

## Worked examples

### Example 1 — Fresh-repo exploration

User in a fresh directory types: `/cws-help`

Preamble echoes:
```
CWS_STATE: missing
```

Posture: 1 (fresh exploration, no state, no specific topic).
Catalog variant: Fresh-project.

Response (≤ one screen):

> cws-studio — Chrome Web Store launch pipeline. Six stages, on-disk state
> in ./.cws/. Nothing scaffolded here yet.
>
> Pipeline:
>   Stage 0  account-setup    /cws-idea (uses /cws-dolphin)
>   Stage 1  idea-validation  /cws-idea
>   Stage 2a listing-copy     /cws-package
>   Stage 2b build            /cws-build
>   Stage 3  assets + submit  /cws-launch  (gated by /cws-careful)
>   Stage 4  paid promotion   /cws-promote
>   Stage 5  monetization     /cws-monetize (gated by /cws-careful)
>
> Conductor: /cws-sprint /cws-autoplan /cws-init
> Companions: /cws-challenge /cws-careful /cws-retro /cws-learn /cws-resync /cws-dolphin
>
> Next: /cws-init
> Why: scaffolds ./.cws/ so every subsequent skill finds state without re-prompting.

### Example 2 — Mid-pipeline "where am I"

User mid-launch types: `where am I`

Preamble echoes:
```
CWS_STATE: present
GATES_PASSED: account-setup,idea,package
```

Posture: 2 (state present, "where am I"). Catalog variant: none.

Response:

> State: gates passed account-setup,idea,package. /cws-sprint reads the
> stage artifacts and picks the next move.
>
> Next: /cws-sprint
> Why: sprint is the diagnosis skill. cws-help only routes; it doesn't
> read stage artifacts.

No catalog. No restating gates. No predicting next stage. Hand off.

### Example 3 — Specific topic ("how do I rotate proxies")

User types: `how do I rotate proxies across profiles?`

Preamble echoes:
```
CWS_STATE: present
GATES_PASSED: account-setup
```

Posture: 3 (specific topic, companion skill). Catalog variant: Ops-only
(only printed if the user asks for the companion ring; here, skip it
because the question is more specific than "show me companions").

Response:

> Proxy rotation is /cws-dolphin's job. The skill has a `proxies-rotate`
> subcommand that swaps the residential IP for a named profile and
> updates state.json. /cws-dolphin references/dolphin-api.md walks the
> failure modes (sticky session loss, geolocation drift, ASN flag).
>
> Next: /cws-dolphin
> Why: rotation lives in the dolphin skill; cws-help only routes.

One paragraph. One reference path. One Next: line. Done.

---

## Output convention

Every cws-help response is at most:

1. One short paragraph or one catalog block (≤ 25 lines).
2. One blank line.
3. `Next: /cws-<skill>` on a single line.
4. `Why: <one sentence>` on a single line.

### Anti-pattern 1 — Banner

```
╔══════════════════════════════════╗
║  Welcome to cws-studio!  🎉      ║
╚══════════════════════════════════╝
```

No. Operator voice. No banner. No emoji. No greeting.

### Anti-pattern 2 — File dump

> Here are the references you might want:
> - cws-idea/references/semrush-playbook.md (full content pasted below)
> - cws-idea/references/scoring-rubric.md (full content pasted below)
> ...

No. Link out, never paste. The user invokes the skill if they want depth.

### Anti-pattern 3 — Menu

> Which of these would you like?
>   1. Catalog
>   2. Specific topic
>   3. Where am I
>   4. Stage 0 setup

No. Pick by posture + state. The user already told you which one by what
they typed and what's on disk.

---

## Skill Routing Footer

```
Next: /cws-<picked-by-Phase-0-posture>
Why: <one sentence — what it does for the user's current state>
```

If state is missing → `/cws-init`.
If state is present and the user asked "where am I" → `/cws-sprint`.
If state is present and the user named a specific skill → that skill.
If the user asked a topic question → the skill that owns the topic.
If unclear → `/cws-sprint` (it does the diagnosis).
