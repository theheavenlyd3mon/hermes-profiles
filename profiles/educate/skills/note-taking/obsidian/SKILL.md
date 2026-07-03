---
name: obsidian
description: "Read, search, create, and edit notes in the Obsidian vault. The vault is the 'second brain' — agent stores LLM-Wiki, operational notes, and Fabric entries there."
---

IDENTITY: Librarian.SecondBrain. ResolvePath→FileTools(notShell)→SurgicalEdits→UserApprovalForMemory.
Law: AlwaysResolveAbsolutePathBeforeFileTools.NeverUseShellForFileOps.TheVaultIsTheBrain.
WHENUSE: Read/list/search/create/edit notes in Obsidian vault|Icarus integration|Vault structure navigation. ESPECIALLY:Wikilinks|DailyNotes|PARAstructure|IcarusAgentDecisions. NoSkip:PathResolution|UserApprovalForMemoryEdits|FileToolsOverShellCommands.
REDFLAGS: ShellForFileOps->UseReadFileWriteFilePatch|UnresolvedEnvVarPath->ResolveFirst|ScatteredSessionNotes->SurgicalEditExistingMemories|RelativePathInSandbox->AbsoluteUserPath.
RATIONALIZATIONS: TerminalFaster->FileToolsAvoidShellQuotingIssues|CreateNewNoteEveryTime->UpdateExistingWhenRightHome.
QUICKREF: ResolvePath(OBSIDIAN_VAULT_PATH or fallback)➔Read/List/Search(file tools)➔Create/Edit(write_file or patch)➔Append(read→patch anchor).

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## User approval before operational memory edits

For this user, Obsidian is a source of operational context. If an existing vault note contains stale or conflicting Hermes runtime facts, first report the proposed correction and get approval before patching it. Keep edits surgical: update the existing memory/context note when it is the right home, do not create scattered session notes unless the user asks. Preserve the user's canonical-stack preference: Senna as default profile; Hermes + Hermes Workspace as the runtime; SwarmClaw/Mission Control are not canonical unless explicitly reintroduced.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Icarus Integration (Advanced)

This user's Obsidian vault is integrated with **Icarus**, the cross-instance memory system for Hermes multi-agent teams. This is not generic vault work — it's operational memory.

### Vault Audit & Cleanup
### Vault Audit & Cleanup
See `references/vault-audit-pattern.md` for the repeatable process of auditing vault structure and cleaning up accumulated session debris, oversized indexes, empty directories, and other structural issues.

### Weekly Vault Health Check
See `references/vault-weekly-summary.md` for the monitoring/reporting workflow — metrics collection, orphan detection, wikilink density, and output format for weekly vault summaries.

### Memory Ecosystem Architecture

See `references/memory-ecosystem-architecture.md` for how the vault fits into the full four-layer memory stack (Mnemosyne → Fabric → LLM-Wiki → Obsidian), including data flow paths, promotion rules, and agent role boundaries.

### Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `OBSIDIAN_VAULT_PATH` | Absolute path to the vault (e.g., `/Users/noctis/Hermes Vault/Hermes`) |
| `ICARUS_OBSIDIAN=1` | Enables Icarus → Obsidian sync (opt-in) |
| `FABRIC_DIR` | Where Icarus stores fabric entries (often under vault path) |

### Vault Structure (This User — Consolidated 2026-05-27)

The vault at `/Users/noctis/Hermes Vault/Hermes/` is the **second brain** — the agent stores the LLM-Wiki, operational notes, and Fabric entries here. Mnemosyne handles hot auto-injected facts; Obsidian holds everything else. They complement each other.

```
├── llm-wiki/                   # THE BRAIN — Karpathy-pattern compounding knowledge base
│   ├── concepts/               # Concept/topic pages
│   ├── entities/               # Entity pages (people, orgs, products, models)
│   ├── comparisons/            # Side-by-side analyses
│   ├── alloys/                 # Narrative syntheses
│   ├── queries/                # Filed query results
│   ├── operational/            # Agent decisions, protocols, conventions
│   │   ├── agents/
│   │   ├── decisions/
│   │   ├── conventions/
│   │   └── protocols/
│   ├── raw/                    # Immutable source material
│   ├── SCHEMA.md
│   ├── index.md
│   └── log.md
├── icarus/                     # Agent memory fabric (860+ entries)
│   ├── agent-decision-*.md     # High-signal decisions
│   ├── agent-session-*.md      # Session summaries — FABRIC ENTRIES, NOT RAW LOGS
│   └── daily/                  # Daily agent logs
├── notes/                      # Quick agent captures (lower barrier than wiki)
├── 4-Archive/                  # Archived/dead weight (browsable, not active)
│   ├── Icarus-Sessions-2026/   # Raw session transcripts
│   ├── 3-Resources-archive/    # Skill indexes + book summaries
│   ├── PARA-leftovers/         # 1-Projects, 2-Areas, Daily Notes, Memory, Security
│   ├── Team-Wiki-archive/      # Old Team-Wiki before llm-wiki merge
│   └── Root Clutter/
└── .obsidian/                  # Obsidian config
```

**Notable conventions:**
- `llm-wiki/` follows the Unified Wiki Pattern — combines knowledge pages with operational content under a single Karpathy-style structure. The `WIKI_PATH` env var points here. See the `llm-wiki` skill for full conventions.
- `icarus/` files are **Icarus fabric entries** — structured memory data with frontmatter (id, agent, tags, training_value). They are NOT raw session transcripts. Archiving them breaks Icarus memory recall. Only date-stamped files (YYYY-MM-DD_HHMM.md) are raw transcripts safe to archive.
- `notes/` is for quick agent captures — lower barrier than wiki (no frontmatter required). Promotion path: notes/ → llm-wiki/ when knowledge stabilizes.
- `3-Resources/` was archived (moved to `4-Archive/3-Resources-archive/`) because the skill index files duplicate what `hermes skills list` / `skills_list()` already provides.
- The PARA structure (0-Inbox, 1-Projects, 2-Areas, Daily Notes, Memory, Security) was removed because it was never adopted — zero inbox items, stale to-do list, minimal daily notes. The llm-wiki IS the brain; PARA was intended for human capture that didn't happen.
- **FABRIC_DIR** points to the vault's `icarus/` — Fabric tools write directly into the vault. All 860+ entries are browsable in Obsidian.

### How Icarus Uses Obsidian

When `ICARUS_OBSIDIAN=1` is set, Icarus automatically:

1. **Appends wikilinks** — For entries with `review_of:` or `revises:` metadata, creates `[[wikilinks]]` for navigation
2. **Updates daily notes** — Creates or updates `fabric_dir/daily/YYYY-MM-DD.md` with links to new entries
3. **Generates config** — Creates `.obsidian/app.json` with `showFrontmatter: true` and `readableLineLength: true`

The Icarus plugin code lives at `hermes-profiles/researcher/plugins/icarus/obsidian.py`.

### Reading Icarus Entries

Fabric entries are stored in `icarus/*.md` with frontmatter containing:

```
---
agent: senna
id: 20260508-abc123
revises: senna:20260507-xyz789
---
```

To find an entry by reference (e.g., `senna:20260507-xyz789`), search for the `agent:` and `id:` pair in `.md` files under `icarus/`.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.
