---
name: agent-resource-triage
description: Triage a batch of AI-agent / LLM GitHub repos (or link dumps) for personal relevance — collapse star-inflated lists into the few that actually apply to your stack and workflow. Use when the user pastes a list of GitHub links and asks "which are worth it" / "review these resources" / "look into all these".
---

# Agent Resource Triage

Class of task: user pastes N GitHub repo URLs (usually AI-agent / LLM / GenAI lists) and wants to know what's actually useful. **Star count is marketing reach, not applicability** — triage by artifact type and fit, never by popularity.

## Method (3 passes)
1. **Bucket by artifact type** — each repo is one of:
   - **Catalog/list** (awesome-X, 500-projects) — scan once, grep later, never study.
   - **Course** (MS/HF lesson series) — pick ONE, skim only lessons past the user's level.
   - **Cloneable code** (awesome-llm-apps, GenAI_Agents notebooks) — highest utility; gut and keep patterns.
   - **Non-agent** (inference tricks, model weights) — out of scope unless the user's stack needs it.
2. **Filter by the user's actual goal** — strip anything that doesn't map to their current stack. (Finance agents don't matter if they said "not finance"; Azure/Foundry courses don't matter if they're on Nous/OpenAI.)
3. **Rank by direct applicability** — what can be cloned/adapted this week vs. what's reference reading only.

## Fleet-wide gap mapping (multi-profile fleet)

When the user asks to review an external skill/plugin repo AND cherry-pick installs spread across profiles, the deliverable is a per-profile ADD/REPLACE matrix, not a verdict table. This user runs 23 profiles — never gap-check against only the current profile.

1. **Clone the source repo** (don't scrape the web page for a catalog). Inventory every SKILL.md; read `name:` + `description:` from frontmatter. Descriptions folded with `>-` need multiline unfolding — the first regex pass will silently return `>-`; unfold by accumulating subsequent indented lines.
2. **Inventory ALL profiles' skills from disk**: `find ~/.hermes/profiles/*/skills -name SKILL.md`, take the parent-dir basename as the skill name. This is the only true overlap source.
3. **Compute fleet-wide overlap by name** (remote ∩ union-of-all-profiles). A senna-only diff massively overstates novelty — a repo's CLI skills are usually already installed on media/knowledge/business (e.g. arr/jellyfin/trakt set, epub/gutenberg/openlibrary, jira/ghost/raleigh/yc).
4. **Version-check overlaps before calling them REPLACE candidates**: grep the frontmatter `version:` field and compare file sizes (remote often has no version field — then sizes tell the story). Most shared skills are already current; a "new" repo usually needs zero replacements.
5. **Map the uninstalled remainder to profiles by domain** (role list: code/infra/mlops/research/knowledge/finance/business/creative/novel/security/cyber-*/homelab/communication/social/educate/senna). Tier each: A install-now / B install-if-domain-grows / skip. Treat repo bundles as single units with one recommended owner profile.
6. **Output shape**: Part 1 already-in-fleet (with which profiles — no action), Part 2 per-profile ADD matrix (tiered), Part 3 replacements (usually 'none'), Part 4 bundles, Part 5 fleet hygiene (duplicate same-name skills inside one profile — report, don't fix unprompted).
7. Ask before installing. Offer a one-shot Tier-A + bundles install as the default.

## Output shape
A table: `repo | one-liner | verdict (high-value / reference / skip)`, then a 3-row priority list, then offer the next concrete move (deep-dive / clone / save-as-skill). Do NOT write essays per repo.

## Pitfalls
- Don't read every repo. `web_extract` the headers in parallel, synthesize from one-liners + star count as a *quality prior* (not truth).
- Don't recommend beginner courses to an advanced user. Check their profile — if they run a multi-profile fleet, lessons 1–3 are waste.
- Star count correlates with listicle marketing, not usefulness. A 21k repo and a 123k repo can both outrank a 113k one for a given user.
- Catch hidden signal: a course's *eval* or *memory* chapter often unblocks a stalled project even when the course itself is skippable.
- "Model weights released today?" — don't trust the HF org page or press; it lags on release day. Verify via API: `curl -s https://huggingface.co/api/models/<org>/<model>` (check `lastModified` + `siblings` for actual safetensors shards), then pull architecture/quant/context facts straight from `https://huggingface.co/<org>/<model>/raw/main/config.json` (num layers, expert count, `quantization_config`, `max_position_embeddings`). Faster and more truthful than any article.
- Don't scope the gap check to the current profile when the user has a fleet. "Which of these do we already have?" means fleet-wide, always. A single-profile answer was corrected once ("I don't want you to just focus on senna") — do the 23-profile union first.
- Bulk-install offers: never auto-install a Tier-A list; the user wants to trim. Default to asking with the trimmed list pre-built.
- Folded frontmatter (`description: >-`) breaks naive `^description:` regexes. Unfold multi-line values or you'll report empty descriptions for half the repo.
- A repo can be a GitHub mirror of a Forgejo/Gitea source you already reviewed (magnus919/agent-skills). Check session history for the original host before re-reviewing from scratch — the growth delta (commit count, bundle list) is often the only new information worth reporting.

## references/
- `references/visual-loop-review-2026-08.md` — deep-dive of Salt-555/visual-loop (critique-driven visual iteration bundle): loop + regression policy summary, relevance to the AgentUnreal verified-self-growth thesis, install-status pending. Check before re-analyzing that repo.
- `references/fleet-review-magnus-2026-08.md` — the fleet-wide gap mapping of magnus919/agent-skills across all 23 profiles: 27 already-in-fleet placements, Tier-A per-profile add list, bundle owners, hygiene notes. Check before re-reviewing that repo or re-running the analysis.
