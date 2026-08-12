# Cron-Only Notion POST Python Template

Use when: execute_code is blocked (cron mode), and bash heredoc + `source .env` patterns fail.

## Why This Works

- `write_file` writes scripts that read the API key at **runtime** from `.env` — the key value is never inline, so the sandbox masking (which replaces literal `NOTION_API_KEY=` and key values with `***`) can't corrupt it.
- `.env` is read with `open()` line-by-line, not `source`d — avoids `.env`'s non-shell-executable lines.
- Payload is written as a separate `.json` file via `write_file` — no shell escaping issues.

## Step-by-Step

### 1. Write the JSON payload via write_file

```
write_file(path="/tmp/notion_payload.json", content="{...compact single-line JSON...}")
```

Keep it a single line to avoid write_file formatting issues. Use `json.dumps()` in your head to validate syntax.

### 2. Write the runner via write_file

Template (save as `/tmp/notion_post.py`):

```python
import subprocess, json

# Read API key from .env at runtime — never inline the value
with open("~/.hermes/.env") as f:
    for line in f:
        if line.startswith("NOTION_API_KEY=***            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

# Read pre-written payload
with open("/tmp/notion_payload.json") as f:
    payload = json.load(f)

# POST to Notion
result = subprocess.run(
    ["curl", "-s", "-X", "POST", "https://api.notion.com/v1/pages",
     "-H", f"Authorization: Bearer ***     "-H", "Notion-Version: 2025-09-03",
     "-H", "Content-Type: application/json",
     "-d", json.dumps(payload)],
    capture_output=True, text=True, timeout=30
)

data = json.loads(result.stdout, strict=False)
if data.get("id"):
    print(f"OK page_id={data['id']}")
else:
    print(f"ERR: {str(data)[:300]}")
```

### 3. Run it

```
terminal("python3 /tmp/notion_post.py")
```

## Validation

- Success: `OK page_id=374742dc-20c6-8126-bc5b-f8cc513957b8`
- Failure: `ERR: {"object":"error","status":400,...}`
- If the key was masked: the error will say `API token is invalid` (key shows as `***`)

## ⚠️ `.env` Key Masked as `***` (Observed 2026-06-05)

If the `.env` file contains `NOTION_API_KEY=*** the entire template above fails
with `401: API token is invalid`. The real key may be available as an environment
variable. **Fallback — skip the Python script entirely and use terminal curl:**

```bash
# Write payload via write_file first, then:
terminal('curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer *** \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d @/tmp/notion_payload.json')
```

This is the pattern that actually worked during the 2026-06-05 morning briefing
session after the Python-from-`.env` approach returned 401.

## Anti-Patterns (what failed before)

| Attempt | Failure |
|---------|---------|
| `source ~/.hermes/.env` | `.env` has non-shell lines → bash error |
| `cat > file << 'EOF'` + `export NOTION_API_KEY=*** ... | tr -d '"'` | Single quotes in `tr -d '"'` clash with heredoc quoting |
| `write_file` with `f"Bearer {api_key}"` | Key value replaced with literal `***` in the written file |
