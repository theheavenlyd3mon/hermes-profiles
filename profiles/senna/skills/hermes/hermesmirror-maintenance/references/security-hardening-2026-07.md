# HermesMirror security hardening — shipped 2026-07-20

Records what was implemented so future maintenance reviews verify the gate is
still wired instead of re-proposing it.

## What shipped

1. **Token gate** — every request to both plugins (`kanban-api` :8643,
   `session-api` :8644) and to the mirror's node_helpers must send header
   `X-Mirror-Token` matching the server's `HERMES_MIRROR_TOKEN` env var.
   - Plugins validate with `hmac.compare_digest` (constant-time).
   - `hermes-chat/node_helper.js` and `hermes-bridge/node_helper.js` attach the
     header on their outbound `fetch` when `this.config.token` is set.
   - **Empty/unset token = open dev mode** (gate is a no-op). This is the
     residual risk: the moment a plugin is bound off-loopback with an empty
     token, everything is exposed again.
2. **Configurable bind host** — `HERMES_MIRROR_HOST` env var (default
   `127.0.0.1`). `hermes-bridge/hermes-bridge.js` reads it for its default
   gateway URL; both node_helpers carry a `token: ""` default in their config.
3. **No CORS headers** — the plugins never emitted `Access-Control-Allow-*`.
   The design doc's old `Access-Control-Allow-Origin: *` line was stale prose,
   not real behavior; it was corrected to "no CORS, same-origin only."

## Files touched
- `modules/hermes-chat/node_helper.js` — token header on fetch.
- `modules/hermes-bridge/hermes-bridge.js` + `node_helper.js` — `HERMES_MIRROR_HOST`,
  `token: ""` default, token header on fetch.
- `~/.hermes/plugins/kanban-api/`, `~/.hermes/plugins/session-api/` — token gate
  via `hmac.compare_digest` (already present; verified this session).
- `docs/HERMES-CHAT-DESIGN.md` — Security section updated (no-CORS, token gate,
  configurable bind host).

## Review checklist (each future pass)
- [ ] Token gate still present in both plugins (`grep compare_digest`).
- [ ] node_helpers still attach `X-Mirror-Token` when `config.token` set.
- [ ] Bind host still defaults to loopback (`HERMES_MIRROR_HOST` unset → 127.0.0.1).
- [ ] No `Access-Control-Allow-*` reintroduced anywhere.
- [ ] If deploy moved off-loopback: confirm `HERMES_MIRROR_TOKEN` is a real secret.

## Standing constraint
Do NOT flip the bind host or set a token during a routine review unless the user
asks — both change the deployment model.
