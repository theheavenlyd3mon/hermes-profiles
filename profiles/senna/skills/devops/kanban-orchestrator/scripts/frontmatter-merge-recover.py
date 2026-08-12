#!/usr/bin/env python3
"""frontmatter-merge-recover.py — rebuild frontmatter by MERGING canonical fields
onto git-HEAD originals, after a bulk revamp worker REPLACED (not merged) frontmatter
and wiped source URLs / title / metadata.

Usage:  python3 frontmatter-merge-recover.py <vault-path>
  - Scans all files changed vs HEAD (staged + unstaged, tracked).
  - For each, parses CURRENT frontmatter + git HEAD frontmatter.
  - Writes a merged frontmatter = canonical fields (ue_version/status/category/source/
    revamped_at/deprecated_symbols/migration_hint/historical_notes) applied on top of
    originals, plus any other original fields (title/type/tags/video_id/series/episode...).
  - Restores original `source` when the current value is empty ("").
  - Body is taken from the CURRENT file (preserves intended version retitles etc).
  - Files relocated/missing on disk are skipped.
  - Untracked-at-HEAD files (new governance notes) are left untouched.

Idempotent: safe to re-run. Body is never modified.
"""
import subprocess, re, os, sys

CANON = ['ue_version', 'status', 'category', 'source', 'revamped_at',
         'deprecated_symbols', 'migration_hint', 'historical_notes']
DEFAULTS = {'ue_version': '"5.8"', 'status': 'current', 'category': 'tutorials',
            'source': '""', 'revamped_at': '2026-07-08', 'deprecated_symbols': '[]',
            'migration_hint': '""', 'historical_notes': '[]'}


def git_show_head(vault, path):
    try:
        return subprocess.run(['git', 'show', f'HEAD:{path}'], cwd=vault,
                              capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None


def parse_fm(text):
    """Return (pairs[(key,raw_line)|(None,raw_line)], body_after_second_dash)."""
    if not text.startswith('---'):
        return [], text
    lines = text.split('\n')
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        return [], text
    body = '\n'.join(lines[end + 1:])
    pairs = []
    for ln in lines[1:end]:
        m = re.match(r'^([A-Za-z_][\w-]*):\s?(.*)$', ln)
        pairs.append((m.group(1), ln) if m else (None, ln))
    return pairs, body


def main():
    vault = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    staged = subprocess.run(['git', 'diff', '--cached', '--name-only'], cwd=vault,
                            capture_output=True, text=True).stdout.split()
    unstaged = subprocess.run(['git', 'diff', '--name-only'], cwd=vault,
                              capture_output=True, text=True).stdout.split()
    out = list(dict.fromkeys(staged + unstaged))
    fixed = 0
    for path in out:
        if not path.endswith('.md'):
            continue
        full = os.path.join(vault, path)
        if not os.path.exists(full):
            continue  # relocated / missing on disk
        head_txt = git_show_head(vault, path)
        with open(full) as f:
            cur = f.read()
        cur_pairs, cur_body = parse_fm(cur)
        head_pairs, _ = parse_fm(head_txt) if head_txt else ([], '')
        C = {k: v for k, v in cur_pairs if k}
        O = {k: v for k, v in head_pairs if k}
        out_pairs = []
        seen = set()
        for k in CANON:
            if k in C:
                raw = C[k]
                if k == 'source' and re.match(r'source:\s*""', raw) and k in O:
                    raw = O[k]  # restore original URL
                out_pairs.append((k, raw))
                seen.add(k)
            elif k in O:
                out_pairs.append((k, O[k]))
                seen.add(k)
            else:
                out_pairs.append((k, f'{k}: {DEFAULTS[k]}'))
                seen.add(k)
        for k, raw in head_pairs:
            if k and k not in seen:
                out_pairs.append((k, raw))
                seen.add(k)
        for k, raw in cur_pairs:
            if k and k not in seen:
                out_pairs.append((k, raw))
                seen.add(k)
        new_fm = '---\n' + '\n'.join(raw for _, raw in out_pairs) + '\n---\n'
        with open(full, 'w') as f:
            f.write(new_fm + cur_body)
        fixed += 1
    print(f"Recovered {fixed} files. New/untracked/relocated files left as-is.")


if __name__ == '__main__':
    main()
