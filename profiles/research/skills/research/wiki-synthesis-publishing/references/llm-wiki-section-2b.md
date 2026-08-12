# Exact "2b" section to merge into `llm-wiki` SKILL.md (if it becomes editable)

This is the Core Operations section text for the Research Investigation → Canonical Page + Manifest
pattern. If/when the `llm-wiki` skill (currently `created_by=None`, off-limits to autonomous curation)
becomes editable, merge this as new operation "2b" between "2. Query" and the existing operations.

```markdown
### 2b. Research Investigation → Canonical Page + Manifest

When the user asks to turn a **completed multi-source research investigation** into the wiki as a canonical
synthesis page + findings manifest. This is distinct from: (a) Ingest — user hands ONE raw source; and
(b) "research X and add to wiki" — see `references/batch-research-ingest-workflow.md`. This operation is
the **synthesis-publishing** pattern (e.g., the novel-craft investigation → `concepts/novel-craft-playbook.md`
+ 5 raw ingests + `findings-2026-07-21.md`).

① **Orient** (steps ⓪–③) — verify `WIKI_PATH` (case-correct!), read SCHEMA/index/log, search for existing
   pages on the topic before creating anything.
② **Extend taxonomy FIRST if a new domain appears.** If the investigation spans a topic with no tag
   section (e.g., `creative-writing`), add a new `#### Topic Section` to SCHEMA.md with the needed tags
   **before** using them (SCHEMA rule: add tags before use). One `patch` call.
③ **Ingest sources as raw files** under `raw/articles/<category>/`:
   - Save body with raw frontmatter (`source_url`, `ingested`, `sha256:` placeholder).
   - **Compute REAL sha256 over the whole file and backfill** — never ship `TODO`/`placeholder`:
     `shasum -a 256 "raw/articles/<cat>/<file>.md" | cut -d' ' -f1`
     Then `patch` the `sha256:` line. The lint script flags placeholder hashes — see Pitfalls.
④ **Write the findings manifest** at `raw/articles/<category>/findings-YYYY-MM-DD.md` — research question,
   sources investigated, key findings, contradictions/tensions (documented, **not** resolved), confidence
   table, deliverables. Same raw frontmatter + real sha256 (it IS a raw file — hash it for real too).
⑤ **Write the canonical concept page** at `concepts/<slug>.md`:
   - Frontmatter: `type: concept`, `composes: []` (root synthesis — no `composed_by` backfill needed),
     `contested: true` when genuine tensions exist (e.g., outlining vs discovery writing),
     `workflow: developing`, `confidence: high` ONLY when primary sources were ingested directly.
   - Body: synthesized playbook; append `^[raw/articles/<cat>/<file>.md]` provenance markers to paragraphs
     tracing to a specific source; include a 'Related pages' section with ≥2 `[[wikilinks]]` to existing
     pages so it isn't isolated.
⑥ **Update index.md** — add the new concept entry (alphabetical), bump 'Total pages' and 'Last updated'.
   **Batch all index changes into ONE `patch` call** (sequential patches duplicate entries — see Pitfalls);
   use `execute_code`/Python for 3+ entries.
⑦ **Append to log.md** — one entry: agent, trigger, files created (concept + manifest + N raw ingests),
   taxonomy extension, index bump, confidence, contradictions noted. **Prefer Python append** over `patch`
   for log.md (avoids anchor/pipe-prefix corruption — see Refresh pitfall).
⑧ **Report** every file created/updated to the user.

**Companion recipe:** `references/research-investigation-to-wiki.md` — exact command sequence + worked
example (creative-writing investigation → canonical page + 5 raw ingests + manifest).
```

## Worked example (the session that spawned this skill)

Topic: novel-writing craft & tooling for a novel profile.
- New taxonomy section added to SCHEMA.md: `#### Creative Writing & Narrative` → tags
  `creative-writing, fiction, storytelling, worldbuilding, writing-craft, novel` (added BEFORE use).
- 5 raw ingests (immutable, real sha256):
  - `sanderson-three-laws-of-magic-2026-07-21.md` (21882ce0…)
  - `snowflake-method-2026-07-21.md` (b22baa5d…)
  - `scene-and-sequel-2026-07-21.md` (ec3dee6e…)
  - `universal-narrative-model-2026-07-21.md` (f20787b1…) — arXiv:2503.04844
  - `narrativity-and-enaction-2026-07-21.md` (f55dfcf1…) — Front. Psychol. 2014, PMC4141283
- Manifest: `findings-2026-07-21.md` (real sha256 699f9f97…)
- Canonical page: `concepts/novel-craft-playbook.md`
  - `composes: []`, `contested: true` (outlining-vs-discovery / hard-magic-dogma / story-grammar-rigidity)
  - cross-links: `persrubric-llm-personality-encoding`, `mega-prompt-engineering`, `llm-wiki-pattern`,
    `agent-skills-standard`, `obsidian-agent-skills`
- index.md: 102 → 103; log.md: appended entry.
- Companion runnable skill created separately: `novel-craft-playbook` (creative-writing category) —
  the agent-loadable twin of this wiki page.
