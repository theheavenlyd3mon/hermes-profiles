# Setting Up Obsidian as Your Hermes Agent's Second Brain

> A practical guide for connecting Obsidian to Hermes Agent — giving your AI a persistent, browsable knowledge base that compounds over time.

---

## Why Obsidian?

Hermes agents accumulate knowledge across hundreds of sessions — research findings, decisions, patterns, preferences. Without a persistent store, that knowledge dies with the session context window.

Obsidian gives you:
- **A knowledge graph** your agent reads and writes automatically
- **Human-readable files** — everything is plain markdown, no proprietary format
- **Graph View** — visualize how concepts connect
- **Cross-device access** via Obsidian Sync or iCloud
- **A second brain** that compounds: new knowledge references old knowledge

---

## The Big Picture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Hermes     │────▶│   Fabric    │────▶│  Obsidian   │
│   Agent      │     │  (memory)   │     │  (vault)    │
└─────────────┘     └─────────────┘     └─────────────┘
  learns things       stores them         you can browse
  calls tools         auto-syncs          graph view
  writes notes        cross-references    searchable
```

Three layers:
1. **Agent memory** — in-session learning via the `memory()` tool
2. **Fabric** — cross-session shared memory (the Icarus plugin)
3. **Obsidian vault** — the browsable, searchable knowledge base

---

## Step 1: Create Your Vault

Create a dedicated vault for Hermes. Don't use your personal notes vault — agents write a lot, and you want clean separation.

**Recommended location:**
```
~/Hermes Vault/
```

**Recommended structure:**
```
Hermes Vault/
├── knowledge/              # The brain — structured wiki pages
│   ├── concepts/           # Topics, techniques, patterns
│   ├── entities/           # People, tools, products
│   ├── how-tos/            # Step-by-step procedures
│   └── decisions/          # Architectural decisions
├── notes/                  # Quick captures (lower barrier)
├── daily/                  # Auto-generated daily logs
└── .obsidian/              # Obsidian config
```

> **Tip:** Keep the structure flat at first. Let it grow organically. You can always reorganize later.

### Open in Obsidian

1. Open Obsidian
2. Click "Open folder as vault"
3. Select your `Hermes Vault` folder
4. Done — Obsidian will create `.obsidian/` automatically

---

## Step 2: Configure Obsidian

In Obsidian Settings (⚙️):

### Core Plugins to Enable
- **Daily notes** — Hermes can auto-log to daily files
- **Graph view** — visualize knowledge connections
- **Backlinks** — see what references what
- **Outgoing links** — see what a page links to
- **Properties** — show YAML frontmatter in the sidebar

### Recommended Settings
- **Files & Links** → "Use [[Wikilinks]]" — ON (Hermes uses wikilinks)
- **Editor** → "Show frontmatter" — ON
- **Graph view** → Enable all filters

No community plugins required. The Hermes integration works through environment variables and the Fabric system, not Obsidian plugins.

---

## Step 3: Connect Hermes to the Vault

Tell Hermes where your vault lives using environment variables.

### Option A: In your shell profile (`~/.zshrc` or `~/.bashrc`)

```bash
export OBSIDIAN_VAULT_PATH="$HOME/Hermes Vault"
export FABRIC_DIR="$HOME/Hermes Vault/knowledge"
export WIKI_PATH="$HOME/Hermes Vault/knowledge"
```

### Option B: In Hermes config

In `~/.hermes/config.yaml` (or your profile's config):

```yaml
env:
  OBSIDIAN_VAULT_PATH: /Users/yourname/Hermes Vault
  FABRIC_DIR: /Users/yourname/Hermes Vault/knowledge
  WIKI_PATH: /Users/yourname/Hermes Vault/knowledge
```

> **Important:** Make sure `FABRIC_DIR` points **inside** the vault, not to a separate directory. This is the most common setup mistake — if your Fabric entries live outside the vault, Obsidian can't see them.

### Reload Hermes

```bash
hermes restart
```

---

## Step 4: Tell Your Agent About the Vault

Add a note to your agent's memory so it knows the vault exists and how to use it.

In a Hermes session, say:

```
Remember: Our Obsidian vault is at ~/Hermes Vault/. 
Use it to store durable knowledge:
- concepts/ for topics and techniques
- entities/ for people, tools, and products  
- how-tos/ for procedures
- decisions/ for architectural choices
- notes/ for quick captures
Use [[wikilinks]] to cross-reference pages.
Write YAML frontmatter on all wiki pages.
```

This gets saved to the agent's persistent memory and injected into future sessions.

---

## Step 5: Create a Knowledge Schema

Your agent needs conventions for how to write wiki pages. Create a `SCHEMA.md` in your vault root:

```markdown
# Knowledge Base Schema

## Frontmatter (required on all pages)
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept | entity | how-to | decision
tags: [tag1, tag2]
sources: [where this knowledge came from]
confidence: high | medium | low
---

## Page Structure
1. Title (H1)
2. One-line summary
3. Body with H2 sections
4. Related pages (wikilinks)

## Naming Conventions
- Lowercase, hyphenated: `my-topic-name.md`
- Concepts go in `concepts/`
- People/orgs go in `entities/`
- Procedures go in `how-tos/`
- Decisions go in `decisions/`

## Cross-Referencing
- Use [[wikilinks]] to connect related pages
- Link to pages that exist AND pages that should exist
- "Ghost links" (links to non-existent pages) are intentional —
  they mark topics worth writing about later
```

---

## Step 6: First Run — Seed Some Knowledge

Start a conversation with your agent and ask it to research something it can file in the vault:

```
Research the best practices for [your interest area].
Write your findings as a wiki page in the vault under concepts/.
Use the frontmatter format from SCHEMA.md.
Cross-reference any related topics.
```

After the first session, open Obsidian and check:
- ✅ Files were created in the right place
- ✅ Frontmatter is present and correct
- ✅ Wikilinks resolve (or are intentional ghosts)
- ✅ Graph view shows connections

---

## Day-to-Day Workflow

Once set up, the flow is automatic:

```
You ask Hermes something
    → Agent researches / works / learns
    → Calls memory() to save durable facts
    → Fabric stores the entry
    → Entry syncs to the vault as a markdown file
    → Wikilinks connect it to existing knowledge
    → Graph view grows
```

Over time, your vault becomes a compounding knowledge base:
- New pages reference old pages
- Contradictions get flagged
- Stale knowledge gets refreshed
- The graph tells you what you know and what's missing

---

## Optional: The LLM Wiki Pattern

For a more structured knowledge base, adopt the [LLM Wiki pattern](https://karpathy.ai) (inspired by Andrej Karpathy):

**Three layers:**
1. **Raw sources** — immutable source material (articles, papers, docs)
2. **Wiki pages** — agent-owned summaries and analyses
3. **Index** — a catalog of everything in the wiki

**Four operations:**
1. **Ingest** — add a new source, extract knowledge, create pages
2. **Lint** — health check for broken links, orphans, staleness
3. **Query** — ask questions against the knowledge base
4. **Review** — decide what to update vs. skip

This turns your vault from a note dump into a self-maintaining knowledge system.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Agent doesn't write to vault | Check `OBSIDIAN_VAULT_PATH` is set and points to an existing directory |
| Fabric entries not showing in Obsidian | Make sure `FABRIC_DIR` points **inside** the vault, not outside it |
| Obsidian shows "No file" for wikilinks | The linked page doesn't exist yet — that's okay, it's a "ghost link" |
| Two agents write the same file | Use separate files per topic, not a shared "notes.md" dump |
| Daily notes get too long | Archive old daily notes monthly, start fresh |
| Graph view is overwhelming | Use filters to show only certain tags or file types |

---

## What to Avoid

- **Don't use your personal notes vault.** Agents write frequently and in volume. Keep it separate.
- **Don't over-structure early.** Start flat, let patterns emerge, then reorganize.
- **Don't require agent writes for everything.** Some knowledge (session logs, quick notes) can be plain files. Reserve wiki structure for durable, cross-referenced knowledge.
- **Don't fight the graph.** If Obsidian's graph view shows clusters, that's useful information. Don't flatten everything into a tree.

---

## Quick Reference

| Variable | Example | Purpose |
|----------|---------|---------|
| `OBSIDIAN_VAULT_PATH` | `~/Hermes Vault` | Where the vault root is |
| `FABRIC_DIR` | `~/Hermes Vault/knowledge` | Where Fabric stores entries |
| `WIKI_PATH` | `~/Hermes Vault/knowledge` | Where wiki pages live |

| Directory | What Goes Here |
|-----------|---------------|
| `knowledge/concepts/` | Topics, techniques, patterns |
| `knowledge/entities/` | People, tools, products |
| `knowledge/how-tos/` | Step-by-step procedures |
| `knowledge/decisions/` | Architectural decisions with rationale |
| `notes/` | Quick captures, scratch work |
| `daily/` | Auto-generated daily logs |

---

*Built with [Hermes Agent](https://hermes.nousresearch.com) by Nous Research.*
