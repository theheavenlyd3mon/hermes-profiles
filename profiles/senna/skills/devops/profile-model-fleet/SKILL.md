---
name: profile-model-fleet
description: Current model assignments for all Hermes profiles (alibaba qwen3.8-max everywhere except senna+research on deepseek-v4-flash). Use to audit configs, diagnose auth errors, run batch fleet updates, or restart gateways after model changes.
version: 7.0.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [profile, model, alibaba, deepseek, qwen3.8-max, config, fleet, gateway]
    related: [kanban-orchestrator, hermes-multi-profile-config, gateway-fleet-ops]
---

# Profile Model Fleet — Current Assignments

Ground truth verified 2026-08-03 against every profile's config.yaml + `hermes profile list`.

## Providers in use

- **Alibaba DASHSCOPE** (`provider: alibaba`, `base_url: https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1`) — primary for all workers. Key: `DASHSCOPE_API_KEY` in `~/.hermes/.env`.
- **DeepSeek** (`provider: deepseek`, `base_url: https://api.deepseek.com`) — senna + research only.

## Profile → Model Map (2026-08-03)

### alibaba / qwen3.8-max (everything else — 22 profiles)
default, business, code, communication, creative, cyber-blue-cloud,
cyber-blue-compliance, cyber-blue-forensics, cyber-blue-soc, cyber-red,
educate, finance, gamehub-mod, homelab, infra, knowledge, media, mlops,
novel, secretary, security, social

### deepseek / deepseek-v4-flash (2 profiles)
senna, research

## Config Templates

Alibaba (default for workers):
```yaml
model:
  provider: alibaba
  default: qwen3.8-max
  base_url: https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
```

DeepSeek (senna, research):
```yaml
model:
  provider: deepseek
  default: deepseek-v4-flash
  base_url: https://api.deepseek.com
```

## Batch Update Procedure

When migrating many profiles at once, write a Python script and run via `terminal`:

```python
import os
profiles = {"creative": ("alibaba", "qwen3.8-max"), "social": ("alibaba", "qwen3.8-max")}
home = os.path.expanduser("~")
for profile, (provider, model) in profiles.items():
    cfg_path = f"{home}/.hermes/profiles/{profile}/config.yaml"
    with open(cfg_path) as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        s = line.strip()
        if s.startswith("provider:") and "model:" not in "".join(new_lines[-3:]):
            new_lines.append(f"  provider: {provider}\n")
        elif s.startswith("default:") and "model:" in "".join(new_lines[-3:]):
            new_lines.append(f"  default: {model}\n")
        else:
            new_lines.append(line)
    with open(cfg_path, 'w') as f:
        f.writelines(new_lines)
```

Then restart gateways for all affected profiles.

## Gateway Restart After Model Change

The **gateway process must be restarted** to pick up new model/provider config:

```bash
hermes --profile <name> gateway restart
# Or batch in background with notify_on_complete:
for p in code finance gamehub-mod infra knowledge novel research secretary security; do
  ~/.hermes/hermes-agent/venv/bin/python3 -m hermes_cli.main --profile $p gateway restart
done
```

**Critical:** Restart the current session's gateway LAST (or skip it) — restarting senna's gateway mid-run drops your live connection.

## Pitfalls

- **Config-drift guard skips unpinned cron jobs.** When the global inference config changes, any cron job without an explicit `model` pin fails with `RuntimeError: Skipped to prevent unintended spend`. Pin via `cronjob action=update job_id=<id> model=<model>`.
- **Gateway restart drain window.** Restart drains in-flight runs first (profile's `gateway_timeout`, default 180s). Batch restarts in background with `notify_on_complete=true`.
- **Profile HOME path mismatch.** Cron sessions override `$HOME` to the profile home. Use absolute paths in scripts.
- **Not all profiles need Discord gateways.** Only profiles with `DISCORD_BOT_TOKEN` in their `.env` can run gateways. Current running fleet (11): senna, creative, code, finance, gamehub-mod, infra, knowledge, novel, research, secretary, security.
- **Cron delivery uses default profile's Discord client.** A job with `profile: X` and `deliver: discord:<channel>` posts from Senna's bot. Fix: `deliver: local` + DELIVERY OVERRIDE in prompt (see `cron-pipeline`).

## References

- `references/model-pricing-watchdog.md` — Sunday pricing watchdog procedure.
- `references/profile-key-inheritance.md` — how profiles inherit API keys from `~/.hermes/.env`.
