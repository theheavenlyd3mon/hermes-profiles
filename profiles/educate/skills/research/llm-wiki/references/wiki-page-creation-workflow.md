# Wiki Page Creation Workflow (Non-Ingest)

When creating wiki pages from gathered context rather than a provided source document. Common when documenting a system, profile, or setup that exists on disk but has no single "source" to ingest.

## When to Use This

- User says "write up how X works" or "document the Y setup" or "review Z and write it in the wiki"
- The source material is a directory structure, config files, or scattered documentation — not a URL or paste
- Multiple information sources need to be gathered before writing

## Workflow

### 1. Parallel Context Gathering

When the documentation task requires inspecting multiple locations, use `delegate_task` with parallel tasks:

```python
delegate_task(tasks=[
    {"goal": "Examine the vault/project structure at X...", "toolsets": ["terminal", "file"]},
    {"goal": "Review the profile/directory at Y and report all details...", "toolsets": ["terminal", "file"]}
])
```

This is faster than sequential inspection and keeps your context clean (subagent details don't flood your window).

### 2. Check Existing Wiki Content

Before writing, search the wiki for existing coverage:

```python
search_files(pattern="topic-name|related-term", path="<WIKI_PATH>", limit=20)
```

Also read `index.md` to see if related pages exist. This prevents duplicates and surfaces cross-link targets.

### 3. Write Wiki Pages

Follow standard frontmatter conventions from SCHEMA.md. Key fields for operational/how-to pages:

```yaml
type: operational        # not concept/entity — this is a how-to or profile doc
tags: [how-to, ...]      # or [agent, profile, ...]
workflow: stable          # if the documented system is established
confidence: high          # if you verified the details from actual files
```

Place in the correct `operational/` subdirectory:
- `operational/conventions/` — setup guides, standards, how-to docs
- `operational/agents/<name>/` — agent profile documentation
- `operational/protocols/` — handoff rules, team workflows
- `operational/decisions/` — architectural decisions with rationale

### 4. Index + Log Maintenance (3 steps, always all three)

**Step A — Update index.md:**
- Bump the "Total pages" count in the header
- Bump the "Last updated" date
- Add entry under the correct Operational subsection
- Use `patch` for single-entry additions

**Step B — Append to log-2026.md:**
- Use `terminal` with `cat >>` (simplest for appends) or Python `open()`/`write()`
- Format: `## [YYYY-MM-DD] create | Brief description`
- List every file created and cross-links added

**Step C — Verify:**
- Confirm files exist on disk
- Confirm index entry is correct (no duplicate, no wrong section)

## Pitfalls

- **Don't use `patch` for log appends** — anchor uniqueness issues on append-only files. Use `terminal` with `cat >>` or Python.
- **Parallel delegates can't access your memory** — pass all relevant paths, constraints, and context in the `context` field.
- **operational/ pages are NOT linted by default** — the wiki-lint script doesn't recurse into `operational/`. Pages there won't trigger index-completeness warnings. This is expected behavior.
- **Cross-link generously** — operational pages should link back to concept pages they reference (e.g., a setup guide linking to the architecture concept page).
