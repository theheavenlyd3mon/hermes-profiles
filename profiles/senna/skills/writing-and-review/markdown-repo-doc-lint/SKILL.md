---
name: markdown-repo-doc-lint
description: Audit and patch a repo's Markdown documentation for tone consistency, section-skeleton drift, dead relative links, and stale boilerplate. Use when asked to review READMEs, guides, profile docs, or any markdown corpus, and return exact diffs or a per-file verdict instead of summary prose.
version: 1.0.0
metadata:
  hermes:
    tags: [docs, markdown, audit, lint, patches]
---

# Markdown Repo Doc Lint

Review a Markdown documentation corpus for:
- tone consistency across top-level files
- section-skeleton drift against the actual file/entity set
- dead relative links
- redundant or stale boilerplate phrases

## Inputs

- repo root path
- scope: top-level READMEs only, or recurse into subdirectories
- style baseline: one canonical file whose section skeleton is treated as normative
- link-host policy: which relative-link host is authoritative (`/guides/` or repo root)

## Workflow

1. Inventory scope.
   - Glob README files and top-level guide docs.
   - Build a manifest of actual entities: directories, profile folders, skill names, external URLs.

2. Pick the canonical skeleton.
   - Choose the newest or best-structured README as the section baseline.
   - Lock the sequence: `## When to Use` -> `## How It Works` -> `## Skills`/`## Skills (N total)` -> `## Personality` -> `## Configuration` -> `## SOUL.md`.
   - Note any intentional variants up front.

3. Per-file audit.

   ### 3.1 Dead-link scan
   - Extract every relative link matching `](...)` that is not `http`, `https`, `#`, or `mailto`.
   - Resolve from the file's own directory; do **not** resolve from repo root.
   - Failure mode: file missing, path mismatched by case, parent-directory boundary crossed unintentionally.

   ### 3.2 Section-skeleton check
   - For every README in scope, compare its section headings against the canonical sequence.
   - Flag:
     - missing sections
     - extra sections not in canonical
     - reordered sections
     - sections that exist in the manifest but not in the docs, or vice versa
   - For Skills sections: if `Skills (N total)` exists anywhere, require the same heading shape everywhere in that class of file. If a file intentionally omits the count, it should still keep a `## Skills` heading unless intentionally section-stripped.

   ### 3.3 Drift vs actuals
   - For entity lists in README tables/trees: every listed entity must exist on disk or in the manifest.
   - For counts (`N total`): compare against the actual skill directory count.
   - For model/version strings: warn if a listed model has not been reviewed for relevance.

   ### 3.4 Tone / phrasing
   - Scan for stale boilerplate: "coming soon", "more profiles soon", placeholder TODOs, "TBD", "near future".
   - Compare sentence length and register between sibling READMEs; flag outliers.
   - Prefer concise role-sentence openings: "<Noun>. <Sentence>. "Do not use em dashes mid-sentence for role definitions.

4. Patch decisions.

   For each file, choose exactly one verdict:
   - **Exact patch provided** — when a fix is mechanical or unambiguous.
   - **No changes needed** — when the file is already correct.
   - **Needs human judgment** — when the doc's intent is unclear or fixing it would change design.

   Patches must:
   - Be reproducible via tools not redone by hand each session.
   - Preserve existing formatting style (Markdown pipe tables, fenced code blocks, heading style).
   - Change wording only when it fixes a defect identified in Section 3, not to "improve" prose that is already consistent.

5. Output.

   Return a per-file verdict block:

   ```
   FILE: <path>
   VERDICT: <EXACT PATCH | NO CHANGES NEEDED | NEEDS HUMAN JUDGMENT>
   ISSUES:
     - <issue summary or empty>
   DIFF or NOTE: <unified diff, or one-line reason>
   ```

## Pitfalls

- Relative links are resolved from the file's directory, not repo root. A `guides/` README linking to `./hermes-obsidian-setup-guide.md` is silently wrong when the file lives at repo root; this is the single most common dead-link pattern in profile collections.
- Do not invent fixes for skill counts you have not verified by listing the directory. If N cannot be confirmed accurately, prefer omitting or leaving `N total` off that file rather than patching with a guessed count.
- "No changes needed" is a real output, not a placeholder. Deliver it honestly rather than manufacturing trivial changes.

## See Also

- `team-wiki/maintain` — Team-Wiki lint/health check uses a similar structure of per-check actions and text/stdout reporting.
- `team-wiki/sync` — re-index after structural changes.
