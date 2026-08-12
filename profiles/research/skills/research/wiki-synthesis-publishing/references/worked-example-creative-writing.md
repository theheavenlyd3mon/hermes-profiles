# Worked Example — Creative-Writing Investigation → Wiki (full command sequence)

Spawns from: a finished research sweep on novel-writing craft + tooling. Goal: persist as a canonical
wiki page + manifest.

## Step 0 — Orient (verify path + read nav)

```bash
WIKI="~/Hermes Vault/Hermes/llm-wiki"   # lowercase! env may say LLM-Wiki
ls -d "$WIKI" || echo "WIKI_PATH mismatch"
```
Read `SCHEMA.md`, `index.md`, `log.md`. Search `concepts/` for 'novel'/'fiction' to avoid dupes.

## Step 1 — Extend SCHEMA taxonomy (new domain)

`patch` SCHEMA.md, add before "#### Unreal Engine & Game Development":
```markdown
#### Creative Writing & Narrative
- `creative-writing` — novel/fiction writing craft, methodologies, author workflows
- `fiction` — fiction genres and craft (fantasy, sci-fi, literary)
- `storytelling` — narrative structure, story theory, cognition of narrative
- `worldbuilding` — fictional world construction, magic systems, setting design
- `writing-craft` — prose craft, revision, editing techniques
- `novel` — long-form fiction specifically
```

## Step 2 — Ingest raw sources (real sha256)

For each source write the file with frontmatter `sha256: TODO`, then:
```bash
for f in "$WIKI/raw/articles/research/creative-writing"/*.md; do
  h=$(shasum -a 256 "$f" | cut -d' ' -f1)
  # patch the file: replace "sha256: TODO" -> "sha256: $h"
done
```
Files: sanderson-three-laws-of-magic, snowflake-method, scene-and-sequel,
universal-narrative-model (arXiv:2503.04844), narrativity-and-enaction (PMC4141283).

## Step 3 — Write findings manifest (also raw → real hash)

`raw/articles/research/creative-writing/findings-2026-07-21.md`
Frontmatter: `source_url: hermes://research-synthesis/novel-craft`, `ingested: 2026-07-21`,
`sha256: <real>` (compute it — don't fake).
Body: research question, sources investigated, 8 key findings, contradictions (documented not resolved),
confidence table (practitioner high / cognitive medium / tools preference-derived), deliverables.

## Step 4 — Write canonical concept page (full wiki frontmatter, not raw)

`concepts/novel-craft-playbook.md`
```yaml
---
title: Novel Craft Playbook
created: 2026-07-21
updated: 2026-07-21
type: concept
tags: [creative-writing, fiction, storytelling, worldbuilding, writing-craft, methodology]
sources:
  - raw/articles/research/creative-writing/sanderson-three-laws-of-magic-2026-07-21.md
  - raw/articles/research/creative-writing/snowflake-method-2026-07-21.md
  - raw/articles/research/creative-writing/scene-and-sequel-2026-07-21.md
  - raw/articles/research/creative-writing/universal-narrative-model-2026-07-21.md
  - raw/articles/research/creative-writing/narrativity-and-enaction-2026-07-21.md
confidence: high
contested: true
workflow: developing
topics: [creative-writing, novel, fiction-craft, storytelling, worldbuilding]
composes: []
---
```
Body: core principle, two-mode intake, 4-stage pipeline (design → magic/worldbuilding → draft → revision),
frameworks table, cognitive grounding, tools, guardrails, contested points, related pages (≥2 wikilinks).
Append `^[raw/...]` provenance markers on synthesized paragraphs.

## Step 5 — Update index.md (ONE batched patch)

- Bump header: `Last updated: 2026-07-21 | Total pages: 103`
- Add under Concepts:
  `- [[novel-craft-playbook]] — Novel/fiction craft playbook: Snowflake + MICE + Scene/Sequel pipeline, Sanderson's 3 Laws of Magic, cognitive storytelling grounding, 5-stage revision, 2026 AI tooling`

## Step 6 — Append log.md (Python, not patch)

```python
p = "~/Hermes Vault/Hermes/llm-wiki/log.md"
s = open(p).read()
entry = (
  "\n## 2026-07-21 create | Novel craft research → wiki (creative-writing category)\n"
  "- Agent: Research (interactive, user request)\n"
  "- Trigger: User asked to push a canonical page + findings manifest into the LLM-Wiki\n"
  "- Created: concepts/novel-craft-playbook.md\n"
  "- Ingested 5 raw sources (immutable, sha256-hashed) under raw/articles/research/creative-writing/\n"
  "- Wrote manifest: raw/articles/research/creative-writing/findings-2026-07-21.md\n"
  "- SCHEMA taxonomy extended: Creative Writing & Narrative (6 tags)\n"
  "- Index: 102 -> 103; Confidence: high (primary sources ingested directly)\n"
)
open(p,'w').write(s.rstrip()+'\n'+entry)
```

## Step 7 — Report to user

List every file created/updated; note protected `llm-wiki` was not edited; confirm sha256 real (not placeholders).
