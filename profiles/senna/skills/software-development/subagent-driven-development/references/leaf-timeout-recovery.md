# Leaf subagent timeout recovery (600s ceiling)

## When this fires
A `delegate_task` leaf returns `status=timeout` (or never reports) while the
target repo shows uncommitted `M`/`D` files in `git status`. The agent was
editing when it died — its edits are **partial and unverified**, and anything it
owed (tests, commit) is missing.

## Recovery protocol (orchestrator does this, do NOT re-dispatch + hope)
1. **Repo is truth, not the summary.** `git diff --stat HEAD` +
   `git status --porcelain` to see exactly what landed on disk.
2. **Compile + import check before trusting:**
   ```bash
   cd <repo>
   for f in $(git diff --name-only HEAD -- '*.py'); do
     python3 -m py_compile "$f" 2>&1 | head -3   # deleted files error here = expected
   done
   python3 -c "import <pkg>"        # smoke import of touched modules
   ```
3. **Re-derive missing pieces the dead agent owed.** A timed-out agent
   frequently leaves its test file unwritten. Write it yourself, then run it.
   - If **pytest is NOT installed** (PEP 668 externally-managed env;
     `python3 -m pytest` → "Failed to spawn process: No such file or
     directory"): run `unittest` with a `sys.path` shim instead:
     ```python
     import sys, unittest
     sys.path.insert(0, 'tests')
     suite = unittest.TestLoader().loadTestsFromName('test_security_injection')
     sys.exit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
     ```
4. **Confirm cross-agent file intersections survived** (see the
   "same-file wave" pitfall in SKILL.md). Grep the shared file for markers
   from BOTH agents.
5. **Commit what's verified**, in reviewable slices (one commit per
   sub-theme; stage only each agent's owned files — never `git add -A`).
   State explicitly that the timed-out agent's edits are *unverified-partial*
   and what you added to close the gap. Do NOT fabricate a "completed"
   status for it.

## Gotcha: trust-boundary / signature mismatches in hand-written tests
If your recovery test imports a symbol the agent's refactor turned into a
method (e.g. `model_card` became `CanonicalStore.model_card`, no longer
exported at module level), the import fails. Verify the real signature
before writing the test:
```bash
python3 -c "import inspect; from mnemosyne.core.canonical import CanonicalStore; print(inspect.signature(CanonicalStore.model_card))"
```
Prefer testing the *defense path* the agent actually wired (e.g. the
`sanitize_for_render` helper `model_card` calls) over instantiating a
DB-backed store just to reach one method.

## Anti-pattern to avoid
Treating the agent's "no summary — status=timeout" as "nothing happened"
and re-dispatching a fresh agent that *also* can't finish. The edits are
already on disk; verify + complete them directly.
