# LSP npm Package Security Audit

Audit performed: 2026-05-12
Hermes version: v0.13.0 post-release (HEAD)
Source: `agent/lsp/install.py` — `INSTALL_RECIPES` registry

## Packages with Auto-Install Recipes

Nine npm packages are eligible for auto-install by Hermes LSP (`install_strategy: auto`). All installs go to `~/.hermes/lsp/bin/` (isolated staging dir). Each is lazy-installed on first use of the corresponding file type.

## Audit Table

| Package | Version | Downloads/wk | Maintainers | Known Vulns | Trust | Notes |
|---------|---------|-------------|-------------|-------------|-------|-------|
| **pyright** | 1.1.409 | 508,873 | 6 (Microsoft) | **None** | High | Microsoft-maintained type checker. Binary size ~30MB. |
| **typescript-language-server** | 5.2.0 | 807,409 | 3 (community) | **None** | High | Wraps tsserver. Peer dep: `typescript` (199M/wk, MS, vuln-free). |
| **@vue/language-server** | 3.2.8 | 73,546 | 2 (Vue core) | **None** | High | Vue core team. Only needed for `.vue` files. |
| **dockerfile-language-server-nodejs** | 0.15.0 | 12,101 | 1 | **None** | Medium | Single maintainer, clean sheet. Small attack surface (Dockerfiles only). |
| **yaml-language-server** | 1.23.0 | 1,454,172 | 4 (Red Hat) | **⚠️ Moderate** | High | Red Hat maintained. Vuln: `yaml` dep (GHSA-48c2) — stack overflow via deeply nested YAML. Low practical risk (local YAML files only). |
| **@astrojs/language-server** | 2.16.8 | 1,252,569 | 2 (Astro) | **⚠️ Moderate** | High | Same transitive `yaml` DoS as yaml-language-server via volar-service-yaml. |
| **svelte-language-server** | 0.18.0 | 29,668 | 3 (Svelte) | **⚠️ Moderate** (4 vulns) | High | Vulns are in **svelte SSR** peer dep, not the LSP protocol. GHSA-crpf, -m56q, -f7gr, -phwv. No fix available. Low practical risk. |
| **bash-language-server** | 5.6.0 | 202,193 | 2 | **🔴 High** (3 ReDoS) | Medium | Vulns via `editorconfig` → `minimatch` (GHSA-3ppc, -7r86, -23c5). All ReDoS (DoS, no code exec). Fix requires downgrade to 5.4.3 (breaking). Needs `shellcheck` on PATH for actual diagnostics — without it the server spawns but emits nothing. |
| **intelephense** | 1.18.2 | 38,338 | 1 | **🔴 High** (8 vulns) | Low | Single maintainer (bmewburn). Vulns via `protobufjs` including code injection (GHSA-66ff, CVSS 8.1). Riskiest package. **Recommend skipping unless actively editing PHP.** |

## Vulnerability Summary

- **11 total** (7 moderate, 4 high, 0 critical)
- **4 packages clean**: pyright, typescript-language-server+typescript, @vue/language-server, dockerfile-language-server-nodejs
- **3 moderate**: yaml-language-server, @astrojs/language-server, svelte-language-server
- **2 high**: bash-language-server (ReDoS only), intelephense (protobufjs code injection)

## Risk Mitigation by Design

1. **Isolated staging directory**: `~/.hermes/lsp/bin/` — not in project `node_modules`, not global npm
2. **Lazy install**: only installed when you edit a matching file type in a git repo
3. **Silent failure**: broken server → falls back to in-process syntax checker, never blocks a write
4. **No network exposure**: LSP servers communicate over local stdio pipes only

## Safe Defaults Recommendation

Install these without concern:
- `pyright` (Python) — Microsoft, clean, 509k downloads/wk
- `typescript-language-server` (JS/TS) — community, clean, 807k downloads/wk
- `yaml-language-server` (YAML) — Red Hat, moderate vuln is stack-overflow DoS only
- `bash-language-server` (Shell) — ReDoS only, needs `shellcheck` on PATH for actual diagnostics
- `dockerfile-language-server-nodejs` (Docker) — single maintainer, clean

Skip unless needed:
- `intelephense` (PHP) — single maintainer + protobufjs injection vulns. Manual install if PHP work starts
- `@vue/language-server`, `svelte-language-server`, `@astrojs/language-server` — only if actively editing those frameworks

Manual (not auto-installed by Hermes):
- `gopls`, `rust-analyzer`, `clangd`, `lua-language-server`, `terraform-ls`, `kotlin-language-server`, `jdtls`, etc.
