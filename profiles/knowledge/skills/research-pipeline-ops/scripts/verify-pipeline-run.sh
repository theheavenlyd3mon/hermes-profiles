#!/usr/bin/env bash
# verify-pipeline-run.sh — post-run verification for a wiki research-pipeline batch.
# Cron-friendly, macOS BSD-grep-safe (use -oE + tr, not character-class ranges).
# Usage: verify-pipeline-run.sh <wiki_root> <new_page...>
#   <wiki_root>    absolute path to the llm-wiki dir, e.g. /Users/noctis/Hermes Vault/Hermes/llm-wiki
#   <new_page...>  relative paths of every page created/updated this run, e.g. concepts/foo.md
# Checks: frontmatter completeness, >=2 outbound wikilinks resolving to existing slugs,
#         raw/ immutability (mtime), index.md entries for each new page.
# Exit 0 = all pass; exit 1 with a per-file failure list otherwise.
set -u

WIKI="${1:?usage: verify-pipeline-run.sh <wiki_root> <new_page...>}"
shift
PAGES=("$@")
: "${PAGES[0]:?usage: verify-pipeline-run.sh <wiki_root> <new_page...>}"
FAIL=0

echo "== wiki: $WIKI =="

# 1. Existing slugs for wikilink resolution (include operational subdirs for operational pages)
ls "$WIKI"/concepts/*.md "$WIKI"/entities/*.md "$WIKI"/comparisons/*.md \
   "$WIKI"/alloys/*.md "$WIKI"/queries/*.md \
   "$WIKI"/operational/protocols/*.md "$WIKI"/operational/conventions/*.md \
   "$WIKI"/operational/decisions/*.md 2>/dev/null \
  | sed 's|.*/||; s|\.md$||' | sort -u > /tmp/wiki_slugs_$$.txt
echo "existing slugs: $(wc -l < /tmp/wiki_slugs_$$.txt | tr -d ' ')"

# 2. Per-page frontmatter + wikilinks
for f in "${PAGES[@]}"; do
  [ -f "$WIKI/$f" ] || { echo "MISSING FILE: $f"; FAIL=1; continue; }
  fm=$(awk '/^---$/{n++} n==1{print} n==2{exit}' "$WIKI/$f")
  miss=""
  for k in title type created updated tags sources workflow confidence; do
    echo "$fm" | grep -q "^$k:" || miss="$miss $k"
  done
  [ -n "$miss" ] && { echo "FRONTMATTER MISSING in $f:$miss"; FAIL=1; }
  # workflow value must be one of the canonical lifecycle states
  wv=$(echo "$fm" | awk '/^workflow:/{gsub(/.*workflow:[[:space:]]*/,""); print; exit}')
  case "$wv" in
    seedling|developing|stable|needs-review|stale) ;;
    "") echo "WORKFLOW EMPTY in $f"; FAIL=1 ;;
    *) echo "WORKFLOW INVALID in $f: '$wv' (want seedling|developing|stable|needs-review|stale)"; FAIL=1 ;;
  esac
  # BSD-grep-safe wikilink extraction
  links=$(grep -oE '\[\[[^]]+\]\]' "$WIKI/$f" | tr -d '[]' | sort -u)
  n=$(echo "$links" | grep -c .)
  unres=""
  for l in $links; do
    base=$(echo "$l" | cut -d'#' -f1)
    grep -qx "$base" /tmp/wiki_slugs_$$.txt || unres="$unres [$l]"
  done
  [ "$n" -lt 2 ] && { echo "TOO FEW LINKS in $f ($n)"; FAIL=1; }
  [ -n "$unres" ] && { echo "UNRESOLVED LINKS in $f:$unres"; FAIL=1; }
  echo "ok: $f (links=$n)"
done

# 3. Raw immutability: no raw file modified on run date
today=$(date +%Y-%m-%d)
touched=$(find "$WIKI/raw" -type f -newermt "$today" 2>/dev/null)
if [ -n "$touched" ]; then
  echo "RAW MODIFIED TODAY (violates immutability):"
  echo "$touched"
  FAIL=1
else
  echo "ok: no raw/ files touched today"
fi

# 4. Index entries: each new page slug must appear in index.md
for f in "${PAGES[@]}"; do
  slug=$(basename "$f" .md)
  c=$(grep -c "\[\[$slug\]\]" "$WIKI/index.md")
  if [ "$c" -lt 1 ]; then echo "INDEX MISSING: $slug"; FAIL=1; fi
done
echo "ok: index entries present for all new pages"

rm -f /tmp/wiki_slugs_$$.txt
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
else
  echo "FAILURES: $FAIL"
  exit 1
fi
