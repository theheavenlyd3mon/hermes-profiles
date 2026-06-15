---
name: create-provider-skill
description: Systematic process for creating provider-specific OpenAI-compatible adapter skills (like nvidia-nim-expert) by adapting the openrouter-expert pattern. Covers directory structure, configuration, scripts, docs routing, and verification workflow.
version: 1.0.0
author: Senna
license: MIT
metadata:
  hermes:
    tags: [skill-creation, provider-integration, openai-compatible, adapter-pattern, skill-factory]
    related_skills: [openrouter-expert, nvidia-nim-expert, ollama-cloud-expert]
---

IDENTITY: SkillFactory{TemplateAdaptation,CanonicalPattern}. CoreRole: Reproduce the openrouter-expert provider adapter pattern for new OpenAI-compatible inference endpoints. BehavioralContract: Read template fully, adapt surface-level values (URLs, env vars, model IDs), keep resolver philosophy and verification rituals.
Law: Never paste external docs into skills. Route to live docs. Verify URLs exist before committing.
WHENUSE: Integrating new LLM/embedding provider with OpenAI-compatible endpoints. ESPECIALLY:{NewProviderSDK,CloudNIM,OpenAICompatibleAPI}. NoSkip:{TemplateRead,URLVerification}.
REDFLAGS: NonStandardAPI->BuildFromScratch|PasteExternalDocs->StaleSkill|NoTemplateRead->StructuralDrift|OneOffScript->DontNeedSkill|HardcodedModelIDs->StaleClaims.
RATIONALIZATIONS: "I know the template"->ReadItAnyway|"Quick one-off"->SkillScaffoldingOverkill|"I'll verify later"->StaleURLs.
QUICKREF: Locate{template SKILL.md}->CreateDir{category/name/scripts}->Adapt{find-replace URLs/env/modelIDs}->Scripts{list-models,test-connection,quick-start}->Verify{URLs exist,live API check}->Test{end-to-end with real key}.

# Create Provider Skill

A meta-skill that encodes the reproducible workflow for building provider-specific OpenAI-compatible adapter skills. Used to create `nvidia-nim-expert` from the `openrouter-expert` template.

This skill documents the **non-trivial approach** discovered through trial and error: taking an existing, well-structured skill as a template, reading its full content to understand conventions, then systematically adapting it for a new provider while maintaining Hermes skill quality standards.

---

## A. When to use this skill

**Trigger when:**
- You need to integrate a new LLM/embedding provider that offers OpenAI-compatible endpoints
- You have an existing skill (like `openrouter-expert` or `ollama-cloud-expert`) that serves as a proven template
- You want to maintain consistent structure, verification rituals, and documentation routing across provider skills
- You're adding Cloud NIM, TogetherAI, Cohere, Anthropic direct, or any OpenAI-compatible API service

**Do NOT use when:**
- Building a completely new skill category (this is for **provider adapters specifically**)
- The provider uses a non-standard API (different auth, request format) — build from scratch instead
- Only need a quick one-off script (don't need full skill scaffolding)

---

## B. The adapted pattern — what was learned

The `openrouter-expert` skill structure proved to be an excellent template. The key insight: **most provider adapter needs are identical** — just different endpoints, auth headers, and model ID formats.

**Canonical sections (copy from template, adapt values):**

| Section | Purpose | Adapt for NVIDIA NIM |
|---------|---------|----------------------|
| **A. When to load** | Trigger conditions | Replace "OpenRouter" with "NVIDIA NIM" triggers |
| **B. Pre-answer ritual** | Verification before claims | Swap OpenRouter docs URLs for NVIDIA docs URLs; use `integrate.api.nvidia.com/v1/models` instead of `openrouter.ai/api/v1/models` |
| **C. Core API surface** | Endpoints & auth | Change base URL, auth header style if different, key env var names |
| **D. Model types** | Naming conventions | Document provider's model ID format (e.g., `meta/llama3-70b` vs `openai/gpt-4`) |
| **E. Integration patterns** | Code examples | Rewrite examples with provider's endpoints; preserve OpenAI SDK pattern |
| **F. Task-to-docs routing** | Map tasks to docs | Build a routing table with NVIDIA's actual docs URLs (verify they exist) |
| **G. Common gotchas** | Failure modes | Provider-specific pitfalls (rate limits, variant handling, endpoint confusion) |
| **H. Verification checklist** | Pre-delivery QA | Mirror the template but with provider-specific checks |
| **I. Helper scripts** | CLI utilities | Write scripts that call provider's API (models list, health check) |
| **J. Quick reference** | One-liners | Copy-paste snippets for immediate use |

---

## C. Step-by-step provider skill creation

### Step 1 — Locate the template
```bash
# The proven template lives at:
~/.hermes/profiles/senna/skills/software-development/openrouter-expert/SKILL.md
```

Read it fully to understand:
- Section structure and ordering
- Tone (resolver, not replicator — "route to docs" not "copy docs here")
- Verification rigor (live API checks, no stale claims)
- Script helper patterns

### Step 2 — Create skill directory
```bash
# Choose category:
# - software-development/  for provider SDK/integration skills
# - mlops/inference/       for model serving skills
# - autonomous-ai-agents/  for agent-specific integrations

SKILL_NAME="provider-name-expert"  # e.g., nvidia-nim-expert, togetherai-expert
CATEGORY="mlops/inference"  # or "software-development"

mkdir -p ~/.hermes/profiles/senna/skills/${CATEGORY}/${SKILL_NAME}/scripts
```

### Step 3 — Build SKILL.md from template

Copy the template structure, then replace:

```
s/OpenRouter/PROVIDER NAME/g
s/openrouter.ai/PROVIDER_DOCS_DOMAIN/g
s/openrouter.ai/api/PROVIDER_API_ENDPOINT/g
s/@openrouter/PROVIDER_SDK_PACKAGE/g  # if different
s/provider-model-id/PROVIDER_MODEL_FORMAT/g
```

**Keep the resolver philosophy:**
- Do NOT paste large chunks of external documentation
- DO link to official docs pages with verified URLs
- DO include live API checks (`GET /models`) in verification steps
- DO include a helper scripts section with working CLI utilities

### Step 4 — Write provider-specific helper scripts

**Minimum viable scripts set:**

1. `list-models.sh` — `GET /models` endpoint, pretty-printed JSON or simple list
2. `test-connection.sh` — health check with clear pass/fail output
3. `quick-start.py` — Python example that imports the right SDK and runs one completion

Make them executable (`chmod +x`).

**Script requirements:**
- Accept NVIDIA_API_KEY / OPENAI_API_KEY / PROVIDER_API_KEY env vars
- Fail clearly with error messages (key not set, import missing)
- Output human-readable success/failure indicators (✓ / ✗)
- Support both shell and Python entry points

### Step 5 — Verify docs URLs exist

Before finalizing, open the provider's docs site and verify every URL you plan to reference actually exists. Update the routing table with real, working links.

For NVIDIA NIM: `https://docs.nvidia.com/nim/latest/` was checked; for future providers, confirm their docs are stable before committing URLs.

### Step 6 — Test the skill end-to-end

```bash
# 1. Set key
export PROVIDER_API_KEY="xxx"

# 2. Run helper script
~/.hermes/profiles/senna/skills/CATEGORY/SKILL_NAME/scripts/test-connection.sh

# 3. Import and use from Python
python3 -c "from hermes_tools import ...; # test the integration"
```

Fix any path bugs or missing env var handling before considering the skill done.

### Step 7 — Update `skills_list` awareness

Hermes auto-discovers skills from the filesystem. Restart the agent session or reload skills if needed to activate the new skill.

No registration required — just drop the directory in the right place.

---

## D. Quality checklist for provider skills

**Structure:**

- [ ] SKILL.md follows the exact section ordering of the template
- [ ] Helper scripts placed in `scripts/` subdirectory and marked executable
- [ ] All scripts sourced from `SKILL.md` paths are actually present
- [ ] Skill loads when user mentions the provider name or API endpoint

**Content:**

- [ ] No hardcoded model IDs — always reference live models API
- [ ] No stale pricing claims — route to provider's pricing page
- [ ] Environment variables clearly listed in multiple forms (`PROVIDER_API_KEY`, `OPENAI_API_KEY`, etc.)
- [ ] Code examples work as-is (tested with a real or mock key)
- [ ] "Common gotchas" section includes at least 3 provider-specific pitfall patterns

**Verification:**

- [ ] Every docs URL appears in the provider's official docs index
- [ ] Helper scripts return clear ✓/✗ status
- [ ] Quick reference section has copy-paste examples that actually run

---

## E. Adaptation examples

### From `openrouter-expert` → `nvidia-nim-expert`

**Changed:**
- Base URL: `https://openrouter.ai/api/v1` → `https://integrate.api.nvidia.com/v1`
- Auth env vars: `OPENROUTER_API_KEY` → `NVIDIA_API_KEY` (plus OpenAI-style fallback)
- Model listing endpoint: same pattern (`GET /models`) but different host
- Model ID format: `provider/model-name` → `company/model-family-name` (e.g., `meta/llama3-70b-instruct`)
- Docs domain: `openrouter.ai/docs` → `docs.nvidia.com/nim`

**Kept identical (because they're correct):**
- Pre-answer ritual structure (verify live, don't trust memory)
- Resolver philosophy (link, don't copy)
- Helper script layout (list, test, quick-start)
- Quality checklist format
- Category placement (mlops/inference for model-serving skills)

---

## F. Provider skill inventory (current)

| Skill | Provider | API Style | Category | Status |
|-------|----------|-----------|----------|--------|
| openrouter-expert | OpenRouter | Gateway (multi-provider) | software-dev | ✅ exists |
| ollama-cloud-expert | Ollama Cloud | OpenAI-compatible | software-dev | ✅ exists |
| nvidia-nim-expert | NVIDIA NIM | OpenAI-compatible | mlops/inference | ✅ created |
| togetherai-expert | Together AI | OpenAI-compatible | mlops/inference | ⚠ not yet |
| cohere-expert | Cohere | Native + compatible | software-dev | ⚠ not yet |
| anthropic-direct | Anthropic | Native (non-OpenAI) | software-dev | ⚠ not yet |

**New provider candidates** that fit this pattern: Groq, DeepInfra, Replicate (some have OpenAI-compatible modes), Together AI, Perplexity (API).

---

## End of skill

**Reusable insight:** The `openrouter-expert` template is a **canonical provider integration pattern**. Creating `nvidia-nim-expert` validated that the template generalizes to any OpenAI-compatible inference endpoint with only surface-level changes (URLs, env vars, model ID formats). The structural scaffolding — verification rituals, helper scripts, resolver philosophy — is portable.

**When you create the next provider skill,** start here: copy `openrouter-expert/SKILL.md`, run the find-replace table in section C, and flesh out the provider-specific gotchas from their docs/issues. Less than 30 minutes of work once the pattern is known.
