# LLM Free-Text Classification Aliasing

## The Problem

AI models like Nemotron 3 Ultra often return free-text classification labels instead of canonical enum values. For example, a triage prompt asking for `trade_needed` returns:

- `"HVAC technician (licensed)"` instead of `"HVAC"`
- `"Licensed plumber (gas certified) or gas utility emergency response"` instead of `"Plumbing"`
- `"plumber or appliance repair technician"` instead of `"Plumbing"`

A strict equality check (`if trade == "Plumbing"`) fails, and the pipeline silently breaks because no vendor is matched.

## The Pattern: Substring-Based Alias Map

Use a multi-strategy normalization chain that falls back gracefully:

```python
# Step 1: Strip known noise suffixes
raw = triage_result.get("trade_needed", "")
clean = raw.replace(" Technician", "").replace(" Specialist", "").replace(" / ", "/").split("/")[0].strip()

# Step 2: Substring alias matching (catches "plumber" in "Licensed plumber...")
lower = clean.lower()
if any(k in lower for k in ("plumber", "appliance repair", "gas certified", "gas utility")):
    result = "Plumbing"
else:
    # Step 3: Canonical set membership (exact match on known values)
    result = clean if clean in {"HVAC", "Plumbing", "Electrical", "Structural", "Pest"} else fallback
```

## When to Use

Apply this pattern whenever an LLM classifies input into categories and returns natural language instead of constrained output. This is common with:

- Free-text classification prompts (no constrained `response_format`)
- Models without structured output support (some OpenRouter free-tier models)
- Apps that must work offline/demo mode without API

## Multi-Stage Fallback Chain

| Stage | Strategy | Example Match |
|-------|----------|---------------|
| 1 | Strip role suffixes | `"HVAC Technician"` → `"HVAC"` |
| 2 | Substring alias map | `"gas certified plumber"` → `"Plumbing"` |
| 3 | Canonical set membership | `"HVAC"` → `"HVAC"` |
| 4 | Hard default | Any miss → `"HVAC"` (or best guess) |

## Anti-Patterns

- **Single regex** — LLM output varies too much for a single pattern. Substring matching on multiple keywords is more robust.
- **LLM re-classify** — Don't call the LLM again just to normalize its own output. Use deterministic string matching.
- **Fuzzy string matching** — Levenshtein/Jaro-Winkler is overkill and can produce wrong results. Keyword substring matching is simpler and more predictable.
- **Exact match only** — Fails on the first unexpected output variation.

## Verification Pattern

After applying the alias map, test with a range of real LLM outputs collected from previous runs:

```python
test_cases = [
    ("HVAC technician (licensed)", "HVAC"),
    ("Licensed plumber (gas certified)", "Plumbing"),
    ("plumber or appliance repair technician", "Plumbing"),
    ("emergency_gas_utility_or_fire_department", "Plumbing"),  # underscores from different model behavior
    ("HVAC (primary), electrician (if electrical)", "HVAC"),
]
for raw, expected in test_cases:
    # normalize(raw) → should match expected
```
