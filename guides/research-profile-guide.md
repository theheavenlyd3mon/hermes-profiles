# Setting Up a Research Agent in Hermes

> A guide for creating a dedicated research profile — an AI investigator that gathers intelligence, synthesizes findings, and builds a persistent knowledge base across sessions.

---

## What This Gets You

A Hermes profile specialized in research that:
- Searches primary sources (not blog summaries)
- Rates every claim with a confidence level
- Synthesizes findings for your specific situation (not generic dumps)
- Files durable knowledge in a browsable knowledge base
- Builds on past research — never rediscovers the same thing twice

---

## How It Works

```
You ask a question
    → Researcher searches primary sources
    → Evaluates reliability, flags contradictions
    → Synthesizes findings for your context
    → Files knowledge in the vault
    → Next session builds on what it already knows
```

The researcher is not a chatbot that googles things. It's a specialist that follows a methodology.

---

## Step 1: Create the Profile

```bash
hermes profile create researcher
```

This creates `~/.hermes/profiles/researcher/` with its own config, memory, and skills.

---

## Step 2: Configure the Profile

Edit `~/.hermes/profiles/researcher/config.yaml`:

```yaml
# Model choice — research needs long sessions
model: deepseek/deepseek-chat    # or anthropic/claude-sonnet-4, openai/gpt-4o, etc.

# Research needs room to breathe
max_turns: 60
gateway:
  timeout: 1200    # 20 minutes — research takes time

reasoning_effort: high

# Terminal for web searches, file operations
terminal:
  timeout: 300
  persistent_shell: true

# Memory — keep facts across sessions
memory:
  enabled: true
  char_limit: 2200
  flush_min_turns: 6
```

> **Model choice:** Use whatever you have access to. DeepSeek is cost-effective for long sessions. Claude and GPT-4o work great too. The methodology matters more than the model.

---

## Step 3: Write the SOUL.md

This is the researcher's identity file — it defines how the agent thinks and works.

Create `~/.hermes/profiles/researcher/SOUL.md`:

```markdown
# Research Agent

IDENTITY: Curious.Rigorous.Synthesizing. You are a research specialist.

## Core Principles

1. **Source-first, not blog-first.** Go to primary sources:
   - HuggingFace model cards and community uploads
   - GitHub repos, arXiv papers, official documentation
   - Community spaces (Discords, forums, leaderboards)
   - Blog posts are downstream — by the time a blog exists, the info is stale

2. **Every claim gets a confidence level.**
   - **High** — verified across 2+ independent sources
   - **Medium** — single reliable source or consistent pattern
   - **Low** — inference, rumor, or unverified claim

3. **Contradictions are flagged, not hidden.** If Source A says X and Source B says Y, cite both with the discrepancy noted. Never silently pick one.

4. **Synthesis over summarization.** Connect findings to the user's specific context. A comparison table means nothing without "and here's what this means for you."

5. **No raw dumps.** Organize, prioritize, and explain. If you found 20 results, report the 5 that matter and why.

## Research Methodology

### Multi-Round Search
1. **Breadth scan** — 3-5 searches across different angles
2. **Depth on promising leads** — drill into the top candidates
3. **Gap filling** — targeted searches for missing information
4. **Stopping criterion** — when >80% of results are already-seen, stop

### Output Format
Always structure findings as:

## Research Question
The original ask, restated precisely.

## Key Findings
Organized by subtopic. Each finding includes:
- The claim
- Confidence level (H/M/L)
- Source with provenance

## Contradictions
Any disagreements between sources, explicitly noted.

## Gaps
What you couldn't find or verify.

## Recommendation
What this means for the user's specific situation.

## Handoff Protocol
When returning findings to another agent or the user:
- SynthesizedFindings{Confidence, Sources, Contradictions, Gaps}
- File durable knowledge in the vault
- Flag anything that needs follow-up

## Quality Gate (check before reporting)
- [ ] Sources cited?
- [ ] Claims confidence-rated?
- [ ] Contradictions flagged (not hidden)?
- [ ] Synthesized (not just summarized)?
- [ ] Knowledge filed in vault?
```

---

## Step 4: Install Research Skills

Skills give the researcher specific tools and methodologies. Install the ones that match your research needs:

### Essential Skills

**`arxiv`** — Search academic papers
```bash
hermes skill install arxiv --profile researcher
```
Gives you: arXiv API search, BibTeX generation, citation graphs, author profiles.

**`llm-wiki`** — Persistent knowledge base
```bash
hermes skill install llm-wiki --profile researcher
```
Gives you: Karpathy-style wiki pattern with ingest, lint, query, and self-review operations. This is how research becomes durable knowledge.

**`research-paper-writing`** — Full paper pipeline
```bash
hermes skill install research-paper-writing --profile researcher
```
Gives you: 8-phase ML paper pipeline (literature review → experiments → drafting → submission). Useful even if you're not publishing — the methodology is rigorous.

### Optional Skills (based on your needs)

| Skill | Use When |
|-------|----------|
| `polymarket` | Researching prediction markets, forecasting |
| `local-llm-research` | Comparing local LLM models for specific hardware |
| `jupyter-live-kernel` | Interactive data exploration and analysis |

---

## Step 5: Connect to a Knowledge Vault

The researcher needs somewhere to file findings. Set up an Obsidian vault (see the [Obsidian Setup Guide](../hermes-obsidian-setup-guide.md)) and point the researcher at it.

In `~/.hermes/profiles/researcher/.env`:

```bash
OBSIDIAN_VAULT_PATH=~/Hermes Vault
FABRIC_DIR=~/Hermes Vault/knowledge
WIKI_PATH=~/Hermes Vault/knowledge
```

Then in SOUL.md, add:

```markdown
## Knowledge Filing
- Durable findings → wiki page in the vault
- Quick notes → notes/ directory
- Use [[wikilinks]] to cross-reference
- Follow the vault's SCHEMA.md for frontmatter
```

---

## Step 6: First Research Task

Test the setup with a real question:

```
Research [your topic of interest]. 
Search primary sources (official docs, GitHub, arXiv, community spaces).
Rate your confidence on each finding.
Synthesize for my specific context: [your situation].
File durable knowledge in the vault.
```

Check after:
- ✅ Agent searched primary sources (not just blog posts)
- ✅ Findings have confidence ratings (H/M/L)
- ✅ Contradictions are flagged, not hidden
- ✅ Output is synthesized for your context
- ✅ Knowledge was filed in the vault
- ✅ Wikilinks connect to existing pages

---

## The Methodology in Practice

### Example: Researching a Tool

**Bad approach (what chatbots do):**
> "Here are the top 10 tools for X according to [blog site]..."

**Good approach (what the researcher does):**
> "I searched GitHub stars, recent commits, open issues, and community discussions. Tool A has 15K stars but 300 open issues and the last commit was 2 months ago. Tool B has 5K stars but active development (commits this week) and a responsive maintainer. For your use case [specific context], Tool B is the better choice because [reasoning]. Confidence: Medium (based on GitHub metrics + 2 community threads). Contradiction: One blog post recommends Tool A but was written before the maintainer went inactive."

### Example: Researching a Topic

**Breadth scan:**
```
Search 1: [topic] best practices 2026
Search 2: [topic] arxiv papers
Search 3: [topic] github implementations
Search 4: [topic] community discussion reddit
Search 5: [topic] official documentation
```

**Depth on top candidates:**
```
→ Drill into the 2-3 most promising results
→ Read source code, not just descriptions
→ Check recent activity, not just star count
```

**Gap filling:**
```
→ What's missing from the picture?
→ What did the breadth scan miss?
→ Targeted searches for specific gaps
```

**Stop when:** The third search returns the same results as the first two.

---

## Optional: Multi-Agent Integration

If you're running multiple Hermes profiles, the researcher can work as part of a team. For onboarding new users or teaching existing operators, the **educate** profile can generate lessons, assessments, and workshop materials from these guides:

| Role | Does What |
|------|-----------|
| **Orchestrator** | Routes research questions to the researcher |
| **Researcher** | Investigates, synthesizes, files knowledge |
| **Analyst** | Processes data the researcher gathered |
| **Writer** | Turns research into polished output |
| **Educate** | Turns findings into lessons, quizzes, and onboarding docs |

The researcher returns findings; other agents act on them. This separation keeps the researcher focused on investigation, not implementation. Use `educate` to convert research output into repeatable teaching material.

To set this up, see the Hermes docs on [multi-profile workflows](https://hermes-agent.nousresearch.com/docs).

---

## Customization Ideas

### For Technical Research
- Add `systematic-debugging` skill for investigating bugs
- Add `codebase-inspection` skill for understanding codebases
- Configure terminal with project-specific environment

### For Market/Financial Research
- Add `polymarket` skill for prediction markets
- Add custom web search sources
- Set up structured output templates for trade ideas

### For Academic Research
- Add `research-paper-writing` skill
- Add `arxiv` skill with BibTeX export
- Configure citation management

### For Competitive Intelligence
- Add `github` skill for repo monitoring
- Set up cron jobs for periodic monitoring
- Create templates for competitor analysis

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Agent uses blog posts instead of primary sources | Reinforce source-first in SOUL.md; add specific source instructions |
| No confidence ratings on findings | Add the quality gate checklist to SOUL.md; remind the agent |
| Research is too generic | Add context about your specific situation to the prompt |
| Agent doesn't file knowledge | Check vault paths in .env; verify WIKI_PATH is set |
| Agent re-researches the same topics | Check that vault is connected; search fabric_recall before researching |
| Sessions are too short to finish | Increase max_turns and gateway timeout in config.yaml |
| Model isn't smart enough for synthesis | Try a stronger model (Claude, GPT-4o) for the researcher profile |

---

## Quick Reference

### Config Values That Matter

| Setting | Recommended | Why |
|---------|-------------|-----|
| `max_turns` | 60+ | Research needs multi-round search |
| `gateway.timeout` | 1200+ | Long sessions for deep dives |
| `reasoning_effort` | high | Synthesis requires thinking |
| `memory.enabled` | true | Remember past research |
| `terminal.timeout` | 300 | Some searches take time |

### SOUL.md Checklist

- [ ] Source-first methodology defined
- [ ] Confidence rating system (H/M/L)
- [ ] Contradiction handling (flag, don't hide)
- [ ] Synthesis requirement (not just summary)
- [ ] Output format template
- [ ] Quality gate checklist
- [ ] Knowledge filing instructions

### Skills to Install

| Priority | Skill | Purpose |
|----------|-------|---------|
| Essential | `arxiv` | Academic paper search |
| Essential | `llm-wiki` | Persistent knowledge base |
| Recommended | `research-paper-writing` | Rigorous methodology |
| Optional | Domain-specific | Match your research needs |
 
