# Bulk path: third-party skill-pack inventories

When the user wants a **full list of skills and how each works** from GitHub skill libraries (SKILL.md packs):

## Do this
1. `git clone --depth 1 <url> ~/Documents/Projects/research/<name>` (reuse clone if present).
2. `find . -name SKILL.md | sort`
3. One code pass: parse frontmatter `name`/`description` + first procedure section as "how it works".
4. Deliver category tables + import shortlist (4–8) + batch go-ahead options.
5. Optional durable MD under `~/Documents/Projects/research/`.

## Do not
- Serially `web_extract` every skill page or raw.githubusercontent URL (truncation + rate limits + call explosion).
- Treat README as complete inventory.

## Session anchor (2026-07-08)
- Clones: `~/Documents/Projects/research/{MengTo-Skills,davidondrej-skills,project-nomad}`
- Catalog: `~/Documents/Projects/research/SKILLS-AND-NOMAD-CATALOG.md`
- Packs: MengTo (UI/design, ~95), davidondrej (agent ops, 29); NOMAD is a Docker product not a skill pack.

## Import hygiene
Active Hermes profile only; strip foreign absolute paths/secrets; no blind upstream auto-sync; label tool-lock-in (Pi/cmux/DeepAPI).
