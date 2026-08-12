---
name: npm-supply-chain-sweep
description: Check npm installs after a supply-chain poisoning advisory.
domain: cybersecurity
subdomain: supply-chain-security
version: '1.0'
---

# npm Supply-Chain Sweep

Advisory-driven verification: a maintainer account got compromised, poisoned
versions of package(s) were published, and the user wants to know "did I get
hit?". Answer with evidence, not vibes. Read-only, no installs required except
the packages you are checking against.

## When to Use
- "New npm supply-chain advisory just dropped — sweep my machine"
- "Did I install the compromised <pkg>@<version>?"
- Any poisoned-version list from an advisory (Mini Shai-Hulud, esbuild,
  ua-parser-js, event-stream, colors/faker, etc.). The workflow is the same.

## Core Principle
A package DIRECTORY with a matching name is NOT a verdict. `keyv`,
`file-entry-cache`, `cacheable-request` and friends are ubiquitous transitive
deps of eslint/stylelint — their dirs appear in almost every node_modules.
**The exact installed VERSION is the verdict.** Always compare installed
version against the advisory's poisoned version list.

## Workflow

1. **Parse the advisory** — build the exact `pkg@poisoned-version` list.
   Versions matter: `file-entry-cache@11.1.6` is poisoned while `11.1.2` is
   fine. Extract payload/dropper filenames (e.g. `setup.mjs`, `Math_*.js`)
   and any C2/exfil domains for later.

2. **Inventory tooling** — `node -v`, `npm -v`, `bun -v`, `npm ls -g --depth=0`,
   `npm config get registry` (a non-registry.npmjs.org registry is itself a
   finding).

3. **Find lockfiles** (exclude `*/Library/*`, `*/.hermes/*`, `*/node_modules/*`):
   `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `bun.lock`, `bun.lockb`,
   `npm-shrinkwrap.json`. For each poisoned package, grep with **package-name
   context**, never a bare version string.

4. **Installed copies** — `find` `*/node_modules/<pkg>` (and nested copies
   under `node_modules/<other>/node_modules/<pkg>` — nested deps are a common
   hiding spot). Read each `package.json`: `version` + `scripts`. A
   `preinstall`/`prepare` script in a version that shouldn't have one is a red
   flag.

5. **Dropper artifacts** — search node_modules for the advisory's filenames
   (`setup.mjs`, `Math_*.js`, `preinstall*`). Absence = strong clean signal.

6. **Caches** — `npm cache ls <pkg>` (poisoned tarball URL = exposure, even if
   node_modules was reinstalled), plus the bun cache
   `~/.bun/install/cache/<pkg>/`. `npm cache ls` per-package can be truncated
   with `head` — run full when the poisoned version is the question.

7. **DECISIVE: publish-time proof** — query
   `curl -s https://registry.npmjs.org/<pkg>` → `d['time'][version]` for the
   poisoned version. Compare against install timestamps
   (`ls -laT <pkg>/package.json`). If every install predates the poisoned
   publish, infection is *physically impossible* — state that.

8. **Live-process check** — `ps aux | grep -E '/(bun|node|deno)'`: a payload
   executes via bun/node; no such process = nothing running.

9. **Token surface** — list `.npmrc` files (existence only; NEVER print token
   contents). No `.npmrc` in projects = nothing for the stealer to harvest.

10. **Network** — `lsof -i -P -n | grep ESTABLISHED` and grep for the
    advisory's exfil domains. Check `/etc/hosts`: users often add their own
    block entries for C2/exfil domains — that is intentional defense, not
    hijack; note it, don't flag it.

## Report
Deliver findings IN CHAT, bottom line first ("no poisoned version installed,
and here is the timing proof"), then severity-ordered. HIGH = poisoned version
found OR patch debt; MEDIUM/LOW = posture items; INFO = intentional
defensive edits. State evidence chains (installed version, lockfile resolved
URL + integrity, publish timestamp) for every verdict.

## Support files
- `scripts/npm_poison_sweep.sh` — re-runnable sweep: takes `pkg@version`
  pairs, checks lockfiles, all installed copies (incl. nested), npm cache,
  dropper artifacts, and fetches the poisoned publish timestamp.
- `references/mini-shai-hulud-iocs.md` — worked example: the Mini Shai-Hulud
  advisory (poisoned versions + publish dates, payload names, exfil domains,
  Defender name) and the session's clean-verdict evidence chain.

## Pitfalls
- Grepping lockfiles for `"version": "6.0.0"` matches ANY package at 6.0.0
  (e.g. `locate-path@6.0.0`) — massive false-positive noise. Anchor on the
  package entry (`"node_modules/keyv"` block) or the `resolved` tarball URL.
- Nested copies: `node_modules/stylelint/node_modules/file-entry-cache` can be
  a different (benign) major version than the top-level one — check every copy.
- `npm cache ls` may only show a few lines; the poisoned tarball could be
  further down the list.
- Scoped packages (`@servicetitan/*`, `@cacheable/*`) need the `@scope/` in
  the find path and grep patterns.
- Don't string-grep whole node_modules trees; target `find` by package dir.
- `freshclam`/ClamAV is a separate, slower pass — the npm sweep is
  deterministic and does not need an AV scan to reach a verdict.
