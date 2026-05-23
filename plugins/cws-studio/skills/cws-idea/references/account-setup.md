# Stage 0 — Account setup (CWS developer account)

Setup needed before publishing. Most relevant for builders in **Russia/Belarus**,
who need an antidetect browser + proxy; builders elsewhere can skip the
antidetect/proxy parts and register normally.

## Why antidetect (RU/BY context)

A June 2024 sanctions package bars US companies from selling some cloud B2B
services to RU. CWS access can arguably be pulled into that category, and
companies often over-restrict to be safe. So: **do not log into the
account/extension-publishing Google account, CWS, or Semrush from a normal
browser** — not even with a VPN (a VPN doesn't truly hide the original address).
Use an **antidetect browser** instead.

## Step 1 — Proxy

Buy a proxy (e.g. Space Proxy, proxyline, proxy-sale — any works). When ordering:
pick a country, select the "for Facebook" use case (fine for CWS/Semrush too).
Buy for ~2 weeks first so you can test it. After purchase you get: IP, port,
login, password.

## Step 2 — Antidetect browser

Install **Dolphin Anty** (free tier ≈ 10 profiles). Add a new proxy in the format
`IP:port:login:password` (e.g. `45.156.155.91:60991:Semenov:123qwe`). Verify the
connection shows the correct country flag (green arrows). Launch the profile and
check anonymity on whoer.net / pixelscan.net — 70–100% green is acceptable.

**Or automate it** — invoke the `cws-dolphin` skill to scaffold the profile +
proxy + fingerprint end-to-end via the Dolphin{anty} REST API. Get a JWT token
from [dolphin-anty.com/panel](https://dolphin-anty.com/panel/index.html#/api),
export `DOLPHIN_API_TOKEN`, then ask Claude to run `cws-dolphin create` with
the launch params.

## Step 3 — Google account

Register a **new Google account** — ideally one per extension. If one account is
banned and holds all extensions, you lose them all; for a first launch keep **max
2 extensions per account**. Once an extension passes 2,000 users it can be
migrated to another account without losing the audience (request via the CWS
one-stop support form; takes ~1 day).

Phone verification — two options:
- **Permanent number** (recommended): esimplus.me, "unburned" numbers, ~$8/mo,
  stays yours forever, never needs detaching. Needs a foreign card (ByBit or
  by.oplatym.ru can help).
- **Temporary number** (no longer recommended): sms-activate.org. Google now
  often re-requests SMS on the *original* registration number even after
  detaching, which can lock you out.

If SMS verification fails (~20% of esimplus numbers) or Google does "reverse"
verification (~5%): register through the **Gmail app on a smartphone (Android
preferred)** — often registers with no SMS at all. Gmail registration is allowed
from RU/BY IPs without VPN.

If Google suspends a new account, appeal with a short letter explaining it's for
developing/publishing a Chrome extension and keeping it separate from a personal
account — **rewrite it via ChatGPT** (the canned text is overused and fails).

## Step 4 — 2FA

At myaccount.google.com/security → Security → 2-Step Verification → add the phone,
then add **Google Authenticator** (iOS/Android) as the app method. Then remove the
backup phone number *only if* you used a temporary number (keep a permanent
esimplus number attached).

## Step 5 — CWS developer registration

From the antidetect browser, go to
`chrome.google.com/webstore/devconsole/register`, log into the Google account,
accept terms, **pay the one-time developer fee** with a foreign card (the card's
country need not match the account country). Go to the developer dashboard,
choose the no-in-app-purchases option for now (switch later when monetizing),
add and confirm a Gmail address (no Mail.ru/Yandex). Enable review and
publication notifications.

In the first 1–2 months Google may occasionally refuse login by the registration
phone. Try up to 3 numbers from different countries; if one works keep it but
**don't delete the original**. If none work, log in via the Gmail app on a phone
(any IP). Last resort: don't touch the account for 7 days, then log in from a
different IP. This is rare (~5%) and disappears after 2–3 months of active use.

> Relay prices, services and URLs factually as the methodology states them.
> Don't invent current prices — they drift.

