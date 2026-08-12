# Skills Audit Guide — Eldrath Series Pipeline

## How to Run a Complete Skills Audit for Writing Projects

This document captures the full search methodology, verified results, and source URLs from the Eldrath series pipeline audit (2025-07).

### Step 1: Hub Search Technique

The Hermes skills hub (79,876+ skills) uses Lucene-style search but has a critical quirk:

```bash
# WRONG: Single-word queries often return empty
hermes skills search "writing"      # → No skills found
hermes skills search "obsidian"     # → Works only because exact match
hermes skills search "emotion"      # → Likely empty

# RIGHT: Multi-word / phrase queries
hermes skills search "creative writing"           # → 12 results
hermes skills search "fiction writing story"      # → May need broader terms
hermes skills search "humanize AI prose"          # → Varies by actual skill titles
hermes skills search "prose style voice edit"     # → Hit or miss
```

**Rule:** Always try multi-word phrases. If that fails, try broader single category terms like `"creative"` or `"writing"` then paginate through results manually with `browse`.

### Step 2: Inspect Before Installing

```bash
hermes skills browse                          # list all, page through
hermes skills inspect "<skill name>"          # preview SKILL.md body
hermes skills install "<identifier>"          # actually install
```

**Critical:** Never install based on description alone. Many descriptions are thin marketing copy. Always read the full SKILL.md preview first.

### Step 3: External Verification Sources

| What to Verify | Where | How |
|----------------|-------|-----|
| GitHub quality | github.com | Stars, last commit, issues, README completeness, actual code vs docs-only repos |
| Community reception | reddit.com/r/ClaudeAI, dev.to, LinkedIn | Search for discussions about the specific skill |
| Skill marketplace listings | skillsllm.com, mcpmarket.com | Cross-reference with hub listing, see if others have installed it |
| Author other work | GitHub profile | Check if they maintain other skills/quality across their repo |

### Step 4: Category Scoring Criteria

When evaluating skills for a fiction project, score each against:

| Criterion | Weight | Questions |
|-----------|--------|-----------|
| **Relevance to craft** | 30% | Does it address narrative, prose, or structure directly? |
| **Series-readiness** | 25% | Can it handle multiple books/volumes, not just one-off? |
| **Practical usability** | 20% | Will an agent actually use this, or is it aspirational? |
| **Maintenance status** | 15% | Is the repo actively maintained? Last commit date? |
| **Integration cost** | 10% | How much setup does it need? API keys? Running servers? |

### Verified External Skill Repos

#### Humanization (Remove AI patterns)

1. **blader/humanizer** — https://github.com/blader/humanizer
   - ⭐ ~30k stars (highly popular)
   - Removes 33 AI writing patterns
   - Based on Wikipedia's "Signs of AI Writing" research
   - Includes voice calibration from user samples
   - **Install:** Look up identifier in hub; may be `skills-sh` indexed

2. **conorbronsdon/avoid-ai-writing** — https://github.com/conorbronsdon/avoid-ai-writing
   - ⭐ ~2.5k stars
   - Audit + rewrite modes (detect-only OR edit-in-place)
   - Supports voice profiles
   - **Install:** Via hub identifier

#### Architecture & Structure

3. **danjdewhurst/story-skills** — https://github.com/danjdewhurst/story-skills
   - Story bible, character files, worldbuilding notes, factions, artifacts
   - Plot arcs, scene state tracking, glossary, worldbuilding folders
   - Built for multi-chapter/saga projects
   - **Install:** Via hub identifier

4. **haowjy/creative-writing-skills** — https://github.com/haowjy/creative-writing-skills
   - Three sub-skills bundled in one repo
   - Story Architecture (4 levels), Prose Quality, Character Depth
   - Well-documented, actively maintained
   - **Install:** Via hub identifier

5. **modoojunko/awesome-novel-skill** — https://github.com/modoojunko/awesome-novel-skill
   - Chinese-developed, English README available
   - Worldbuilding → character → chapter planning → full-text generation
   - Fantasy/wuxia genre templates included
   - Less polished but domain-relevant
   - **Install:** Via hub identifier

#### Craft & Diagnosis

6. **the-storytellers-workbench** — Available in Hermes hub via `clawhub`
   - Craft-level literary fiction skill (~300 lines of principles)
   - Diagnoses flat scenes, voice drift, pacing, character interiority
   - Core principles: Tension engine, Voice contract, Humor precision
   - **Install:** `hermes skills install the-storytellers-workbench`

7. **writing-claw** — Available in Hermes hub via `clawhub`
   - Narrative OS with hierarchy (Moment→Interaction→Scene→Sequence→Chapter→Story→Story Cluster)
   - Character registry with state fields
   - Gap-based tension theory
   - **Install:** `hermes skills install writing-claw`

#### Obsidian Vault

8. **Base obsidian skill** — Multiple variants in hub
   - Clawhub: generic vault management
   - `obsidian-literature-workflow` — lit-specific templates
   - `obsidian-bases` — template/base management
   - For novel-specific needs, build custom wrapping these foundations

### Installation Commands Reference

Once you identify the right skill from an audit:

```bash
# From Hermes hub (preferred)
hermes skills install <identifier>

# From GitHub directly (if not in hub)
npx skills add <owner>/<repo> --agent hermes

# Verify installation
hermes skills list | grep <name>

# Preview after install
hermes skills inspect <name>
```

### Notes on Language and Localization

- Some high-quality skills are authored in non-English languages (especially Chinese)
- They often include English READMEs but the actual skill/templates may be in the author's language
- Always verify content language before installing for an English-language project
- Translation-ready skills are preferable when the template language doesn't match your project

### Pitfalls Documented During This Audit

1. **Single-word search returns empty** — The most common mistake. The hub search uses exact/near-exact matching for single words.
2. **Description inflation** — Several skills had compelling descriptions but sparse SKILL.md bodies. Always inspect before installing.
3. **Stale repos masquerading as useful** — Checked GitHub timestamps; some popular repos hadn't been updated in 12+ months.
4. **Chinese repo ambiguity** — `awesome-novel-skill` by modoojunko had English docs but unclear whether the actual skill content was translatable.
5. **Pordl Creative Writer is an API routing skill** — Not a craft skill; it routes requests through PORDL's creative-mode API. Only relevant if you want to use PORDL as a backend model provider.
6. **Creative Writing Workshop for AI agents** — This is a web-server workshop tool requiring a running server. NOT what we needed.
