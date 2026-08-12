# Python CLI argparse gotchas (agent-friendly CLIs)

Condensed from building `ue5`, an agent-facing CLI that wraps existing helper
tool classes (`tools/file.py`, `tools/build.py`, `tools/project.py`). These are
non-obvious patterns that bite on real runs; the `python-agent-cli` SKILL.md
Gotcha 1/2 summarize them.

## 1. Global flags clobbered before the subcommand (argparse bpo-9351)

Problem: `--json` / `--config` defined only on the top parser. Then
`tool scan --json` works but `tool --json scan` prints human text — the
subparser's default overwrites the already-parsed main-level value. This is
Python bug 9351 (subparser defaults win over main parser values).

Fix: one shared parent parser carrying the globals, with `default=argparse.SUPPRESS`
so "omitted" stays absent (doesn't clobber), and pass `parents=[parent]` to the
top parser AND every subparser.

```python
parent = argparse.ArgumentParser(add_help=False)
parent.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                    help="Emit machine-readable JSON on stdout.")
parent.add_argument("--config", default=argparse.SUPPRESS,
                    help="Path to config.yaml.")

p = argparse.ArgumentParser(prog="ue5", parents=[parent], description="...")
sub = p.add_subparsers(dest="cmd", required=True)
s = sub.add_parser("scan", parents=[parent], help="...")
```

In handlers resolve the flag safely — it is absent when omitted:
```python
as_json = bool(getattr(args, "json", False))
```

## 2. Errors must go to stderr + nonzero exit (even in --json mode)

The single `emit()` helper is the only output point so `--json` can never leak
aux text. But error results (dicts with an `"error"` key) must go to **stderr**
with `sys.exit(1)`, never stdout — otherwise pipeline consumers (`jq`, other
agents) break on the mixed stream.

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

## 3. Verification checklist (run before claiming done)

```bash
python3 -m tool scan --json | python3 -c "import sys,json;json.load(sys.stdin)"   # valid JSON
python3 -m tool --json scan | python3 -c "import sys,json;json.load(sys.stdin)"   # JSON even when flag PRECEDES subcommand
python3 -m tool read --path /etc/passwd 1>/tmp/o 2>/tmp/e; \
  [ $? -ne 0 ] && [ ! -s /tmp/o ] && grep -qi error /tmp/e   # errors->stderr, empty stdout
python3 -m tool write --path x --content hi   # then again identical -> still success (idempotent)
python3 -m tool write --path y --content z --dry-run   # shows diff, file NOT created
```

## 4. QA hygiene

Run QA against a throwaway project/config in `/tmp`, never copy test configs
into the repo root. A stray `rm -f ./config.yaml` inside a QA step deletes the
committed config; restore with `git checkout HEAD -- config.yaml`.
