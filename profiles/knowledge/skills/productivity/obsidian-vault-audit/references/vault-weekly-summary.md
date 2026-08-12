# Vault Weekly Summary Pattern

Run a weekly health check on the Obsidian vault — created/modified notes, attention items, and overall stats. Designed for cron automation. Logs results to Notion Agent Logbook.

## Checklist

1. **Notes created in last 7 days** — use macOS `stat` birth time, not `-newermt` (which checks mtime, not creation):
   ```bash
   find "$VAULT" -name "*.md" -not -path "*/.obsidian/*" -not -path "*/4-Archive/*" \
     -exec stat -f '%SB %N' -t '%Y-%m-%d' {} \; | \
     awk -F' ' '$1 >= "YYYY-MM-DD" && $1 <= "YYYY-MM-DD"' | sort | uniq
   ```
   On Linux, use `stat -c '%W %n'` (birth time in epoch seconds).

2. **Notes modified in last 7 days** — use `-newermt` or `stat -f '%m'`:
   ```bash
   find "$VAULT" -name "*.md" -not -path "*/.obsidian/*" -not -path "*/4-Archive/*" \
     -newermt "$(date -v-7d +%Y-%m-%d)" -exec stat -f '%m %N' {} \; | sort -rn
   ```

3. **Notes needing attention:**
   - Inbox: `ls "$VAULT/0-Inbox/"` or `"$VAULT/Inbox/"` — flag if non-empty
   - `notes/` directory: should exist but being empty is OK (ready for agent captures)
   - Untitled files: `find "$VAULT" -name "Untitled*" -not -path "*/.obsidian/*"`
   - Empty directories: `find "$VAULT" -type d -empty -not -path "*/.obsidian/*" -not -path "*/.git/*"`
   - Untagged wiki files: `find "$VAULT/llm-wiki" -name "*.md" -exec grep -L '^tags:' {} \;` — filter out structural files (SCHEMA.md, index.md, log.md) and raw/ source material

4. **Overall stats:**
   ```bash
   # Active notes (excl. archive + .obsidian)
   find "$VAULT" -name "*.md" -not -path "*/.obsidian/*" -not -path "*/4-Archive/*" | wc -l
   # Total
   find "$VAULT" -name "*.md" -not -path "*/.obsidian/*" | wc -l
   # By directory
   find "$VAULT" -name "*.md" -not -path "*/.obsidian/*" -not -path "*/4-Archive/*" | \
     sed 's|/[^/]*$||' | sort | uniq -c | sort -rn
   # Wikilink graph (top linked concepts)
   find "$VAULT" -name "*.md" -not -path "*/.obsidian/*" -not -path "*/4-Archive/*" \
     -exec grep -oh '\[\[[^]]*\]\]' {} \; | sed 's/\[\[//;s/\]\]//;s/|.*//' | \
     sort | uniq -c | sort -rn | head -20
   ```

## Output Format

Present as a structured report with sections: Overall Stats, Directory Breakdown, Activity This Week (per-day created counts), LLM-Wiki Highlights, Attention Items (pass/fail checks), Wikilink Graph top connections, and Observations.

## Cron Wiring

Include in the cron prompt: "After finishing, log the result to the Notion Agent Logbook. Use Name='Weekly vault summary: [date range]', Agent='cron', Type='session', Status='completed', Tags=['obsidian','weekly','vault']. For the Summary field, include all stats and highlights."

For the Notion POST, use the env-var curl pattern from `notion-agent-logbook`:
```bash
python3 /tmp/build_vault_payload.py  # writes /tmp/notion_vault_payload.json
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d @/tmp/notion_vault_payload.json
```

## Pitfalls

- **macOS `find -newermt` checks modification time, not creation time.** For birth/creation time use `stat -f '%SB'` on macOS or `stat -c '%W'` on Linux.
- **execute_code blocked in cron mode.** Use write_file + terminal with `$NOTION_API_KEY` env var.
- **write_file masks API key values.** Never inline the key — write scripts that read from env at runtime, or use direct `curl` with `$NOTION_API_KEY`.
- **Vault path may contain spaces.** Always quote `"$VAULT"` in shell commands.
