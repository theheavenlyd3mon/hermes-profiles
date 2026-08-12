---
name: system-audit
description: >-
  Systematic audit of all installed tools, packages, and dependencies for
  available updates. Covers Homebrew, pip, npm/pnpm, system software updates,
  git repos, and key CLI tools. Run when the user asks "check if anything needs
  updating" or similar maintenance queries.
category: devops
triggers:
  - check for updates
  - what's outdated
  - audit installed tools
  - what needs upgrading
  - review versions
  - anything new available
  - system maintenance
  - mac is hot
  - what's running
  - something is slow
  - cpu hog
  - memory pressure
---

IDENTITY: Auditor.InventoryScanner. Run parallel checks across all package managers (brew,pip,npm,pnpm,node,git,softwareupdate) and compile a single structured update report.
Law: NeverUpgradeSystemPip — it breaks macOS.
WHENUSE: UserAsks{CheckUpdates,WhatsOutdated,AnythingNeedUpgrading,SystemMaintenance}. ESPECIALLY:AfterMajorHermesUpdate->PostUpdateVerification{PluginHealth+ToolHealth}. NoSkip:PostUpdateSmokeTests.
REDFLAGS: SystemPipOutdated->FlagButLeaveAlone|nvmNotFound->ShellFunctionNotExecutable|pnpmCorepack->GlobalVersionMayNotMatter|GitHubRateLimited->UseBrewInfoFallback.
RATIONALIZATIONS: UpgradeSystemPythonLibs->BreaksMacOS|SkipPostUpdateCheck->PluginMayBeBroken|JustShowRawLog->GroupIntoSections{NoAction,UpdateAvail,DontTouch}.
QUICKREF: Scan{Homebrew{formulae+casks}->pip+pipx->npm+pnpm+yarn->node{LTS+latest}->KeyCLI{gh,bun,tmux,pnpm}->GitRepos->macOSSoftwareUpdate}->Compile{GroupBySection->NoteVersionDelta->FlagMajorVsMinor}->Verify{PluginHealth{hermes plugins list+hermes tools list}->GitPluginIntegrity->SmokeTestCriticalTools}.

Run this when the user asks a general "what's outdated" / "check for updates" /
"anything need upgrading" question. Covers all package managers and common
sources of updates on a macOS system.

## Order of Checks

Run these in parallel where possible, then compile a single report.

### 1. Homebrew (formulae + casks)

```bash
brew outdated                  # formula updates
brew outdated --cask          # cask updates (GUI apps)
```

Check both. `brew outdated` auto-updates taps so you get current data.

### 2. pip / pipx

```bash
# System Python pip (be careful - upgrading system libs can break macOS)
python3 -m pip list --outdated --format=columns

# pipx-managed tools
pipx list 2>/dev/null
```

### 3. npm / pnpm / yarn

```bash
# Global npm packages
npm ls -g --depth=0

# pnpm version vs latest on npm
pnpm --version
npm view pnpm version

# yarn version vs latest on npm
yarn --version
npm view yarn version
```

### 4. Node.js version

```bash
node --version
# Check latest LTS:
curl -s https://nodejs.org/dist/index.json | python3 -c \
  "import sys,json; d=json.load(sys.stdin); lts=[v for v in d if v['lts']]; print(lts[0]['version'], lts[0]['lts'])"
# Check latest overall:
curl -s https://nodejs.org/dist/index.json | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d[0]['version'])"
```

### 5. Key CLI tools

For each tool installed, check version vs latest release:

```bash
# gh CLI
gh --version
curl -sI https://github.com/cli/cli/releases/latest | grep -i location | sed 's/.*tag\///'

# bun
bun --version
curl -sI https://github.com/oven-sh/bun/releases/latest | grep -i location | sed 's/.*tag\///'

# tmux
tmux -V
curl -sI https://github.com/tmux/tmux/releases/latest | grep -i location | sed 's/.*tag\///'

# pnpm
pnpm --version
curl -sI https://github.com/pnpm/pnpm/releases/latest | grep -i location | sed 's/.*tag\///'
```

### 6. Cloned git repos

Find manually cloned repos and check if they're behind upstream:

```bash
find ~ -maxdepth 3 -name ".git" -type d 2>/dev/null | grep -v hermes-workspace | grep -v ".nvm" | head -20
```

For each: `cd` in, `git remote -v`, `git fetch --dry-run`, `git log --oneline HEAD..origin/main` (or `master`).

### 7. macOS system updates

```bash
softwareupdate --list
```

### 8. Mnemosyne Memory System

Check Mnemosyne health and dependency status:

```bash
# Quick status check
hermes memory              # shows plugin status, active provider

# Check installed version vs PyPI latest
~/.hermes/hermes-agent/venv/bin/pip3 show mnemosyne-memory 2>/dev/null | grep Version
# Compare with https://pypi.org/project/mnemosyne-memory/

# Key deps for full hybrid search (vector + FTS5 + importance):
# - mnemosyne-memory: core package (v3.1.0+)
# - fastembed: semantic embeddings (BAAI/bge-small-en-v1.5)
# - sqlite-vec: vector similarity search in SQLite
# Without fastembed+sqlite-vec, falls back to FTS5 keyword-only search.
```

**To install/upgrade (skip llama-cpp-python — it builds from source on Intel Mac):**
```bash
~/.hermes/hermes-agent/venv/bin/pip3 install mnemosyne-memory fastembed sqlite-vec
```

**Post-install:** A Hermes restart is required — the running agent process loads deps at startup, so newly installed packages won't be detected until restart.

**Pitfall:** `pip install "mnemosyne-memory[all]"` includes `llama-cpp-python` and `ctransformers` which build from source and hang on Intel Macs. Install core + fastembed + sqlite-vec individually instead.

## Compilation Rules

- Group into sections: "No action needed" / "Updates available" / "Don't touch"
- For "Don't touch", explain why (e.g. system Python libs break macOS)
- For "Updates available", note the version delta
- Flag major version jumps vs minor patches
- If a tool's installed version matches latest, say so

## Pitfalls

- **System Python pip** is deliberately old (21.x). Upgrading it or setuptools/wheel via pip can break macOS tools. Flag but recommend leaving alone unless something is actually broken.
- **nvm** is a shell function, not an executable — `which nvm` fails. Use `NVM_DIR="$HOME/.nvm"` or the nvm function if sourced.
- **pnpm** installed via corepack: the global version is controlled by corepack. Projects pin their own version via `packageManager` in `package.json`. Upgrading the global pnpm may have no practical effect.
- **`git fetch --dry-run`** fetches new refs but doesn't update HEAD — check origin/main vs HEAD after a real fetch.
- Some GitHub API calls (`api.github.com/repos/.../releases/latest`) may be rate-limited without authentication.
- **`ffmpeg` version tags on GitHub** don't use standard SemVer — check `brew info ffmpeg` for the version delta instead.
- **Pip-installed plugins get wiped on venv recreation.** If `hermes update` or a profile migration recreates the venv, packages installed via pip (not declared in requirements.txt) vanish. Known casualties: `rtk-hermes` (RTK command rewriting plugin), `mnemosyne-memory` (memory provider). After ANY venv recreation, run `pip3 show rtk-hermes mnemosyne-memory` and reinstall missing packages. Git-installed plugins in `~/.hermes/plugins/` are NOT affected — they survive venv changes.
- **`plugins.enabled` can become a stringified JSON string.** If set via `hermes config set`, the YAML value may become `enabled: '["list","of","plugins"]'` (a string) instead of a proper YAML list. The plugin loader may not parse this correctly. Fix: rewrite as a proper YAML list using Python yaml.dump. Always verify with `grep -A 20 "^plugins:" config.yaml` — the enabled list should show `- item` lines, not a single quoted string.
- **`mnemosyne-memory[all]` builds llama-cpp-python from source** which hangs on Intel Macs (>120s). Install core + key extras individually instead: `pip install mnemosyne-memory fastembed sqlite-vec`.

## Example Output Structure

```
**No action needed — up to date:**
- gh v2.92.0 ✓
- bun v1.3.13 ✓

**Updates available:**
- ffmpeg: 8.1_1 → 8.1.1 (brew)
- macOS Sequoia 15.7.7 (system, requires restart)

**Don't touch:**
- System pip (21.2.4 → 26.0.1 available - upgrading breaks macOS)
```

## Post-Update Verification

After upgrading anything, there are two follow-ups the user may want:

### 1. Plugin & Tool Health Check

Verify Hermes plugins and toolsets are still loaded and functional:

```bash
hermes plugins list       # check all plugins show "enabled"
hermes tools list          # check built-in and plugin toolsets show ✓ enabled
hermes memory              # check mnemosyne plugin is "installed ✓" and "active"
```

**Critical: check pip-installed plugins survive venv changes:**
```bash
# These get wiped if the venv was recreated during update
~/.hermes/hermes-agent/venv/bin/pip3 show rtk-hermes 2>&1
~/.hermes/hermes-agent/venv/bin/pip3 show mnemosyne-memory 2>&1
# If "not found", reinstall immediately
```

For git-installed plugins, verify the repo is intact:
```bash
ls $HERMES_HOME/plugins/<name>    # dir exists
cd $HERMES_HOME/plugins/<name> && git log --oneline -1   # git history intact
```

If any show as "not enabled" after an update, re-enable with:
```bash
hermes plugins enable <name>
```

### 2. Show What Changed in an Update

When the user asks "what changed from the version we had" for a git-pulled plugin or repo:

```bash
# If you know the OLD commit (e.g. from reflog or the previous tag):
cd <repo-path> && git log <old-ref>..HEAD --oneline --no-decorate

# If plugin has a plugin.yaml with version:
head -5 plugin.yaml   # check current version
git tag | tail -5     # see tags for changelog reference
git log --oneline <prev-tag>..HEAD   # changes between tags

# Alternative: find the previous state from reflog:
git reflog --date=iso | head -5      # shows when last pull/clone happened
```

Group the output by version/release (e.g., "v0.10.0 — key change, v0.10.1 — fix X") so the user gets a readable summary, not a raw log dump.

### 3. Smoke Test Critical Tools

For non-Hermes upgrades (brew formulas, etc.), do a quick sanity check:

```bash
<tool> --version         # confirm new version
<tool> --help            # basic invocation still works
```

Cross-reference against Hermes plugin dependencies — if the upgraded tool is used by any plugin, check the plugin's tool listing still shows ✓ enabled.

## Reference Files

- `references/post-update-sweep-checklist.md` — quick parallel checklist for post-update verification, known recovery commands, and symptom→cause table.
- `references/runtime-diagnostics.md` — macOS runtime diagnostics: CPU hog identification, memory pressure checks, process tree tracing, daemon management. Use when the user says "my Mac is hot", "what's running", or "something is slow".
