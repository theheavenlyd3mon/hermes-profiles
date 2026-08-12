---
name: t3mp3st
description: "Operate, explain, review, and deploy T3MP3ST-class offensive-security meta-harnesses: multi-agent red-team automation with a local-agent brain, arsenal wrappers, scope gating, War Room UI, and reproducibility checks. Use when the task involves T3MP3ST setup, architecture review, agent-loop wiring, scope enforcement, benchmark verification, or beginner-friendly red-team explanations."
---

# T3MP3ST-Class Offensive-Security Meta-Harnesses

Class-level guidance for working with T3MP3ST-style frameworks that turn an existing local AI coding agent into an autonomous red-team platform.

## Core mental model

T3MP3ST is NOT a scanner or exploit framework itself. It is a **meta-harness**:
- **Brain**: an existing local agent CLI such as Claude Code, Codex, or Hermes.
- **Body**: the Arsenal/tool wrappers the brain can call.
- **Rules**: mission target/scope, rules of engagement, and evidence vault.
- **Room**: War Room UI or HTTP API for mission control.
- **Receipts**: `verify-claims` re-derives headline numbers from committed artifacts.

## Beginner explanation pattern

When the user is unfamiliar with red teaming:
1. Start with one analogy: either **home security inspection** or **autopilot inspection car**.
2. Name the actual components in plain terms: brain, tool belt, allowed zone, report.
3. Keep operator tables to the proven fraction. Emphasize that later operators are experimental unless asked otherwise.
4. End with two caveats: authorization only, and it is an assistant not a teacher.

## Hermes integration

Hermes is a first-class local brain. From `src/agent/local-agents.ts`:
- `bin: hermes`
- invocation: `hermes -z "<prompt>"`
- optional unattended mode: `--yolo` only when `T3MP3ST_HERMES_YOLO=1`
- default is safe mode and preserves normal approval behavior
- no second API key is required; Hermes uses its existing auth/config

Modes to explain:
- **Keyless**: connect Hermes in Settings; T3MP3ST drives it headlessly
- **Local model**: Ollama/LM Studio/vLLM via `TEMPEST_LOCAL_BASE_URL`
- **API key**: OpenRouter/Anthropic/OpenAI/Venice/XAI

When asked how Hermes pilots it:
- explain subprocess invocation
- one-shot prompt round-trip
- T3MP3ST interprets text/tool plans
- Hermes remains the brain; T3MP3ST is the harness

## Stable vs experimental status

Default correctness is tied to the repo's own status model. Use these labels unless the user asks otherwise:
- ✅ Stable: recon, mission engine, arsenal/MCP/HTTP, scope gating, coordinator/reporting pieces
- ⚠️ Experimental/🚧: later operators, advanced modules when unproven

Important honesty points always worth stating:
- headline scores came from a single-agent ReAct loop, not the 8-operator swarm
- Recon/Scanner/Reporting are most trustworthy today
- Exploiter/Infiltrator/Exfiltrator/Ghost/Coordinator are real tool-backed loops but unbenchmarked as coordinated swarm

## Source review workflow

When the user wants a structural review:
1. Clone repo
2. Read README/FEATURES/TEAM_PREVIEW for product claims
3. Read `src/agent/local-agents.ts` for supported local agents and safety switches
4. Read `src/server.ts` and `src/llm/index.ts` for adapter routing
5. Read `docs/INSTALL_MATRIX.md` and `docs/ARSENAL_ACTIVATION_PLAN.md` for dependency reality
6. Report only what is actually coded; match README claims to code evidence
7. Run `npm run verify-claims` on a fresh clone — the definitive integrity check (see below)

## Verifying the headline numbers (tested 2026-08)

The repo re-derives every README number from committed artifacts. This is the single best way to tell real claims from branding:

```bash
git clone --depth 1 https://github.com/elder-plinius/T3MP3ST /tmp/t3mp3st
cd /tmp/t3mp3st && npm install --no-audit --no-fund && npm run verify-claims
```

- Requires node >= 22.19 (package.json `engines`); install + run ≈ 2-5 min
- Healthy result: exit 0, `ALL CLAIMS VERIFIED — 27 passed, 0 failed`
- Output confirms tool counts (109 = 73 adapters + 36 built-in), 8 operators,
  CVE-Zero held-out 10/10 found + 8/10 exact file/line/CWE, Cybench 15-iter,
  and the integrity gate (0 phantom / 606 scored solves)
- If verify-claims fails or output is redacted, treat headline numbers as unverified

## Pitfalls to avoid

- Do not claim the swarm is proven; the repo explicitly says it is not.
- Do not present benchmark numbers without the caveats about single-agent source.
- Do not suggest `T3MP3ST_HERMES_YOLO=1` as a default; it disables approval prompts.
- Do not skip the authorization reminder when explaining use cases.
- Do not rely on overfitting claims; note the anti-fitting/verify-claims intent.

## Reference lookup

For session-specific technical evidence: `references/t3mp3st-source-notes.md`
For quick architecture explanation: `references/t3mp3st-beginner-aids.md`
