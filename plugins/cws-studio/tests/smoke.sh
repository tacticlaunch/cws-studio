#!/usr/bin/env bash
# smoke.sh — exercise cws-studio bin helpers + dolphin-cli (no network calls).
#
# Run:  bash plugins/cws-studio/tests/smoke.sh
# Exit code = number of failed tests.

set -u

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="$PLUGIN_ROOT/bin"
DOLPHIN_CLI="$PLUGIN_ROOT/skills/cws-dolphin/references/dolphin-cli.py"

TESTS_PASS=0
TESTS_FAIL=0
FAILED_NAMES=()

# Throwaway workspace — cleaned at exit.
WORK=$(mktemp -d /tmp/cws-test-XXXXXX)
trap 'rm -rf "$WORK"' EXIT

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then
    printf "  ok   %s\n" "$label"
  else
    printf "  FAIL %s\n       expected=%q\n       actual  =%q\n" "$label" "$expected" "$actual"
    return 1
  fi
}

assert_contains() {
  local label="$1" needle="$2" haystack="$3"
  if printf '%s' "$haystack" | grep -qF -- "$needle"; then
    printf "  ok   %s\n" "$label"
  else
    printf "  FAIL %s\n       needle=%q\n       in    =%q\n" "$label" "$needle" "$haystack"
    return 1
  fi
}

assert_true() {
  local label="$1"
  shift
  if "$@"; then
    printf "  ok   %s\n" "$label"
  else
    printf "  FAIL %s  (cmd: %s)\n" "$label" "$*"
    return 1
  fi
}

run_test() {
  local name="$1"
  printf "\n== %s ==\n" "$name"
  if "$name"; then
    TESTS_PASS=$((TESTS_PASS + 1))
  else
    TESTS_FAIL=$((TESTS_FAIL + 1))
    FAILED_NAMES+=("$name")
  fi
}

# ---------- 1. cws-slug -----------------------------------------------------

test_cws_slug() {
  local repo="$WORK/repo-one"
  mkdir -p "$repo"
  ( cd "$repo" && git init -q && git config user.email t@t && git config user.name t )
  local out
  out=$( cd "$repo" && CWS_HOME="$WORK/home" "$BIN/cws-slug" ) || return 1

  assert_contains "emits SLUG=" "SLUG=" "$out" || return 1
  assert_contains "emits CWS_HOME=" "CWS_HOME=" "$out" || return 1
  assert_contains "emits CWS_PROJECT_DIR=" "CWS_PROJECT_DIR=" "$out" || return 1

  # SLUG should be repo dir basename lowercased.
  assert_contains "slug = repo dir basename" "SLUG=repo-one" "$out" || return 1
  assert_contains "CWS_HOME honored" "CWS_HOME=$WORK/home" "$out" || return 1
  assert_contains "project dir derived" "CWS_PROJECT_DIR=$WORK/home/projects/repo-one" "$out" || return 1

  # The output must `eval` cleanly in a subshell.
  (
    eval "$out"
    [ "$SLUG" = "repo-one" ] && \
    [ "$CWS_HOME" = "$WORK/home" ] && \
    [ "$CWS_PROJECT_DIR" = "$WORK/home/projects/repo-one" ]
  ) || { echo "       FAIL eval round-trip"; return 1; }
  printf "  ok   eval round-trip\n"
}

# ---------- 2. cws-config ---------------------------------------------------

test_cws_config() {
  local home="$WORK/cfg"
  export CWS_HOME="$home"

  "$BIN/cws-config" set foo bar >/dev/null || return 1
  local v
  v=$("$BIN/cws-config" get foo)
  assert_eq "get returns value" "bar" "$v" || return 1

  v=$("$BIN/cws-config" get nonexistent)
  assert_eq "get nonexistent = empty (no error)" "" "$v" || return 1

  local list
  list=$("$BIN/cws-config" list)
  assert_contains "list returns JSON object" "\"foo\"" "$list" || return 1
  # Validate JSON well-formedness.
  /usr/bin/python3 -c "import json,sys; json.loads(sys.stdin.read())" <<< "$list" \
    || { echo "       FAIL list output not valid JSON"; return 1; }
  printf "  ok   list output is valid JSON\n"

  # Overwrite an existing key.
  "$BIN/cws-config" set foo baz >/dev/null
  v=$("$BIN/cws-config" get foo)
  assert_eq "set overwrites" "baz" "$v" || return 1

  unset CWS_HOME
}

# ---------- 3. cws-learnings-search -----------------------------------------

test_cws_learnings_search() {
  local repo="$WORK/repo-learn"
  mkdir -p "$repo"
  ( cd "$repo" && git init -q && git config user.email t@t && git config user.name t )
  local home="$WORK/home-learn"
  export CWS_HOME="$home"

  # Empty / missing → exit 0, no output.
  local out
  out=$( cd "$repo" && "$BIN/cws-learnings-search" )
  local code=$?
  assert_eq "missing learnings → exit 0" "0" "$code" || return 1
  assert_eq "missing learnings → empty out" "" "$out" || return 1

  # Seed learnings.
  local pd="$home/projects/repo-learn"
  mkdir -p "$pd"
  local f="$pd/learnings.jsonl"
  for i in 1 2 3 4 5 6 7; do
    echo "{\"n\":$i,\"stage\":\"idea\",\"msg\":\"entry-$i\"}" >> "$f"
  done
  echo '{"n":8,"stage":"build","msg":"build-thing"}' >> "$f"

  # Default limit=5 → last 5 lines.
  out=$( cd "$repo" && "$BIN/cws-learnings-search" )
  local n_lines
  n_lines=$(printf '%s\n' "$out" | grep -c '^{')
  assert_eq "default limit returns 5 entries" "5" "$n_lines" || return 1
  assert_contains "last entry is build-thing" "build-thing" "$out" || return 1

  # --limit 2 → 2 lines.
  out=$( cd "$repo" && "$BIN/cws-learnings-search" --limit 2 )
  n_lines=$(printf '%s\n' "$out" | grep -c '^{')
  assert_eq "--limit 2 returns 2" "2" "$n_lines" || return 1

  # --stage build → only build entry.
  out=$( cd "$repo" && "$BIN/cws-learnings-search" --stage build --limit 10 )
  assert_contains "--stage build filters" "build-thing" "$out" || return 1
  if printf '%s' "$out" | grep -q '"stage":"idea"'; then
    echo "       FAIL --stage build leaked idea entries"
    return 1
  fi
  printf "  ok   --stage build excludes idea\n"

  # --grep entry-3
  out=$( cd "$repo" && "$BIN/cws-learnings-search" --grep entry-3 --limit 10 )
  assert_contains "--grep matches" "entry-3" "$out" || return 1

  unset CWS_HOME
}

# ---------- 4. cws-timeline-log ---------------------------------------------

test_cws_timeline_log() {
  local repo="$WORK/repo-timeline"
  mkdir -p "$repo"
  ( cd "$repo" && git init -q && git config user.email t@t && git config user.name t )
  local home="$WORK/home-timeline"
  export CWS_HOME="$home"

  ( cd "$repo" && "$BIN/cws-timeline-log" '{"skill":"cws-idea","event":"started"}' ) || return 1
  ( cd "$repo" && "$BIN/cws-timeline-log" '{}' ) || return 1
  ( cd "$repo" && "$BIN/cws-timeline-log" ) || return 1   # empty arg defaults to {}

  local f="$home/projects/repo-timeline/timeline.jsonl"
  [ -f "$f" ] || { echo "       FAIL timeline.jsonl not created"; return 1; }
  printf "  ok   timeline.jsonl created\n"

  local n
  n=$(wc -l < "$f" | tr -d ' ')
  assert_eq "three appended lines" "3" "$n" || return 1

  # Each line is valid JSON with a ts field.
  /usr/bin/python3 -c "
import json,sys
for ln in open('$f'):
    d=json.loads(ln)
    assert 'ts' in d, 'ts missing in '+ln
print('ok')
" >/dev/null || { echo "       FAIL JSON / ts validation"; return 1; }
  printf "  ok   every line valid JSON with ts field\n"

  unset CWS_HOME
}

# ---------- 5. dolphin-cli --------------------------------------------------

test_dolphin_cli_syntax() {
  /usr/bin/python3 -c "import ast; ast.parse(open('$DOLPHIN_CLI').read())" \
    && printf "  ok   AST parse\n" \
    || { echo "       FAIL syntax error"; return 1; }
}

test_dolphin_cli_help() {
  local out
  out=$(/usr/bin/python3 "$DOLPHIN_CLI" --help 2>&1)
  local code=$?
  assert_eq "--help exits 0" "0" "$code" || return 1
  for sub in status create list get update delete start stop \
             export-cookies import-cookies add-proxy list-proxies \
             bulk-add-proxies check-proxy proxies-suggest proxy6-buy; do
    assert_contains "lists subcommand $sub" "$sub" "$out" || return 1
  done
}

test_dolphin_cli_proxies_suggest() {
  # No token, no network — pure print.
  local out
  out=$(/usr/bin/python3 "$DOLPHIN_CLI" proxies-suggest 2>&1)
  local code=$?
  assert_eq "proxies-suggest exits 0" "0" "$code" || return 1
  assert_contains "lists Space Proxy" "Space Proxy" "$out" || return 1
  assert_contains "lists Proxy6" "Proxy6" "$out" || return 1
  assert_contains "lists iProxy.online" "iProxy.online" "$out" || return 1
}

test_dolphin_cli_proxy6_buy_no_key() {
  # Ensure PROXY6_API_KEY is unset.
  ( unset PROXY6_API_KEY
    out=$(/usr/bin/python3 "$DOLPHIN_CLI" proxy6-buy 2>&1)
    code=$?
    [ "$code" != "0" ] || { echo "       FAIL expected non-zero exit"; exit 1; }
    printf '%s' "$out" | grep -q "PROXY6_API_KEY not set" \
      || { echo "       FAIL missing error message; got: $out"; exit 1; }
    echo "  ok   exits with PROXY6_API_KEY error"
  ) || return 1
}

test_dolphin_cli_delete_force_delete() {
  # Source-level regression: cmd_delete must POST forceDelete:True.
  grep -q 'forceDelete' "$DOLPHIN_CLI" \
    && printf "  ok   forceDelete token present in source\n" \
    || { echo "       FAIL forceDelete missing from cmd_delete"; return 1; }
  # And the body shape is {"forceDelete": True}.
  grep -q '"forceDelete": True' "$DOLPHIN_CLI" \
    && printf "  ok   delete body = {forceDelete:True}\n" \
    || { echo "       FAIL expected literal forceDelete: True"; return 1; }
}

test_dolphin_cli_create_minimal_payload() {
  # Regression for "Undefined array key mode" 500s: payload must include
  # useragent:{mode:manual,...} and must NOT include the bloated cpu/memory/
  # audio/etc. mode-object blocks.
  grep -q '"useragent": {"mode": "manual"' "$DOLPHIN_CLI" \
    && printf "  ok   useragent.mode=manual present\n" \
    || { echo "       FAIL useragent block missing"; return 1; }
  for bad in '"cpu":' '"memory":' '"audio":' '"webgl":' '"canvas":'; do
    if grep -E "\"(cpu|memory|audio|webgl|canvas)\": *\{ *\"mode\"" "$DOLPHIN_CLI" >/dev/null 2>&1; then
      echo "       FAIL bloated mode-object detected: $bad"
      return 1
    fi
  done
  printf "  ok   no bloated mode-object blocks\n"
}

test_dolphin_cli_bulk_parser_formats() {
  local fixture="$WORK/proxies.txt"
  cat > "$fixture" <<EOF
# four shapes the parser must handle
1.2.3.4:8080:alice:secret
bob:hunter2@5.6.7.8:9090
socks5://carol:pw@9.10.11.12:1080
13.14.15.16:3128
EOF
  local out
  out=$(/usr/bin/python3 "$DOLPHIN_CLI" bulk-add-proxies --file "$fixture" --dry-run 2>&1)
  local code=$?
  assert_eq "bulk-add-proxies --dry-run exits 0" "0" "$code" || return 1
  # Validate would_create contains all four hosts.
  for host in 1.2.3.4 5.6.7.8 9.10.11.12 13.14.15.16; do
    assert_contains "parsed $host" "\"host\": \"$host\"" "$out" || return 1
  done
  # First three must carry credentials.
  assert_contains "alice login parsed" "\"login\": \"alice\"" "$out" || return 1
  assert_contains "bob login parsed" "\"login\": \"bob\"" "$out" || return 1
  assert_contains "carol login parsed" "\"login\": \"carol\"" "$out" || return 1
  # socks5 scheme honored.
  assert_contains "socks5 type honored" "\"type\": \"socks5\"" "$out" || return 1
}

# ---------- main ------------------------------------------------------------

run_test test_cws_slug
run_test test_cws_config
run_test test_cws_learnings_search
run_test test_cws_timeline_log
run_test test_dolphin_cli_syntax
run_test test_dolphin_cli_help
run_test test_dolphin_cli_proxies_suggest
run_test test_dolphin_cli_proxy6_buy_no_key
run_test test_dolphin_cli_delete_force_delete
run_test test_dolphin_cli_create_minimal_payload
run_test test_dolphin_cli_bulk_parser_formats

echo
echo "================================================"
echo "PASS: $TESTS_PASS, FAIL: $TESTS_FAIL"
if [ "$TESTS_FAIL" -gt 0 ]; then
  echo "Failed: ${FAILED_NAMES[*]}"
fi
echo "================================================"
exit "$TESTS_FAIL"
