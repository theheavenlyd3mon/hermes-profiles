# Reference: HermesMirror AGENTS.md

This is the real AGENTS.md written for the HermesMirror project during a live session. Use it as a concrete example when creating AGENTS.md for other projects — it shows what a complete, production-quality AGENTS.md looks like.

## The File

Path: `~/projects/HermesMirror/AGENTS.md`

```markdown
# HermesMirror

**Type:** MagicMirror² fork — modular smart mirror platform
**Origin:** https://github.com/MagicMirrorOrg/MagicMirror
**Local path:** `~/projects/HermesMirror`
**GitHub (fork):** `<your-github-username>/HermesMirror`
**Upstream remote:** `upstream` (MagicMirrorOrg/MagicMirror)

## Tech stack

- Node.js (JavaScript, CommonJS modules)
- Electron (desktop shell)
- Vitest (test runner)
- ESLint + Prettier + Stylelint + Markdownlint (linting)
- EditorConfig (`.editorconfig`)
- Husky (git hooks)

## Key commands

| Command | What it does |
|---|---|
| `npm test` | Full test suite (vitest) |
| `npm run test:js` | ESLint only |
| `npm run test:css` | Stylelint only |
| `npm run test:e2e` | E2E tests (Playwright) |
| `npm run lint:js --fix` | Auto-fix JS lint |
| `npm run lint:css --fix` | Auto-fix CSS |
| `npm run lint:prettier` | Format everything |
| `npm run config:check` | Validate config |
| `npm run server` | Start headless server |

## Branch strategy

- `master` — main development branch
- Upstream tracked via `upstream/master`
- No `main` branch — the fork uses `master`

## Conventions

- **Indentation:** Tabs (not spaces)
- **Line endings:** LF
- **Style:** Follow existing patterns in the codebase; ESLint/Prettier config is authoritative
- **Tests:** Vitest, only run on changed logic — no need to run full suite for docs/readme edits
- **Commits:** Descriptive messages referencing the change area (e.g. "module: add calendar refresh", "fix: config check crash")
- **Pushing:** Always verify with `git push --dry-run` first

## Agent notes

When working on this project, always `cd ~/projects/HermesMirror` — do not use `~/` paths as Hermes sandboxes `$HOME`. All file references in this repo should use absolute paths or relative paths from the project root.
```

## Key sections to always include

| Section | Purpose |
|---|---|
| **Type + Origin** | What is this project and where did it come from (especially if a fork) |
| **Tech stack** | Language, runtime, test runner, linters — lets agents pick the right tools without guessing |
| **Key commands** | Flat table — the most frequent operations. Agents load this to know what `npm test` runs vs `npm run lint:js` |
| **Branch strategy** | Which branch is the main one, upstream tracking — prevents accidental pushes to wrong branch |
| **Conventions** | Project-specific rules that aren't in the linter config — tabs vs spaces, commit style, test scope |
| **Agent notes** | Path caveats, sandbox gotchas, any Hermes-specific setup needed |

## What NOT to put in AGENTS.md

- **Personal preferences** of a specific agent (belongs in user profile / memory)
- **Transient task state** ("currently working on the calendar module") — that's session context
- **Full API docs** — link to external docs or skill references instead
- **Environment-specific paths** that change per machine — keep the path to the local copy only
- **Detailed explanations** — the AGENTS.md is a cheat sheet, not a tutorial. Link out for depth
