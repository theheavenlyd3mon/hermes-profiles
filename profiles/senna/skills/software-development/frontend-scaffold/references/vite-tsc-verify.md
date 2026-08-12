# Vite scaffold: verifying TypeScript correctly

## The trap
Vite `react-ts` scaffolds emit a solution-style root `tsconfig.json`:
```json
{ "files": [], "references": [ { "path": "./tsconfig.app.json" }, { "path": "./tsconfig.node.json" } ] }
```
`"files": []` means the root owns zero source files. `npx tsc --noEmit` (bare, at repo root) therefore compiles nothing and prints `TypeScript: No errors found` unconditionally. A green result is meaningless.

## The fix — always target the project configs
```bash
# App source (src/): this is what catches your component/lib/typings errors
npx tsc --noEmit -p tsconfig.app.json

# Node-side config files (vite.config.ts, vitest.config.ts, etc.)
npx tsc --noEmit -p tsconfig.node.json

# Or just run the real build (uses the reference graph via `tsc -b`)
npm run build
```

## What lives where (typical Vite react-ts)
- `tsconfig.app.json` — `include: ["src"]`, `jsx`, DOM lib, `vite/client` types. Checks components, hooks, `src/lib/*`, `src/vite-env.d.ts`.
- `tsconfig.node.json` — checks `vite.config.ts` and other tooling config.
- `vite-env.d.ts` (in `src/`) — `/// <reference types="vite/client" />` + `ImportMetaEnv` interface. Only validated under `tsconfig.app.json`.

## Real-world miss
On the Spark-Avatar dApp: `src/lib/chain.ts` (viem import, `import.meta.env` reads) and `src/vite-env.d.ts` compiled clean under `-p tsconfig.app.json` but would have been entirely invisible to a bare `tsc --noEmit`. Always use `-p`.
