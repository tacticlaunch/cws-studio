#!/usr/bin/env python3
"""
Dolphin{anty} CLI wrapper for cws-studio.

Wraps the common operations cws-studio skills need:
  - create   : end-to-end profile creation (fingerprint -> UA -> proxy -> profile)
  - list     : list profiles (optional folder/tag filter)
  - get      : fetch one profile
  - update   : PATCH a profile
  - delete   : delete a profile (confirm via --force)
  - start    : start a profile via the local agent
  - stop     : stop a profile via the local agent
  - status   : local agent liveness + token validity
  - export-cookies / import-cookies
  - add-proxy / list-proxies

Auth: set DOLPHIN_API_TOKEN in env. Token from
https://dolphin-anty.com/panel/index.html#/api

Requires: Python 3.8+ stdlib only (urllib + json).
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

CLOUD = "https://dolphin-anty-api.com"
LOCAL = "http://localhost:3001"
TOKEN_ENV = "DOLPHIN_API_TOKEN"


def _token():
    t = os.environ.get(TOKEN_ENV, "").strip()
    if not t:
        sys.exit(
            f"error: {TOKEN_ENV} not set. Grab a JWT from "
            f"https://dolphin-anty.com/panel/index.html#/api and `export {TOKEN_ENV}=...`"
        )
    return t


def _req(method, url, body=None, params=None):
    if params:
        url = url + "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    data = None
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8")
            if not raw:
                return {}
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"raw": raw}
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8"))
        except Exception:
            err = {"error": str(e)}
        sys.exit(f"HTTP {e.code} on {method} {url}: {json.dumps(err, ensure_ascii=False)}")
    except urllib.error.URLError as e:
        sys.exit(f"network error on {method} {url}: {e.reason}")


# ----- commands --------------------------------------------------------------


def cmd_status(args):
    out = {"token_set": bool(os.environ.get(TOKEN_ENV)), "cloud_ok": False, "local_ok": False}
    try:
        _req("GET", f"{CLOUD}/browser_profiles", params={"limit": 1})
        out["cloud_ok"] = True
    except SystemExit as e:
        out["cloud_error"] = str(e)
    try:
        _req("GET", f"{LOCAL}/v1.0/auth/login-with-token")
        out["local_ok"] = True
    except SystemExit as e:
        out["local_error"] = "Dolphin app not running (or wrong port)"
    print(json.dumps(out, indent=2))


def cmd_create(args):
    platform = args.platform
    bver = args.browser_version
    print(f"[1/4] fingerprint platform={platform} bver={bver} …", file=sys.stderr)
    fp = _req(
        "GET",
        f"{CLOUD}/fingerprints/fingerprint",
        params={"platform": platform, "browser_type": "anty", "browser_version": bver},
    )
    time.sleep(1)
    print("[2/4] useragent …", file=sys.stderr)
    ua = _req(
        "GET",
        f"{CLOUD}/fingerprints/useragent",
        params={"platform": platform, "browser_version": bver},
    )
    time.sleep(1)
    proxy_block = None
    if args.proxy_host:
        print("[3/4] proxy save …", file=sys.stderr)
        proxy = _req(
            "POST",
            f"{CLOUD}/proxy",
            body={
                "type": "http",
                "host": args.proxy_host,
                "port": args.proxy_port,
                "login": args.proxy_login,
                "password": args.proxy_pass,
                "name": f"cws · {args.name}",
                "countryCode": args.proxy_country or "us",
            },
        )
        proxy_block = {"id": proxy.get("id") or proxy.get("data", {}).get("id")}
        time.sleep(1)
    print("[4/4] create profile …", file=sys.stderr)
    ua_value = ua if isinstance(ua, str) else ua.get("data") or ua.get("useragent") or fp.get("userAgent", "")
    body = {
        "name": args.name,
        "platform": platform,
        "platformVersion": args.platform_version or "10.15.7",
        "browserType": "anty",
        "fingerprint": fp,
        "useragent": {"mode": "manual", "value": ua_value},
        "tags": (args.tags or "").split(",") if args.tags else ["cws-studio"],
    }
    if proxy_block:
        body["proxy"] = proxy_block
    if args.folder:
        body["folderName"] = args.folder
    out = _req("POST", f"{CLOUD}/browser_profiles", body=body)
    print(json.dumps(out, indent=2))


def cmd_list(args):
    params = {"limit": args.limit or 50}
    if args.folder:
        params["folder"] = args.folder
    if args.query:
        params["query"] = args.query
    out = _req("GET", f"{CLOUD}/browser_profiles", params=params)
    print(json.dumps(out, indent=2))


def cmd_get(args):
    print(json.dumps(_req("GET", f"{CLOUD}/browser_profiles/{args.id}"), indent=2))


def cmd_update(args):
    body = json.loads(args.body) if args.body else {}
    print(json.dumps(_req("PATCH", f"{CLOUD}/browser_profiles/{args.id}", body=body), indent=2))


def cmd_delete(args):
    if not args.force:
        sys.exit("refusing to delete without --force (gate via cws-careful first)")
    print(json.dumps(_req("DELETE", f"{CLOUD}/browser_profiles/{args.id}",
                          body={"forceDelete": True}), indent=2))


def cmd_start(args):
    out = _req("GET", f"{LOCAL}/v1.0/browser_profiles/{args.id}/start",
               params={"automation": 1 if args.automation else None})
    print(json.dumps(out, indent=2))


def cmd_stop(args):
    out = _req("GET", f"{LOCAL}/v1.0/browser_profiles/{args.id}/stop")
    print(json.dumps(out, indent=2))


def cmd_export_cookies(args):
    out = _req("GET", f"{CLOUD}/cookies/export", params={"profileId": args.id})
    print(json.dumps(out, indent=2))


def cmd_import_cookies(args):
    cookies = json.load(open(args.file))
    out = _req("POST", f"{CLOUD}/cookies/import", body={"profileId": args.id, "cookies": cookies})
    print(json.dumps(out, indent=2))


def cmd_add_proxy(args):
    body = {
        "type": args.type,
        "host": args.host,
        "port": args.port,
        "login": args.login,
        "password": args.password,
        "name": args.name,
        "countryCode": args.country,
    }
    print(json.dumps(_req("POST", f"{CLOUD}/proxy", body=body), indent=2))


def cmd_list_proxies(args):
    print(json.dumps(_req("GET", f"{CLOUD}/proxy"), indent=2))


# ----- proxy parsing / bulk import ------------------------------------------

PROXY_SCHEMES = ("http", "https", "socks4", "socks5", "ssh")


def parse_proxy_line(line):
    """Parse one proxy line into a dict. Returns None for blank/comment lines.

    Accepted shapes (most-permissive parser):
      socks5://user:pass@host:port
      http://host:port
      host:port:user:pass
      host:port@user:pass
      user:pass@host:port
      host:port
    Any trailing fields separated by `|` are kept as a name hint, e.g.
      host:port:user:pass|us|provider-x
    """
    raw = line.strip()
    if not raw or raw.startswith("#"):
        return None

    extras = ""
    if "|" in raw:
        raw, extras = raw.split("|", 1)

    ptype = "http"
    for scheme in PROXY_SCHEMES:
        prefix = scheme + "://"
        if raw.lower().startswith(prefix):
            ptype = "socks5" if scheme in ("socks5", "socks4") and scheme == "socks5" else (
                scheme if scheme in ("socks5", "socks4", "ssh") else "http"
            )
            raw = raw[len(prefix):]
            break

    login = password = ""
    host = port = ""

    # Try colon-form first (host:port:user:pass). Common provider export shape;
    # passwords with `@` inside are common so handle this before @-form.
    parts = raw.split(":")
    if len(parts) >= 4 and parts[1].isdigit():
        host, port, login = parts[0], parts[1], parts[2]
        password = ":".join(parts[3:])
    elif len(parts) == 2 and parts[1].isdigit():
        host, port = parts
    elif "@" in raw:
        left, right = raw.rsplit("@", 1)
        # decide which side is creds vs host:port
        if ":" in right and right.rsplit(":", 1)[-1].isdigit():
            cred_part, hp = left, right
        elif ":" in left and left.rsplit(":", 1)[-1].isdigit():
            cred_part, hp = right, left
        else:
            return {"__err": f"unparseable proxy line: {line!r}"}
        if ":" in cred_part:
            login, password = cred_part.split(":", 1)
        else:
            login = cred_part
        host, port = hp.rsplit(":", 1)
    else:
        return {"__err": f"unparseable proxy line: {line!r}"}

    if not host or not port.isdigit():
        return {"__err": f"unparseable proxy line: {line!r}"}

    extras_parts = [p for p in extras.split("|") if p.strip()] if extras else []
    country = (extras_parts[0].strip() if extras_parts else "")
    provider = (extras_parts[1].strip() if len(extras_parts) > 1 else "")

    out = {
        "type": ptype,
        "host": host,
        "port": int(port),
        "name": f"cws · {host}:{port}",
    }
    if login:
        out["login"] = login
    if password:
        out["password"] = password
    if country:
        out["countryCode"] = country.lower()
    if provider:
        out["provider"] = provider
    return out


def cmd_bulk_add_proxies(args):
    lines = open(args.file).read().splitlines()
    parsed = [parse_proxy_line(l) for l in lines]
    parsed = [p for p in parsed if p is not None]
    errors = [p for p in parsed if "__err" in p]
    bodies = [p for p in parsed if "__err" not in p]

    if errors:
        for e in errors:
            print(e["__err"], file=sys.stderr)
        if args.strict:
            sys.exit(f"{len(errors)} unparseable lines (strict mode)")

    if args.dry_run:
        print(json.dumps({"would_create": bodies, "errors": errors}, indent=2))
        return

    out = []
    for i, body in enumerate(bodies, 1):
        print(f"[{i}/{len(bodies)}] add {body['host']}:{body['port']} …", file=sys.stderr)
        try:
            res = _req("POST", f"{CLOUD}/proxy", body=body)
            pid = res.get("id") or res.get("data", {}).get("id")
            out.append({"host": body["host"], "port": body["port"], "id": pid, "ok": True})
        except SystemExit as e:
            out.append({"host": body["host"], "port": body["port"], "ok": False, "error": str(e)})
        time.sleep(0.3)
    print(json.dumps(out, indent=2))


def cmd_check_proxy(args):
    """Validate a saved proxy by hitting an IP-echo through it via local agent.

    Requires local Dolphin agent (start it via `open -a 'Dolphin Anty'`).
    Falls back to plain HTTPS GET via urllib through the proxy if local agent
    is offline.
    """
    if args.id:
        proxies = _req("GET", f"{CLOUD}/proxy").get("data", [])
        match = [p for p in proxies if str(p.get("id")) == str(args.id)]
        if not match:
            sys.exit(f"proxy id {args.id} not found")
        p = match[0]
    else:
        p = {"type": args.type, "host": args.host, "port": args.port,
             "login": args.login, "password": args.password}

    scheme = "socks5" if p["type"].startswith("socks") else "http"
    auth = f"{p.get('login','')}:{p.get('password','')}@" if p.get("login") else ""
    url = f"{scheme}://{auth}{p['host']}:{p['port']}"
    handler = urllib.request.ProxyHandler({"http": url, "https": url})
    opener = urllib.request.build_opener(handler)
    try:
        with opener.open("https://ipinfo.io/json", timeout=10) as r:
            data = json.loads(r.read().decode())
        print(json.dumps({"ok": True, "ip": data.get("ip"),
                          "country": data.get("country"), "asn": data.get("org")}, indent=2))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, indent=2))
        sys.exit(1)


# ----- argparse --------------------------------------------------------------


def main():
    p = argparse.ArgumentParser(prog="dolphin-cli", description=__doc__.split("\n")[1])
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("status", help="check token + local-agent liveness")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("create", help="create a profile end-to-end")
    sp.add_argument("--name", required=True)
    sp.add_argument("--platform", default="macos", choices=["macos", "windows", "linux"])
    sp.add_argument("--browser-version", default=130, type=int)
    sp.add_argument("--platform-version", default="")
    sp.add_argument("--proxy-host")
    sp.add_argument("--proxy-port", type=int)
    sp.add_argument("--proxy-login")
    sp.add_argument("--proxy-pass")
    sp.add_argument("--proxy-country", default="us")
    sp.add_argument("--folder")
    sp.add_argument("--tags", help="comma-separated")
    sp.set_defaults(func=cmd_create)

    sp = sub.add_parser("list", help="list profiles")
    sp.add_argument("--folder")
    sp.add_argument("--query")
    sp.add_argument("--limit", type=int, default=50)
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("get", help="fetch one profile")
    sp.add_argument("id")
    sp.set_defaults(func=cmd_get)

    sp = sub.add_parser("update", help="PATCH a profile (raw JSON body)")
    sp.add_argument("id")
    sp.add_argument("--body", help="JSON object string")
    sp.set_defaults(func=cmd_update)

    sp = sub.add_parser("delete", help="delete a profile")
    sp.add_argument("id")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_delete)

    sp = sub.add_parser("start", help="start a profile via local agent")
    sp.add_argument("id")
    sp.add_argument("--automation", action="store_true")
    sp.set_defaults(func=cmd_start)

    sp = sub.add_parser("stop", help="stop a profile via local agent")
    sp.add_argument("id")
    sp.set_defaults(func=cmd_stop)

    sp = sub.add_parser("export-cookies", help="export cookies from profile")
    sp.add_argument("id")
    sp.set_defaults(func=cmd_export_cookies)

    sp = sub.add_parser("import-cookies", help="import cookies file into profile")
    sp.add_argument("id")
    sp.add_argument("--file", required=True)
    sp.set_defaults(func=cmd_import_cookies)

    sp = sub.add_parser("add-proxy", help="save a proxy to your library")
    sp.add_argument("--type", default="http")
    sp.add_argument("--host", required=True)
    sp.add_argument("--port", required=True, type=int)
    sp.add_argument("--login", required=True)
    sp.add_argument("--password", required=True)
    sp.add_argument("--name", required=True)
    sp.add_argument("--country", default="us")
    sp.set_defaults(func=cmd_add_proxy)

    sp = sub.add_parser("list-proxies", help="list saved proxies")
    sp.set_defaults(func=cmd_list_proxies)

    sp = sub.add_parser("bulk-add-proxies",
                        help="bulk-add proxies from a file (one per line; see parse_proxy_line)")
    sp.add_argument("--file", required=True)
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--strict", action="store_true", help="fail if any line is unparseable")
    sp.set_defaults(func=cmd_bulk_add_proxies)

    sp = sub.add_parser("check-proxy", help="validate a proxy by routing ipinfo.io through it")
    sp.add_argument("--id", help="id of a saved proxy")
    sp.add_argument("--type", default="http", choices=list(PROXY_SCHEMES))
    sp.add_argument("--host")
    sp.add_argument("--port", type=int)
    sp.add_argument("--login")
    sp.add_argument("--password")
    sp.set_defaults(func=cmd_check_proxy)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
