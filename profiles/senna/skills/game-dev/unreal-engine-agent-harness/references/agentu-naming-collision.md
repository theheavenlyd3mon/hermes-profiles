# Naming collision: AgentU vs. agentu

This note captures what happened in one UE agent harness scoping session so future sessions don't repeat it.

## What happened

- The user and I built a small standalone Unreal Engine agent harness in `~/Desktop/ue-agent-harness/` and named it **AgentU** (a README header: "AgentU — UE Agent Harness").
- I later web-searched the name and found an existing PyPI package / GitHub repo also called **agentu** (`github.com/hemanth/agentu`), a published Python agent-runtime framework.
- The two projects are unrelated, but the collision creates ambiguity in web search, PyPI imports, and any future public publishing.

## Lesson

Check for naming collisions **before** a name hardens into files, config, prompts, and user muscle memory. Collision vectors to verify:

1. **PyPI** — `pip install <name>` or pypi.org search.
2. **GitHub** — `site:github.com "<name>"`.
3. **Generic web** — exact-phrase search.
4. **Language module namespace** — if the project is Python, `import <name>` conflicts with an installed package.

## Practical check recipe

```bash
pip install <proposed-name> --dry-run 2>&1 | head -n 5
# or
pip search <proposed-name>               # if available
# plus web:
# "<proposed-name>" python package
# "<proposed-name>" site:github.com
```

## Options if a collision exists

1. **Rename** to a distinct name (preferred if the project is young and not yet public).
   - Examples: `UEAgent`, `AgentUnreal`, `UnrealAgentHarness`, `MurimAgent` (project-specific).
2. **Keep the name but document the distinction** only if the collision is in a different ecosystem or the existing name is abandoned.
3. **Namespace the project** (e.g. `nous-agentu`, `murim-agentu`) if you still want the word in the name.

## When this matters most

- Before writing README headers, package metadata, import names, or GitHub repo names.
- Before publishing to PyPI, npm, crates.io, etc.
- Before asking an LLM to research the project by name (the search results will be polluted).

## Related

- `templates/config.yaml` — starter config; keep the project name in config, not in code, so renaming is cheap.
- Pitfall added to `SKILL.md`: "Naming the harness before checking for collisions."
