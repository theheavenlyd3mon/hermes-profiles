#!/usr/bin/env python3
"""divergence_reconcile.py

Classify local-only git files vs a remote base by CONTENT, not by path.

WHY: When a local branch and the remote both restructured in parallel (renames,
re-dos, de-dup passes), the naive "keep files that only exist locally" plan
re-creates duplicates -- the same content lives under different paths on each
side. Example from a real vault sync: local `BP_Class_3_Events_Functions.md`
vs origin `BP_Class_3_Events_and_Functions.md` are the same note renamed.
Path-only comparison calls both "unique" and you end up with two copies.

Classify every local-only-by-path file as:
  - dup     (>=0.80 Jaccard vs some remote file) -> drop, remote has equivalent
  - overlap ( 0.50-0.80)                          -> likely rename / older version, review
  - genuine ( <0.50)                             -> truly unique, keep

Normalization strips leading numbers and the word "and" so rename pairs like
  Events_Functions.md  vs  Events_and_Functions.md
still match on content rather than name.

Usage:
  python3 divergence_reconcile.py <repo_path> [local_ref] [remote_ref]
Defaults: local_ref=HEAD, remote_ref=origin/main
Output: human summary to stdout + .divergence_classified.json in the repo.
"""
import subprocess, os, re, sys, json

def run(repo, args):
    return subprocess.run(["git", "-C", repo] + args, capture_output=True, text=True).stdout

def norm(p):
    b = os.path.basename(p).lower().replace('.md', '')
    b = re.sub(r'^\d+[_-]?', '', b)
    b = b.replace('_', ' ').replace('-', ' ')
    b = re.sub(r'\s+', ' ', b).replace(' and ', ' ')
    return b.strip()

def lset(repo, sha):
    return set(l.rstrip() for l in run(repo, ["show", sha]).splitlines() if l.strip())

def jac(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    local = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    remote = sys.argv[3] if len(sys.argv) > 3 else "origin/main"

    local_files = run(repo, ["ls-tree", "-r", "--name-only", local]).splitlines()
    remote_files = run(repo, ["ls-tree", "-r", "--name-only", remote]).splitlines()
    remote_set = set(remote_files)
    local_only = [f for f in local_files if f not in remote_set]

    Os = {f: lset(repo, f"{remote}:{f}") for f in remote_files}
    out = []
    for p in sorted(local_only):
        L = lset(repo, f"{local}:{p}")
        best = -1.0
        bm = None
        for f, S in Os.items():
            s = jac(L, S)
            if s > best:
                best, bm = s, f
        out.append({"path": p, "best_sim": round(best, 2), "best_match": bm})

    dup = [r for r in out if r["best_sim"] >= 0.8]
    ov = [r for r in out if 0.5 <= r["best_sim"] < 0.8]
    ge = [r for r in out if r["best_sim"] < 0.5]

    print(f"local-only-by-path: {len(local_only)}   dup={len(dup)}  overlap={len(ov)}  genuine={len(ge)}\n")
    print(f"### GENUINE (keep) -- {len(ge)}")
    for r in ge:
        print(f"  {r['best_sim']:.2f}  {r['path']}")
    if ov:
        print(f"\n### OVERLAP (review) -- {len(ov)}")
        for r in ov:
            print(f"  {r['best_sim']:.2f}  {r['path']}  ~{r['best_match']}")
    print(f"\n### DUP (drop) -- {len(dup)}")
    for r in dup:
        print(f"  {r['best_sim']:.2f}  {r['path']}  -> {r['best_match']}")

    json.dump({"genuine": ge, "overlap": ov, "dup": dup},
              open(os.path.join(repo, ".divergence_classified.json"), "w"))
    print(f"\nwrote {os.path.join(repo, '.divergence_classified.json')}")

if __name__ == "__main__":
    main()
