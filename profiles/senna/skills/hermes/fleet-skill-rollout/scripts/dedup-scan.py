#!/usr/bin/env python3
"""Find double-nested skill duplicates fleet-wide (or in one profile).

Bulk skill installs create skills/<cat>/<name>/<name>/SKILL.md next to the
canonical skills/<cat>/<name>/SKILL.md. This prints every duplicate cluster
with version/size/mtime so the keep/delete decision is deterministic.

Rule: keep the canonical top-level copy UNLESS the nested one is larger or
newer (compare version field, then size, then mtime). One known inverted case:
finance/oracle-aitrader kept the NESTED 6.2K over the canonical 3.9K.

Usage:
    python3 dedup-scan.py                 # scan all profiles under ~/.hermes/profiles
    python3 dedup-scan.py <profile-dir>   # scan one profile
"""
import os, re, glob, sys, datetime

def version_of(path):
    try:
        txt = open(path, encoding='utf-8', errors='replace').read()
    except Exception:
        return '?'
    m = re.search(r'^version:\s*"?([\w.\-]+)"?', txt, re.M)
    return m.group(1) if m else '(none)'

def scan(base):
    byname = {}
    for f in glob.glob(os.path.join(base, 'skills', '**', 'SKILL.md'), recursive=True):
        name = os.path.basename(os.path.dirname(f))
        byname.setdefault(name, []).append(f)
    for name in sorted(byname):
        paths = byname[name]
        if len(paths) < 2:
            continue
        print(f"{name} x{len(paths)}")
        for path in sorted(paths, key=os.path.getmtime):
            st = os.stat(path)
            when = datetime.datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M')
            print(f"  {when} v{version_of(path)} {st.st_size:>7}B {path}")
        # keep recommendation
        def sortkey(p):
            st = os.stat(p)
            return (version_of(p) == '(none)', -st.st_size, -st.st_mtime)
        keep = max(paths, key=sortkey)
        print(f"  -> KEEP {keep}")
        print()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        scan(sys.argv[1])
    else:
        for p in sorted(glob.glob(os.path.expanduser('~/.hermes/profiles/*/'))):
            name = os.path.basename(p.rstrip('/'))
            if not os.path.isdir(os.path.join(p, 'skills')):
                continue
            print(f"=== {name} ===")
            scan(p)
