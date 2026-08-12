#!/usr/bin/env python3
"""Extract name/description/version from every SKILL.md in a repo clone.

Handles folded YAML descriptions (description: >-  with indented continuation
lines), which naive one-line regexes miss. Prints:
    ### name [version]  (relative/path/SKILL.md)
    description (first 400 chars)

Usage:
    python3 extract-skill-frontmatter.py /tmp/<repo> [--exclude agent-council] [--skip-bundles-nested]
"""
import os, re, sys, glob

def frontmatter(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    m = re.match(r'^---\n(.*?)\n---', txt, re.S)
    if not m:
        return {}
    fm, cur, folded = {}, None, None
    for line in m.group(1).splitlines():
        mm = re.match(r'^(\w+):\s*(.*)$', line)
        if mm:
            k, v = mm.group(1), mm.group(2).strip()
            fm[k] = v
            if k == 'description':
                if v in ('>-', '|-', '>', '|'):
                    folded, cur = v, ''
                else:
                    cur = v
        elif folded is not None:
            cur += ' ' + line.strip()
    if folded is not None:
        fm['description'] = ' '.join(cur.split())
    return fm

def main():
    args = sys.argv[1:]
    root = args[0] if args else '.'
    excludes = []
    if '--exclude' in args:
        excludes = args[args.index('--exclude') + 1].split(',')
    skip_nested_bundles = '--skip-bundles-nested' in args

    out = []
    for f in sorted(glob.glob(os.path.join(root, '**', 'SKILL.md'), recursive=True)):
        rel = os.path.relpath(f, root)
        if any(x in rel for x in excludes):
            continue
        if skip_nested_bundles and '/bundles/' in rel and rel.count('/') > 1:
            continue
        fm = frontmatter(f)
        name = fm.get('name', os.path.basename(os.path.dirname(f)))
        desc = ' '.join(fm.get('description', '').split())
        ver = fm.get('version', '')
        out.append((name, ver, rel, desc[:400]))

    for name, ver, rel, desc in out:
        print(f"### {name} [{ver}]  ({rel})")
        print(desc)
        print()
    print(f"TOTAL: {len(out)}")

if __name__ == '__main__':
    main()
