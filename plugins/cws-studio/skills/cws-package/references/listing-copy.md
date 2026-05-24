# Stage 2 — Listing copy (name, short & full description)

The **meta-information** = name + short description + full description. A
well-built name (across languages) drives ~70% of SEO success; the short + full
description the remaining ~30%. Track all of it in a working doc as you go.

## Character limits

| Element | manifest key | Max chars (incl. spaces) | Target |
|---|---|---|---|
| Name / title | `name` | 75 | the chosen keyword |
| Short description | `description` | 132 | name + 2 keywords |
| Full description | (uploaded in CWS, not manifest) | 16,000 | **~4,500** |

## 1. Name

Most of the work was done in Stage 1 (choosing the name keyword). Put that
keyword into `name` in `manifest.json`.

- More popular query → more potential audience, but harder to rank #1. Don't use
  ultra-popular 1-word names (`adblocker`, `screenshot`). You can start mid-popular
  and rename to a fatter query once the extension grows.
- You can **mix two popular queries** in one name (`Free and fair adblocker`) to
  rank for both — but ranking for two at once is always harder than one. Best
  used in low-competition niches and non-English languages.
- **Never** use `best`, `recommended`, `premium`, `free`, `#1` in name or
  descriptions — moderation rejects them.

## 2. Short description

Ask ChatGPT for a short description that uses the name once and ~2 other
keywords. Keep it plain. Specifics:
- The single most important word of the name ~3×; any other keyword ≤2× (don't
  let two different words both hit 3×).
- Fill near the **132-char max** (~130) — extra words space the keywords apart,
  which helps pass moderation.

## 3. Full description (~4,500 chars)

Write it with ChatGPT, then **edit by hand** — ChatGPT swallows keywords, forgets
lists, makes mistakes. Generate it a few times and assemble the best paragraphs.

Prompt template:
```
Work as a professional SEO specialist. Write description for google chrome
extension: about 4500 characters, 10-16 paragraphs. Sometimes use emojis, but
not more than one per line. Don't use quotation marks. Use lists at least 5
times, for example: 1, 2, 3 and 1️⃣, 2️⃣, 3️⃣ and -, ➤, ▸, •. Separate
paragraphs with spaces. Also, use the following keywords exactly as they are
written and as often as possible. List of the keywords:
[your keyword list, one per line]
```

Quality checklist for the final text:
- **Structured lists, multiple types**: numbered (1,2,3 / 1️⃣,2️⃣,3️⃣), bullets
  (➤ ▸ •), dashes (-), emoji markers (💡 📌 📍), question-answer (FAQ).
  Structure and "air" (short paragraphs, no walls of 4–5+ lines) boost SEO.
- **Main keyword** (name keyword + its long-tail variations) used ~15–20 times.
  ~Half as the exact name keyword, ~half as variations with tails (`ai email
  generator tool`, `ai email response generator`).
- **Extra keywords** (other Semrush keywords) also used ~15–20 times. ~30
  keywords total for a 4,500-char text. Keep 15–20 rows of keywords per category.
- Use keywords as **whole phrases** (`color code picker`, `pick color code`), not
  bare single words (`code`, `pick`).
- Always put a **space between emoji and word** or numbered lists may not parse.
- Lowercase keywords in ~50% of occurrences in short + full description — all-caps
  keys can slightly pessimize ranking (people search `bpm finder`, not `BPM
  Finder`).
- When counting a keyword's uses, also count it inside longer keywords (e.g.
  `incognito mode` counts inside `chrome incognito mode`).

See `references/listing-examples.md` for three full real descriptions that
passed CWS moderation and ranked well (Temp Phone Number, Youtube to Text,
Youtube repeat).

### Main vs Extra keywords — where each comes from

- **Main keywords** = everything from the Semrush **Broad Match** tab — the name
  keyword and its tails, *including* phrases where another word breaks the name
  (`convert pages file to word` for the name `convert pages to word`). How-to
  question keywords on-topic also go here.
- **Extra keywords** = the **Related** tab — phrases where a word is missing,
  changed to a synonym, or the whole phrase differs.
- A keyword differing by one letter / article / word form counts as a **separate
  keyword** — take both.
- **Never** take keywords about a *different* product even if they look similar
  (`pdf pages` when your product is `pages file to word`). Verify by opening the
  keyword's SERP — wrong-topic results mean wrong keyword.

### The iron rule — 8–10 name-keyword occurrences = no overspam

Using the name keyword **8–10 times** across the meta (name + short + full
description) **guarantees** no overspam. This is mandatory. Procedure: do the
maximum optimization (fill Main + Extra, weave everything in), then **trim
keywords from the *end* of the list** until overspam is gone. **Avoiding overspam
beats using every keyword.** If too few keywords exist, **do not shorten the
text** — just use the name more often.

### Keyword density per paragraph

Max **3** occurrences of the same keyword per paragraph in the first 1–2
paragraphs; **max 2** per paragraph after that. More than 3 close together = very
likely moderation rejection.

## 4. Spam check — turgenev.ashmanov.com

Spamminess = too-frequent repeats of the same words; Google pessimizes
over-spammed pages. Register at turgenev.ashmanov.com, paste name + short + full
description as one text, click check.

- Watch the **"повторы" (repeats)** score, the text window, and the repeats
  table with red flags. **Remove the red flags** — reduce each keyword's
  frequency to ≤3%.
- Reduce spamminess by **both** cutting keyword count **and lengthening the
  text** (if under 4,500 chars; add structured lists). Longer text lowers the
  per-word percentage.
- A small overspam (1–2 occurrences into the red) is tolerable — Google favors
  extensions in its own ecosystem — but don't allow heavy overspam.
- No more than 3 identical keywords standing close together in one paragraph.
  Above the CWS "read more" fold: ≤2–3 of the same keyword per text chunk; below
  the fold: 1–2 per chunk.
- **A purple/violet word in Turgenev = the same as red** — overspam, reduce it.
- **Ignore the site-only metrics** Turgenev shows — academic nausea (тошнота),
  word-combination nausea, linkbuilding. Those apply to websites; extensions are
  forgiven on them. Watch **only**: the repeats/red-flag column, overall risk
  (must be low/insignificant), and name words in the top (below).

## 5. Pessimization risk

In the same service, the left-sidebar **"общий риск пессимизации" (overall
pessimization risk)** must read **insignificant / low**. It drops once overspam
is removed.

## 6. Compare against competitors

If you have well-optimized competitors, check their text too and beat them on:
- **Length** — yours longer (aim 4,500 chars).
- **Structure** — more list types, emoji markers.
- **Keyword count + percentage** — higher than the competitor, *without* red
  flags. Use the keywords they use, then exceed their counts.
If a competitor isn't optimized, there's nothing to compare against — just get
clean Turgenev results and good optimization of your own.

## 7. Name-keyword saturation check

In Turgenev's **Words** and **Phrases** tabs, the words/phrases from your name
must be near the top (ignore grey "service words"). Turgenev sometimes swallows a
word (`temp`) or grey-marks a real word (`youtube`, `html`) — count those
manually. If name words aren't on top, redistribute their occurrences in the text.

- The **name keyword must rank top** — other phrases may be high but must stay
  *below* it.
- For a **multi-word name**, *each individual word* of the name should be in the
  top, and the 2-word combinations from the name should rank high too.

## 8. List structure (full description)

- Use **multiple list types**: numbered (1,2,3), dashes (-), bullet-points
  (➤ ▸ •), and 2–3 different emoji-marker styles. Always include at least one
  numbered list.
- **Within one list**, items should be roughly **equal length**; **across
  different lists**, vary the length (one list of short 2-word items, another of
  full-line items). Equal-length items help Google read it as a structured list.
- A list has **3–6 items** — not 2 (not a list), not 10.
- Within one list keep the **bullet type consistent** (all emoji, or all numbers).
- **Mix paragraphs and lists** — alternate them; never a wall of 10 paragraphs in
  a row.

## 9. Capitalization

- **Name** — written grammatically correct (proper case).
- **Short description** — some keyword occurrences lowercase.
- **Full description** — mix ~30% proper-case / ~70% lowercase (as people
  actually search). Search engines claim case doesn't matter; mixing observably
  works best.

## 10. Don't fake reviews or over-promise

- **Never write reviews inside the description** — moderation dislikes
  in-text "reviews"; remove them. Politely asking for a review at the very end
  is fine. Links to your other products/site are allowed but ~99% of users never
  read the description, so don't expect traffic from there.
- **Don't describe features that don't exist yet**, and never write "coming
  soon". Rewording the same real feature with different keywords is fine;
  inventing absent features risks moderation rejection.


## Case-study insights from product reviews

### Name — additions

- **Trademarked-looking compound names**: a two-word name made of two ordinary
  English words but with no natural meaning (e.g. "Content Keeper") is almost
  certainly a brand. The "ask a native speaker" test — if they can't immediately
  say what the product is, treat it as a trademark and skip, even with low KD
  and good traffic.
- **Sub-100 US searches is fine for tails** — 20 US searches becomes ~200
  across English-speaking countries and ~2,000 once translated. Don't reject
  low-volume keywords for the name if the longer tail is a clean fit.
- **English capitalization is a conversion lever.** Capitalize every content
  word in the `name` field per English title-case rules; lowercase only
  articles/prepositions/conjunctions; acronyms uppercase. Native speakers
  subconsciously distrust a name with bad case.
- **Two-word keyword in `name`**: only acceptable after ~10K users, usually
  skipped — it splits weight across two queries and the product ranks for
  neither.
- **Indian-skewed keyword is a bonus, not a blocker** — if US has enough
  volume to justify the keyword, larger volume in IN/SEA is upside (relevant
  for translation/promotion stages).

### Short description — additions

- **Fill close to 132 chars (~120–130)** even if the prose feels padded —
  extra symbols pull keywords apart and lower the same-paragraph trigger
  risk during moderation.
- **Don't separate keywords with only a comma.** Comma-chained keyword lists
  inside short or full description are the single most reliable moderation
  trigger. Insert a period and start a new sentence; do not chain
  "AI, Description, Generator, Tool".
- **Two adjacent occurrences of the main keyword in the short description is
  dangerous.** E.g. "AI ChatGPT Online" sitting beside "AI Text Generation"
  without separator words risks rejection. Push them apart with intermediate
  words.
- **The "3× main word + 2× per other word" formula is hard-capped.** Any
  single word used 4× in 132 chars is guaranteed overspam. Use 3× only for
  the single most important word; if another word also hits 3× (e.g. both
  `compress` and `png`), reduce one to 2×.
- **A morphologically varied third occurrence reads cleaner.** `Summarizer /
  Summarize / Summarized` counts as ~2.5× to moderation rather than three
  identical hits and noticeably reduces overspam risk while keeping SEO
  weight.

### Full description — keyword tactics

- **Mandatory 8–10 exact-form name occurrences is an ironclad floor.** When
  removing keywords to clear Turgenev overspam, never cut the name below 8 —
  sacrifice every other keyword first. If the niche has too few tails, repeat
  the bare name standalone until the count is met; do not shorten the text.
- **First two paragraphs may carry 3 keywords each**; from the third paragraph
  onward, strictly max 2 keywords per paragraph.
- **The CWS "Read more" fold matters for keyword weighting.** Text visible
  above the fold has higher SEO weight. Front-load 1–2 extra keyword
  occurrences in that visible portion (without spamming) and put a list /
  structured element above the fold rather than only paragraphs.
- **Prefer keywords that nest the name keyword.** A phrase like
  `text to speech reader app` simultaneously contributes to the name count
  AND occupies a tail-keyword slot — two SEO targets in one occurrence. Aim
  for at least half of Main Keywords to be name-nesting.
- **Semrush Phrase Match + Exact Match tabs** are where to find more name-
  containing tails when Broad Match is sparse. Order them inside Main —
  tails where the name is broken across words (e.g. `convert pages file to
  word` for name `convert pages to word`) belong in Main, not Extra.
- **Drop keywords with mismatched SERP.** Click each keyword through to
  Google SERP and verify top results match your product format. A keyword
  scoring well in Semrush but returning wrong-product SERP (e.g.
  `ai generator` returning only image generators when you ship a text
  generator) must be dropped or used ≤1×.
- **Adding one or two competitor brand keywords in the full description
  (not name, not short)** helps Google semantically cluster you with the
  leader and lift your ranking on your own keyword. Weave them naturally and
  sparingly, never comma-listed. Never include brands in name or short
  description.
- **Acronym / abbreviation niches** (`CPM Calculator`, `BPM`, `SMS Checker`):
  two case forms (e.g. `SMSChecker` and `SMS Checker`) count as **different**
  keywords — use both.
- **`free` rules**: never in name, ≤1× in short description, max 2–3× in
  full description. Otherwise Google clusters you with the bargain-hunter
  audience and behavioral signals collapse when you monetize.
- **`best`, `recommended`, `premium`, `#1`** are hard moderation blockers
  anywhere in meta.
- **Zipf's-law check** (why name-words must be top in Turgenev): human-
  written text has a sharply skewed word frequency. If your name keywords
  are NOT visibly spiking above the baseline in Turgenev's word/phrase tabs,
  Google's LLM/AI-text detector pessimizes you. Hand-count words Turgenev
  silently treats as service words (`HTML`, `youtube`, `temp`) — they still
  need to be top.
- **Multi-word name top-check.** Each individual word AND each 2-word
  combination from the name must be top in their respective Turgenev tabs.
  Turgenev compares phrases only within the same word-count bucket — 3-word
  phrases never compete with 2-word phrases.

### Full description — structure

- **List items must be ≤1 line each.** If any item exceeds one line, it
  stops being a list to Google's parser and degrades to a paragraph.
  Consistency within one list outranks visual variety.
- **Don't bullet-mark items with emoji AFTER the list-item text** — emojis
  at end of a line read as decoration to Google's parser and risk being
  scored as robotic / spam ornamentation. Emoji prefixes only.
- **Always a space between emoji and text** (some parsers fail to tokenize
  the list otherwise).
- **Lead-emoji within one list must be identical** — varying emoji inside
  one list destroys the "structured content" signal. Use different emoji
  types only between separate lists.
- **Headers above lists must be separated by exactly ONE empty line** —
  never tabs, never indent. The only allowed formatting in CWS is `\n` and
  `\n\n`. Strip anything ChatGPT adds.
- **Single-word column lists** (especially brand or format lists like
  `JPG / PNG / GIF`) are a strong moderation trigger even when accurate to
  your product. Distribute these terms inline across paragraphs.
- **Lists of ≤2 items don't count as lists;** 5–6 items is the upper bound.
  Don't make the whole description one big list.
- **Alternate paragraphs and lists.** Never stack >3 paragraphs in a row or
  >2 lists in a row. Walls of paragraphs are the #1 robotic-text signal
  Google catches.
- **Vary list lengths between lists** (one of 2-word items, one of half-line
  items, one of full-line items) but keep length consistent within each
  list. Uniform within = "structured"; varied across = "human".
- **Description length is hard-coupled to the keyword formula.** 4,500
  chars (with spaces) is the bench. ≥4,700 forces more absolute keyword
  occurrences to maintain proportion, which the moderator threshold rejects.
  ≤4,300 has insufficient keyword density. The new Turgenev counter shows
  *non-space* chars — always read the WITH-space number.
- **Never write fake / anonymous reviews in the description text** —
  reviews-inside-description is a fast moderation flag. Asking for a
  review at the very end is fine; quoting reviews is not.
- **Don't describe features that don't exist yet** and never write
  "coming soon" — moderation occasionally cross-checks claims vs the
  running UI and rejects.

### Turgenev specifics — additions

- **Always paste name + short + full description together** into Turgenev —
  they sit on the same CWS page and Google indexes them jointly. Submitting
  only the full description gives misleading proportions.
- (Already covered: purple = red; ignore academic nausea / linkbuilding;
  Turgenev swallows service-marked words like `temp`, `youtube`, `html`.)


## Backfilled sections (transcript-grounded)

The sections below were added to close methodology gaps. Each cites the
bootcamp source so a future reader can verify. Where the bootcamp does not
cover a topic, the section is marked `TODO — not in transcripts`.

### Worked name-occurrence audit table — Temp Phone Number

> Source: Module II lesson 056 (`Примеры хороших описаний`) — full text of the
> approved description. Counts done by hand against the published text.

The name `Temp Phone Number` is a 3-word name. The most important standalone
word for Google is `phone` (the head noun); `number` is a close second; `temp`
is the qualifier. Below is where the **exact phrase `temp phone number`** (or
its 2-word substring `phone number`) appears, mapped to block.

| Block | Exact `temp phone number` | `phone number` (2-word) | `temp` standalone | `phone` standalone |
|---|---|---|---|---|
| Name | 1 | (overlaps) | (overlaps) | (overlaps) |
| Short description | 1 | (overlaps) | (overlaps) | (overlaps) |
| Paragraph 1 (header `🛡️ Temp phone number…`) | 2 | (overlaps) | (overlaps) | (overlaps) |
| Paragraph 1 body | 0 | 1 (`disposable phone numbers`) | 0 | 1 (`personal contacts… phone`) |
| Section 2 `🌟 Instant privacy with disposable numbers` (3 bullets) | 0 | 1 (`disposable phone numbers`) | 0 | 0 |
| Section 3 `📲 Instant connect` | 0 | 0 | 0 | 0 |
| Section 4 `🌐 Unlimited global reach` (3 bullets) | 0 | 0 | 0 | 2 (`country-specific phones`, `phone options`) |
| Section 5 `💎 Innovative & user-centric design` | 0 | 0 | 0 | 1 (`disposable phones provider`) |
| Section 6 `🔒 Robust security protocols` | 0 | 0 | 0 | 0 |
| Section 7 `🔄 Dynamic allocation` | 0 | 1 (`Phone numbers are refreshed`) | 0 | 1 (`most reliable phones`) |
| Section 8 `📈 Analytics and insights` | 0 | 0 | 0 | 0 |
| Section 9 `📑 Transparent usage policies` | 0 | 0 | 0 | 0 |
| Section 10 `🌍 Cultural and linguistic support` | 0 | 0 | 0 | 0 |
| Section 11 `🔝 Enhanced user experience` | 0 | 0 | 0 | 0 |
| Section 12 `👥 Growth through community` | 0 | 0 | 0 | 0 |
| Section 13 `🚀 Exclusive perks` | 0 | 1 (`free second phone numbers`) | 0 | 0 |
| Closing line | 0 | 0 | 0 | 0 |
| FAQ Q1 `How does the app protect…` | 0 | 0 | 0 | 0 |
| FAQ A1 | 0 | 0 | 0 | 0 |
| FAQ Q2 `Can I use multiple numbers…` | 0 | 0 | 0 | 0 |
| FAQ Q3 `What benefits do additional phone contacts offer?` | 0 | 0 | 0 | 1 (`primary contact phone`) |
| FAQ A3 | 0 | 0 | 0 | 0 |
| FAQ Q4 `Is this service really free?` | 0 | 0 | 0 | 0 |
| FAQ Q5 `How long can I use a temporary phone?` | 0 | 0 | 0 | 1 (`temporary phone`) |
| FAQ Q6 `Can I select a contact…` | 0 | 0 | 0 | 0 |
| FAQ Q7 `Are messages private and secure?` | 0 | 0 | 0 | 0 |
| **Totals** | **4** exact | **+4** as `phone number` | **0** standalone (`temp` is in the brand only) | **+7** standalone `phone` |

Read it this way: the **exact 3-word name** lands 4 times (name, short, two in
paragraph 1 header + lead). The **head 2-word substring `phone number`** picks
up 4 more, giving an exact + substring total of **8** — exactly at the floor
of the 8–10 rule when counted as the customer would search. The standalone
word `phone` adds 7 more in tail phrases (`country-specific phones`, `most
reliable phones`, `temporary phone`) — these reinforce the head noun without
re-triggering Turgenev overspam on the full phrase.

Notes:

- The qualifier `temp` is silently treated as a service word by Turgenev
  (Module II lesson 060 confirms `temp` gets swallowed). Hand-count it.
- The FAQ block is very light on the exact name — only one occurrence
  (`temporary phone` in Q5, and `primary contact phone` in Q3 which is not
  the keyword). The FAQ pulls its weight via the **synonym belt**
  (`temporary`, `contacts`, `phones`) rather than the head keyword.
- Paragraph 1 is where the name keyword density is concentrated (2 exact +
  surrounding `disposable phone numbers`) — this matches the Module II
  lesson 057 + lesson 079 rule that the visible-above-fold text gets higher
  SEO weight.

### Turgenev "Words tab" service-word list

> Source: Module II lesson 060 (`Проверяем наполненность текста ключом из
> названия`) + video 092 (`Нюанс 7 поднимаем концентрацию слов из названия в
> Тургеневе`) + video 103 (`Нюанс 18 особенности цветовой разметки`).

Turgenev's Words tab marks some tokens grey ("service words") and excludes
them from the top-frequency view. The bootcamp never publishes a master
list — it explicitly says Turgenev is unpredictable and you must
**hand-check** every name token. Confirmed examples from the transcripts:

| Token | Behavior | Source |
|---|---|---|
| `temp` | Swallowed (not shown at all in Words tab) | Lesson 060 |
| `youtube` | Marked grey (counted as service word) | Lesson 060 |
| `html` | Marked grey (counted as service word) | Video 092 |

Standard English stop-words (`a`, `the`, `of`, `to`, `for`, `with`, `and`,
`or`, `in`, `on`, `at`) are also greyed out — this is normal stop-word
filtering and not the problem the bootcamp flags. The problem is when a
**content-bearing** name token (a brand fragment, a product noun, a
technology acronym) gets dropped into the service-word bucket.

> TODO — not in transcripts — the bootcamp gives only the three examples
> above. A future operator should grow this table from first-hand Turgenev
> runs (likely candidates: other short brand tokens, common file-format
> tokens like `pdf`, `png`, `gif`, common platform tokens like `gmail`,
> `chatgpt`).

Procedure when a name token is greyed/swallowed: do **not** trust
Turgenev's "name word is top" check for that token. Open the text view,
manually count occurrences, and confirm the token's frequency is at the
level you'd expect (i.e. it should still spike above prose-baseline once
you count it yourself).

### FAQ block keyword density

> Source: lessons 055, 056, 057 (`Создаем полное описание`, `Примеры
> хороших описаний`, `Проверяем тексты на спам`). The bootcamp does **not**
> give an FAQ-specific keyword-density rule.

What the transcripts do say:

- FAQs are explicitly listed as one of the allowed structural list types
  (lesson 055 — `вопрос-ответ` in the checklist).
- The general per-paragraph density rule (max 3 keys per paragraph in
  first two paragraphs, max 2 per paragraph thereafter — lesson 057 +
  video 103) applies to **every** paragraph including FAQ Q and FAQ A
  paragraphs.
- The FAQ block sits **below** the CWS "Read more" fold (video 079 confirms
  the fold sits after the first paragraph or two), so it falls under the
  stricter ≤1–2 same-key-per-chunk rule for below-fold text (lesson 057).

The Temp Phone Number example above is the empirical answer: across 7 FAQ
Q+A pairs (~14 paragraphs), the exact name keyword `temp phone number`
appears 0 times; the head 2-word `phone number` appears 0 times; the
standalone `phone` appears 2 times. **FAQ blocks deliberately under-use
the head keyword** and lean on the synonym belt (`disposable`,
`temporary`, `contact`, `verification`) instead. This keeps below-fold
density low while still feeding question-tail keywords.

Operational sub-rule:
- FAQ Q: ≤1 occurrence of the head keyword per question, and only in
  ~30% of the questions. Most questions should ask about
  *adjacent* concepts (privacy, install, supported platforms,
  troubleshooting) so the question text itself reads naturally.
- FAQ A: ≤1 occurrence of the head keyword per answer, same ~30%
  coverage. Use synonyms / tail variants in the rest.

### CWS "above-the-fold" boundary — character count

> TODO — not pinned in transcripts — the bootcamp tells you the fold exists
> (lesson 057 + video 079: "часть текста она видна сразу, часть текста под
> спойлером") and that above-fold text carries more SEO weight, but it
> never publishes the exact character count at which CWS truncates the
> short-description card. The bootcamp shows screenshots of the fold
> position rather than naming a count.

What is true per transcripts:
- The fold is in the **full description** body on the CWS detail page —
  video 079 says "до спойлера он виден" and treats it as a visual cutoff,
  not a fixed char count.
- Behavior above fold: max 3 same-key occurrences per chunk (lesson 057).
- Behavior below fold: max 1–2 same-key occurrences per chunk
  (lesson 057).
- The first 1–2 paragraphs should carry the highest keyword density and a
  structural element (list) above the fold (video 079).

The figure `~600 chars` that appears elsewhere in this skill is not
confirmed by the bootcamp. A future operator should measure on a live
CWS listing (open three live products at standard zoom, count the chars
to the "Read more" link) and replace the figure here. Until then, use
**"first 1–2 paragraphs"** as the operating heuristic rather than a char
count.

### Morphologically varied third occurrence — qualitative only

> Source: video 079 (`Разборы ошибок ЧАСТЬ 1`) — the only mention of
> cognate forms in moderation.

The transcript text:

> вопрос читается ли при модерации однокоренные слова за одно и то же
> пример юрейл шортоннер гугл основное писание юрейл шортоннер гугл это
> допускается да если мы берем прокатка описание вот если мы видим речь
> прокатка описание то формы мы считаем

Translation: "Question: does moderation read cognates as the same word?
Example: `URL Shortener Google` in main description — `URL Shortener
Google` — this is allowed, yes; if we look at the short description,
when we see speech in short description we count forms…"

The bootcamp confirms cognates are **allowed** and treated as the same
word for moderation, but **never quantifies** them. The "~2.5× weighting"
heuristic that appears in the case-study insights above is a
post-bootcamp folk rule, not from the transcripts.

**Downgrade the rule** to: a morphologically varied third occurrence
(`Summarize / Summarizer / Summarized`) reads as cleaner human prose and
softens Turgenev's repeat scoring vs three identical hits. Do not treat
it as ~2.5× math — that number is not in the bootcamp.

### Translation count-preservation across locales

> Source: Module III lesson 124 (`Создаем автоматический перевод`),
> lesson 125 (`Переводим название, краткое и полное описание в
> Localizer`), lesson 127 (`Переводим название и описание расширения на
> важные языки вручную`), and video 166 (`Нюанс 16 обрезка кратких
> описаний при автопереводе`).

What happens to keyword counts during Localizer auto-translation:

1. **Full description** auto-translation via Localizer runs through
   ChatGPT (or DeepL/Google for languages where OpenAI has problems —
   Localizer flags those with 🚨). The transcripts do **not** quantify
   keyword-count preservation. They do say (lesson 124): "перевод на
   другие языки позволит увеличить шансы продвижения в выдаче Google в
   несколько раз" — the goal is reach, not count parity.

2. **Short description (132 char limit)** is the documented failure point.
   Video 166 confirms: ChatGPT-5 is poor at honoring the 132-char limit
   during translation. Two failure modes:
   - Prompted with the limit → translation comes back **too short**,
     dropping keywords.
   - Prompted without the limit → translation comes back **over 132
     chars**, getting truncated on upload (final keywords cut off).

   The bootcamp's explicit policy:
   > "по другим языкам гораздо меньше конкуренция, чем английском" —
   > non-English competition is much lower, so even truncated short
   > descriptions still beat skipping translation entirely.

3. **Name** auto-translation is the same risk on a 75-char field. The
   bootcamp recommends (lesson 127) **hand-translating** names + short
   descriptions for the high-value languages:
   - **Wealthy-country list (latinise-friendly)**: DE, FR, ES, IT, NL,
     SV, DA, NO, FI — translate name + short description manually.
   - **Large-audience list**: AR, ID, RU, PT, JA, FIL, VI, TR, TH, KO —
     at minimum manually translate the **top 3** (AR, ID, RU).

   For these languages, manually verify the keyword count formula
   survives (3× main word in short, 8–10× name in full).

4. **Full description in other languages** can stay auto-translated. The
   transcript explicitly says (lesson 127): "над названием
   заморачиваемся, над кратким описанием – поменьше, а полное описание
   просим перевести через ChatGPT c английского" — fuss over the name,
   fuss less over short, just ask ChatGPT to translate full from English.

Operating rule:

| Field | EN keyword count target | Auto-translate? | Re-verify count? |
|---|---|---|---|
| `name` | 1× (the keyword) | No — handcraft per language for top markets | Yes |
| `description` (short, 132) | 3× main + 2× supporting | Auto, accept truncation OR handcraft for top markets | Handcraft path: yes; auto: skip — competition is lower |
| Full description | 8–10× name + ~30 total keys | Auto via Localizer | Skip per-language — bootcamp does not require it |

> TODO — not in transcripts — no per-language Turgenev re-check is
> documented. A future operator may want to run Turgenev (or a local
> equivalent) on the top 3 non-English locales for the head keyword to
> confirm no overspam was introduced by translation.
