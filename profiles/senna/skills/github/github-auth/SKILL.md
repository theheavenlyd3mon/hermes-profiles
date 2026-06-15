---
name: github
description: "GitHub workflows: authentication, PR lifecycle, code review, issues management, repository management. Use when working with GitHub repos, PRs, issues, or CI/CD."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Git, PR, Issues, Code-Review, Authentication, CI/CD, Repositories]
    related_skills: [hermes-agent]
---

# GitHub Workflows

Complete guide for working with GitHub — authentication, PRs, code review, issues, and repository management. Each section shows `gh` first, then the `git` + `curl` fallback.

This skill sets up authentication so the agent can work with GitHub repositories, PRs, issues, and CI. It covers two paths:

- **`git` (always available)** — uses HTTPS personal access tokens or SSH keys
- **`gh` CLI (if installed)** — richer GitHub API access with a simpler auth flow

## Conceptual Overview (for Non-Developers)

If the user is new to git and GitHub and needs the "why" before the "how,"
see `references/non-developer-introduction.md` for a plain-language walkthrough
of authentication, safety layers (`.gitignore`, secret redaction, GitHub's own
scanning), and the daily PR-review workflow. Use this to answer questions like
"what if my API key accidentally ends up in a commit?" or "do I need to know
git commands?" before jumping into the setup commands below.

## Detection Flow

When a user asks you to work with GitHub, run this check first:

```bash
# Check what's available
git --version
gh --version 2>/dev/null || echo "gh not installed"

# Check if already authenticated
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```

**Decision tree:**
1. If `gh auth status` shows authenticated → you're good, use `gh` for everything
2. If `gh` is installed but not authenticated → use "gh auth" method below
3. If `gh` is not installed → use "git-only" method below (no sudo needed)

**Also check for embedded tokens in remote URLs:** Old tokens often get baked directly into git remote URLs (e.g., `https://x-access-token:***@github.com/...` or `https://username:token@github.com/...`). When git finds credentials in the URL itself, it uses those and **never calls the credential helper** — so a freshly-authenticated `gh` or a new PAT is completely invisible to push operations. Run this check:

```bash
# Scan the user's real home projects (these are what the user sees in Finder/terminal)
find /Users/<you>/projects ~/Hermes\\ Vault -name ".git" -maxdepth 4 2>/dev/null \
  -exec sh -c 'git -C "$(dirname "$1")" remote -v 2>/dev/null | grep -E "@" | grep -v "git@"' _ {} \;

# Also scan sandboxed profile projects (repos cloned from within Hermes)
for profile in ~/.hermes/profiles/*/; do
  sandbox_home="${profile}home"
  if [ -d "$sandbox_home/projects" ]; then
    find "$sandbox_home/projects" -name ".git" -maxdepth 4 2>/dev/null \
      -exec sh -c 'git -C "$(dirname "$1")" remote -v 2>/dev/null | grep -E "@" | grep -v "git@"' _ {} \;
  fi
done
```
  -exec sh -c 'git -C "$(dirname "$1")" remote -v 2>/dev/null | grep -E "@" | grep -v "git@"' _ {} \;
```

Any match showing `https://something@github.com/...` has an embedded credential. Fix: strip it with `git remote set-url origin https://github.com/<owner>/<repo>.git`.

---

## Method 1: Git-Only Authentication (No gh, No sudo)

This works on any machine with `git` installed. No root access needed.

### Option A: HTTPS with Personal Access Token (Recommended)

This is the most portable method — works everywhere, no SSH config needed. You have **two types** of token to choose from:

#### Fine-Grained PAT (Recommended)

Go to: **https://github.com/settings/tokens?type=beta**

- Click "Generate new token"
- Give it a name like "hermes-agent" and a description
- Set expiration (the user will be prompted when it expires)
- Under **Resource owner**, select the user or org
- **Repository access** — choose "Only select repositories" and pick the repos the agent should access, or "All repositories" for blanket access
- **Permissions** — set these to **Read and write**:

| Permission | Why |
|---|---|
| **Contents** | Push, pull, edit files, merge PRs — the core code/documentation permission |
| **Pull requests** | Open, manage, and merge pull requests |

Security principle: grant **Contents + Pull requests** only. Leave everything else on "No access" unless the agent needs to file issues, manage Actions, etc. See `references/fine-grained-pat-permissions.md` for a complete reference of all 28 repository permissions with plain-language explanations.

The token auto-expires and is scoped to exactly the repos you select.

#### Classic PAT (Legacy)

Go to: **https://github.com/settings/tokens**

- Click "Generate new token (classic)"
- Give it a name like "hermes-agent"
- Select scopes:
  - `repo` (full repository access — read, write, push, PRs)
  - `workflow` (trigger and manage GitHub Actions)
  - `read:org` (if working with organization repos)
- Set expiration (90 days is a good default)

Classic PATs give **broad access** — the `repo` scope unlocks everything across all repos the user owns. Simpler to set up, but less secure than fine-grained.

**Step 2: Configure git to store the token**

```bash
# Set up the credential helper to cache credentials
# "store" saves to ~/.git-credentials in plaintext (simple, persistent)
git config --global credential.helper store

# Now do a test operation that triggers auth — git will prompt for credentials
# Username: <their-github-username>
# Password: <paste the personal access token, NOT their GitHub password>
git ls-remote https://github.com/<their-username>/<any-repo>.git
```

After entering credentials once, they're saved and reused for all future operations.

**Alternative: cache helper (credentials expire from memory)**

```bash
# Cache in memory for 8 hours (28800 seconds) instead of saving to disk
git config --global credential.helper 'cache --timeout=28800'
```

**Alternative: set the token directly in the remote URL (per-repo)**

```bash
# Embed token in the remote URL (avoids credential prompts entirely)
git remote set-url origin https://<username>:<token>@github.com/<owner>/<repo>.git
```

**Step 3: Configure git identity**

```bash
# Required for commits — set name and email
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

**Step 4: Verify**

```bash
# Test push access (this should work without any prompts now)
git ls-remote https://github.com/<their-username>/<any-repo>.git

# Verify identity
git config --global user.name
git config --global user.email
```

### Option B: SSH Key Authentication

Good for users who prefer SSH or already have keys set up.

**Step 1: Check for existing SSH keys**

```bash
ls -la ~/.ssh/id_*.pub 2>/dev/null || echo "No SSH keys found"
```

**Step 2: Generate a key if needed**

```bash
# Generate an ed25519 key (modern, secure, fast)
ssh-keygen -t ed25519 -C "their-email@example.com" -f ~/.ssh/id_ed25519 -N ""

# Display the public key for them to add to GitHub
cat ~/.ssh/id_ed25519.pub
```

Tell the user to add the public key at: **https://github.com/settings/keys**
- Click "New SSH key"
- Paste the public key content
- Give it a title like "hermes-agent-<machine-name>"

**Note for fine-grained PAT users:** If `gh ssh-key add` returns `HTTP 403: Resource not accessible by personal access token`, the PAT lacks the `write:keys` scope. This is common with limited-scope fine-grained PATs. The web UI route above is the only workaround — GitHub doesn't allow SSH key management via non-owner-scoped tokens. After adding the key manually, `git push` via SSH will work regardless of PAT permissions.

**Step 3: Test the connection**

```bash
ssh -T git@github.com
# Expected: "Hi <username>! You've successfully authenticated..."
```

**Step 4: Configure git to use SSH for GitHub**

```bash
# Rewrite HTTPS GitHub URLs to SSH automatically
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**Step 5: Configure git identity**

```bash
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

---

## Method 2: gh CLI Authentication

If `gh` is installed, it handles both API access and git credentials in one step.

### Install (macOS)

```bash
brew install gh
```

Install on other platforms: https://cli.github.com/

### Interactive Browser Login (Desktop)

```bash
gh auth login
# Select: GitHub.com
# Select: HTTPS
# Authenticate via browser
```

### Token-Based Login (Headless / SSH Servers)

If the token is already stored in an env var or `.env` file:

```bash
# From plain env var
echo "$GITHUB_TOKEN" | gh auth login --with-token

# From root ~/.hermes/.env (extract just the token value — do NOT pipe the whole file)
grep "^GITHUB_TOKEN=" ~/.hermes/.env | cut -d= -f2 | gh auth login --with-token
```

**Pitfall — piping the whole `.env` file fails.** `gh auth login --with-token` expects a bare token, not `KEY=value` lines. If you pipe the entire `.env` to stdin, gh tries to use `GITHUB_TOKEN=ghp_...` (including the key and `=` prefix) as the Authorization header value, which produces `net/http: invalid header field value for "Authorization"`. Always extract the value only: `grep "^<KEY>=" <file> | cut -d= -f2`.

**Pitfall — Hermes profile sandboxing (`$HOME` remapping).** When this skill is used from within a Hermes profile, `$HOME` is remapped to `~/.hermes/profiles/<name>/home/`. Running `gh auth login` in the user's real terminal writes the token to `~/.config/gh/hosts.yml`, but Hermes's `gh` reads from the sandboxed `~/.hermes/profiles/<name>/home/.config/gh/hosts.yml` — the two are different files. You'll see `gh auth status` report `✓ Logged in` on the user's terminal but `✗ The token is invalid` from within Hermes.

**Fix — inject from within the Hermes context:** Have the user paste their PAT, then run `echo TOKEN | gh auth login --with-token` from within the Hermes session (not on the user's terminal). This writes to the correct sandboxed path. Then sync the properly-formatted config to the real user's home:

```bash
# After successful gh auth login --with-token inside Hermes:
cp ~/.hermes/profiles/<name>/home/.config/gh/hosts.yml ~/.config/gh/hosts.yml
```

Alternatively, sync in the other direction if the user already authenticated outside:

```bash
# If user already ran gh auth login in their own terminal:
cp /Users/<you>/.config/gh/hosts.yml ~/.hermes/profiles/<name>/home/.config/gh/hosts.yml
gh auth status   # verify it's now valid inside Hermes
```

**Root cause:** Manually editing the YAML is fragile — the file needs both `users.<user>.oauth_token` AND a top-level `oauth_token` field in the correct structure. Using `gh auth login --with-token` guarantees the correct format is written.

After successful login, configure gh to also handle git push/pull credentials:

```bash
gh auth setup-git
```

### Post-setup cleanup: remove stale GITHUB_TOKEN from .env

Once `gh` auth is working (git already wired to use `gh` as its credential helper), the `GITHUB_TOKEN` env var in `~/.hermes/.env` is redundant. Leaving it in place is harmless but can be misleading — tools reading the var directly are bypassing the credential helper. Remove it:

```bash
# Remove the live GITHUB_TOKEN line from the root .env
sed -i '' '/^GITHUB_TOKEN=/d' ~/.hermes/.env

# Profile .env files are typically symlinks to the root, but verify:
ls -la ~/.hermes/profiles/*/.env 2>/dev/null | grep -v "^.*->.*\.env$"
# If any are NOT symlinks, clean them individually too
```

**Why this is safe:** Git's credential helper (`gh auth git-credential`) handles all push/pull/clone auth. API calls via `gh` read from `hosts.yml`. There is no scenario where a stale `GITHUB_TOKEN` in `.env` is needed once `gh auth login` succeeded — it was a fallback for scripts that didn't use `gh` at all.

### Verify

```bash
gh auth status
```

### Post-setup: git identity

If git identity (`user.name`, `user.email`) isn't set yet, configure it:

```bash
git config --global user.name "Your GitHub Username"
git config --global user.email "your-email@example.com"
```

---

## Using the GitHub API Without gh

When `gh` is not available, you can still access the full GitHub API using `curl` with a personal access token. This is how the other GitHub skills implement their fallbacks.

### Setting the Token for API Calls

```bash
# Option 1: Export as env var (preferred — keeps it out of commands)
export GITHUB_TOKEN="<token>"

# Then use in curl calls:
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

### Extracting the Token from Git Credentials

If git credentials are already configured (via credential.helper store), the token can be extracted:

```bash
# Read from git credential store
grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|'
```

### Helper: Detect Auth Method

Use this pattern at the start of any GitHub workflow:

```bash
# Try gh first, fall back to git + curl
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  echo "AUTH_METHOD=gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  echo "AUTH_METHOD=curl"
elif [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
  export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
  echo "AUTH_METHOD=curl"
elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
  export GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
  echo "AUTH_METHOD=curl"
else
  echo "AUTH_METHOD=none"
  echo "Need to set up authentication first"
fi
```

---

## Troubleshooting

See `references/git-push-403-diagnosis.md` for a full systematic diagnosis workflow for push failures.

| Problem | Solution |
|---------|----------|
| `git push` asks for password | GitHub disabled password auth. Use a personal access token as the password, or switch to SSH |
| `remote: Permission to X denied` | Token may lack `repo` scope — regenerate with correct scopes |
| `fatal: Authentication failed` | Cached credentials may be stale — run `git credential reject` then re-authenticate |
| `gh repo fork` → 403 Forbidden | Fine-grained PAT lacks `forks: write` scope. Use web UI fork instead |
| `gh ssh-key add` → 403 Forbidden | Fine-grained PAT lacks `write:keys` scope. Upload the SSH key manually |
| `git push` → 403 denied despite PAT having push | **Fine-grained PAT scoping issue:** The PAT was created with access to specific repos and the target repo wasn't added |
| `ssh: connect to host github.com port 22: Connection refused` | Try SSH over HTTPS port: add `Host github.com` with `Port 443` and `Hostname ssh.github.com` to `~/.ssh/config` |
| `git push` fails despite `gh auth status` showing logged in | **Check for embedded tokens in the remote URL** — an old `https://x-access-token:***@github.com/...` in the remote URL causes git to bypass the credential helper entirely |
| Credentials not persisting | Check `git config --global credential.helper` — must be `store` or `cache` |
| Multiple GitHub accounts | Use SSH with different keys per host alias in `~/.ssh/config`, or per-repo credential URLs |
| `gh: command not found` + no sudo | Use git-only Method 1 above — no installation needed |

---

## PR Lifecycle

Complete guide for managing the PR lifecycle: branch creation, commits, pushing, creating PRs, monitoring CI, auto-fixing failures, and merging.

### Branch Creation

```bash
git fetch origin
git checkout main && git pull origin main
git checkout -b feat/add-user-authentication
```

Branch naming: `feat/`, `fix/`, `refactor/`, `docs/`, `ci/`

### Creating a PR

**With gh:**
```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary\n- Adds login and register API endpoints\n\nCloses #42"
```

**With curl:**
```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d '{"title": "feat: add JWT-based user authentication", "body": "Closes #42", "head": "'$(git branch --show-current)'", "base": "main"}'
```

### Monitoring CI

**With gh:**
```bash
gh pr checks           # One-shot check
gh pr checks --watch   # Watch until all checks finish
```

### Auto-Fixing CI Failures

1. Get failure details: `gh run view <RUN_ID> --log-failed`
2. Fix and push: `git add . && git commit -m "fix: ..." && git push`
3. Verify: Re-check CI status

### Merging

**With gh:**
```bash
gh pr merge --squash --delete-branch
gh pr merge --auto --squash --delete-branch   # Auto-merge when checks pass
```

---

## Code Review

Perform code reviews on local changes before pushing, or review open PRs on GitHub.

### Reviewing Local Changes (Pre-Push)

```bash
git diff main...HEAD --stat        # See scope of changes
git diff main...HEAD               # Full diff
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME"  # Find issues
```

### Reviewing a PR

**With gh:**
```bash
gh pr view 123
gh pr diff 123
gh pr checkout 123
```

**Leave inline comments:**
```bash
gh api repos/$OWNER/$REPO/pulls/123/comments \
  --method POST \
  -f body="This could be simplified with a list comprehension." \
  -f path="src/auth/login.py" \
  -f commit_id="$HEAD_SHA" \
  -f line=45 \
  -f side="RIGHT"
```

**Submit a formal review:**
```bash
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
```

### Review Checklist

- **Correctness:** Does the code do what it claims? Edge cases handled?
- **Security:** No hardcoded secrets, input validation, no SQL injection/XSS
- **Code Quality:** Clear naming, no unnecessary complexity, DRY
- **Testing:** New code paths tested? Happy path and error cases?
- **Performance:** No N+1 queries, appropriate caching
- **Documentation:** Public APIs documented, non-obvious logic commented

---

## Issues Management

Create, search, triage, and manage GitHub issues.

### Viewing Issues

```bash
gh issue list
gh issue list --state open --label "bug"
gh issue view 42
gh issue list --search "authentication error" --state all
```

### Creating Issues

```bash
gh issue create \
  --title "Login redirect ignores ?next= parameter" \
  --body "## Description\nAfter logging in, users always land on /dashboard." \
  --label "bug,backend" \
  --assignee "username"
```

### Managing Issues

```bash
gh issue edit 42 --add-label "priority:high,bug"
gh issue edit 42 --add-assignee username
gh issue comment 42 --body "Investigated — root cause is in auth middleware."
gh issue close 42
gh issue reopen 42
```

### Triage Workflow

1. List untriaged issues: `gh issue list --label "needs-triage" --state open`
2. Read and categorize each issue
3. Apply labels and priority
4. Assign if the owner is clear
5. Comment with triage notes if needed

---

## Repository Management

Create, clone, fork, configure, and manage GitHub repositories.

### Cloning

```bash
git clone https://github.com/owner/repo-name.git
git clone --depth 1 https://github.com/owner/repo-name.git   # Shallow
gh repo clone owner/repo-name
```

### Creating Repos

```bash
gh repo create my-new-project --public --clone
gh repo create my-new-project --private --description "A useful tool" --license MIT --clone
```

### Forking

```bash
gh repo fork owner/repo-name --clone
```

**Keeping a fork in sync:**
```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

### Repository Settings

```bash
gh repo edit --description "Updated description" --visibility public
gh repo edit --enable-wiki=false --enable-issues=true
gh repo edit --enable-auto-merge
```

### Secrets Management (GitHub Actions)

```bash
gh secret set API_KEY --body "your-secret-value"
gh secret list
gh secret delete API_KEY
```

### Releases

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release list
gh release download v1.0.0 --dir ./downloads
```

### GitHub Actions

```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID>
gh workflow run ci.yml --ref main
```

---

## Quick Reference Table

| Action | gh | git + curl |
|--------|-----|-----------|
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name --public` | `curl POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `curl POST /repos/o/r/forks` |
| Create PR | `gh pr create` | `curl POST /repos/o/r/pulls` |
| View PR | `gh pr view N` | `curl GET /repos/o/r/pulls/N` |
| Review PR | `gh pr review N --approve` | `curl POST /repos/o/r/pulls/N/reviews` |
| List issues | `gh issue list` | `curl GET /repos/o/r/issues` |
| Create issue | `gh issue create` | `curl POST /repos/o/r/issues` |
| Create release | `gh release create v1.0` | `curl POST /repos/o/r/releases` |
| Set secret | `gh secret set KEY` | `curl PUT /repos/o/r/actions/secrets/KEY` |
