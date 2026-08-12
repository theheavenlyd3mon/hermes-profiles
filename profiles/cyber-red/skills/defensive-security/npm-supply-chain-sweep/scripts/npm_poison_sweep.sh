#!/bin/bash
# npm_poison_sweep.sh — sweep a dev machine for known-poisoned npm package versions.
# Usage: npm_poison_sweep.sh <pkg>@<poisoned-version> [<pkg>@<version> ...]
#   e.g. npm_poison_sweep.sh keyv@6.0.0 file-entry-cache@11.1.6 cache-manager@7.2.10
# Read-only. Prints HIT lines (installed copy matches poisoned version), CLEAN
# lines (other versions), cache findings, dropper-artifact search, and the
# poisoned version's registry publish timestamp for the timing-proof.
set -u
HOME_DIR="${HOME}"
if [ "$#" -eq 0 ]; then
  echo "usage: $0 pkg@poisoned-version [pkg@version ...]" >&2
  exit 2
fi

echo "=== tooling ==="
for t in node npm bun; do printf '%s: ' "$t"; command -v "$t" >/dev/null 2>&1 && "$t" --version 2>/dev/null || echo 'not installed'; done
echo "npm registry: $(npm config get registry 2>/dev/null)"

echo
echo "=== lockfiles (home, excl Library/.hermes/node_modules) ==="
LOCKFILES=$(find "$HOME_DIR" -maxdepth 7 \( -name package-lock.json -o -name yarn.lock -o -name pnpm-lock.yaml -o -name bun.lock -o -name bun.lockb -o -name npm-shrinkwrap.json \) -not -path '*/Library/*' -not -path '*/.hermes/*' -not -path '*/node_modules/*' 2>/dev/null)
echo "$LOCKFILES" | grep -c . | sed 's/^/count: /'

for SPEC in "$@"; do
  PKG="${SPEC%@*}"; VER="${SPEC#*@}"
  echo
  echo "##### $SPEC #####"

  echo "-- lockfile references for '$PKG' --"
  if [ -n "$LOCKFILES" ]; then
    # shellcheck disable=SC2086
    grep -nE "node_modules/$PKG\"|/$PKG-|$PKG@|\"$PKG\"" $LOCKFILES 2>/dev/null | head -15
  fi

  echo "-- installed copies (name + version + scripts) --"
  COPIES=$(find "$HOME_DIR" -maxdepth 9 -type d \( -path "*/node_modules/$PKG" -o -path "*/node_modules/@*/$PKG" \) -not -path '*/Library/*' -not -path '*/.hermes/*' 2>/dev/null)
  if [ -z "$COPIES" ]; then
    echo "  (no installed copy found)"
  else
    while IFS= read -r d; do
      [ -f "$d/package.json" ] || continue
      v=$(python3 -c "import json;print(json.load(open('$d/package.json')).get('version','?'))" 2>/dev/null)
      s=$(python3 -c "import json;print(json.dumps(json.load(open('$d/package.json')).get('scripts',{})))" 2>/dev/null)
      if [ "$v" = "$VER" ]; then
        echo "  HIT (POISONED VERSION): $v  $d"
        echo "    scripts: $s"
      else
        echo "  clean: $v  $d"
      fi
    done <<< "$COPIES"
  fi

  echo "-- npm cache for '$PKG' (poisoned tarball = exposure even after reinstall) --"
  CACHE=$(npm cache ls "$PKG" 2>/dev/null | grep -oE "$PKG/-/$PKG-[^ ]+\.tgz" | sort -u)
  echo "$CACHE" | sed 's/^/  /'
  echo "$CACHE" | grep -q "$VER" && echo "  ^ CACHE CONTAINS POISONED VERSION"

  echo "-- registry publish time for poisoned $VER --"
  curl -s "https://registry.npmjs.org/$PKG" | python3 -c "import json,sys; d=json.load(sys.stdin); t=d.get('time',{}); print('  $VER published:', t.get('$VER','n/a'))"
  echo "  (compare against install timestamps: ls -laT <dir>/package.json)"
done

echo
echo "=== dropper artifacts in node_modules (setup.mjs / Math_*.js / preinstall*) ==="
find "$HOME_DIR" -maxdepth 10 -path '*/node_modules/*' \( -name 'setup.mjs' -o -name 'Math_*.js' -o -name 'preinstall*' \) -not -path '*/Library/*' -not -path '*/.hermes/*' 2>/dev/null | head -20
echo "(end)"
