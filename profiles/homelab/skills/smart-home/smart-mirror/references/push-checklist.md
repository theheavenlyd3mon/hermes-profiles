# HermesMirror Pre-Push Checklist — Updated 2026-05-13

## The Problem

MagicMirror's `.gitignore` line 58: `/modules/*` ignores all modules. New Hermes modules are invisible to `git status` and excluded from commits. The repo shows "working tree clean" even though your modules exist on disk.

## Checklist

```bash
cd ~/projects/HermesMirror

# 1. Force-add modules (bypass gitignore)
git add -f modules/hermes-bridge modules/hermes-dashboard modules/hermes-status

# 2. Verify modules are actually tracked
git ls-files modules/
# Expected: all 9 files listed (3 modules × ~3 files each)

# 3. Config validation
npm run config:check
# Expected: syntax and structure both pass

# 4. ESLint (check for new errors only)
npm run lint:js 2>&1 | tail -5
# Pre-existing errors are fine — look for NEW errors in modules/

# 5. Stylelint
npm run lint:css
# Expected: clean

# 6. Unit tests (headless only)
npx vitest run --project=unit
# Expected: 357 pass, 1 fail (systeminfo expects "platform: linux" — pre-existing macOS issue)

# 7. Syntax check on Node helper files
node -c modules/hermes-bridge/node_helper.js
node -c modules/hermes-dashboard/hermes-dashboard.js
node -c modules/hermes-status/hermes-status.js
```

## Commit strategy

Separate your work from the fork baseline. See `magicmirror-hermes-integration` skill for the fork baseline branch pattern.

## Pre-Existing Failures (don't block)

| Check | Expected | Why |
|---|---|---|
| Vitest unit tests | 357 pass, 1 fail | systeminfo expects "linux" — pre-existing on macOS |
| ESLint | ~6-12 errors | pre-existing in defaultmodules and server files |
| Package files | may be modified | pinned versions, audit fixes from fork setup |
| Translations | may be modified | upstream MM2 translation updates |
