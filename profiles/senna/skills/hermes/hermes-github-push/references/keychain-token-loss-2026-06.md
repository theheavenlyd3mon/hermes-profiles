# Case Study: macOS Keychain Token Loss (June 2026)

## Symptoms
- `gh auth status` showed "✓ Logged in" via `GITHUB_TOKEN` env var
- `gh api user` returned 401 Bad Credentials
- `gh auth token` returned "no oauth token found"
- `~/.config/gh/hosts.yml` had NO `oauth_token` field (only user/git_protocol)
- User ran `gh auth login -h github.com -p https --web` successfully in real terminal
- Token STILL didn't persist — `gh auth token` still empty after login

## Root Cause
macOS Keychain entry for `gh:github.com` was corrupted or inaccessible. The `gh` CLI on macOS stores OAuth tokens in the system Keychain by default, NOT in `hosts.yml`. When the Keychain entry is stale/corrupted:
- `gh auth login` appears to succeed but can't write the token
- `hosts.yml` never gets an `oauth_token` field
- Git push fails because there's no credential to use

## What Failed
1. `GITHUB_TOKEN=*** gh auth status` — showed success (misleading — status check is lightweight)
2. `GITHUB_TOKEN=*** gh api user` — 401 (token was actually invalid)
3. `gh auth setup-git` — no effect (no token to wire)
4. `git -c credential.helper='!gh auth git-credential' push` — no token to use
5. Embedding token in remote URL — token was bad, same 401

## What Would Have Worked
```bash
# Delete corrupted Keychain entry
security delete-generic-password -s "gh:github.com" 2>/dev/null

# Re-login (fresh Keychain entry)
gh auth login -h github.com -p https --web

# Verify token actually persisted
gh auth token | head -c 20

# Then push
git push
```

## Lesson
Always verify `gh auth token` returns a real value AFTER `gh auth login`. "✓ Logged in" is not proof of persistence.
