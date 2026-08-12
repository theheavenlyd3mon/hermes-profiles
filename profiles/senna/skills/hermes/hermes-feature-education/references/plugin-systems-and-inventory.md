# Plugin Systems & Inventory Workflow

How to explain Hermes plugins to a user and inventory what's actually installed.
Derived from the Aug 2026 session where the user believed their installed agent
plugins were "desktop plugins" — the two-system distinction was the core confusion.

## The two systems (teach this table first)

| | Agent plugins | Desktop plugins |
|---|---|---|
| Adds | tools, hooks, slash commands, backends | UI: panes, statusbar, ⌘K commands, pages, keybinds, themes |
| Format | Python + `plugin.yaml` | plain JS ESM (`plugin.js`) |
| Path | `~/.hermes/plugins/<name>/` | `~/.hermes/desktop-plugins/<name>/` |
| Loader | agent runtime (me) | the desktop app itself |
| Enable | `plugins.enabled` in config.yaml | Settings → Plugins (live toggle) or `defaultEnabled: false` opt-in |
| Reload | session restart | hot-reload on save; ⌘K → Reload desktop plugins |

Key tell: users almost always mean AGENT plugins when they say "I have plugins
installed." The desktop dir is frequently empty — that's normal, not broken.

## Inventory workflow (ground truth, in order)

1. **Version + status first**: `hermes --version`, `hermes status` (shows providers/keys).
2. **`hermes plugins list`** — discovered plugins with Status (enabled / not enabled)
   and Source (bundled / user / etc.). NOTE: output is a wrapped table that
   truncates badly in narrow terminals — `head`/`grep` it or read config directly.
3. **Check BOTH plugin dirs** so you can state which system has entries:
   ```bash
   ls ~/.hermes/plugins/            # agent plugins
   ls ~/.hermes/desktop-plugins/    # desktop UI plugins (often absent)
   ```
   Gotcha: `~/.hermes/profiles/<name>/plugins` may be a SYMLINK to
   `~/.hermes/plugins` (true for senna). Check with `ls -ld` — don't double-count.
4. **Read manifests** for what each plugin does: `head <dir>/plugin.yaml` →
   name/version/description/author. Author tells you provenance (e.g.
   `author: Senna` = user's own; third-party names = installed from elsewhere).
5. **Config allow-list is the enable ground truth**:
   ```bash
   grep -n -A 25 "^plugins:" ~/.hermes/config.yaml
   ```
   `enabled:` = loaded. `disabled:` deny-list wins on conflict. "Installed but
   not in enabled" is a real state (discovered, not loaded) — e.g. a plugin can
   sit installed-but-off for months. Say "installed, not enabled," not "broken."
6. **Special plugin kinds bypass the allow-list entirely** — they activate via
   their own config keys, so absence from `plugins.enabled` does NOT mean off:
   - Memory providers (`plugins/memory/`) → active one via `memory.provider` (e.g. mnemosyne)
   - Context engines → `context.engine`
   - Image/video gen backends → `<category>.provider` (e.g. `image_gen.provider: fal`)
   - Bundled platform adapters → `gateway.platforms.<name>.enabled`
   - Model providers → lazily scanned on first use
7. **Bundled ≠ user-installed**: browser backends (browser_use/browserbase/firecrawl),
   disk-cleanup, dashboard_auth appear enabled but ship with Hermes. The Source
   column distinguishes them; don't present them as the user's plugins.

## Session example (senna profile, Aug 2026)

- Agent plugins enabled: ponytail, katana, hermes-lcm, image-studio, icarus,
  eikon, hermes-achievements, kanban-api, web-search-plus (+ bundled browser/dashboard/image_gen)
- Installed but NOT enabled: session-api (HermesMirror bridge — off until needed)
- Memory provider: mnemosyne (via `memory.provider`, not the plugins list)
- Desktop plugins: none installed — offered to build a demo statusbar/pane plugin
- Provenance: kanban-api, session-api, katana, ponytail authored by Senna (user's own)

## Educational framing that worked

- Lead with the two-system table; it resolves "what are all these plugins" instantly.
- Inventory their REAL install (not generic docs) — users respond to their own list.
- End with 1-3 concrete offers: write a demo desktop plugin (~20 lines), enable a
  dormant plugin, or audit a specific plugin's source.
