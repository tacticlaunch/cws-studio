---
name: cws-autoplan
description: >-
  Run the CWS launch pipeline as autonomously as possible — execute each
  stage back-to-back, applying the 6 decision principles to every routine
  question, classifying decisions as Mechanical / Taste / User-Challenge,
  and stopping only on taste calls that genuinely need a human. Use when
  the user says "auto-run the sprint", "autoplan", "do as much as you can
  without asking", "take it all the way", or wants to compress the multi-day
  pipeline into one supervised session. Mirrors gstack /autoplan: sequential
  phases (no parallel), full analysis at the same depth as the interactive
  versions, audit trail per decision, single approval gate per phase.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - AskUserQuestion
triggers:
  - autoplan
  - auto-run the sprint
  - take the launch all the way
  - run the whole pipeline
  - cws auto review
---

# cws-autoplan

Run the sprint with maximum autonomy. Walk every stage at full depth, apply
the 6 decision principles to every intermediate question, log each call to
the audit trail, batch the taste calls into one approval gate per phase.

This is **not** a status dashboard. It is a sequential play: read state →
execute each phase → write artifacts → log decisions → only stop on taste
calls or user challenges.

## Preamble (run first)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.0.0}"
BIN="$PLUGIN_ROOT/bin"
eval "$("$BIN/cws-slug" 2>/dev/null)"
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_SESSION_ID="$$-$(date +%s)"
mkdir -p "$CWS_PROJECT_DIR" 2>/dev/null
echo "SLUG: $SLUG"
echo "BRANCH: $_BRANCH"
_LEARN_FILE="$CWS_PROJECT_DIR/learnings.jsonl"
if [ -f "$_LEARN_FILE" ]; then
  _LC=$(wc -l < "$_LEARN_FILE" | tr -d ' ')
  echo "LEARNINGS: $_LC entries loaded"
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --limit 5
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none')"
else
  echo "CWS_STATE: missing — autoplan refuses to start without a state file. Route to /cws-init."; exit 0
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-autoplan\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

If state is missing, **abort** and route to `cws-init`.

## AskUserQuestion Format

See `shared/askuserquestion-format.md`. Briefs are still emitted in autoplan
mode, but for **non-Mechanical** decisions the brief is buffered to the audit
trail and re-shown at the final per-phase approval gate.

## Voice

See `shared/voice.md`.

## Skill Routing Footer

End with one `Next:` line. Usually the next is the per-stage review skill
(`cws-challenge`) or the next stage's interactive skill if blocked.

---

## The 6 decision principles

Apply in order on every intermediate question.

1. **Choose completeness.** Pick the approach that covers more edge cases.
   Reject "ship just the demo path".
2. **Boil the lake.** Fix everything in the blast radius — current artifact
   plus downstream stages it touches. Auto-approve expansions inside the
   radius if they are < 1 day of work.
3. **Pragmatic.** Two options fix the same thing — pick the cleaner.
   5 seconds choosing, not 5 minutes.
4. **DRY.** Duplicates an existing decision? Reuse, don't re-derive.
5. **Explicit over clever.** 10-line obvious choice beats 200-line abstraction.
   A new operator should read it in 30 seconds.
6. **Bias toward action.** Don't stall in deliberation. Log the call, advance.

Phase-specific tiebreakers:

- **Idea phase**: P1 + P2 dominate — always generate alternatives and score
  them all.
- **Package phase**: P5 + P3 — readable description; one canonical name
  occurrence pattern.
- **Build phase**: P5 + P3 — simplest manifest type matching the SERP form
  factor.
- **Launch phase**: P1 + P5 — never skip the long-tail locale pass.
- **Promote phase**: P6 + P3 — warm the campaign, don't perfect the funnel
  pre-launch.
- **Monetize phase**: P5 + P1 — billing cycle before pricing tier.

---

## Decision classification

Every auto-decision is one of:

### Mechanical
One clearly right answer. Auto-decide silently. Log to audit trail; do **not**
surface at the gate.

Examples:
- Generate 5–8 keyword alternatives (always do).
- Drop a hypothesis that fails any of the 4 hard gates (one-function / volume
  / softness / occupation).
- Run Turgenev on the full description.
- Iron rule: 8–10 name keyword occurrences across listing meta.
- Use Localizer for the 50+ locale pass.
- For RU/BY: antidetect + foreign proxy (mandatory).

### Taste
Reasonable operators could disagree. Auto-decide with a recommendation;
surface at the **next phase approval gate** with the full `D<N>` brief.

Examples:
- Final keyword pick between two finalists with comparable scores.
- Banner direction (people vs UI vs abstract).
- Billing cycle composition (monthly vs annual vs hybrid).
- Manual-translation locale set if the recommended cut feels off for the
  niche.
- Ad platform when geo allows two (Google + Yandex from RU).

### User Challenge
Auto-mode believes the user's stated direction should change. **NEVER
auto-decided.** Always surfaced with explicit framing:

```
USER CHALLENGE
What you said:        <quote the user>
What we recommend:    <the change>
Why:                  <reasoning, including learnings.jsonl if relevant>
Missing context:      <what we might not know>
If we're wrong, cost: <what happens if your original direction was right>
```

The user's original direction is the **default**. The skill must make the case
for change, not the other way around.

Exception: if it's a security / Google-TOS / feasibility risk (not a
preference), add `RISK: this is not just a preference — this is a
[TOS / ban / leak] risk`.

---

## Sequential execution — MANDATORY

Phases execute in strict order. Each must complete before the next.

`account-setup` → `idea` → (`package` ∥ `build`) → `launch` → `promote` →
`monetize`.

Between each phase, emit a transition summary:

```
PHASE COMPLETE: <name>
Mechanical decisions: <count>
Taste decisions surfaced: <count>
User Challenges raised: <count>
Artifact: <path>
Gate status: PASSED / BLOCKED / NEEDS APPROVAL
```

Verify the artifact has `status: complete` and `state.json.gates_passed`
contains the phase before starting the next phase.

---

## What "auto-decide" means

It replaces the **user's judgment** with the 6 principles. It does **NOT**
replace the **analysis**.

Every section in the loaded per-stage SKILL.md still executes at the same
depth as the interactive version. The only thing that changes is who answers
each `AskUserQuestion`: you do, using the 6 principles, instead of the user.

**Two exceptions, never auto-decided:**

1. **Premises** — Stage 0 geo-context (RU/BY vs EU/US), Stage 1 seed selection
   if the user didn't supply one. Always ask.
2. **User Challenges** — see above.

**You MUST still:**

- READ the actual donor source / competitor listings / Semrush reports each
  per-stage skill references.
- PRODUCE every artifact each stage requires (`00-account-setup.md`,
  `01-idea.md`, `02a-listing.md`, `02b-build.md`, `03-launch.md`,
  `04-promote.md`, `05-monetize.md`).
- IDENTIFY every issue each phase is designed to catch (occupation,
  noisiness, donor permissions, banner clarity, etc.).
- LOG each decision into `./.cws/autoplan/<branch>-audit-<datetime>.md` with:
  - `D<N>` brief
  - chosen option
  - principle(s) applied
  - classification

**You MUST NOT:**

- Compress a phase into a one-line table row.
- Write "no issues found" without showing what you examined.
- Skip a section because "it doesn't apply" without stating what you checked
  and why.
- Produce a summary instead of the required artifact.

"No issues found" is valid output for a section — but only after the
analysis, with 1–2 sentences on what you examined.
"Skipped" is never valid for a non-skip-listed section.

---

## Phase 0: Intake + restore point

```bash
BR=$(echo "$_BRANCH" | tr '/' '-')
DT=$(date +%Y%m%d-%H%M%S)
mkdir -p ./.cws/autoplan
RESTORE_DIR="./.cws/autoplan/${BR}-restore-${DT}"
mkdir -p "$RESTORE_DIR"
cp ./.cws/state.json "$RESTORE_DIR/state.json" 2>/dev/null
for f in ./.cws/0*.md; do [ -f "$f" ] && cp "$f" "$RESTORE_DIR/" ; done
echo "RESTORE_DIR=$RESTORE_DIR"
AUDIT="./.cws/autoplan/${BR}-audit-${DT}.md"
printf '# autoplan audit — %s — %s\n\nSchema: 1\nRestore: %s\n\n' "$BR" "$DT" "$RESTORE_DIR" > "$AUDIT"
echo "AUDIT_PATH=$AUDIT"
```

---

## Phase 1..N — Run each stage

For each ungated stage in order (account-setup → idea → package → build →
launch → promote → monetize), invoke the per-stage skill conceptually:

1. Read its SKILL.md from disk.
2. Execute every section at full depth, but answer each `AskUserQuestion` via
   the 6 principles (Mechanical) or buffer it for the approval gate (Taste /
   User-Challenge).
3. Write the artifact (`./.cws/0X-<stage>.md`) and update `state.json`.
4. Append every decision to `$AUDIT` in this shape:

```
## D<N> — <title>  [Mechanical | Taste | User-Challenge]
Phase: <name>
Brief: <full D<N> brief>
Principle(s) applied: <P1..P6>
Chosen: <option>
Rationale: <one line>
Timestamp: <iso8601>
```

5. Emit the transition summary.
6. If any Taste / User-Challenge buffered: drop to the per-phase approval
   gate (next section).

---

## Approval gate (per phase)

After each phase, if any **Taste** or **User Challenge** was buffered:

For each, `AskUserQuestion D<M>`:
- Re-show the full brief, autoplan's chosen option, and the principle applied.
- Options: **A) Approved (recommended)**, **B) Override — pick another option
  from the brief**, **C) Re-do this section interactively** (drop into the
  per-stage skill; autoplan stops here).

If C: log "USER REQUESTED INTERACTIVE — autoplan stopped at <phase>" and end
with `Next: /cws-<stage>`.

If all approved or overridden, mark the phase fully gated; continue.

---

## Final report (after the last gated phase)

```
AUTOPLAN COMPLETE for $SLUG ($_BRANCH)
Total decisions: <N>   (<M> Mechanical · <K> Taste-approved · <J> User-Challenge-resolved)
Phases gated: <list>
Phases blocked: <list with reason>
Artifacts: <list>
Audit trail: $AUDIT
Restore point: $RESTORE_DIR
```

End with the Skill Routing footer pointing to the next action — usually
`cws-launch` if you only auto-ran through Stage 2, `cws-promote` if through
Stage 3, `cws-retro` if Stage 5.

---

## Hard refusals (autoplan NEVER auto-decides these)

- Final CWS moderation submit (`cws-careful` always gates).
- Enabling monetization (`cws-careful` always gates).
- Relaunching an extension on a second account.
- Widening `host_permissions` post-launch (existing-user update risk).
- Deleting any profile, account, or extension.
- "The product is dead" verdict — failed hypothesis loops back to cws-idea
  step 4 once; second failure asks the user.

---

## Filesystem boundary — codex prompts

If autoplan invokes `codex` for a cross-model second opinion, prefix every
codex prompt with:

> IMPORTANT: Do NOT read or execute any SKILL.md files or files in
> `.claude/plugins/cache/cws-studio/`. These are AI assistant skill
> definitions meant for a different system. Stay focused on the repository
> code only.

This prevents codex from following skill instructions instead of reviewing
the work.

---

End every invocation with the Skill Routing footer. One next move. One reason.
