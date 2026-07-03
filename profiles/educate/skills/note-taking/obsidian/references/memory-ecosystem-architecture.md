# Memory Ecosystem Architecture

How the Obsidian vault fits into the full memory stack. This is the "why" behind the vault structure — understanding the flow prevents orphaned data and broken pipelines.

## Four-Layer Stack

```
┌─────────────────────────────────────────────────────┐
│  Mnemosyne   — Hot facts, always injected           │  ← Agent auto-writes
├─────────────────────────────────────────────────────┤
│  Fabric      — Session capture, operational logs    │  ← All agents + cron
├─────────────────────────────────────────────────────┤
│  LLM-Wiki    — Curated knowledge (Karpathy pattern) │  ← Agent on approval
├─────────────────────────────────────────────────────┤
│  Obsidian    — The vault that holds it all          │  ← Human browses in app
└─────────────────────────────────────────────────────┘
```

### Layer 1: Mnemosyne (Hot Facts)

- **Purpose:** Always-injected context for every session
- **Writes:** Agent auto-writes when it detects stable preferences
- **Contains:** User preferences, environment details, tool quirks
- **Lifetime:** Updated in place; never grows large
- **Storage:** Hermes memory system (not in vault)

### Layer 2: Fabric / Icarus (Session Capture)

- **Purpose:** Operational logging — what happened, what was decided
- **Writes:** All agents + cron jobs
- **Contains:** Session summaries, decisions, task outcomes, daily logs
- **Lifetime:** Permanent; promotes to wiki when high-value
- **Storage:** `icarus/` directory in vault

**Critical distinction:**
- `agent-session-*.md` and `agent-decision-*.md` = **fabric entries** (structured, ~1KB, with frontmatter). Archiving breaks Icarus recall.
- `YYYY-MM-DD_HHMM.md` = **raw transcripts** (date-stamped, safe to archive).

### Layer 3: LLM-Wiki (Curated Knowledge)

- **Purpose:** Compounding knowledge base (Karpathy pattern)
- **Writes:** Knowledge agent on approval only
- **Contains:** Concepts, entities, comparisons, syntheses, operational docs
- **Lifetime:** Permanent; grows and cross-references over time
- **Storage:** `llm-wiki/` directory in vault

### Layer 4: Obsidian (The Vault)

- **Purpose:** The container that holds everything; human browses in app
- **Writes:** Agents write via file tools; human edits in Obsidian
- **Contains:** All of the above, plus quick notes and archives
- **Lifetime:** Permanent

## Data Flow Paths

```
Sources (web, sessions, user input)
    ↓
Mnemosyne (preferences)  ←→  Agent memory tool
    ↓
Fabric (session capture)  ←→  All agents write
    ↓
Curation (memory-curator + fabric-promote-review cron)
    ↓
LLM-Wiki (curated knowledge)  ←→  Knowledge agent writes on approval
    ↓
Obsidian vault  ←→  Human browses, agent reads
```

## Promotion Paths

| From | To | Trigger | Approval |
|------|----|---------|----------|
| Session → Fabric | Auto | Every session | None needed |
| Fabric → Wiki | Cron scan | `training_value: high` + `status: completed` | User approval |
| Notes → Wiki | Curator scan | 3+ wikilinks OR tagged concept | User approval |
| Wiki → Archive | Curator scan | 90+ days stale | User approval |
| Archive → Delete | User explicit | After 30 days in archive | User approval only |

## Agent Role Boundaries

| Role | Reads | Writes |
|------|-------|--------|
| **All agents** | Wiki, fabric, notes | Fabric entries, notes |
| **Knowledge agent** | Everything | Wiki pages, index.md, log.md |
| **Human** | Everything (in Obsidian) | Direct edits in Obsidian |

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `OBSIDIAN_VAULT_PATH` | Root vault path | `~/vault` |
| `WIKI_PATH` | Wiki directory (usually inside vault) | `~/vault/llm-wiki` |
| `ICARUS_OBSIDIAN=1` | Enable Icarus → Obsidian sync | `1` |
| `FABRIC_DIR` | Fabric entries location | `~/vault/icarus` |
