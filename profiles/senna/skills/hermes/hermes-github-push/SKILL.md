---
name: hermes-github-push
description: "Push changes from Hermes to GitHub repos. Covers sandboxed terminal auth, token management, and common failure patterns."
version: 1.0.0
author: senna
metadata:
  hermes:
    tags: [github, git, push, auth, hermes, sandboxed-terminal]
    related_skills: [github, git-master, hermes-agent]
---

# Hermes GitHub Push

Push changes from Hermes terminal to GitHub repos. The terminal is sandboxed (`~/.hermes/profiles/<profile>/home/`), which creates auth challenges.

## Quick Reference

```bash
# Check if auth works
gh auth status

# If auth fails, user must run in REAL terminal:
gh auth login -h github.com -p https --web

# Then copy config to sandboxed home
cp ~/.config/gh/hosts.yml ~/.config/gh/hosts.yml

# Push
cd /path/to/repo && git push
```

## The Sandboxed Terminal Problem

Hermes terminal runs in a sandboxed home directory:
- Real home: `~/`
- Sandboxed: `~/.hermes/profiles/<profile>/home/`

This means:
- `gh auth status` looks at sandboxed `~/.config/gh/hosts.yml` (empty)
- `GITHUB_TOKEN` env var may not be available in sandbox
- `git push` fails with "could not read Username"

## Auth Workflow

### Step 1: Check current state
```bash
gh auth status 2>&1
gh auth token 2>&1 | head -c 20   # verify token actually exists
```

If status says "Logged in" AND token shows a real value — you're good, just push.
If status says "Failed" or token says "no oauth token found" — proceed to Step 2.

### Step 2: Check session history FIRST
Before attempting auth, search session history for past auth patterns:
```
session_search(query="gh auth login github push", limit=3)
```

The user has likely done this before. Don't go in circles.

### Step 3: User runs auth in REAL terminal
Tell the user to run in their **Mac terminal** (not through Hermes):
```bash
gh auth login -h github.com -p https --web
```

They'll get a code to paste in browser. Once it says "✓ Logged in", **verify before proceeding**:
```bash
gh auth token 2>&1 | head -c 20
```

**Pitfall:** `gh auth login --web` can say "✓ Logged in" but NOT persist the token — especially on macOS where `gh` stores tokens in the system Keychain. If `gh auth token` returns "no oauth token found", the Keychain entry is corrupted or inaccessible. Fix:
```bash
# Delete stale keychain entry and retry
security delete-generic-password -s "gh:github.com" 2>/dev/null
gh auth login -h github.com -p https --web
```

### Step 4: Copy config to sandboxed home
```bash
cp ~/.config/gh/hosts.yml ~/.config/gh/hosts.yml
```

**Verify hosts.yml has an oauth_token field:**
```bash
grep oauth_token ~/.config/gh/hosts.yml
```
If missing, the login didn't persist properly — go back to Step 3.

### Step 5: Push and verify
```bash
cd /path/to/repo && git push
```

**After pushing, verify nothing's left behind:**
```bash
git log --oneline origin/main..main
```
If this returns commits, they didn't get pushed. Push again or investigate. A common case: the user committed locally but didn't push, so your first push only covers your own commit — their older commits are still pending. Always check `origin/main..main` after a push, not just `git status`.

### Step 6: If push STILL fails after auth succeeded
If `gh auth status` is green and `gh auth token` returns a value but `git push` says "Invalid username or token":

1. Check if token is actually valid for API calls (not just status check):
   ```bash
   gh api user --jq '.login'
   ```
2. If 401: token is expired/scoped-wrong. The user needs a fresh PAT with `repo` scope.
3. Try `gh auth setup-git` to wire gh credentials into git:
   ```bash
   gh auth setup-git
   git push
   ```
4. As last resort, embed token in remote URL:
   ```bash
   TOKEN=$(gh auth token)
   git remote set-url origin "https://<user>:${TOKEN}@github.com/<user>/<repo>.git"
   git push
   ```

## Alternative: GITHUB_TOKEN in .env

If the user has `GITHUB_TOKEN` set in a `.env` file (e.g. `~/.hermes/profiles/<profile>/.env`):
```bash
# Extract token
TOKEN=$(grep 'GITHUB_TOKEN' /path/to/.env | grep -v '^#' | cut -d'=' -f2 | tr -d '"' | tr -d "'")

# Verify it actually works (not just present)
GITHUB_TOKEN="$TOKEN" gh api user --jq '.login'
```

**Pitfall:** `gh auth status` may report "Logged in" with a `.env` token even when the token is expired or has wrong scopes. Always verify with `gh api user` — a 401 means the token is bad regardless of what status says.

**Pitfall:** `gh` CLI does NOT read `.env` files. Setting `GITHUB_TOKEN` in `.env` only helps if you explicitly `export` it in the shell. For `gh` to use it, pass it inline: `GITHUB_TOKEN="$TOKEN" gh ...`

## Common Failure Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| `could not read Username` | No auth configured | Run `gh auth login` in real terminal |
| `Invalid username or token` | Token expired/bad | Re-run `gh auth login` or regenerate PAT |
| `Host key verification failed` | SSH key issue | Use HTTPS, not SSH |
| `Device not configured` | Sandboxed terminal can't prompt | Copy gh config from real home |
| `no oauth token found` | Keychain entry corrupted | `security delete-generic-password -s "gh:github.com"` then re-login |
| `gh auth status` OK but `gh api` 401 | Token expired but status cached | Run `gh api user` to verify, re-login if 401 |
| `hosts.yml` has no `oauth_token` | `gh` stores in Keychain, not file | Check `gh auth token`; if empty, re-login |

## User Frustration Signals

If the user says:
- "I've done this before" → Check session history first
- "We're going in circles" → You're re-attempting something that already failed
- "Just push it" → Stop explaining, find the working path

**Rule:** Never attempt `gh auth login` through Hermes terminal. Always ask user to run it in their real terminal.

## Related Skills

- `github` — GitHub workflows: authentication, PR lifecycle, code review
- `git-master` — Teach and guide GitHub workflows

## Reference Files

- `references/windowshermes-repo.md` — Repo structure, profile names, vault layout
- `references/vault-sync-workflow.md` — How to scan Hermes Vault and sync content to windowshermes repo. Explains concepts, recommends workflows

## Cross-References

- `references/vault-to-profiles-pipeline.md` — how to audit the Hermes Vault llm-wiki for content to copy into game-dev profiles
