# Stale / Orphan Script Audit

How to find scripts that exist on disk but are referenced by nothing — cron,
skill, config, or SOUL — so the user can decide what to delete. Verified
workflow from 2026-08-03 (found 8 stale files in senna + root, ~35 scratch
files in gamehub-mod, and 1 broken job referencing a missing script).

## The Audit: classify every script against every reference source

A script is IN USE if any of these reference it:

1. **Cron jobs** — `script:` field on any job in any profile's `cron/jobs.json`.
   Cron stores are PER-PROFILE: `profiles/*/cron/jobs.json` (not just the
   active profile's). A job's `script` resolves against the profile that OWNS
   the job (`<profile>/scripts/`), not the session's active profile.
2. **Skills** — filename mentioned in `SKILL.md`, `references/`, or a bundled
   copy under `skills/<cat>/<skill>/scripts/`.
3. **Config / SOUL / plugins** — filename in `config.yaml`, `SOUL.md`, plugin dirs.

### Step 1 — enumerate all script dirs

```bash
for d in ~/.hermes/profiles/*/scripts ~/.hermes/scripts; do
  [ -d "$d" ] && echo "--- $d" && ls -la "$d" | tail -n +2
done
```

### Step 2 — collect every script referenced by cron (all profiles)

```bash
for f in profiles/*/cron/jobs.json cron/jobs.json; do
  [ -f "$f" ] && python3 -c "
import json, sys
data = json.load(open('$f'))
jobs = data if isinstance(data, list) else data.get('jobs', data.get('entries', []))
for j in jobs:
    s = j.get('script')
    if s: print('$f', j.get('name'), '->', s)
"
done
```

### Step 3 — grep skills / config / SOUL for each candidate filename

```bash
for s in <script-names...>; do
  hits=$(grep -rl "$s" profiles/senna/skills profiles/senna/plugins \
    profiles/senna/config.yaml profiles/senna/SOUL.md \
    profiles/*/config.yaml profiles/*/SOUL.md 2>/dev/null \
    | grep -v curator_backups | wc -l | tr -d ' ')
  echo "$s -> $hits"
done
```

**Pitfalls in the grep step:**
- Exclude `.curator_backups/` — backup snapshots of old cron jobs reference
  every historical script and produce false "in use" hits.
- `state.db` / `logs/*.log` matches are HISTORICAL (past session text), not
  live references. A script found only in state.db/logs is still stale.
- Self-match: `~/.hermes/scripts/foo.sh` greps itself when the search path
  includes the scripts dir. Verify hits point at real references.
- Whole-tree `grep -rl` over `~/.hermes` times out (180s+). Restrict to the
  dirs that matter: skills, plugins, configs, SOULs.

### Step 4 — check skill-bundled copies vs profile-scripts copies

Skills often bundle their own `scripts/` copies (e.g.
`gamehub-mod/skills/integrations/discord-moderation-bot/scripts/`). The
profile-scripts dir may hold older scratch versions. Compare:

```bash
for f in skills/<cat>/<skill>/scripts/*; do
  b=$(basename "$f")
  if [ -f "scripts/$b" ]; then
    cmp -s "$f" "scripts/$b" && echo "IDENTICAL: $b" \
      || echo "DIFFERS: $b (skill=$(wc -c < "$f") vs scripts=$(wc -c < "scripts/$b"))"
  else
    echo "NO-PROFILE-COPY: $b"
  fi
done
```

Divergence matters: a cron job runs the PROFILE copy (cron resolves
`<profile>/scripts/`), not the skill copy. If the skill's is newer, the cron
is running stale logic.

### Step 5 — classify and report

- **IN USE** (cron or skill or config ref) → keep, no action.
- **STALE** (zero live refs) → deletion candidates. Report size + purpose
  hint; let the user decide.
- **BROKEN** (cron job references a script that exists NOWHERE on disk) →
  not a delete decision, a fix decision: recreate the script or remove the
  job. Check `cron/executions.db` (table `executions`, filter `job_id`) to
  see what the job actually did in past runs.

## Real-world results (2026-08-03)

- senna/scripts + root scripts: 8 stale files (28K total) — fetch_playlist_transcripts.py,
  patch-hermes-desktop.py, hermes-desktop-version-check.py (0-byte),
  restart_research.sh (dup in both dirs), post-clone-scan.sh, retry_failed.sh,
  supply-chain-guard.sh.
- gamehub-mod/scripts: ~35 files / 172K of one-off server-provisioning scratch
  (provision_server.py, create_roles.py, apply_muted_*, verify_*, inspect_*,
  discord_diag.py, etc.); only audit_watch.sh is live (cron audit-watch job).
- checkpoint-cleanup (48a23e15afa4): references checkpoint-cleanup.sh that
  exists nowhere. executions.db showed `completed` under the pre-update
  gateway — old scheduler tolerated missing scripts silently. Post-v0.19
  scheduler alerts instead (see SKILL.md pitfall).
