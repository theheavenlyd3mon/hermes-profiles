# Build Plan Parsing — Extracting BLOCKING vs PARALLEL Tasks

When a build plan uses an explicit dependency graph with BLOCKING and PARALLEL markers, parse it systematically to decide what to build directly vs. delegate to subagents.

## The Standard Format (used in hackathon build plans)

Build plans in this format have three sections per task:

```
### PHASE 1: Foundation (Day 1-2)

#### Task 1.1: Project Scaffold & API Wiring `[BLOCKING]`
**Delegate as:** single subagent — coding tools

**What to build:**
1. FastAPI app skeleton with health check endpoint
2. NVIDIA Nemotron client wrapper
3. ...

#### Task 1.2: NemoClaw Guardrails (Config Files) `[PARALLEL with 1.1]`
...same structure...

#### Task 1.3: Demo Data Seeding `[PARALLEL with 1.1, 1.2]`
...same structure...
```

## Parsing Rules

### BLOCKING tasks
- Everything downstream depends on them
- **Build yourself** — they establish the architecture, conventions, and integration points
- These involve: app structure (main.py, config.py, db.py), client wrappers that all other code imports, shared data models
- Verification: the app boots and hello-world works before any parallel task's output is integrated

### PARALLEL tasks
- Independent of each other and of the blocking task (or depend only on the architecture conventions the blocking task establishes)
- **Delegate to subagents** — self-contained work that produces files at known paths
- These involve: config files at fixed paths, seed data, standalone modules that import from the shared layer
- Each subagent needs the full spec context for its domain (guardrail YAML specs, DB schema for seed data)

### Verification Order
1. Build blocking task → verify it boots
2. Delegate parallel tasks → they run in background
3. While they run, start using the blocking-task infrastructure
4. On subagent completion, verify their output immediately — import modules, run test functions, check file paths
5. Fix issues directly (patch the file) rather than re-dispatching

## Heuristic: What to Build vs. Delegate

| Build Yourself (BLOCKING) | Delegate (PARALLEL) |
|---|--|
| App entry point / main() | Configuration files at fixed paths |
| API client wrappers | Seed/populate scripts |
| Database schema + connection pool | Test fixtures |
| Shared data models | Demo data definitions |
| Webhook handlers (Twilio, Stripe) | Isolated utility modules |
| Top-level routing and config loading | Static file generation |

## Context for Subagents

When dispatching a parallel task, include in the `context` field:
- The exact spec excerpt relevant to their task
- File paths they should write to (absolute paths)
- Expected output format / verification command
- Data definitions in full (don't make them look up parts of the spec themselves)
- Any dependencies they need pip-installed

### Environment setup before dispatching

Before any subagent touches the project code, ensure the runtime environment is ready:

1. **Project venv has core deps installed** — `pip install openai stripe yaml` (or whatever the project's clients/ layer needs). Subagents hit import chain failures when they try to `from config import get_nemotron_client` and `config.py` imports `stripe` or `openai` which aren't installed.
2. **API keys in the project's .env** — if the project reads credentials from `config.py` which reads `os.environ`, write the key to the project's `.env` file before dispatching. Don't rely on the profile's `.env` — subagents run in their own session context.
3. **Verify the key is accessible** — a quick `grep -c "API_KEY" ~/maintenops/.env && echo "PRESENT"` before dispatching saves subagents from credential errors.

### Verification command pattern

Include a one-liner verification command at the end of every delegation goal that the subagent runs to self-validate:

```python
# In the goal/context field:
VERIFY: python3 -c "import asyncio; from tools.my_module import func; r = asyncio.run(func('test_input')); print(r['expected_key'])"
```

This should produce a specific output when the code is correct. The subagent runs this, sees expected output, and reports success with evidence rather than a vague "looks good."

Example:

```python
delegate_task(
    goal="Create seed script at /Users/.../seed.py",
    context="""
    SPEC EXCERPT (DB schema):
    CREATE TABLE vendors (
        id UUID PRIMARY KEY,
        name TEXT NOT NULL,
        ...
    );
    
    DEMO DATA:
    5 vendors (3 HVAC, 2 Plumbing):
    - CoolTech HVAC, license: CA-HVAC-4821, ...
    - ...
    
    FILE PATH: ~/maintenops/seed.py
    
    VERIFY: python3 seed.py --simulate
    """,
    toolsets=['file', 'terminal']
)
```
