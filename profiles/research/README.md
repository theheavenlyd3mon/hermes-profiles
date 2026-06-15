# Research — Domain Orchestrator: Investigation

The investigator. Searches primary sources, evaluates evidence, synthesizes findings. Claim without citation is opinion.

## When to Use

- Deep research on any topic
- Literature review and paper analysis
- Data gathering and analysis
- Competitive intelligence
- Market reconnaissance

## How It Works

```
Question → Breadth scan (3-5 searches) → Depth on leads → Gap filling → Synthesize → File knowledge
```

Every claim gets a confidence level (H/M/L). Contradictions are flagged, not hidden. Synthesis over summarization.

## Skills (13 total)

Key skills:
- **arxiv** — Academic paper search, BibTeX, citation graphs
- **llm-wiki** — Karpathy-style persistent knowledge base
- **blogwatcher** — RSS/Atom feed monitoring
- **open-source-research** — Systematic OSS evaluation
- **research-pipeline** — Multi-phase research with agents
- **polymarket** — Prediction market queries
- **jupyter-live-kernel** — Interactive Python/data exploration
- **safe-web-research** — Scraping with neutralization of prompt injection
- Plus 5 more (data scientist, epub, etc.)

## Personality

Analytical, thorough, evidence-based. Structured and cited. Confidence-calibrated.

## Configuration

```yaml
model: deepseek/deepseek-chat  # cost-effective for long sessions
max_turns: 60
reasoning_effort: high
gateway:
  timeout: 1200  # research takes time
terminal:
  timeout: 300
```

## Detailed Setup Guide

See [guides/research-profile-guide.md](../../guides/research-profile-guide.md) for a full walkthrough including knowledge vault setup.

## SOUL.md

See [SOUL.md](SOUL.md) for the full agent definition.
