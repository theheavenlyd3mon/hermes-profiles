# Environment Context Injection

## The Problem

Hermes agents running on macOS can confuse the current host environment with
other machines the user owns (e.g., a Windows PC with an your GPU for UE5
work). This happens because `environment_probe: true` is set in config.yaml but
`environment_hint: ''` is empty — there is no persistent context telling the
agent which machine it is currently running on.

## Root Cause

The `agent.environment_probe` config flag enables environment detection, and
`agent.environment_hint` is the field where a human-readable environment
description should be stored. When `environment_hint` is empty, the agent has
no structured way to distinguish "I am on a MacBook" from "I am on the Windows
PC."

## The Fix

### Option 1: Set environment_hint in config.yaml

```yaml
agent:
  environment_probe: true
  environment_hint: "macOS 15.7.7 — MacBook Pro — primary development machine. Windows PC (your GPU, UE 5.7) is a separate machine for UE5/Murim Souls work. Do NOT reference Windows paths or UE5 work unless the task explicitly involves the Windows machine."
```

### Option 2: Set environment_hint via CLI

```bash
hermes config set agent.environment_hint "macOS 15.7.7 — MacBook Pro — primary development machine. Windows PC (your GPU, UE 5.7) is a separate machine for UE5/Murim Souls work."
```

## Verification

After setting the hint, verify it's loaded:

```bash
hermes config | grep -A2 "Environment"
```

Then `/reset` to start a new session. The agent should now correctly identify
which machine it's running on and avoid referencing the wrong environment.

## When to Update

Update `environment_hint` when:
- The user adds a new machine to their fleet
- The user changes their primary development machine
- The user changes the OS version (major upgrade)
- The user reports environment confusion again

## Related Config Fields

- `agent.environment_probe` — enables environment detection (boolean)
- `agent.environment_hint` — human-readable environment description (string)
- `agent.coding_context` — auto-detected coding context (auto | file | project)
- `terminal.cwd` — working directory for terminal commands
