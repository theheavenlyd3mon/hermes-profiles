---
name: project-workspace
description: Multi-agent project workspace conventions — filesystem layout, shared working copies, project-level AGENTS.md, and sandbox-awareness for Hermes profiles.
version: 1.0.0
author: Senna / Hermes Agent
license: MIT
platforms: [macos, linux]
trigger:
  - "project structure"
  - "workspace conventions"
  - "multi-agent"
  - "project organization"
  - "AGENTS.md"
  - "where should I put"
  - "all agents work on"
  - "project workspace"
  - "knowledge architecture"
  - "knowledge store"
  - "wiki conventions"
  - "shared knowledge"
  - "permanent memory"
  - "agent profile setup"
  - "scratch space"
metadata:
  hermes:
    tags: [workspace, projects, conventions, multi-agent, filesystem]
    related_skills: [github-repo-management, github-auth, writing-plans]
---

IDENTITY: Architect.ConventionEnforcer. Establish and enforce one shared workspace layout so multiple Hermes profiles can work on the same projects without path confusion, duplicated clones, or sandbox isolation.
Law: UniversalConventionFirst — apply pattern to ALL profiles immediately, never leave user to retroactively fill gaps.
WHENUSE: SettingUpNewProfile|MultiAgentProject|Debugging"CantFindRepo"|OnboardingNewAgent. ESPECIALLY:ProfilesHaveSandboxedHome|SharedKnowledgeNeeded|NewAgentNeedsScratchFolder. NoSkip:OnboardingFullSetup{sixSteps}.
REDFLAGS: GHRepoCloneWithoutAbsTarget->SandboxClone|GitCloneWithRelativePath->VerifyPWD|npmStartLaunchesGUI->DocumentHeadlessCmdInAGENTS.md|SymlinkBetweenSandboxAndRealHome->FragileProfileCleanupBreaksIt.
RATIONALIZATIONS: CloneToSandboxAndMoveLater->CloneCorrectlyFirstTime|ProfileHomeIsFineForProjects->SandboxedPathInvisibleToUser|JustTellAgentWhereRepoIs->AGENTS.mdIsSingleSourceOfTruth.
QUICKREF: Diagnose{CheckRealProjectsDir->CheckAllSandboxes->MoveToCanonical->UpdateRemoteURL}->Onboard{CreateScratchFolder->UpdateSCHEMA.md->UpdateIndex.md->AppendLog.md->NoteInSOUL.md->DocumentDomain}.

# Project Workspace

## Core Principle: Universal Convention First

When you establish a pattern for one profile (scratch folder, config path, credential sync), apply it to ALL existing and future profiles immediately — never leave the user to retroactively fill gaps. The user's instinct is "do this for all profiles to mitigate this in the future." Trust and follow that instinct proactively.

Conventions for organizing project files so that multiple Hermes profiles (Senna, Coder, Foreman, Reviewer, etc.) can work on the same projects without path confusion, duplicated clones, or "I can't find the repo" problems.

## The Core Problem

Hermes profiles remap `$HOME` to a sandboxed directory:

```
Real home:         /Users/<you>/
Senna's home:      ~/.hermes/profiles/senna/home/
Coder's home:      ~/.hermes/profiles/coder/home/
Foreman's home:    ~/.hermes/profiles/foreman/home/
```

When any profile uses `~/path` or relative paths for `git clone`, the repo lands in its own sandbox — invisible to the user and to other profiles.

## Knowledge Store Conventions

Hermes profiles also need to share a knowledge base across sessions. The same "one shared copy" principle applies.

### Canonical knowledge stores

The knowledge base is a **unified wiki** inside the Obsidian vault. Both "knowledge" (concepts, research, entities) and "operations" (protocols, conventions, agent scratch spaces, decisions) live in `llm-wiki/`:

```
llm-wiki/                    # Second brain (Karpathy pattern) — unified wiki
├── SCHEMA.md               # Conventions, tag taxonomy, page types
├── index.md                # Content catalog with one-line summaries
├── log.md                  # Append-only action log
├── raw/                    # Immutable source material (articles, papers, transcripts)
├── entities/               # Entity pages (people, orgs, products, models)
├── concepts/               # Concept/topic pages
├── comparisons/            # Side-by-side analyses
├── queries/                # Filed query results
├── alloys/                 # Synthesized pages combining 2+ existing pages
└── operational/            # Agent operations — how we do things, not what we know
    ├── agents/             # Per-agent scratch spaces (senna, foreman, coder, ...)
    ├── protocols/          # Handoff rules, inter-agent contracts, kanban workflow
    ├── conventions/        # Standards, style guides, commit patterns
    └── decisions/          # Architectural decision records with rationale
```

**Team-Wiki is archived.** `Team-Wiki/` was merged into `llm-wiki/operational/` in May 2026. If you encounter references to `Team-Wiki/` in older memory or files, the canonical path is now the `operational/` directory above.

Obsidian vault: `/Users/<you>/Hermes Vault/Hermes/` (PARA structure: `0-Inbox/` through `4-Archive/` plus `icarus/`, `Memory/`, `Daily Notes/`).

**Rules:**
- Durable knowledge (entities, concepts, comparisons) goes to the shared folders, tagged appropriately in frontmatter.
- Scratch notes stay in `operational/agents/<name>/` — transient unless promoted.
- Operational pages (protocols, conventions, decisions) document how the agent system works, not domain knowledge.
- Promotion path: when scratch notes mature, the agent promotes to `concepts/`, `entities/`, or `operational/decisions/` with proper frontmatter, wikilinks, and index entry.

**Why not separate vaults:** Cross-pollination. The researcher finding a paper and the coder finding a related implementation pattern should connect in the same graph. Separate vaults would never discover those links.

### Onboarding a new profile

When creating a new Hermes profile, before first use, run the full setup:

1. Create its scratch folder: `mkdir -p /Users/<you>/Hermes\\ Vault/Hermes/Team-Wiki/profiles/<name>/`
2. Update `SCHEMA.md` — add a row to the agent table in the "Agent Scratch Spaces" section
3. Update `index.md` — add the new agent to the Scratch Spaces table
4. Append to `log.md` — record the new agent with "[YYYY-MM-DD] create | Added agent <name> to scratch spaces"
5. Note the scratch path in the profile's SOUL.md or Mnemosyne memory so the agent knows where to write
6. If the profile has a specific domain (e.g. researcher → raw/ ingest), document that in SCHEMA.md

This ensures every future profile inherits the knowledge architecture without retrofitting. If you forget a step, catch it during `team-wiki/maintain` which will flag missing profile folders.

## The Standard

One shared copy, absolute paths, project-level metadata.

### 1. Canonical location

```
/Users/<you>/projects/<project-name>/
```

All profiles use this absolute path. No `~/` ambiguity. The user sees it in Finder. All agents can `cd` there regardless of which profile is active.

### 2. Project-level metadata: AGENTS.md

Each project root can contain an `AGENTS.md` file that any agent reads when it starts working on that project. This replaces fragmented conventions spread across memory or chat history.

```markdown
# AGENTS.md

## Project
HermesMirror — fork of MagicMirror² (https://github.com/MagicMirrorOrg/MagicMirror)

- `references/agents-md-conventions.md` — AGENTS.md patterns: roadmap, DO NOT launch GUI, worker recovery, HelixMirror example
## Conventions
- npm installs must be vetted before running
- Upstream remote: `upstream` → MagicMirrorOrg/MagicMirror
- Test runner: vitest (not plain jest)
- Lint: ESLint with project config

## Filesystem layout
- ~/projects/HermesMirror/
- Modules: ./modules/
- Config: ./config/
```

See `templates/AGENTS.md` for a starter template. The template has placeholder variables (`{{PROJECT_NAME}}`, `{{USER}}`, etc.) — replace those when creating a real AGENTS.md for a project.

See `references/hermesmirror-agents.md` for a concrete real-world example (the HermesMirror AGENTS.md written during a live session). It shows all sections in practice — tech stack table, key commands, conventions, and the path/sandbox caveat.

See `references/agent-topology.md` for the multi-profile fleet topology map, the current communication model (delegate_task), and how the A2A protocol plugin would enable peer-to-peer communication between profiles — including the single-profile constraint, the multi-gateway workaround, and which profiles benefit most from running as persistent A2A gateways.

### 3. Git remotes

- `origin` → your fork on GitHub
- `upstream` → the original repo (for forks)

Agents always work on `origin`. Push/pull via `gh` credential helper (see `github-auth` skill).

### 4. Shared auth

All profiles use the same `gh` credential, which writes to `~/.hermes/profiles/<name>/home/.config/gh/hosts.yml`. After `gh auth login --with-token` from one profile, sync the config:

```bash
cp ~/.hermes/profiles/senna/home/.config/gh/hosts.yml ~/.config/gh/hosts.yml
```

Each profile's `gh` reads its own sandboxed copy — sync to real home makes it available for manual user terminal use.

## Diagnosing "I can't find the repo"

If the user says a project isn't visible:

```bash
# 1. Check real projects directory
ls /Users/<you>/projects/ 2>/dev/null

# 2. Check all Hermes profile sandboxes
for p in ~/.hermes/profiles/*/; do
  sandbox="${p}home/projects"
  if [ -d "$sandbox" ]; then
    echo "--- ${p##*/} sandbox ---"
    ls "$sandbox"
  fi
done

# 3. If found in a sandbox, move it to canonical location
mv ~/.hermes/profiles/<name>/home/projects/<repo> /Users/<you>/projects/<repo>
```

After moving, update the remote URL if it has an embedded token:

```bash
cd /Users/<you>/projects/<repo>
git remote -v  # check for @github.com patterns
# If embedded token found:
git remote set-url origin https://github.com/<owner>/<repo>.git
```

## Pitfalls

- **Electron / desktop GUI projects: `npm start` launches a full-screen window.** Many projects (Electron, Tauri, etc.) map `npm start` to launching the desktop GUI. When dispatching fix tasks to such projects, workers must verify changes with headless alternatives: `npm run server`, `npm test`, or `npm run config:check` — never `npm start`. Document the headless command in the project's AGENTS.md under Key Commands. Example: HermesMirror uses `npm run server` for headless mode.
- **`gh repo clone` always uses sandboxed HOME.** Never run it bare — always append an absolute target: `gh repo clone owner/repo /Users/<you>/projects/repo`
- **Relative paths in `git clone`** resolve against `$PWD`, which may also be sandboxed. Verify with `pwd` before cloning.
- **Moving a repo that was ahead of origin** — check `git status` first. An unpushed commit needs to be pushed before (or after) the move.
- **Symlinks between sandbox and real home** can work but are fragile — profile directory cleanup or reinstallation can break them. Prefer a single canonical copy.
