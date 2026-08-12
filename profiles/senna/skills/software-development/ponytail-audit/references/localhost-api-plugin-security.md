# Localhost-bound API plugin security — worked example

**Context:** a MagicMirror² fork. Two Python aiohttp plugins on the Mac feed a
MagicMirror² instance:
- `kanban-api` (port 8643): `GET /api/kanban/board` → task board from the kanban DB.
- `session-api` (port 8644): `GET /api/session/messages` → raw conversation
  transcripts from the LCM SQLite DB.

Both bind `127.0.0.1` (localhost only), **no auth**, `Access-Control-Allow-Origin: *`.

## Findings (ranked, as they landed)
| Sev | Finding | Minimal fix |
|-----|---------|-------------|
| CRITICAL* | host hardcoded `127.0.0.1`, no knob; `0.0.0.0` for Pi→LAN exposes all with zero auth | configurable host + refuse non-loopback w/o token |
| HIGH | no auth; `session_id` is a free param → enumerate any session | `X-Api-Token`, fail-closed |
| HIGH | `session-api` returns raw transcripts (keys/PII leak) | redaction regex |
| MED-HIGH | CORS `*` → localhost drive-by exfil today | delete header (Node ignores CORS) |
| LOW | hardcoded `profiles/senna/` path | derive from `HERMES_PROFILE` env |

\* CRITICAL only in the planned Mac↔Pi LAN deploy; safe on localhost today.
No SQLi — queries are parameterized and `limit` is clamped 1–200.

## Minimal hardening (~10 lines/plugin, lazy)
- `API_TOKEN = os.environ.get("HERMES_MIRROR_TOKEN", "")`. In each handler:
  ```python
  if not API_TOKEN or not hmac.compare_digest(
          request.headers.get("X-Api-Token", ""), API_TOKEN):
      return web.Response(status=401, body=b"unauthorized")
  ```
- Client (`node_helper.js` `fetch`) sends the same `X-Api-Token` header.
- Remove `Access-Control-Allow-Origin: *` (dead weight for a Node client).
- Redact transcript content BEFORE the `[:4000]` slice:
  ```python
  content = re.sub(r'(sk-|AKIA|Bearer |ghp_)[^\s"\']+', r'\1[REDACTED]', content)
  ```
- `_HOST = os.environ.get("HERMES_MIRROR_HOST", "127.0.0.1")`; if host is not
  loopback and `API_TOKEN` is empty → refuse to start.
- `HERMES_PROFILE = os.environ.get("HERMES_PROFILE", "")` instead of `"senna"`.

## Lesson
"localhost only" is NOT a security boundary once the deployment adds a second
machine. Audit these plugins as if they're already on the LAN, and couple
exposure to authentication so they can't be opened by accident. The CORS
wildcard is the one item exploitable *before* any LAN move — kill it first.
