---
name: hermes-security-hardening-macos
description: Comprehensive security hardening for Hermes on macOS: permission fixes, keychain secret management, gitleaks pre-commit hooks, security policy documentation, and automation scripts.
triggers:
  - security audit hermes
  - harden hermes
  - hermes security review
  - fix hermes permissions
  - hermes keychain setup
  - macos hermes security
steps:
  - id: 1
    description: Audit Hermes directories — locate all .env, .git, and config files
    commands:
      - find ~ -name '.env' -path '*hermes*' 2>/dev/null
      - find ~ -name '.git' -path '*hermes*' -type d 2>/dev/null
      - ls -l ~/.hermes/archive/.env ~/hermes-webui/.env ~/hermes-workspace/.env 2>/dev/null
    verification: Check for world-readable files (perms 644 or looser)
    artifacts:
      - List of all Hermes-related sensitive files and their permissions

  - id: 2
    description: Fix file permissions — .env to 600, .git remove world access (o-rwx)
    commands:
      - chmod 600 ~/.hermes/archive/.env ~/hermes-webui/.env ~/hermes-workspace/.env
      - chmod -R o-rwx ~/.hermes/.git ~/hermes-webui/.git ~/hermes-workspace/.git
    verification: ls -l shows -rw------- for .env; .git perms lack '...r-x...' for others
    note: Use absolute paths to avoid shell alias interference

  - id: 3
    description: Create macOS Keychain loader — ~/.hermes/load-keychain-secrets.sh
    file: ~/.hermes/load-keychain-secrets.sh
    content: |
      #!/usr/bin/env bash
      KEYCHAIN_SERVICE="hermes-secrets"
      SECURITY_CMD="/usr/bin/security"
      _secret() { "$SECURITY_CMD" find-generic-password -s "$KEYCHAIN_SERVICE" -a "$1" -w 2>/dev/null; }
      export OPENROUTER_API_KEY="$(_secret "openrouter-api-key")"
      export GITHUB_TOKEN="$(_secret "github-token")"
      export HERMES_GITHUB_TOKEN="$GITHUB_TOKEN"
    chmod: 755
    critical_insight: |
      macOS 'security' may be aliased to another command; always use /usr/bin/security absolute path.
      Non-interactive/SSH sessions cannot access GUI keychain — must run in local Terminal.app.
      If keychain locked, run: security unlock-keychain

  - id: 4
    description: Add secrets to keychain (user must supply actual values)
    commands:
      - /usr/bin/security add-generic-password -a openrouter-api-key -s hermes-secrets -w "<USER_KEY>"
      - /usr/bin/security add-generic-password -a github-token -s hermes-secrets -w "<USER_TOKEN>"
    verification: |
      /usr/bin/security find-generic-password -s hermes-secrets -a openrouter-api-key -w
      Should print the key. If not: check keychain locked, re-run add command.
    note: |
      To avoid shell history, omit -w flag and type interactively when prompted.
      If "User interaction is not allowed" or "authorization canceled", unlock keychain via GUI (Keychain Access app) or `security unlock-keychain`.

  - id: 5
    description: Install gitleaks and configure pre-commit secret scanning
    commands:
      - brew install gitleaks
      - pip install bandit safety
      - cp ~/.hermes/security/pre-commit.template ~/hermes-webui/.git/hooks/pre-commit
      - chmod +x ~/hermes-webui/.git/hooks/pre-commit
    artifacts:
      - ~/hermes-webui/.gitleaks.toml — custom rules for sk-or- and ghp_ patterns
      - ~/hermes-webui/.git/hooks/pre-commit — blocks commits containing secrets
    note: Hook greps for high-entropy strings (>40 chars) and Hermes-specific key prefixes

  - id: 6
    description: Write comprehensive security policy document
    file: ~/.hermes/security/SECURITY_POLICY.md
    sections:
      - Secrets Management — keychain-only, .env non-secret only
      - File Permissions Matrix — .env=600, .git=700
      - Network Security — localhost bindings, TLS requirements for external
      - Code Security — exec, eval, pickle, shell=True forbidden
      - Monitoring & Incident Response — weekly checks, key rotation
      - Maintenance Cadence — daily/weekly/monthly/quarterly/annual
    verification: File exists and size > 8000 bytes

  - id: 7
    description: Create automation wrapper scripts in ~/.hermes/security/
    scripts:
      - harden-hermes.sh — idempotent bash runner (recommended)
      - harden-hermes-security.py — Python alternative
      - MORNING_CHECKLIST.sh — daily env + permission + gitleaks verification
      - install-all.sh — fresh-install one-command wrapper
    verification: All scripts executable and run without error

  - id: 8
    description: Log to Obsidian — create daily note of work performed
    file: ~/Hermes Vault/Hermes/Daily Notes/YYYY-MM-DD/Hermes Security Hardening & Keychain.md
    frontmatter:
      date: YYYY-MM-DD
      tags: [hermes, security, keychain, hardening]
      category: security
      status: completed
    content_summary: |
      Permissions fixed (.env→600, .git→700), automation created, keychain configured,
      policy written. Morning verification pending: source loader, check env vars, add to ~/.zshrc.

  - id: 9
    description: Configure shell persistence — auto-load keychain on new shells
    commands:
      - echo 'source ~/.hermes/load-keychain-secrets.sh' >> ~/.zshrc
      - source ~/.zshrc
    verification: echo $OPENROUTER_API_KEY prints non-empty value

pitfalls:
  - "Shell alias 'security' may override /usr/bin/security — discovered when 'security find-generic-password' ran 'hermes' CLI instead. Fix: use absolute path."
  - "Non-interactive environments cannot access GUI keychain — user must run add/retrieve commands in local Terminal.app, not SSH or CI."
  - "Keychain locked — 'User interaction is not allowed' or 'authorization canceled'. Fix: unlock via `security unlock-keychain` or GUI Keychain Access app before adding secrets."
  - "Pre-commit hook false positives — may block legitimate commits. Tune ~/hermes-webui/.gitleaks.toml allowlist paths (tests/, *.md, etc.)."
  - "Permissions may drift if other tools modify files — harden-hermes.sh is idempotent; run weekly via cron to auto-correct."
  - "API keys in shell history if typed directly — use 'security add-generic-password' without -w flag to prompt interactively, avoiding history."

outputs:
  - "All .env files set to 600 (owner read/write only)"
  - "All .git directories have world access removed (o-rwx)"
  - "macOS Keychain 'hermes-secrets' service populated with accounts: openrouter-api-key, github-token"
  - "~/.hermes/load-keychain-secrets.sh sourced in shell; OPENROUTER_API_KEY, GITHUB_TOKEN, HERMES_GITHUB_TOKEN exported"
  - "Gitleaks pre-commit hook installed and active in ~/hermes-webui/.git/hooks/"
  - "Security policy documented at ~/.hermes/security/SECURITY_POLICY.md"
  - "Automation scripts in ~/.hermes/security/ ready for weekly/monthly maintenance"
  - "Obsidian daily note created documenting the session"
post_commands:
  - /usr/bin/security find-generic-password -s hermes-secrets -a openrouter-api-key -w
  - source ~/.hermes/load-keychain-secrets.sh
  - echo $OPENROUTER_API_KEY
  - echo 'source ~/.hermes/load-keychain-secrets.sh' >> ~/.zshrc
---

## Usage Notes

**When to invoke:** After initial Hermes install, after discovering exposed secrets/permissions, or during security hardening sprints.

**User decisions required:**
1. Confirm external network access needed for WebUI (affects binding configuration in policy)
2. Choose keychain over plaintext .env (this skill enforces keychain)
3. Authorize rotating exposed keys or monitoring only (user chose monitoring)
4. Accept pre-commit hook blocking (may require tuning allowlist)

**Generated artifacts:**
- `~/.hermes/security/` — all automation files
- `~/.hermes/load-keychain-secrets.sh` — sourced in shell
- `~/hermes-webui/.gitleaks.toml` and `.git/hooks/pre-commit` — secret scanning
- `~/.hermes/security/SECURITY_POLICY.md` — reference policy
- `~/Hermes Vault/.../Daily Notes/` — Obsidian logging

**Morning handoff:** User must verify keychain accessibility, source loader, confirm env vars, and add to ~/.zshrc. Skill creates MORNING_CHECKLIST.sh to automate this.

**Experiential findings incorporated:**
- macOS `security` command may be shadowed by alias or wrapper — always use `/usr/bin/security`
- Keychain operations require GUI-terminal context, not sandboxed/non-interactive
- `.env` files commonly world-readable by default — explicitly fix to 600
- Git history often contains old secrets — restrict .git dir perms (o-rwx) as defense-in-depth
- Pre-commit hooks should be simple greps initially; tune allowlist as needed

**Integration:** Works alongside `obsidian-memory-bridge` for vault logging. Complements `team-wiki/sync` for shared team policies (if scaled beyond personal use).
