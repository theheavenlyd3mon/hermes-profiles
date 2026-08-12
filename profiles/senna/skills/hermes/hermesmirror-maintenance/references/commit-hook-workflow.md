# Commit workflow in HermesMirror — husky + lint-staged gotchas

The repo has a husky `pre-commit` hook that runs `npx lint-staged`. Config (in
`package.json` under `lint-staged`):

```json
{
  "*": "prettier --ignore-unknown --write",
  "*.js": "eslint --fix",
  "*.css": "stylelint --fix"
}
```

Four gotchas hit during the 2026-07-20 security-hardening commit (`c3183047`).

## 1. `git add` refuses `modules/*` paths — use `git add -f`

`.gitignore` lists `/modules/*` (MagicMirror² convention — modules are normally
per-install). But the four `hermes-*` modules ARE tracked (force-added
historically). So a plain `git add modules/hermes-chat/hermes-chat.js` fails:

```
The following paths are ignored by one of your .gitignore files:
modules/hermes-chat
hint: Use -f if you really want to add them.
```

**Fix:** stage in two passes — normal add for non-ignored files, `-f` for modules:

```bash
git add AGENTS.md config/config.js docs/... package.json package-lock.json tests/...
git add -f modules/hermes-bridge/*.js modules/hermes-chat/*.js
```

(`config/config.js` is ALSO force-added/tracked despite being in `.gitignore`
line ~28 — same treatment.) Verify with `git diff --cached --stat` and
`git status --short` (first-column `M` = staged).

## 2. lint-staged reformats WHOLE files, not just your hunks

`prettier --write` (not `--check`) runs on every staged file and normalizes the
entire file — table alignment, whitespace, quote style. A 10-line edit to
`AGENTS.md` became a 72-line diff; a 6-line design-doc edit became 45 lines.

**This is expected, not corruption.** But after the commit lands you MUST
re-verify substance survived the reformat:
- `npx vitest run tests/unit/modules/hermes-chat` (29/29)
- `npm run lint:js` (0 errors)
- grep for your key content (token-gate strings, version pins, doc claims)

## 3. Prettier SyntaxError on ` ```js ` fences in Markdown

Prettier parses embedded ` ```js ` code blocks as JS programs. A fence holding a
**bare object literal with `//` comments** is not valid statement-context JS:

```js
{
    module: "hermes-chat",
    position: "bottom_left",   // or wherever fits the layout   <-- SyntaxError here
    config: { ... }
}
```

`{` opens a block, `module:` is a label, and the comma after the string is a
syntax error. Prettier fails the whole commit:

```
[error] docs/HERMES-CHAT-DESIGN.md: SyntaxError: Unexpected token (3:13)
```

The fence may be **pre-existing** — it only trips the hook when YOUR edit puts
that file in lint-staged's path (the file was likely committed with
`--no-verify` originally).

**Fix:** add `<!-- prettier-ignore -->` on the line immediately before the fence:

```markdown
Add to `config/config.js`:
<!-- prettier-ignore -->
```js
{ ... }
```
```

Verify standalone before committing: `npx prettier --check docs/<file>.md`.
Scan for other ` ```js ` fences that could trip the same way.

## 4. `eslint --fix` SIGKILL in the hook ≠ a lint error

```
[FAILED] eslint --fix [SIGKILL]
```

SIGKILL is a resource/timeout kill of the hook subprocess, NOT a lint failure.
The standalone command is the source of truth:

```bash
npm run lint:js   # 0 errors, N JSDoc warnings = clean
```

If standalone lint is clean, the SIGKILL is transient — fix the other hook
failure (usually the prettier one above) and retry; eslint typically passes on
the second attempt. Do NOT reach for `--no-verify` to bypass — diagnose first.

## Commit that exercised all four

`c3183047` — "security: token gate + configurable bind host for mirror APIs;
docs sync". 10 files, 265 insertions / 288 deletions (inflated by prettier
reformat). Not pushed (held at the standing no-push-until-asked convention).
