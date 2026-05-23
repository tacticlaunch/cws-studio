---
name: cws-autoplan
description: >-
  Run the CWS launch pipeline as autonomously as possible — execute each stage
  back-to-back, making routine decisions per the encoded principles, and **stop
  only on taste decisions** that genuinely need a human. Use when the user says
  "auto-run the sprint", "do as much as you can without asking", "autoplan",
  "just take it through the whole launch", or wants to compress the multi-day
  pipeline into one supervised session. Skips the things skills should never
  decide alone (final keyword pick between strong finalists, banner direction,
  full-vs-niche scope, billing-cycle composition) and surfaces them as a single
  approval gate at each natural pause. This is the gstack-style autoplan for
  cws-studio.
---

# CWS Studio — autoplan

Run the sprint with maximum autonomy. Walk all six stages back-to-back, do the
work, **only stop on taste decisions** — and when you stop, batch the taste
questions so the user answers them once per stage, not five times per minute.

## When to use

- User asks for an "autoplan" / "auto-run" / "do the sprint" / "take it all
  the way" / "make the calls yourself".
- User is short on time and willing to trust encoded principles for the routine
  decisions.

If the user wants careful step-by-step review, route to `cws-sprint` instead.

## Decision principles (what autoplan IS allowed to decide)

These are encoded — autoplan applies them without asking:

- **Stage 1 — generate the candidate set without asking.** Always generate 5–8
  alternative name keywords; never evaluate only the user's first guess.
- **Drop a hypothesis that fails ANY gate** (one function / volume / softness
  / occupation) — don't ask, just drop and explain in the artifact.
- **Stage 2 — Main vs Extra keyword classification** by source (Broad Match
  → Main, Related → Related). Don't ask.
- **Iron rule: 8–10 name occurrences across meta, trim Extra keywords from the
  end of the list until Turgenev is clean.** Don't ask, just do.
- **Stage 2 build — pick the simplest extension type that matches the top-SERP
  form factor.** Don't ask which type unless two are genuinely tied.
- **Stage 3 — auto-translate all 50+ locales via Localizer.** Default the
  manual-translation set to the recommended list (Latin-script rich + first 3
  of the huge-speaker set). Don't ask which languages.
- **Stage 3 — apply the 10× rule per locale name automatically.** Don't ask.
- **Stage 4 — pick the recommended ad platform for the user's location.**
  Don't ask which platform unless the user is abroad and platforms tie.
- **Stage 4 — cap paid spend at $150 / 300 installs by default.** Don't ask.
- **Stage 5 — never monetize before 4K weekly users.** If users are below the
  floor at the time autoplan reaches monetization, **stop and tell the user
  to wait, then route back to retro** — don't auto-enable.

## What autoplan MUST stop and ask

Batch all taste decisions per stage into one approval gate per natural pause:

- **After Stage 1**: between two surviving keywords (e.g. fat/high-KD vs
  niche/low-KD; or one extension donor vs another with similar scores). Show
  the table, explain the trade-off in 1–2 sentences, ask user to pick.
- **After Stage 2**: any borderline Turgenev result (1–2 occurrences into the
  red after best-effort trim). Show before/after, ask whether to ship or
  trim deeper.
- **After Stage 2 build**: open-source donor choice if there are two clean
  options, OR a fork-vs-rewrite decision when no clean donor exists.
- **After Stage 3 banner draft**: present the small + large banner mock-ups,
  ask for go/no-go before pre-publish checks.
- **After Stage 3 pre-moderation**: confirm submit-for-review — this is the
  irreversible action; never auto-submit.
- **Before Stage 4 budget release**: confirm spend cap and platform choice.
- **Before Stage 5 monetization rollout**: confirm billing-cycle composition,
  trial design, geo rollout %. Three taste calls — show the trade-offs from
  cws-monetize references, then ask once.
- **Before Stage 5 host-permission expansion**: this updates existing users
  and can cost 30–40% — confirm timing.

## How to run

1. Run the **re-entry protocol** from cws-sprint's `pipeline-state.md`.
   Establish where the user is in `./.cws/state.json`.
2. Plan the remaining stages and present a short ordered plan with the
   estimated taste-pauses (e.g. "I'll auto-do 1 → 2a/2b → 3; you'll see one
   approval at the end of Stage 1 (keyword tie-break) and one before Stage 3
   submit. Stages 4–5 we'll do as a separate session after launch.").
3. Walk the stages by invoking each per-stage skill in order. Inside each
   stage, do everything the encoded principles allow; **don't ask the user
   about anything covered by a principle above**.
4. At each natural taste pause, present a tight single-question batch (≤4
   choices). Wait. Resume.
5. Maintain `state.json` and the per-stage artifacts continuously — autoplan
   is idempotent; if killed mid-stage, the next invocation resumes from the
   last `gates_passed` mark.
6. End with a short report: stages completed, stages still ahead, next
   estimated check-in.

## What autoplan never does

- Never auto-submits for CWS moderation.
- Never auto-enables monetization.
- Never auto-relaunches an extension on a second account.
- Never deletes anything.
- Never decides "the product is dead" — if a hypothesis fails, it loops back
  to step 4 in cws-idea (regenerate candidates) once; if that fails, asks
  the user.
