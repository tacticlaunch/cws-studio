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
---

## Preamble (run first)

Run the standard preamble (see `shared/preamble.md`). It loads `$SLUG`,
branch, prior learnings (filtered by this stage), and `./.cws/state.json`.
Skip the rest of this skill if the preamble exits — the preamble is the
gate.

## AskUserQuestion Format

See `shared/askuserquestion-format.md`. Every interactive decision goes
through `AskUserQuestion` as a `D<N>` decision brief (ELI10 · Stakes ·
Recommendation · Completeness · Pros/cons · Net). D-numbering starts at D1
per invocation.

## Voice

See `shared/voice.md`. Operator voice. No banners. No file-creation dumps.
Concrete numbers, names, paths. Lead with the point.

## Skill Routing Footer

End every invocation with a single `Next: /cws-<skill>` line per
`shared/skill-routing.md`. Never a menu.

---
# CWS Studio — Dolphin{anty} automation

Programmatic Dolphin{anty} profile management — replaces the manual clicking
that Stage 0 used to require.

## When to use

- **First-time Stage 0** — create the antidetect profile + attach the bought
  proxy + verify connection, instead of doing it by hand.
- **New launch on a fresh CWS account** — spin up a profile for the new
  account in one shot.
- **Multi-account portfolios** (cws-monetize scaling pattern) — manage
  several profiles, one per extension / account.
- **Ad platform rotation** (cws-promote) — keep a profile per ad account
  (FB / Google / Yandex) to compartmentalize fingerprint risk.
- **Profile housekeeping** — list, tag (status / folder), export cookies for
  backup, delete obsolete profiles.

## Two APIs at play

| API | Base URL | Use for |
|---|---|---|
| **Cloud** | `https://dolphin-anty-api.com` | Profile CRUD, fingerprints, proxies, folders, cookies, transfer |
| **Local agent** | `http://localhost:3001` (Dolphin Anty app running) | Start / stop a profile (opens the actual browser window) |

Both authenticate with the **same** JWT Bearer token from
[dolphin-anty.com/panel](https://dolphin-anty.com/panel/index.html#/api).

Set the token once:

```bash
export DOLPHIN_API_TOKEN='ey...'
```

(Or add to `~/.zshrc` for persistence.)

## How to run

1. Read `.cws/state.json` to know which launch / account this Dolphin
   operation belongs to.
2. Verify token: `echo $DOLPHIN_API_TOKEN | head -c 12` — if empty, instruct
   user to set it from the panel.
3. For start/stop operations, verify the **local Dolphin app** is running
   (try `GET http://localhost:3001/v1.0/auth/login-with-token`). If not,
   tell the user to launch the app before retrying.
4. Use `references/dolphin-cli.py` (small Python wrapper around the most
   common operations) — or hand-roll `curl` for one-offs. The wrapper handles
   the multi-step fingerprint workflow (fetch fingerprint → fetch UA → fetch
   WebGL → POST profile) so you don't have to chain it manually.
5. Record the resulting `browserProfileId` into `.cws/state.json` under
   `dolphin.profiles[<account_label>]` so future skills know which profile
   to start.

## Typical workflows

### Create a profile for a new launch

```bash
python references/dolphin-cli.py create \
  --name 'cws-studio · <product-name>' \
  --platform macos \
  --browser-version 130 \
  --proxy-host 45.156.155.91 --proxy-port 60991 \
  --proxy-login Semenov --proxy-pass 123qwe \
  --folder 'cws-studio'
```

Writes profile ID to stdout. Skill captures it into `state.json`.

### Start the profile (open the browser)

```bash
python references/dolphin-cli.py start <profileId>
```

This hits the local agent. The actual Chrome window opens.

### Stop the profile

```bash
python references/dolphin-cli.py stop <profileId>
```

### List launch profiles by tag

```bash
python references/dolphin-cli.py list --folder cws-studio
```

### Find a provider + auto-buy

The agent does not have a baked-in proxy supply. Two paths:

```bash
# 1. print curated provider table (Space Proxy, Proxy6, Proxyline, Proxy-Sale,
#    iProxy, Smartproxy) with prices, payment options, who has an API.
python references/dolphin-cli.py proxies-suggest

# 2. autonomous purchase via Proxy6 (only provider with a public buy API):
export PROXY6_API_KEY=…   # from https://proxy6.net/user/developers
python references/dolphin-cli.py proxy6-buy --country us --period 7 --count 2
#    → dry-run price check; add --yes to actually buy.
#    The purchased proxies are auto-imported into Dolphin's proxy library.
```

For providers without an API (Space Proxy is the bootcamp default — buy 2-week
static IPv4 labeled "for Facebook"): buy in the browser, paste credentials into
`proxies.txt`, then `bulk-add-proxies` (below).

### Bulk-import proxies from a provider export

```bash
# accepted line shapes (one per line; blank/`#`-prefixed lines skipped):
#   host:port:user:pass
#   user:pass@host:port
#   socks5://user:pass@host:port
#   host:port
#   host:port:user:pass|us|provider-name   ← optional country|provider hints
python references/dolphin-cli.py bulk-add-proxies --file proxies.txt --dry-run
python references/dolphin-cli.py bulk-add-proxies --file proxies.txt
```

After import, sanity-check each one before attaching to a profile:

```bash
python references/dolphin-cli.py check-proxy --id <proxyId>
# → {ok: true, ip, country, asn} via ipinfo.io routed through the proxy
```

Fail = drop the proxy or contact provider before wasting it on a ranking
profile. The check uses `urllib`'s proxy handler — it works without the
Dolphin local agent running.

### Backup cookies before re-uploading the extension

```bash
python references/dolphin-cli.py export-cookies <profileId> > cookies.json
```

### Delete an obsolete profile

```bash
python references/dolphin-cli.py delete <profileId>
```

…always confirm via `cws-careful` before deleting a profile tied to a
ranking extension — if you lose the cookie state, the dev-dashboard login
will require 2FA re-verification.

## State integration

Each operation updates `.cws/state.json`:

```json
{
  "dolphin": {
    "token_set": true,
    "local_agent_reachable": true,
    "profiles": {
      "primary_account": {
        "id": 12345,
        "folder": "cws-studio",
        "proxy": "45.156.155.91:60991",
        "created": "2026-05-23T10:00Z",
        "last_started": "2026-05-26T09:12Z"
      }
    }
  }
}
```

The convention: one profile per **CWS developer account**, not per extension.
The bootcamp method's "max 2 extensions per account" guideline (in
`cws-idea/references/account-setup.md`) still holds.

## Reference doc

See `references/dolphin-api.md` for the curated endpoint cheat-sheet (the full
OpenAPI spec is ~8K lines; the reference distills the ~20 endpoints
cws-studio actually uses).

## Dolphin docs MCP

The plugin also wires the **Dolphin docs MCP** (`https://docs.dolphin-anty.com/_mcp`)
into Claude Code. Tool: `search_documentation` — semantic search across the
official Dolphin docs. Use it for "how do I configure X in Dolphin" questions
that aren't covered by `references/dolphin-api.md`.

## What this skill never does

- Doesn't generate API tokens — the user must grab them from the panel.
- Doesn't fingerprint-mismatch profiles (always uses the recommended
  fetch-fingerprint-first workflow).
- Doesn't start a profile without confirming the local agent is reachable.
- Doesn't delete a profile linked to a ranking extension without going
  through `cws-careful`.
