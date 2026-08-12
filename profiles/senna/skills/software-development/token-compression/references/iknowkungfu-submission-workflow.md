# iknowkungfu Submission Workflow

Discovered 2026-05-16 during submission of `token-compression` and `persona-compression`. Documented here so future submissions don't re-discover the same friction points.

## Prerequisites

```
gh auth status          # must be logged in
git config user.name    # must be set
git config user.email   # must be set
```

## Fork

The user does NOT have write access to `samuelgudi/iknowkungfu`. They need a fork:

```bash
# Via web UI (when token lacks fork scope):
# Go to https://github.com/samuelgudi/iknowkungfu → click Fork

# Via CLI (when token has fork scope):
gh repo fork samuelgudi/iknowkungfu --clone --default-branch-only
```

## GitHub Token Scopes (Fine-Grained PAT)

The CLI uses different GitHub API paths for different ops, and a fine-grained PAT needs permissions on each:

| Operation | Token Permission Needed | Endpoint |
|---|---|---|
| `git push` to fork | **Contents: Write** | git HTTPS |
| `gh pr create` cross-repo | **Pull requests: Write** on the **upstream** repo | GraphQL |
| `gh pr create` fork→fork | **Pull requests: Write** on the fork repo | GraphQL |
| `gh repo fork` | Repository **Fork** permission | REST API |

For submission to `samuelgudi/iknowkungfu` (upstream), the token needs `pull_requests: write` on the upstream — not just the fork. If the token is scoped only to the fork, use the web UI for the cross-repo PR:

```
https://github.com/samuelgudi/iknowkungfu/compare/main...<your-login>:<branch-name>?expand=1
```

## Pip Package Issue: Missing Templates and Scripts

`kfu submit` calls scripts and templates at these paths relative to the venv:

- `clients/skill_contribution/templates/review.md`
- `clients/skill_contribution/templates/pr-body.md`
- `../scripts/validate.py` (relative to `agent_skills/`)

**The pip package `iknowkungfu==0.1.8` does NOT include these files.** The templates directory has only an empty `__init__.py`. The `agent_skills/scripts/` directory doesn't exist.

**Workaround:** Copy from the cached registry repo:

```bash
# Find the registry cache
REGISTRY_CACHE=~/.hermes/profiles/senna/home/.cache/iknowkungfu/registry-repo

# Find the pip site-packages
SITE_PKG=$(python3 -c "import agent_skills; from pathlib import Path; print(Path(agent_skills.__file__).parent.parent / 'clients' / 'skill_contribution' / 'templates')")

# Copy templates
cp "$REGISTRY_CACHE/clients/skill_contribution/templates/"* "$SITE_PKG/"

# Copy scripts
cp -r "$REGISTRY_CACHE/scripts/" $(python3 -c "import agent_skills; from pathlib import Path; print(Path(agent_skills.__file__).parent / 'scripts')")
```

## Running kfu submit

```bash
# Clone the fork (not upstream)
git clone https://github.com/<your-login>/iknowkungfu
cd iknowkungfu

# Prepare skill directory with SKILL.md and corrected meta.json
kfu init /tmp/my-skill    # scaffolds meta.json interactively
# Then FIX meta.json — --yes flag picks wrong defaults (category=media, agent_compat=claude-code only)
# Set: category=dev, agent_compat=[claude-code,hermes,codex,opencode,pi,openclaw]

# Submit
kfu submit /tmp/my-skill
```

## Common kfu init Meta.json Fixes

After `kfu init --yes`, always correct these fields:

```json
{
  "category": "dev",
  "tags": ["compression", "token-optimization", "dsl", ...],
  "agent_compat": ["claude-code", "hermes", "codex", "opencode", "pi", "openclaw"],
  "version": "1.0.0"
}
```

## CI Gates

From `AGENTS.md` of the registry (hard constraints, no override):

- **One skill per PR** — CI rejects PRs touching more than one `submitted/<author>/<slug>/` directory
- **SKILL.md filename is case-exact** — Linux CI rejects lowercase `skill.md`
- **No package-manager installs inside `scripts/`** — blocked by security scan (`PKG-INSTALL`)
- **No fabricated test evidence in REVIEW.md** — paste actual command output for `has_scripts: true` skills
- **Yanked versions are unreachable** — no install override flag exists
- **Author identity is immutable** — `author.github_id` is fetched automatically by `kfu init`
