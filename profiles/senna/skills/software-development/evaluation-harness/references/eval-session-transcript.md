# Eval Harness Debugging Session — 2026-07-23

## Summary

Expanded the eval task suite from 4 to 26 tasks and fixed 6 bugs in the
eval pipeline. All 15 unit tests pass; all 26 eval tasks pass (100%).

## Bugs fixed

1. **Prompt path resolution** — `Path("prompts/system.txt")` broke when run
   as a module from a tmp dir. Fixed to `Path(__file__).resolve().parent.parent.parent / "prompts" / name`.
2. **ScriptedLLM planner collision** — The scripted LLM consumed its first
   call on the planner step. Fixed by handling `tools is None` separately.
3. **Session file selection** — `sorted(glob("*.jsonl"))[-1]` picked
   `metrics.jsonl` (alphabetically last). Fixed by filtering out
   `metrics.jsonl` and `trajectories.jsonl`.
4. **Harvest enrichment** — Raw log didn't include `tool_name` in tool
   messages, so the harvester couldn't verify `dry_run → write_file`
   ordering. Added `tool_name` to the log entry.
5. **Tool parameter naming** — ScriptedLLM called `build_module` with
   `{"module": "MyGame"}` but the signature expects `module_name`.
   Fixed to `{"module_name": "MyGame"}`.
6. **Task suite expansion** — 4 → 26 tasks across all four kinds.

## Commands

```bash
# Run both tests and eval
python scripts/run_test_suite.py

# Just pytest
python scripts/run_test_suite.py --tests-only

# Just eval suite
python scripts/run_test_suite.py --eval-only

# Or directly:
pytest test_stub.py -v                          # 15 passed
python -m agentunreal.eval.run_suite --json     # 26 tasks, 26 passed, 0 violations
```

## Task suite breakdown

| Kind | Count | IDs |
|------|-------|-----|
| new-class | 10 | mana-component, combat-component, character-base, item-actor, game-mode, player-controller, weapon-actor, animation-instance, save-game, game-instance |
| build-fix | 3 | missing-include, undef-pointer, header-guard |
| refactor | 3 | tmap-to-tarray, delegate-to-tarray, fstring-to-fname |
| editor-command | 6 | stat-unit, stat-scene, stat-memory, stat-physics, compile-blueprints, is-editor-running |
| (original) | 4 | build-fix-undeclared-helper, editor-stat-fps, new-class-stamina, refactor-tobjectptr |

## Full debugging transcript

See `references/eval-harness-debugging.md` in the `unreal-engine-agent-harness`
umbrella skill for the full transcript with code diffs.