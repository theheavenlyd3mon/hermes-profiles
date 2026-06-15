---
name: technical-documentation-authoring
description: "Write accurate technical docs about systems, tools, and stacks. Covers setup guides, architecture overviews, and component inventories. Core principle: verify before documenting."
---

# Technical Documentation Authoring

Write accurate technical documentation — setup guides, architecture overviews, component inventories, comparison docs. The core discipline is **verify before you claim**.

## When To Use

- Writing a .md file documenting how a system is set up or composed
- Creating setup guides for another agent or person to follow
- Comparing what's built-in vs added vs custom in a stack
- Reviewing existing docs for accuracy

## Workflow

### 1. Inventory components

Before writing, gather the actual state:
- What's built into the framework (shipped, always available)
- What's a third-party addition (installed separately, has its own install steps)
- What's user-created (custom config, hand-written files, no external source)
- What's an external tool (separate application, not part of the stack at all)

Run verification commands:
```bash
# Check if a package is in the framework's own repo
pip show <package>          # is it installed? who provides it?
ls ~/.hermes/plugins/       # what plugins are added?
ls ~/.hermes/profiles/*/skills/  # what skills exist?
grep -r "import <module>" ~/.hermes/hermes-agent/  # is it imported by core?
```

### 2. Draft with provenance markers

Every component gets a provenance label:
- **Built-in** — ships with the framework, no installation needed
- **Third-party** — installed via pip/npm/etc., has its own repo and version
- **User-created** — hand-written config, custom files, no external source
- **External** — separate application (Obsidian, VS Code, etc.)

### 3. Setup guide accuracy

The setup guide must match reality:
- Built-in components: "No installation needed. Available as `tool_name`."
- Third-party components: "Install via `pip install X`. Not included with the framework."
- User-created components: "Create this directory structure. The agent maintains it going forward."

**Never write "ships with X" or "built into X" without verifying.** Check the framework's own source, package list, or plugin directory first.

### 4. Review pass

Before delivering, re-read with fresh eyes asking:
- Would someone reading this get the right impression about what they need to install?
- Are any claims about origin unverified?
- Do the setup steps actually work if followed from scratch?

## Correction Workflow

When you discover a documentation error (especially about component origins), don't just fix the file you're working on. The same mistake is usually replicated elsewhere. Fix all locations:

1. **The file you're editing** — immediate fix
2. **Related wiki pages** — check the LLM-Wiki for pages covering the same topic. If the wiki page says the same wrong thing, fix it too. Add an origin table if one is missing.
3. **Fabric entry** — log the correction as a completed decision so other agents see it in their briefs. Training value: high.
4. **Mnemosyne memory** — save the correction at high importance so future sessions don't repeat it.
5. **Memory (legacy)** — if the correction is about a fundamental distinction (built-in vs third-party), save it there too as a belt-and-suspenders measure.

The user said it directly: "we must fix our mistakes and become more efficient." The efficiency comes from fixing the *pattern*, not just the instance. Search for all occurrences of the wrong claim before declaring the fix done.

## Pitfalls

### Assuming third-party packages are built-in

**What happened:** Wrote "Mnemosyne ships with Hermes Agent" when it's actually a separate Python package (mnemosyne-memory) we installed ourselves via pip.

**Why it's dangerous:** Anyone following the setup guide would skip the install step and get a broken memory system. The guide looks authoritative but gives false confidence.

**Fix:** Always verify. If you didn't install it yourself in this session, check: `pip show <package>`, `ls ~/.hermes/plugins/`, `grep -r "import" <framework-source>`. If it's not in the framework's own codebase, it's added — say so explicitly.

**Pattern to watch for:** Anything described as "native," "built-in," "ships with," or "auto-installed" needs verification. These phrases are easy to write casually but create real confusion when wrong.

### Treating Obsidian as "just a human notebook"

**What happened:** Wrote "Obsidian is the human's personal vault. The agent can read, search, and create notes there when asked, but this is the human's space."

**Why it's wrong:** The user corrected this — Obsidian is the "second brain" where the agent stores the LLM-Wiki, operational notes, and (when consolidated) Fabric entries. Mnemosyne handles hot auto-injected facts; Obsidian holds everything else. They complement each other.

**Fix:** When documenting Obsidian's role, frame it as the central knowledge store that both agent and human write to. The LLM-Wiki lives inside the vault — it's not a separate system.

### Documenting stale version numbers

Don't hardcode version numbers in documentation unless you just verified them. Write "v3.0+" or omit the number. Versions change; the doc shouldn't need a patch every time.

### Copying claims from previous sessions without re-verification

When writing a doc that references past work (e.g., "we set up X on May 15"), verify the current state rather than trusting the memory of what happened. Systems change; docs should reflect what IS, not what WAS.

## References

- `references/hermes-memory-stack.md` — verified component inventory for the Hermes memory stack (Mnemosyne, Fabric, LLM-Wiki, Obsidian, Skills) with correct provenance labels AND the "Obsidian is the second brain" correction
- Wiki page `concepts/memory-architecture.md` in the LLM-Wiki also tracks these origins — update it in sync with this reference file
