---
name: cws-package
description: >-
  Write and SEO-optimize the Chrome Web Store listing copy for a browser
  extension — name, short description, and full description. Stage 2 (packaging)
  of the CWS launch pipeline. Use when the user wants to write or improve an
  extension's store listing: pick the final name, create the short/full
  description, optimize keyword saturation, check the text for spam
  (Turgenev/pessimization risk), compare the text against competitors, or verify
  the name keyword saturates the text. Triggers on "write my extension
  description", "optimize my CWS listing", "check my listing for spam", "pick a
  name for my extension", or "how long should my description be". Leans on the
  Semrush MCP for keyword gathering.
---

# CWS Studio — Stage 2: Listing copy

The **meta-information** = name + short description + full description. A
well-built name (across languages) drives ~70% of SEO success; the descriptions
the remaining ~30%. This stage runs in parallel with **cws-build**.

## Core principles

1. The **name keyword** (chosen in Stage 1, cws-idea) is the ranking lever.
2. Descriptions must be **keyword-rich but not spammed** — Google pessimizes
   over-spammed text; CWS moderation rejects visible keyword stuffing.
3. **Structure wins** — emoji-marked lists, short paragraphs, FAQ blocks.
4. All copy is in **English** and must be run through a "correct this text" pass
   — the paying audience are native speakers.

## What this stage produces

- `name` (≤75 chars) and `description` (≤132 chars) in `manifest.json`.
- A ~4,500-char full description, keyword-optimized, spam-checked, with the name
  keyword used 8–10× across the meta (the iron rule that guarantees no overspam).

## How to run it

Follow `references/listing-copy.md` — the full workflow: character limits,
Main/Extra keyword sourcing (Semrush Broad Match vs Related tabs), the ChatGPT
generation prompt, the quality checklist, the Turgenev spam check, pessimization
risk, competitor comparison, list structure, capitalization, and the
name-saturation check.

See `references/listing-examples.md` for three full real descriptions that
passed CWS moderation and ranked well — use them as the structural target.

## Gate to the next stage

Name + short + full description written, spam-free in Turgenev (no red flags,
overall risk low/insignificant), name keyword in the top of Turgenev's word and
phrase tabs.

Next stage: **cws-launch** (assets, translations, publishing).

## Artifacts & re-entry

This skill reads `./.cws/state.json` + `./.cws/01-idea.md` (required prior
gate: `idea`) and writes `./.cws/02a-listing.md`. Follow the re-entry protocol
in cws-sprint's `pipeline-state.md` reference.

**`02a-listing.md` must contain:**
- Final `name` (≤75) and `description` / short desc (≤132).
- Full description (~4,500 chars) — the actual text, ready to paste into CWS.
- Main keywords table: keyword | times used | source (Broad Match / Phrase /
  Exact / generated).
- Extra keywords table: keyword | times used | source (Related).
- Turgenev verdict: `repeats_red_flags: 0`, `overall_risk: low|insignificant`,
  `purple_words: []`, `name_words_top: yes`.
- Capitalization audit (proper-case name; ~30/70 mix in full desc).
- Spam-check screenshot reference / paste of the Turgenev output (textual).

**On gate pass**, update `state.json`:
- `package.name`, `package.short_desc_chars`, `package.full_desc_chars`,
  `package.name_occurrences_total` (must be 8–10).
- `package.turgenev_clean: true`.
- Append `"package"` to `gates_passed`; log `gate_passed` event.
- Set artifact frontmatter `status: complete`.
