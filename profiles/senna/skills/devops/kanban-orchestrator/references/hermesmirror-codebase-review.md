# HermesMirror Codebase Review — Session Reference

This file documents the concrete codebase review pattern used during the first kanban task for the HermesMirror project. It serves as a worked example for the "Phased Codebase Review" pattern in the skill.

## Context

- Project: HermesMirror (MagicMirror² fork) at ~/projects/HermesMirror
- Codebase: 230 JS files, 12 CSS files, 167 test files, 23 deps + 23 dev deps
- 3 parallel Phase A workers, all independent (no parent links)
- Workers dispatched via `hermes kanban dispatch` directly (no cron wait)

## Task Design

### Architecture Review (→ architect)

```
Title: "arch: HermesMirror architecture review"
Body: Review the HermesMirror codebase at ~/projects/HermesMirror.
Focus: overall architecture — module system, Electron shell, server/client split, IPC patterns, dependency graph, module lifecycle, config system, socket communication.
Provide your findings with file paths and a structural diagram of how components connect.
This is read-only analysis — do not make changes.
Workspace: dir:~/projects/HermesMirror
```

### Code Quality Review (→ reviewer)

```
Title: "review: HermesMirror code quality review"
Body: Review the HermesMirror codebase at ~/projects/HermesMirror.
Focus: code quality — JavaScript patterns, CommonJS module structure, error handling, test coverage (167 test files, vitest), duplication across modules, adherence to project conventions (tabs, LF, EditorConfig).
Check each default module (calendar, clock, weather, newsfeed, compliments, alert, helloworld) for consistent patterns.
This is read-only analysis — do not make changes.
Workspace: dir:~/projects/HermesMirror
```

### Security Audit (→ security)

```
Title: "sec: HermesMirror security audit"
Body: Audit the HermesMirror codebase at ~/projects/HermesMirror.
Focus: security — npm audit of 23 production dependencies and 23 dev dependencies, Electron security practices (nodeIntegration, contextIsolation, CSP), input validation in HTTP server (port 8080), IP whitelisting logic, dependency vulnerability scan, and overall attack surface.
Run: npm audit --omit=dev
Check Electron main process for secure defaults.
This is read-only analysis — do not make changes.
Workspace: dir:~/projects/HermesMirror
```

## Observed Runtimes (230 JS files, macOS)

| Worker | Profile | Runtime | Output format |
|---|---|---|---|
| Architecture review | architect | ~6 min (346s) | File: `ARCHITECTURE_REVIEW.md` (415 lines) with structural diagrams |
| Security audit | security | ~7 min (393s) | Comment with table of findings by severity (1 CRIT, 3 HIGH, 3 MED, 2 LOW) |
| Code quality review | reviewer | ~8 min (503s) | Blocked with `review-required`, structured JSON in comment (5 important, 4 minor) |

## Worker Output Diversity

- **Architect**: writes a file to the workspace (ARCHITECTURE_REVIEW.md). The summary says "written to file." Read the file for the full output.
- **Security**: posts a long comment with a severity table. The summary gives a severity count breakdown. Read the comment text.
- **Reviewer**: blocks with `review-required` and posts a structured JSON comment with `{findings: [{severity, file, line, issue}], positives: [], verdict: "REQUEST_CHANGES"}`. Unblock after user review.

## Dispatching

All 3 tasks were created first, then dispatched once:
```bash
hermes kanban dispatch
# Output: Spawned: 3
#   - t_c9acdaf2  ->  architect  @ ~/projects/HermesMirror
#   - t_633bbc39  ->  reviewer   @ ~/projects/HermesMirror
#   - t_1e36ee6f  ->  security   @ ~/projects/HermesMirror
```

No Foreman cron needed — direct dispatch works for immediate execution.

## Polling Strategy

Used `hermes kanban list --json | python3` filtering for the HermesMirror tasks only:
```bash
hermes kanban list --json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for t in data:
    if t.get('id','').startswith('t_c9') or t.get('id','').startswith('t_633') or t.get('id','').startswith('t_1e'):
        print(f'{t[\"id\"]:16} [{t[\"status\"]:8}]')
"
```

## Pitfall: Workers that launch GUI apps

The code quality fix task (coder profile) ran `npm start` to test its changes, which launched the HermesMirror Electron app full-screen. The coder is a subprocess and doesn't know about the user's desktop — it just runs the test command it knows. This was fixed by:

1. Adding a `### DO NOT launch GUI` section to `AGENTS.md` with headless alternatives
2. Patching the `kanban-orchestrator` skill with a general pitfall about GUI apps
3. Reclaiming the task and reviewing the changes manually

Workers that were reclaimed mid-flight leave their code changes in the working tree (`git diff` still shows them). No work is lost.

## Pitfall: Don't reclaim worker that looks "dead"

The code quality verification task (reviewer profile) was reclaimed 3 times because `ps aux` showed no process, but it was actively working each time. Kanban workers are subprocesses invisible from the parent sandbox. A `running` status with a non-expired claim means the worker is alive. Check run duration on `kanban show` instead:
- Run 46 ran 270s before reclaim (legitimate analysis)
- Run 47 ran 196s before reclaim (still working)
- Run 48 ran 74s before reclaim (just started)

Worker was eventually killed by manual reclaim, never by crash.

## Phase B — Fix Tasks

After the user greenlit the findings, two parallel fix tasks were created, each gated behind a Phase A parent:

```
T1 (security review) ──→ T4 (security fixes, coder)
T2 (code quality review) ──→ T5 (code quality fixes, coder)
```

Both fix tasks created simultaneously with `--parent` links. Dependency engine promotes them from `todo → ready` when the parent completes.

### Task body pitfalls

Writing task bodies inline with long markdown and characters like arrows (→) confused the shell. Error: "Foreground command uses '&' backgrounding". Fix: write the body to a temp file and inject via `--body "$(cat /tmp/body.md)"`. See the skill's pitfalls section for the complete pattern.

**Alternative — python3 for body file creation.** When the body itself contains `&`, heredocs, or other shell metacharacters, `python3 -c` avoids the escaping problem entirely:

```bash
python3 -c "
body = '''Your task body here with & and other special chars.'''
with open('/tmp/task-body.txt', 'w') as f:
    f.write(body)
"
hermes kanban create 'title' --assignee <profile> --body "$(cat /tmp/task-body.txt)"
```

This is cleaner than `cat > /tmp/file << 'EOF'` when the body contains ampersands, backticks, or nested quotes. The heredoc approach works fine for bodies without special characters.

## Phase C — Verification Tasks

After fix tasks completed, verification tasks (reviewer) checked each fix point:

```
T4 (security fixes) ──→ T6 (verify security, reviewer)
T5 (code quality fixes) ──→ T7 (verify code quality, reviewer)
```

Verification tasks list every original finding and ask the reviewer to confirm each is resolved, reporting `clean=true` in metadata.

## Key Commands from This Session

| Action | Command |
|---|---|
| Create task with file-injected body | `hermes kanban create "title" --assignee <p> --body "$(cat /tmp/body.md)" --workspace "dir:/path" --parent t_<id> --json` |
| Complete a task | `hermes kanban complete t_<id> --summary "..."` |
| Reclaim (abort running) | `hermes kanban reclaim t_<id>` |
| Unblock (stuck task) | `hermes kanban unblock t_<id>` |
| Dispatch ready tasks | `hermes kanban dispatch` |
| Verify if alive | `hermes kanban show t_<id> | grep -E "^  status:"` (reliable) — `ps aux` is NOT reliable |
| Kill Electron if opened | `pkill -f "electron js/electron.js"`
