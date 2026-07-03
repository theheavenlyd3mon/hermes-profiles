# MagicMirror² v2.36.0 — Dependency Risk Analysis (Worked Example)

This document records the dependency-by-dependency risk assessment produced during a real session when the user (security-conscious after a previous npm supply chain incident) asked to vet MagicMirror² before running `npm install`.

## Methodology

Each direct dependency was categorized by function, attack surface, and maintenance health. DevDependencies and optional dependencies were noted but deprioritized (dev deps don't install with `--omit=dev`; optional deps can be skipped).

## Direct Dependencies (13 packages)

### 🟢 Low Risk — Static Assets

| Package | Version | Purpose | Rationale |
|---------|---------|---------|-----------|
| `@fontsource/roboto` | ^5.2.10 | Font files | Served statically via CSS, zero code execution |
| `@fontsource/roboto-condensed` | ^5.2.8 | Font files | Same — static CSS/font assets |
| `@fortawesome/fontawesome-free` | ^7.2.0 | Icon font | Same — static |
| `weathericons` | ^2.1.0 | Weather icon set | Same — static |

### 🟢 Low Risk — Pure Computation / Utilities

| Package | Version | Purpose | Rationale |
|---------|---------|---------|-----------|
| `suncalc` | ^1.9.0 | Sun position math | Pure trigonometry on lat/lng input, no I/O |
| `moment` | ^2.30.1 | Date formatting | Maintenance-only mode (no new features), stable, widely audited |
| `moment-timezone` | ^0.6.2 | Timezone data | Same — maintenance-only |
| `iconv-lite` | ^0.7.2 | Character encoding | Stable, widely used, zero network |
| `ipaddr.js` | ^2.3.0 | IP address parsing | Minimal surface — parses IP strings |
| `ajv` | ^8.20.0 | JSON schema validation | Well-maintained, active development |
| `croner` | ^10.0.1 | Cron scheduling | Small, focused, no external I/O |

### 🟡 Medium Risk — Parsers (External Data)

| Package | Version | Purpose | Rationale |
|---------|---------|---------|-----------|
| `feedme` | ^2.0.2 | RSS/Atom feed parser | **Closest analogue to the `marked` ReDoS issue.** Parses untrusted RSS/Atom data. However, RSS is a narrow format (XML-based, no markdown rendering) — smaller surface. Risk increases if the user adds arbitrary feeds. |
| `html-to-text` | ^9.0.5 | HTML-to-text conversion | Parses HTML — broader surface. Risk depends on whether HTML content comes from trusted sources. |
| `node-ical` | ^0.26.0 | iCalendar parser | Processes `.ics` calendar files — similar parser risk to feedme. Only used if the calendar module is enabled. |

### 🟡 Medium Risk — Network-Facing

| Package | Version | Purpose | Rationale |
|---------|---------|---------|-----------|
| `express` | ^5.2.1 | HTTP server | Well-audited, actively maintained by Express TC. Express 5 is the latest major. | 
| `socket.io` | ^4.8.3 | WebSocket library | Network-facing but well-maintained, regular releases |
| `helmet` | ^8.1.0 | Security HTTP headers | Mitigates risk (adds security headers) — risk-reducing, not risk-adding |
| `undici` | ^8.1.0 | HTTP client | Maintained by the Node.js core team. | 

### 🟡 Medium Risk — System Access

| Package | Version | Purpose | Rationale |
|---------|---------|---------|-----------|
| `systeminformation` | ^5.31.5 | System diagnostics (CPU, mem, disk) | Reads local hardware info, no network. Well-maintained. |
| `pm2` | ^6.0.14 | Process manager daemon | Complex — runs as a background daemon with its own process management. Medium risk due to complexity, not network exposure. |

### 🟡 Medium Risk — Templating

| Package | Version | Purpose | Rationale |
|---------|---------|---------|-----------|
| `nunjucks` | ^3.2.4 | Template engine | Templates are project-authored (in `config.js` and modules), not user-submitted. Template injection only possible if user content enters templates, which isn't the default usage pattern. |
| `globals` | ^17.5.0 | ESLint globals definitions | Declarative definitions only — no runtime code path |
| `eslint` | ^10.2.1 | Linter | Listed in dependencies but is a dev-time tool. Won't execute in production. |

### 🟠 Runtime — Electron

| Package | Version | Purpose | Rationale |
|---------|---------|---------|-----------|
| `electron` | ^41.3.0 | Desktop application runtime | **Optional dependency** — listed in `optionalDependencies`. Can be skipped with `--ignore-optional` if you only run the server module. Electron bundles Chromium+Node.js with a large attack surface, but has a dedicated security team and actively releases patches (CVE disclosures are public and timely). v41.x is very recent. |

### Summary

| Risk Level | Count | Notes |
|:-----------|:-----:|:------|
| 🟢 Low | 8 | Static + utilities |
| 🟡 Medium | 7 | Parsers, network, system access |
| 🟠 Runtime | 1 | Electron (optional — can skip) |
| 🔴 Critical | 0 | None |

## Key Mitigations Suggested

1. **Lock exact versions** — change `^` to pinned versions in `package.json` before install
2. **Run `npm audit`** post-install to verify zero known vulnerabilities in resolved tree
3. **Skip unused modules** — if you don't use RSS/calendar, those parser packages don't execute
4. **Optional Electron** — can install with `--ignore-optional` if you plan to run headless/server-only mode initially

## What Made This User Security-Conscious

The user had previously investigated the `marked@^17.0.1` vulnerability (ReDoS) in the Hermes workspace. `marked` is a markdown renderer — a parser with a wider attack surface than RSS or iCalendar parsers. The concern generalized to any npm project that depends on parser libraries.
