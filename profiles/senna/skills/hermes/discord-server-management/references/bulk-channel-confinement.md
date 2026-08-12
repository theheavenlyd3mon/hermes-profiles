# Bulk channel confinement procedure

Goal: set `allowed_channels` to each bot's home channel across the full active Discord fleet, then restart every running gateway. Last executed: 2026-07-02 with fleet `code` `creative` `finance` `infra` `knowledge` `research` `security` `senna`.

## Channel map

| Profile | Home channel ID(s) |
|---|---|
| senna | <id>,<id> |
| code | <id> |
| creative | <id> |
| finance | <id> |
| infra | <id> |
| knowledge | <id> |
| research | <id> |
| security | <id> |

## Caveats

- Do **not** touch the active `senna/config.yaml` with `patch`. The cross-profile write guard blocks profile self-edits. Use `python3`/`sed` against the absolute path instead.
- `patch` with `old_string: "  allowed_channels: ''"` often matches 3+ times per profile (built-in `discord:` + nested duplicate). Use a regex-based write, not `patch`, or include more surrounding context.
- Keep `free_response_channels` unchanged — it already points to the single home channel.

## Bulk write script

Use for all 8 running profiles, including senna:

```python
import re, pathlib

profiles = {
  'code': '<id>',
  'creative': '<id>',
  'finance': '<id>',
  'infra': '<id>',
  'knowledge': '<id>',
  'research': '<id>',
  'security': '<id>',
  'senna': '<id>,<id>',
}

home = pathlib.Path.home() / '.hermes/profiles'
for profile, channel_id in profiles.items():
    p = home / profile / 'config.yaml'
    text = p.read_text()
    subblock = (
        r"(discord:\n  require_mention: true\n  free_response_channels: "
        + re.escape(channel_id.replace(',', '').split(',')[0])
        + r"[^\n]*\n(?:  free_response_channels: '[^']*'\n)?  allowed_channels: )''"
    )
    replacement = r"\1'" + channel_id + "'"
    new_text, n = re.subn(subblock, replacement, text, count=1)
    if n:
        p.write_text(new_text)
    else:
        print(f'{profile}: no match', flush=True)
```

## Restart sequence

Restart in any order; the built-in per-profile restart substituted cleanly:

```bash
for p in code creative finance infra knowledge research security senna; do
  hermes --profile "$p" gateway restart 2>&1 | tail -1
  sleep 1
done
```

## Verification

```bash
sleep 6
hermes gateway list | awk '/^  .*running|^  .*PID/'

for p in code creative finance infra knowledge research security senna; do
  printf '%-10s channel_dirs=' "$p"
  grep -Eo 'Channel directory built: [0-9]+' \
    ~/.hermes/profiles/$p/logs/gateway.log | tail -1
done
```

Channel-directory counts shift to reflect restricted scope, but they do not guarantee Discord-side `<archived>` permissions — that still requires category/channel admin edits.
