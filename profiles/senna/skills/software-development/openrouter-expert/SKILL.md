---
name: openrouter-expert
description: Use this skill when building with OpenRouter — the unified API for 300+ AI models. Covers SDK selection (@openrouter/sdk, @openrouter/agent, OpenAI SDK, framework adapters), model discovery and routing (Auto Router, variants, fallbacks), multimodal inputs, tool calling, structured outputs, embeddings, RAG, observability, and admin features. Always verify current docs and live model IDs before implementing. Skill triggers on intent to build AI features, even if OpenRouter isn't explicitly named.
version: 1.0.0
author: Senna
license: MIT
metadata:
  hermes:
    tags: [openrouter, ai-integration, sdk, api-integration, model-routing, multimodal, tool-calling]
    related_skills: [autonomous-ai-agents, software-development, mcp]
---

IDENTITY: ProviderResolver{OpenRouter,LiveVerificationFirst,ResolverNotReplicator}. CoreRole: Route users to correct OpenRouter docs pages and verify claims via live API. BehavioralContract: Read llms.txt index before claiming any doc exists. Verify model IDs via /api/v1/models. Never replicate docs — link to them. Never hardcode pricing/capabilities.
Law: Every docs URL must appear in llms.txt. Every model claim must be verified against live API. Do not construct variant IDs manually.
WHENUSE: OpenRouter API integration, model routing/selection, SDK choice, multimodal inputs, tool calling, embeddings, RAG, observability. ESPECIALLY:{ModelSelection,SdkChoice,FeatureIntegration}. NoSkip:{DocsIndexRead,LiveModelVerification}.
REDFLAGS: HardcodedModelIDs->LiveLookup|ConstructedVariants->CheckVariantsArray|PricingFromMemory->LivePricing|UntraceableURL->DontLink|AgentSDKForSimpleCall->UseSDKorREST|ServerToolsVsPluginsConfusing->DifferentMechanisms.
RATIONALIZATIONS: "I remember the URL"->CheckIndexAnyway|"This model definitely exists"->FetchLive|"Variants work the same"->ReadVariantDocs|"One docs page is enough"->CrossCheck.
QUICKREF: Ritual{read llms.txt->verify URL->fetch models}->Route{task->canonical docs page from table}->SDK{simple=@openrouter/sdk,agentic=@openrouter/agent,framework=adapter}->Verify{checklist: docs,models,URLs,SDK,claims,features}.

# OpenRouter Expert

Agent resolver skill for building correctly with OpenRouter — the unified API gateway to 300+ AI models across OpenAI, Anthropic, Google, Meta, and dozens of other providers.

This skill enforces a canonical workflow: read the live docs index first, verify claims against current API/docs, and use live model discovery when model IDs matter.

---

## A. When to load this skill

**Trigger immediately when:**
- User says "OpenRouter" or references openrouter.ai
- User wants to integrate AI models via a unified API across providers
- User asks about model selection, routing, fallbacks, or cost/latency optimization
- User asks about SDKs: `@openrouter/sdk` (TypeScript), `openrouter` (Python), `@openrouter/agent`, OpenAI SDK on OpenRouter, or any framework adapter (Vercel AI SDK, LangChain, PydanticAI, LiveKit, Anthropic Agent SDK, Mastra, TanStack AI, etc.)
- User wants to build: chatbots, agents with tools, RAG/search, embeddings, multimodal inputs (images, PDFs, audio, video), image/video generation, TTS, structured outputs, coding agents
- User asks about OpenRouter features: workspaces, guardrails, prompt caching, OAuth/PKCE, BYOK, usage tracking, observability (Broadcast/Langfuse/Datadog/etc.), zero data retention (ZDR), service tiers, response healing, message transforms

**Implied intent (even if OpenRouter not named):**
- "unified API for multiple LLMs"
- "switch between Claude and GPT without changing code"
- "cost-optimized model routing"
- "free tier for LLMs"
- "web search built into any model"
- "auto fallback when provider is down"

**Do NOT load for:**
- Generic AI advice with no API integration question
- Questions about AI providers' native APIs without mentioning a gateway/unified layer

---

## B. Pre-answer ritual — mandatory before any OpenRouter claim

Every time you answer an OpenRouter question, follow this exact sequence before responding:

1. **Read the docs index** — fetch `https://openrouter.ai/docs/llms.txt` to know what pages exist. If you're unsure whether a feature exists, the index is the source of truth.

2. **Read full page content only when necessary** — use `https://openrouter.ai/docs/llms-full.txt` appended with the page slug (e.g., `https://openrouter.ai/docs/guides/overview/models.mdx`) to get clean markdown for detailed questions. Do not rely on memory for detailed behaviors.

3. **Verify URL existence** — every docs URL you reference must appear in `llms.txt`. If a URL is not in the index, do NOT link to it. Say "I can't find the official docs page for that; please check the OpenRouter docs directly."

4. **Verify model IDs and capabilities via API** — when the task requires specific model IDs, variants, or capability information:
   - Call `GET https://openrouter.ai/api/v1/models` (no auth required for public listing)
   - Inspect the `id` field for exact model identifiers
   - Do NOT construct model IDs manually (e.g., `openai/gpt-4:free` only if `:free` variant appears in that model's `variants` list in the API response)
   - Do NOT assume base model and variant share context length, tool support, or pricing

5. **Prefer current docs/API over memory** — do not cite pricing, model availability, or SDK features from memory that might be stale. Route to live docs/API for changing facts.

**Minimum viable answer quality:**
- At least one docs page verified from `llms.txt`
- At least one cross-check (API call or fresh page read) if making specific claims
- Clear statement if something is unverified or appears to conflict with docs

---

## C. Core API surface — stable basics

**Base endpoint** (verified from Quickstart):
```
https://openrouter.ai/api/v1
```

**Authentication**:
- Header: `Authorization: Bearer $OPENROUTER_API_KEY`
- The API key is obtained from the OpenRouter dashboard or via the Management API keys endpoint

**Optional attribution headers** (help app rankings on openrouter.ai):
- `HTTP-Referer: <YOUR_SITE_URL>`
- `X-Title: <YOUR_SITE_NAME>`

**Key endpoints** (verify each in the API reference before using):
- `POST /chat/completions` — chat completions (OAI-compatible)
- `POST /embeddings` — create embeddings
- `GET /models` — list available models (public, no auth required)
- `GET /generations` — list your generation history (requires auth)
- `GET /credits` — get credit balance (requires auth)
- `POST /auth/key` — create a management API key (requires auth)
- `POST /auth/key/rotate` — rotate API keys (requires auth)
- `GET /providers` — list provider information
- `GET /rerank` — reranking endpoint

**Authentication reference**: https://openrouter.ai/docs/api/reference/authentication.mdx  
**Parameters reference**: https://openrouter.ai/docs/api/reference/parameters.mdx  
**Errors**: https://openrouter.ai/docs/api/reference/errors-and-debugging.mdx  
**Streaming**: https://openrouter.ai/docs/api/reference/streaming.mdx

**Responses API (Beta)** — an OpenAI-compatible stateless transformation layer with built-in reasoning, tool calling, and web search:
- Overview: https://openrouter.ai/docs/api/reference/responses/overview.mdx
- Basic usage, reasoning, tool calling, web search, error handling are separate pages — fetch specific ones when needed.

---

## D. SDK decision framework

Choose the integration approach based on task complexity and language:

| Goal / Task | Recommended SDK | When to choose this | Docs |
|-------------|----------------|---------------------|------|
| Simple model calls, minimal dependencies, any language | OpenRouter REST API (`fetch`/`curl`) | One-off requests, shell scripts, non-JS/Python langs | Quickstart |
| Type-safe client, TypeScript/JavaScript | `@openrouter/sdk` | Direct API calls, chat, embeddings, models listing, account operations, no agent loops needed | TypeScript SDK |
| Type-safe client, Python | `openrouter` (Python SDK) | Same as above for Python projects | Python SDK |
| Go projects | `openrouter` Go SDK | Typed client for Go; covers chat, embeddings, models, etc. | Go SDK reference |
| **Agentic workflows** with tools, multi-turn state, stop conditions | `@openrouter/agent` (TypeScript) | Building autonomous agents, tool-calling loops, dynamic parameters, streaming with state | Agent SDK |
| Existing codebase already using OpenAI SDK | OpenAI SDK (pointed at OpenRouter) | Drop-in replacement to keep code unchanged while accessing OpenRouter catalog | OpenAI SDK integration |
| Framework-native integration (Vercel AI SDK, LangChain, PydanticAI, etc.) | Framework adapter | Use the project's native OpenRouter integration page | Frameworks overview |
| Deep provider-specific tuning or provider-native SDKs | Provider's native SDK | Only when using provider directly, not through OpenRouter | Provider docs |

**Critical SDK rules to enforce:**

1. **Do NOT recommend `@openrouter/agent` as a default for simple calls.** It's an agentic framework; use it only when the user needs tool-calling loops, stop conditions, conversation state management, or multi-step dynamic behavior. For a single chat completion, use `@openrouter/sdk` or the REST API.

2. **`@openrouter/agent` is TypeScript-first.** If it's the right fit, provide TypeScript examples unless the user explicitly requests another language. It does not have official Python bindings as of current docs.

3. **When user only needs direct model calls or account operations**, default to `@openrouter/sdk` (TS) or `openrouter` (Python). Explicitly state when a task is too simple for the Agent SDK.

4. **When user mentions a framework (LangChain, Vercel AI SDK, etc.)**, immediately route to that framework's OpenRouter integration page from the docs index. Do not guess API calls — read the framework-specific page first.

5. **SDK feature parity varies by language.** The TypeScript SDK may have response streaming primitives; check the respective API reference pages before claiming capability.

---

## E. Task-to-docs routing table

Map user tasks to the canonical docs pages listed in `llms.txt`. This is a resolver: it routes to the right existing page; do not reproduce docs here.

| Task / User Intent | Primary Docs Page | Notes |
|--------------------|-------------------|-------|
| Getting started, first API call | Quickstart: https://openrouter.ai/docs/quickstart.mdx | Shows API, SDKs, Agent SDK options |
| Understanding OpenRouter's approach and guarantees | Principles: https://openrouter.ai/docs/guides/overview/principles.mdx | |
| Browsing all models, understanding provider catalog | Models guide: https://openrouter.ai/docs/guides/overview/models.mdx | Always pair with live `/api/v1/models` lookup |
| **Supported input/output modalities** | | |
| Send images to vision models | Image inputs: https://openrouter.ai/docs/guides/overview/multimodal/images.mdx | |
| Send PDFs to any model | PDF inputs: https://openrouter.ai/docs/guides/overview/multimodal/pdfs.mdx | |
| Send audio files, receive audio responses | Audio: https://openrouter.ai/docs/guides/overview/multimodal/audio.mdx | |
| Send video to video-capable models | Video inputs: https://openrouter.ai/docs/guides/overview/multimodal/videos.mdx | |
| Generate images from text | Image generation: https://openrouter.ai/docs/guides/overview/multimodal/image-generation.mdx | |
| Generate speech from text (TTS) | Text-to-speech: https://openrouter.ai/docs/guides/overview/multimodal/tts.mdx | |
| Generate videos from text | Video generation: https://openrouter.ai/docs/guides/overview/multimodal/video-generation.mdx | |
| **Model selection, routing, optimization** | | |
| Automatic failover when provider is down or rate-limited | Model fallbacks: https://openrouter.ai/docs/guides/routing/model-fallbacks.mdx | |
| Route across providers to optimize cost/performance | Provider routing: https://openrouter.ai/docs/guides/routing/provider-selection.mdx | |
| Let OpenRouter pick the best model automatically | Auto Router: https://openrouter.ai/docs/guides/routing/routers/auto-router.mdx | |
| Ask for model selection using natural language | Body Builder router: https://openrouter.ai/docs/guides/routing/routers/body-builder.mdx | |
| Route to free models only | Free models router: https://openrouter.ai/docs/guides/routing/routers/free-models-router.mdx | |
| Optimize tool-calling provider ordering | Auto Exacto: https://openrouter.ai/docs/guides/routing/auto-exacto.mdx | |
| **Model variants** — suffix modifiers (verify model supports variant via API first) | | |
| Access the free inference tier | Free variant: https://openrouter.ai/docs/guides/routing/model-variants/free.mdx | Only if `:free` appears in that model's `variants` array |
| Extended context window version | Extended variant: https://openrouter.ai/docs/guides/routing/model-variants/extended.mdx | |
| Prioritize high-quality tool-calling providers | Exacto variant: https://openrouter.ai/docs/guides/routing/model-variants/exacto.mdx | |
| Access models with longer reasoning/thinking phase | Thinking variant: https://openrouter.ai/docs/guides/routing/model-variants/thinking.mdx | |
| Add real-time web search capability | Online variant: https://openrouter.ai/docs/guides/routing/model-variants/online.mdx | Alternative to server tools web search |
| Nitro variant — high-speed inference | Nitro variant: https://openrouter.ai/docs/guides/routing/model-variants/nitro.mdx | |
| **Core SDK integration** | | |
| TypeScript SDK overview | Client SDKs overview: https://openrouter.ai/docs/client-sdks/overview.mdx | |
| Python SDK overview | Python SDK: https://openrouter.ai/docs/client-sdks/python/overview.mdx | |
| Go SDK methods reference | Go SDK API reference: https://openrouter.ai/docs/client-sdks/go/api-reference/chat.mdx (start here, then others) | Look under /client-sdks/go/api-reference/ |
| Agent SDK (callModel, tools, state) | Agent SDK overview: https://openrouter.ai/docs/agent-sdk/overview.mdx | |
| Using OpenAI SDK with OpenRouter | OpenAI SDK integration: https://openrouter.ai/docs/guides/community/openai-sdk.mdx | Drop-in replacement |
| Migrate from old agent toolkit | Migration guide: https://openrouter.ai/docs/client-sdks/agent-migration.mdx | |
| **Framework & ecosystem integrations** | | |
| All framework integrations overview | Frameworks and integrations overview: https://openrouter.ai/docs/guides/community/frameworks-and-integrations-overview.mdx | Start here |
| Vercel AI SDK (Next.js, streaming) | Vercel AI SDK: https://openrouter.ai/docs/guides/community/vercel-ai-sdk.mdx | |
| LangChain (chains, agents, retrievers) | LangChain: https://openrouter.ai/docs/guides/community/langchain.mdx | |
| PydanticAI (structured outputs, tools) | PydanticAI: https://openrouter.ai/docs/guides/community/pydantic-ai.mdx | |
| LiveKit Agents (voice AI) | LiveKit: https://openrouter.ai/docs/guides/community/livekit.mdx | |
| Anthropic Agent SDK | Anthropic Agent SDK: https://openrouter.ai/docs/guides/community/anthropic-agent-sdk.mdx | |
| Mastra framework | Mastra: https://openrouter.ai/docs/guides/community/mastra.mdx | |
| TanStack AI | TanStack AI: https://openrouter.ai/docs/guides/community/tanstack-ai.mdx | |
| Effect AI SDK | Effect AI: https://openrouter.ai/docs/guides/community/effect-ai-sdk.mdx | |
| MCP servers with OpenRouter | MCP servers: https://openrouter.ai/docs/guides/coding-agents/mcp-servers.mdx | |
| OpenClaw (multi-platform agents) | OpenClaw: https://openrouter.ai/docs/guides/coding-agents/openclaw-integration.mdx | |
| Xcode / Apple Intelligence | Xcode: https://openrouter.ai/docs/guides/community/xcode.mdx | |
| Zapier integrations | Zapier: https://openrouter.ai/docs/guides/community/zapier.mdx | |
| **Tools: OpenRouter server-side tools** (executed by OpenRouter, not client) | | |
| Web search tool server-side | Server tools web search: https://openrouter.ai/docs/guides/features/server-tools/web-search.mdx | Distinct from plugin version |
| Datetime awareness server-side | Server tools datetime: https://openrouter.ai/docs/guides/features/server-tools/datetime.mdx | |
| Image generation server-side tool | Server tools image generation: https://openrouter.ai/docs/guides/features/server-tools/image-generation.mdx | |
| Web fetch (URL retrieval) server-side | Server tools web fetch: https://openrouter.ai/docs/guides/features/server-tools/web-fetch.mdx | |
| Server tools overview | Server tools overview: https://openrouter.ai/docs/guides/features/server-tools/overview.mdx | |
| **Tools: plugins** (different mechanism from server tools) | | |
| Web search as a plugin | Plugin web search: https://openrouter.ai/docs/guides/features/plugins/web-search.mdx | |
| Response healing (JSON repair) plugin | Response healing: https://openrouter.ai/docs/guides/features/plugins/response-healing.mdx | |
| Plugins overview | Plugins overview: https://openrouter.ai/docs/guides/features/plugins/overview.mdx | |
| **Structured outputs & schemas** | | |
| JSON schema validation on responses | Structured outputs: https://openrouter.ai/docs/guides/features/structured-outputs.mdx | |
| **Other key features** | | |
| Cache repeated model calls | Response caching: https://openrouter.ai/docs/guides/features/response-caching.mdx | |
| Transformation/compression of messages | Message transforms: https://openrouter.ai/docs/guides/features/message-transforms.mdx | |
| Workspaces (project isolation) | Workspaces: https://openrouter.ai/docs/guides/features/workspaces.mdx | |
| Presets (saved configurations) | Presets: https://openrouter.ai/docs/guides/features/presets.mdx | |
| Spending & model access controls | Guardrails: https://openrouter.ai/docs/guides/features/guardrails.mdx | |
| Control cost/latency tradeoff | Service tiers: https://openrouter.ai/docs/guides/features/service-tiers.mdx | |
| Log prompts/completions for debugging | Input/output logging: https://openrouter.ai/docs/guides/features/input-output-logging.mdx | |
| Observability: traces to external backends | Broadcast overview: https://openrouter.ai/docs/guides/features/broadcast/overview.mdx | Covers Langfuse, Datadog, Sentry, OpenTelemetry, etc. |
| **Privacy, data, compliance** | | |
| Data collection & usage policy | Data collection: https://openrouter.ai/docs/guides/privacy/data-collection.mdx | |
| How providers log your data | Provider logging: https://openrouter.ai/docs/guides/privacy/provider-logging.mdx | |
| Opt out of data retention | Zero Data Retention (ZDR): https://openrouter.ai/docs/guides/features/zdr.mdx | |
| Bring your own provider keys | BYOK: https://openrouter.ai/docs/guides/overview/auth/byok.mdx | |
| User authentication for apps | OAuth PKCE: https://openrouter.ai/docs/guides/overview/auth/oauth.mdx | |
| **Administration** | | |
| Export activity reports (CSV/PDF) | Activity export: https://openrouter.ai/docs/guides/administration/activity-export.mdx | |
| Rotate API keys securely | API key rotation: https://openrouter.ai/docs/guides/administration/api-key-rotation.mdx | |
| Organization & team management | Organization management: https://openrouter.ai/docs/guides/administration/organization-management.mdx | |
| Track usage per key/model/user | Usage accounting: https://openrouter.ai/docs/guides/administration/usage-accounting.mdx | |
| Sub-user analytics | User tracking: https://openrouter.ai/docs/guides/administration/user-tracking.mdx | |
| **Best practices & optimization** | | |
| Latency optimization strategies | Latency and performance: https://openrouter.ai/docs/guides/best-practices/latency-and-performance.mdx | |
| Cache common prompt responses | Prompt caching: https://openrouter.ai/docs/guides/best-practices/prompt-caching.mdx | |
| Maximize uptime via routing | Uptime optimization: https://openrouter.ai/docs/guides/best-practices/uptime-optimization.mdx | |
| Reasoning/chain-of-thought control | Reasoning tokens: https://openrouter.ai/docs/guides/best-practices/reasoning-tokens.mdx | |
| **Coding agents & MCP** | | |
| Claude Code with OpenRouter | Claude Code integration: https://openrouter.ai/docs/guides/coding-agents/claude-code-integration.mdx | |
| Codex CLI integration | Codex CLI: https://openrouter.ai/docs/guides/coding-agents/codex-cli.mdx | |
| JetBrains Junie integration | Junie: https://openrouter.ai/docs/guides/coding-agents/junie.mdx | |
| MCP servers with OpenRouter | MCP servers: https://openrouter.ai/docs/guides/coding-agents/mcp-servers.mdx | |
| Auto code review setup | Automatic code review: https://openrouter.ai/docs/guides/coding-agents/automatic-code-review.mdx | |
| Build custom agent TUI harness | Create agent harness TUI: https://openrouter.ai/docs/guides/coding-agents/create-agent-harness-tui.mdx | |
| Claude Desktop integration | Claude Desktop: https://openrouter.ai/docs/guides/coding-agents/claude-desktop-integration.mdx | |
| **Evaluate & optimize** | | |
| Build RAG with embeddings + rerank + LLM | RAG guide: https://openrouter.ai/docs/guides/evaluate-and-optimize/rag.mdx | |
| Model migration guides (Claude, GPT) | Model migrations index — see llms.txt under "Evaluate and Optimize" section | Check specific model migration pages |
| Distillation & training data policy | Distillation: https://openrouter.ai/docs/guides/evaluate-and-optimize/distillation.mdx | |
| Authorized red teaming policy | Red teaming: https://openrouter.ai/docs/guides/evaluate-and-optimize/red-teaming.mdx | |
| **API reference (general)** | | |
| Complete API spec & request/response schemas | API reference overview: https://openrouter.ai/docs/api/reference/overview.mdx | |
| API limits, rate limits, quotas | Limits: https://openrouter.ai/docs/api/reference/limits.mdx | |

---

## F. Model selection framework

Always fetch live model list before coding that requires specific model IDs:
```
GET https://openrouter.ai/api/v1/models
```

No authentication needed.

### When to use Auto Router

**Use Auto Router** when:
- You don't have strict provider requirements
- Cost optimization matters more than absolute peak performance
- You want best-effort availability with automatic fallbacks
- The use case is general-purpose (summarization, Q&A, general chat)

**Do NOT rely on Auto Router** when:
- You need a specific provider due to data residency, compliance, or licensing
- You require a specific model family (e.g., Claude Sonnet, GPT-4o) for known capabilities
- You need to guarantee a minimum context length or feature set

### When to use specific model IDs

Use a specific `provider/model-id` format (e.g., `openai/gpt-4o`, `anthropic/claude-sonnet-4`) when:
- Task needs known context window or tool-calling capability that Auto Router might substitute
- You need to compare across providers explicitly
- Your app's UX requires showing which model generated the response

### Free model rate limits (critical for cost planning)

OpenRouter offers two kinds of free models — understand the difference:

**`:free` tagged models** (e.g., `qwen/qwen3-coder:free`, `deepseek/deepseek-v4-flash:free`):
- 20 requests/minute
- If you've purchased **less than 10 credits** total: **50 requests/day**
- If you've purchased **10+ credits** total: **1,000 requests/day**
- These limits are per-model, per-API-key
- Hitting the limit returns HTTP 429. Resets daily UTC.

**Native $0 models without `:free` tag** (e.g., Owl Alpha — OpenRouter's own model):
- Do NOT follow the same `:free` rate limits
- Limits are based on OpenRouter's capacity for that specific model
- Owl Alpha serves ~1.3 trillion tokens/week with 99.99% uptime — much more generous
- Always check the model's specific page on OpenRouter for its capacity

**Key implication:** If you have never paid OpenRouter (0 credits purchased), `:free` models are effectively capped at 50 requests/day — too tight for agent workloads. A one-time $10 top-up unlocks 1,000/day across `:free` models. For heavier usage, prefer non-`:free` $0 models like Owl Alpha when available.

### Using OpenRouter as a Hermes Agent provider

When configuring Hermes Agent to use OpenRouter as its model provider or fallback:

**Set as primary provider (config.yaml):**
```yaml
model:
  provider: openrouter
  default: deepseek/deepseek-v4-flash:free
```

**Set as fallback provider (config.yaml):**
```yaml
model:
  provider: nous
  default: deepseek/deepseek-v4-flash:free
  fallback:
    provider: openrouter
    default: deepseek/deepseek-v4-flash:free   # same model, different provider for resilience
```

**Via CLI (no manual YAML editing needed):**
```bash
hermes config set model.fallback.provider openrouter
hermes config set model.fallback.default deepseek/deepseek-v4-flash:free
```

**Key principles:**
- Same-model-different-provider fallback is a valid pattern (provider diversity, not model diversity)
- The OpenRouter API key must be available — either in `~/.hermes/.env`, profile `.env`, or as a shell env var
- Verify with `hermes auth list` — OpenRouter should show as a credential with source `env:OPENROUTER_API_KEY`
- Each profile has its own config — apply fallback per-profile for multi-agent setups

**Common pitfalls:**
- Nesting order matters: `model.fallback.provider` not `model.provider.fallback`
- Don't set fallback to the same model on the same provider (doesn't help for provider-wide outages)
- Free model daily limits apply via OpenRouter even as a fallback

### When (and how) to use model variants

Variants are suffix modifiers appended to a model ID (e.g., `openai/gpt-4o:nitro`). They alter behavior or tier. Rules:

1. **Only use variants that appear in the API response for that model.** The models endpoint returns each model with a `variants` array listing all valid suffixes. If `:free` is not in that model's `variants`, `model:free` is invalid — do NOT invent it.

2. **Do NOT assume variant and base have identical capabilities.** A `:free` variant may have lower rate limits, different pricing, or constrained context length. A `:extended` variant may have larger context but different cost curve. Always read the variant-specific docs page linked in the routing section above for changes.

3. **Variant availability is model-specific.** Not every model has every variant. Check the live model list.

4. **When variant semantics are unclear** (e.g., `:floor`, `:thinking`, `:exacto`), read the corresponding variant docs page first. Some variants affect inference cost/latency tradeoffs; others change reasoning behavior.

### When to use fallbacks and provider routing

- Fallbacks: When your primary provider/model is down or rate-limited, and you want automatic retry on alternative providers/models without code changes.
- Provider routing: When you want OpenRouter to select providers for each request based on current cost/performance signals.
- Provider restrictions: Use provider selection to exclude certain providers (e.g., exclude providers that log data if user privacy is required).

### Fetch models and inspect capabilities

**Do this** before implementing:
- Model discovery for dynamic UI/model selection: show users all available models
- Version-sensitive features (varying context lengths, tool availability, multimodal support) — the models API returns `context_length`, `top_provider` (default provider), `supported_parameters`, `pricing`, `架构架构architecture` details
- Pricing calculations — `pricing.prompt` and `pricing.completion` per token

**Never do this:**
- Hardcode model IDs when you can offer users a dynamic list
- Assume all providers support the same parameters or tool-calling features
- Assume all models support image inputs just because some do

---

## G. Tool calling and structured output framework

OpenRouter supports three distinct mechanisms. Do not confuse them.

### 1. Native tool calling (client-side execution)
The model emits tool call messages. Your application receives them and decides whether/ how to execute the tool. Then you send tool results back to the model.

**When to use:** When you need custom tool logic, internal API access, or control over tool execution order. Works with OpenAI, Anthropic, and other provider-native function-calling formats.

**Docs to read:**
- Tool calling feature: https://openrouter.ai/docs/guides/features/tool-calling.mdx
- Provider-specific tool support varies — verify your model supports tool calling via the models API

### 2. Server tools (OpenRouter-executed)
OpenRouter runs the tool on your behalf and returns results as part of the model response. Currently includes: web search, datetime, image generation, and web fetch.

**When to use:** Externalities — you want the model to fetch real-time info (search, datetime) or generate images without your own tool infrastructure.

**Docs to read:**
- Server tools overview: https://openrouter.ai/docs/guides/features/server-tools/overview.mdx
- Each server tool has its own page (see routing table above)
- Server tools are **not** the same as plugins or response healing

### 3. Structured outputs (constrained response schema)
The model is constrained to output valid JSON matching your provided schema. No tool calls — just a validated final response in the desired shape.

**When to use:** You need a reliable data structure from the model (e.g., extract entities, generate structured API payloads) without the overhead of a tool-calling loop.

**Docs to read:**
- Structured outputs: https://openrouter.ai/docs/guides/features/structured-outputs.mdx

### 4. Plugins
Different from server tools. Enable capabilities like response healing (malformed JSON repair) or web search via a plugin mechanism rather than direct server tool execution.

**Docs to read:**
- Plugins overview: https://openrouter.ai/docs/guides/features/plugins/overview.mdx
- Response healing plugin: https://openrouter.ai/docs/guides/features/plugins/response-healing.mdx

### Gotchas across all three

- **Support is model-dependent.** A model that supports tool calling may not support all three mechanisms equally. Check the model's `supported_parameters` from the models API; some have `tools`, others have `structured_outputs`. Some server tools require a provider that supports them.
- **Schema strictness varies.** Structured outputs may fail silently or throw errors if the schema is too restrictive or conflicts with provider-side validation.
- **Do not expect tool calling and structured outputs to be interchangeable.** Tool calls invoke functions; structured outputs constrain final text format.
- **Server tools execute on OpenRouter's infrastructure,** not your environment. This means rate limits, latency, and availability are outside your direct control.
- **Tool call loops require Agent SDK for easy management.** Native tool-calling loops require you to manually send tool_result messages back and forth. Use `@openrouter/agent` for automatic state management unless you need custom orchestration.

---

## H. Common gotchas — failure modes to prevent

**Model ID & variant errors:**
- ❌ Hardcoding model IDs that don't exist in the current model catalog. Always check `GET /api/v1/models` first.
- ❌ Constructing variant IDs by appending `:free`, `:nitro`, `:exacto`, `:thinking`, `:extended` manually. Only use variants listed in that model's `variants` array in the API response.
- ❌ Assuming base and variant models share context length, tool support, or pricing. Variant may be a different model variant entirely; read its specific docs page.
- ❌ Using a model region/provider that doesn't exist for that model (check `providers` array in model object).

**Docs linking errors:**
- ❌ Linking to docs URLs not present in `llms.txt`. Every URL must appear in the index. If unsure, fetch `llms.txt` and grep for the path segment.
- ❌ Copying code examples from outdated blog posts or third-party tutorials instead of official docs.

**SDK/feature confusion:**
- ❌ Recommending `@openrouter/agent` for simple completions. It's meant for agent loops; use `@openrouter/sdk` or REST for one-shot requests.
- ❌ Assuming SDK feature parity across languages. TypeScript SDK streaming API is not identical to Python SDK streaming API — check language-specific API reference pages.
- ❌ Mixing up Server Tools with plugins with structured outputs. They are different feature families with different activation patterns.
- ❌ Treating server-side web search (server tool) and response streaming as the same thing.

**Making unverified claims:**
- ❌ Pricing — do not state exact prices without cross-checking the models API (`pricing.prompt`, `pricing.completion`) or official pricing page.
- ❌ Model availability — do not say "Model X is available" unless it's in the live models list.
- ❌ Support status — do not say "feature X is supported" without checking the relevant docs page (capabilities move between beta/stable/removed).
- ❌ Performance numbers — do not quote latency, throughput, or uptime statistics. Route to the best practices pages instead.

**Execution boundary errors:**
- ❌ Assuming tools execute on client side when they're server tools. Server tools return as part of the model response; your code does not make the external call.
- ❌ Assuming structured outputs can call functions. They constrain output format, they don't execute actions.
- ❌ Streaming errors are often silent. Read the streaming error handling page before implementing streaming.

**Environment/secrets:**
- ❌ Hardcoding API keys in examples. Use `$OPENROUTER_API_KEY` environment variable placeholders only.

---

## I. Verification checklist (pre-delivery)

Before finalizing any answer about OpenRouter, confirm the following:

- [ ] **Docs checked:** Read `https://openrouter.ai/docs/llms.txt` to confirm the page exists. If uncertain, fetch the index and search for the relevant URL segment.
- [ ] **Model/API check:** If model IDs, variant IDs, or capabilities are involved, call `GET https://openrouter.ai/api/v1/models` and verify against the live response.
- [ ] **URL verification:** Every OpenRouter docs URL included in the answer appears in the `llms.txt` index (grep the index or use exact path match if uncertain).
- [ ] **SDK choice justified:** The recommended SDK matches the task scope (simple call → SDK/REST; agentic → Agent SDK; framework-specific → framework adapter).
- [ ] **Examples match current docs:** Code snippets follow the structure shown in the current official docs page for the referenced feature. If in doubt, re-fetch that page.
- [ ] **No unverified claims:** No statements about pricing, availability, performance, or support status unless supported by a checked live source (models API, pricing page, or docs from the index).
- [ ] **Correct feature boundaries:** Distinction between server tools, client-side tools, structured outputs, and plugins is clear in the explanation.

If any item fails, go back and gather current information before answering.

---

## J. Helper scripts (optional)

These are small shell utilities to automate routine checks. Keep them in `scripts/` next to this SKILL.md when the skill is installed.

### `scripts/pull-docs-index.sh`

Fetch the latest documentation index and store it locally for fast reference.

```bash
#!/bin/bash
# Usage: ./scripts/pull-docs-index.sh [output-file]
# Default: writes to ./openrouter-docs-index.txt
OUT="${1:-openrouter-docs-index.txt}"
curl -sL https://openrouter.ai/docs/llms.txt -o "$OUT"
echo "Saved docs index to $OUT"
```

### `scripts/check-doc-url.sh`

Verify a given URL exists in the cached index.

```bash
#!/bin/bash
# Usage: ./scripts/check-doc-url.sh <full-url>
# Example: ./scripts/check-doc-url.sh https://openrouter.ai/docs/guides/features/tool-calling.mdx
INDEX="${OPENROUTER_DOCS_INDEX:-./openrouter-docs-index.txt}"
URL="$1"

if [ -z "$URL" ]; then
  echo "Usage: $0 <full-url>"
  exit 1
fi

# Extract path after /docs/
PATH_PART=$(echo "$URL" | sed -n 's|.*/docs/\(.*\)|\1|p')
if [ -z "$PATH_PART" ]; then
  echo "Error: URL does not contain /docs/ path"
  exit 1
fi

if [ ! -f "$INDEX" ]; then
  echo "Error: docs index not found at $INDEX"
  echo "Run pull-docs-index.sh first."
  exit 1
fi

if grep -q "/$PATH_PART" "$INDEX"; then
  echo "✓ URL found in index: $URL"
  exit 0
else
  echo "✗ URL NOT found in index — may be stale or incorrect: $URL"
  exit 1
fi
```

### `scripts/list-models.sh`

Fetch current model list and output JSON. Optionally filter by provider or search term.

```bash
#!/bin/bash
# Usage: ./scripts/list-models.sh [filter-pattern]
# Example: ./scripts/list-models.sh openai
# Reads OPENROUTER_API_KEY environment variable (can be empty for public listing)
API_KEY="${OPENROUTER_API_KEY:-}"
AUTH_HEADER=""
if [ -n "$API_KEY" ]; then
  AUTH_HEADER="-H \"Authorization: Bearer $API_KEY\""
fi

curl -sL $AUTH_HEADER "https://openrouter.ai/api/v1/models" | python3 -m json.tool 2>/dev/null || curl -sL $AUTH_HEADER "https://openrouter.ai/api/v1/models"
```

**Note:** These scripts are helpers only. Do not call them automatically during skill execution unless the user explicitly enables automation. The core skill logic prefers live API/docs over cached files.

---

## End of skill

This skill is a resolver: it routes you to the right docs and checks live sources. It does not replicate full documentation content — that would become stale. Instead it gives you:

- Exact URLs to read (verified against `llms.txt`)
- Decision frameworks when multiple approaches exist
- Common failure patterns to avoid
- A pre-answer ritual that forces verification before claiming anything

**Reference files:**
- `references/free-agent-models.md` — detailed benchmarks for Owl Alpha, Qwen3 Coder, Nous negative-balance quirk, and model comparison for agent use cases

**Template note:** This skill's structure has become a canonical **provider adapter pattern**. The `nvidia-nim-expert` skill was created by reading this SKILL.md in full and systematically adapting its sections (URLs, env vars, model ID formats) for NVIDIA's OpenAI-compatible NIM endpoint. When building new provider skills, start here: copy this file, run the find-replace mapping in Section C of `create-provider-skill`, and verify provider-specific gotchas.

Remember: if the user is asking a generic AI question that doesn't require the OpenRouter-specific layer, you may not need this skill. Only activate it when OpenRouter's unified API, routing, or SDKs are relevant to the user's intent.
