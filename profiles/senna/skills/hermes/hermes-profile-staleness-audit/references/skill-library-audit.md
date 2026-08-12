# Skill Library Content Audit (excess/redundancy pruning)

Use when the user asks "audit my skills", "do I have too many skills", or wants a profile's skill library slimmed. CONTENT audit (overlap, duplication, staleness) — distinct from profile-activity and disk-space audits. Same read-only mandate: report, get batched approval, then prune.

## Procedure

1. **Inventory from disk, not the catalog.** The system-prompt skill index can lag reality.
   ```bash
   cd ~/.hermes/profiles/<profile>/skills
   for d in $(find . -name SKILL.md | sed 's|/SKILL.md||'); do
     sz=$(du -sk "$d" | cut -f1); mt=$(stat -f '%Sm' -t '%Y-%m-%d' "$d/SKILL.md")
     echo "$sz KB | $mt | $d"
   done | sort -t'|' -k3
   ```
2. **Empty category dirs** — zero SKILL.md inside, always safe to delete:
   ```bash
   for c in */; do n=$(find "$c" -name SKILL.md | wc -l | tr -d ' '); [ "$n" = "0" ] && echo "EMPTY: $c"; done
   ```
3. **Cross-profile duplicates.** If a router profile (e.g. senna) holds domain skills the domain worker profile also owns (e.g. `financial-markets/oracle-*` on both senna and finance), the router's copies are excess — it delegates, never loads them:
   ```bash
   find ~/.hermes/profiles/<other>/skills -name SKILL.md | sed 's|.*/skills/||'
   ```
4. **Overlap/merge candidates.** Near-duplicate names solving the same problem (two git-reconcile skills; two model-fleet snapshots where only one can be current).
5. **Staleness heuristic.** Old mtime + the workflow it describes has shipped = archive candidate. Skills touched in the last ~2 weeks are low-priority even if overlapping.
6. **Suite dependencies.** If skill A orchestrates skills B/C/D, it's keep-all or kill-all — present as ONE decision.

## Counter-intuitive rule

Disk size ≠ context cost. Only each skill's one-line description is loaded per turn; a 1MB skill dir costs the same context as a 4KB one. Never flag large skills as library bloat. (Oversized SKILL.md files are a separate load-time problem — see hermes-directory-cleanup's `oversized-skill-context-freeze.md`.)

## Presentation

Group findings: CONFIRMED EXCESS / OVERLAP (merge) / STALE (user call) / NOT EXCESS. Numbered list for batched go-ahead ("1-8: yes/no"). Nothing deleted before approval; offer a git safety commit first.

## Real example (2026-07-28, senna)

96 skills on disk. Found: 16 empty category dirs; 6 oracle/trading skills duplicated on the finance profile (which owns them + trade-tracking); 2 competing profile-model-fleet snapshots; 2 overlapping git-reconcile skills; a 4-skill idea-doc suite untouched since May; post-event hackathon cluster. Recommendation: 96 → ~85 with 2 merges.
