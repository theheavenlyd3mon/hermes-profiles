# Knowledge Architecture for Multi-Agent Setups

Derived from: session 20260513_120000 — user asked about profile-to-knowledge-store flow and setting proactive conventions.

## Problem

Hermes profiles each have their own skills (procedural memory), Mnemosyne memory (preferences/facts), and a sandboxed home directory. But they share a filesystem and a user. Knowledge written by one profile should be findable by another — otherwise agents rediscover what past agents already learned.

## Solution: Shared wiki + per-profile scratch folders

One Team-Wiki at a canonical absolute path. All profiles write to it. Durable knowledge goes to the shared folders (entities/, concepts/, comparisons/, queries/). Work-in-progress and agent-specific notes go to profiles/<name>/.

### Why not separate wikis/vaults per profile

- Cross-pollination vanishes — the graph never learns connections between domains
- User has to switch contexts to find anything
- Duplicate effort — both researcher and coder might write about the same concept
- Agent improvement already happens through per-profile skills and memory; the wiki is the shared semantic layer

## Convention for new profiles

When spinning up a new profile (e.g. researcher, coder), create its scratch folder at setup time:

```
mkdir -p /path/to/Team-Wiki/profiles/<name>/
```

Then embed the path in the profile's SOUL.md or Mnemosyne memory so the agent never asks "where should I put this." This is a proactive convention — do it before the profile's first session, not after.

## Tagging for provenance

Pages in shared folders should be tagged with `agent:<profile-name>` so graph queries can distinguish "researcher wrote about RAG" from "coder wrote about RAG." This enables both cross-pollination (same topic, different angles) and attribution (who has the authority on this topic).
