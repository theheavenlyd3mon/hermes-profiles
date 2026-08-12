# `hermes skills search discord` — condensed results

Run: `hermes skills search discord` → **25 results** across skills.sh + clawhub (all "community" trust).

## Most relevant to a Hermes manager/moderation bot

| Identifier | What it does | Caveat |
|---|---|---|
| `clawhub/discord-communities` | Manage guilds, channels, messages, members, roles | OpenClaw/Clawdbot idiom — inspect before use |
| `clawhub/discord-channel-auditor` | Auto-update a server guide/info channel | Genuinely useful for onboarding; verify framework fit |
| `clawhub/discord-chat` / `discord-chat-1-0-0` | Send/reply/search messages | Other-framework DSL |
| `skills-sh/steipete/clawdis/discord` | Indexed from a claude/discord skill | Inspect first |
| `clawhub/discord` | Generic Discord request handler | Generic |

## Bulk of the rest

`oo-discord`, `discord-hub`, `taizi-discord`, `discord-bot` (×2), `discord-claude-code-delegation`, `discord-connect-ui`, `discord-connect-wizard` — mostly Clawdbot/OpenClaw/Claude-Code specific.

## Takeaway

The Hermes-native path for a manager bot is the built-in **`hermes-discord` toolset** + **`discord_admin`** actions (gated by `server_actions` in config.yaml). Hub skills are supplementary — `inspect` any before install, since most assume non-Hermes frameworks.
