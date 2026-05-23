# Scoring rubric & output template

Two kinds of criteria: **0–10 scores** (judged *relatively* across the candidate set, except KD which is fixed-tier) and **gates** (binary; a failed gate disqualifies the hypothesis regardless of points).

## Scored criteria (0–10, relative)

| # | Criterion | How to score |
|---|---|---|
| Users | Popularity of the seed | Score the seed's user count 0–10 vs. the other candidates. Exclude giant brand extensions. |
| Revenue | Monetization potential | users/10 (one-time) + (users/100)×$3 (IAP); **boost** if a paid subscription exists and the higher its price. |
| Simplicity | Ease of building one function | Relative 0–10; **raise** when open-source prior art exists on GitHub. |
| Volume | Name-keyword search demand | Relative 0–10 from US exact volume (`phrase_this`). Must clear the gate threshold below. |
| KD | Keyword difficulty (fixed tiers) | 0–49 → **10**, 50–69 → **7**, 70–84 → **6**, 85–100 → **5**. |

## Gates (binary — failing = DROP)

| Gate | Pass condition | Fail = |
|---|---|---|
| One function? | Idea collapses to one simple feature | DROP |
| Volume threshold | US exact ≥ 2,000 (broad niche) or ≥ 500 (narrow niche) | DROP |
| Softness | >50% of top SERP is software; **not** >30% non-software | DROP keyword |
| Keyword free | Not owned by a *well-optimized* extension (name contains all your words + >3K-char description + >30 translations) | RED FLAG → DROP keyword |

A niched name with lower volume than a generic competitor is **fine** — do not penalize volume for niching down (you outrank the generic competitor on the niched query).

## Total

`Total = Users + Revenue + Simplicity + Volume + KD` (each 0–10; max 50).
Any failed gate ⇒ **Verdict = DROP** with the reason, and the row is not ranked on points.

## Output table template (always use this)

```markdown
| Hypothesis (seed) | Name keyword | Users | Revenue | Simplicity | Volume | KD (zone) | Soft? | Keyword free? | Total | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| CSS Scan | css checker | 8 | 9 | 9 | 6 | 8 (orange→7... ) | YES | YES | 48 | #1 |
| GoFullPage | page screenshot | 9 | 8 | 9 | 7 | – | YES | NO (optimized) | – | DROP — RED FLAG (keyword occupied) |
```

Then add:
- **Recommendation** (2–4 sentences): which to build first and why; if the user is choosing between a fat/high-KD vs. niche/low-KD keyword, recommend testing both but **starting with the niche/low-KD** one.
- **Confidence flags**: note any metric that's low-confidence (Semrush unavailable, ambiguous softness SERP, unverified monetization).

Keep KD cell readable: show the % and the zone, e.g. `74 (red → 6)`.
