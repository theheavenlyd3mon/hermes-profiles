---
name: hermes-security-hardening
description: Comprehensive security hardening for Hermes installations — fixes permissions, sets up secret scanning, configures macOS Keychain integration, creates security policies, and installs pre-commit hooks.
triggers:
  - "security audit"
  - "harden hermes"
  - "fix permissions"
  - "security review"
  - "hermes vulnerability assessment"
---

IDENTITY: Hardener.Sysadmin. Execute security hardening — fix file permissions, install secret-scanning hooks, migrate to macOS Keychain, create security policy, and set up automated prevention. Action-first, report-after.
Law: AlwaysUseAbsolutePaths — macOS terminal tool's ~ resolution is unreliable for file operations.
WHENUSE: InitialSetup|AfterExposedSecretsFound|PeriodicHardening{weekly,monthly}|ComplianceRequirement. ESPECIALLY:WorldReadableEnvFiles|NoSecretScanningOnCommit|PlaintextKeysInDotEnv. NoSkip:PostChangeVerification{statPermissions,gitleaksScan,npmAudit}.
REDFLAGS: cp~pathFailsSilently->Use/$USER/absPath|hermesConfigGetReturnsEmpty->grepConfigDirectly|Gitleaks--pipeFlagFails->Use--no-gitWith--source|PreCommitHookNotFiring->CheckExecutable+core.hooksPath|KeychainSecretsNotLoading->CheckAccountName+ReAdd.
RATIONALIZATIONS: BashVsPython->BashFasterNoFstringIssues|GitleaksVsTruffleHog->GitleaksFasterBetterTOML|NoAutomaticKeyRotation->UserWantsMonitoringFirst.
QUICKREF: Map{ActiveEnvFiles{findNotArchive}->WhichEnvLoaded{hermes config}}->Audit{Permissions,SecretsExposed,NetworkExposure,ConfigPrivacy{redact_secrets,redact_pii,approvals.mode}}->Create{SecDir{scripts+gitleaks+precommit+policy+keychainLoader}}->Apply{chmod600,gitleaks,precommit,keychain}->Verify{Stats,gitleaksScan,banditScan,npmAudit,KeychainLoad,PreCommitTest}.

## Overview

This skill automates comprehensive security hardening for a Hermes installation. It addresses the three critical areas:

1. **File Permissions** — `.env` files to `600`, `.git` directories to remove world access
2. **Secret Management** — migrates from plaintext `.env` to macOS Keychain, provides loader script
3. **Prevention** — installs gitleaks pre-commit hooks, creates security policy, builds automated remediation

## When to Use

- Initial Hermes installation security setup
- After discovering exposed secrets or weak permissions
- Periodic security hardening (weekly/monthly)
- Auditing a Hermes installation for compliance

## Prerequisites

- macOS (uses `security` CLI for Keychain)
- Hermes installed in standard locations: `~/.hermes/`, `~/hermes-webui/`, `~/hermes-workspace/`
- User has write permissions to all Hermes directories
- Shell: `zsh` or `bash`

## What This Skill Creates

```
~/.hermes/security/
├── harden-hermes.sh              (primary — bash, idempotent)
├── harden-hermes-security.py     (fallback — Python)
├── install-all.sh                (one-command fresh install)
├── pre-commit.template           (gitleaks hook source)
├── .gitleaks.toml.template       (gitleaks config)
├── SECURITY_POLICY.md            (full security policy)
├── README.md                     (quick reference)
└── HARDENING_SUMMARY.md          (run summary)

~/.hermes/load-keychain-secrets.sh   (keychain loader — source in shell)
~/hermes-webui/.gitleaks.toml         (active gitleaks config)
~/hermes-webui/.git/hooks/pre-commit  (active pre-commit hook)
```

## Execution Approach

This user prefers **action-first, explanation-after**. Do not list options or ask "which do you want to do?" — instead, execute the full set of changes, then deliver a structured report explaining what changed and how each control works. Verify each change after applying it and include the verification result in the report. This preference applies to all security-hardening sessions unless the user explicitly asks for a plan first.

## Step-by-Step Process

### Step 0: Map the Active .env Files

Before hardening, identify which `.env` files actually carry active credentials. The skill's template references `archive/.env` but that's a state-snapshot directory — not active config.

```bash
# Find all active .env files (exclude archive and home/ subdirectories)
find ~/.hermes -name ".env" -not -path "*/home/*" -not -path "*/state-snapshots/*" -not -path "*/archive/*"

# Check which .env is loaded by the current profile
hermes config | grep "Secrets:"
```

**Likely targets:**
- `~/.hermes/.env` — root, shared across profiles (often the primary threat)
- `~/.hermes/profiles/<name>/.env` — profile-specific overrides

### Step 1: Audit Current State

Scan to identify issues before fixing:

```bash
# Check .env file permissions (use ABSOLUTE paths — macOS ~ resolution bug)
ls -la /Users/$USER/.hermes/.env /Users/$USER/.hermes/profiles/senna/.env
stat -f "%A %N" /Users/$USER/.hermes/.env /Users/$USER/.hermes/profiles/senna/.env

# Check git directory world-access
namei -l /Users/$USER/hermes-webui/.git /Users/$USER/hermes-workspace/.git 2>/dev/null

# Check for exposed secrets in files
grep -r "api_key\|token\|password\|HERMES.*KEY\|OPENROUTER\|ANTHROPIC\|DEEPSEEK\|GITHUB" ~/.hermes/.env ~/.hermes/profiles/senna/.env 2>/dev/null

# Check network exposure
lsof -i -n -P | grep -E '8787|8642'

# Check current config values for privacy/security toggles
grep -n "redact_secrets\|redact_pii\|approvals.mode\|mode:" /Users/$USER/.hermes/profiles/senna/config.yaml | head -10
```

Expected findings before fix:
- `.env` files: `-rw-r--r--` (644) — world-readable ❌
- `.git` dirs: `drwxr-xr-x` (755) — world-traversable ❌
- Secrets in plaintext ❌
- `redact_pii: false` — PII exposed in gateway context ❌
- `approvals.mode: manual` — prompts on every flagged command ❌

### Step 2: Create Security Directory Structure

```bash
mkdir -p ~/.hermes/security
```

All artifacts live here for version control and backup.

### Step 3: Build the Hardening Script (Bash — Recommended)

Create `~/.hermes/security/harden-hermes.sh`:

```bash
#!/usr/bin/env bash
set -e

echo "🔐 Hermes Security Hardening"
echo "============================"

# 1. Fix .env perms (root + active profile — NOT archive/ which is state snapshots)
chmod 600 ~/.hermes/.env 2>/dev/null && echo "✓ ~/.hermes/.env" || echo "- not found"
chmod 600 ~/.hermes/profiles/senna/.env 2>/dev/null && echo "✓ profile .env" || echo "- not found"

# 2. Fix git dirs (remove world access — all repos that contain Hermes code)
chmod -R o-rwx ~/hermes-webui/.git 2>/dev/null && echo "✓ ~/hermes-webui/.git" || echo "- not found"
chmod -R o-rwx ~/hermes-workspace/.git 2>/dev/null && echo "✓ ~/hermes-workspace/.git" || echo "- not found"

# 3. Install tools
brew install gitleaks 2>/dev/null && echo "✓ gitleaks" || echo "⚠ gitleaks may already be installed"
pip install bandit safety 2>/dev/null && echo "✓ bandit, safety" || echo "⚠ pip install failed"

# 4. Configure gitleaks (if missing)
if [ ! -f ~/hermes-webui/.gitleaks.toml ]; then
    cp ~/.hermes/security/.gitleaks.toml.template ~/hermes-webui/.gitleaks.toml 2>/dev/null || true
fi

# 5. Install pre-commit hooks in ALL Hermes repos
for repo in ~/hermes-webui ~/hermes-workspace; do
    if [ -d "$repo/.git" ]; then
        cp ~/.hermes/security/pre-commit.template "$repo/.git/hooks/pre-commit" 2>/dev/null || true
        chmod +x "$repo/.git/hooks/pre-commit" 2>/dev/null || true
        echo "✓ pre-commit hook installed: $repo"
    fi
done

echo "✅ Done!"
```

**Rationale for bash over Python:** Bash avoids f-string formatting issues (experienced), uses native `chmod`, simpler error handling with `||`, and runs faster without interpreter overhead. Keep Python version as fallback for complex logic extensions.

Make it executable:
```bash
chmod +x ~/.hermes/security/harden-hermes.sh
```

### Step 4: Create the Pre-commit Hook

**Hook file:** `~/.hermes/security/pre-commit.template`

```bash
#!/usr/bin/env bash
# Hermes Pre-commit Hook — blocks secret leakage

if command -v gitleaks &>/dev/null; then
    echo "🔍 Scanning for secrets with gitleaks..."
    if ! gitleaks detect --source="$(git rev-parse --show-toplevel)" --no-git -v 2>/dev/null; then
        echo "❌ Commit blocked: secrets detected!"
        exit 1
    fi
fi

# Optional: bandit for Python files
if command -v bandit &>/dev/null; then
    STAGED_PY=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
    if [ -n "$STAGED_PY" ]; then
        echo "🔍 Scanning Python files with bandit..."
        echo "$STAGED_PY" | xargs bandit -r 2>/dev/null || true
    fi
fi

exit 0
```

**Install pre-commit hooks to BOTH repos (workspace AND webui):**
```bash
# Use ABSOLUTE paths — macOS terminal tool may not resolve ~ correctly for cp
cp /Users/$USER/.hermes/security/pre-commit.template /Users/$USER/hermes-webui/.git/hooks/pre-commit
cp /Users/$USER/.hermes/security/pre-commit.template /Users/$USER/hermes-workspace/.git/hooks/pre-commit
chmod +x /Users/$USER/hermes-webui/.git/hooks/pre-commit /Users/$USER/hermes-workspace/.git/hooks/pre-commit
```

**Note:** Pre-commit hooks are per-repo, not global. You must install in each Hermes component repo separately. Don't forget `hermes-workspace` — the skill's original examples only show `hermes-webui`. Document this in policy.

### Step 5: Configure Gitleaks

Create `~/.hermes/security/.gitleaks.toml.template`:

```toml
[extend]
useDefault = true

[allowlist]
description = "Allowlist for Hermes codebase"
regexTarget = "line"
regexes = [
    # HERMES_WEBUI_PORT=8787 — allowed
    'HERMES_WEBUI_PORT=\d+',
    # HERMES_WEBUI_HOST=127.0.0.1 — allowed
    'HERMES_WEBUI_HOST=',
    # OBSIDIAN_VAULT_PATH — allowed
    'OBSIDIAN_VAULT_PATH=',
]

# Custom rules for your secret patterns
[[rules]]
id = "hermes-exposed-api-key"
description = "Detect exposed API keys in .env files"
regex = '''(?i)(api[_-]?key|token|secret|password)\s*=\s*["']?[A-Za-z0-9_\-]{20,}["']?'''
tags = ["key", "secret"]
```

Copy to active repo:
```bash
cp ~/.hermes/security/.gitleaks.toml.template ~/hermes-webui/.gitleaks.toml
```

### Step 6: Create Keychain Loader

**File:** `~/.hermes/load-keychain-secrets.sh`

```bash
#!/usr/bin/env bash
# Load Hermes secrets from macOS Keychain into environment variables
# Source this in your shell: source ~/.hermes/load-keychain-secrets.sh

KEYCHAIN_SERVICE="hermes-secrets"

# Function to load a secret by account name
_load_secret() {
    local account="$1"
    local varname="$2"
    local secret
    secret=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -a "$account" -w 2>/dev/null)
    if [ -n "$secret" ]; then
        export "$varname=$secret"
        echo "✓ Loaded $account → $varname"
    else
        echo "⚠ $account not found in keychain"
    fi
}

# Load all Hermes secrets
_load_secret "openrouter-api-key" "OPENROUTER_API_KEY"
_load_secret "github-token" "GITHUB_TOKEN"

# Unset helper function
unset -f _load_secret
```

Make executable:
```bash
chmod +x ~/.hermes/load-keychain-secrets.sh
```

**Add to shell profile:**
```bash
echo 'source ~/.hermes/load-keychain-secrets.sh' >> ~/.zshrc
source ~/.zshrc
```

### Step 7: Create Security Policy

**File:** `~/.hermes/security/SECURITY_POLICY.md`

Structure:
- **Section 1 — Overview**: Security principles (least privilege, defense in depth)
- **Section 2 — Secrets Management**: Mandatory Keychain storage, `.env` only for non-secrets
- **Section 3 — File Permissions**: Matrix of required modes (`.env=600`, `.git=700`)
- **Section 4 — Network Security**: Binding policy (`127.0.0.1` default, external needs approval)
- **Section 5 — Code Security**: Prohibited patterns (`exec()`, `pickle.load()`, `shell=True`)
- **Section 6 — Access Control**: Non-root execution, user isolation
- **Section 7 — Monitoring & Incident Response**: Log review schedule, key monitoring
- **Section 8 — Regular Maintenance**: Weekly/monthly/quarterly checklists
- **Section 9 — Security Checklist**: New install verification
- **Section 10 — Compliance & Exceptions**: How to document deviations
- **Section 11 — Contact & Resources**: Tool references
- **Section 12 — Quick Reference Commands**: One-liners

**Key policy decisions to document:**
- External API binding (`0.0.0.0`) is allowed but requires firewall justification
- Secrets: Keychain only, never plaintext `.env`
- No TLS for localhost (acceptable risk for single-user)
- Key rotation: OpenRouter 90d, GitHub 180d (monitor instead, user discretion)

### Step 8: Add Secrets to Keychain

User executes (manual — cannot automate secret entry):

```bash
security add-generic-password -a openrouter-api-key -s hermes-secrets -w "sk-or-actual-key-here"
security add-generic-password -a github-token -s hermes-secrets -w "ghp_actual-token-here"
```

Verify (values hidden):
```bash
security find-generic-password -s hermes-secrets -g
```

**Important:** The `security` CLI prompts for keychain access on first use. User must allow.

### Step 9: Verify Everything

Run comprehensive checks:

```bash
# 1. Permissions — check ACTIVE .env files, not archive/ snapshots
stat -f "%A %N" ~/.hermes/.env ~/.hermes/profiles/senna/.env 2>/dev/null     # → 600
ls -ld ~/hermes-webui/.git             # → drwx------ (no world bits)

# 2. Secret scanning
gitleaks detect --source=~/hermes-webui
gitleaks detect --source=~/hermes-workspace

# 3. Python security scan
bandit -r ~/hermes-webui/api

# 4. Dependency check
cd ~/hermes-workspace && npm audit --audit-level=moderate

# 5. Keychain loading
source ~/.hermes/load-keychain-secrets.sh
echo $OPENROUTER_API_KEY  # should show (if added)

# 6. Pre-commit test
cd ~/hermes-webui
git add -A  # should run gitleaks and pass if no secrets
```

### Step 10: Set Up Weekly Automation (Optional)

Cron job to re-harden weekly:

```bash
crontab -e
# Add:
0 3 * * 0 ~/.hermes/security/harden-hermes.sh >/dev/null 2>&1
```

Or use Hermes's built-in cron (if available):
```bash
# In hermes config
cronjob(action='create', schedule='0 3 * * 0', prompt='Run Hermes security hardening', skills=['hermes-security-hardening'])
```

## Pitfalls & Solutions

### Problem: macOS '~' path resolution in terminal tool

**Symptom:** `cp ~/.hermes/security/pre-commit.sh …` fails silently or copies to a wrong location, even though other commands (like `ls -la`) work fine with tilde paths. The file "exists at abs path" when checked with `/Users/$USER/...` but `cp ~/...` errors with "No such file or directory."

**Cause:** The Hermes terminal tool runs without a full shell environment, so `~` may resolve differently (or to a subdirectory like `~/.hermes/profiles/senna/home/.hermes/`) than in an interactive terminal.

**Fix:** Always use absolute paths (`/Users/$USER/...`) for file operations — especially `cp`, `mv`, `chmod`, and `stat`:

```bash
# DO — use absolute paths
cp /Users/$USER/.hermes/security/pre-commit.sh /Users/$USER/hermes-webui/.git/hooks/pre-commit

# DON'T — may fail or resolve to wrong directory
cp ~/.hermes/security/pre-commit.sh ~/hermes-webui/.git/hooks/pre-commit
```

For read-only commands (`ls`, `grep`, `cat`), tilde often works fine. For destructive/copy operations, always resolve the full path.

### Problem: Config change not verifiable via `hermes config get`

**Symptom:** `hermes config get approvals.mode` returns empty output or exit code 2, even though the value is set in config.yaml.

**Cause:** `hermes config get` only recognizes a subset of config keys. Privacy/security sub-keys (under `privacy:`, `security:`, `approvals:`) may not be exposed via this interface.

**Fix:** Use `grep` directly on the config file:

```bash
grep -n "redact_secrets\|redact_pii\|approvals.mode\|mode:" /Users/$USER/.hermes/profiles/senna/config.yaml
```

This is more reliable than `hermes config get` for nested config sections.

### Problem: Gitleaks `--pipe` flag (v8.x)

**Symptom:** Running `gitleaks detect --no-git --pipe` fails with "unknown shorthand flag" or hangs scanning large directories.

**Cause:** Gitleaks v8.x changed its stdin handling. The `--pipe` flag is for reading from stdin (e.g., `cat file | gitleaks detect --pipe`). The `--no-git` flag treats the source as a regular directory. In a pre-commit hook context, use `--no-git` with a `--source` pointing to the repo root — don't pipe into it.

**Fix in pre-commit hooks:** The hook should use `--no-git` with `--source` set to `$(git rev-parse --show-toplevel)`:
```bash
gitleaks detect --source="$(git rev-parse --show-toplevel)" --no-git -v
```

**Symptom:** `SyntaxError: f-string: missing '}'` or similar when running Python hardening script.

**Cause:** In Python 3.11 and earlier, f-strings cannot contain backslash-escaped expressions that span lines. The original script had `f"  ✓ {f} -> {oct(expected_perm)}"` on a single line but the `{f}` variable came from a loop that used path objects with backslashes in string formatting.

**Solution:** Switch to bash for the primary hardening script (simpler, no f-string issues). If Python is required, replace f-strings with concatenation:
```python
log("  ✓ " + str(f) + " -> " + oct(expected_perm), "OK")
```
Or use `.format()`:
```python
log("  ✓ {} -> {}".format(f, oct(expected_perm)), "OK")
```

**Decision:** Bash is better for this task — fewer dependencies, runs faster, fewer syntax traps.

### Problem: Pre-commit hook not firing

**Symptom:** `git commit` doesn't run gitleaks scan.

**Cause:** Hook not executable, or installed in wrong repo, or git config `core.hooksPath` overrides.

**Solution:**
```bash
chmod +x ~/hermes-webui/.git/hooks/pre-commit
git config core.hooksPath  # if set, adjust accordingly
ls -l ~/hermes-webui/.git/hooks/pre-commit  # should show -rwxr-xr-x
```

### Problem: Keychain secrets not loading

**Symptom:** `echo $OPENROUTER_API_KEY` shows empty after `source`.

**Cause:** Secret not in keychain, wrong account name, or keychain access denied.

**Diagnosis:**
```bash
security find-generic-password -s hermes-secrets -a openrouter-api-key -w
# Returns secret if found, or prompts for keychain access
```

**Fix:** Re-add with exact account name:
```bash
security add-generic-password -a openrouter-api-key -s hermes-secrets -w "actual-key"
```

### Problem: Gitleaks false positives

**Symptom:** Hook blocks commit on allowed patterns (e.g., `HERMES_WEBUI_PORT=8787`).

**Cause:** Default gitleaks rules are overzealous.

**Fix:** Add regex allowlist entries in `~/hermes-webui/.gitleaks.toml`:
```toml
[allowlist]
regexes = [
    'HERMES_WEBUI_PORT=\d+',
    'HERMES_WEBUI_HOST=',
]
```

### Problem: Permissions revert after reboots

**Symptom:** `.env` files become `644` again after system restart.

**Cause:** Some backup/restore process or synced folder resetting permissions. Unlikely on local macOS.

**Fix:** Ensure no cloud sync (Dropbox, iCloud) is resetting. Add cron weekly check:
```bash
0 3 * * 0 ~/.hermes/security/harden-hermes.sh
```

## Decision Log

| Decision | Rationale |
|----------|-----------|
| **Bash primary, Python fallback** | Bash simpler, no f-string issues; Python kept for complex extension |
| **Keychain over .env for secrets** | macOS integrates with Secure Enclave, encryption at rest |
| **No automatic key rotation** | User wants monitoring first; rotation can break integrations |
| **Allow external API binding** | User confirmed need; firewall mitigates; documented in policy |
| **Pre-commit hook per-repo** | Git doesn't support global hooks without `core.hooksPath`; per-repo is standard |
| **Gitleaks over truffleHog** | Gitleaks faster, more active, better TOML config |
| **No TLS for localhost** | Acceptable for single-user machine; would add overhead; documented exception |

## Output

After running this skill, you will have:

1. **All file permissions corrected** — verified with `ls -l`
2. **Active secret scanning** — `git commit` triggers gitleaks
3. **Keychain integration** — `source ~/.hermes/load-keychain-secrets.sh` populates env vars
4. **Security policy** — documented standards in `SECURITY_POLICY.md`
5. **Automation** — one-command `harden-hermes.sh` for future runs
6. **Audit trail** — all changes logged, reversible

## Verification Checklist

- [ ] `stat -f "%A %N" ~/.hermes/.env` shows `600` (owner-only)
- [ ] `stat -f "%A %N" ~/.hermes/profiles/senna/.env` shows `600`
- [ ] `ls -ld ~/hermes-webui/.git` shows no world-bits (`drwx------`)  
- [ ] `ls -ld ~/hermes-workspace/.git` shows no world-bits
- [ ] `grep "redact_secrets" ~/.hermes/profiles/senna/config.yaml` shows `true`
- [ ] `grep "redact_pii" ~/.hermes/profiles/senna/config.yaml` shows `true`
- [ ] `grep "approvals.mode" ~/.hermes/profiles/senna/config.yaml` shows `smart`
- [ ] `lsof -nP -iTCP:8642 -sTCP:LISTEN` shows `127.0.0.1:8642` (localhost-only)
- [ ] `gitleaks version` returns a version number (v8+)
- [ ] `ls -la ~/hermes-webui/.git/hooks/pre-commit` exists and is executable
- [ ] `ls -la ~/hermes-workspace/.git/hooks/pre-commit` exists and is executable
- [ ] `cat ~/.hermes/security/SECURITY_POLICY.md` exists and is readable

**Config verification:** `hermes config get <key>` may not return all values. Always fall back to grepping the config file directly for nested keys under `privacy:`, `security:`, and `approvals:`.

## Runtime Security Plugin

This skill hardens the **pre-deploy** layer (permissions, secrets, pre-commit hooks). To add **runtime** security that fires automatically on every tool call (command scanning, output filtering, audit trail, injection defense), see `hermes-runtime-security`. It builds a Hermes plugin using the `pre_tool_call` / `post_tool_call` / `pre_gateway_dispatch` hooks — once installed, it runs without manual invocation.

The two approaches are complementary layers in a defense-in-depth strategy:
- **This skill** = static hardening (permissions, keychain, gitleaks)
- **hermes-runtime-security** = dynamic middleware (live scanning at execution time)

## Related Skills

- `hermes-directory-cleanup` — cleanup old archives (complementary)
- `gitleaks` — standalone secret scanning (used internally)
- `system-hardening` — broader OS-level security (future)

## VPS Security Hardening (Linux Cloud Servers)

When deploying Hermes on a VPS (Oracle Cloud, Hetzner, DigitalOcean, etc.), apply security hardening on day 1 before installing Hermes. The VPS has a different threat model than macOS: it's internet-facing, discoverable (especially if you build in public), and attackers scan new IPs within hours.

**Full checklist:** `references/vps-security-hardening.md`

Key layers:
1. **SSH hardening** — key-only auth, no root login, max 3 retries
2. **UFW firewall** — default deny, only SSH open (Hermes communicates outbound only)
3. **Fail2Ban** — auto-ban after 3 failed SSH attempts
4. **Unattended security updates** — auto-patch CVEs
5. **Audit logging** — track config/user/cron changes
6. **Non-root user** — never run Hermes as root

**VPS provider comparison** is included in the reference (Oracle Free vs Hetzner CX22/CX32 vs DigitalOcean vs Contabo).

## Build-in-Public Security

When your repos are public (build-in-public), the threat model changes:
- Commits are scraped by bots within seconds of push
- Screenshots may leak terminal contents with secrets
- Architecture diagrams shouldn't include internal IPs

**What to expose:** source code, architecture decisions, commit history, bug stories, performance metrics, revenue numbers, tech stack choices.

**What to hide:** API keys, .env files, server IPs, DB connection strings, OAuth secrets, SSH keys, personal info in code comments.

**The golden rule:** If you'd be uncomfortable seeing it on the front page of Hacker News, don't commit it.

**Required for public repos:**
- `.gitignore` covering `.env`, `*.key`, `*.pem`, `auth.json`, `credentials.json`
- `gitleaks` pre-commit hook (blocks secret commits before they happen)
- GitHub secret scanning enabled per repo
- Dependabot alerts enabled
- Branch protection on main (require PR reviews, even if solo)
- GitHub PAT with minimal scopes (only `repo`, not `admin:org`)

## Runtime Security Companion

This skill covers STATIC hardening (permissions, pre-commit hooks, keychain). For RUNTIME security during agent operation (command scanning, injection defense, output scanning), the Katana plugin runs automatically:

- Plugin: `~/.hermes/profiles/senna/plugins/katana/`
- Config: `~/.hermes/profiles/senna/plugins/katana/config.yaml`
- Audit: `~/.hermes/logs/katana-audit.jsonl`
- Development pattern: see `hermes-plugin-dev` skill

Static (this skill) + Runtime (Katana plugin) = defense in depth.

## References


## Maintenance

This skill produces artifacts that require periodic updates:

- **Weekly:** Run `~/.hermes/security/harden-hermes.sh` to fix any drift
- **Monthly:** Update gitleaks rules, review `SECURITY_POLICY.md`
- **Quarterly:** Rotate API keys in keychain, run full `bandit` scan

If you update the policy or hooks manually, consider patching this skill to keep the templates current.
