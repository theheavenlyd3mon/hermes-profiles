---
name: python-agent-cli
description: >-
  Build or maintain Python CLIs designed for AI-agent consumption — thin argparse
  wrappers over existing tool modules with --json machine output, --dry-run preview,
  and errors-to-stderr contracts. Use when wrapping repo helper classes into an
  agent-facing CLI, debugging why an agent keeps mis-calling your Python CLI, or
  hitting argparse global-flag / output-routing pitfalls. Companion to the
  (pinned) cli-builder skill, focused on Python-specific gotchas.
license: MIT
metadata:
  tags: [cli, agent-tooling, python, argparse, automation]
---

# Python Agent CLI — patterns & pitfalls

Companion to `cli-builder`. The broader design principles (non-interactive,
idempotent, `--dry-run`, examples in `--help`) live there; this skill covers the
**Python/argparse-specific** traps that surface only on real runs and that the
general skill does not prevent.

## When to use
- Wrapping existing Python tool classes (e.g. `tools/file.py`, `tools/build.py`) into a CLI the agent calls.
- A `--json` flag works after the subcommand but not before it.
- Error output is leaking to stdout / breaking `jq` consumers.
- You need a copy-paste verification checklist before claiming the CLI is agent-ready.

## Principle: thin wrapper, not reimplementation
If the operations already exist as Python classes/functions in the repo, the CLI
is a thin `argparse` shell that *calls* them — do NOT duplicate the logic in the
CLI. The CLI is only the machine-facing contract (flags, `--json`, `--dry-run`,
exit codes); all real work stays in the underlying modules so there is one source
of truth.

## Gotcha 1 — global flags clobbered before the subcommand (argparse bpo-9351)
`tool scan --json` works but `tool --json scan` prints human text: the subparser's
default silently overwrites the already-parsed main-level value (Python bug 9351).
Fix: one shared parent parser carrying the globals with `default=argparse.SUPPRESS`,
passed via `parents=[parent]` to BOTH the top parser and every subparser; resolve
with `getattr(args, "json", False)`.

## Gotcha 1a — Python 3.12+ changed behavior
Python 3.12 modified argparse's handling of global flags. The fix now requires:
`parent = argparse.ArgumentParser(add_help=False)` and passing `parent` to both
the main parser and all subparsers. Previous fixes may not work with newer Python.

```python
parent = argparse.ArgumentParser(add_help=False)
parent.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                    help="Emit machine-readable JSON on stdout.")
parent.add_argument("--config", default=argparse.SUPPRESS, help="Path to config.yaml.")

p = argparse.ArgumentParser(prog="ue5", parents=[parent], description="...")
sub = p.add_subparsers(dest="cmd", required=True)
s = sub.add_parser("scan", parents=[parent], help="...")
```

## Gotcha 2 — errors must go to stderr + nonzero exit
A single `emit()` helper is the only output point so `--json` can never leak aux
text. Error results (dicts with an `"error"` key) go to **stderr** with
`sys.exit(1)`, never stdout — otherwise pipeline consumers break on the mixed stream.

```python
def _emit(obj, human):
    as_json = bool(getattr(args, "json", False))
    is_err = isinstance(obj, dict) and bool(obj.get("error"))
    payload = json.dumps(obj) if as_json else human
    if is_err:
        sys.stderr.write(payload + "\n")
        sys.exit(1)
    sys.stdout.write(payload + "\n")
```

## Verification checklist (run before claiming done)
Don't hand-type these — run `scripts/verify_agent_cli.sh <module> <config.yaml> [repo_dir]`.
It drives the universal contract checks (json valid pre/post subcommand via the
bpo-9351 guard, errors→stderr+nzexit, missing-arg names the flag, idempotent
write, dry-run preview). The CLI-specific checks (subcommand names) are marked
with a comment — edit them to match your subcommands. Then commit the same checks
as `tests/test_<module>_cli.py` (subprocess-driven, real `--config`) so a
regression fails loudly instead of silently.

## Pitfall — QA step can delete a tracked file by accident
A QA run that copies a temp `config.yaml` into the repo root and later `rm`s it
will delete the REAL committed `config.yaml` if the copy landed at the same path.
Always write QA fixtures under a temp dir (e.g. `/tmp/qa/`), and after any QA that
touched the repo root, confirm `git status --porcelain config.yaml` is clean
(`git checkout HEAD -- config.yaml` to recover from the committed version).

## References
- [references/python-cli-argparse-gotchas.md](references/python-cli-argparse-gotchas.md) — argparse pitfalls, the `emit()` routing pattern, copy-paste verification checklist, QA hygiene.
- [scripts/verify_agent_cli.sh](scripts/verify_agent_cli.sh) — re-runnable contract harness (12 checks). Run it; don't hand-type the checks.
