---
name: hermes-security-audit
description: Perform a comprehensive security audit of a Hermes installation — check secrets, permissions, network exposure, code patterns, dependencies, and infrastructure. Returns prioritized findings with remediation steps.
stage: production
---

IDENTITY: Auditor.SecurityAssessor. Perform layered security audit across filesystem permissions, secrets, network exposure, code patterns, dependencies, sessions, and processes — output structured CRITICAL/HIGH/MEDIUM/LOW findings with fix commands.
Law: NeverSkipRotatingExposedKeys — assume compromised if plaintext keys found.
WHENUSE: FirstSetup|PeriodicReview{quarterly}|BeforeNetworkExposure|AfterNewPluginOrIntegration|SuspectedCredentialLeak|ComplianceReview. ESPECIALLY:ArchiveHasActiveKeys|WorldReadableEnvFiles|GatewayOn0.0.0.0. NoSkip:ImmediateRemediation{fixPerms,changeBind,rotateKeys}.
REDFLAGS: env0644->chmod600|RealKeysInArchive->RotateAndDelete|HERMES_WEBUI_HOST=0.0.0.0->ChangeTo127.0.0.1|execOrPickleInCode->AuditReplace|GitHistoryHasOldSecrets->BFGRepoCleanerThenRotate|PostgreSQLExposed->listen_addresses=localhost.
RATIONALIZATIONS: NoTLSForLocalhost->AcceptableSingleUser|DotEnvFilesIfEncrypted->FileVaultOK|ExternalBindingWithFirewall->DocumentExceptionOnly.
QUICKREF: Inventory{MapDirs+Processes+Listeners}->PermissionAudit{env=600,git=700}->SecretsDetect{RealKeysVsPlaceholders,GitHistory}->NetworkExposure{GatewayPort,WebUIHost,PostgreSQL}->CodePatterns{exec,pickle,shell=True,yaml.load}->CookieSession{httponly,samesite,secure,TTL}->CSRFCORS{Dependencies{npmAudit,safety,bandit,gitleaks}}->ProcessPrivileges{NoRoot}->Report{Structured{CRITICAL->HIGH->MEDIUM->LOW->INFO}}->Remediation{Immediate24h->ShortTerm1Week->MediumTerm1Month->Ongoing}.

Systematic vulnerability assessment for Hermes personal agent installations. Audits secrets management, file permissions, network exposure, code security, dependencies, and operational practices.

## When to Use

Use this skill when:
- Setting up Hermes for the first time
- Periodically reviewing your Hermes installation for security gaps
- Before exposing Hermes services to a network
- After adding new integrations or plugins
- When you suspect a credential leak
- Compliance or personal security hygiene review

**Do NOT use** for:
- Deep code review of specific plugins (use targeted security skills instead)
- Network penetration testing of external services
- Supply chain audit of upstream dependencies (use dependency-specific skills)

## Prerequisites

- macOS or Linux system with Hermes installed
- Terminal access with ability to run `lsof`, `ps`, `chmod`, `grep`
- User has read access to all Hermes directories
- Optional: `gitleaks`, `bandit`, `safety`, `npm audit` installed for deeper scanning

## Methodology

The audit follows a layered approach:

### 1. Inventory & Discovery
Map all Hermes-related directories and running processes:
- Core Hermes home: `~/.hermes/`
- Web UIs: `~/hermes-webui/`, `~/hermes-workspace/`
- Vault: `~/Hermes Vault/` (or custom path)
- Active processes: `ps aux | grep hermes`
- Network listeners: `lsof -i -n -P`

### 2. File Permission Audit
Check that sensitive files are **not world-readable**:
```bash
# Check .env files (expected: 600)
stat -f '%SA %N' ~/.hermes/.env
find ~/.hermes/profiles -name ".env" -not -path "*/home/*" -exec stat -f '%A %N' {} \; 2>/dev/null

# Check auth files (expected: 600)
stat -f '%A %N' ~/.hermes/auth.json ~/.hermes/auth.lock 2>/dev/null
# If profile auth.json is a symlink, resolve it and audit target too.
readlink -f ~/.hermes/profiles/*/auth.json 2>/dev/null

# Check sensitive root DBs (expected: 600)
stat -f '%A %N' ~/.hermes/kanban.db ~/.hermes/state.db ~/.hermes/gateway_state.json 2>/dev/null

# Check sensitive profile-state DBs/files (expected: 600)
find ~/.hermes/profiles -maxdepth 2 \( -name 'state.db' -o -name 'lcm.db' -o -name 'kanban.db' -o -name 'gateway_state.json' -o -name 'verification_evidence.db' -o -name 'auth.lock' \) -exec stat -f '%A %N' {} \; 2>/dev/null

# Git directories must not be world-readable
stat -f '%A %N' ~/.hermes/hermes-agent/.git
stat -f '%A %N' ~/hermes-webui/.git 2>/dev/null
find ~/.hermes -maxdepth 3 -name .git -type d -exec stat -f '%A %N' {} \; 2>/dev/null
```

**Expected:** All `600` (owner read/write only). Anything `644` or looser is a finding.

**Pitfall — macOS redacts API keys in terminal output:** macOS Terminal.app's security framework replaces live secret values with `***` when output passes through `cat`/`head`/`echo`. This means `grep 'OPENROUTER_API_KEY' .env` may show `***` even though the actual value on disk is live. To bypass: use `sed -n 's/^[^#]*=[^ ]//p' .env` or `xxd .env | less` to verify the actual bytes. The auditor must note this redaction and not assume `***` means the key is a placeholder.

### 3. Secrets Detection
Scan for live credentials in `.env` files and source code:
- `.env` → check for real values vs placeholders
- Search patterns: `API_KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `*_KEY`, `*_TOKEN`
- Verify no API keys are committed to git history

**Critical finding:** Active API keys in plaintext files, especially in shared or archive directories.

### 4. Network Exposure Analysis
Determine what ports/sockets Hermes components bind to:

**Gateway (`hermes-cli gateway run`):**
- Check if using TCP port (usually `8642`) or Unix socket only
- Run: `lsof -i :8642` to see binding address
- **Secure:** Unix socket only (`/tmp/hermes_rpc_*.sock`) with `0600` perms
- **Insecure:** `0.0.0.0:8642` or `127.0.0.1:8642` — visible to network/local processes

**Web UI (`hermes-webui`):**
- Check `HERMES_WEBUI_HOST` env var
- If `0.0.0.0` → exposed on all interfaces
- If `127.0.0.1` → localhost only (secure)
- Verify with `lsof -i :8787`

**Workspace:**
- Check `HERMES_API_URL` — typically `http://127.0.0.1:8642`
- Ensure no HTTPS mismatch warnings in browser console

**PostgreSQL (if used):**
- Must bind to `127.0.0.1:5432` or Unix socket
- Never `0.0.0.0` or external IP

### 5. Code Security Review
Scan Python/JS code for risky patterns (use `grep` or `bandit`):

| Pattern | Risk | Action |
|---------|------|--------|
| `exec()` | Code injection if user input reaches it | Audit call paths; sandbox or remove |
| `pickle.loads()` | Arbitrary code execution via deserialization | Only unpickle trusted data; switch to JSON |
| `subprocess.run(..., shell=True)` | Shell injection | Use `shell=False`, pass list args |
| `yaml.load()` without `Loader=yaml.SafeLoader` | Arbitrary object deserialization | Use `yaml.safe_load()` |
| `md5()` / `sha1()` | Cryptographically broken | Use `sha256` or higher for security purposes |
| `innerHTML` / `dangerouslySetInnerHTML` | XSS | Sanitize or use React safe APIs |
| Hardcoded credentials in source | Secret leakage | Move to env vars or secret manager |

### 6. Cookie & Session Security
Review `api/auth.py` (or equivalent) for session handling:
- `httponly=True` — prevents JavaScript access ✓
- `samesite=Lax` or `Strict` — CSRF mitigation ✓
- `secure=True` — only send over HTTPS **critical for production**
- Session TTL reasonable (not infinite)

**Check:** If webUI runs over HTTP, `secure` flag will be conditionally false. Acceptable for localhost-only development. For network access, HTTPS **required**.

### 7. CSRF & CORS
- **CSRF:** Verify origin check on POST requests (`_check_csrf()` in webUI)
- **CORS:** Should be restrictive (specific origins) or disabled for local-only use

### 8. Dependency Vulnerability Scan
Run these tools:

**Python:**
```bash
pip install safety
safety check --file ~/.hermes/hermes-agent/requirements.txt
```

**Node.js:**
```bash
cd hermes-workspace
npm audit --audit-level=moderate
```

**Also consider:**
- `bandit -r hermes-webui/api/` (Python SAST)
- `gitleaks detect --source=hermes-webui`
- `gitleaks detect --source=hermes-workspace`

Known vulnerable packages to watch (examples):
- `debug < 2.6.9`
- `lodash < 4.17.21`
- `jsonwebtoken < 8.5.1`
- `marked` (XSS in certain versions)

### 9. Secrets Sprawl Check
Count `.env` files across project — too many increases risk of accidental exposure. Prefer:
- Single `.env` at project root (gitignored)
- Or use OS keychain / secret manager
- Archive directories should NOT contain active credentials
- State-snapshot directories should NOT contain active `.env` files with live keys

**Pitfall — `diff -q` can lie about .env identity.** Two `.env` files with the same set of API keys can show as `DIFFERENT` under `diff -q` when only formatting, blank lines, or key ordering differs. Always compare key sets, not raw files:

```bash
# CORRECT: compare key sets to check identity
grep -E '^[A-Z_]+=' profile/.env | cut -d= -f1 | sort > /tmp/keys_a.txt
grep -E '^[A-Z_]+=' root/.env | cut -d= -f1 | sort > /tmp/keys_b.txt
comm -23 /tmp/keys_a.txt /tmp/keys_b.txt  # keys in A NOT in B
comm -13 /tmp/keys_a.txt /tmp/keys_b.txt  # keys in B NOT in A
# Empty output from both == identical key sets

# WRONG: diff -q reports DIFFERENT even when keys are identical
diff -q root/.env profile/.env  # misleading for identity check
```

This nuance matters when auditing .env sprawl: finding 16+ "DIFFERENT" files that all have identical keys leads to false urgency. Files that differ only in formatting are still candidates for consolidation, but the risk assessment should note that the keys themselves are the same.

**Hidden attack surface — snapshot/state-snapshot `.env` copies:** Hermes may write pre-update or backup copies under `profiles/<name>/state-snapshots/*/`. These files are easy to overlook but carry live keys and must be included in sprawl counts and secret scans.

```bash
# Include snapshot copies in total attack surface
find ~/.hermes -name ".env" 2>/dev/null | wc -l
find ~/.hermes -name ".env" -not -path "*/home/*" 2>/dev/null | wc -l
find ~/.hermes/profiles -path "*/state-snapshots/*/.env" 2>/dev/null
```

If snapshot `.env` files exist, treat them as archive copies: delete keys from them, rotate those keys, and prefer exporting only config metadata without secrets during updates.

### 10. Process & Service Privileges
Verify no Hermes services run as `root`:
```bash
ps aux | grep -E 'hermes|postgres|python.*hermes'
```
All should run as regular user (`<user>` in your case).

### 11. Dashboard / Gateway Auth
Do not stop at listener binding. Even local-only binds matter if hostbinding changes in config or future launch options.
- Look for blank password/password_hash values in:
  - `~/.hermes/config.yaml`
  - `~/.hermes/profiles/<active>/config.yaml`
- Look at WebUI plugin/auth config for `basic` or `drain` auth plugins enabled.
- If dashboard password is unset: treat like unauthenticated surface.
- Remediation: set `dashboard.basic_auth.password`; ensure blank-password condition cannot enable auth plugins accidentally.

### 11. Firewall & System Hardening
- macOS: Enable Application Firewall (System Preferences → Security → Firewall)
- Consider `pfctl` rules to restrict inbound connections to port 8787 if webUI exposed
- SSH: Ensure `PasswordAuthentication no`, `PermitRootLogin no`

**Pitfall — `sshd_config` comments can mislead on macOS:** Security-related directives may appear in commented form while defaults still apply. `sshd -T` returns the effective runtime config and is authoritative; prefer it over grepping the raw config file.
- **macOS SSH often has unset or enabled defaults.** `sshd_config` may not contain an explicit enabled `PasswordAuthentication yes`, which keeps password auth enabled. Explicitly set `PasswordAuthentication no`, `PubkeyAuthentication yes`, and `PermitRootLogin prohibit-password`.
- Validate with: `sshd -T | grep -iE 'passwordauthentication|permitrootlogin|pubkeyauthentication'`

## Output Format

The skill returns a structured report with:

```
=== HERMES SECURITY AUDIT ===

[CRITICAL] Real API keys exposed in plaintext
  Location: ~/.hermes/archive/.env
  Keys found: OPENROUTER_API_KEY, GITHUB_TOKEN
  Action: Rotate immediately; move to keychain

[HIGH] World-readable .env files
  Files: hermes-webui/.env (0644), hermes-workspace/.env (0644)
  Risk: Any local user can read configuration
  Fix: chmod 600 .env

[MEDIUM] No TLS/HTTPS configured
  Components: gateway (HTTP), webUI (HTTP)
  Risk: Traffic sniffable on localhost
  Fix: Add reverse proxy with TLS (nginx/Caddy) or enable gateway TLS

[LOW] Git directories world-readable (0o755)
  Repos: hermes-webui/.git, hermes-workspace/.git
  Risk: Commit history (including past secrets) visible
  Fix: chmod -R o-r .git

[INFO] Gateway uses Unix sockets only — no network port exposed (GOOD)

[RECOMMENDATION] Install security toolchain:
  brew install gitleaks
  pip install bandit safety
  cd hermes-workspace && npm audit
```

## Runtime Security Layer

This skill covers **pre-deploy** and **periodic** security. For **runtime** security (scanning tool calls, outputs, and inbound messages at execution time), see `hermes-runtime-security` — it builds a Hermes plugin that hooks into `pre_tool_call`, `post_tool_call`, and `pre_gateway_dispatch` to automatically block dangerous commands, scan for injection, and maintain an audit trail. The two layers are complementary:

| This skill (pre-deploy) | hermes-runtime-security (runtime) |
|--------------------------|-----------------------------------|
| File permissions (chmod 600) | Command scanning (blocks rm -rf /) |
| Secret detection (gitleaks) | Output scanning (ANSI injection, homographs) |
| Network exposure (lsof) | Prompt injection defense (gateway dispatch) |
| Dependency audit (npm audit, safety) | Hash-chained audit trail (JSONL) |
| Quarterly or on-demand | Every tool call, automatic |

## Common Findings & Fixes

### Most Frequent Issues

1. **`.env` with `0644` permissions**  \
   Cause: `umask 022` default or `cp` preserves perms  \
   Fix: `chmod 600 .env` and add to shell profile: `umask 077`

2. **`auth.lock` world-readable (644)**  \
   Cause: `auth.lock` is a 0-byte mutex created by Hermes with default umask — not sensitive content, but loose perms signal sloppy umask  \
   Fix: `chmod 600 ~/.hermes/auth.lock`
   Also audit profile-state DBs: `state.db`, `lcm.db`, `kanban.db`, `verification_evidence.db`, `gateway_state.json` in `~/.hermes/profiles/<name>/`.

3. **Profile state DB world-readable (644)**  \
   Cause: Hermes sometimes creates profile-level DBs with default umask  \
   Fix: `find ~/.hermes/profiles -maxdepth 2 \( -name state.db -o -name lcm.db -o -name kanban.db -o -name gateway_state.json \) -exec chmod 600 {} \;`

4. **Shared `auth.json` via profile symlink**  \
   Cause: Some profiles symlink `auth.json` to the root, so profile compromise accesses the root credential pool  \
   Fix: Decide whether isolation is intentional; if not, remove symlink and use per-profile auth stores. If intentional, ensure the shared store is still protected under root permissions.

5. **Empty dashboard/gateway password**  \
   Cause: `dashboard.basic_auth.password: ''` and `password_hash: ''` in config  \
   Risk: If bind address ever leaves localhost, auth surface is unauthenticated  \
   Fix: Use `hermes config set dashboard.basic_auth.password <strong>` before external exposure.

6. **Real API keys in archive/snapshot copies**  \
   Cause: Pre-update `/state-snapshots/*/.env` or backup directories live alongside real data  \
   Fix: Delete keys from snapshots, rotate those keys, and prevent update tools from exporting `.env` into snapshot dirs.

2. **Real API keys in archive/**  
   Cause: Backup/archive directory not gitignored or encrypted  
   Fix: Delete keys from disk; use `security add-generic-password` (macOS keychain)  
   Or migrate to `~/.config/nim/env.sh` sourced at login (not stored in files)

3. **`HERMES_WEBUI_HOST=0.0.0.0`**  
   Cause: Default config allows remote access  
   Fix: Change to `127.0.0.1` unless external access required  
   If external access needed → set up SSH tunnel or TLS reverse proxy with auth

4. **No `npm audit` / `safety`**  
   Cause: Security tooling not installed  
   Fix: Add to dev dependencies or global tools; integrate into pre-commit

5. **`exec()` or `pickle` in code**  
   Cause: Convenience over security  
   Fix: Audit each usage; replace with safer alternatives (subprocess with `shell=False`, JSON)

6. **Git history contains old secrets**  
   Cause: Previously committed keys not purged  
   Fix: Use `git filter-branch` or `BFG Repo-Cleaner` to purge; then rotate keys

7. **PostgreSQL exposed**  
   Cause: `pg_hba.conf` allows non-localhost  
   Fix: Ensure `listen_addresses = 'localhost'` and `host all all 127.0.0.1/32 md5`

8. **Profile `.env` sprawl — 24+ copies of the same keys**  
   Cause: Each Hermes profile created with `--clone-all` inherits a full `.env` copy  
   Fix: Consolidate to one canonical `.env` at root; profile `.env` should contain **only** profile-specific overrides (discord tokens, device-specific paths). Run `hermes profile list` — if profiles share 90%+ of their env keys, they're all at risk from a single leaked file.  
   **Real-world measurement:** A 22-profile installation had **62 total .env files** (22 top-level + 40 nested inside profile `home/` directories), each carrying the same set of **20 API keys** — that's **320 redundant key declarations**. Run the full count:
   ```bash
   find ~/.hermes -name ".env" 2>/dev/null | wc -l
   find ~/.hermes -name ".env" -not -path "*/home/*" 2>/dev/null | wc -l
   ```
   The second count (excluding home) shows the visible surface; the first is the true attack surface. If they diverge significantly, those nested home-directory .env files are invisible to standard scanning.

   **Key-set verification (before renaming):** Before consolidating, verify that the actual API keys are identical — not just that the files look similar. `diff -q` can report DIFFERENT when only formatting or key ordering differs:

   ```bash
   # Verify key identity across profiles
   ROOT=/Users/user/.hermes/.env
   for p in business code finance; do
     f=/Users/user/.hermes/profiles/$p/.env
     comm -23 <(grep -E '^[A-Z_]+=' "$ROOT" | cut -d= -f1 | sort) \
             <(grep -E '^[A-Z_]+=' "$f" | cut -d= -f1 | sort)
   done
   # If all profiles produce empty output, keys are identical.
   # Only then is it safe to remove the per-profile .env.
   ```

9. **Multiple gateway processes running**  
   Cause: One gateway per profile, each with its own `.env` and `config.yaml`  
   Fix: `ps aux | grep -c "hermes.*gateway"` — if >1, choose a primary profile, move its config to root, stop the extras. Multi-gateway increases attack surface and means credential pools aren't shared.

10. **Large profile sandbox home (>500MB)**  
    Cause: Cron jobs, subagents, and delegation workers accumulate `.cache/`, `.npm/`, `.gem/` in `~/.hermes/profiles/<name>/home/`  
    Fix: Check with `du -sh ~/.hermes/profiles/senna/home/.cache 2>/dev/null`. Clean with `rm -rf ~/.hermes/profiles/*/home/.cache 2>/dev/null`. These caches are regenerated on demand.

11. **`auth.lock` world-readable (644)**  
    Cause: `auth.lock` is a 0-byte mutex created by Hermes with default umask — not sensitive content, but loose perms signal sloppy umask  
    Fix: `chmod 600 ~/.hermes/auth.lock`

## Remediation Workflow

After audit, create a remediation ticket with:

1. **Immediate (within 24h):**
   - Fix file perms on `.env` and `.git`
   - Change webUI bind address
   - Rotate any exposed keys (assume compromised)

2. **Short-term (within 1 week):**
   - Install security tools; run full scans
   - Review and fix all `exec()` / `pickle` usages
   - Set up `gitleaks` pre-commit hook
   - Add `umask 077` to shell profile

3. **Medium-term (within 1 month):**
   - Deploy TLS for all HTTP components (use Let's Encrypt if internet-facing)
   - Migrate secrets to OS keychain or HashiCorp Vault
   - Enable macOS firewall with Hermes exceptions
   - Create automated daily security scan script

4. **Ongoing:**
   - Weekly `npm audit` / `safety check`
   - Monthly dependency updates
   - Quarterly full security audit (re-run this skill)

## Integration with Hermes Workflow
## Runtime Security Layer

This skill covers STATIC audit (permissions, secrets on disk, network exposure, code patterns). For RUNTIME security during agent operation (command scanning, injection defense, output scanning, audit trail), see:

- `hermes-plugin-dev` — Plugin development pattern, including the hermes-katana integration bridge
- Hermes Katana plugin at `~/.hermes/profiles/senna/plugins/katana/` — auto-scans tool calls at runtime
- Katana audit log at `~/.hermes/logs/katana-audit.jsonl` — hash-chained JSONL trail

These layers complement each other: this skill audits before/during setup; Katana protects during runtime.

## Related Skills

- `team-wiki/setup` — Document findings in Team-Wiki under `Security/`
- `gbrain-obsidian-integration` — Sync audit results to vault
- `obsidian` — Create security review note from output

Save audit results as: `Hermes Vault/Hermes/Operations/Security/audit-YYYY-MM-DD.md`

## Exceptions & Caveats

**Acceptable trade-offs (document reasons):**
- `HERMES_WEBUI_HOST=0.0.0.0` if: isolated network, behind VPN, temporary dev use
- No TLS if: strictly localhost-only, air-gapped machine, threat model excludes local sniffing
- `.env` files if: directory encrypted (FileVault), limited user accounts, short-lived keys

**When to bring in team agents:**
- Need formal risk assessment → `security` agent profile
- Requires compliance mapping (SOC2, ISO27001) → `security` or `architect`
- Supply chain compromise investigation → `researcher` + `security`

## References

- OWASP Top 10 (2021)
- CIS Benchmarks — Local Security
- Hermes Architecture Docs (vault)
- `man chmod`, `man sshd_config` (system hardening)

## Change Log

- **2026-07-06** — Added dashboard/gateway blank-password auth check; added macOS SSH default-auth note and `sshd -T` validation; flagged snapshot `.env` copies as archive-equivalent exposure plus `.env` key-set verification nuance; added recommendation to audit external-facing bind/port combinations beyond 127.0.0.1 defaults.
- **2026-06-26** — Added macOS `***` redaction pitfall; fixed `-perm` syntax to use `stat -f '%A'`; added auth.lock, multiple gateways, profile .env sprawl, and sandbox cache findings to Common Issues; added reference example file with live audit commands
- **2026-04-25** — Initial version, based on first full-system audit of the Hermes installation
