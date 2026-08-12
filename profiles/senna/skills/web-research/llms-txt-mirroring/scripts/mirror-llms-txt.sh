#!/bin/bash
# Mirror every page listed in an llms.txt catalog to local Markdown.
# Usage: mirror-llms-txt.sh <llms.txt-url> [dest_dir]
#   dest_dir defaults to ./agentwikis-mirror (relative to cwd).
# Verified: pulled 1,479 pages / 51 wikis from agentwikis.com in ~37s, 0 failures.
set -u

LLMS_URL="${1:?usage: mirror-llms-txt.sh <llms.txt-url> [dest_dir]}"
DEST="${2:-./agentwikis-mirror}"
mkdir -p "$DEST/raw"
cd "$DEST" || exit 1

# 1. Catalog
curl -s --max-time 30 "$LLMS_URL" -o catalog-llms.txt
echo "catalog bytes: $(wc -c < catalog-llms.txt)"

# 2. Extract raw page paths (per-wiki llms.txt: /wiki/<slug>/llms.txt also works)
grep -o '/raw/[a-z0-9-]*/[^)]*\.md' catalog-llms.txt | sort -u > all-pages.txt
TOTAL=$(wc -l < all-pages.txt | tr -d ' ')
echo "expected pages: $TOTAL"

# 3. Parallel download — build "url|dest" queue, 12 workers
: > queue.txt
while read -r p; do
  dest="raw${p#/raw}"
  echo "https://agentwikis.com${p}|${dest}" >> queue.txt
done < all-pages.txt

fetch() {
  line="$1"
  url="${line%%|*}"
  dest="${line#*|}"
  mkdir -p "$(dirname "$dest")"
  curl -s --max-time 30 --retry 2 "$url" -o "$dest" || echo "FAIL $url"
}
export -f fetch
cat queue.txt | xargs -P 12 -n 1 -I{} bash -c 'fetch "$1"' _ {}
echo "download pass done"

# 4. Verify
FOUND=$(find raw -name '*.md' | wc -l | tr -d ' ')
ZERO=$(find raw -name '*.md' -size 0 | wc -l | tr -d ' ')
echo "downloaded .md: $FOUND / expected $TOTAL"
echo "zero-byte files: $ZERO"
[ "$FOUND" -eq "$TOTAL" ] && [ "$ZERO" -eq 0 ] && echo "MIRROR OK" || echo "MIRROR INCOMPLETE — inspect above"
