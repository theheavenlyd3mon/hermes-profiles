# JSON Parsing in execute_code (merged from `execute-code-json-parsing`)

When `execute_code` scripts need to parse JSON files, three common approaches fail:

## The Three Failure Modes

1. **`read_file()` + `json.loads()`** — FAILS because `read_file()` prepends line numbers (`1|{...}`), which is not valid JSON
2. **`terminal("cat file.json")` + `json.loads()`** — FAILS because terminal stdout may contain control characters that break `strict=True` parsing
3. **`json_parse()`** — Still fragile: fails on null bytes, truncated output, encoding mismatches

## The Reliable Path: `jq`

```python
from hermes_tools import terminal

# Structure check
result = terminal("jq 'keys' /path/to/file.json")

# Extract specific fields
result = terminal("jq '.repos[] | {name, score, label}' /path/to/file.json")

# Filter and sort
result = terminal("""jq '[.repos[] | select(.label == "ADOPT")] | sort_by(-.score) | .[0:5]' /path/to/file.json""")

# Count items
result = terminal("jq '.items | length' /path/to/file.json")
```

**Why jq always works:** handles control characters, UTF-8/BOM, arbitrarily large files (streaming parser), built into macOS and most Linux.

## Quick Reference

| Scenario | Approach |
|---|---|
| Read JSON file in execute_code | `terminal("jq ...")` |
| Read small JSON (<100 lines, trusted) | `terminal("cat")` + `json_parse()` may work |
| Read non-JSON text file | `read_file()` (line numbers are fine for text) |
| Parse API response in memory | `json.loads()` or `json_parse()` |
| Transform/filter JSON data | `terminal("jq '...' file.json")` |

## Pitfalls

- `read_file` is for TEXT, not JSON — the line-number prefix breaks structured data
- Don't parse-then-filter when jq can filter-then-parse (save tokens on large files)
- Terminal stdout cap is 50KB — use jq to narrow output first on large files
- jq not installed? `brew install jq` (macOS) or `apt install jq` (Linux)
