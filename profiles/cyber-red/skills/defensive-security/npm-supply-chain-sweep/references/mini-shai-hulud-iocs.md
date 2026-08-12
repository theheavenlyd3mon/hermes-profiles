# Mini Shai-Hulud npm supply-chain attack — worked example (2026-08-04)

Advisory: @MsftSecIntel (Microsoft Threat Intelligence), 2026-08-04. Active
npm supply-chain campaign; attacker compromised trusted maintainer accounts to
publish credential-stealing packages. Microsoft Defender alert:
`Trojan:npm/MalBun.A`.

## Poisoned versions (confirmed malicious)
- keyv@6.0.0
- file-entry-cache@11.1.6
- cache-manager@7.2.10
- cacheable-request@13.0.20
- qlik/api@2.14.2
- cacheable/memory, cacheable/utils, cacheable/net (i.e. @cacheable/*)
- 17+ servicetitan/* packages (eslint-config, anvil-themes, table, form,
  log-service, etc.)

## Publish timestamps (from registry.npmjs.org `time` field)
- keyv@6.0.0: 2026-08-04T09:35:00Z
- cacheable-request@13.0.20: 2026-08-04T10:11:24Z
- file-entry-cache@11.1.6: 2026-08-04T10:13:02Z

All poisoned versions published the same day as the advisory — timing proof
against older installs is decisive.

## Execution chain
1. Malicious `preinstall` hook in the poisoned tarball.
2. Launches obfuscated dropper `setup.mjs`.
3. Downloads a Bun binary from GitHub, executes it.
4. Runs credential-stealing payload `Math_Symbol.js` or `Math_Init.js`
   (Mini Shai-Hulud family).
5. Harvests npm, GitHub, cloud, and CI credentials; exfiltrates secrets.
6. Uses stolen publishing access to inject itself into package tarballs,
   increment versions, and republish — self-propagating.

## Exfil / C2 surface (Session messenger P2P network)
- filev2.getsession.org
- seed1.getsession.org / seed2.getsession.org / seed3.getsession.org
Blocking these in /etc/hosts is a common proactive user hardening (seen on
this user's machine; intentional, not hijack).

## Benign noise that matches the package NAMES (not versions)
keyv 4.5.4, file-entry-cache 8.0.0 / 11.1.2 (nested under stylelint),
cacheable-request 7.0.4, @cacheable/memory 2.0.8, @cacheable/utils 2.4.1 —
all standard eslint/stylelint transitive deps. Dir presence alone proves
nothing; versions + lockfile `resolved` URLs + publish timestamps do.

## Clean-verdict evidence chain used in session
- Installed versions all benign (above), lockfiles resolve to legit tarballs
  with integrity hashes.
- npm cache: only keyv 4.5.4/5.6.0, file-entry-cache 11.1.2/8.0.0,
  cacheable-request 7.0.4. bun cache: keyv@4.5.4, file-entry-cache@8.0.0.
- No setup.mjs / Math_*.js anywhere; no node/bun processes running; no
  .npmrc token surfaces in projects; no outbound getsession.org traffic.
- node_modules install dates (May 12, Jul 16) predate all poisoned publishes
  (Aug 4) — infection physically impossible.
