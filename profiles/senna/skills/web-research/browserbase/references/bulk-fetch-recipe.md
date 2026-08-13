# Bulk fetch recipe (multi-page scraping via browse CLI)

Verified 2026-08-10 scraping diysolarforum.com (server-rendered XenForo — Fetch-friendly, free tier OK).

## One-liner fetch + extract

```bash
browse cloud fetch "$url" --format markdown 2>&1 | grep -v "Update available" | \
  python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("content",""))' > out.md
```

- `grep -v "Update available"` strips the CLI banner that otherwise breaks JSON parsing.
- Fetch returns a JSON object; the page text is in `.content` (markdown).

## Loop over many URLs

```bash
export BROWSERBASE_API_KEY=$(grep "^BROWSERBASE_API_KEY=" ~/.hermes/.env | sed 's/^BROWSERBASE_API_KEY=//')
mkdir -p /tmp/diy-solar-raw
declare -a urls=(
  "https://site.com/threads/foo.123/|name1"
  "https://site.com/forums/bar.52/|name2"
)
for entry in "${urls[@]}"; do
  url="${entry%%|*}"; name="${entry##*|}"
  browse cloud fetch "$url" --format markdown 2>&1 | grep -v "Update available" | \
    python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("content",""))' > "/tmp/diy-solar-raw/$name.md" 2>/dev/null
  echo "$name: $(wc -c < /tmp/diy-solar-raw/$name.md) bytes"
done
```

## Thread-title extraction (for listing pages)

```bash
grep -oE '\[[^]]{15,90}\]\(https://site\.com/threads/[^)]+' listing.md | sed 's/](https:\/\/site.com\/threads\// | /' | head -40
```

## Notes

- Public forums with server-rendered HTML (XenForo, phpBB, Discourse SSR) return clean markdown with no bot wall — prefer Fetch over spinning a browser session.
- Thread pages may carry ad/boilerplate at top and bottom; the educational content sits between the title and the "You must log in" footer.
- Some threads are just a video/link post (little text) — check byte size; tiny files mean nothing to read.
