# AskUserQuestion Format (cws-studio canonical)

Every interactive decision goes through `AskUserQuestion` as a **decision brief**,
not prose. Pattern is identical to gstack's; reproduced here so each skill can
reference one file.

## Tool resolution

`AskUserQuestion` resolves to either an MCP-hosted variant (e.g.
`mcp__conductor__AskUserQuestion`) or the native Claude Code tool. If any
`mcp__*__AskUserQuestion` variant is in your tool list, prefer it. If none is
available, the skill is **BLOCKED** — stop and report
`BLOCKED — AskUserQuestion unavailable`. Never substitute prose stop-and-wait.

## Brief format

```
D<N> — <one-line question title>
Project/branch/task: <one short grounding sentence using $SLUG, $_BRANCH>
ELI10: <plain English a 16-year-old could follow, 2–4 sentences, name the stakes>
Stakes if we pick wrong: <one sentence — what breaks, what user sees, what's lost>
Recommendation: <choice> because <one-line reason>
Completeness: A=X/10, B=Y/10
  (or: Note: options differ in kind, not coverage — no completeness score)
Pros / cons:
A) <option label> (recommended)
  ✅ <pro — concrete, ≥40 chars>
  ✅ <pro>
  ❌ <con — honest, ≥40 chars>
B) <option label>
  ✅ <pro>
  ❌ <con>
Net: <one-line synthesis — what you're trading off>
```

- D-numbering increments per skill invocation (D1, D2, …). It is **model-level**;
  not a runtime counter.
- `Recommendation:` is ALWAYS present. Keep `(recommended)` on one option even
  when the call is neutral — `cws-autoplan` depends on it.
- `Completeness: N/10`: 10 = covers everything, 7 = happy path, 3 = shortcut. If
  options differ in kind not coverage, write the kind-note instead.
- Pros/cons: minimum 2 ✅ and 1 ❌ per real option, each ≥40 chars. Hard-stop
  escape: `✅ No cons — this is a hard-stop choice`.
- Effort labels (when relevant): dual-scale, e.g. `(human: ~2 days / CC: ~15 min)`.
- Non-ASCII (Cyrillic / CJK / accents): write literal UTF-8. **Never** `\uXXXX`-escape
  long strings — model misencodes codepoints reliably.

## Self-check before emitting

Before calling `AskUserQuestion` verify:

- [ ] `D<N>` header present
- [ ] `ELI10` paragraph present
- [ ] `Stakes if we pick wrong` line present
- [ ] `Recommendation:` line with a concrete reason
- [ ] `Completeness:` scored OR kind-note present
- [ ] Every option has ≥2 ✅ and ≥1 ❌, each ≥40 chars (or hard-stop escape)
- [ ] `(recommended)` label on exactly one option
- [ ] `Net:` synthesis line closes the trade-off
- [ ] You are calling the tool, not writing prose
- [ ] Non-ASCII chars literal, not `\uXXXX`

## Auto-mode (`cws-autoplan`)

In `cws-autoplan` the same brief is generated, but answered by the 6 decision
principles (completeness · boil-lakes · pragmatic · DRY · explicit · bias-to-action)
instead of by the user. Briefs are logged to the audit trail in the autoplan
artifact. Three classes:

- **Mechanical** — one clearly right answer; auto-decide silently.
- **Taste** — reasonable people could disagree; auto-decide with reason, surface
  at the final approval gate.
- **User Challenge** — auto-mode thinks the user's stated direction should change;
  NEVER auto-decided; always surface for confirmation with explicit framing of
  what the user said vs. what the models recommend.
