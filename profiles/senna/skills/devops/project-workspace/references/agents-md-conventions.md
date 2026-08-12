# AGENTS.md Convention Patterns

These patterns were established during the HermesMirror project setup. They serve as a template for any project that uses Hermes Kanban for multi-agent work.

## Sections every project AGENTS.md should have

1. **Project identity** — type, origin, local path, GitHub repo, upstream
2. **Tech stack** — languages, frameworks, test runner, linters
3. **Key commands** — the commands workers need to know: test, lint, format, config check, headless server
4. **Branch strategy** — which branch to work on, any special rules
5. **Conventions** — indentation, line endings, style guide, commit format, pushing rules
6. **Agent notes** — absolute paths, sandbox behavior, special working directory rules

## Critical pattern: DO NOT launch GUI section

For any project with a desktop GUI (Electron, Tauri, Qt, etc.), add this section:

```markdown
### ⚠️ DO NOT launch GUI

`npm start` launches the [Electron] desktop app full-screen. Never use this for testing.

**Use these headless alternatives instead:**

| Command | Purpose |
|---|---|
| `npm test` | Run test suite (no GUI) |
| `npm run server` | Start HTTP server only for dev testing |
| `npm run config:check` | Validate config |
```

Why this matters: Kanban workers don't know they're on a user's desktop — they'll run `npm start` to test changes, launching a full-screen window on an unsuspecting user. The AGENTS.md must be the single source of truth for which test commands are safe.

Every kanban task body for that project should reference the AGENTS.md convention or include the headless command explicitly.

## Roadmap section

For active projects, add a roadmap to help agents (and human reviewers) understand what's in progress vs planned:

```markdown
## Roadmap

### Active (current phase)
- **Feature A** — short description
- **Feature B** — short description

### Future
- **Feature C** — short description
```

This prevents agents from building features that overlap with planned work. Update the roadmap when a phase completes so dispatched workers always see current state.

## Worker recovery pattern

When a worker launches the GUI despite AGENTS.md rules:
1. Reclaim the task immediately (`hermes kanban reclaim t_<id>`)
2. Check `git status` — worker's code changes are still in the working tree (not lost)
3. Complete the task manually if the changes are correct
4. Re-dispatch with explicit "do not launch GUI" instructions in the body

## HelixMirror example (working template)

The file at `~/projects/HermesMirror/AGENTS.md` serves as a live reference. It includes:
- Roadmap with Active and Future sections
- DO NOT launch Electron section with headless command table
- Agent notes with absolute path requirements
