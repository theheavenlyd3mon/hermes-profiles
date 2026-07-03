# Supply Chain Scan — May 14, 2026

Manual fallback scan performed on 2026-05-14 because the daily advisory
cron job (`supply-chain-advisory-check`, ID `5d3366224d17`) errored on
both its automated runs (07:18 and 07:37).

## Methodology

1. Ran `npm audit --audit-level=critical` on each project with a lockfile
2. Searched web for recent supply chain incidents (freshness=week)
3. No IDE persistence scan or lockfile diff — this was a pending catch-up

## NPM Audit Results

### /Users/noctis/projects/HermesMirror
```
1 high severity vulnerability (RESOLVED — see below)

systeminformation  4.17.0 - 5.31.5
Severity: high
Systeminformation vulnerable to Linux command injection in
networkInterfaces() via unsanitized NetworkManager connection profile name
https://github.com/advisories/GHSA-hvx9-hwr7-wjj9
fix available via `npm audit fix --force`
Will install systeminformation@5.31.6
```
Verdict: 1 high, known and old. Pre-existing in the MagicMirror lockfile.
**Resolution:** `npm audit fix --force` applied on 2026-05-14 at 07:38.
  Updated systeminformation to 5.31.6. HermesMirror now shows 0 vulns.

### /Users/noctis/.hermes/hermes-agent
```
found 0 vulnerabilities
```
Verdict: Clean.

### /Users/noctis/.hermes/hermes-office
```
3 vulnerabilities (1 moderate, 2 high)

next  9.3.4-canary.0 - 16.3.0-canary.5
Severity: high
Next.js has a Denial of Service with Server Components
https://github.com/advisories/GHSA-q4gf-8mx6-v5v3
[...13 additional Next.js advisories...]

postcss  <8.5.10
Severity: moderate
PostCSS XSS in CSS Stringify Output
https://github.com/advisories/GHSA-qx2v-qp2m-jg93

vite  7.0.0 - 7.3.1
Severity: high
Vite Path Traversal in Optimized Deps .map Handling
https://github.com/advisories/GHSA-4w7w-66w2-5vf9
+ Vite: server.fs.deny bypassed with queries
+ Vite Arbitrary File Read via Dev Server WebSocket
```
Verdict: 1 moderate + 2 high. All Next.js vulns in a pinned old version
(16.3.0-canary.5). Fix: `npm audit fix --force` (will install next@16.2.6).

## Web Scan — Recent Supply Chain Incidents

No new incidents since the Mini Shai-Hulud/TeamPCP campaign (May 11, 2026).
The dominant stories remain:
- TanStack postmortem (42 packages, 84 artifacts, CVE-2026-45321)
- Red Hat advisory roundup on the three waves of Shai-Hulud attacks
- pnpm v11 release notes on consumer-side security controls

The TanStack attack vector chain:
`pull_request_target` → cache poisoning → OIDC token extraction → package
publication with valid SLSA Build L3 attestations

## Files Checked

Projects with lockfiles under /Users/noctis/:
- projects/HermesMirror/package-lock.json
- .hermes/hermes-agent/package-lock.json
- .hermes/hermes-office/package-lock.json
- hermes-solar-system/package-lock.json (omitted — inactive project)
- .npm/_npx/.../package-lock.json (omitted — npx cache)
- .hermes/hermes-agent/ui-tui/package-lock.json (omitted — sub-project)
- .hermes/hermes-agent/web/package-lock.json (omitted — sub-project)
- .hermes/hermes-agent/website/package-lock.json (omitted — sub-project)

## What to Fix (if desired)

- HermesMirror: `cd /Users/noctis/projects/HermesMirror && npm audit fix --force`
- hermes-office: `cd /Users/noctis/.hermes/hermes-office && npm audit fix --force`
