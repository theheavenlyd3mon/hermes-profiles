# Bot Connected but in Wrong Guild

## Symptom
Gateway logs show `Connected as <BotName>` and process is healthy (PID in `hermes gateway list`), but the bot does NOT appear in the member list of the server the user is looking at. User says "bot is not connecting" or "not responding" — it's actually online in a *different Discord server*.

## Distinguish from Home-Channel Scoping
Home-channel scoping = bot is in the right server but only auto-responds in one channel (still visible in member list). Wrong-guild = bot is in a completely different server (absent from member list entirely). **Check the member list first.** If the bot isn't there at all, it's a guild problem, not a channel problem.

## Diagnosis

```bash
# 1. Confirm the bot IS connected (gateway is healthy)
grep "Connected as" ~/.hermes/profiles/<p>/logs/gateway.log | tail -1

# 2. Check which guild the bot is configured for
grep 'DISCORD_GUILD_ID' ~/.hermes/profiles/<p>/.env

# 3. Compare against a known-working bot in the target server
grep 'guild=' ~/.hermes/profiles/senna/logs/gateway.log | tail -1
# (or any bot confirmed online in the user's server)

# 4. Check channel IDs too
grep -E 'DISCORD_(HOME_CHANNEL|ALLOWED_CHANNELS|FREE_RESPONSE)' ~/.hermes/profiles/<p>/.env
```

If guild IDs differ → the bot was never invited to (or was removed from) the target server.

## Fix

1. **Generate invite link** from the bot token's client ID:
   ```python
   import base64
   # First dot-segment of token is base64-encoded bot user ID
   uid = base64.b64decode(token.split('.')[0] + '==').decode()
   print(f'https://discord.com/oauth2/authorize?client_id={uid}&scope=bot%20applications.commands&permissions=274878220352')
   ```
2. **User opens the link**, selects the correct server, authorizes.
3. **Update `.env`**: set `DISCORD_GUILD_ID` to the target server's guild ID, update `DISCORD_HOME_CHANNEL`, `DISCORD_ALLOWED_CHANNELS`, `DISCORD_FREE_RESPONSE_CHANNELS` to the correct channel IDs.
4. **Check `config.yaml`**: `discord.allowed_channels` and `discord.free_response_channels` may hardcode different channel IDs than `.env`. The `.env` values win at runtime, but both should agree to avoid confusion.
5. **Restart**: `hermes --profile <p> gateway restart`

## Real Example (2026-07-20)
Novel bot: guild `1524839522876129330`, channels `1524890193986064486`. Noctis Hub: guild `1508910747382583610`, #writing-room `1508955982871662694`. Bot was healthy and connected — just in a completely different server. Also had a stale `config.yaml` hardcoding yet another channel ID that didn't match `.env`.

## Key Insight
"Bot not connecting" ≠ "bot offline." Always check the member list in the user's actual server first. If the bot isn't there, it's a guild/invite problem, not a gateway/token/config problem. The gateway logs will look perfectly healthy.
