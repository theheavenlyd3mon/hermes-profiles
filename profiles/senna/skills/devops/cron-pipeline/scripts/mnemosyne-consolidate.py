#!/usr/bin/env python3
"""Mnemosyne memory consolidation cron job.

Runs sleep_all_sessions against the LIVE profile-scoped mnemosyne DB.

PATH HISTORY (why this changed):
- Pre-2026-07-27 this script targeted the GLOBAL DB at
  ~/.hermes/mnemosyne/data/mnemosyne.db. That DB went stale at profile
  migration (last write 2026-06-24) — consolidating it was a no-op against
  a frozen store while the live profile DB accumulated. It also caused a
  phantom "no writes since May 27" dojo-nightly flag. Archived 2026-07-27
  as mnemosyne.db.legacy-20260727. Do NOT point back at the global path.

Usage:
  ~/.hermes/hermes-agent/venv/bin/python scripts/mnemosyne-consolidate.py

Verified 2026-07-27: live profile DB working=1278, episodic=164,
43 writes on the day itself. Archive-check: global path no longer exists.
"""
import sqlite3
import sys
from pathlib import Path
from mnemosyne.core.memory import Mnemosyne

PROFILE_DB = Path("~/.hermes/profiles/senna/mnemosyne/data/mnemosyne.db")
LEGACY_GLOBAL_DB = Path("~/.hermes/mnemosyne/data/mnemosyne.db")


def resolve_db():
    if PROFILE_DB.exists():
        return PROFILE_DB
    # ponytail: size guard — post-migration the global path is a 0-byte shell
    # with no tables; falling back to it crashes on "no such table: working_memory"
    if LEGACY_GLOBAL_DB.exists() and LEGACY_GLOBAL_DB.stat().st_size > 0:
        print("WARNING: profile DB missing, falling back to legacy global DB — "
              "verify this is intentional", file=sys.stderr)
        return LEGACY_GLOBAL_DB
    sys.exit("No mnemosyne DB found at profile or legacy path.")


def get_stats(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM working_memory WHERE consolidated_at IS NULL")
    unconsolidated = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) as c FROM working_memory")
    working = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) as c FROM episodic_memory")
    episodic = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(DISTINCT session_id) as c FROM working_memory")
    sessions = cur.fetchone()["c"]
    conn.close()
    return working, unconsolidated, episodic, sessions


def main():
    db = resolve_db()
    print(f"DB: {db}")
    before_working, before_uncons, before_episodic, before_sessions = get_stats(db)
    print(f"PRE: working={before_working}, unconsolidated={before_uncons}, "
          f"episodic={before_episodic}, sessions={before_sessions}")

    mnemo = Mnemosyne(session_id="cron_consolidation", db_path=db)
    result = mnemo.sleep_all_sessions(dry_run=False)
    print(f"RESULT: {result}")

    after_working, after_uncons, after_episodic, _ = get_stats(db)
    print(f"POST: working={after_working}, unconsolidated={after_uncons}, "
          f"episodic={after_episodic}")
    print(f"DIFF: items_consolidated={result.get('items_consolidated', 0)}, "
          f"summaries_created={result.get('summaries_created', 0)}, "
          f"sessions_scanned={result.get('sessions_scanned', 0)}, "
          f"method={result.get('method', 'unknown')}")


if __name__ == "__main__":
    main()
