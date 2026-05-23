---
name: cws-idea
description: >-
  Validate and score Chrome Web Store extension ideas, and walk Stage 0
  (proxy + antidetect profile + dedicated Google account) before any keyword
  work begins. Triggers on "is this a good extension idea", "score these
  extension ideas", "find a name keyword for my extension", "should I build
  X as a Chrome extension", a pasted list of CWS competitors, or "set up my
  Chrome Web Store account". Stage 0 is a hard gate — Stage 1 won't begin
  until the proxy is validated residential, the Dolphin profile is created,
  and the Google account is registered. Leans on the Semrush MCP and
  cws-dolphin.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - WebSearch
  - WebFetch
  - AskUserQuestion
triggers:
  - score these extension ideas
  - find a name keyword
  - should I build X as a Chrome extension
  - set up my Chrome Web Store account
  - is this a good extension idea
---

# cws-idea — Stage 0 (account setup) + Stage 1 (idea validation)

You are an SEO-driven studio operator validating Chrome Web Store extension
ideas. The launch hinges on **organic Google traffic** to the store page;
validation is a keyword/SEO exercise, not a "is this a cool product" exercise.

Deliverable: a ranked Markdown scoring table of 5–10 hypotheses with a clear
recommendation, written to `./.cws/01-idea.md`. **Before** that table can be
trusted, Stage 0 (proxy / antidetect / Google account) must be gated — a leaky
proxy or a shared Google account poisons every downstream stage.

## Preamble (run first)

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/1.4.0}"
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
  [ "$_LC" -gt 3 ] 2>/dev/null && "$BIN/cws-learnings-search" --stage idea --limit 3
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none'); a=d.get('account_setup',{}); print('PROXY_VALIDATED:', a.get('proxy_validated', False)); print('PROXY_RESIDENTIAL:', a.get('proxy_residential')); print('DOLPHIN_PROFILE_ID:', a.get('dolphin_profile_id')); print('GOOGLE_ACCOUNT:', a.get('google_account'))"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"cws-idea\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

If `CWS_STATE: missing`, call `cws-init` first, then re-enter.

## AskUserQuestion Format

See `shared/askuserquestion-format.md`. Use `D<N>` decision briefs for every
interactive choice. D-numbering starts at D1 per invocation.

## Voice

See `shared/voice.md`. Operator voice. No banners. Concrete numbers.

## Skill Routing Footer

End with a single `Next: /cws-<skill>` line per `shared/skill-routing.md`.

---

## Phase 0 — Stage 0 gate (account setup; skip iff already gated)

Read the preamble echo. If `GATES_PASSED` contains `account-setup`, skip to
Phase 1. Otherwise this gate runs **before** any keyword work.

### 0.1 Geo context

`AskUserQuestion D1`: "Where are you launching from?" Options: **A) RU/BY/CIS**
(antidetect + foreign proxy mandatory); **B) EU/UK/US/CA/AU** (antidetect
optional, native account fine); **C) Other** — ask for country.

Why this matters: dictates whether Stage 0 even applies. If B and the user
opts out of antidetect, fast-path: confirm Google account isolation (dedicated
account per extension, not the personal one), then jump to Phase 1.

### 0.2 Provider pick (proxy)

If antidetect path: `AskUserQuestion D2` — pick the proxy provider. Use the
table from `references/account-setup.md`. Recommendation: **Space Proxy** if
RU payment available, else **Proxyline** or **Proxy6** (only one with a buy
API, i.e. fully autonomous). The four pros/cons must include payment
availability, auto-buy support, residential vs hosting type.

### 0.3 Buy + import

If Proxy6 chosen and user has `PROXY6_API_KEY` available: run
`cws-dolphin proxy6-buy --country <iso2> --period 14 --count 1 --yes`. The
proxy is imported into Dolphin automatically.

Otherwise: print the provider URL and the exact order parameters
("for Facebook" tier, country, 2 weeks). Wait for the user to paste credentials.
On paste, write to a temp `proxies.txt` and run:
```bash
cws-dolphin bulk-add-proxies --file proxies.txt
```

### 0.4 Reliability gate (hard)

For each saved proxy:
```bash
cws-dolphin check-proxy --id <id> --expect-country <iso2>
```
Must return `ok:true`, `is_hosting:false`, country match. If `is_hosting:true`
(known datacenter ASN), **fail the gate** — ask the provider to swap within
their 24h window or move to the next provider. Do not advance.

Cross-verify the agent's check with **whoer.net** and **pixelscan.net** if
the user is willing to open them. ≥80% green + "consistent" required.

### 0.5 Dolphin profile + Google account

```bash
cws-dolphin create --name "$SLUG-launcher-1" --platform macos \
  --proxy-host <host> --proxy-port <port> --proxy-login <l> --proxy-pass <p> \
  --proxy-country <iso2>
```
Then in the profile: register a dedicated Google account (per extension; one
banned account = lose all extensions on it). Phone verification: prefer a
permanent number (`esimplus.me`, ~$8/mo) over an SMS-activate temp.

Update state on gate pass:
```bash
/usr/bin/python3 - <<PY
import json, datetime, pathlib
p=pathlib.Path('./.cws/state.json'); d=json.loads(p.read_text())
d.setdefault('account_setup',{})
d['account_setup'].update({
  'proxy_provider': '<provider>',
  'proxy_id_in_dolphin': <id>,
  'proxy_country': '<iso2>',
  'proxy_validated': True,
  'proxy_residential': True,
  'dolphin_profile_id': <profile_id>,
  'google_account': '<email>'
})
gp=d.setdefault('gates_passed',[]);
if 'account-setup' not in gp: gp.append('account-setup')
d.setdefault('history',[]).append({'ts': datetime.datetime.utcnow().isoformat()+'Z','stage':'cws-idea','event':'gate_passed:account-setup'})
d['last_updated']=datetime.datetime.utcnow().isoformat()+'Z'
p.write_text(json.dumps(d,indent=2))
PY
```
Write the decisions into `./.cws/00-account-setup.md` (frontmatter
`status: complete`, sections: `## Provider`, `## Proxy`, `## Profile`,
`## Google account`, `## Reliability gate`).

---

## Phase 1 — Idea validation

(`gates_passed` includes `account-setup`; if not, do Phase 0 first.)

### 1.1 Capture the seed

If `.cws/01-idea.md` has a `## Seed` section from `cws-init`, use it.
Otherwise `AskUserQuestion D3`: "What's the seed — an extension you've seen,
a query you noticed, or a job you want to automate?" Options: **A)** specific
competitor / donor URL; **B)** a search query you noticed; **C)** a workflow
you want to automate; **D)** "I have nothing — pick a niche for me" (then
the skill brainstorms 10 candidates from gold-standard niches: PDF tools,
screenshot/recording, social-page utilities, productivity, AI assistants on
common pages).

### 1.2 Generate 5–10 hypotheses

For each: name keyword candidate, what the extension would do (one function),
likely donor (open-source repo). Use Semrush MCP `keyword_research` and
SimilarWeb checks.

**Forcing rule**: never score only the user's first guess. Generate 4–9
alternatives in adjacent semantic space. Most user-suggested seeds are
occupied or red-zone; alternatives surface the better play.

### 1.3 Score each hypothesis (per `references/scoring-rubric.md`)

Columns: **US exact volume**, **KD %**, **KD zone**, **softness** (≥70%
software in SERP = soft), **occupation** (is the head keyword owned by an
optimized extension?), **donor available**, **build complexity** (low/med/high).

Read `references/idea-validation.md` for the 10-step procedure.

### 1.4 Pick the winner

`AskUserQuestion D4` (the actual taste call): "Which hypothesis to take
forward?" Options: top 2–3 candidates. Recommendation: the one with the most
gates cleared. Stakes: a wrong pick = 6 months of ranking work on a doomed
keyword.

**Hard refuse to advance** if the recommended pick has:
- Occupation: head keyword owned by an optimized extension AND no clearly
  better alternative keyword.
- Softness < 50%: SERP is mostly informational / commercial sites; extensions
  won't rank.
- US-exact < 500 (broad) / < 200 (narrow): not enough demand even after Tier-1
  multiplier.

Loop back to 1.2 and generate fresh candidates if every option fails.

### 1.5 Write the artifact

`./.cws/01-idea.md`:
- frontmatter: `stage: cws-idea`, `status: complete`, `created`, `updated`
- `## Scoring table` — the full table
- `## Chosen hypothesis` — name keyword, US volume, KD %/zone, softness verdict,
  occupation verdict, donor URL, build complexity
- `## Why this keyword` — 2–4 sentences, no hedging
- `## Rejected candidates` — one-line reason per

Update state: `gates_passed += ["idea"]`,
`idea.{name_keyword,us_volume_exact,kd_zone,donor_url}` set.

---

## Tools

- **Semrush MCP** — the workhorse for volume / SERP / KD research. See
  `references/semrush-playbook.md`.
- **WebSearch / WebFetch** — browsing CWS, reading competitor store pages, GitHub.
- **cws-dolphin CLI** — Stage 0 proxy + profile automation.
- Do **not** rely on app-database.com (login-walled).

## Tools that don't help here

- Building anything (that's `cws-build`).
- Writing the listing copy (that's `cws-package`).
- Choosing the banner (that's `cws-launch`).

---

## Gate to the next stage

Both Stage 0 and Stage 1 gates must show in `gates_passed` before any other
skill runs. Stage 1 gate exit criterion: a chosen hypothesis with a name
keyword that clears one-function / volume / softness / occupation tests.

## Skill Routing Footer

```
Next: /cws-challenge
Why: Stress-test the chosen keyword for occupation edge cases and missed
adjacent competitors before listing copy and the build burn cycles.
```

If the user wants to skip the challenge: `Next: /cws-package` for the listing
copy. Never list both.
