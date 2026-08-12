# Profile Repo Mirror — Refresh from Live Profiles

Use this when the user has an existing GitHub repo of Hermes profiles and wants to sync it from `~/.hermes/profiles/`.

## Sequence

1. Confirm intended profiles to copy.
2. Copy profile directories into the repo mirror.
3. Strip runtime artifacts.
4. Mark local-only profiles as non-portable.
5. Sanitize personal paths/usernames.
6. Verify with grep checks.
7. Commit and push with scoped message.

## Copy Command

```bash
cp -Rn ~/.hermes/profiles/<profile-name> /path/to/repo/profiles/
```

Repeat per profile. Do not copy the entire `~/.hermes/profiles/` tree.

## Runtime Strip List

Remove before committing:

- `.env`, `.env.bak`, `.env.*`
- `logs/`, `logs/*.log`
- `state.db`, `state.db-wal`, `state.db-shm`
- `cache/`, `sessions/`, `spawn-trees/`
- `.hermes_history`, `.hermes_history.lock`
- `.DS_Store`, `Thumbs.db`
- `*.lock`, `*.jsonl`
- `auth.json`, `auth.lock`

Quick cleanup:

```bash
find /path/to/repo/profiles -maxdepth 3 \( \
  -name '.env' -o -name '.env.bak' -o -name 'state.db*' -o -name '*.lock' \
  -o -name '*.log' -o -name '.DS_Store' \
\) -delete
```

## Local-Only Profile Handling

Examples: `educate`.

Treat as specialized/non-portable:
- Strip all runtime artifacts.
- Sanitize paths and usernames.
- Keep only `SOUL.md`, `README.md`, and skill files.
- Add a short note in the profile README that it is local-only/specialized.

## Verification

```bash
# Username leakage
grep -rn '<user>' /path/to/repo/profiles --include='*.md' || true

# Hardcoded home paths
grep -rn '/Users/' /path/to/repo/profiles --include='*.md' | grep -v '<you>\|<user>\|name/\|*/' || true
```

## Commit Message Pattern

```bash
git add -A
git commit -m "Refresh profiles: <list>

- Stripped runtime artifacts
- Sanitized personal paths/usernames"
```
