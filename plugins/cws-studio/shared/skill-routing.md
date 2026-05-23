# Skill Routing Footer

End every cws-studio skill invocation with a **single next-skill recommendation**.
Never a menu. The user can override by typing another skill name.

## Decision table

| Just completed | Next skill | Reason |
|---|---|---|
| `cws-init` (scaffolded) | `cws-idea` | Stage 0 (proxy + antidetect) routes through cws-idea preamble. |
| `cws-idea` (account-setup gate passed) | `cws-idea` (continue into idea validation) | Same skill handles Stage 0 → Stage 1. |
| `cws-idea` (idea gate passed) | `cws-challenge` | Stress-test the chosen keyword before building. |
| `cws-challenge` on idea | `cws-package` + `cws-build` (parallel) | Listing copy and build are independent. |
| Both `cws-package` and `cws-build` gates passed | `cws-launch` | Assets + publish. |
| `cws-launch` submitted, moderation pending | wait → `cws-retro` snapshot baseline | Don't spam moderators. Capture baseline. |
| `cws-launch` approved | `cws-promote` | Ad warm-up cannot wait. |
| `cws-promote` running, < 3K weekly users | `cws-retro` weekly | Watch behavioral factors. |
| `cws-promote` running, ≥ 3K users, search position consolidated | `cws-challenge` → `cws-monetize` | Stress-test before paywall. |
| `cws-monetize` enabled | `cws-retro` monthly + queue `cws-idea` for next product | Ship next. |
| Any retro flagged regression | `cws-resync` then the stage skill | Don't paper over downstream rot. |
| Any irreversible step (submit, monetize on, host_permissions widen, account delete) | `cws-careful` **before** the action | Hard gate. Never skip. |

## Form

End the skill with this block (prose, not banner):

```
Next: /cws-<skill>
Why: <one sentence — what it does and why this is the next move>
```

If you have nothing to recommend (e.g. waiting on moderation), say so:

```
Next: wait — CWS moderation is pending; usual SLA 1–3 business days. Run
`/cws-retro` once to capture the pre-promotion baseline while you wait.
```

Never list 3 options. Never say "you can run X, Y, or Z." Pick one.
