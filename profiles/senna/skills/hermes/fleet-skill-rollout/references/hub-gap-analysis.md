# Hub catalog gap analysis — 2026-08-03 results

Fleet: 23 profiles, 1,729 SKILL.md files, 1,123 unique skill names (frontmatter).
Hub curated set: the 111 Nous first-party "official optional" skills
(`--source official` == `--source well-known`; docs count bar "Optional 111").

## Method
1. Extract fleet frontmatter names (see Step 0b in SKILL.md).
2. `hermes skills browse --source official --size 200`, awk name column ($3),
   strip `…`, lowercase.
3. Prefix-match hub names (renderer truncates ~13 chars) against fleet names.
4. Group the missing set by theme; tier per profile (A/B/skip).

## Results — already installed somewhere in fleet (13/111, no action)
agentmail, axolotl, baoyu-comic, chroma, dspy, faiss, godmode, heartmula,
hyperframes, obliteratus, outlines, pixel-art, stocks

## Results — NOT installed anywhere (86), grouped

Finance/trading: 3-statement-model, comps-analysis, dcf-model, lbo-model,
merger-model, hyperliquid, evm, solana, shopify, shop, stripe-link-cli,
stripe-projects, excel-author, pptx-author, qmd

MLOps/training/inference: audiocraft-audio-generation, bioinformatics, clip,
distributed-llm-pretraining, fine-tuning-with-trl, guidance,
huggingface-accelerate, huggingface-tokenizers, inference-sh-cli, instructor,
jupyter-notebook, lambda-labs-gpu-cloud, llava, modal-serverless-gpu,
nemo-curator, optimizing-attention, peft-fine-tuning, pinecone,
pinecone-research, pytorch-fsdp, pytorch-lightning, qdrant-vector-search,
segment-anything-model, simpo-training, slime-rl-training,
sparse-autoencoder-training, stable-diffusion-image-generation, darwinian-evolver

Creative/visual: baoyu-article-illustrator, blender-mcp, concept-diagrams,
creative-ideation, meme-generation, kanban-video-orchestrator

Autonomous agents/infra: antigravity-cli, blackbox, cloudflare-temporary-deploy,
docker-management, gitnexus-explorer, mpp-agent, openclaw-migration, openhands,
page-agent, parallel-cli, pinggy-tunnel, hermes-s6-container-setup

Research/OSINT/security: adversarial-ux-test, domain-intel, drug-discovery,
duckduckgo-search, osint-investigation, oss-forensics, sherlock, searxng-search,
scrapling, rest-graphql-debug, mcp-oauth-remote-gateway, fastmcp, mcporter

Productivity/misc: 1password, canvas, code-wiki, fitness-nutrition, here.now,
honcho, memento-flashcards, neuroskill-bci, one-three-one-rule, pokemon-player,
siyuan

## Priority reads for this user
- Finance (Oracle-adjacent): hyperliquid, evm, solana
- ML stack: peft-fine-tuning, pytorch-fsdp, distributed-llm-pretraining,
  pinecone, qdrant-vector-search, inference-sh-cli
- Creative: stable-diffusion-image-generation, baoyu-article-illustrator
- Cyber: sherlock, osint-investigation

Deep-dive evaluations of kanban-video-orchestrator, stable-diffusion-image-generation,
neuroskill-bci, one-three-one-rule live in hermes-skills-hub
references/docs-skills-page.md.
