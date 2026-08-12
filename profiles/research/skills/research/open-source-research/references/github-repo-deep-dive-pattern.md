# GitHub Repo Deep-Dive Pattern

## When to Use
Evaluating open-source projects for integration into the Hermes fleet or skill library. Works for any domain — finance, ML, automation, etc.

## Workflow

### Phase 1: Discovery (parallel)
```
web_search(query="GitHub AI agent <domain>", count=10)
web_search(query="site:github.com <specific terms>", count=10)
```
- `web_search_plus` does NOT support `provider: 'github'` — use regular `web_search` with Brave/Serper backend
- Collect 8-12 candidate repos, deduplicate by URL
- Star count, recency (check for 2026 updates), and license are primary filters

### Phase 2: Extraction (parallel, max 5 URLs per call)
```
web_extract(urls=[repo1_readme, repo2_readme, ...])
```
- README extraction gives architecture, install steps, feature list
- For deeper dives, extract specific files: `docs/README_AGENT.md`, `skills/*/SKILL.md`, `default_config.py`
- Use raw.githubusercontent.com for files that web_extract can't reach through GitHub UI

### Phase 3: Evaluation Framework
Score each repo on these axes:

| Axis | What to Check |
|------|--------------|
| **Architecture fit** | Does the decomposition match fleet patterns? (specialist agents, handoff chains) |
| **Integration cost** | API-only (low) vs clone+setup (medium) vs full pipeline (high) |
| **Provider support** | Does it support the fleet's existing LLM providers? (Nous, DeepSeek, Qwen) |
| **Data dependencies** | Free APIs vs paid keys vs proprietary data |
| **Maintenance signal** | Recent commits, active issues, version releases in 2026 |
| **License** | Apache-2.0 and MIT are safe. Check for AGPL/SSPL |

### Phase 4: Synthesis
Present results in tiers:
- **Tier 1:** Purpose-built, high architecture fit, ready to integrate
- **Tier 2:** Useful components or APIs, partial fit
- **Tier 3:** Reference/catalog, not directly integrable

Always include: repo URL, stars, license, one-line description, and integration cost estimate.

## Pitfalls
- **Don't trust star counts alone.** Some high-star repos are abandoned or have breaking API changes. Check latest release date and commit activity.
- **web_extract truncates large READMEs.** For repos with extensive docs, extract the specific files you need (config examples, API docs) rather than the full README.
- **Docker-first repos are easier to evaluate.** If a repo has docker-compose.yml, the integration path is clearer than "conda create" workflows.
- **Check for agent-native integration patterns.** Some repos (like AI-Trader) have SKILL.md files designed for agent consumption — these are gold for Hermes integration.
