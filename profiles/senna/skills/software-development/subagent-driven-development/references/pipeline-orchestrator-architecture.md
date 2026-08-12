# Pipeline-Orchestrator Architecture

After dispatching parallel subagents to build independent tool modules, you need an orchestrator that wires them together into a sequenced pipeline. This reference documents the pattern.

## The Problem

You have N independent tool modules (e.g. `tools/triage.py`, `tools/compliance.py`, `tools/vendor_match.py`), each built by its own subagent. They have different import paths, different async signatures, and different return shapes. You need one `agent.py` that calls them in order, accumulates state across phases, and degrades gracefully when individual modules fail.

## The Pattern

### 1. Guarded imports

Each tool module is imported in a `try/except ImportError` block. If the module is missing (subagent build failed, dependency not installed), the orchestrator sets it to `None` and logs a warning. Downstream phases check for `None` and use a fallback path.

```python
try:
    from tools.triage import triage_issue
except ImportError:
    triage_issue = None
    logger.warning("tools.triage not available")
```

This means the orchestrator never crashes at import time — a missing tool produces a degraded but functional pipeline, not a traceback.

### 2. Phase functions

Each pipeline phase is an `async def` function with a clear name (`phase_triage`, `phase_habitability`, etc.). Each function:

- Logs its start with a header separator
- Accepts only the data it needs (small surface area)
- Returns a dict result
- Catches exceptions internally and returns a fallback dict
- Logs key output values

```python
async def phase_triage(tenant_report: str, state: str) -> dict:
    logger.info("=" * 60)
    logger.info("PHASE 1 — TRIAGE")
    logger.info("=" * 60)
    
    if triage_issue is None:
        raise RuntimeError("Triage module not available")
    
    result = await triage_issue(tenant_report, state)
    logger.info("Triage result: urgency=%s  trade=%s", ...)
    return result
```

### 3. Pipeline state accumulation

The main pipeline function creates a `pipeline` dict at the top, calls phases in sequence, and stores each result under `pipeline["phases"][phase_name]`:

```python
async def run_pipeline(tenant_report: str, ...) -> dict:
    pipeline = {
        "ticket_id": ticket_id,
        "tenant_report": tenant_report,
        "started_at": ...,
        "phases": {},
    }
    
    triage_result = await phase_triage(tenant_report, state)
    pipeline["phases"]["triage"] = triage_result
    
    compliance_result = await phase_habitability(...)
    pipeline["phases"]["habitability"] = compliance_result
    
    # ... more phases ...
    
    pipeline["status"] = "completed"
    return pipeline
```

Each phase reads from the accumulated state (previous phase outputs) and writes back. The pipeline dict is the single source of truth.

### 4. Hardcoded fallback data

For demo/development, include hardcoded data that the orchestrator can use when external services (DB, APIs) are unavailable. This makes the pipeline runnable without any external dependencies:

```python
DEMO_VENDORS = {
    "CoolTech HVAC": {
        "name": "CoolTech HVAC", "trade": "HVAC", "rating": 4.9,
        "stripe_connect_account_id": "acct_vendor_001",
        "license_active": True, "insurance_active": True,
    },
    # ...
}

DEMO_OWNER = {
    "name": "Demo Owner", "maintenance_limit": 1500.00,
    "stripe_customer_id": "cus_demo_001",
}
```

This serves two purposes: (1) the pipeline works immediately after build for testing, and (2) the fallback data acts as a specification that real data sources should match.

### 5. Structured output formatting

Separate the pipeline execution from the output rendering. A `format_pipeline_summary(pipeline: dict) -> str` function reads the completed pipeline dict and produces a human-readable report:

```python
def format_pipeline_summary(pipeline: dict) -> str:
    lines = []
    lines.append("╔" + "═" * 58 + "╗")
    lines.append(f"║  Pipeline {pipeline['status'].upper()}")
    # ... read from pipeline["phases"] and format ...
    return "\n".join(lines)
```

### 6. CLI entry point

The `__main__` block accepts input from argv or uses a default:

```python
if __name__ == "__main__":
    report = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not report:
        report = "AC not cooling, 87 degrees inside, have a newborn baby"
    result = asyncio.run(run_pipeline(report))
    print(format_pipeline_summary(result))
```

## When to use vs. not

**Use this pattern when:**
- You have 3+ independent tool modules that need sequencing
- Phases have a clear dependency order (triage → compliance → vendor match → etc.)
- You want the system to degrade gracefully when individual tools fail
- The pipeline produces a single result (ticket resolved, payment made, etc.)

**Do NOT use this pattern when:**
- The tools are called independently (user asks "check warranty" in isolation) — just call the tool directly
- The phases are truly parallel with no ordering constraints — dispatch subagents instead
- The pipeline has branches or conditional routing (if emergency → skip quote comparison) — use a different structure

## Example: 10-phase pipeline

```
1. triage      → normal: {"urgency": "urgent", "trade_needed": "HVAC"}
                   fallback: {"urgency": "routine", "trade_needed": "General Contractor"}
2. habitability → normal: {"deadline_hours": 24, "applicable": true}
                   fallback: {"applicable": false}
3. vendor_match  → normal: [{"name": "CoolTech", "rating": 4.9}]
                   fallback: hardcoded top-3
4. simulate_quotes → purely synthetic, no fallback needed
5. quote_compare    → normal: {"recommendation": {vendor, amount}}
                   fallback: cheapest quote
6. guardrails       → normal: {"passed": true, "blocks": []}
                   fallback: passed (no guardrail module = no blocks)
7. dispatch         → purely synthetic, no fallback needed
8. work_complete    → purely synthetic, no fallback needed
9. payment          → normal: {"vendor_payout": 824.50}
                   fallback: simulated transfer
10. warranty       → normal: {"claim_generated": true}
                   fallback: {"skipped": true, "reason": "module unavailable"}
```

## Verification pattern

After building the orchestrator, test all urgency/input paths:

```bash
python3 agent.py "gas leak emergency"    # should produce EMERGENCY, ETA 30-60min
python3 agent.py "AC not cooling 87deg"  # should produce URGENT, ETA 2-4h
python3 agent.py "garbage disposal hum"  # should produce ROUTINE, ETA 24-48h
```

Each path should complete without crashes, with appropriate urgency classification, vendor dispatch, payment, and warranty handling.
