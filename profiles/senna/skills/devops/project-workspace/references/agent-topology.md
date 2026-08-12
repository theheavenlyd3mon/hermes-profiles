# Agent Topology & Inter-Profile Communication

## The Profile Fleet

The user has 11 Hermes profiles that map 1:1 to the ROUTE_MAP in Senna's SOUL.md:

```
senna         — Default, routing, meta-agent
architect     — System design
coder         — Implementation
data-analyst  — Data science
debugger      — Bug isolation
devops        — Infrastructure
foreman       — Mission orchestration (autonomous cron-driven)
researcher    — Investigation (has Browserbase, own cron jobs)
reviewer      — Quality gate
secretary     — Knowledge keeper
security      — Security audit
```

Each profile has its own SOUL.md, skill set, config, sessions, and Mnemosyne database.

## Current Communication Model

Profiles communicate via **delegate_task** (spawns a disposable child agent within the calling profile). Characteristics:

1. Child agents are **ephemeral** — each call starts fresh with no continuity
2. The caller **blocks** until the child finishes
3. Child agents **inherit** the parent's context and authority (no security boundary)
4. No persistent conversation threads between profiles
5. `foreman` orchestrates via kanban board (asynchronous, not direct peer-to-peer)

This works for linear pipelines but doesn't support:
- Push notifications between profiles ("researcher found something → notify senna")
- Persistent conversations ("coder asks reviewer a question, reviewer responds later")
- Security boundaries between profiles

## A2A Protocol Option

The [hermes-a2a-preview](https://github.com/iamagenius00/hermes-a2a-preview) plugin implements Google's A2A protocol (donated to the Linux Foundation). It converts profiles into peer-to-peer A2A nodes.

### How it works (single-profile)

- Install to `~/.hermes/plugins/a2a/`
- Starts an HTTP server (default port 8081) inside the Hermes process
- Each agent becomes a node with an Agent Card at `/.well-known/agent.json`
- Per-friend trust: each remote agent gets its own token, rate limit, trust level
- SSRF protection (DNS pinning, redirect blocking), outbound redaction, provenance tracking
- Persistent conversations stored on disk at `~/.hermes/a2a_conversations/`

### The single-profile constraint

The plugin was designed for one Hermes process. Key constraints:

| Constraint | Why | Workaround |
|---|---|---|
| One HTTP server per process | Plugin starts `ThreadingHTTPServer` on a fixed port | Run each profile as its own gateway process with unique `A2A_PORT` |
| Global env vars | `A2A_ENABLED`, `A2A_PORT`, `A2A_WEBHOOK_SECRET` from `~/.hermes/.env` | Override per gateway invocation |
| Global config | `a2a.agents` list from `~/.hermes/config.yaml` | Use per-profile `config.yaml` sections |
| Both ends must be online | Synchronous 120s timeout with HMAC webhook for wake | Profiles run as persistent gateways |

### Multi-gateway approach (for all 11 profiles)

```bash
# Each profile runs as its own long-lived gateway on a unique port
A2A_PORT=8081 hermes gateway start                                   # senna
A2A_PORT=8082 A2A_ENABLED=true hermes -p researcher gateway start     # researcher
A2A_PORT=8083 A2A_ENABLED=true hermes -p coder gateway start          # coder
...
```

Each profile's `config.yaml` (or per-profile config section) lists the others:

```yaml
a2a:
  agents:
    - name: "senna"
      url: "http://127.0.0.1:8081"
      auth_token: "<token-from-senna>"
    - name: "researcher"
      url: "http://127.0.0.1:8082"
      auth_token: "<token-from-researcher>"
```

### What A2A enables that delegate_task cannot

| Capability | delegate_task | A2A |
|---|---|---|
| Persistent conversation | ❌ Each call is a fresh disposable | ✅ Conversations persisted to disk |
| Push notifications | ❌ Caller must poll or block | ✅ HMAC webhook wakes target profile |
| Security boundary | ❌ Child inherits parent's authority | ✅ Per-friend tokens, rate limits, trust levels |
| Provenance tracking | ❌ No chain-of-request tracking | ✅ Provenance digests, taint markers |
| Stranger handling | ❌ Not applicable | ✅ Stranger capture + review queue |

### Current gaps (M2 preview)

- No streaming/SSE for real-time responses
- No dashboard UI for managing the friend graph
- No relay/mailbox fallback for offline agents
- Per-profile setup must be done manually (no unified installer)

## Future pattern: hybrid

For the user's setup, the pragmatic architecture is:
- **Senna** runs as a persistent A2A gateway (the hub)
- **Researcher** runs as a persistent A2A gateway (headless, cron-based)
- Other profiles run on-demand via CLI/TUI (no A2A server)
- When Senna needs to talk to a non-gateway profile, fall back to `delegate_task`
- Profiles that run as gateways also benefit from the A2A security layer (per-friend tokens, audit)

This avoids running all 11 instances simultaneously while still getting peer-to-peer benefits where it matters most.
