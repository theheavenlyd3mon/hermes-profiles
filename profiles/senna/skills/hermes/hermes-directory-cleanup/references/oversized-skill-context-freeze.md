# Oversized Skills Causing Context Window Freeze

A skill's SKILL.md can be too large for the agent's context window — not a disk space problem, a token budget problem. When `skill_view` loads the file, its entire content plus metadata gets injected into the context. If the skill is large and the context is already populated (system prompt, memory, tools, conversation history), the agent freezes or becomes unresponsive.

## Diagnosis

**Symptom:** Agent freezes, hangs, or becomes extremely slow when loading a specific skill. May manifest as the agent appearing to "think forever" on a turn that triggers the skill load.

**Root cause:** The skill's SKILL.md is too large for the available context window. `skill_view` returns the full file content plus metadata expansion (tags, linked_files, readiness_status, etc.) — the injected content can be 3-4x the raw file size.

**How to check:**
```bash
# Find the skill file
find ~/.hermes -path "*/skills/<category>/<skill-name>/SKILL.md" -o -path "*/skills/<skill-name>/SKILL.md"

# Check size
wc -c <path>/SKILL.md
wc -l <path>/SKILL.md

# Rule of thumb: >20KB SKILL.md is a risk. >50KB will likely cause issues.
```

**How skill_view expands content:**
The tool wraps the SKILL.md content with metadata (frontmatter parsing, linked_files listing, readiness checks, usage hints). A 28KB file can return ~105K chars to the context. A 100KB file will return 200K+ chars — which can exceed the entire available context window on shorter-context models.

## Remediation: Slim Core + References

The fix is structural decomposition — move reference material out of SKILL.md into `references/` files that load on demand.

### Target sizes
- SKILL.md: **5-15KB** (150-400 lines) — only operational knowledge needed every turn
- references/ files: **unlimited** — loaded individually via `skill_view(file_path='references/<file>')` only when needed

### What stays in SKILL.md
- What the skill/tool/service IS (1-2 paragraphs)
- Quick start / essential commands
- Key paths and config tables (the stuff you need every time)
- Troubleshooting QUICK REF (top 3-5 issues, one-liner fixes)
- **References/ index** — a table listing every reference file with a one-line description, so the agent knows what's available on demand

### What moves to references/
- Full CLI command reference (flags, subcommands)
- Detailed troubleshooting guides
- Provider/platform-specific setup guides
- Architecture deep-dives
- Edge cases and advanced patterns
- Contributor/developer guides
- Duplicate sections (check for sections that appear twice at different detail levels)

### Execution

```bash
# 1. Map the file structure
grep -n "^## \|^### " <skill>/SKILL.md

# 2. Extract sections to reference files using sed
sed -n '108,645p' SKILL.md > references/cli-reference.md

# 3. Remove extracted sections from SKILL.md
# (keep the references/ index table instead)

# 4. Verify
wc -c SKILL.md  # target: 5-15KB
```

## Example: hermes-agent skill (100KB → 15.5KB)

The senna profile's hermes-agent SKILL.md grew to 100KB (1961 lines) over months of accumulated troubleshooting, edge cases, and reference tables. `skill_view` returned ~105K chars on every Hermes-related turn, causing the agent to freeze.

**Fix applied:**
- Extracted 9 sections into references/ (cli-reference, slash-commands, browser-automation, lsp-diagnostics, security-toggles, spawning-details, local-optimization, troubleshooting, contributor-guide)
- Slim core kept: intro, quick start, config tables, voice summary, spawning summary, quick troubleshooting, references index
- Result: 100KB → 15.5KB (85% reduction), context injection dropped from ~105K to ~16K chars

## Prevention

- When adding content to a skill's SKILL.md, check the file size after editing
- If the SKILL.md exceeds 20KB, ask: "Does every turn that loads this skill need this section?"
- Reference tables (CLI flags, provider lists, troubleshooting checklists) are prime candidates for extraction
- The references/ index table is the key pattern — it tells the agent what's available without loading everything
