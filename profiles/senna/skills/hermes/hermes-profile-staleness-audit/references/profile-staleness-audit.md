# Profile Staleness Audit — Full Recipes

## The ONE true activity signal: state.db, not mtimes

File mtimes lie — gateway restarts and cron tickers touch logs/state.db constantly.
The authoritative "was this profile ever used" probe:

```bash
sqlite3 profiles/<p>/state.db "SELECT datetime(MAX(timestamp),'unixepoch') FROM messages;"
sqlite3 profiles/<p>/state.db "SELECT COUNT(*) FROM sessions;"
```

Pitfall: the timestamp column is `timestamp REAL` (unix epoch), NOT `created_at`.
`SELECT MAX(created_at)` errors with "no such column".

Tell-tale of a never-used shell: `state.db` ~12K, 0 sessions, "last msg: none".
Profiles like this with only gateway boot-noise logs (agent.log ~4.7K, gateway.log
~1.5K, errors.log ~847B) are batch-created clones, not real agents.

## Clone / redundant-pair detection

Two profiles are the same agent twice when ALL of these match:

```bash
diff <(grep -oE '^[A-Z_]+=' profiles/A/.env) <(grep -oE '^[A-Z_]+=' profiles/B/.env)
diff <(ls profiles/A/skills) <(ls profiles/B/skills)
diff profiles/A/config.yaml profiles/B/config.yaml   # model/skin/channel diffs are cosmetic
```

Also compare byte sizes of logs — identical sizes down to the byte across two
profiles means batch creation, not coincidental use.

## Duplicate cron pipelines (hidden LLM spend)

Two profiles can run the SAME pipeline — e.g. identical 6-job weekly research
refresh Mon–Sat plus a Sunday job at the same cron slot. Parse jobs.json:

```bash
python3 -c "import json;d=json.load(open('profiles/<p>/cron/jobs.json'));\
print('\n'.join(f\"{j.get('name')} | {j.get('schedule')} | enabled={j.get('enabled')}\" \
for j in (d if isinstance(d,list) else d.get('jobs',[]))))"
```

Missing cron/jobs.json entirely = zero scheduled jobs for that profile.
Recommendation when duplicated: consolidate onto one profile, disable the other's
jobs — disk savings ~0 but halves duplicate daily LLM spend.

## Live gateways on empty profiles

An unused profile can still have a RUNNING gateway burning RAM. Check:

```bash
cat profiles/<p>/gateway.pid   # JSON: {"pid": N, "kind": "hermes-gateway", ...}
ps -p <pid> -o pid,comm
```

Removal sequence matters: stop the gateway BEFORE recommending profile removal.

## Per-profile gathering recipe (one loop)

```bash
for p in <profiles>; do
  du -sh profiles/$p                                  # total
  du -sh profiles/$p/* profiles/$p/.[!.]* 2>/dev/null | sort -rh | head -15  # incl. hidden
  ls profiles/$p/config.yaml profiles/$p/.env         # presence
  grep -oE '^[A-Z_]+=' profiles/$p/.env               # key NAMES only, never values
  ls profiles/$p/skills | wc -l                       # category count
done
```

Dead-path check without printing secrets: extract each `*_PATH`/`*_DIR` value to a
shell var and test `[ -e "$v" ]`, reporting only OK/DEAD.

## Typical reclaimable items (real sizes, 2026-07 audit of 5 profiles)

| Item | Size | Note |
|---|---|---|
| never-used profile (whole dir) | ~28M each | 20M of it is bin/tirith binary |
| knowledge/lsp/node_modules | ~34M | regenerable via npm i |
| logs/ on ACTIVE profiles | 24–25M each | rotate, don't delete profile |
| models_dev_cache.json | ~3M each | regenerable |
| config.yaml.corrupt.*.bak | ~16K | leftover from failed write |

Full audit example: research 104M ACTIVE (64 sessions), knowledge 161M ACTIVE
(103 sessions, duplicate cron pipeline vs research), educate 31M DORMANT,
researcher + secretary 28M each — zero sessions ever, live gateways PIDs present,
byte-identical .env keys and skills → both CANDIDATE-FOR-REMOVAL.
