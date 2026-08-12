#!/usr/bin/env bash
# session_probe.sh — read-only Hermes session forensics.
#
# Usage:
#   session_probe.sh <profile> <keyword>            # find sessions mentioning keyword
#   session_probe.sh <profile> <keyword> tail <SID> # read tail of a specific session
#   session_probe.sh <profile> <keyword> head <SID> # read head of a specific session
#
# Gotcha baked in: after a /reset the new session REUSES the old session id, so a
# plain WHERE session_id=X mixes pre- and post-reset rows (and your own current
# messages). To isolate pre-reset content, find the reset-anchor message id and
# add "AND id < ANCHOR" to the tail/head query.
set -euo pipefail

PROFILE="${1:?profile required, e.g. creative}"
KEYWORD="${2:?keyword required}"
MODE="${3:-find}"
SID="${4:-}"
DB="$HOME/.hermes/profiles/$PROFILE/state.db"

[[ -f "$DB" ]] || { echo "no state.db at $DB"; exit 1; }

case "$MODE" in
  find)
    sqlite3 -separator ' | ' "$DB" "
      SELECT s.id, s.source, s.title,
             datetime(min(m.timestamp),'unixepoch','localtime') AS first,
             COUNT(*) AS n
      FROM messages m JOIN sessions s ON s.id=m.session_id
      WHERE m.content LIKE '%$KEYWORD%' AND m.role IN ('user','assistant')
      GROUP BY s.id ORDER BY first DESC LIMIT 8;"
    ;;
  tail|head)
    [[ -n "$SID" ]] || { echo "tail/head needs a session id as \$4"; exit 1; }
    ORDER="DESC"; [[ "$MODE" == "head" ]] && ORDER="ASC"
    sqlite3 -separator $'\n\n===MSG===\n\n' "$DB" "
      SELECT role||' [id='||id||']: '||substr(content,1,2500)
      FROM messages
      WHERE session_id='$SID' AND role IN ('user','assistant')
        AND content IS NOT NULL AND content!=''
      ORDER BY id $ORDER LIMIT 8;"
    ;;
  *)
    echo "mode must be find|tail|head"; exit 1 ;;
esac
