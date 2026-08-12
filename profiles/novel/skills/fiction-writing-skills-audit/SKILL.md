---
name: fiction-writing-skills-audit
description: Evaluate the skills ecosystem (registry + web + GitHub) to identify installed skills, recommend installations, and map gaps requiring custom skill creation for long-form AI-assisted fiction pipelines. Use when setting up a new book-writer profile, expanding from short-novel to multi-book scope, or assessing pipeline capability before committing to a series pitch.
version: 1.0.0
---

# Fiction Writing Skills Audit

When planning or expanding an AI-assisted long-form fiction pipeline, systematically evaluate what skills already exist, what should be installed, and what must be built custom. This prevents reinventing wheels and ensures the pipeline has the architecture needed for the target scope.

## Procedure

### 1. Inventory Installed Skills
Run `skills_list()` or `hermes skills list` to catalog what's already installed in the active profile. Note which are pinned (can patch/edit but not delete), which are bundled/protected, and which are hub-installed.

### 2. Search External Registry
Update the iknowkungfu registry (`mcp__iknowkungfu__update_registry`) then search for relevant terms:
- `writing craft`, `story structure`, `humanize style`, `obsidian`, `prose quality`
- Note: the registry may return zero results for creative-writing queries even when real repos exist. Don't treat empty results as "nothing exists."

### 3. Web/GitHub Search
Search multiple angles simultaneously:
- GitHub repositories: `[tool] + [domain] + github` (e.g., `humanizer fiction claude code github`)
- Community discussions: Reddit r/ClaudeAI, r/WritingWithAI
- Comparison sites: SkillsLLM comparison matrix
- Extract and review top candidate repos for README + SKILL.md

### 4. Categorize Findings
Place each found skill into tiers:
- **Tier 1 (High Priority):** Fills a critical gap, high star count/community adoption, install immediately
- **Tier 2 (Review/Conditional):** Could be useful but needs evaluation before full install
- **Redundant:** Already covered by installed skills; skip

### 5. Map Gaps
After reviewing external options, identify what does NOT exist but IS needed:
- Multi-book/saga continuity tracking (rarely addressed by single-skill solutions)
- Power system/magic system consistency engines (specific to progression-fantasy)
- Emotional beat mapping across volumes (beyond plot tracking)
- Obsidian vault integration for novel planning (community interest but fragmented implementations)
- Cross-book voice calibration drift detection

### 6. Recommend Actions
Present findings to user with:
- List of recommended installs with rationale
- Custom skill proposals with priority ratings
- Any registry/search limitations encountered

## Critical Insights

- **Multi-book series orchestration is an unmet niche.** Most available fiction-writing skills target single novels or one-session drafting. When users expand to 3–5+ books, gaps appear quickly in continuity, power progression, and cross-volume voice lock.
- **Registry searches alone are unreliable for creative-domain skills.** The iknowkungfu registry appears heavily skewed toward coding/devops tooling. Always follow up with direct GitHub/web searches.
- **Humanizer is nearly universal value.** The `blader/humanizer` skill (⭐30k) removes 33 AI-writing patterns and includes voice calibration. Install early in any publication-bound pipeline.
- **Don't skip external reviews.** Writing your own everything-from-scratch skills wastes time on solved problems. Install proven skills first, build custom ones only for genuine domain gaps.

## Pitfalls

- **Installing everything at once.** Evaluate Tier 2 skills individually before installing; some may conflict or overlap with installed skills.
- **Assuming all found skills integrate with Hermes.** Many were built for Claude Code; verify SKILL.md format compatibility. Use `--agent hermes` during install.
- **Ignoring the humanization step.** Pipeline draft → revisor review → humanize → export. Without the humanizer pass, published text may retain detectable AI patterns.
- **Underestimating multi-book complexity.** A single-book audit looks complete until Book 2 shows character arc drift. Always audit with the expected series length in mind, not just the first book.
- **Pinned skills block autonomous updates.** Pinned skills (via `hermes curator pin`) cannot be patched by the background curator. If you need to update them, ask the user to run `hermes curator unpin <name>` first.
