#!/usr/bin/env python3
"""Run the UE Agent Harness test suite + eval suite.

Usage:
    python scripts/run_test_suite.py              # both tests + eval
    python scripts/run_test_suite.py --tests-only  # just pytest
    python scripts/run_test_suite.py --eval-only   # just eval suite
"""
import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run pytest test_stub.py."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test_stub.py", "-v"],
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def run_eval():
    """Run the eval suite via python -m agentunreal.eval.run_suite."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "agentunreal.eval.run_suite", "--json"],
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    # Parse and print a summary
    import json
    try:
        data = json.loads(result.stdout)
        agg = data["aggregate"]
        print(f"\nEval Suite: {agg['passed']}/{agg['tasks']} passed "
              f"({agg['pass_rate']:.0%}) · "
              f"build-success {agg['build_success_rate']:.0%} · "
              f"avg attempts {agg['avg_build_attempts']:.1f} · "
              f"violations {agg['total_constraint_violations']}")
    except (json.JSONDecodeError, KeyError):
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def main():
    args = sys.argv[1:]
    tests_only = "--tests-only" in args
    eval_only = "--eval-only" in args

    rc = 0
    if not eval_only:
        rc = run_tests()
    if not tests_only:
        eval_rc = run_eval()
        rc = rc or eval_rc

    sys.exit(rc)


if __name__ == "__main__":
    main()