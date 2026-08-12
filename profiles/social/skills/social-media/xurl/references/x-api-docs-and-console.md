# X API Documentation & Developer Console Reference

This reference documents the X API documentation structure and the Developer Console flow that was mapped during the 2026-05-10 setup session. Use this when a user asks about setting up, troubleshooting, or understanding X API credentials — particularly the steps *before* xurl is configured.

## Key URLs

| Resource | URL | Notes |
|----------|-----|-------|
| Developer Console (signup, apps, keys) | `https://console.x.com` | **This is the correct URL.** The old `developer.x.com/en/portal/dashboard` redirects to a login page. |
| X API Docs (overview) | `https://docs.x.com/x-api/overview` | Root docs hub. Append `.md` for raw markdown (agent-friendly). |
| Docs Index (for agents) | `https://docs.x.com/llms.txt` | Complete page index. Use for page discovery. |
| Getting Access (app creation guide) | `https://docs.x.com/x-api/getting-started/getting-access.md` | Official step-by-step with credential-type table. |
| Make Your First Request | `https://docs.x.com/make-your-first-request.md` | cURL + SDK examples. |
| xurl GitHub README | `https://github.com/xdevplatform/xurl` | Upstream CLI docs, auth setup, troubleshooting. |

## Docs Structure (for Agent Research)

The X API docs at `docs.x.com` are built for both humans and agents:
- **All pages support `.md` suffix** for clean markdown retrieval. E.g. `https://docs.x.com/x-api/getting-started/getting-access.md` returns raw markdown.
- **`llms.txt`** at the root provides a full index of all pages.
- **`llms-full.txt`** contains the entire doc set as a single markdown file (useful for maximum context).
- The sidebar has collapsible sections (expand via click on toggle buttons).

## Developer Console: App Creation Flow

When a user needs to create an X API app from scratch:

1. **Go to `console.x.com`** → sign in with X account
2. **Accept Developer Agreement** + complete profile (one-time)
3. **Click "New App"** → enter name, description, use case
4. **Configure User Authentication Settings:**
   - App type: **"Web app, automated app or bot"** (NOT "Native App")
   - Redirect URI: `http://localhost:8080/callback`
   - Scopes: `tweet.read`, `users.read`, `offline.access` minimum
5. **Copy credentials** from "Keys and Tokens" tab:
   - **Client ID** (often ends in `MTpjaQ`)
   - **Client Secret** (shown once — save immediately)
6. **Enroll in Pay-per-use** (required for API v2 access):
   - Apps → Manage apps → Open app → Move to package → Pay-per-use → Production

## Credential Types (from Getting Access page)

| Credential | Purpose | Used by xurl? |
|------------|---------|---------------|
| **Client ID & Secret** | OAuth 2.0 user-context auth | ✅ Primary method |
| **Bearer Token** | App-only read-only auth | Optional (via `xurl auth app`) |
| **API Key & Secret** | OAuth 1.0a app identification | Optional (via `xurl auth oauth1`) |
| **Access Token & Secret** | OAuth 1.0a user-context | Optional (via `xurl auth oauth1`) |

## Common Confusion Points Found in This Session

1. **"Client ID vs API Key":** The Getting Access page lists both. For xurl's OAuth 2.0 flow, use **Client ID** and **Client Secret**. The "API Key & Secret" (OAuth 1.0a) is different.
2. **console.x.com vs developer.x.com:** The old URL redirects to login. Always point users to `console.x.com`.
3. **Two "Client Secret" labels:** The X UI has a known bug where the first "Client Secret" value shown is actually the Client ID. Check the "Keys and tokens" page directly.
4. **Pay-per-use enrollment:** Even after successful OAuth, reads will fail with `client-forbidden` if the app isn't moved to Pay-per-use + Production. This is a platform enrollment issue, not a code problem.

## Verification After Setup

```bash
xurl auth apps list          # should show the registered app
xurl auth status             # default app should be a named app (not empty "default")
xurl whoami                  # should return your X handle
xurl search "test" -n 3     # confirm search works
```
