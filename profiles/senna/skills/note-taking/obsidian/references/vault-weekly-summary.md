# Vault Weekly Summary / Health Check

A repeatable monitoring workflow for tracking Obsidian vault health over time. Unlike the cleanup-focused `vault-audit-pattern.md`, this is a reporting/monitoring pass — no edits, just measurement.

## Triggers

- "weekly vault summary"
- "vault health check"
- "how's the vault doing"
- Cron job on weekly cadence

## Metrics to Collect

Run each block as a separate `terminal()` call (parallel where independent). Avoid `execute_code` in cron context — it's blocked without user approval.

### 1. Total Note Count

```bash
find "$VAULT" -name "*.md" -type f 2>/dev/null | wc -l
```

### 2. Directory Count

```bash
find "$VAULT" -type d -not -path "*/.obsidian/*" -not -path "*/.obsidian" 2>/dev/null | wc -l
```

### 3. Notes Modified in Last 7 Days

```bash
find "$VAULT" -name "*.md" -type f -mtime -7 2>/dev/null | wc -l
```

**Pitfall:** On macOS, `-Btime -7d` (birth time) may match the same files as `-mtime -7` (modification time) when notes are bulk-imported or generated in batch. The modification time (`-mtime -7`) is the reliable metric for "recently active."

### 4. Notes Created in Last 7 Days

```bash
# macOS only — -Btime uses birth time (crtime)
find "$VAULT" -name "*.md" -type f -Btime -7d 2>/dev/null | wc -l
```

If this matches the modified count, the vault had a bulk-write event (e.g., Icarus session dump). Report both numbers and note the correlation.

### 5. Directory Breakdown

```bash
for dir in icarus llm-wiki notes "4-Archive"; do
  count=$(find "$VAULT/$dir" -name "*.md" -type f 2>/dev/null | wc -l)
  modified=$(find "$VAULT/$dir" -name "*.md" -type f -mtime -7 2>/dev/null | wc -l)
  echo "  $dir: $count total, $modified modified (7d)"
done
```

### 6. Wikilink Graph Density

```bash
# Total wikilinks
grep -roh "\[\[[^]]*\]\]" "$VAULT" --include="*.md" 2>/dev/null | wc -l
```

Density = total_wikilinks / total_notes. Healthy range: 1.0–3.0 links/note. Below 0.5 means under-linked; above 5.0 may indicate link spam.

### 7. Tagged vs Untagged

```bash
# Notes with frontmatter tags
grep -rl "^tags:" "$VAULT" --include="*.md" 2>/dev/null | wc -l
```

Untagged count = total_notes - tagged_notes. Not all notes need tags (raw articles, daily logs are fine untagged). Flag only if >80% are untagged.

### 8. Orphan Detection

Orphan notes = notes whose filename never appears as a `[[wikilink]]` target. Uses `comm` for set difference:

```bash
# Get all unique wikilink targets
grep -roh "\[\[[^]]*\]\]" "$VAULT" --include="*.md" 2>/dev/null | sed 's/\[\[//;s/\]\]//' | sort -u > /tmp/linked_notes.txt

# Get all note basenames
find "$VAULT" -name "*.md" -type f -exec basename {} .md \; 2>/dev/null | sort -u > /tmp/all_notes.txt

# Orphans = in all_notes but not in linked_notes
comm -23 /tmp/all_notes.txt /tmp/linked_notes.txt | wc -l
```

**Expected orphans:** date-stamped daily logs (`YYYY-MM-DD*.md`), structural files (`SCHEMA.md`, `index.md`, `log.md`). Filter these out before flagging.

### 9. Inbox Check

```bash
find "$VAULT" -ipath "*inbox*" -name "*.md" -type f 2>/dev/null
```

Zero is clean. Non-zero means triage is needed.

### 10. Root-Level Clutter

```bash
find "$VAULT" -maxdepth 1 -name "*.md" -type f 2>/dev/null
```

Should be empty (all notes organized into subdirectories).

### 11. Recently Modified Highlights (llm-wiki)

```bash
find "$VAULT/llm-wiki" -name "*.md" -type f -mtime -7 2>/dev/null | while read f; do
  mod=$(stat -f "%Sm" -t "%Y-%m-%d" "$f")
  rel=$(echo "$f" | sed "s|$VAULT/||")
  echo "  [$mod] $rel"
done | sort -r
```

### 12. LLM-Wiki Category Breakdown

```bash
for subdir in concepts entities comparisons alloys queries operational raw; do
  count=$(find "$VAULT/llm-wiki/$subdir" -name "*.md" -type f 2>/dev/null | wc -l)
  echo "  llm-wiki/$subdir: $count"
done
```

## Output Format

Structure the report as:

1. **Vault Stats** — table with total notes, directories, wikilinks, density, tagged count, orphan count
2. **Activity (Last 7 Days)** — modified count + breakdown by directory
3. **LLM-Wiki Breakdown** — category counts
4. **Highlights This Week** — recently modified wiki entries with dates
5. **Needs Attention** — inbox items, root clutter, significant untagged percentage

## Logging

After generating the report, log to Notion Agent Logbook using the `notion-agent-logbook` skill pattern. Use:
- Name: `"Weekly vault summary: YYYY-MM-DD"`
- Agent: `"cron"`
- Type: `"session"`
- Tags: `["obsidian", "weekly", "vault"]`
- Summary: full stats and highlights (truncate to 1990 chars)
