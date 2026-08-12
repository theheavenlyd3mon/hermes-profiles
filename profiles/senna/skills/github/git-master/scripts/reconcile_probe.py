#!/usr/bin/env python3
"""
reconcile_probe.py — safe, reversible diff/reconcile probe for a divergent
git clone vs its remote (default: origin/main).

What it does (ALL non-destructive on a clean tree):
  1. Dry-run merge: `git merge --no-ff --no-commit <target>`, tally conflict
     codes, then `git merge --abort` (restores the original clean tree).
  2. Classify local-unique files (present in HEAD, absent from target) by
     all-vs-all Jaccard line-similarity:
        dup     sim >= 0.80  -> target already has equivalent content (drop)
        overlap 0.50-0.80    -> likely older/renamed version (usually drop)
        genuine < 0.50       -> truly new content (carry forward)
  3. Print a summary so the agent can decide the reconcile strategy before
     touching anything.

Usage:
    python3 reconcile_probe.py [REPO_PATH] [TARGET_REF]
    # defaults: REPO_PATH=.  TARGET_REF=origin/main

Output is human-readable. The script never commits, resets, or aborts the
user's real branch state beyond the local dry-run merge it always aborts.
"""
import subprocess, sys, os, re, json
from collections import defaultdict


def gshow(repo, ref_path):
    return subprocess.run(["git", "-C", repo, "show", ref_path],
                          capture_output=True, text=True).stdout


def lset(text):
    return set(l.rstrip() for l in text.splitlines() if l.strip())


def jac(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def norm(p):  # noqa: F841  (kept for callers wanting name-only matching)
    b = os.path.basename(p).lower().replace(".md", "")
    b = re.sub(r"^\d+[_-]?", "", b)
    b = b.replace("_", " ").replace("-", " ").replace(" and ", " ")
    return re.sub(r"\s+", " ", b).strip()


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    target = sys.argv[2] if len(sys.argv) > 2 else "origin/main"

    st = subprocess.run(["git", "-C", repo, "status", "--porcelain"],
                        capture_output=True, text=True).stdout.strip()
    if st:
        print("!! Working tree is NOT clean. Aborting (this probe needs a clean tree).")
        print(st[:500])
        sys.exit(1)

    local_list = subprocess.run(["git", "-C", repo, "ls-tree", "-r",
                                 "--name-only", "HEAD"], capture_output=True, text=True).stdout.splitlines()
    target_list = subprocess.run(["git", "-C", repo, "ls-tree", "-r",
                                  "--name-only", target], capture_output=True, text=True).stdout.splitlines()
    target_set = set(target_list)
    local_only = [f for f in local_list if f not in target_set]

    # ---- 1. reversible conflict probe ----
    print(f"=== DRY-RUN MERGE: HEAD -> {target} (will abort) ===")
    subprocess.run(["git", "-C", repo, "merge", "--no-ff", "--no-commit", target],
                   capture_output=True, text=True)
    out = subprocess.run(["git", "-C", repo, "status", "--porcelain"],
                         capture_output=True, text=True).stdout
    codes = defaultdict(int)
    for line in out.splitlines():
        c = line[:2].strip()
        if c in ("UU", "UD", "DU", "DD", "AA", "AU", "UA"):
            codes[c] += 1
    print("Conflict code tally:", dict(codes), " total:", sum(codes.values()))
    subprocess.run(["git", "-C", repo, "merge", "--abort"], capture_output=True, text=True)
    print("Aborted. Tree restored.\n")

    # ---- 2. content-similarity classification of local-unique ----
    Tset = {f: lset(gshow(repo, f"{target}:{f}")) for f in target_list}
    results = []
    for p in local_only:
        L = lset(gshow(repo, f"HEAD:{p}"))
        best, bm = -1.0, None
        for f, S in Tset.items():
            s = jac(L, S)
            if s > best:
                best, bm = s, f
        results.append({"path": p, "sim": round(best, 2), "match": bm})

    dup = [r for r in results if r["sim"] >= 0.80]
    overlap = [r for r in results if 0.50 <= r["sim"] < 0.80]
    genuine = [r for r in results if r["sim"] < 0.50]

    print(f"=== LOCAL-UNIQUE-BY-PATH: {len(local_only)} files ===")
    print(f"  DUP (drop)       : {len(dup)}")
    print(f"  OVERLAP (inspect): {len(overlap)}")
    print(f"  GENUINE (carry)  : {len(genuine)}")
    print("\n-- GENUINE (likely truly new, carry forward after reset) --")
    for r in genuine:
        print(f"  {r['sim']:.2f}  {r['path']}")
    print("\n-- OVERLAP (likely renamed/older, usually drop) --")
    for r in overlap:
        print(f"  {r['sim']:.2f}  {r['path']}  ~ {r['match']}")
    print("\n-- DUP (target has equivalent, drop) --")
    for r in dup:
        print(f"  {r['sim']:.2f}  {r['path']}  -> {r['match']}")

    out_path = os.path.join(repo if repo != "." else ".", ".reconcile_probe.json")
    json.dump({"local_only": local_only, "dup": dup, "overlap": overlap,
               "genuine": genuine, "conflict_codes": dict(codes)}, open(out_path, "w"))
    print(f"\nWrote machine-readable results to {out_path}")


if __name__ == "__main__":
    main()
