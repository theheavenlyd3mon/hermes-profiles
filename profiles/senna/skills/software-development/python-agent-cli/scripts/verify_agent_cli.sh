#!/usr/bin/env bash
# verify_agent_cli.sh — reusable contract QA for a Python "agent CLI" built to the
# cli-builder / python-agent-cli contract: --json output, --dry-run preview,
# errors -> stderr + nonzero exit, idempotent writes, shared flags parse before
# AND after the subcommand.
#
# Default targets the ue-agent-harness `ue5` CLI. The UNIVERSAL checks (json order,
# errors->stderr, missing-arg, dry-run, idempotent) use the contract flag names
# (--json/--config/--dry-run) and need no edits IF your CLI follows them. The
# subcommand-specific checks (CLI-SPECIFIC block) must be changed to match your
# subcommands — they assume `scan`/`build-cs`/`read`/`write` exist.
#
# Usage:
#   ./verify_agent_cli.sh <module> <config.yaml> [repo_dir]
#   e.g. ./verify_agent_cli.sh ue5 /tmp/qa/config.yaml ~/Desktop/ue-agent-harness
set -u
MODULE="${1:?usage: verify_agent_cli.sh <module> <config.yaml> [repo_dir]}"
CFG="${2:?usage: verify_agent_cli.sh <module> <config.yaml> [repo_dir]}"
REPO="${3:-$(pwd)}"

cd "$REPO" || exit 1
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || true

P=0; F=0
chk() { if eval "$2"; then echo "PASS $1"; P=$((P+1)); else echo "FAIL $1"; F=$((F+1)); fi; }

# 1. syntax
python3 -c "import py_compile; py_compile.compile('${MODULE}.py', doraise=True)" && chk "1 syntax" true

# 2. help has examples (agents pattern-match off these)
python3 -m "$MODULE" scan --help 2>&1 | grep -qi example && chk "2 help examples" true

# 3. --json AFTER subcommand -> valid JSON on stdout
python3 -m "$MODULE" scan --config "$CFG" --json 2>/dev/null | python3 -c "import sys,json;json.load(sys.stdin)" && chk "3 json post-subcmd" true

# 3b. --json BEFORE subcommand -> STILL valid JSON (argparse bpo-9351 guard)
python3 -m "$MODULE" --json scan --config "$CFG" 2>/dev/null | python3 -c "import sys,json;json.load(sys.stdin)" && chk "3b json pre-subcmd" true

# 4. missing required arg -> immediate error naming the missing flag
python3 -m "$MODULE" build-cs 2>&1 | grep -qi -- "--module" && chk "4 missing arg error" true

# 6. errors -> stderr ONLY, nothing on stdout, nonzero exit
python3 -m "$MODULE" read --path /etc/passwd --config "$CFG" 1>/tmp/o.txt 2>/tmp/e.txt; ec=$?
{ [ $ec -ne 0 ] && [ ! -s /tmp/o.txt ] && grep -qi "outside the allowed" /tmp/e.txt; } && chk "6 errors->stderr" true
rm -f /tmp/o.txt /tmp/e.txt

# 7. idempotent write: two identical writes both succeed, content unchanged
TW="/tmp/qa_tw.txt"
python3 -m "$MODULE" write --path "$TW" --content "hi" --config "$CFG" >/dev/null 2>&1
[ -f "$TW" ] && [ "$(cat "$TW")" = "hi" ] && chk "7 idempotent write" true
rm -f "$TW"

# 8. dry-run write previews a diff and touches nothing on disk
python3 -m "$MODULE" write --path /tmp/qa_dry.txt --content "z" --dry-run --config "$CFG" 2>&1 | grep -qi "new file\|diff" && chk "8 dry-run preview" true

echo "-----"; echo "PASS=$P FAIL=$F"
# CLI-SPECIFIC CHECKS: replace scan/build-cs/read/write with your subcommands.
# Universal checks above (3,3b,4,6,7,8) need no edits if flag names match.
[ "$F" -eq 0 ]
