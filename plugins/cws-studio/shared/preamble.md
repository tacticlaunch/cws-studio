# Standard Preamble (run first in every cws-studio skill)

Run this bash block at the start of every skill invocation. It loads the
per-project slug, prior learnings, branch, and config. Skills route off the
echoed values that follow.

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/cws-studio/cws-studio/2.3.0}"
BIN="$PLUGIN_ROOT/bin"
eval "$("$BIN/cws-slug" 2>/dev/null)"
_BRANCH=$(git branch --show-current 2>/dev/null || echo "no-git")
_SESSION_ID="$$-$(date +%s)"
mkdir -p "$CWS_PROJECT_DIR" 2>/dev/null
_PROACTIVE=$("$BIN/cws-config" get proactive 2>/dev/null)
[ -z "$_PROACTIVE" ] && _PROACTIVE=true
_EXPLAIN_LEVEL=$("$BIN/cws-config" get explain_level 2>/dev/null)
[ -z "$_EXPLAIN_LEVEL" ] && _EXPLAIN_LEVEL=default
echo "SLUG: $SLUG"
echo "BRANCH: $_BRANCH"
echo "PROACTIVE: $_PROACTIVE"
echo "EXPLAIN_LEVEL: $_EXPLAIN_LEVEL"
_LEARN_FILE="$CWS_PROJECT_DIR/learnings.jsonl"
if [ -f "$_LEARN_FILE" ]; then
  _LC=$(wc -l < "$_LEARN_FILE" | tr -d ' ')
  echo "LEARNINGS: $_LC entries loaded"
  if [ "$_LC" -gt 3 ] 2>/dev/null; then
    "$BIN/cws-learnings-search" --limit 3
  fi
else
  echo "LEARNINGS: 0"
fi
_STATE_FILE="./.cws/state.json"
if [ -f "$_STATE_FILE" ]; then
  echo "CWS_STATE: present"
  /usr/bin/python3 -c "import json; d=json.load(open('$_STATE_FILE')); print('CURRENT_STAGE:', d.get('current_stage','none')); print('GATES_PASSED:', ','.join(d.get('gates_passed',[])) or 'none')"
else
  echo "CWS_STATE: missing"
fi
"$BIN/cws-timeline-log" "{\"skill\":\"<this-skill>\",\"event\":\"started\",\"branch\":\"$_BRANCH\",\"session\":\"$_SESSION_ID\"}" 2>/dev/null
```

Replace `<this-skill>` with the actual skill name (e.g. `cws-idea`).

After running, the calling skill reads these echoed values to branch:

- `CWS_STATE: missing` → route to `cws-init` first if appropriate.
- `LEARNINGS: <n> entries loaded` → surface the 3 printed entries before any decision.
- `EXPLAIN_LEVEL: terse` → drop glosses and outcome-framing; shorter prose.
- `PROACTIVE: false` → don't auto-suggest the next skill; ask first.
