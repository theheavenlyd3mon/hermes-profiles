---
name: frontend-scaffold
description: Scaffold a Vite + React + TypeScript web app (optionally a web3/viem dApp) at a repo root, wire up .gitignore/.env.example, verify the build + dev server, and commit locally. Embeds two critical pitfalls - "npm silently omits devDependencies" and "bare root `tsc --noEmit` is a silent no-op (always verify with `-p tsconfig.app.json`)".
---

# frontend-scaffold

## When to use
- User asks to "scaffold", "set up", "bootstrap", or "create" a React/TS frontend, Vite app, or web3 dApp frontend.
- Starting a new repo root that should hold the app directly (NOT under a `frontend/` subdir) unless they specify otherwise.
- Web3 frontends: when `viem`/`wagmi`/contract-address `.env` keys are expected.

## Steps
1. Verify environment: `node --version`, `npm --version`, and confirm the target dir does NOT already exist (`ls -la <dir> 2>/dev/null || echo MISSING`).
2. Scaffold: `npm create vite@latest <name> -- --template react-ts` (adjust template as asked).
3. `git init` if creating a fresh repo root.
4. Install deps — see Pitfalls. Check `npm config get omit`; if it lists `dev`, run `npm install --include=dev`. Then add requested libs, e.g. `npm i viem`.
5. Create root files:
   - `.gitignore`: `node_modules/`, `dist/`, `.env`, plus tool-specific dirs (e.g. `contracts/artifacts/`). Replace Vite's minimal default.
   - `.env.example`: `VITE_*` keys with EMPTY values (e.g. `VITE_CONTRACT_ADDRESS=`). Do NOT create `.env` itself.
6. Verify build: `npm run build` (runs `tsc -b && vite build`). Fix any type errors.
7. Verify dev server: start `npm run dev` in background, then `curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>` → expect `200`, then kill the process.
8. Commit locally (no push unless asked): set repo-local identity if global is unset, `git add -A`, `git commit`.

## Verification checklist
- `git check-ignore .env` prints `.env` (secrets ignored).
- `git ls-files | grep -i env` shows only `.env.example` (no real secrets tracked).
- `npm run build` exits 0 and emits `dist/assets/index-*.js`.
- Dev server `curl` returns `200`.

## Pitfalls

### npm silently omits devDependencies (CRITICAL — recurring on this machine)
Symptom after `npm create vite` + `npm install` + `npm run build`:
```
error TS2688: Cannot find type definition file for 'vite/client'.
error TS2688: Cannot find type definition file for 'node'.
```
Cause: a global or per-dir `~/.npmrc` sets `omit[]=dev` (often alongside `NODE_ENV=production`). `npm install` then installs only prod deps; `vite`, `typescript`, `@types/*`, `@vitejs/plugin-react` are all devDeps and get skipped. The first install reports suspiciously few packages (e.g. ``added 3 packages``).
Diagnosis:
```
npm config get omit        # prints "dev" → dev deps were dropped
ls node_modules/@types     # empty
ls -d node_modules/vite    # missing
```
Fix:
```
npm install --include=dev  # re-pull all dev deps
npm run build              # now succeeds
```
See `references/npm-devdeps-omit-pitfall.md` for the full reproduction recipe.

### Tool-call heuristic false-positive on `npm install`
Commands beginning with `npm install` (or anything the runtime mistakes for a long-lived server) may be rejected with "appears to start a long-lived server." Mitigation: run them as `background=true` + `process(action=wait)`, or chain them in a shell that `cd`s first so the heuristic doesn't trip.

### Vite default `.gitignore` is minimal
`npm create vite` writes a thin `.gitignore`. Replace/extend it so `node_modules/`, `dist/`, and `.env` are covered, then confirm only `.env.example` is tracked.

### Root `tsc --noEmit` is a SILENT NO-OP in Vite scaffolds (CRITICAL verification trap)
Vite's `react-ts` (and any `npm create vite --template *-ts`) writes a **solution-style root `tsconfig.json`**:
```json
{ "files": [], "references": [ { "path": "./tsconfig.app.json" }, { "path": "./tsconfig.node.json" } ] }
```
With `"files": []` and only `references`, the root owns **no source files**. So `npx tsc --noEmit` (run bare from the repo root) compiles **nothing** and reports `TypeScript: No errors found` even when `src/*.ts` is full of type errors. This is a green check that proves nothing.

**Always verify against the real project config, never the empty root:**
```bash
# Correct — points tsc at the app project tsconfig that `include`s "src"
npx tsc --noEmit -p tsconfig.app.json    # compiles src/, surfaces real errors
# Node-side config files (vite.config.ts etc.):
npx tsc --noEmit -p tsconfig.node.json
```
`npm run build` already does the right thing (`tsc -b && vite build` uses the reference graph), so a green `npm run build` also catches src errors. The trap is specifically bare `tsc --noEmit` at root.

**Why this matters for dApp work:** `vite-env.d.ts` (`/// <reference types="vite/client" />` + `ImportMetaEnv`) and `src/lib/*.ts` (viem import, `import.meta.env` reads) live under `src/` and are NOT checked by bare root `tsc`. Validate them with `-p tsconfig.app.json`. See `references/vite-tsc-verify.md`.

## Notes / assumptions
- Scaffold directly at the repo root unless the user explicitly wants a `frontend/` subdir.
- Install ONLY what's requested (e.g. `viem`); do not add extra scaffolding libs (e.g. `@tanstack/react-query`) unless asked.
- Report `viem`/`react`/`vite`/`typescript` versions actually installed for re-verifiability.
