# iknowkungfu Contribution Pipeline

Known pitfalls when submitting skills to the iknowkungfu registry (v0.1.8).

## Prerequisites

1. **GitHub fork** — fork `samuelgudi/iknowkungfu` to your account. `kfu submit` pushes to the fork's `origin`.
2. **GitHub PAT permissions** — fine-grained PAT needs at least:
   - `contents: write` (push branch)
   - `pull_requests: write` (create PR)
3. **`kfu` CLI** — installed via `pip install iknowkungfu` (in Hermes venv at `venv/bin/kfu`)

## Missing Templates/Scripts (v0.1.8)

The pip package v0.1.8 does **not** bundle `scripts/` or `clients/skill_contribution/templates/` directories. `kfu submit` crashes with `FileNotFoundError` when it tries to use `validate.py`, `review.md`, or `pr-body.md`.

**Fix before running `kfu submit`:**

```bash
# Locate the registry-repo cache (populated by the MCP server on first use)
REGISTRY_CACHE=~/.hermes/profiles/senna/home/.cache/iknowkungfu/registry-repo
VENV_SITE=~/.hermes/hermes-agent/venv/lib/python3.11/site-packages

# Copy scripts
cp -r "$REGISTRY_CACHE/scripts/" "$VENV_SITE/agent_skills/scripts/"

# Copy templates
cp "$REGISTRY_CACHE/clients/skill_contribution/templates/"* \
   "$VENV_SITE/clients/skill_contribution/templates/"
```

## Submission Flow

```bash
# 1. Fork on GitHub, clone the fork
gh repo clone your-username/iknowkungfu /tmp/iknowkungfu-fork
cd /tmp/iknowkungfu-fork

# 2. Prepare skill directory (SKILL.md + meta.json)
kfu init /tmp/my-skill          # scaffolds meta.json interactively

# 3. Validate + push + open PR (must run FROM the cloned fork)
kfu submit /tmp/my-skill
```

## CI Bounce Checklist

| Failure | Fix |
|---|---|
| `validate` schema error | Run `kfu validate <dir>` locally, fix `meta.json` field |
| `security_scan` block (`PKG-INSTALL`) | Move package installs to `meta.json.requires.commands` |
| `SKILL.md` filename case | Must be uppercase `SKILL.md` (Linux CI is case-sensitive) |
| Multiple `submitted/` dirs in one PR | Run `kfu submit` once per skill |
| GitHub ID mismatch | Re-run `kfu init` to refetch numeric ID |

## One Skill Per PR

CI rejects PRs touching more than one `submitted/<author>/<slug>/` directory. Each skill gets its own branch and PR. Do not bundle.

## Token Scope Note

If `gh repo fork` gives HTTP 403, the fine-grained PAT lacks fork permission. Fork manually via GitHub web UI, then `gh repo clone your-fork`.
