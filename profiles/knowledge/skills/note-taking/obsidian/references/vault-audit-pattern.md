# Vault Audit & Cleanup Pattern

A repeatable process for auditing and cleaning up an Obsidian vault that has accumulated structural debris from prolonged agent use. Run when the vault feels cluttered, or on a maintenance cadence (monthly/quarterly).

## Triggers

- "clean up the vault"
- "review the Obsidian brain"
- User notices clutter, empty dirs, or untitled files
- Post-migration or post-agent-update cleanup

## Phase 1: Scan & Identify Issues

Run these scans to build a full picture:

### 1a. Directory Tree

```bash
# Full directory listing
find "$VAULT" -maxdepth 3 -type d | sort

# All markdown files
find "$VAULT" -maxdepth 3 -name "*.md" | sort
```

### 1b. Identify Issue Classes

Scan each class of issue:

| Issue class | How to detect | Typical culprits |
|---|---|---|
| **Clutter (high file count)** | `ls <dir> | wc -l` on icarus/, sessions/, root | icarus/ auto-generated session logs |
| **Duplicate-purpose dirs** | Two dirs with same naming (`Archive` vs `Archived`) | Sessions/Archive vs Sessions/Archived |
| **Empty placeholder dirs** | `find . -type d -empty` or manual check | Workspace/, To-Dos/, Guides/ |
| **Untitled files at root** | `ls *.md *.canvas 2>/dev/null` | Untitled.md, Untitled.canvas from Obsidian |
| **Oversized single files** | `find . -size +100k -name "*.md"` | Auto-generated indexes, monolithic notes |
| **Date-directory anomalies** | Directories named as dates containing single files | 2026-04-25/ containing one note |
| **Dual wikis** | Two wiki structures (Team-Wiki + llm-wiki) | Verify they serve different purposes (operational vs knowledge) |

### 1c. Sample Content

For high-signal files (decisions, project notes), read the first ~30 lines to assess substance. For suspected-low-signal files (session logs), sample 2-3 to confirm the pattern before bulk-archiving.

## Phase 2: Prioritize

Rank by signal-to-noise impact:

| Priority | Class | Rationale |
|---|---|---|
| **P1** | Clutter (30+ low-signal files), duplicate-purpose dirs | Directly increases cognitive load on vault navigation |
| **P2** | Oversized files, untitled files | Hinders search and open-in-Obsidian UX |
| **P3** | Empty directories, date anomalies | Cleanliness, not blockers |
| **P4** | Minor conventions (daily note format, naming) | Nice-to-have consistency |

## Phase 3: Execute via Kanban

Create one kanban task per priority level or structural area. Let workers handle bulk operations.

```bash
hermes kanban create "Triage icarus/ — extract decisions, archive session noise" \
  --assignee <profile> \
  --body "Detailed plan with file counts, sub-steps, and archive target path"
```

### Worker Task Body Pattern

Include in each task body:
1. Exact file counts and locations
2. Archive target path (e.g., `4-Archive/Icarus-Sessions/`)
3. What to keep vs archive (with rationale)
4. Any wiki extraction needed from substantive files
5. Options for ambiguous cases (label A/B/C and let the human pick when the worker blocks)

### Fan-out Strategy

- **Independent areas** → parallel tasks (no parent links). icarus triage, sessions dedup, untitled files, and empty dirs can all run concurrently.
- **Dependent follow-ups** → link via `--parent`. e.g., "Verify cleanup" depends on all cleanup tasks.
- **Same-profile queue** → workers serialize automatically. Assign all cleanup to `senna` (or the active profile); dispatcher handles ordering.

## Phase 4: Verify & Resolve

After kanban workers complete:

```bash
# Check for protocol violations (blocked tasks)
hermes kanban list --status blocked

# Unblock and complete remaining work manually when edge cases
hermes kanban unblock <task_id>
# For tasks where the bulk work is already done but the worker couldn't close:
hermes kanban complete <task_id> --summary "..."
```

Common reasons workers block on vault tasks:
- **Options not decided** (A/B/C in the task body) — worker can't pick; read the session file and make the call
- **File path contains special characters** (&, $, etc.) — use cp/write_file not shell mv
- **Recursive delete** — worker defers to human approval. Use your terminal tool to handle.

## Phase 5: Update References

After cleanup, update any skill or documentation that references the old structure:
- The `obsidian` skill's Vault Structure section
- Any wiki pages that mention vault paths
- Memory entries about vault layout

## Known Patterns

### icarus/ Overgrowth

Most frequent issue. The Icarus agent writes session records to `icarus/`. Over time, these accumulate.

**CRITICAL DISTINCTION — Fabric Entries vs Raw Transcripts:**

- `agent-session-*.md` and `agent-decision-*.md` files are **Icarus fabric entries** — ~1KB summaries with structured frontmatter (id, agent, tags, training_value, summary). They are the **active memory data** that Icarus uses for recall. Archiving them **breaks Icarus memory recall**.
- Date-stamped files like `2026-04-22_2219.md` are **raw session transcripts** — these are safe to archive, they're never re-read.

```
KEEP in icarus/ (fabric data — Icarus needs these):
- agent-decision-*.md        (high-signal decisions with frontmatter)
- agent-session-*.md         (session summaries with frontmatter — fabric entries)
- daily/                     (recent agent daily logs)

Archive to 4-Archive/Icarus-Sessions/ (raw transcripts only):
- YYYY-MM-DD_HHMM.md         (date-stamped raw session transcripts)
- *.md files WITHOUT agent- or frontmatter structure

NEVER bulk-archive everything in icarus/ — always distinguish fabric entries from raw transcripts.
```

### 3-Resources/Skills/ Redundancy

If the vault has a `3-Resources/Skills/` directory with skill index files (e.g., `Autonomous-AI-Agents-Index.md`, `Business-Index.md`), these are **redundant with Hermes's built-in skills system** (`hermes skills list`, `skills_list()`). The indexes were human-curated mirrors of skill metadata that Hermes already tracks.

Book summaries (e.g., in `Business/`, `Research/` subdirectories) may have value — assess individually before archiving. If wiki-worthy, move to `llm-wiki/raw/` instead of deleting.

### PARA Structure Assessment

Before cleaning, assess whether the PARA folders are actually used:

```bash
for d in 0-Inbox 1-Projects 2-Areas 3-Resources; do
  count=$(find "$VAULT/$d" -name "*.md" 2>/dev/null | wc -l)
  echo "$count  $d"
done
```

If the user never adopted PARA (empty Inbox, stale Areas, minimal Projects), the entire structure is dead weight. Archive it all — the llm-wiki IS the brain, PARA was intended for human capture that didn't happen.

### Wiki Extraction from Decisions

When triaging icarus/ decisions, extract knowledge to llm-wiki before archiving the source. Decision files that may contain wiki-worthy content:
- Use case syntheses (cross-cutting themes, taxonomies, case studies)
- Architecture explanations (memory systems, multi-agent designs)
- Optimization priority analyses (ranked improvement candidates)
- Debugging documentation (failure modes, fixes)

Decisions that are already captured (skill docs, wiki, scripts, cron jobs) need no extraction.

### Sessions/ Consolidation

If the vault has both `Sessions/` and `icarus/`, they serve the same purpose. Consolidate into `icarus/`:
- Move `Sessions/Active/*` to `icarus/`
- Remove `Sessions/` entirely
- Remove redundant `Archive`/`Archived` subdirectories
