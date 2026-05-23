# Semrush MCP playbook

How to drive the Semrush MCP for CWS extension validation. The MCP is multi-step: a **discovery** call lists reports, `get_report_schema` returns a report's parameters, and `execute_report` runs it. You usually don't need discovery — call `get_report_schema(report=...)` then `execute_report(...)` directly.

Always use the **`us`** database unless the user asks otherwise (the methodology benchmarks on US volume). Output is **semicolon-delimited CSV** with a header row; parse it, don't quote it back raw.

## Report cheat-sheet (toolkit: keyword_research)

| Validation step | Report | What it gives | Key params |
|---|---|---|---|
| 4, 8 — head volume + KD | `phrase_this` | Single keyword: volume, CPC, competition, #results, **KD**, trend | `phrase`, `database`, `export_columns` |
| 4, 6 — variations / long tails | `phrase_fullsearch` | All variants containing the phrase (reorderings, spellings) w/ volumes | `phrase`, `database`, `export_columns`, `display_limit` |
| 4 — generate candidates | `phrase_related` | Semantically related / adjacent terms w/ volume + KD | same |
| 6 — question tails | `phrase_questions` | who/what/how question keywords w/ volume | same |
| 5, 7 — SERP (softness + competitors) | `phrase_organic` | Ranking domains/URLs/positions for the keyword | `phrase`, `database`, `export_columns` |
| 8 — KD only | `phrase_kdi` | Keyword difficulty index | `phrase`, `database` |
| 10 — batch scoring | `phrase_these` | Metrics for many keywords at once | `phrase` = `kw1;kw2;kw3`, `database` |
| multi-country reach | `phrase_all` | Volume/CPC/competition per country | `phrase`, `database` |

## Useful export_columns

Pass `export_columns` as an array. Common codes:
- `Ph` keyword phrase · `Nq` search volume · `Cp` CPC · `Co` competition (0–1) · `Nr` number of results · `Kd` keyword difficulty index · `Td` trend (12-month series)
- For `phrase_organic`: `Dn` domain · `Ur` URL · `Po` position

If `export_columns` is omitted you get defaults (`Ph, Nq, Cp, Co, Nr`) — KD won't be included, so request `Kd` explicitly when you need it.

## Worked calls

**Head volume + KD (steps 4 & 8):**
```
execute_report(report="phrase_this",
  params={"phrase": "site blocker", "database": "us",
          "export_columns": ["Ph","Nq","Cp","Co","Nr","Kd","Td"]})
```
Returns e.g. `site blocker;2900;1.3;0.3;2510000000;74;0.36,...` → US volume **2900**, KD **74** (red zone → 6 pts). 2900 ≥ 2000 broad-niche threshold → passes step 4.

**SERP for softness + competitor check (steps 5 & 7):**
```
execute_report(report="phrase_organic",
  params={"phrase": "site blocker", "database": "us",
          "export_columns": ["Dn","Ur","Po"]})
```
Read the top ~10 domains. Count software vs. non-software for softness. Flag any `chromewebstore.google.com` URLs as extension competitors, **note their position**, and open them (web_fetch) to judge optimization (name overlap, >3K-char description, >30 translations). Occupation is judged by **prime positions (top-10, especially top-5)** — an extension at #19 behind a page full of websites means the keyword is *winnable*, not occupied.

**Variations / long tails (steps 4 & 6):**
```
execute_report(report="phrase_fullsearch",
  params={"phrase": "site blocker", "database": "us",
          "export_columns": ["Ph","Nq","Kd"]})
```

**Candidate generation (step 4):**
```
execute_report(report="phrase_related",
  params={"phrase": "site blocker", "database": "us",
          "export_columns": ["Ph","Nq","Kd"]})
```

**Batch scoring several finalists (step 10):**
```
execute_report(report="phrase_these",
  params={"phrase": "site blocker;web site blocker;focus mode", "database": "us",
          "export_columns": ["Ph","Nq","Kd"]})
```

## Interpreting volume (the three numbers in the source UI)

The Semrush Keyword Overview screen shows three figures; map them to reports:
- **Volume** (US, exact, no long tails) → `phrase_this` `Nq` on the US database. **This is the number the thresholds (2K / 500) are measured against.**
- **Global Volume** (worldwide, exact) → `phrase_all` summed, or the US/world proportion.
- **Keyword Variations total volume** (US, *with* long tails) → `phrase_fullsearch` summed `Nq`.
Worldwide-with-tails ≈ extrapolate from the US/global proportion (source example: US 2.4K / global 42.6K ≈ 5%; so US-with-tails 103.5K ÷ 5% ≈ 2M worldwide).

## Notes & caveats

- Semrush sometimes under-reports ("no volume") on keywords that clearly have SEO traffic. Don't bet on those — prefer confirmed volume.
- KD applies to sites more than extensions; an optimized extension can rank at very high KD on its exact head term, but only there if the query is noisy.
- Keep API usage sane: one `phrase_this` + one `phrase_organic` per finalist keyword is usually enough; batch with `phrase_these` for the final comparison.
