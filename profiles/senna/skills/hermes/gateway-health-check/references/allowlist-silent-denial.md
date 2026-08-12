# Allowlist Silent Denial

Bot is online, gateway is healthy, but the user gets zero responses.

## Log Signatures

```
WARNING gateway.run: No env user allowlists configured. Messaging platforms default to pairing/allowlist policies and will deny unknown senders unless you configure platform allowlists (e.g., TELEGRAM_ALLOWED_USERS=your_id) or explicitly opt in with GATEWAY_ALLOW_ALL_USERS=true plus dm_policy/group_policy: open on the platform.

WARNING hermes_plugins.discord_platform.adapter: [Discord] Discord messages are being denied because no allowlist is configured. Set DISCORD_ALLOWED_USERS, DISCORD_ALLOWED_ROLES, or DISCORD_ALLOWED_CHANNELS, or set DISCORD_ALLOW_ALL_USERS=true for open access.

WARNING hermes_plugins.discord_platform.adapter: [Discord] Unauthorized slash attempt: user=<name> id=<id> channel=<chan> guild=<guild> cmd='/reset' reason='user not in DISCORD_ALLOWED_USERS / DISCORD_ALLOWED_ROLES'
```

## Diagnosis

```bash
# Check if allowlist exists
grep 'DISCORD_ALLOWED_USERS' ~/.hermes/profiles/<name>/.env

# Find the user's Discord ID from a working bot's log
grep 'invoked by user=' ~/.hermes/profiles/<working>/logs/gateway.log | tail -1
# Extract: id=968599126101098547
```

## Fix

```bash
echo 'DISCORD_ALLOWED_USERS=<user_id>' >> ~/.hermes/profiles/<name>/.env
hermes --profile <name> gateway restart
```

## .env Append Gotcha

If the `.env` file's last line has no trailing newline, `echo 'X=Y' >> .env`
concatenates onto the previous line instead of creating a new one:

```
DISCORD_IGNORED_CHANNELS=123,456DISCORD_ALLOWED_USERS=789   # BROKEN
```

**Safe append pattern:**

```bash
# Ensure trailing newline before appending
printf '\nDISCORD_ALLOWED_USERS=%s\n' "<user_id>" >> ~/.hermes/profiles/<name>/.env
```

Or use Python for guaranteed correctness:

```python
path = os.path.expanduser('~/.hermes/profiles/<name>/.env')
with open(path, 'a') as f:
    f.write('\nDISCORD_ALLOWED_USERS=<user_id>\n')
```

## Distinguishing From Other "Silent" Failures

| Symptom | Allowlist | Wrong Guild | Token Collision |
|---------|-----------|-------------|-----------------|
| Bot in member list? | Yes | No | Yes (as wrong name) |
| `Connected as` in log? | Yes | Yes | Yes |
| Messages denied in log? | Yes | No | No |
| Bot identity matches? | Yes | Yes | No |
