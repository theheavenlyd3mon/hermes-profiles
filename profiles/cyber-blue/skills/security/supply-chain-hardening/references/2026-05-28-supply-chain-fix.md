# Supply Chain Fix — May 28, 2026

Cron script reconstruction session. 3 missing scripts recreated, then
supply-chain-scan.sh ran and found vulnerabilities in both projects.

## Scan Results

### HermesMirror — 5 moderate (FIXED)
| Package | Severity | Advisory | Fix |
|---------|----------|----------|-----|
| brace-expansion 5.0.2-5.0.5 | moderate | GHSA-jxxr-4gwj-5jf2 — large numeric range defeats max DoS protection | `npm audit fix` |
| qs 6.11.1-6.15.1 | moderate | GHSA-q8mj-m7cp-5q26 — qs.stringify crashes on null/undefined in comma-format arrays | `npm audit fix` |
| ws 8.0.0-8.20.0 (engine.io) | moderate | GHSA-58qx-3vcg-4xpx — uninitialized memory disclosure | `npm audit fix` |
| ws 8.0.0-8.20.0 (socket.io-adapter) | moderate | same as above, transitive via socket.io | `npm audit fix` |

**Applied:** `npm audit fix` — added 1 pkg, removed 2, changed 4.
Result: **0 vulnerabilities**.

### hermes-office — 3 moderate → 0 (FIXED)
| Package | Severity | Advisory | Fix |
|---------|----------|----------|-----|
| postcss <8.5.10 (via next) | moderate | GHSA-qx2v-qp2m-jg93 — XSS via unescaped </style> in CSS stringify | npm override |
| ws 8.0.0-8.20.0 | moderate | GHSA-58qx-3vcg-4xpx — uninitialized memory disclosure | `npm audit fix` |

**Problem:** `npm audit fix --force` would downgrade Next.js from 16.2.6 to 9.3.3
(semver-major downgrade, would destroy the project). The postcss vulnerability
is in Next.js's transitive dependency tree.

**Solution:** Added `overrides` to `package.json`:
```json
{
  "overrides": {
    "postcss": "^8.5.10"
  }
}
```

Then `npm install` — forces postcss to patched version while keeping Next.js
at 16.2.6. Result: **0 vulnerabilities**, no breaking changes.

## Postinstall Script Detection

The supply-chain-scan.sh script now also scans for packages with `postinstall`
scripts in node_modules. This is informational, not a vulnerability finding.

Detected in this scan:
- HermesMirror: msw, unrs-resolver, electron (3 packages)
- hermes-office: unrs-resolver, esbuild (2 packages)

All are expected/legitimate — msw is dev-only (test mocking), electron is the
runtime, esbuild is the bundler, unrs-resolver is a native binary resolver.

## Scan Directory Coverage

The supply-chain-scan.sh script scans these directories:
1. /Users/noctis/projects/HermesMirror
2. /Users/noctis/hermes-solar-system
3. /Users/noctis/hermes-workspace
4. /Users/noctis/.hermes/hermes-office

Only HermesMirror and hermes-office had package-lock.json files.
hermes-solar-system and hermes-workspace had no lockfile (skipped).
