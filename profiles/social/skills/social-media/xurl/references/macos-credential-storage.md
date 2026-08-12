# macOS Credential Storage for xurl Setup

This reference documents how to handle X API Client ID and Client Secret securely
during xurl setup on this machine. These credentials are only needed for the
one-time `xurl auth apps add` command — after that, xurl manages its own OAuth
tokens in `~/.xurl` (YAML, auto-refreshing).

## Two Patterns Used on This Machine

### Pattern A: Base64-Encoded File (Current)

This is the user's active approach. Secrets are base64-encoded and stored in
`~/.config/nim/`, loaded at shell startup via `~/.config/nim/env.sh`:

```bash
# ~/.config/nim/env.sh — loader script
export OPENAI_API_KEY=$(cat ~/.config/nim/.or_key | base64 -d)
```

**For xurl:** Store the Client ID and Client Secret the same way, then use them
in `xurl auth apps add`:

```bash
# Store (one-time, outside agent session):
echo -n "your-client-id" | base64 > ~/.config/nim/.x_client_id
echo -n "your-client-secret" | base64 > ~/.config/nim/.x_client_secret
chmod 600 ~/.config/nim/.x_client_id ~/.config/nim/.x_client_secret

# Use (outside agent session — the command exposes the secret inline):
xurl auth apps add my-app \
  --client-id "$(cat ~/.config/nim/.x_client_id | base64 -d)" \
  --client-secret "$(cat ~/.config/nim/.x_client_secret | base64 -d)"
```

The base64 encoding is **obfuscation, not encryption** — it prevents casual
shoulder-surfing and grep discovery but doesn't protect against a determined
attacker with filesystem access. Acceptable for dev credentials with rotation.

### Pattern B: macOS Keychain (Aspirational — Not Yet Set Up)

The security-hardening session created a loader script template at
`~/.hermes/load-keychain-secrets.sh` (service name: `hermes-secrets`) but it was
never populated. To use Keychain instead:

```bash
# Store (one-time, outside agent session):
security add-generic-password -a xurl-client-id \
  -s hermes-secrets -w "your-client-id"
security add-generic-password -a xurl-client-secret \
  -s hermes-secrets -w "your-client-secret"

# Use (outside agent session):
xurl auth apps add my-app \
  --client-id "$(security find-generic-password -s hermes-secrets -a xurl-client-id -w)" \
  --client-secret "$(security find-generic-password -s hermes-secrets -a xurl-client-secret -w)"
```

**Important:** The `security` CLI prompts for Keychain access on first use
(Approved/Always Allow/Deny). The user must approve.

## Why This Matters for xurl

xurl itself is well-designed for security:
- OAuth 2.0 PKCE flow — tokens auto-refresh, stored in `~/.xurl`
- `xurl auth status` shows app names, not secrets
- Never use `--verbose` in agent sessions (can leak auth headers)

The risk window is **only during setup**: when the user copies Client ID/Secret
from the X Developer Portal and needs to temporarily hold them before
`xurl auth apps add`. The patterns above close that window.

## Verification

After registering the app:

```bash
xurl auth apps list          # should show your app name
xurl auth status             # default app should be your named app, not empty "default"
xurl whoami                  # should return your X handle
```
