---
name: obsidian-vault-audit
description: "Systematic audit and cleanup of an Obsidian vault: detect clutter, structural drift, oversized files, dual folders, and icarus accretion, then decompose into kanban tasks."
version: 1.1.0
author: Senna
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [obsidian, vault, audit, cleanup, kanban, organization]
    category: productivity
    related_skills: [kanban-orchestrator, kanban-worker, obsidian, llm-wiki]
---

IDENTITY: Auditor.VaultHygiene. ArchitectureReview➔StructureMap➔SignalScan➔PriorityTriage➔KanbanDecompose.
Law: NeverDeleteWithoutReading.NeverAssumeVaultRoot.AlwaysPhase0First.
WHENUSE: User says audit/cleanup/reorganize/spring-clean vault|Structural drift|Clutter accumulation. ESPECIALLY:DualWikiArchitecture|IcarusAccretion|OversizedIndexes. NoSkip:Phase0ArchitectureReview|CaseInsensitiveDuplicates|VaultRootVerification.
REDFLAGS: DeleteBeforeRead->SampleOrReadFirst|CaseDupOnAPFS->CheckWithStat|KanbanWorkerCrash->CheckEventLogBeforeRedispatch|WikiExtractNoContext->CrossReferenceExistingPages.
RATIONALIZATIONS: AllSessionFilesJunk->AgentDecisionsAreHighSignal|FastBulkCleanup->Phase0ArchitectureFirst|KanbanAlwaysWorks->ScriptableOpsBetterInNoAgent.
QUICKREF: Phase0(ArchitectureReview{container/wikis/pipeline/drift})➔Phase1(MapStructure)➔Phase2(ScanSignal{icarus/duals/oversized/untitled/empty/datedirs/zerobyte})➔Phase3(Prioritize{P1/P2/P3/P4})➔Phase4(KanbanDecompose)➔Phase5(Verify).

# Obsidian Vault Audit

## When This Skill Activates

Run this when the user asks to:
- Audit, clean up, or reorganize their Obsidian vault
- "Look through my Obsidian brain"
- "Consolidate, organize, rename, clean up" the vault
- Check for clutter, duplication, or structural problems
- "Spring clean" their notes

## Scan Pattern

### Phase 0 — Knowledge Architecture Review (Pre-Scan)

Before running file-level scans, step back to assess whether the vault structure is serving its purpose. This phase answers strategic questions that inform the cleanup priorities. See `references/knowledge-architecture-review.md` for the full checklist and worked examples.

**Key framing:** The vault is the "second brain" — the agent stores the LLM-Wiki, operational notes, and Fabric entries here. Mnemosyne handles hot auto-injected facts; Obsidian holds everything else. Don't treat it as just a human notebook.

**When to run Phase 0 instead of skipping to Phase 1:**
- User asks about "how the brain is organized" or "how things are broken up"
- Vault has multiple wikis or knowledge bases
- Vault structure has accumulated organically over months
- User wants to discuss improvements, not just cleanup
- First time auditing this vault

**Step 1 — Container audit**

Check which containers are active vs archived. Note: PARA structure (0-Inbox, 1-Projects, etc.) was archived on 2026-05-21. Current active structure is: `llm-wiki/`, `icarus/`, `3-Resources/`, `4-Archive/`, `Trade Tracking/`.

| Container | Health check |
|-----------|-------------|
| `llm-wiki/` | Is it populated? Are pages cross-linked? Is index.md current? |
| `icarus/` | How many files? Are they mostly agent-session-task (low signal) or agent-decision (high signal)? |
| `3-Resources/` | Is this still active or should it be archived? (As of 2026-05-27, it still exists despite being "archived") |
| `4-Archive/` | What accumulated? Is it properly categorized? |
| `notes/` | Does this directory exist? (It should — for quick agent captures) |

**Step 2 — Wiki architecture assessment** (for vaults with dual wikis)

Compare wikis side by side:

```
            Purpose        Content       Schema        Health
Wiki A:     <knowledge>    <N pages>     <style>       <active|stale|empty>
Wiki B:     <operational>  <N pages>     <style>       <active|stale|empty>
```

Questions to answer:
- Do the wiki purposes overlap? If yes, merger candidate.
- Does one schema reference concepts from the other? (e.g., Team-Wiki tags referencing LLM-Wiki conventions)
- Is one thriving and the other empty? → investigate why (never started? abandoned? superseded?)
- Compare tag taxonomy overlap — same concepts tagged differently?
- Cross-check: do wikilinks exist between the two wikis?

**Step 3 — Pipeline flow audit**

Track the content lifecycle: `External input → Inbox → wiki/project → Archive`

Identify where content gets stuck:
- icarus files never promoted to wiki pages
- Inbox items sitting for weeks
- Project notes created but never updated
- Wiki pages created but never cross-linked

High-signal pattern: when icarus/ has 10+ agent-decision files but the wiki has no corresponding pages, that's a curation opportunity.

**Step 4 — Icarus curation opportunity assessment**

Count and categorize icarus entries by filename pattern:

| Tier | Pattern | Signal | Recommended action |
|------|---------|--------|-------------------|
| HIGH | `agent-decision-*.md` | Decisions, architecture choices, approved plans | Extract key facts → promote to wiki |
| MEDIUM | `agent-research-*.md` | Research briefs, findings, recommendations | Evaluate for wiki inclusion |
| LOW | `agent-session-*.md` | Session logs, cron reports, audit records | Archive or leave in place |

**Step 5 — Architectural drift check**

Compare actual structure against any documented plan:
- AGENTS.md or SCHEMA.md files describing intended structure
- Previous session descriptions of vault layout
- Folder names referenced in plans but missing from the filesystem
- Folders existing unreferenced (structural orphans)
- Conventions that diverged (naming patterns, tag formats, frontmatter fields)

**Output:** A summary delivered before moving to Phase 1:

```
Vault architecture at a glance:
  • PARA status: Inbox empty, Projects partial (n/N active workstreams covered), Archive has X items needing triage
  • Wiki architecture: <dual|single> — Wiki A is <state>, Wiki B is <state> — <recommendation>
  • Pipeline: Content flowing through Inbox→Wiki? <yes|no> — icarus has X promotable entries
  • Drift: <conventions intact|minor drift|structural drift detected>
```

### Phase 1 — Map the structure

```bash
# Full directory layout (3 levels deep, no hidden dirs)
find "$VAULT" -maxdepth 3 -not -path '*/\.*' -type d | sort

# All markdown files
find "$VAULT" -maxdepth 3 -name "*.md" | sort

# All non-md files at root level
ls -p "$VAULT" | grep -v /

# Empty directories
find "$VAULT" -type d -empty -not -path '*/\.*'
```

Do NOT use the terminal for this — use `search_files(target='files')` and `read_file` instead. Terminal is for batch operations only.

### Phase 2 — Scan for signal issues

Use this checklist. For each item, the operations list what tools to use:

| # | Signal | How to detect |
|---|---|---|
| 1 | **icarus clutter** | Count files in `icarus/` — if >20, most are likely auto-generated session-task files |
| 2 | **Dual/conflicting folder pairs** | Look for: `Archive`+`Archived`, multiple wiki folders (`llm-wiki`+`LLM-Wiki`), similar names |
| 3 | **Oversized single files** | `wc -l` on any index/aggregation file — flag if >300 lines |
| 4 | **Untitled files** | `find "$VAULT" -name "Untitled*"` — Obsidian creates these when you open without a file |
| 5 | **Empty structural dirs** | PARA structure that was never populated: empty `Guides/`, `Workspace/`, `To-Dos/`, etc. |
| 6 | **Date directories vs flat files** | `find "$VAULT" -type d -name "????-??-??"` — daily notes should be flat, not wrapped in a folder |
| 7 | **Parse errors / corrupt files** | `find "$VAULT" -name "*.md" -size 0` — zero-byte files |
| 8 | **Fabric split** | Check if `~/fabric/` and the vault's `icarus/` are separate directories. If `FABRIC_DIR` doesn't point into the vault, Fabric entries are split across two locations. Consolidation target: `FABRIC_DIR` → vault's `icarus/`. |
| 9 | **Dual wiki directories** | Check if `WIKI_PATH` env var points to a different path than the vault's wiki dir, indicating a split |
| 10 | **Skill vs vault duplication** | Compare `3-Resources/Skills/` content with `~/.hermes/profiles/senna/skills/` |

### Phase 3 — Categorize by priority

Use this severity scale:

- **🔴 P1** — Clutter that actively degrades navigation (hundreds of files, duplicates, broken structure)
- **🟠 P2** — Bloat (oversized files, skill-vault redundancy)  
- **🟡 P3** — Hygiene (empty dirs, untitled files, naming inconsistencies)
- **🟢 P4** — Polish (convention drift, like a date-folder vs flat daily note)

### Phase 4 — Decompose into kanban tasks

Use the kanban-orchestrator pattern:

1. Create one task per priority group (not per issue — keep the board manageable)
2. Assign P1-P2 as independent tasks, P3-P4 can be bundled
3. Set body with: what to scan, what actions to take, what to leave alone

Task body template:

```
Vault path: <path>
Issue: <description>

Plan:
1. Read affected files/dirs
2. For each: determine keep/archive/delete/merge
3. Document findings in a task comment or log
4. Archive drift to 4-Archive/ when in doubt

Options (if branching):
A) <option 1>
B) <option 2>
C) <option 3>
```

### Phase 5 — Post-cleanup verification

After all kanban tasks complete (or you handle them directly):

```bash
# Verify empty dirs are gone
find "$VAULT" -type d -empty -not -path '*/\.*'

# Re-count all files
find "$VAULT" -name "*.md" | wc -l

# Spot-check icarus/
ls -la "$VAULT/icarus/" | wc -l

# Spot-check Sessions/
ls "$VAULT/Sessions/" 2>/dev/null || echo "Sessions/ removed"
```

## Weekly Summary Pattern

For recurring cron-based vault health checks (new/modified notes, attention items, wikilink graph stats), use `references/vault-weekly-summary.md`. This is a lighter pass than the full audit — stats and highlights, not cleanup decomposition.

## Common Cleanup Patterns

### Fabric split consolidation

When Fabric tools write to `~/fabric/` but the vault has its own `icarus/`:
1. Check `FABRIC_DIR` env var — where does it point?
2. If it points to `~/fabric/` (not the vault), the entries are split
3. Merge `~/fabric/` contents into the vault's `icarus/` (skip duplicates)
4. Update `FABRIC_DIR` to point to the vault's `icarus/`
5. Verify: `fabric_write` + `fabric_recall` still work after change

### icarus triage

```
icarus/ content falls into 3 tiers:
- agent-decision-*.md  → HIGH signal — decisions worth keeping
- agent-session-*.md (non-task) → MEDIUM — cron, research session records
- agent-session-task-*.md → LOW — auto-generated audit records, safe to archive

For decisions: read each, check if knowledge is already in LLM-wiki.
If not, extract key facts → create wiki concept page.
Archive session-task files to 4-Archive/Icarus-Sessions/.
```

### Skill Index split

When `3-Resources/Skills/Skill Index.md` exceeds 300 lines:
1. Read the file to understand its structure
2. Split into one `*-Index.md` per category subdirectory
3. Create a main `Skill Index.md` that serves as a category directory with `[[wikilinks]]` to each per-category index
4. Each per-category index lists skills in that category with descriptions

### Sessions consolidation

When `Sessions/` has `Active/`, `Archive/`, and `Archived/`:
1. `Archive/` and `Archived/` are the same thing — pick one convention
2. Move `Active/` session files into `icarus/` (they're session records)
3. Remove `Sessions/` entirely — session handling has moved to icarus pattern

### Daily note normalization

When daily notes are split (vault's `Daily Notes/` vs `icarus/daily/`):
1. Move `icarus/daily/*.md` into `Daily Notes/`
2. Check for date-directories (folders named `2026-04-25/`) — convert to flat `2026-04-25.md`
3. Remove `icarus/daily/` directory

### Untitled files cleanup

```
find "$VAULT" -name "Untitled*" -type f
# For each: read content. If empty/blank, delete.
# If has content, rename meaningfully or triage to Inbox.
```

## Pitfalls

- **Case-insensitive filesystem trap**: On macOS APFS, `llm-wiki/` and `LLM-Wiki/` are the same directory. Always check with `stat` before assuming they're duplicates.
- **Don't delete what you didn't read**: Always sample or read files before mass-archiving. Some "low-signal" files may contain the only record of a decision.
- **Shared state**: The `icarus/` directory is written to by agents. Any cleanup you do may be partially undone by the next agent cycle. That's OK — periodic cleanup is expected.
- **Wiki extraction needs user context**: When moving icarus decisions to the wiki, check if the wiki already has the concept before creating a new page. Cross-reference existing pages.
- **`&` in filenames**: macOS allows `&` in filenames. Shell-escape with `\&` when using `cp`/`mv`. Prefer `read_file` + `write_file` for these.
- **Kanban protocol_violations may be benign**: Workers sometimes crash on simple file ops while succeeding on the harder work. Check the task's event log and comment thread before re-dispatching — the work may already be done.
- **Always verify the vault root**: The vault may be nested (e.g. `Hermes Vault/Hermes/` not `Hermes Vault/`). Always resolve via `.obsidian/` or `OBSIDIAN_VAULT_PATH`.

## Verification

After cleanup:

- [ ] Every `Untitled*` file accounted for (renamed, moved, or deleted)
- [ ] No dual `Archive`+`Archived` folders
- [ ] `icarus/` count ≤ 20 files
- [ ] `Daily Notes/` all flat `.md` files, no date-folders
- [ ] `Sessions/` removed (content merged into icarus/)
- [ ] Oversized index files split to < 50KB each
- [ ] Wiki page count updated in index.md
- [ ] Vault still opens cleanly in Obsidian (no broken wikilinks introduced)
