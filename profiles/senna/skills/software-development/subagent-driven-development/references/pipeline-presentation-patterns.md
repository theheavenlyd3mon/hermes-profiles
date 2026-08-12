# Pipeline Presentation Patterns

After building a pipeline orchestrator (`agent.py`), you need a way to show it working — either as a live demo or a recorded submission. This reference covers two patterns for presenting pipeline results.

## Pattern 1: Timed CLI Reveal

A standalone script that runs the pipeline and displays each phase with a timed delay, colored output, and visual separation. Works for recorded demos where you narrate over the output.

### Structure

```python
# demo.py — Imports the pipeline orchestrator and reveals stages

def run_demo(report: str):
    os.system("clear")
    print(f"{C.BOLD}  ⌘  PROJECT NAME — Interactive Demo{C.RESET}")

    result = asyncio.run(run_pipeline(report))
    phases = result.get("phases", {})

    # Show each phase with a title, step message, and timed delay
    title("📋 PHASE 1 — Step Name", C.BLUE)
    step("🧠", "AI describes what it's doing...")
    ok("Key result")
    time.sleep(1.5)

    # ... repeat for each phase ...

    # End with a summary card
    hr("═", C.GREEN)
    print(f"  Pipeline Complete ✅")
    print(f"     Key metric 1:    value")
    print(f"     Key metric 2:    value")
```

### Color conventions

Use a consistent color palette so phases are visually distinguishable:

| Element | Color | Use |
|---------|-------|-----|
| Phase headers | `C.BLUE` | Title bar for each phase |
| Success | `C.GREEN` | Checkmarks, OK messages, money amounts |
| Warnings | `C.YELLOW` | Fallback paths, cautions |
| Errors | `C.RED` | Failures, blocked states |
| Urgency badges | `C.RED`/`C.YELLOW`/`C.GREEN` | EMERGENCY / URGENT / ROUTINE |
| Secondary text | `C.DIM` or `C.GREY` | IDs, timestamps, notes |
| Highlights | `C.BOLD` | Vendor names, amounts, key values |
| Accent | `C.PURPLE` | Project title, branding |

### Pitfall — `asyncio.run()` inside an async context

If your `demo.py` is itself an `async def` (because it awaits things like `os.system` alternatives or other coroutines), you **cannot** call `asyncio.run(pipeline)` inside it. Python raises:

```
RuntimeError: asyncio.run() cannot be called from a running event loop
```

**Fix:** If `demo.py`'s entry point is already `asyncio.run(run_demo(...))`, then inside `run_demo` just `await` the pipeline directly:

```python
# Wrong — inside an async function
result = asyncio.run(run_pipeline(report))   # RuntimeError

# Right — inside an async function
result = await run_pipeline(report)
```

**Check:** Does `demo.py` call `asyncio.run()` only once at the bottom (`__main__` block), and use `await` everywhere else? If it calls `asyncio.run()` from inside an `async def`, that's a bug.

### Timing

Each phase should have a distinct delay (0.3s-1.5s) so the audience has time to read. Shorter delays for simple steps (quote received, warranty checked), longer for steps that "take time" (AI processing, dispatch, payment):

```python
def step(icon, label, detail="", delay=0.8):
    time.sleep(delay)
    print(f"\n  {icon}  {C.BOLD}{label}{C.RESET}")
    if detail:
        for line in detail.split("\n"):
            print(f"     {C.DIM}{line}{C.RESET}")
```

### Helper functions

Standardize on a few helpers:

```python
def hr(char="-", color=C.GREY):
    """Horizontal rule spanning terminal width."""
    print(f"{color}{char * terminal_width}{C.RESET}")

def title(text, color=C.BOLD):
    """Phase header with full-width rule above and below."""
    hr("=", color)
    print(f"{color}{' ' * 2}{text}{C.RESET}")
    hr("=", color)

def ok(text):
    print(f"     {C.GREEN}v{C.RESET} {text}")

def warn(text):
    print(f"     {C.YELLOW}!{C.RESET} {text}")

def badge(text, color=C.PURPLE):
    return f"{color}{C.BOLD}{text}{C.RESET}"

def money(amount):
    return f"{C.GREEN}${amount:,.2f}{C.RESET}"
```

---

## Pattern 2: Web UI with Animated Timeline

A browser-based portal where a user submits input and sees the pipeline phases animate in sequence. Works for live interactive demos where audience members can try the system.

### Architecture

```
Browser HTML form  --POST-->  FastAPI /api/run-pipeline
                                    |
                              Pipeline orchestrator
                              (agent.run_pipeline())
                                    |
                              JSON result dict
                                    |
Browser animates phases  <--  JSON response
```

### FastAPI endpoint

```python
@app.post("/api/run-pipeline")
async def run_pipeline(data: dict):
    issue = data.get("issue", "")
    from agent import run_pipeline as agent_run
    result = await agent_run(issue, state="CA", zip_code="94102")
    return result
```

### Frontend HTML structure

The page has three sections:

1. **Form** -- Address, unit, issue textarea, notes, quick-fill buttons, submit
2. **Timeline** -- Hidden initially, shown on submit. 10 phase rows, each with:
   - Indicator dot (spinning to green check or red X)
   - Icon (brain for triage, wrench for vendors, card for payment)
   - Title line
   - Detail line (filled in when phase completes)
3. **Summary card** -- Appears after all phases complete with key metrics

### Phase timeline state machine

Each phase element has three visual states via CSS classes:

```css
.phase { opacity: 0.3; }                  /* Waiting */
.phase.active { opacity: 1; }            /* Currently processing */
.phase.done { opacity: 0.8; }            /* Completed */
.phase.failed { opacity: 1; }            /* Error */
```

Active state has a pulsing animation. Done gets a green checkmark. Failed gets a red X.

### Frontend animation logic

```javascript
const PHASES = [
  { id: 'triage', icon: 'brain', label: 'Triage' },
  { id: 'habitability', icon: 'clock', label: 'Habitability' },
];

async function animatePipeline(data) {
  const p = data.phases || {};

  setPhaseActive('triage');
  await sleep(800);
  setPhaseDone('triage', urgency + ' - ' + trade);

  setPhaseActive('habitability');
  await sleep(600);
  setPhaseDone('habitability', deadline_hours + 'h deadline');

  await sleep(300);
  showSummary(data);
}
```

The delays simulate processing time -- the audience sees each phase being "worked on" before results appear.

### Quick-fill demo buttons

Pre-populate the form with common scenarios so presenters can click one button instead of typing:

```html
<button onclick="fillDemo('123 Main St', '3B', 'AC not cooling, 87 degrees, newborn')">
  AC + Newborn
</button>
<button onclick="fillDemo('123 Main St', '3B', 'I smell gas in the kitchen')">
  Gas Leak
</button>
```

### Summary card

After the timeline completes, show a summary card with key metrics from each phase:

| Row | Source field | Display |
|-----|-------------|---------|
| Status | triage.urgency | Badge (EMERGENCY / URGENT / ROUTINE) |
| Issue type | triage.trade_needed | e.g. "HVAC Technician" |
| Habitability | habitability.deadline_hours | e.g. "24h deadline in CA" |
| Vendor | quote_comparison.recommendation | e.g. "CoolTech HVAC -- $850" |
| Guardrails | guardrails.passed | Passed / Blocked |
| Dispatch ETA | dispatch.eta | e.g. "2-4 hours" |
| Vendor payout | payment.vendor_payout | e.g. "$824.50" |
| Commission | payment.commission_amount | e.g. "+$25.50" |
| Warranty | warranty.claim_generated | Claim filed / reason |
| Elapsed time | elapsed_seconds | e.g. "0.5s" |

---

## When to use each pattern

| Pattern | Best for | Requirements |
|---------|----------|-------------|
| CLI Reveal | Recorded video demos, presenting on stage with projection | Terminal with Python + venv |
| Web UI | Live interactive demos, letting audience try it | FastAPI server running |

Both patterns can coexist -- the same agent.run_pipeline() function backs both.
