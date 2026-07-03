# Knowledge Architecture Review — Reference

## Purpose

A strategic pre-scan that assesses whether the vault structure is serving its purpose,
before diving into file-level cleanup. Answers questions like: "Are the wikis working?",
"Where is content getting stuck?", "What's planned vs what exists?"

Run this when the user asks to "review how the brain is set up" or "discuss improvements."

---

## Full Checklist

### 1. Container Audit

For each PARA container, determine usage status.

```
0-Inbox/
  ├── Empty?           → No pipeline feeding it, or pipeline bypassed
  ├── < 5 items?       → Light pipeline — check freshness
  ├── > 10 items?      → Backlog — stale items need triage
  └── Notes in inbox?  → Items that should have been promoted

1-Projects/
  ├── Count active workstreams from memory/kanban/session search
  ├── Does each have a doc? What's missing?
  └── Are project docs current or stale?

2-Areas/
  ├── What responsibility areas are documented?
  └── Any undocmented area that should have a note?

3-Resources/
  ├── Reference material organized by category?
  ├── Any oversized/index files > 300 lines?
  └── Skill vs vault duplication (skills/ dir vs skills on disk)

4-Archive/
  ├── Random clutter or properly categorized?
  └── Has it become a catch-all instead of intentional archive?
```

### 2. Wiki Architecture Assessment

For vaults with multiple wikis, compare side-by-side:

```
            Purpose        Pages       Schema         Health         Tags
──────────  ────────────   ────────    ──────────     ───────────    ──────────
Wiki A:     <knowledge>    N=28        Karpathy       Active         flat, 21-tag
Wiki B:     <operational>  N=0         domain:item    Empty/skel     prefixed
```

**Diagnostic questions:**
- Purposes overlap? → Merge candidate if yes
- One schema references the other's concepts? → Could signal integration intent
- One thriving, one empty? → Was the empty one superseded, never started, or waiting for content?
- Tag taxonomy overlap? → Same concepts tagged differently between wikis → consistency issue
- Cross-wiki wikilinks exist? → If yes, they're connected; if no, they're truly separate

**Recovery paths:**
- **Merge two wikis** when their content domains overlap and schemas are reconcilable. Pick the richer schema, tag-remap the other's pages, consolidate directories.
- **Keep separate** when their content domains are genuinely different and cross-linking is sufficient.
- **Revive an empty wiki** only if the user confirms the need. Otherwise archive the skeleton to 4-Archive/.

### 3. Pipeline Flow Audit

Track content lifecycle through the vault:

```
External input → [0-Inbox/] → [wiki|project pages] → [4-Archive/]
                                    ↓
                             [icarus/] (fabric records)
```

**Where content gets stuck:**
- icarus entries never promoted to wiki → this is the most common gap
- Inbox items sitting stale (check created dates)
- Project notes created once, never updated
- Wiki pages created but never cross-linked → they exist in isolation

**Icarus promotion opportunity:**
| File pattern | Signal | Action |
|---|---|---|
| `agent-decision-*.md` | HIGH — user-approved architecture, decisions | Extract → wiki concept or entity page |
| `agent-research-*.md` | MEDIUM — research briefs and findings | Evaluate for wiki inclusion |
| `agent-session-*.md` | LOW — session logs | Leave in place or archive |

Check: if icarus has 10+ agent-decision files but the wiki has no corresponding pages,
that's a curation opportunity worth raising to the user.

### 4. Architectural Drift Check

Compare actual vault against any documented plan:

- **AGENTS.md** or project setup docs describing intended structure
- Previous session descriptions of vault layout
- SCHEMA.md / index files that reference folders that don't exist
- Folders on disk that no plan references (orphans)
- Conventions that diverged — tags, naming, frontmatter fields

**Common drift patterns:**
- A wiki was planned in architecture docs but never created on disk
- A wiki was created but the planning docs still reference the old path/name
- Tag conventions changed mid-stream (flat → prefixed, or vice versa)
- Frontmatter fields were added to some pages but SCHEMA.md wasn't updated

---

## Worked Example: Hermes Vault Review

From session 2026-05-13. The user asked to "review how we have the obsidian brain set up."

### Steps Taken

1. **Load session history** — Search past sessions for "obsidian vault brain setup" to understand the planned architecture.

2. **Map current structure** — Get directory tree (maxdepth 3), list all markdown files, check root-level items.

3. **Read wiki schemas** — For each wiki, read SCHEMA.md and index.md. Compare.

4. **Check PARA health** — List contents of Inbox, Projects, Areas, Resources, Archive.

5. **Count icarus entries** — List icarus/ root files and daily subdir. Triage by filename pattern.

6. **Cross-reference with memory** — Recall user profile and past sessions for workstream context, preferences, decisions.

### Findings Pattern

```
Vault root: /Users/noctis/Hermes Vault/Hermes

PARA: Inbox empty, Projects partial (3 docs, n active workstreams undocumented),
      Archive has icarus remnants, Areas is minimal

Wiki architecture: DUAL — LLM-Wiki (28 pages, active) + Team-Wiki (0 pages, skeleton since Apr 25).
  Team-Wiki has cleaner operational schema but zero content.
  LLM-Wiki has full Karpathy structure but accumulating lint issues (7 broken wikilinks,
  7 missing frontmatter type fields, 22 out-of-taxonomy tags).

Pipeline: Inbox empty — nothing feeding in. LLM-Wiki being populated by agent.
  icarus has 17 entries — 16 agent-decision and 1 agent-research. None promoted to wiki.
  This is the biggest pipeline gap.

Drift: Team-Wiki referenced in 10-Agent Team Setup doc but never populated.
  Tag conventions differ between wikis (flat vs domain:item prefix).
```

### Output to Present

A structured briefing organized as:
1. Topology map (tree or ascii)
2. Container-by-container status
3. Wiki comparison table
4. Pipeline gaps
5. Questions/worthy directions for discussion (not recommendations — leave space for user input)

---

## Pitfalls

- **Case-insensitive trap**: On macOS APFS, `LLM-Wiki` and `llm-wiki` are the same directory. Always check with `stat` or exact path casing before reporting duplications.
- **Memory is not always current**: The user's planned architecture (as stored in memory or old session summaries) may have been superseded by decisions made outside your sessions. Always verify by reading actual vault files.
- **Don't conflate empty with broken**: An empty Team-Wiki is not necessarily a problem — it might be intentionally deferred. Ask before treating it as something to fix.
- **One review is not ownership**: The vault's architecture evolves. A Phase 0 review gives a snapshot. Note the date so future reviews can measure drift over time.
