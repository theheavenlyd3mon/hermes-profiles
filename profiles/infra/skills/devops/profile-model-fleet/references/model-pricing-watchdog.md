# Model Pricing Watchdog

Automated cross-provider model pricing watcher that detects changes across Nous Portal, NVIDIA NIM, and OpenRouter.

## Script location

```
~/.hermes/profiles/senna/scripts/model-pricing-watcher.py
```

## What it checks

| Provider | Models | Auth method | Real pricing? |
|----------|--------|-------------|---------------|
| **Nous Portal** | 408 | `agent_key` from `~/.hermes/auth.json` credential pool | Partial (some $0.0000) |
| **NVIDIA NIM** | 125 | `NVIDIA_API_KEY` from `~/.hermes/.env` | No (all $0.0000 in list) |
| **OpenRouter** | thousands | None needed for list | Yes — real `:free` tags |

## What it reports

- **New free models** — models that appeared since last snapshot with $0.0000 pricing (or `:free` suffix on OpenRouter)
- **Free → paid reversions** — models that used to be free and now cost something
- **Free models removed** — free models that disappeared from the catalog entirely
- **Fleet model price changes** — any of the actively-used fleet models changed price

**If nothing changed:** outputs `✓ Model pricing check — no changes`

## Cron schedule

Weekly, Sundays at 9am:

```bash
0 9 * * 0
```

Job name: `model-pricing-watchdog` (managed via `cronjob()` tool)

## Snapshot data

```
~/.hermes/model-pricing-snapshot.json
```

Each run saves the full model catalog as JSON with pricing + metadata. Comparison is done against this snapshot on the next run.

## Key gotchas

- **NVIDIA list endpoint returns $0.0000 for everything** — real NVIDIA pricing requires checking the pricing page or making actual completion calls. The watchdog treats NVIDIA models with $0.0000 as "free" which is likely inaccurate. NVIDIA pricing detection is approximate.
- **Hermes sandbox:** When the script runs as a cron job, `~/.hermes/` resolves to the sandboxed profile directory, not the real home. The script uses `~` directly for auth.json and .env paths.
- **OpenRouter `:free` suffix:** Free-tier OpenRouter models are suffixed with `:free` and detected via pricing=0.0000. These are genuinely free (rate-limited).
