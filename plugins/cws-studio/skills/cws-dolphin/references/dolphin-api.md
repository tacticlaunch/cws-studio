# Dolphin{anty} API — curated endpoint cheat-sheet

Curated from `openapi.yaml v1.0.7`. Only the endpoints `cws-studio` skills
actually call. For anything else, query the Dolphin docs MCP
(`search_documentation`) or pull the full spec from
`https://docs.dolphin-anty-cdn.com/openapi.yaml`.

## Auth

JWT Bearer. Same token works for both servers.

```
Authorization: Bearer <DOLPHIN_API_TOKEN>
```

Token from: `https://dolphin-anty.com/panel/index.html#/api`. Store in
`$DOLPHIN_API_TOKEN`.

## Servers

| Purpose | Base URL |
|---|---|
| Cloud API (profile CRUD, fingerprints, proxies, folders) | `https://dolphin-anty-api.com` |
| Local agent (start/stop browser windows) | `http://localhost:3001` |
| Cloud v2 (a subset of operations) | `https://apiv2.dolphin-anty-api.com/api/v2` |

The local agent only works when the **Dolphin{anty} desktop app is running**.
A 200 from `GET /v1.0/auth/login-with-token` is the canonical liveness check.

---

## Browser profiles — CRUD

### `POST /browser_profiles` — create

Returns: `{ browserProfileId: <int>, ... }`. **All fingerprint fields are
required** — the backend does NOT auto-generate them. The safe pattern is to
chain the three helper endpoints below first, then assemble.

Required top-level fields:
- `name` (string)
- `platform` (`windows` | `macos` | `linux`)
- `browserType` (`anty` — use this)
- `platformVersion` (string)
- `fingerprint` (object — paste verbatim from `GET /fingerprints/fingerprint`)

Optional:
- `proxy` (object — see Proxy below; can be inline or referenced by ID)
- `useragent.value` (override the UA in the fingerprint)
- `tags` (array of strings)
- `statusId` (int — see statuses)
- `notes` (string)
- `mainWebsite` (string)

### `GET /browser_profiles` — list

Query params: `limit`, `page`, `tags[]`, `statuses[]`, `query` (search by
name), `folder`. Returns paginated list of profile objects.

### `GET /browser_profiles/{id}` — read one

Returns full profile object with `fingerprint`, `proxy`, `cookies`, etc.

### `PATCH /browser_profiles/{id}` — update

Partial update. Useful for: re-attaching proxy, changing name, moving folder,
re-tagging.

### `DELETE /browser_profiles/{id}` — delete

Permanent. Body **must** include `{"forceDelete": true}` or the call returns
HTTP 403 with `E_BROWSER_PROFILE_FORCE_DELETE`. **Gate via `cws-careful` if the
profile holds a ranking extension's CWS account login.**

### `POST /browser_profiles/mass` — bulk create / delete / move

Useful when spinning up a portfolio.

### `POST /browser_profiles/transfer` — transfer profile to another Dolphin
team / user.

---

## Fingerprint helpers (Cloud)

Always run these in order **before** creating a profile.

### `GET /fingerprints/fingerprint?platform=&browser_type=anty&browser_version=`

Returns a full fingerprint JSON (canvas, WebGL, audio, screen, hardware
metrics, ...). Pass the **major** Chrome version only (e.g. `130`).

### `GET /fingerprints/useragent?platform=&browser_version=`

Returns a single UA string consistent with the platform/version above.

### `GET /fingerprints/webglList?platform=&withMaximum=true&browser_version=`

Returns a list of real GPU adapter pairs (WebGL1 + WebGL2). Pick one,
**always copy the pair together** to keep `webglInfo` and `webgl2Maximum` in
sync.

### `GET /fingerprints/font-list?platform=`

Returns realistic font families for the platform. Extract `.font` strings
into the profile's `fonts` array. Set `fontsMode: "manual"`.

---

## Profile start / stop (Local agent)

### `GET /v1.0/browser_profiles/{browserProfileId}/start[?automation=1]`

Starts the profile — opens a Chrome window. With `automation=1` returns a
WebSocket debugging URL for Puppeteer/Playwright control.

### `GET /v1.0/browser_profiles/{browserProfileId}/stop`

Closes the browser window.

### `POST /v1.0/browser_profiles/start`

Mass-start: body `{ "profileIds": [1,2,3] }`.

### `GET /v1.0/auth/login-with-token`

Liveness check for the local agent. 200 = local app running and authed.

---

## Proxy

### `POST /proxy` — add a proxy to your library

Body:
```json
{
  "type": "http",
  "host": "45.156.155.91",
  "port": 60991,
  "login": "Semenov",
  "password": "123qwe",
  "name": "cws-studio · primary",
  "countryCode": "us"
}
```

Returns `{ id, ... }`. Reference by ID in profile create (`proxy: { id: <int> }`)
or inline.

### `GET /proxy` — list saved proxies
### `PATCH /proxy/{id}` — update
### `DELETE /proxy/{id}` — delete

---

## Folders & statuses

Useful to organize profiles **per launch** so they don't pollute the global
profile list.

- `POST /folders` — create folder `cws-studio` (or per-product subfolder).
- `POST /folders/mass/attach-profiles` — bulk-attach by profileIds.
- `POST /folders/mass/detach-profiles` — bulk-detach.
- `GET /browser_profiles/statuses` / `POST` — manage custom status labels
  (e.g. `idea`, `building`, `launched`, `monetizing`) to mirror the cws-studio
  pipeline stage on the profile itself.

---

## Cookies

### `POST /cookies/import` — import cookie JSON into a profile

Body: `{ "profileId": <int>, "cookies": [...] }` (Chrome cookie format).

### `GET /cookies/export?profileId=<int>` — export cookies from a profile

Returns a JSON array — back up before any risky operation.

### `POST /v1.0/import/cookies/{browserProfileId}/robot` — start automated
cookie-warming (visits sites under the profile to seed cookies).
### `POST /v1.0/import/cookies/{browserProfileId}/robot-stop` — stop.

---

## Tags (informal)

`PATCH /browser_profiles/{id}` with `{ "tags": ["cws-studio", "<product>",
"<launch-month>"] }`. Helpful for filtering in `GET /browser_profiles`.

---

## Recommended patterns for cws-studio

### Stage 0 (cws-idea account setup) — one-shot

1. `GET /fingerprints/fingerprint?platform=macos&browser_type=anty&browser_version=130`
2. `GET /fingerprints/useragent?platform=macos&browser_version=130`
3. `POST /proxy` — store the bought proxy.
4. `POST /folders` — create `cws-studio` folder (if first run).
5. `POST /browser_profiles` — full body with fingerprint, UA, proxy ID,
   folder, name (e.g. `cws-studio · primary`), tag `cws-studio`.
6. `GET /v1.0/browser_profiles/{id}/start` — open it; user signs into
   Google + CWS inside this profile.
7. Persist the profile ID in `.cws/state.json`.

### Stage 5 (cws-monetize scale) — N accounts

Repeat the above N times with different names, *different proxies*, and a
distinct folder per launch. The playbook rule "≤ 2 extensions per account"
still applies — one Dolphin profile per CWS account.

### Stage 4 (cws-promote ad accounts)

Some teams maintain *separate* Dolphin profiles per ad platform (FB / Google
/ Yandex) to compartmentalize fingerprint risk. The same proxy can be shared
across them or each gets its own; per the playbook guidance, **don't
swap the proxy frequently** — buy long-term and warm the fingerprint.

---

## Common errors

- `400` on `POST /browser_profiles` → fingerprint missing fields. Always
  start from `/fingerprints/fingerprint`.
- `401` → token expired or empty. Regenerate at the panel.
- `Local agent unreachable` → Dolphin app not running, or running on a
  non-default port. Restart the app.
- `403` on a team operation → token belongs to a different team / no
  permission.

## Rate limits

The spec doesn't document rate limits explicitly. Practical limit observed:
the fingerprint helper endpoints rate-limit at roughly 1 call/sec — batch
profile creation should sleep briefly between iterations.
