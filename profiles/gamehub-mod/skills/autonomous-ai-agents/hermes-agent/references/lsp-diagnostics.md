## LSP — Semantic Diagnostics (Post-v0.13.0)

Hermes runs full language servers (pyright, gopls, rust-analyzer, typescript-language-server, ~20 more) as background subprocesses. Their semantic diagnostics feed into the post-write lint check used by `write_file` and `patch`, augmenting the in-process syntax checker that shipped in v0.13.0.

### Two-Layer Architecture

| Layer | What it catches | Speed | Shipped |
|-------|----------------|-------|---------|
| In-process syntax lint | Syntax errors only (Python/JSON/YAML/TOML) | Microsecond | v0.13.0 |
| LSP diagnostics | Type errors, undefined names, missing imports, project-wide semantic issues | ~seconds (server warm-up) | Post-v0.13.0 (HEAD) |

### When LSP Runs

- **Gated on git workspace detection** — only activates when the agent's cwd is inside a git worktree.
- Outside git repos: LSP stays dormant; in-process syntax checker handles everything.
- **Fails silently** — flaky/missing language server never breaks a write.

**Flow on every successful `write_file`/`patch`:**
1. In-process syntax check (microsecond, always runs first)
2. If git repo detected: capture baseline LSP diagnostics for the file
3. Perform the write
4. Re-query language server, filter out baseline, surface only new diagnostics

### CLI

```bash
hermes lsp status                    # service state + per-server install status
hermes lsp list --installed-only     # only servers with binaries found
hermes lsp install <server_id>       # eagerly install one server
hermes lsp install-all               # try every server with a known auto-install recipe
hermes lsp restart                   # tear down running clients (next edit re-spawns)
hermes lsp which <server_id>         # print resolved binary path
```

### Installation Mechanism

- Auto-installs missing servers on first use via `npm install --prefix <HERMES_HOME>/lsp/`.
- Binaries land in **`~/.hermes/lsp/bin/`** (isolated staging dir, never global `node_modules`).
- Lazy install — a missing server doesn't block writes, just silently falls back to syntax check.
- **Install strategy**: `auto` (default). Set `install_strategy: manual` in `config.yaml` to never auto-install — only use binaries already on PATH.

### Configuration

```yaml
lsp:
  enabled: true                    # Master toggle (default: true)
  wait_mode: document              # "document" or "full"
  wait_timeout: 5.0                # Seconds to wait for diagnostics
  install_strategy: auto           # "auto" or "manual"
  servers:
    pyright:
      disabled: false
      command: ["/abs/path/to/pyright-langserver", "--stdio"]
      initialization_options:
        python:
          analysis:
            typeCheckingMode: "strict"
    typescript:
      disabled: true               # skip TS entirely
```

### Supported Languages & Servers

| Language | Server | Auto-install | Package |
|----------|--------|--------------|---------|
| Python | `pyright-langserver` | npm (`pyright`) | Microsoft |
| TypeScript/JS/JSX/TSX | `typescript-language-server` | npm (+ peer dep `typescript`) | Community |
| Vue | `@vue/language-server` | npm | Vue core |
| Svelte | `svelte-language-server` | npm | Svelte core |
| Astro | `@astrojs/language-server` | npm | Astro core |
| Go | `gopls` | `go install` | Go team |
| Rust | `rust-analyzer` | manual (rustup) | rust-analyzer team |
| C/C++ | `clangd` | manual (LLVM) | LLVM |
| Bash/Zsh | `bash-language-server` | npm | Community |
| YAML | `yaml-language-server` | npm | Red Hat |
| PHP | `intelephense` | npm | Single maintainer |
| Dockerfile | `dockerfile-language-server-nodejs` | npm | Single maintainer |
| Lua, Terraform, Dart, Haskell, Julia, Clojure, Nix, Zig, Gleam, Elixir, Prisma, Kotlin, Java, OCaml | Various | Manual | Toolchain-managed |

### Security Considerations for npm Auto-Install

Hermes installs into `~/.hermes/lsp/bin/` — an isolated staging directory, not your project's `node_modules` or global npm. Since these are npm dependencies that may have transitive vulnerabilities:

- **Lazy install**: only installs what you actually use (edit a `.py` file → installs pyright; never touches intelephense unless you edit `.php`)
- **Silent fallback**: if npm fails or the server crashes, the in-process syntax checker still runs
- **Trusted packages**: `pyright` (Microsoft), `typescript` (Microsoft), `yaml-language-server` (Red Hat) have high trust and clean audit records

For a full npm security audit of all auto-installed packages (maintainer count, download stats, known vulns per transitive dep), see `references/lsp-npm-security-audit.md`.
