# Claw3D Auto-Install via Hermes Desktop — Full Details

## Trigger

Hermes Desktop has a built-in "Hermes Office (Claw3d)" feature. When the user activates it from within Hermes Desktop, the app:

1. Clone the Claw3D repo to `~/.hermes/hermes-office/`
2. Install npm dependencies
3. Auto-generate `.env` with correct Hermes API values
4. Create `~/.openclaw/claw3d/` with `settings.json`

## File Layout After Auto-Install

```
~/.hermes/hermes-office/
├── .env                          # Auto-configured by Hermes Desktop
├── node_modules/                 # Dependencies already installed
├── server/
│   └── hermes-gateway-adapter.js # WebSocket adapter (translates Claw3D ↔ Hermes)
├── src/                          # Frontend source
├── scripts/
│   └── clawd3d-start.sh          # One-command start script
└── ...

~/.openclaw/claw3d/
└── settings.json                 # Connection settings (gateway URL, adapter type, etc.)

~/.hermes/clawd3d-history.json    # Conversation history (empty `{}` initially)
```

## sample .env (auto-generated)

```
# Auto-configured by Hermes Desktop
PORT=3000
HOST=127.0.0.1
NEXT_PUBLIC_GATEWAY_URL=ws://localhost:18789
CLAW3D_GATEWAY_URL=ws://localhost:18789
CLAW3D_GATEWAY_TOKEN=
HERMES_ADAPTER_PORT=18789
HERMES_MODEL=hermes
HERMES_AGENT_NAME=Hermes
```

`HERMES_API_URL` is not explicitly set — the adapter defaults to `http://localhost:8642`, which is correct for standard Hermes installations.

## sample settings.json (auto-generated)

```json
{
  "version": 1,
  "gateway": {
    "url": "ws://localhost:18789",
    "token": "",
    "adapterType": "hermes",
    "lastKnownGood": {
      "url": "ws://localhost:18789",
      "token": "",
      "adapterType": "hermes"
    }
  },
  "focused": {},
  "avatars": {},
  "deskAssignments": {},
  "analytics": {},
  "voiceReplies": {},
  "office": {},
  "standup": {},
  "taskBoard": {}
}
```

## Starting After Auto-Install

```bash
# One command:
bash ~/.hermes/hermes-office/scripts/clawd3d-start.sh

# Or two terminals:
cd ~/.hermes/hermes-office && npm run hermes-adapter
cd ~/.hermes/hermes-office && npm run dev
```

## Agent/Model Auto-Population

- **Agents:** Hermes profiles (senna, researcher, etc.) appear as agents in the 3D office automatically via the adapter. No manual agent creation needed.
- **Models page:** Shows whatever provider/model Hermes is configured with (e.g. DeepSeek + deepseek-v4-flash). Pulled from the Hermes API.
- **Sub-agents:** Can be spawned from within Claw3D using `spawn_agent` / `delegate_task` etc. — these are powered by Hermes orchestration tools under the hood.
