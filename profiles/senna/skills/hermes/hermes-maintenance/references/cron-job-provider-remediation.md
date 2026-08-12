# Cron Job Provider/Model Remediation

## When to Use

When a cron job fails with:
- `RuntimeError: Skipped to prevent u...` (provider timeout)
- `Not supported model` (wrong endpoint for model)
- `404 Not Found` (model not on provider)
- `401 Unauthorized` (expired/stale credentials)

## Root Cause

Cron jobs store their `provider` and `model` at creation time. Changing
`config.yaml` does NOT update existing cron jobs. The job continues using
the stale provider/model until manually fixed.

## Fix

### Step 1: Identify the failing job

```bash
hermes cron list 2>&1 | grep -E "FAILED|error|Not supported"
```

Or check `jobs.json` directly:

```bash
python3 -c "
import json
with open('~/.hermes/profiles/senna/cron/jobs.json') as f:
    data = json.load(f)
for j in data['jobs']:
    if j.get('last_status') == 'error' or 'error' in str(j.get('last_error', '')):
        print(f\"{j['name']}: {j.get('last_error', 'N/A')[:100]}\")
"
```

### Step 2: Edit jobs.json

```python
import json, os
path = os.path.expanduser("~/.hermes/profiles/senna/cron/jobs.json")
with open(path) as f:
    data = json.load(f)

for job in data['jobs']:
    if 'HuggingNews' in job.get('name', ''):
        job['provider'] = 'custom'
        job['model'] = 'laguna-s-2.1'  # MUST be a plain string, not a dict

with open(path, 'w') as f:
    json.dump(data, f, indent=2, default=str)
```

### Step 3: Restart gateway

```bash
hermes gateway restart --profile senna
```

### Step 4: Re-trigger the job

```bash
hermes cron run <job_id>
```

## Pitfalls

- **model must be a plain string**, NOT a dict. `{'provider': 'x', 'model': 'y'}`
  causes `'dict' object has no attribute 'lower'` because the cron system calls
  `.lower()` on the model value.
- **`hermes cron edit` has no `--model` flag.** For model/provider changes,
  edit jobs.json directly. For schedule changes, use `--schedule`.
- **Scheduler may cache old config.** If re-triggering doesn't work, restart
  the gateway and try again.
- **Cron output accumulation.** Check `~/.hermes/cron/output/` for detailed
  error logs. Prune with `rm -rf ~/.hermes/cron/output/*` if large.

## Prevention

After changing a profile's provider in config.yaml, verify all cron jobs:

```bash
hermes cron list 2>&1 | grep -E "Provider:|model:"
```

If any job uses the old provider, update it before it fails.
