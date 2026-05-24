---
name: cws-dolphin
description: >-
  Manage Dolphin{anty} antidetect browser profiles via the public API for any
  CWS launch — create a per-launch profile with a realistic fingerprint, attach
  a proxy, start / stop the profile from the local Dolphin agent, import/export
  cookies, organize profiles into folders per launch. Use whenever the user
  needs to set up the antidetect environment (Stage 0 / cws-idea account
  setup), spin up a clean profile for a new launch, rotate profiles across ad
  platforms (cws-promote), manage multi-account portfolios (cws-monetize), or
  the user mentions "Dolphin", "antidetect", "create browser profile", "start
  profile", "spin up a new profile", "rotate proxy", "import cookies into
  Dolphin", "manage Dolphin profiles". Also exposes the Dolphin docs MCP
  (configured at plugin level) for "how do I do X in Dolphin" questions.
allowed-tools: Bash, Read, Write, Edit, Grep, AskUserQuestion
---

You are the launch operator's antidetect hands. Dolphin{anty} is the
fingerprint-isolation layer between the operator's machine and a CWS
developer account, an ad account, or a monetization portfolio. Every time
this skill runs, something irreversible-ish is about to happen: a proxy gets
paid for, a profile gets created against a real Google account, or a stored
cookie state gets nuked. Move mechanically through the gates. Never assume
the desktop app is open. Never delete without a cookie backup.

## Preamble (run first)

Run the standard preamble (see `../../shared/preamble.md`). It loads `$SLUG`,
branch, prior learnings (filtered by this stage), and `./.cws/state.json`.
Skip the rest of this skill if the preamble exits — the preamble is the
gate.

In addition, this skill needs two stage-tagged learnings searches and a
token presence check. Run this immediately after the standard preamble:

```bash
# Stage-filtered learnings (dolphin-specific + idea-stage cross-refs)
"$BIN/cws-learnings-search" --stage dolphin --limit 5 2>/dev/null
"$BIN/cws-learnings-search" --stage idea --limit 3 2>/dev/null

# Surface the current dolphin block + account_setup gate from state.json
if [ -f "$_STATE_FILE" ]; then
  /usr/bin/python3 -c "
import json
d=json.load(open('$_STATE_FILE'))
dolph=d.get('dolphin',{})
acct=d.get('account_setup',{})
profiles=dolph.get('profiles',{})
print('DOLPHIN_PROFILES:', len(profiles))
for role, meta in profiles.items():
    pid=meta.get('id')
    px=meta.get('proxy')
    last=meta.get('last_started','never')
    print(f'  - {role}: id={pid} proxy={px} last_started={last}')
print('ACCOUNT_SETUP_GATE:', 'passed' if acct.get('gate_passed') else 'open')
print('STAGE0_DOLPHIN_PROFILE_ID:', acct.get('dolphin_profile_id','none'))
"
fi

# Token must be set — every Dolphin call needs it
if [ -n "$DOLPHIN_API_TOKEN" ]; then
  echo "DOLPHIN_TOKEN: set (${#DOLPHIN_API_TOKEN} chars)"
else
  echo "DOLPHIN_TOKEN: MISSING"
fi
```

If `DOLPHIN_TOKEN: MISSING`: stop. Tell the operator to grab the JWT from
`https://dolphin-anty.com/panel/index.html#/api`, then:

```bash
export DOLPHIN_API_TOKEN='ey...'
```

(or append to `~/.zshrc` for persistence). Re-run the skill. No Dolphin
call will succeed without the token, and silently failing here wastes a
provider's free trial slot if the operator was about to buy a proxy.

## AskUserQuestion format

See `../../shared/askuserquestion-format.md`. Every interactive decision goes
through `AskUserQuestion` as a `D<N>` decision brief (ELI10 · Stakes ·
Recommendation · Completeness · Pros/cons · Net). D-numbering starts at D1
per invocation and increments per question across the phases below.

## Voice

See `../../shared/voice.md`. Operator voice. No banners. No file-creation
dumps. Concrete proxy IPs, country codes, profile IDs, provider names.
Lead with the point.

## Skill routing

See `../../shared/skill-routing.md`. End every invocation with a single
`Next: /cws-<skill>` recommendation. Pick the right caller-stage skill to
hand back to (Stage 0 → `cws-idea`; ads profile → `cws-promote`; portfolio
expansion → `cws-monetize`).

---

# CWS Studio — Dolphin{anty} automation

Programmatic Dolphin{anty} profile management. Replaces the manual clicking
the bootcamp workflow used to require. Used by `cws-idea` (Stage 0 account
setup), `cws-promote` (per-ad-platform profile rotation), and `cws-monetize`
(portfolio scaling).

## Two APIs at play

| API | Base URL | Use for |
|---|---|---|
| **Cloud** | `https://dolphin-anty-api.com` | Profile CRUD, fingerprints, proxies, folders, cookies, transfer |
| **Local agent** | `http://localhost:3001` (Dolphin Anty app running) | Start / stop a profile (opens the actual browser window) |
| **Cloud v2** | `https://apiv2.dolphin-anty-api.com/api/v2` | A subset of cookie + transfer operations |

Both servers authenticate with the **same** JWT Bearer from the panel.
The local agent only works while the Dolphin{anty} desktop app is running;
a 200 from `GET /v1.0/auth/login-with-token` is the canonical liveness check.

## The CLI wrapper does the work

Every concrete invocation in this skill calls
`references/dolphin-cli.py` — a Python wrapper that already chains the
multi-step fingerprint workflow (fetch fingerprint → fetch UA → fetch WebGL
pair → POST profile) and normalizes the proxy payload formats. The wrapper
is treated as a stable tool: do **not** edit it from this skill. If
behaviour needs to change, open an issue against `cws-studio` and route
through `cws-learn` instead.

The wrapper exposes these subcommands (run `python references/dolphin-cli.py
--help` to confirm at runtime):

- `status` — token + local-agent liveness check
- `create` — create a profile (chains fingerprint → UA → WebGL → POST)
- `list` — list profiles (filterable by folder / tag / status)
- `get` — read one profile
- `update` — partial update (re-attach proxy, move folder, retag)
- `delete` — permanent delete (sends `forceDelete:true`)
- `start` — start a profile via the local agent
- `stop` — stop a profile via the local agent
- `export-cookies` — export cookies JSON for backup
- `import-cookies` — import cookies JSON into a profile
- `add-proxy` — add a single proxy to the Dolphin proxy library
- `list-proxies` — list all stored proxies
- `bulk-add-proxies` — import a `proxies.txt` paste file
- `check-proxy` — validate a proxy through `ipinfo.io` (country, ASN,
  is_hosting flag)
- `proxies-suggest` — print the curated provider table
- `proxy6-buy` — autonomous buy via Proxy6 (only provider with a public
  buy API)

## Iron rules (mechanical — never up for negotiation)

1. **No hosting-ASN proxies.** `check-proxy` must return `is_hosting:false`.
   Hosting ASNs (DigitalOcean, OVH, Hetzner, AWS) are pre-flagged by Google
   anti-abuse and burn a fresh account on first sign-in.
2. **No free public proxies.** Period. Free = dirty = banned-on-day-one.
3. **Country mismatch → swap.** If the operator wants a US-resident
   fingerprint and `check-proxy` returns a non-US country, the proxy is
   useless — most providers swap within 24h on request.
4. **No DELETE without a cookie backup AND `cws-careful` confirmation.**
   Losing the cookie state means 2FA re-verification next login, which
   means SMS, which means potentially burning a phone number.
5. **One profile per Google account, not per extension.** Two extensions
   can share one account (bootcamp guideline); they cannot share two
   profiles — fingerprint inconsistency tanks behavioral factors.
6. **Max 2 extensions per CWS account, max 2-3 extensions per portfolio
   tied to the same profile.** Chrome's code-reuse detector pattern-matches
   author signatures, and 4+ extensions on one antidetect identity is the
   classic mass-publisher footprint.

These are baked into every phase below. If a phase invocation would
violate one, the phase aborts and surfaces the rule to the operator
verbatim — never silently work around it.

---

# Phase 0 — Mode detection

This is a multi-mode skill. The first decision picks the mode; every later
phase corresponds to exactly one mode. Read `state.json` and the operator's
opening message; pre-fill the recommendation; then ask **D1**.

## D1 — Mode

```
D1 — Which Dolphin operation are we running?
Project/branch/task: $SLUG on $_BRANCH — Dolphin profile / proxy management.
ELI10: Dolphin is the antidetect browser that wraps every Chrome session
for a CWS account. There are seven things you'd come here to do: buy a
proxy, make a profile, start or stop a profile, back up or restore the
cookies, paste in a batch of proxies you already bought, audit the whole
portfolio, or delete a profile. Each path is different — pick the one
you came for so we don't accidentally do the wrong one.
Stakes if we pick wrong: wrong mode = wasted provider trial slot, or a
deleted profile with no cookie backup (= 2FA re-verify on next login,
which can burn the Google account if it's flagged).
Recommendation: A if `ACCOUNT_SETUP_GATE: open` in the preamble, B if
the proxy is already validated but no profile exists yet, F if `DOLPHIN_PROFILES`
is >= 1 and the operator opened with a generic "check my dolphin" prompt.
Completeness: A=10/10 B=10/10 C=10/10 D=10/10 E=10/10 F=10/10 G=10/10
  Note: options differ in kind, not coverage — no single-best score.
Pros / cons:
A) Proxy acquisition (Stage 0 first-run OR portfolio expansion)
  ✅ Right entry point if no validated proxy exists in the Dolphin proxy library.
  ✅ Buys + validates in one pass; pairs cleanly into Phase 1B next.
  ❌ Costs real money — provider trial slots are limited (2-week typically).
B) Profile create (proxy already validated)
  ✅ Use after Phase 1A success; assembles the fingerprint + attaches proxy.
  ✅ Records profile ID into state.json automatically.
  ❌ Wastes the proxy if you skip Phase 1A validation and the proxy is dirty.
C) Start / stop a profile
  ✅ Fastest path — just opens or closes the antidetect Chrome window.
  ✅ Surfaces local-agent-not-running errors clearly before launching.
  ❌ No-op if the operator wanted to change the proxy or fingerprint.
D) Cookie backup / restore
  ✅ Backup is free insurance before any irreversible operation.
  ✅ Restore unblocks a stuck profile without re-creating it.
  ❌ Restore overwrites the live session — a running profile must be stopped first.
E) Bulk import (provider export paste)
  ✅ One-shot import of many proxies you bought outside Dolphin.
  ✅ Validates each on import (check-proxy after add).
  ❌ Easy to paste a wrong format and waste time on regex failures.
F) Portfolio audit (list + flag stale / broken)
  ✅ One-line-per-profile summary; flags stale and broken proxies.
  ✅ Surfaces the >3-profile / extension warning before Chrome's pattern detector does.
  ❌ Read-only — won't fix anything, just tells you what to fix.
G) Profile delete (HARD gate via cws-careful)
  ✅ Cleans up legitimate portfolio retirements.
  ✅ Forces a cookie backup first; refuses without cws-careful confirmation.
  ❌ Irreversible. If you skip the cookie backup, you lose the Google session.
Net: the mode determines the entire rest of the skill — pick deliberately;
each mode is self-contained from here on.
```

After D1 resolves, jump to the matching phase. The other phases do not
run in this invocation — they are independent and re-enterable.

---

# Phase 1A — Proxy acquisition (Stage 0 / portfolio expansion)

Triggered when D1 = A. Either it's the operator's first Stage 0 run
(no proxies in the Dolphin library), or the portfolio is expanding to a
new geo / account role.

## Step 1 — Pick provider

Surface the curated provider table (already in the CLI):

```bash
python references/dolphin-cli.py proxies-suggest
```

Then ask **D2**:

```
D2 — Which proxy provider?
Project/branch/task: $SLUG — buying the antidetect proxy for a Stage 0
account-setup gate (or portfolio expansion).
ELI10: Each provider trades off price, payment options, country coverage,
and API availability. We bias toward the one with a public buy API
(Proxy6) when the operator is set up for it; otherwise Space Proxy is
the bootcamp default for the US/RU mix. Free public proxies are never
on the table — they're banned on day one.
Stakes if we pick wrong: a dirty / hosting-ASN proxy burns a fresh CWS
account on first Google sign-in (≈ $50 of phone-verification slot + a
24h cool-off). A wrong-country proxy means the Chrome Web Store
moderator sees a geo mismatch with the developer billing address.
Recommendation: A if PROXY6_API_KEY is set OR the operator is comfortable
with crypto/card on Proxy6 — it's the only one we can fully automate.
B (Space Proxy) is the bootcamp default if RU card payment is available.
C (paste existing) if the operator already bought elsewhere.
Completeness: A=10/10 B=9/10 C=9/10 D=8/10 E=8/10 F=7/10 G=10/10
Pros / cons:
A) Proxy6 — autonomous buy via API (recommended if PROXY6_API_KEY set)
  ✅ Only provider with a public buy API; full automation via dolphin-cli.
  ✅ ~$1.50 / IP / month, supports 50+ countries including US / DE / GB.
  ❌ Requires PROXY6_API_KEY env var; ban risk slightly higher than premium tiers.
B) Space Proxy — bootcamp default, manual buy
  ✅ Static IPv4 labeled "for Facebook" — pre-screened against ad-platform bans.
  ✅ RU card payment supported; 2-week trial slot per IP.
  ❌ No public buy API; we paste credentials from the browser into proxies.txt.
C) Proxyline — premium static residential, manual buy
  ✅ Tier-1 residential pool; very low ban rate on Google / Meta.
  ✅ Per-IP rotation control; good for ads profiles.
  ❌ ~$5 / IP / month; no buy API.
D) Proxy-Sale — broad geo, manual buy
  ✅ Largest geo selection (180+ countries).
  ✅ Cheap (~$1 / IP / month) — fine for non-critical secondary profiles.
  ❌ Mixed ASN quality; check-proxy must validate is_hosting:false.
E) iProxy — mobile residential
  ✅ Mobile carrier IPs — cleanest pool, best for ad-platform warm-up.
  ✅ Per-IP rotation on demand.
  ❌ Premium pricing (~$10+ / IP / month); overkill for Stage 0.
F) Smartproxy — enterprise residential
  ✅ Largest residential pool; very high trust score.
  ❌ Subscription-only model (~$75+ / month minimum); only worth it for monetize-stage portfolios.
G) Paste existing — operator already bought outside Dolphin
  ✅ Reuses what's already paid for; zero new spend.
  ✅ Validates on import via check-proxy.
  ❌ If the provider isn't on the curated list, ban risk is unknown.
Net: A or B is the mechanical answer for Stage 0. C/E for ads or monetize
portfolios where a higher trust tier pays for itself. D for cheap secondary
roles. F only at portfolio scale. G if the proxy already exists.
```

## Step 2 — Buy

### Branch A: Proxy6 + `PROXY6_API_KEY` set

Mechanical. No further question:

```bash
# Always dry-run price-check first (no --yes flag)
python references/dolphin-cli.py proxy6-buy \
  --country us \
  --period 14 \
  --count 1

# Confirm the price + slot count, then commit
python references/dolphin-cli.py proxy6-buy \
  --country us \
  --period 14 \
  --count 1 \
  --yes
```

The wrapper auto-imports the purchased proxies into the Dolphin proxy
library on success. Move straight to Step 3 (validation).

### Branch B-G: Manual buy via the provider's browser flow

Surface the order URL and parameters explicitly. The operator clicks
through their browser (we don't drive the provider UI from this skill —
each provider has its own dashboard quirks, and a misclick on
country/period costs real money).

Order parameters (mechanical, do not ask):

- Tier: "for Facebook" (Space Proxy label) / static residential (Proxyline) /
  generic IPv4 (Proxy6, Proxy-Sale) / mobile (iProxy)
- Country: ISO2 from the operator (bootcamp default: `us` for the CWS
  developer account; ad-platform profiles match the ad account country)
- Period: **14 days** (Stage 0 trial; long enough to validate the launch
  cohort, short enough to abandon if dirty)
- Count: 1 (Stage 0) or matches portfolio-expansion role count

Once the operator pastes the credentials back, drop them into a temp file
and bulk-import:

```bash
cat > /tmp/cws-proxies-$SLUG.txt <<'EOF'
# host:port:user:pass  (or any other accepted format — see Phase 1E)
45.156.155.91:60991:Semenov:123qwe|us|space-proxy
EOF

python references/dolphin-cli.py bulk-add-proxies \
  --file /tmp/cws-proxies-$SLUG.txt
```

Then delete the temp file:

```bash
rm /tmp/cws-proxies-$SLUG.txt
```

## Step 3 — Validation gate (hard, no advancement on fail)

For each newly imported proxy ID:

```bash
python references/dolphin-cli.py check-proxy \
  --id <proxyId> \
  --expect-country us
```

The wrapper hits `ipinfo.io` through the proxy and asserts:

- `ok:true` — the proxy actually routes traffic.
- `is_hosting:false` — the ASN is residential / mobile, not a hosting
  provider. Iron rule #1.
- `country:<expect>` — matches the requested ISO2. Iron rule #3.

If any of these fail:

1. Ask the provider to swap (most premium providers do this within 24h
   on a ticket — "wrong country", "hosting ASN", "high abuse score").
2. If the provider refuses or doesn't swap, drop the proxy from the
   library and move to the next provider in D2.
3. **Do not advance to Phase 1B.** A profile attached to a bad proxy
   wastes the fingerprint slot and risks the Google account.

After CLI validation passes, **cross-verify in a real browser** before
attaching to a profile that holds a ranking account:

- Start a throwaway profile on this proxy (Phase 1B with role
  `proxy-validate-throwaway`), open `https://whoer.net`, target score
  ≥ 80%. The wrapper does not automate whoer scoring — it's a manual
  visual check.
- Cross-check `https://pixelscan.net` — all signals (browser, OS, GPU,
  timezone, language) should be consistent.

Anything below 80% on whoer.net = the proxy or fingerprint has a leak.
Don't proceed.

## Step 4 — Record + handoff

Update state.json with the validated proxy ID:

```bash
/usr/bin/python3 - <<EOF
import json, datetime, sys
p='./.cws/state.json'
with open(p) as f: d=json.load(f)
d.setdefault('dolphin',{})
d['dolphin'].setdefault('validated_proxies', [])
d['dolphin']['validated_proxies'].append({
  'id': <proxy_id>,
  'country': 'us',
  'provider': '<provider-slug>',
  'validated_at': datetime.datetime.utcnow().isoformat()+'Z',
})
json.dump(d, open(p,'w'), indent=2)
EOF
```

Then route per the skill-routing footer:

- If Stage 0 (`ACCOUNT_SETUP_GATE: open`): continue into Phase 1B in the
  same invocation. Stage 0 is one workflow — the operator shouldn't have
  to call cws-dolphin twice.
- Otherwise: footer routes to the caller (`cws-promote` for ad
  rotation; `cws-monetize` for portfolio scaling).

---

# Phase 1B — Profile create

Triggered when D1 = B, or as the continuation of Phase 1A in a Stage 0
run. A validated proxy exists in the Dolphin proxy library.

## Step 1 — Pick platform

```
D3 — Which OS for the Dolphin profile?
Project/branch/task: $SLUG — creating a new antidetect profile for role
<role> (Stage 0 launcher / ads-fb / ads-google / ads-yandex / monetize-N).
ELI10: Dolphin fakes the OS fingerprint at the browser level. macos
matches our dev machine — easier for sanity checks during dev. windows
is the broadest and matches the modal CWS user, useful for ad-portfolio
diversity. linux is rare on consumer web and slightly suspicious.
Stakes if we pick wrong: an OS that doesn't match the operator's billing
country / payment fingerprint may not get flagged immediately but
accumulates as a soft signal. For ad platforms (Meta especially), a
windows profile blends best.
Recommendation: A (macos) for the Stage 0 launcher profile if the
operator's dev machine is macOS — fewer cross-OS gotchas during local
debugging. B (windows) for any ads-* or monetize-* role — windows is the
modal Chrome user and blends into ad-platform telemetry.
Completeness: A=10/10 B=10/10 C=8/10
Pros / cons:
A) macos (recommended for Stage 0 launcher)
  ✅ Matches the dev machine fingerprint surface; less leakage during local debug.
  ✅ ~17% of US Chrome users; not unusual.
  ❌ Less common than windows; ad-platform telemetry may slightly down-weight.
B) windows (recommended for ads / monetize roles)
  ✅ ~74% of global Chrome users — the modal blend.
  ✅ Ad platforms calibrate against windows-heavy traffic.
  ❌ Cross-OS debug from a macOS dev machine has minor inconsistencies (path separators, fonts).
C) linux
  ✅ Useful for engineer-targeted extensions (developer tools).
  ❌ ~3% of Chrome users — stands out; not recommended unless the product targets devs.
Net: macos for Stage 0 + dev, windows everywhere else. Linux only when
the extension is explicitly developer-targeted.
```

## Step 2 — Pick role + proxy

The role is the slot in `state.json.dolphin.profiles`. Mechanical naming:

- Stage 0 first profile: role = `launcher` (recorded to
  `state.json.account_setup.dolphin_profile_id` AND
  `state.json.dolphin.profiles.launcher`)
- Ad rotation: role = `ads-fb`, `ads-google`, `ads-yandex`, `ads-tiktok`,
  one per ad platform
- Monetize portfolio: role = `monetize-account-1`, `monetize-account-2`,
  … one per CWS developer account in the portfolio

Pull the validated proxy from `state.json.dolphin.validated_proxies[]` —
the most recent one if Stage 0 continuation, otherwise prompt with the
list. The proxy details (host/port/login/pass) are then attached inline
to the create call (Dolphin supports both inline proxy and referenced-by-id;
inline keeps the profile self-contained).

## Step 3 — Create

```bash
python references/dolphin-cli.py create \
  --name "$SLUG-<role>-1" \
  --platform <macos|windows|linux> \
  --browser-version 130 \
  --proxy-host <ip> --proxy-port <port> \
  --proxy-login <user> --proxy-pass <pass> \
  --proxy-country us \
  --folder "cws-studio"
```

The wrapper:

1. Fetches a fresh fingerprint matching `--platform` and `--browser-version`.
2. Fetches a consistent UA.
3. Fetches a WebGL pair (always copy WebGL1 + WebGL2 together — splitting
   them breaks the WebGL consistency check).
4. POSTs to `/browser_profiles` with the assembled fingerprint + proxy.
5. Prints the resulting `browserProfileId` to stdout.

If any step fails (most common: token expired, rate limit, fingerprint
helper returns 503), the wrapper exits non-zero and prints the upstream
error. Surface verbatim to the operator — do not retry silently more
than once (rate limit will only get worse).

## Step 4 — Record into state.json

```bash
PROFILE_ID=<output from create>
ROLE=<launcher|ads-fb|monetize-account-1|...>

/usr/bin/python3 - <<EOF
import json, datetime
p='./.cws/state.json'
with open(p) as f: d=json.load(f)
d.setdefault('dolphin',{}).setdefault('profiles',{})
d['dolphin']['profiles']['$ROLE'] = {
  'id': $PROFILE_ID,
  'folder': 'cws-studio',
  'proxy': '<ip>:<port>',
  'platform': '<macos|windows|linux>',
  'created': datetime.datetime.utcnow().isoformat()+'Z',
  'last_started': None,
}
# Stage 0 also records into account_setup
if '$ROLE' == 'launcher':
  d.setdefault('account_setup',{})['dolphin_profile_id'] = $PROFILE_ID
json.dump(d, open(p,'w'), indent=2)
EOF
```

## Step 5 — Smoke test (start once)

Run Phase 1C `start <id>` once to confirm the local agent reaches the
profile, the proxy attaches without error, and the browser window
actually opens. If it fails, the profile is broken — Dolphin sometimes
returns a 200 on create but the local agent still refuses on start (e.g.
fingerprint mismatch between cloud and local cache). Re-create from
scratch in that case.

---

# Phase 1C — Start / stop

Triggered when D1 = C. The operator wants to open or close a profile.

## Step 1 — Local agent liveness

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  http://localhost:3001/v1.0/auth/login-with-token \
  -H "Authorization: Bearer $DOLPHIN_API_TOKEN"
```

Expected: `200`. Any other code (most commonly `000` = connection
refused) means the Dolphin{anty} desktop app is not running. Stop and
tell the operator:

> Dolphin desktop app is not running. Open `/Applications/Dolphin
> Anty.app` (or the Windows equivalent), let it finish syncing the
> profile list, then re-run.

Do **not** try to start the app via `open` / equivalent — the operator's
config may need the app to be opened manually with credentials the
skill doesn't have.

## Step 2 — Start or stop

```bash
# Start (opens the antidetect Chrome window)
python references/dolphin-cli.py start <profileId>

# Stop (closes it)
python references/dolphin-cli.py stop <profileId>
```

On start, the wrapper returns the `automation` block (port + ws URL for
Selenium / Playwright control). For pure manual browsing, ignore it.

## Step 3 — Record last_started

```bash
PROFILE_ID=<id>
ROLE=$(/usr/bin/python3 -c "
import json
d=json.load(open('./.cws/state.json'))
for r,m in d.get('dolphin',{}).get('profiles',{}).items():
    if m.get('id')==$PROFILE_ID: print(r); break")

/usr/bin/python3 - <<EOF
import json, datetime
p='./.cws/state.json'
with open(p) as f: d=json.load(f)
if '$ROLE':
  d['dolphin']['profiles']['$ROLE']['last_started']=datetime.datetime.utcnow().isoformat()+'Z'
  json.dump(d, open(p,'w'), indent=2)
EOF
```

`last_started` is what Phase 1F's portfolio audit reads to flag stale
profiles (> 90 days unused).

---

# Phase 1D — Cookie backup / restore

Triggered when D1 = D. The operator wants to export cookies for backup
(safe, no D), or import a previously-exported JSON into a profile
(destructive, needs D4).

## Branch: Export (no D — safe)

```bash
PROFILE_ID=<id>
TS=$(date +%Y%m%dT%H%M%SZ)
mkdir -p ./.cws/backups
python references/dolphin-cli.py export-cookies $PROFILE_ID \
  > ./.cws/backups/${PROFILE_ID}-cookies-${TS}.json
```

The backup file lives in `./.cws/backups/`. Filename pattern:
`<profile_id>-cookies-<ISO8601>.json`. Always run an export **before**
any potentially destructive operation on a profile (proxy swap, delete,
re-create). It's free insurance.

## Branch: Import (needs D4)

Iron rules first:

- Refuse the import if the profile is currently running (the operator
  must stop it via Phase 1C first — Dolphin will silently fail to
  overwrite live session state).

```
D4 — Confirm cookie overwrite into profile <id>?
Project/branch/task: $SLUG — restoring cookies from <backup-path> into
profile <id> (role=<role>).
ELI10: Importing cookies overwrites the live session for that profile.
If the profile has a fresh login (e.g. you signed into Google after the
backup was taken), that fresh login state is **gone** after import. The
import is irreversible without another backup.
Stakes if we pick wrong: a wrong-version backup = re-do all logins
(Google, ad accounts, CWS dashboard) + possible 2FA SMS storm. If the
profile was tied to a ranking extension, behavioral factors briefly
flatline while logins re-establish.
Recommendation: A only if the operator has explicitly identified the
backup file and confirmed it matches the expected role + Google account.
B otherwise.
Completeness: A=10/10 B=10/10
Pros / cons:
A) Import — overwrite session (recommended only on explicit confirmation)
  ✅ Restores a known-good state from before a config change broke things.
  ✅ Avoids re-doing every login + 2FA flow manually.
  ❌ Irreversible without another backup — destroys any newer session state.
B) Cancel — keep current session
  ✅ Zero risk; current logins remain intact.
  ✅ Preserves the option to re-export current state as a fresher backup first.
  ❌ Whatever was broken stays broken until you choose A deliberately.
Net: never reach for A without a deliberate "yes the old backup is the
one I want" — when in doubt, B and take a fresh export first.
```

If A:

```bash
python references/dolphin-cli.py import-cookies <profileId> \
  --file ./.cws/backups/<backup-filename>.json
```

---

# Phase 1E — Bulk import

Triggered when D1 = E. The operator pasted a batch of proxies bought
outside Dolphin (or this is the manual-buy fork from Phase 1A).

## Step 1 — Accepted line formats

The wrapper accepts these line shapes (one per line; blank and
`#`-prefixed lines skipped):

```
host:port:user:pass
user:pass@host:port
scheme://user:pass@host:port           # scheme in {http, https, socks5}
host:port                              # no auth
host:port:user:pass|us|provider-name   # optional country|provider hints
```

Provider hints are recorded into `state.json` so portfolio audits can
group by provider when one supplier becomes unreliable.

## Step 2 — Dry run

Always dry-run first. The CLI parses the file, normalizes each line, and
prints what it **would** import without hitting the Dolphin API:

```bash
python references/dolphin-cli.py bulk-add-proxies \
  --file <path> \
  --dry-run
```

If any line is rejected (regex failure, unknown scheme), fix the file
and re-dry-run. Do not push a half-broken batch into the live import —
partial state in the Dolphin proxy library is painful to clean up.

## Step 3 — Live import + per-proxy validation

```bash
python references/dolphin-cli.py bulk-add-proxies --file <path>
```

The wrapper imports each line and prints the resulting `proxyId`s.
Immediately validate every one (Phase 1A Step 3):

```bash
for PROXY_ID in <id1> <id2> ...; do
  python references/dolphin-cli.py check-proxy \
    --id $PROXY_ID \
    --expect-country <iso2>
done
```

Any failure → swap or drop per the iron rules. Update
`state.json.dolphin.validated_proxies[]` only with the IDs that passed.

---

# Phase 1F — Portfolio audit

Triggered when D1 = F. Read-only. Surfaces stale profiles, broken
proxies, and over-portfolio warnings.

## Step 1 — List

```bash
python references/dolphin-cli.py list --folder cws-studio
```

The wrapper returns the full profile list. Format as one line per
profile:

```
<profile_id>  <name>  <proxy_ip:port>  last_started=<iso8601|never>  role=<role>
```

## Step 2 — Flag stale

A profile is **stale** if `last_started > 90 days ago`. Google's
behavioral factors decay quickly; a profile dormant >90d is effectively
cold-start when re-opened. Flag inline:

```
12345  $SLUG-launcher-1   45.156.155.91:60991   last_started=2026-01-12T10:00Z   role=launcher   ⚠ stale (132 days)
```

## Step 3 — Re-check every proxy

Re-validate every attached proxy (proxies go dirty between purchases):

```bash
# pull every distinct proxy ID from state.json and re-check
/usr/bin/python3 -c "
import json
d=json.load(open('./.cws/state.json'))
for p in d.get('dolphin',{}).get('validated_proxies',[]):
    print(p['id'])
" | while read pid; do
  python references/dolphin-cli.py check-proxy --id $pid
done
```

Flag any that now fail `is_hosting:false` or country match. These
profiles will burn their account on next start.

## Step 4 — Portfolio-size warning

Mechanical iron rule #6: if `len(profiles) > 3` AND multiple profiles
share an extension-author signature (heuristic: same operator email on
the CWS account), surface this:

> Warning: <N> profiles tied to overlapping extension authorship.
> Chrome's code-reuse detector flags mass-publisher footprints at ≈4+
> extensions per identity cluster. Consider splitting the portfolio
> across two operator identities, or retiring the weakest profile.

This is a heuristic — the operator decides whether to act. The skill
surfaces, never acts.

## Step 5 — No taste decisions; surface and exit

Audit is read-only. Route the operator to a follow-up skill if anything
needs action:

- Broken proxy → return to Phase 1A (provider swap).
- Stale profile → start once via Phase 1C to refresh behavioral signal,
  or retire via Phase 1G.
- Over-portfolio warning → `cws-monetize` decides; gate via
  `cws-careful` before adding more.

---

# Phase 1G — Profile delete

Triggered when D1 = G. **Hard gate via cws-careful.** The most
destructive operation in this skill — irreversible.

## Step 1 — Refuse without cws-careful confirmation

State.json must show `gates_passed` includes a recent `cws-careful`
entry tagged to this delete. If not, stop:

> DELETE blocked. Run `/cws-careful` first to confirm. Profile delete
> is irreversible — Dolphin sends `forceDelete:true` and the cloud
> record is gone immediately. Losing the cookie state means 2FA
> re-verification on next Google login, which can burn the account if
> Google's anti-abuse is suspicious of the geo / device.

Re-run after `cws-careful` passes.

## Step 2 — Mandatory cookie backup first

Run Phase 1D Export branch unconditionally:

```bash
PROFILE_ID=<id>
TS=$(date +%Y%m%dT%H%M%SZ)
mkdir -p ./.cws/backups
python references/dolphin-cli.py export-cookies $PROFILE_ID \
  > ./.cws/backups/${PROFILE_ID}-cookies-${TS}.json

# Verify the backup is non-empty (a zero-byte JSON = no cookies = the
# Google session can't be restored)
if [ ! -s ./.cws/backups/${PROFILE_ID}-cookies-${TS}.json ]; then
  echo "Cookie backup is empty — aborting delete"
  exit 1
fi
```

## Step 5 — D5 — Surface portfolio expansion taste decision (if applicable)

If the operator is deleting to make room for a portfolio expansion (D1
context indicates monetize-stage scaling), surface the trade-off:

```
D5 — Confirm portfolio expansion direction?
Project/branch/task: $SLUG — about to delete profile <id> (role=<role>)
to free a slot for <new-role>.
ELI10: You're retiring an existing antidetect identity to create a new
one. Iron rule #6 caps the portfolio at 2-3 extensions per profile and
recommends splitting across operator identities at 4+. If this delete
is to stay under that cap, it's the right call. If it's to add yet
another extension on the same operator identity, you're walking into
Chrome's code-reuse detector.
Stakes if we pick wrong: continuing to expand on one identity cluster
risks a mass-publisher flag = simultaneous strikes across every
extension on that account.
Recommendation: A if retiring under the cap. B if expansion would push
the identity cluster over 4 extensions — split operator identities
instead.
Completeness: A=10/10 B=10/10
Pros / cons:
A) Continue delete + replace (recommended only if staying under cap)
  ✅ Frees the slot cleanly; portfolio stays under the detector threshold.
  ✅ Cookie backup is in place; rollback is possible if Google flags the new identity.
  ❌ Still spends Google's trust budget on the new account warm-up (~30 days).
B) Pause — split to a second operator identity instead
  ✅ Avoids the code-reuse pattern entirely; safer scaling.
  ✅ Doubles the portfolio ceiling on the same product.
  ❌ Operationally heavier — second billing identity, second payment method, second phone.
Net: if this expansion stays under 3 extensions per identity, A. If
it'd be the 4th, take the operational hit of B.
```

This is a **taste** decision — auto-mode (`cws-autoplan`) surfaces it at
the final approval gate; never auto-decides.

## Step 6 — Execute

```bash
python references/dolphin-cli.py delete <profileId> --force
```

The `--force` flag sends `forceDelete:true` in the request body (Dolphin
returns HTTP 403 `E_BROWSER_PROFILE_FORCE_DELETE` without it).

## Step 7 — Update state.json

```bash
PROFILE_ID=<id>
ROLE=<role>

/usr/bin/python3 - <<EOF
import json, datetime
p='./.cws/state.json'
with open(p) as f: d=json.load(f)
if '$ROLE' in d.get('dolphin',{}).get('profiles',{}):
  # archive into a retired block rather than dropping outright — audit trail
  retired = d['dolphin']['profiles'].pop('$ROLE')
  retired['retired_at']=datetime.datetime.utcnow().isoformat()+'Z'
  d['dolphin'].setdefault('retired',[]).append({'role':'$ROLE', **retired})
json.dump(d, open(p,'w'), indent=2)
EOF
```

Retired profiles stay in `state.json.dolphin.retired[]` so future audits
can correlate ranking dips against profile retirements.

---

## State integration (read by every phase)

Each operation reads/writes `.cws/state.json`:

```json
{
  "dolphin": {
    "token_set": true,
    "local_agent_reachable": true,
    "validated_proxies": [
      {
        "id": 78901,
        "country": "us",
        "provider": "space-proxy",
        "validated_at": "2026-05-23T09:00Z"
      }
    ],
    "profiles": {
      "launcher": {
        "id": 12345,
        "folder": "cws-studio",
        "proxy": "45.156.155.91:60991",
        "platform": "macos",
        "created": "2026-05-23T10:00Z",
        "last_started": "2026-05-26T09:12Z"
      },
      "ads-fb": {
        "id": 12346,
        "folder": "cws-studio",
        "proxy": "45.156.155.92:60991",
        "platform": "windows",
        "created": "2026-05-24T10:00Z",
        "last_started": "2026-05-26T09:12Z"
      }
    },
    "retired": []
  },
  "account_setup": {
    "gate_passed": true,
    "dolphin_profile_id": 12345
  }
}
```

The convention: **one profile per CWS developer account, NOT per
extension** (iron rule #5; bootcamp rule restated). Two extensions can
share one account; they cannot share two profiles.

## Reference docs

This skill does not duplicate API documentation. The two reference files
already in the skill directory are authoritative:

- `references/dolphin-api.md` — curated endpoint cheat-sheet. ~20
  endpoints `cws-studio` actually uses (full OpenAPI is ~8K lines; the
  reference is the ~200-line distilled version). Read this before
  hand-rolling any `curl` call the wrapper doesn't expose.
- `references/dolphin-cli.py` — the Python wrapper. Tested live against
  the real Dolphin cloud + local agent. Treat as a stable tool — do
  **not** edit from this skill.

For anything not covered by either, query the Dolphin docs MCP
(`search_documentation`) — the plugin wires `https://docs.dolphin-anty.com/_mcp`
into Claude Code automatically.

## When NOT to use this skill

- Pure proxy / networking questions that don't involve the antidetect
  layer ("which residential proxy provider is cheapest in Brazil") —
  route to the provider's own docs or a general proxy comparison
  resource. This skill is about the Dolphin{anty} integration, not
  proxy market research.
- Generic Chrome profile management (no antidetect, no fingerprint
  control) — use Chrome's built-in profile manager. Dolphin overhead
  isn't worth it unless you specifically need fingerprint isolation.
- API tokens for Dolphin itself — the operator generates these in the
  panel; this skill never creates them.

## Companion skills

- **cws-careful** — hard gate before any DELETE (Phase 1G) or portfolio
  expansion past 3 extensions on one identity (D5).
- **cws-idea** — Stage 0 caller. Phase 1A + Phase 1B run inside the
  cws-idea account-setup gate.
- **cws-promote** — caller for per-ad-platform profile rotation
  (`ads-fb`, `ads-google`, `ads-yandex`, `ads-tiktok` roles).
- **cws-monetize** — caller for portfolio scaling
  (`monetize-account-N` roles); also the caller most likely to trip
  iron rule #6 (>3 extensions per identity).
- **cws-learn** — record per-provider reliability lessons (which
  proxy provider swapped within 24h, which had hosting-ASN slippage,
  which burned an account). Future invocations of this skill read those
  learnings via the `--stage dolphin` filter in the preamble.

## What this skill never does

- Never generates API tokens — operator grabs them from the panel.
- Never fingerprint-mismatches profiles (always the
  fetch-fingerprint-first chain via the CLI wrapper).
- Never starts a profile without confirming the local agent is reachable.
- Never deletes a profile linked to a ranking extension without
  `cws-careful` + cookie backup.
- Never silently retries failed Dolphin API calls more than once (rate
  limits compound).
- Never accepts a proxy that fails `is_hosting:false` / country match.
- Never accepts a free public proxy.

## Skill routing footer

End the invocation with one of:

- Stage 0 first-run (Phase 1A → Phase 1B in one call):
  ```
  Next: /cws-idea
  Why: Stage 0 account setup is the immediate next move — the gate is open and
  Stage 1 (idea validation) is blocked until it passes.
  ```
- Ads profile creation (Phase 1B with `ads-*` role):
  ```
  Next: /cws-promote
  Why: per-ad-platform profile is in place; the ad warm-up workflow uses it directly.
  ```
- Portfolio expansion (Phase 1B with `monetize-*` role, or Phase 1G
  retirement-then-replace):
  ```
  Next: /cws-monetize
  Why: portfolio slot is live; resume the scaling workflow that called us.
  ```
- Audit-only (Phase 1F):
  ```
  Next: <caller-stage skill>
  Why: audit found <0|N> issues — <hand back to caller | fix the flagged issue first>.
  ```
- Start / stop only (Phase 1C):
  ```
  Next: <caller-stage skill>
  Why: profile state is updated; the caller's workflow can resume.
  ```

Pick one. Never a menu.
