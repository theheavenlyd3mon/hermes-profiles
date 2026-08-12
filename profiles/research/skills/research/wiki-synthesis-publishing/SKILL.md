---
name: wiki-synthesis-publishing
description: "Publish a COMPLETED multi-source research investigation to an LLM-Wiki as a canonical synthesis concept page + findings manifest, with raw-source ingests (real sha256) and schema/taxonomy extension. Use when the user says 'turn this research into a wiki page', 'push a canonical page + manifest into the wiki', or after a research sweep that produced synthesis worth persisting. Complements (does not replace) the llm-wiki skill's Ingest/Query/Fabric/Lint operations."
version: 1.0.0
author: Hermes Research Orchestrator
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, synthesis, publishing, llm-wiki]
    category: research
    related_skills: [llm-wiki, arxiv, open-source-research]
---

# Wiki Synthesis Publishing

Publish a **finished** multi-source research investigation to the LLM-Wiki as a canonical synthesis page
plus a findings manifest. This is the **synthesis-publishing** pattern — distinct from:

- **Ingest (llm-wiki op 1):** user hands ONE raw source → ingest it.
- **batch-research-ingest-workflow.md (inside llm-wiki):** "research X and add to wiki" — search →
  extract → ingest, usually one concept per source.
- **This op:** an investigation ALREADY done (multiple sources synthesized) → publish as ONE canonical
  concept page + ONE manifest + N immutable raw ingests.

> **NOTE on `llm-wiki`:** The `llm-wiki` umbrella skill is the canonical home for wiki operations, but in
> this environment it is flagged `created_by=None` (manually authored) and is **off-limits to autonomous
> curation**. This skill captures the synthesis-publishing sub-pattern that `llm-wiki` does not yet
> document. If `llm-wiki` becomes editable later, this content could be merged into its Core Operations
> as "2b. Research Investigation → Canonical Page + Manifest" (the exact section text is preserved in
> `references/llm-wiki-section-2b.md`).

## When this skill activates

- User: "turn this research into a wiki page / push a canonical page + manifest into the wiki"
- After a research session produced a synthesis the user wants persisted as a wiki page
- You've finished a multi-angle investigation and want it to compound in the wiki

## Prerequisites

- A wiki at `WIKI_PATH` following the `llm-wiki` SCHEMA (SCHEMA.md, index.md, log.md, `raw/` immutable).
- The research is DONE — you have sources, a synthesis, and (ideally) confidence calibration.

## Procedure

① **Orient** (critical — do this every session):
   - Verify `WIKI_PATH` exists. On macOS the env may say `LLM-Wiki` but the real dir is `llm-wiki`
     (HFS+ hides case; Linux breaks on the mismatch). `ls -d "$WIKI_PATH"` first.
   - Read `SCHEMA.md`, `index.md`, recent `log.md`. Search for existing pages on the topic before
     creating anything (avoids duplicates / missed cross-links).

② **Extend taxonomy FIRST if a new domain appears.** If the topic has no tag section (e.g.
   `creative-writing`), add a new `#### Topic Section` to SCHEMA.md with needed tags **before** using
   them (SCHEMA rule: declare tags before use). One patch.

③ **Ingest sources as raw files** under `raw/articles/<category>/`:
   - Write body + raw frontmatter (`source_url`, `ingested: YYYY-MM-DD`, `sha256: TODO`).
   - **Compute REAL sha256 over the whole file and backfill** — never ship `TODO`/`placeholder`:
     ```bash
     shasum -a 256 "raw/articles/<cat>/<file>.md" | cut -d' ' -f1
     ```
     Then patch the `sha256:` line. Lint flags placeholder/fake hashes as `[INFO] placeholder`.
   - Raw is IMMUTABLE. Never edit a raw file after ingest.

④ **Write the findings manifest** at `raw/articles/<category>/findings-YYYY-MM-DD.md`:
   - Research question, sources investigated, key findings, contradictions/tensions (documented, NOT
     resolved), confidence table, deliverables.
   - It IS a raw file → give it raw frontmatter and a REAL sha256 too (don't fake the manifest hash).

⑤ **Write the canonical concept page** at `concepts/<slug>.md` (NOT a raw file — full wiki frontmatter):
   - `type: concept`, `composes: []` (root synthesis — no `composed_by` backfill needed),
     `contested: true` when genuine tensions exist, `workflow: developing`.
   - `confidence: high` ONLY when primary sources were ingested directly; `medium` for contested/cognitive claims.
   - Body: synthesized playbook; append `^[raw/articles/<cat>/<file>.md]` provenance markers to paragraphs
     tracing to a specific source; include a "## Related pages" section with ≥2 `[[wikilinks]]` to existing
     pages so it isn't isolated.

⑥ **Update index.md** — add the new concept entry (alphabetical), bump 'Total pages' and 'Last updated'.
   **Batch all index changes into ONE patch call** (sequential patches duplicate entries); use execute_code
   / Python for 3+ entries.

⑦ **Append to log.md** — one entry: agent, trigger, files created (concept + manifest + N raw ingests),
   taxonomy extension, index bump, confidence, contradictions noted. **Prefer Python append** over patch
   (avoids anchor/pipe-prefix corruption — see llm-wiki Refresh pitfall):
   ```python
   p = f"{WIKI}/log.md"
   s = open(p).read()
   entry = "\n## 2026-07-21 create | <subject>\n- Agent: Research ...\n- ...\n"
   open(p,'w').write(s.rstrip()+'\n'+entry)
   ```

⑧ **Report** every file created/updated to the user.

## Pitfalls

- **Placeholder sha256 in the manifest** — the manifest is a raw file; hash it for real.
- **Taxonomy-before-use** — tags used in a page but absent from SCHEMA.md are a lint error. Extend first.
- **`composed_by` backfill not needed** — a root synthesis page has `composes: []`; only pages that BUILD
  on it later get `composed_by`. Don't invent backlinks.
- **WIKI_PATH case** — env may say `LLM-Wiki`; real dir is `llm-wiki`. Orientation ① catches it.
- **Batch index updates** — one patch for all index additions; sequential patches duplicate entries.
- **Log append via Python** — never patch-append to log.md (anchor/pipe-prefix corruption).
- **Protected `llm-wiki`** — do not attempt to edit `llm-wiki` itself (created_by=None, off-limits to
  autonomous curation). This skill is the sanctioned satellite for the synthesis-publishing pattern.

## References

- `references/llm-wiki-section-2b.md` — the exact "2b" section text to merge into `llm-wiki` if it
  ever becomes editable, plus the worked example from this session (creative-writing investigation →
  canonical page + 5 raw ingests + manifest).
- `references/worked-example-creative-writing.md` — full command sequence + file inventory from the
  novel-craft investigation that spawned this skill.
