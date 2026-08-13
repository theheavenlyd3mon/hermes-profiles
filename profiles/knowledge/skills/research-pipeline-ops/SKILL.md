---
name: research-pipeline-ops
description: "Wiki research-pipeline: overflow and verification."
version: 1.0.0
author: Senna (Hermes)
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [obsidian, wiki, research, pipeline, cron, verification]
    related_skills: [team-wiki/research-pipeline, team-wiki/maintain, note-taking/obsidian]
---

# research-pipeline-ops

IDENTITY: Ops.Runner. DetectCategories→CompareDates→Ingest→VerifyBatch→Report.
Complements `team-wiki/research-pipeline` (the ingestion contract — threshold gate, frontmatter, contradiction protocol, index/log rules). This skill owns the **run orchestration and verification** around that contract: deciding which categories need processing, verifying a multi-page batch afterward, and the tool pitfalls that appear when executing in cron. Load both for a full pipeline run.

WHENUSE: Overflow pass over all research categories|Knowledge Manager Sunday ingest|Verifying a multi-page pipeline run|Any cron wiki batch hitting tool quirks.
NoSkip: FindingsFileListing|LogDateParsing|RawImmutabilityCheck|WikilinkResolutionCheck.

## Multi-category overflow detection

When the task is an overflow/KM pass over *all* research categories (not one assigned category):

1. List findings files: `search_files(target='files', pattern='findings-*.md', path='raw/articles/research/')`. Group by category directory.
2. Parse `log.md` for the last processed date **per category**: search for `## YYYY-MM-DD <slug> pipeline` and `overflow pass` entries (they record the scope). A category with no such entry has never been processed.
3. Process only categories whose **newest findings-YYYY-MM-DD filename date > last processed date**. Equal-or-older findings are skipped. Retired categories (protocol pivot table, e.g. 2026-08-04) are skipped unless a newer findings file exists — a retired cron that still fires is an attention item, not a re-run trigger.
4. Categories with **no findings files at all** are skipped but MUST appear in the report ("no findings files") — a new active category silently producing nothing is a cron-health attention item.
5. Log: ONE batch entry with a `### <category> pipeline` subsection per processed category plus a `### Summary` block (precedents: 2026-08-02 and 2026-08-09 log entries). Never one entry per category.

## Batch verification

For multi-page runs, run `scripts/verify-pipeline-run.sh <wiki_root> <new page paths...>` instead of hand-checking each page. It checks:
- frontmatter completeness (title/type/created/updated/tags/sources/workflow/confidence)
- ≥2 outbound `[[wikilinks]]` per page, all resolving to existing slugs
- raw/ immutability via mtime (no raw file modified on run date)
- index.md contains at least one entry per new page slug

Exit 0 = all pass; non-zero with a per-file failure list otherwise. Trust the script's failures — they are real (missing frontmatter field, unresolved link, raw write). Fix and re-run.

## Full-wiki sweep (audit, not batch verify)

When the ask is "sweep / audit the wiki" (not verifying one batch), run `scripts/wiki-sweep.py <wiki_root>` — it audits every knowledge page in one read-only pass and prints a sectioned report. Checks (mirrors `team-wiki/maintain` but executable):
- frontmatter: required fields, type↔directory match, workflow presence in EITHER style, valid confidence, contested⇒contradictions, tags in taxonomy
- wikilinks: graph resolution, ghost-note inventory with backlink counts (promote at 3+), stale zero-backlink ghosts
- orphans: knowledge pages with no inbound links (flags `[index-only]` vs fully disconnected)
- index completeness: every knowledge slug in index.md AND every index link resolving to an existing page
- outbound minimum (<2 links), oversized pages (>200 lines per SCHEMA), raw/ mtime within 3 days, log entry count vs 500 threshold

Add the **cron-drift cross-check** to every sweep: compare `cronjob list` against the category table in `operational/protocols/research-pipeline-categories.md`, BOTH directions. Verified 2026-08-10: the 2026-08-04 pivot retired 6 categories (llm-agents, agent-protocols, context-engineering, local-inference, prompt-engineering, research-methodologies) and added 5 new ones (local-llm, open-source-models, generative-media, llm-research, ai-advancement), but ALL 6 retired crons remained scheduled/enabled (llm-agents fired the morning after its own log flagged retirement) and NO cron existed for any new category. A retired cron firing is an attention item, not a re-run trigger; an active category with no cron and no findings files is silent cron-health drift. Also check the inverse: a `findings-YYYY-MM-DD.md` with no registered cron that could have produced it is an anomaly worth flagging.

## Workflow-tag convention split (verified 2026-08-10 sweep)

The wiki has TWO coexisting workflow styles, and SCHEMA.md, the research-pipeline skill, and `verify-pipeline-run.sh` each imply a different one:
- **Key style (~103 pages):** separate frontmatter key `workflow: developing|stable|seedling|...`. This is what `verify-pipeline-run.sh` greps for (`^workflow:`), so key-style pages pass verification.
- **Tag style (newest pages, ~11):** `workflow:seedling` INSIDE `tags: [..., workflow:developing]` (airi-ai-companion, streamcore-server, browsafe, solar/ pages). These FAIL `verify-pipeline-run.sh`'s `workflow:` key check despite being valid per SCHEMA's "Workflow Tags" section.

Before treating a tag-style page as a verification failure, check for `workflow:<state>` inside the tags list. Also flag non-canonical values (`workflow: proposed`, `workflow: reference` seen on hermes-platform-tool-loading, hermes-desktop-profile-management, threejs-hologram-particle-techniques — allowed set is seedling|developing|stable|needs-review|stale) and pages with NEITHER style (moonlake-blender-mcp-ue5-pipeline-report, ue-ai-coding-pipeline-report — also missing updated/sources, non-SCHEMA type `research-report`).

**RESOLVED 2026-08-10 (user approved "go with your recommendations"):** the dedicated `workflow:` key is the canonical lifecycle form; in-tags `workflow:xxx` is legacy-accepted and normalized to the key on lint. SCHEMA.md now documents the key as canonical (frontmatter example, Field Reference, Workflow Tags section), `verify-pipeline-run.sh` validates the value against seedling|developing|stable|needs-review|stale, and 11 tag-style pages were normalized to key-style. When sweeping now: flag pages with NEITHER style or non-canonical values; converting tag-style → key-style is the sanctioned fix (moves `workflow:seedling` out of `tags:` into a `workflow:` key line). Also: `type: summary` is a VALID type for pages in `concepts/` (research-report summaries, e.g. the two fixed pipeline reports) — do not flag it as a dir mismatch. See `references/2026-08-10-sweep-remediation.md` for the full remediation playbook.

## Tool pitfalls (verified in the 2026-08-09 overflow run; sweep pitfall added 2026-08-10)

- **BSD grep "invalid character range"**: `grep -o '\[\[[^]]*\]\]'` fails on macOS. Extract wikilinks with `grep -oE '\[\[[^]]+\]\]' | tr -d '[]' | sort -u`.
- **read_file binary false positive**: `read_file` may report "Binary file - cannot display as text" for a valid UTF-8 page (hit on `concepts/model-landscape-2026.md`). Verify with `file <page>` and `xxd <page> | grep ' 00 '` — no null bytes means false positive. Read via `cat`, patch normally (`patch` still works), and do NOT rewrite the file to "fix" it.
- **execute_code is denied in cron context** (arbitrary Python needs user approval; none present in cron). Don't use it for batched searches in cron runs — batch parallel `search_files`/`read_file` calls instead, and use `terminal` for aggregate read-only verification sweeps.
- **Tag-list parsing traps in sweep/audit scripts**: naive regex token extraction (`[a-z][a-z0-9-]+`) splits `workflow:seedling` at the colon into two tokens (`workflow`, `seedling`) and mangles leading-digit tags (`3d-modeling` → `d-modeling`). On the 2026-08-10 sweep this produced ~90 false "no workflow tag" / "tag not in taxonomy" flags. Parse `tags:` by stripping brackets/quotes and splitting on commas, then check `workflow:<state>` as a single token. (The sweep script in `scripts/wiki-sweep.py` already does this.)

## Protected-skill relationship

`team-wiki/research-pipeline` (and the `team-wiki/*` family) is user-owned in this profile: `skill_manage` refuses both the qualified name ("not found") and the unqualified alias ("not curator-managed — no usage record"). Until `hermes curator adopt team-wiki/research-pipeline` is run, this umbrella carries the ops knowledge. When the adoption happens, merge this skill's content into `team-wiki/research-pipeline` and delete this one (absorbed_into=team-wiki/research-pipeline).

## Related

- `team-wiki/research-pipeline` — the ingestion contract this skill wraps
- `team-wiki/maintain` — daily lint/health-check (overlaps the verification sweep; curator may consolidate)
- `note-taking/obsidian` — file-tool discipline for vault work
