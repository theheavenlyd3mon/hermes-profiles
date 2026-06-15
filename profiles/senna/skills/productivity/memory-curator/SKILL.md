---
name: memory-curator
description: "Automated memory curation: monitors Obsidian notes/, triggers moves/promotions, handles archiving. Works with Mnemosyne (hot layer), Icarus (operational), and llm-wiki (curated). One component of a five-layer memory stack (Mnemosyne, Fabric, LLM-Wiki, Obsidian, Skills)."
version: 1.0.0
author: Senna
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, curation, obsidian, automation]
    category: productivity
    related_skills: [llm-wiki, obsidian]
triggers:
  - notes review
  - memory cleanup
  - archive stale
  - promote to wiki
---

IDENTITY: Curator.MemoryHygiene. NotesCheck→PromoteCandidates→ArchiveStale→DeleteUserOnly.
Law: NeverAutoDelete.NeverAutoPromote.AlwaysGetApproval.
WHENUSE: User says curate/cleanup/archive/notes review|Notes≥10 items|Stale≥3 days. ESPECIALLY:PromoteToWiki|ArchiveOld|NotesOverflow. NoSkip:WikilinksBeforeMove|ArchiveFirstDeleteLater|CuratorFatigueTune.
REDFLAGS: AutoDelete->ArchiveFirstApprovalGated|AutoPromote->WikiQualityNeedsReview|BrokenWikilinks->CheckBeforeMove.
RATIONALIZATIONS: FastCleanup->30DayArchiveGrace|PromoteEverything->Only3+WikiLinksOrConceptTag.
QUICKREF: NotesCheck(count+age)➔PromoteCandidates(wikilinks+tags)➔ArchiveCandidates(90+days)➔UserApproval(execute).

# Memory Curator

Automates the memory hygiene workflow: monitors Inbox, triggers promotions to llm-wiki, handles archiving.

## When This Skill Activates

- You ask to review, clean, or audit your memory
- You mention "notes", "archive", "promote", or "curate"
- Session ends and notes/ has 10+ items or 3+ day-old items
- Manual trigger: `curate`, `cleanup`, `archive`

## Configuration

**Obsidian Vault Path:**
```
OBSIDIAN_VAULT_PATH=~/Hermes Vault/Hermes
```

Defaults to your configured vault or prompts if unset.

**Curator Rules:**
| Trigger | Threshold |
|---------|-----------|
| Notes alert | 10+ items |
| Stale alert | 3+ days since modified |
| Archive alert | 90+ days since modified |
| Promote to llm-wiki | Item has 3+ wikilinks OR is tagged `concept` |

## Workflow

```
Session ends / you invoke curator
         ↓
Check notes/ for promotion candidates
         ↓
┌─────────────────────────────────────────┐
│  IF item has 3+ wikilinks              │
│     OR tag: concept                     │
│     OR stable across 2+ sessions        │
│  → Report: "Promote candidates: [...]" │
│  → Ask: "Promote to llm-wiki?"          │
└─────────────────────────────────────────┘
         ↓
Check Fabric for high-value entries
         ↓
┌─────────────────────────────────────────┐
│  IF entry has training_value: high      │
│     AND status: completed               │
│     AND not yet promoted                │
│  → Report: "Fabric candidates: [...]"  │
│  → Ask: "Promote to llm-wiki?"          │
└─────────────────────────────────────────┘
         ↓
Check for archive candidates
         ↓
┌─────────────────────────────────────────┐
│  IF item modified 90+ days ago          │
│  → Report: "Archive candidates: [...]" │
│  → Ask: "Archive these?"                │
│  → YOU decide what gets deleted         │
└─────────────────────────────────────────┘
```

**Note:** The old PARA Inbox (`0-Inbox/`) was removed during the May 2026 consolidation. The vault is now flat: `llm-wiki/`, `icarus/`, `notes/`, `4-Archive/`. Curator scans `notes/` for promotion candidates instead of Inbox.

## Core Operations

### 1. Inbox Check (now notes/ check)

```bash
# Count items in notes/
ls -1 "$OBSIDIAN_VAULT_PATH/notes/" | wc -l

# Find stale items (3+ days old)
find "$OBSIDIAN_VAULT_PATH/notes/" -mtime +3 -type f

# Find archive candidates (90+ days old)
find "$OBSIDIAN_VAULT_PATH/" -path "*/4-Archive/*" -mtime +90 -type f
```

### 2. Promote to llm-wiki

When you approve promotion:
1. Read the source note from Inbox
2. Extract entity/concept from frontmatter
3. Determine if entity page or concept page
4. Create/update the llm-wiki page:
   - Move to `entities/` or `concepts/`
   - Add frontmatter (type, tags, sources)
   - Ensure 2+ wikilinks to existing pages
5. Add to `index.md` under correct section
6. Append to `log.md`
7. Remove from Inbox

### 3. Archive

When you approve archive:
1. Move note to `4-Archive/` with subfolder by year-month
2. Update any pages linking to it → replace `[[wikilink]]` with plain text + "(archived)"
3. Do NOT delete — you decide what's deleted

### 4. Delete (Your Approval Only)

Archive → delete path:
1. Note sits in `4-Archive/` for 30 days
2. After 30 days, you can request "permanent delete"
3. You review each file, confirm deletion
4. Only then does it leave the vault entirely

## Commands

| Command | Action |
|---------|--------|
| `curate inbox` | Check notes/, report stats |
| `curate promote` | Find and propose promote candidates |
| `curate archive` | Find and propose archive candidates |
| `curate full` | Run full curator cycle (inbox + promote + archive) |
| `curate approve <action>` | Approve pending action (move/promote/archive) |

**Division of Labor (Full Stack)**

| Layer | Task | Who Does What |
|-------|------|---------------|
| **Mnemosyne** | Always-injected preferences & env facts | Agent auto-writes; never trained or curated |
| **Fabric (Icarus)** | Session capture, operational logging | All agents + cron write; curator promotes from |
| **LLM-Wiki** | Curated knowledge (curator target) | Agent writes on curation approval |
| **Obsidian** | Second brain (vault) | Agent stores wiki, notes, Fabric entries; human browses/curates |

**Curator-specific:**

| Task | Who Does What |
|------|---------------|
| **Inbox → Wiki** | Curator scans Inbox, proposes candidates |
| **Fabric → Wiki** | fabric-promote-review cron scans fabric (5am), proposes candidates |
| **Review** | Curator presents options, you approve |
| **Archive** | Curator moves, you review for deletion |
| **Delete** | You explicitly approve |

**Note:** A complementary cron job `fabric-promote-review` (daily at 5am) scans fabric entries with `status: completed` and `training_value: high` for wiki promotion candidates. This handles the fabric → wiki pipeline, while the memory curator handles the Inbox → wiki pipeline. Both propose to the user — neither auto-creates pages. The morning briefing aggregates candidates from both sources.

## Pitfalls

- **Obsidian is the second brain, not just a human notebook.** The agent stores the LLM-Wiki, operational notes, and Fabric entries in the vault. Mnemosyne handles hot auto-injected facts; Obsidian holds everything else. Don't treat it as "the user's space that the agent occasionally peeks at" — it's the central knowledge store.
- **LCM ≠ Mnemosyne.** LCM (hermes-lcm plugin) compresses session context within a single conversation. Mnemosyne (`hermes mnemosyne` CLI) consolidates memories across sessions. They are separate systems — don't look for mnemosyne functionality inside LCM tools or vice versa.
- **Don't auto-delete** — archive first, delete only on your explicit command
- **Don't auto-promote** — llm-wiki quality matters; get your approval first
- **Check wikilinks before move** — broken links break the graph
- **Curator fatigue** — if alerts are too frequent, tune thresholds
- **`sleep` timeout on large DBs** — background it with `notify_on_complete` in cron; see [references/mnemosyne-cli.md](references/mnemosyne-cli.md) for pattern

## Related Skills

- [llm-wiki](/skills/llm-wiki) — Karpathy-style compounding knowledge base (lives inside the vault)
- [obsidian](/skills/obsidian) — vault operations (the second brain)
- [fabric-promote-review](/skills/fabric-promote-review) — Full fabric→wiki promotion workflow (scan, cross-check, create, index, log, Notion)
- [references/mnemosyne-cli.md](references/mnemosyne-cli.md) — `hermes mnemosyne` CLI commands, output formats, cron integration