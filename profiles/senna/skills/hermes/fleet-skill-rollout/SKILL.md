---
name: fleet-skill-rollout
description: Review external skills repos and roll out per profile.
version: 1.0.0
metadata:
  hermes:
    tags: [skills, fleet, rollout, kanban, dedup, registry]
    category: hermes
---

# Fleet Skill Rollout — external repo → per-profile install

The user repeatedly sends external skill repos (hermes-skins-pack, visual-loop,
magnus919/agent-skills x2, agents-towards-prod...) and expects: full review, per-profile
placement across the WHOLE fleet (not just the current profile), tiering, install,
hygiene, and a durable registry. This is the validated workflow from the 2026-08-03
magnus919/agent-skills rollout (114 skills, 20 kanban cards, 15 profiles).

## Hard rules (learned the hard way)

1. **Inventory ALL profiles first, never just the current one.** `ls ~/.hermes/profiles/*/`
   then per-profile skill names. A skill "new to senna" is often already installed on
   media/business/knowledge — the fleet-wide overlap is much larger than the current-profile
   overlap. Compute `comm -23 remote local` per profile, not once.
2. **Read descriptions mechanically, not by hand.** SKILL.md frontmatter descriptions are
   often folded YAML (`>-`), which one-line regexes miss. Use
   `scripts/extract-skill-frontmatter.py` — it handles folded/literal blocks and prints
   `### name [version] (path)` + description for every SKILL.md.
3. **Never bulk-install blind.** Tier explicitly: A = install now, B = defer (registry),
   skip = noise. Get the user's pick before creating the wave.
4. **Install via kanban cards, one per profile** (assignee = the profile itself, so it owns
   its own skills dir). Bodies must be self-contained: exact source paths, exact target
   paths, verify steps, completion summary. Point bodies at manifest files on disk rather
   than inlining long lists.
5. **Verify on disk, not board labels.** `done` only means the worker exited cleanly.
   Check SKILL.md exists at target and its `name:` frontmatter equals the dir name.
6. **Registry note is the durable record; /tmp manifests are ephemeral.** Write the
   B-tier/installed tables into the vault (llm-wiki/operational/conventions/skill-registry.md
   convention) + a silent watchdog script + weekly cron. Cron scripts must live under
   `~/.hermes/scripts/` (absolute paths rejected) — use a tiny wrapper that execs the
   canonical script living elsewhere.

## Workflow

### Step 0 — Fleet inventory
```bash
for p in ~/.hermes/profiles/*/; do name=$(basename "$p"); [ -d "$p/skills" ] && \
  echo "$name: $(find "$p/skills" -name SKILL.md | wc -l | tr -d ' ')"; done
```

### Step 0b — Hub catalog gap analysis (variant: "what don't we have?")
When the ask is "which hub skills are NOT in the fleet" (no external repo to clone),
diff the hub curated set against every profile's frontmatter names instead:
```bash
find ~/.hermes/profiles -path '*/skills/*/SKILL.md' | while read f; do
  awk '/^---/{n++} n==2{exit} /^name:/{sub(/^name:[ ]*/,""); gsub(/["'"'"']/,""); print tolower($0); exit}' "$f"
done | sort -u > /tmp/fleet-skills.txt
COLUMNS=240 hermes skills browse --source official --size 200 \
  | awk -F'│' '/^│/ && $2 ~ /[0-9]/ {gsub(/^ +| +$/,"",$3); gsub(/….*/,"",$3); print tolower($3)}' \
  | sort -u > /tmp/hub-official.txt
```
Name = field $3 (field $2 is the row number); hub names may be truncated ~13 chars, so
prefix-match when diffing. `--source official` == `--source well-known` (same 111 set).
Then tier per profile exactly as Step 3 — results from 2026-08-03 (13/111 already
installed, 86 missing grouped by theme) in `references/hub-gap-analysis.md`.

### Step 1 — Clone + extract
```bash
git clone --depth 1 <url> /tmp/<repo>
python3 ~/.hermes/profiles/senna/skills/hermes/fleet-skill-rollout/scripts/extract-skill-frontmatter.py /tmp/<repo> > /tmp/remote-skills.txt
```

### Step 2 — Fleet-wide overlap
Compare remote skill names against EVERY profile's skill names. Already-installed =
placed correctly, note where, no action (unless version refresh needed).

### Step 3 — Tier per profile
A = install now, B = defer to registry, skip = service-specific/noise. Read deeper
(skill_view) only on candidates.

### Step 4 — Manifests + kanban wave
Write two manifests to /tmp:
- `skill-install-manifest.md`: per-profile install lists + target convention
  (`~/.hermes/profiles/<p>/skills/<category>/<skill>/`; a provenance category like
  `magnus` keeps source clear).
- `skill-dedup-manifest.md`: KEEP/DELETE pairs for nested duplicates.
Create one card per profile with `--body "$(cat /tmp/kb-bodies/<p>.md")` (bodies written
via execute_code/write_file, NOT inline case loops — see pitfalls). Dispatch once,
poll `hermes kanban show <id> | grep status`.

### Step 5 — Dedup hygiene
Bulk skill installs historically create DOUBLE-NESTED duplicates:
`skills/<cat>/<name>/<name>/SKILL.md` next to canonical `skills/<cat>/<name>/SKILL.md`.
Rule: keep the canonical top-level copy UNLESS the nested one is larger/newer (check
size + version + mtime; the oracle-aitrader case kept the nested 6.2K over canonical
3.9K). Scan with `scripts/dedup-scan.py`, then execute deletes (see approval-gate pitfall).

### Step 6 — Registry + watchdog
B-tier candidates go to the vault note (knowledge profile owns it via a kanban card) with
why-deferred notes + B→A upgrade path. Add a silent watchdog script
(`skill-registry-check.sh`: shallow-fetch repo, diff top-level skill dirs vs reviewed set,
print only NEW unreviewed skills; silent exit 0 when nothing new) and a weekly cron
(no_agent=true, `0 9 * * 0`, deliver=local, script path relative under ~/.hermes/scripts/).

## Pitfalls

- **`skills-sh/<owner>/<repo>/<skill>` identifiers from `hermes skill search` CANNOT be
  installed directly** — `hermes skills install` fails with "Could not fetch from any
  source" for both the skills-sh identifier and the bare `<owner>/<repo>/<skill>` form.
  skills.sh entries are index-only. Resolution: hit the GitHub tree API
  (`curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1"`,
  get `<branch>` from the repo endpoint's `default_branch` — varies main/master), grep
  `"path":` for the skill's SKILL.md (it may sit under `plugins/.../skills/`, `skills/`,
  or `skills/.experimental/`), then install by raw URL:
  `hermes skills install "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>/SKILL.md" --yes`.
- **`hermes skills install` lands skills UNCATEGORIZED at `skills/` top level** — `mv`
  them into a category dir afterward, or the fleet convention drifts.
- **Small-batch hub installs (a handful of skills, not a repo rollout):** skip the
  kanban wave. Install into senna first — install auto-runs the skills-guard scan
  (verdict + provenance printed) — then do your own intent pass
  (`grep -rinE "ignore (all )?previous|system prompt|exfiltrat|webhook|base64 -d|eval\(|curl [^ ]*http"`
  over the installed dir; scanners catch patterns, you check intent — iOS docs saying
  "system prompt" about Apple's permission dialog is benign, not injection). Then
  `cp -R` to each target worker profile's skills dir (explicit user direction =
  cross-profile write is fine). **Keep the senna copy** — kanban `--skill` resolves
  from the orchestrator's registry, so deleting it breaks future dispatch.
- **macOS bash 3.2 has NO associative arrays** (`declare -A` = "invalid option") and
  multi-line `for`+`case` one-liners explode under eval. Write a `.sh` script file with a
  `create_card()` function instead of inline loops. A broken inline loop can silently
  create a junk card with assignee "0" — archive it (`hermes kanban archive t_xxx`) before dispatch.
- **Headless kanban workers CANNOT consent to destructive commands.** `rm -rf` in a worker
  hits the terminal approval gate, times out, and the worker blocks with
  `kind: needs_input` ("approval gate timed out without consent... do not retry, do not
  rephrase"). Do NOT unblock+redispatch (it re-blocks). The ORCHESTRATOR (whose terminal
  has the approval path) verifies the worker's pre-delete evidence, executes the exact rm,
  verifies on disk, then `hermes kanban complete <id> --summary "rm executed by orchestrator
  after worker's approval-gate block"`.
- **`hermes kanban create --json` id key is `id`, not `task_id`** — grep it out; never pipe
  kanban stdout into python (security scanner blocks the pipe).
- **Card body too long / special chars** (parentheses, #hex, `&`) → write body to a file
  and `--body "$(cat file)"`.
- **Start stopped gateways before dispatch** for profiles receiving cards:
  `hermes -p <profile> gateway start` (workers crash with "pid not alive" on stopped gateways).

## Support files

- `references/hub-gap-analysis.md` — 2026-08-03 hub-gap results: 13/111 curated
  skills already installed, 86 missing grouped by theme, priority reads per user.
- `scripts/extract-skill-frontmatter.py` — extract name/description/version from every
  SKILL.md in a clone; handles folded YAML descriptions.
- `scripts/dedup-scan.py` — find double-nested `skills/<cat>/<name>/<name>/` duplicates
  fleet-wide with version/size/mtime so keep/delete is deterministic.
