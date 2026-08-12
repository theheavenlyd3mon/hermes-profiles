# Memory Stack Architecture

The full five-layer memory architecture that this curator participates in.

Last updated: 2026-05-27

## Component Origins

| Component | Origin | Install |
|---|---|---|
| **Mnemosyne** | Third-party package | `pip install mnemosyne-memory` |
| **Fabric (Icarus)** | Built-in to Hermes | No install — always available |
| **LLM-Wiki** | User-created | `mkdir` + agent maintains it |
| **Obsidian** | External app + central knowledge store | User installs app; vault is the second brain |
| **Skills** | Built-in to Hermes | `skill_manage` — always available |
| **hermes-lcm** | Third-party plugin | Git clone to `~/.hermes/plugins/hermes-lcm/` |
| **Session search** | Built-in to Hermes | `session_search` — SQLite + FTS5 |

```
                     ┌──────────────────────┐
                     │      OBSIDIAN         │  ← The second brain
                     │  (vault: wiki + notes │     Agent + human both write
                     │   + Fabric entries)   │
                     └──────────┬───────────┘
                                │ everything lives here
                     ┌──────────▼───────────┐
                     │      LLM-WIKI         │  ← Karpathy-style compounding KB
                     │  (curated concepts)   │  ← Curation target (inside vault)
                     └──────────┬───────────┘
                                │ promoted when stable
                     ┌──────────▼───────────┐
                     │   ICARUS (Fabric)     │  ← Shared memory / training
                     │  (operational logs)   │  ← Curation source (inside vault)
                     └──────────┬───────────┘
                   ╭───╯ rare edge ╰───╮
                   ↓                    ↓
            ┌──────────┐      ┌──────────────┐
            │MNEMOSYNE │      │   CRON JOBS   │
            │(hot layer│      │(autonomous    │
            │ always   │      │ overnight ops)│
            │injected) │      └──────┬───────┘
            └──────────┘             │ writes
                                     ↓
                              ┌──────────────┐
                              │    FABRIC     │
                              │ (all agents   │
                              │  write here)  │
                              └──────────────┘
```

## The Five Layers

### 1. Mnemosyne — Hot persistence (always injected)

- Third-party package (`mnemosyne-memory`, installed via pip — NOT built into Hermes).
- SQLite + vectors, auto-loaded every turn.
- Stores: user preferences, environment facts, one-shot lessons, corrected behavior.
- Importance-weighted (0.0–1.0); critical facts surface aggressively.
- Written by both user and agent. Never exported for training.
- **Complements Obsidian:** Mnemosyne is what the agent always knows; Obsidian is what the agent can always look up.
- **Edge case** — Fabric → Mnemosyne: when something discovered in Fabric is durable enough for automatic injection rather than just searchable. Rare; the main pipeline is Fabric → LLM-Wiki.

### 2. Icarus (Fabric) — Cross-agent operational memory

- Built-in to Hermes — no installation needed.
- Shared JSON memory store. Every profile reads/writes: Senna, Researcher, cron, gateway.
- Stores: task outcomes, decisions with reasoning, code reviews, bug resolutions, cross-agent handoffs.
- Each entry has type (`task`, `decision`, `review`, `resolution`, etc.), status, and training-value label.
- Doubles as fine-tuning data pipeline — high-value entries are exported for model training.
- Session start: `fabric_brief` shows pending work, overnight cron results, and recent activity.
- **Vault integration:** When `FABRIC_DIR` points into the vault's `icarus/`, Fabric entries become browsable in Obsidian.

### 3. LLM-Wiki — Curated knowledge base

- Interlinked markdown concept pages (Karpathy pattern). The "final draft" layer.
- Lives INSIDE the Obsidian vault at `llm-wiki/`.
- Stores: architecture decisions, model fleet assignments, project conventions, workflow patterns.
- Graduated from Fabric when knowledge proves stable. Also promoted from Obsidian Inbox via curator.
- Written by the agent. User approves promotions before they happen.

### 4. Obsidian — The second brain (central knowledge store)

- The vault is the central knowledge store — NOT just a human notebook.
- The agent stores the LLM-Wiki, operational notes, and Fabric entries here.
- Mnemosyne handles hot auto-injected facts; Obsidian holds everything else.
- Obsidian's graph view shows how everything connects — wiki, Fabric entries, daily notes.
- Both agent and human write. The agent maintains the wiki and writes operational notes. The human browses, curates, and directs.

### 5. Skills — Procedural memory

- Built-in to Hermes — `skill_manage` always available.
- Repeatable procedures with exact commands, pitfalls, and verification steps.
- Created by the agent after complex tasks (5+ tool calls) or when the user says "save this."
- Profile-scoped — each profile has its own skills directory.

## The Graduation Pipeline

Knowledge enters raw and graduates upward as it stabilizes:

```
Cron jobs & agent sessions
         ↓  write
      Fabric          ──rare──→  Mnemosyne
         ↓  stable knowledge
    LLM-Wiki (inside vault)
         ↓  when user consults
     Obsidian (vault — everything visible in graph view)
```

**Fabric** is the scratchpad — fast write, every session outcome lands here.
**LLM-Wiki** is the curated shelf — promoted from fabric when stable. Lives in the vault.
**Mnemosyne** is the hot layer — always-injected, rare promotions from fabric for exceptionally durable facts.
**Obsidian** is the second brain — wiki, notes, and Fabric entries all visible in one place.
**Skills** are procedural memory — repeatable workflows, pitfalls, verification.

## Current State (2026-05-27)

**Consolidated.** FABRIC_DIR points to the vault's `icarus/`. Fabric entries are browsable in Obsidian with graph view. 3-Resources archived. Notes/ created for quick agent captures. 860+ Fabric entries in the vault.

## How the Curator Fits

The memory curator sits at the **Fabric → LLM-Wiki** and **Inbox → LLM-Wiki** junctions:

- **Inbox → Wiki:** Scans Obsidian Inbox for items with 3+ wikilinks or `concept` tag → proposes promotion.
- **Fabric → Wiki:** The `fabric-promote-review` cron (5am daily) scans completed high-value fabric entries → proposes promotion.
- **Both propose, never auto-create.** User approval required.

| Task | Layer | Tool |
|------|-------|------|
| Always-injected context | Mnemosyne | `mnemosyne_remember` / `mnemosyne_recall` |
| Session logging | Fabric | `fabric_write`, `fabric_recall` |
| Inbox → Wiki promotion | Inbox → LLM-Wiki | `memory-curator` skill |
| Fabric → Wiki promotion | Fabric → LLM-Wiki | `fabric-promote-review` cron + curator |
| Wiki maintenance | LLM-Wiki | `llm-wiki` skill (lint, refresh, ingest) |
| Vault browsing | Obsidian | `obsidian` skill |
| Procedural memory | Skills | `skill_manage` |

## How Cron Jobs Participate

Cron jobs are autonomous agents that write to Fabric just like interactive sessions:

```
Cron runs overnight → writes Fabric entry (type, training value, evidence)
     ↓
Next morning: fabric_brief surfaces it
     ↓
I review, extract stable knowledge → promote to LLM-Wiki
     ↓
Fabric entry updated: "promoted to wiki: <concept>"
```

Cron follows the same Fabric conventions — type, status, training value, evidence. The only difference: no `clarify` calls (no user present to answer).
