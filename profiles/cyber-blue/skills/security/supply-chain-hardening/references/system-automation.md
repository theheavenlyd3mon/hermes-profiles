# System-Specific Automation — Supply Chain Guards

Deployed on this Hermes installation (macOS, ~noctis) on 2026-05-12.

## Active Guards

### 1. Shell Wrapper — `~/.hermes/scripts/supply-chain-guard.sh`

Sourced from `~/.zshrc`. Wraps `npm`, `pnpm`, and `yarn` shell commands:

- Checks a lockfile exists before allowing any install
- Automatically appends `--ignore-scripts` to install commands
- Prompts user confirmation if no lockfile is found

**Files:**
- Script: `~/.hermes/scripts/supply-chain-guard.sh`
- Activation: `~/.zshrc` line `source ~/.hermes/scripts/supply-chain-guard.sh`

**To manually activate** (if a new shell doesn't source it):
```bash
source ~/.hermes/scripts/supply-chain-guard.sh
```

### 2. Git Post-Clone Hook — `~/.git-templates/hooks/post-checkout`

Scans every cloned/checked-out repo for:
- `router_init.js`, `tanstack_runner.js`, `router_runtime.js`, `vite_setup.mjs`
- `.claude/setup.mjs`, `.claude/settings.json`
- `.vscode/setup.mjs`, `.vscode/tasks.json`
- `.cursor/` poisoned configs

**Hook script:** `~/.hermes/scripts/post-clone-scan.sh`

**Template location:** `~/.git-templates/hooks/post-checkout`

**Applied to:** All existing repos under `~/` (`find ~ -name ".git" -type d` populated on setup)

**New repos/clones:** Auto-inherited via `git config --global init.templateDir ~/.git-templates`

### 3. Cron Job — `supply-chain-advisory-check`

Runs daily at 9 AM local time. Uses **no_agent mode** with a shell script for reliability.

**Script:** `~/.hermes/profiles/senna/scripts/supply-chain-scan.sh`

What it does:
- Runs `npm audit --audit-level=critical` on known project directories: HermesMirror (`~/projects/HermesMirror`) and hermes-office (`~/.hermes/hermes-office`)
- Reports findings only when vulnerabilities are found (silent = clean)
- No agent context loaded — just `bash`, `npm`, and `cd`

**Cron ID:** `5d3366224d17`
**Schedule:** `0 9 * * *`
**Mode:** `no_agent=true` (no skill loading, no LLM call)
**Script:** `supply-chain-scan.sh` (resolved under profile's scripts/)

**Why no_agent?** The original agent-based cron job errored repeatedly (likely tool/skill-loading timeouts in short-lived cron sessions). The no_agent + script pattern is more robust for deterministic, scriptable checks where you don't need LLM reasoning — the script runs, outputs any findings, and the scheduler delivers them verbatim.

**When to revert to agent-based:** If you need web research integration (e.g. checking npm advisory feed), add a companion agent-based job for that and keep the scan in no_agent mode. The two concerns — local audit vs. external research — have different reliability profiles.

## Verification

Run `scripts/verify-guards.sh` to check all three layers are active. See that script for exact commands.

## Limitations

- Shell wrapper only activates in new interactive Zsh sessions (not in subprocesses or non-interactive shells)
- Post-clone hook requires git template directory config to persist across git version updates
- Cron job only fires once daily; doesn't catch same-day zero-days until the next run
