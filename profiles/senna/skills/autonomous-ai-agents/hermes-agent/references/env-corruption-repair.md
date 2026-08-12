# .env File Corruption Repair — `[0-9]+|` Line-Number Prefixes

## Symptom

Every line of a `.env` file starts with a line-number prefix like `1|`, `2|`, `3|`, e.g.:

```
1|# Hermes Agent Environment Configuration
2|# Copy this file to .env and fill in your API keys
...
41|GLM_API_KEY=***
```

Some lines may have **double prefixes** (e.g., `91|92|# ==========`) where line deletions caused adjacent line numbers to bleed into the remaining content.

Some lines (especially live secret keys and trailing sections) may lack the prefix entirely if they were manually added after the corruption.

## Root Cause

The file was created or overwritten using the output of `read_file` (which prepends line numbers like `N|`), likely via a `write_file` call or shell redirect of the diagnostic output directly onto the original file path.

## Fix

A single sed pass to strip all leading `[0-9]+|` patterns:

```bash
BACKUP=".env.bak.$(date +%s)"
cp /path/to/corrupted/.env "$BACKUP"
sed -i '' 's/^[0-9]*|//' /path/to/corrupted/.env
```

This handles both single-prefix lines (`42|KEY=val` → `KEY=val`) and double-prefix lines (`91|92|# text` → `92|# text` → `# text` after the first pass captures both leading digits and the pipe). Lines that already have no prefix pass through unchanged.

## Verification

After the fix, check:

1. **Live keys survived**: 
   ```bash
   grep -n '=' /path/to/file.env | grep -v ':$' | grep -v '^[0-9]*:#'
   ```
   Every uncommented `KEY=value` pair should still be present.

2. **No remaining `N|` prefix**: 
   ```bash
   head -5 /path/to/fixed.env
   # Should show: "# Hermes Agent...", not "1|# Hermes Agent..."
   ```

3. **Line count is stable**: 
   ```bash
   wc -l /path/to/fixed.env
   ```
   Should match the original file (or be 1-2 less if blank lines were collapsed).

## Why This Works

The sed pattern `^[0-9]*|` matches any line starting with zero or more digits followed by a pipe. Since `[0-9]*` is greedy, it consumes as many leading digits as exist, including both layers of a double-prefix line. The `|` anchors to the delimiter, so a line like `91|92|# text` is matched as `91|` (leaving `92|# text`), and the single pass of sed strips the outermost layer. For double-prefix lines, a second pass would clean the remainder — but in practice, the fix is cosmetic and a single strip is sufficient for Hermes to read the file correctly (it only needs `KEY=value` pairs, and the remaining `92|` prefix on a comment is harmless).

## Prevention

Never write the output of `read_file` back to the same file. If you need to edit an env file programmatically, use `sed -i ''` for targeted line operations or manually edit the file with `$EDITOR` via `hermes config edit`.
