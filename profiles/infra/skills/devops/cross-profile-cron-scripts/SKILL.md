---
name: cross-profile-cron-scripts
description: Pitfalls when deploying cron scripts under non-default Hermes profiles.
triggers:
  - "deploying a script-based cron job with profile != default"
  - "script not found errors on cron runs"
  - "script runs fine locally but fails in cron"
---

# Cross-Profile Cron Script Deployment

When a cron job specifies `profile: <name>`, two things change that break naive assumptions:

## Pitfall 1: Script Path Resolution

The cron runner looks for scripts in `~/.hermes/profiles/<name>/scripts/`, **not** `~/.hermes/scripts/` (default profile).

**Fix:** Symlink or copy the script into the target profile's scripts dir:
```bash
ln -sf ~/.hermes/<project>/scripts/<script>.py \
       ~/.hermes/profiles/<name>/scripts/<script>.py
```

## Pitfall 2: `$HOME` Override

Hermes profiles override `$HOME` to the profile's own directory (e.g. `~/.hermes/profiles/oracle/home/`). Any script using `$HOME` or `os.path.expanduser("~")` to find files will look in the wrong place.

**Fix:** Never rely on `$HOME` in cron scripts. Use one of:
1. **Hardcoded absolute path** as default: `Path(os.environ.get("ORACLE_DIR", "~/.hermes/oracle"))`
2. **Env var** set in the cron job or profile .env

## Debugging "script not found" Failures

When a `no_agent` cron job errors with "script not found":

1. **Check which profile the job runs under:**
   ```bash
   # Look at the cron job config — profile field determines script resolution
   # cronjob list → find the job → check "profile" and "script" fields
   ```

2. **Verify the symlink exists in the RIGHT profile's scripts dir:**
   ```bash
   ls -la ~/.hermes/profiles/<profile>/scripts/<script>.py
   # NOT ~/.hermes/scripts/ (that's the default profile)
   ```

3. **Test the script manually:**
   ```bash
   python3 ~/.hermes/profiles/<profile>/scripts/<script>.py
   # If it errors on imports → install deps
   # If it errors on file paths → check $HOME issue (Pitfall 2)
   ```

4. **Check if `$HOME` is the issue:**
   ```bash
   # The profile's cron overrides $HOME to ~/.hermes/profiles/<profile>/home/
   # Any script using os.path.expanduser("~") or $HOME will look in the wrong place
   # Quick test: run with explicit HOME
   HOME=~ python3 ~/.hermes/profiles/<profile>/scripts/<script>.py
   ```

5. **Trigger a manual cron run to verify the fix:**
   ```bash
   # cronjob run <job_id> — then check last_status in cronjob list
   ```

## Checklist

When creating a `no_agent` script-based cron job with a custom profile:

- [ ] Script exists at `~/.hermes/profiles/<profile>/scripts/<name>` (not just the default profile)
- [ ] Script uses absolute paths (not `$HOME`) for all file references
- [ ] Script dependencies are installed (run it manually first)
- [ ] Manual test run produces no errors: `python3 ~/.hermes/profiles/<profile>/scripts/<name>.py`
- [ ] `cronjob run <id>` succeeds after deployment

## Related Skills

- `cron-pipeline` — overnight pipeline patterns, catch-up batches
- `hermes-agent` (protected) — profile architecture, script resolution
- `hermes-agent-skill-authoring` — has `references/skill-loading-architecture.md` covering how profiles affect script resolution at the code level
