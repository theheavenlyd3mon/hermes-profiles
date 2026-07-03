# Hermes Memory Stack — Verified Component Inventory

Last verified: 2026-05-27

## Component Origins

| Component | Origin | How we know |
|---|---|---|
| **Fabric (Icarus)** | Built-in to Hermes | Tools (fabric_write, fabric_recall, etc.) appear in the core tool list. No separate package or plugin. |
| **Mnemosyne** | Third-party package | `mnemosyne-memory` installed via pip into Hermes venv. NOT in Hermes source. |
| **hermes-lcm** | Standalone plugin | Git plugin at `~/.hermes/plugins/hermes-lcm/`. NOT in Hermes source. |
| **Skills** | Built-in to Hermes | `skill_manage`, `skill_view` are core tools. Skills directory is a Hermes convention. |
| **LLM-Wiki** | User-created | Directory structure we made. No package, no plugin — just markdown files the agent maintains. Lives inside the Obsidian vault. |
| **Obsidian** | External app + central knowledge store | Separate app (obsidian.md). Not part of Hermes. BUT the vault IS the "second brain" — agent stores wiki, notes, and Fabric entries there. |
| **Session search** | Built-in to Hermes | `session_search` is a core tool backed by SQLite + FTS5. |
| **Notion integration** | User-created via skills | Custom curl-based logging. Notion skills define the databases and schemas. |

## Key Corrections

### Obsidian is the second brain (2026-05-27)

**Previous framing:** "Obsidian is the human's personal vault. The agent can read, search, and create notes there when asked, but this is the human's space."

**Corrected framing:** "Obsidian is the central knowledge store — the 'second brain' where the agent stores notes, the LLM-Wiki, and operational memory. Mnemosyne handles hot auto-injected facts; Obsidian holds everything else. They complement each other."

The vault at `~/Hermes Vault/Hermes/` contains:
- `llm-wiki/` — Karpathy-style compounding knowledge base (agent-maintained)
- `icarus/` — Fabric entries (agent operational memory)
- `notes/` — Quick agent captures (lower barrier than wiki)
- `4-Archive/` — Old material

Both agent and human write to the vault. The agent maintains the wiki and writes operational notes. The human browses, curates, and directs.

### Fabric consolidation (2026-05-27)

**Resolved.** Merged `~/fabric/` (54 files) into the vault's `icarus/`. FABRIC_DIR was already set to point at the vault. Fabric tools confirmed working — 862 entries now in the vault, all browsable in Obsidian. 3-Resources/ archived (was empty stubs). `notes/` directory created for quick agent captures.

### Mnemosyne is third-party (2026-05-27)

Easy to assume it's built-in because it's always injected into context. It's not — it's a separate package (`mnemosyne-memory`) we chose to install.

## Common Mistakes

- **Mnemosyne**: Easy to assume it's built-in because it's always injected into context. It's not — it's a separate package (`mnemosyne-memory`) we chose to install. The memory entry from May 15 confirms: "Mnemosyne (mnemosyne-memory) is the memory system — Installed as a Python package (v2.6.0 in venv)."
- **Fabric**: Actually IS built-in, which is the opposite mistake — easy to assume it's added because it feels like a plugin. It's core Hermes.
- **hermes-lcm**: Separate from Mnemosyne. LCM = Lossless Context Management (conversation history compression). Mnemosyne = memory storage/recall. Different systems, different locations.
- **Obsidian as "just a human notebook"**: The vault is the second brain. The agent writes the wiki, operational notes, and (when consolidated) Fabric entries there. Don't document it as "the user's space that the agent occasionally peeks at."
- **LLM-Wiki as separate from Obsidian**: The wiki lives INSIDE the vault. It's not a separate system — it's a component of the vault.

## Mnemosyne Setup (for a fresh Hermes instance)

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
pip install mnemosyne-memory
python3 -c "import mnemosyne; print(mnemosyne.__version__)"
```

Data: `~/.hermes/mnemosyne/data/mnemosyne.db`
Dependencies (auto-installed): fastembed, sqlite_vec, numpy

## hermes-lcm Setup (for a fresh Hermes instance)

```bash
cd ~/.hermes/plugins/
git clone <hermes-lcm-repo> hermes-lcm/
```

Location: `~/.hermes/plugins/hermes-lcm/`
