# Real-World Hermes Audit — May 14, 2026

> **Update (2026-05-28):** `hermes-office/` (1 GB) was removed. `~/hermes-solar-system/` (78 MB) was also deleted. Total `~/.hermes` is now ~11 GB.

Audit of a multi-profile Hermes installation (10 profiles: senna, architect, coder, debugger, researcher, reviewer, secretary, security, data-analyst, foreman, devops). Senna is the active personal profile.

## Summary

| Category | Size |
|----------|------|
| Total `~/.hermes` | 12 GB |
| Disk | 233 GB total, 85 GB used, 134 GB free (39%) |

## Biggest Consumers

### 1. Senna Profile Home (6.1 GB)
- `home/hermes-workspace/node_modules/` — 1.5 GB (companion app deps)
- `home/Library/pnpm/store/` — 1.3 GB (global npm store)
- `home/Library/Caches/camoufox/` — 685 MB (browser profiles)
- `home/Library/Caches/ms-playwright/` — 542 MB (browser binaries)
- `home/Library/Caches/Homebrew/` — 203 MB
- `home/Library/Caches/electron/` — 116 MB
- `home/Library/Caches/node-gyp/` — 62 MB
- `home/Library/Caches/pip/` — 60 MB

### 2. Duplicate Repo Checkouts (2.5 GB)
- `~/.hermes/hermes-agent/` — 1.7 GB (venv: 755M, web: 252M, ui-tui: 214M, node_modules: 136M, .git: 319M)
- `~/.hermes/profiles/senna/hermes-agent/` — 824 MB (separate checkout, not symlink; .git: 227M, venv: 173M, node_modules: 136M)
- `~/.hermes/hermes-office/` — 1.0 GB (separate Next.js project)

### 3. State Snapshots (1.2 GB)
- 19 pre-update snapshots in `profiles/senna/state-snapshots/`
- Range: 21 MB (oldest, May 8) to 145 MB (newest, May 14)

### 4. Orphaned Old .hermes (641 MB)
- At `profiles/senna/home/.hermes/` — pre-profile-migration leftover
- `mnemosyne/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` — 638 MB, NOT referenced by any profile config
- Contains stale mnemosyne.db and old plugins/hermes-lcm copy

### 5. Other Profile Data (~300 MB)
- Sessions: 133 MB (senna), ~3.6 MB each for coder/reviewer/researcher
- Logs: 15 MB (senna), minor for others
- Checkpoints: senna 1.3M, coder 31M (largest), others small

## Audit Commands Used

```bash
# Broad scan
du -sh ~/.hermes/
du -sh ~/.hermes/*/ | sort -rh

# Profile drill-down
du -sh ~/.hermes/profiles/senna/*/ | sort -rh

# Home cache drill-down
du -sh ~/.hermes/profiles/senna/home/Library/Caches/*/ | sort -rh

# Check for duplicate repos
ls -la ~/.hermes/profiles/senna/hermes-agent  # not a symlink → separate checkout
du -sh ~/.hermes/hermes-agent/
du -sh ~/.hermes/profiles/senna/hermes-agent/

# Orphaned model check
find ~/.hermes -name "*.gguf" -type f
grep -ri "tinyllama\|gguf" profiles/senna/config.yaml .env

# State snapshots
ls ~/.hermes/profiles/senna/state-snapshots/ | wc -l
du -sh ~/.hermes/profiles/senna/state-snapshots/*/ | sort -rh

# Checkpoint sizes per profile
for p in ~/.hermes/profiles/*/; do
  name=$(basename "$p")
  sz=$(du -sh "$p/checkpoints" 2>/dev/null | cut -f1)
  [ -n "$sz" ] && echo "$name checkpoints: $sz"
done

# Stale DB backups
find ~/.hermes -name "*.pre_e*_backup" -type f
```
