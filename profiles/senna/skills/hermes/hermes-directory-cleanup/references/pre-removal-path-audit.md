# Pre-Removal Path Audit

Before removing any directory under `~/.hermes/`, verify nothing references it.
A directory that looks dead may be referenced by configs, services, or plugins.

## Audit Checklist

Run each check. If ALL return empty, the directory is safe to remove.

```bash
TARGET="profiles/senna/hermes-agent"  # relative to ~/.hermes/

# 1. Config files (yaml, yml, json, env, plist, conf, toml)
grep -r "$TARGET" ~/.hermes/ \
  --include="*.yaml" --include="*.yml" --include="*.json" \
  --include="*.env" --include="*.plist" --include="*.conf" --include="*.toml" \
  2>/dev/null | grep -v ".git/" | grep -v "venv/" | grep -v "__pycache__"

# 2. Launchd plists
grep -r "$TARGET" ~/Library/LaunchAgents/ /Library/LaunchDaemons/ 2>/dev/null

# 3. Shell profiles
grep -r "$TARGET" ~/.zshrc ~/.zprofile ~/.bashrc ~/.bash_profile ~/.profile ~/.zshenv 2>/dev/null

# 4. Other profile configs
grep -r "$TARGET" ~/.hermes/profiles/*/config.yaml 2>/dev/null

# 5. Cron job configs
grep -r "$TARGET" ~/.hermes/profiles/*/cron/ 2>/dev/null

# 6. Plugin symlinks
find ~/.hermes/plugins -type l -exec sh -c 'readlink "$1" | grep -q "$TARGET" && echo "$1"' _ {} \;

# 7. .env files across all profiles
find ~/.hermes/profiles -name ".env" -exec grep -l "$TARGET" {} \; 2>/dev/null
```

## What Counts as a Live Reference

| Source | Verdict |
|--------|---------|
| Config yaml/json/env | **Block removal** — fix the reference first |
| Launchd plist | **Block removal** — service will break |
| Shell profile | **Block removal** — PATH or env var depends on it |
| Other profile config | **Block removal** — cross-profile dependency |
| Cron job config | **Block removal** — scheduled task will fail |
| Plugin symlink | **Block removal** — plugin will break |
| Cron output/log files | Safe — historical data, not live references |
| Session transcripts | Safe — historical data |
| Memory/fabric entries | Safe — informational only |

## After Confirming No References

1. Check for uncommitted changes: `cd <target> && git status --short`
2. Check for unique untracked files: `git ls-files --others --exclude-standard`
3. Compare venv packages if applicable: `diff <(pip list) <(other-pip list)`
4. Compare .env files for unique API keys
5. Present findings to user with size and confirmation to proceed
