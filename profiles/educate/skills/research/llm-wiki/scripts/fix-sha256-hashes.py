#!/usr/bin/env python3
"""
Fix placeholder SHA256 hashes in wiki raw sources.

Companion to wiki-lint.py — run after lint detects placeholder hashes.
Recovers real SHA256 digests for raw files that have placeholder values
(e.g., 'placeholder', '<placeholder>', 'computed-at-ingest...') and
rewrites the frontmatter with the actual hash.

Usage:
    python3 fix-sha256-hashes.py <wiki_path> [--dry-run]

Options:
    --dry-run   Show what would be fixed without modifying files
"""

import os, re, hashlib, argparse


def looks_like_real_sha256(val):
    """Check if a stored sha256 is a real digest vs. a placeholder/fake value."""
    if not val or val.lower() == 'placeholder':
        return False
    if val.startswith('<') or val.startswith('computed'):
        return False
    if len(val) != 64:
        return False
    try:
        int(val, 16)
    except ValueError:
        return False
    pairs = [val[i:i+2] for i in range(0, 64, 2)]
    if len(set(pairs)) < 8:
        return False
    return True


def extract_body(content):
    """Extract body content after frontmatter."""
    if not content.startswith('---'):
        return content
    end = content.find('---', 3)
    if end == -1:
        return content
    return content[end+4:]


def fix_hashes(wiki_path, dry_run=False):
    raw_dir = os.path.join(wiki_path, 'raw')
    if not os.path.isdir(raw_dir):
        print(f"ERROR: {raw_dir} does not exist")
        return 0

    fixed = 0
    skipped = 0

    for root, dirs, files in os.walk(raw_dir):
        for f in sorted(files):
            if not f.endswith('.md'):
                continue
            fpath = os.path.join(root, f)
            with open(fpath, 'r') as fh:
                content = fh.read()

            if not content.startswith('---'):
                continue
            end = content.find('---', 3)
            if end == -1:
                continue

            fm_block = content[3:end].strip()
            body = content[end+4:]

            # Find sha256 line
            sha_line = None
            for line in fm_block.split('\n'):
                if line.strip().startswith('sha256:'):
                    sha_line = line
                    break

            if not sha_line:
                continue

            stored = sha_line.split(':', 1)[1].strip().strip("'\"")

            if looks_like_real_sha256(stored):
                skipped += 1
                continue

            # Compute real hash
            computed = hashlib.sha256(body.encode('utf-8')).hexdigest()
            rel = os.path.relpath(fpath, wiki_path)

            if dry_run:
                print(f"  [DRY] {rel}: '{stored[:20]}...' -> {computed[:16]}...")
            else:
                new_content = content.replace(sha_line, f'sha256: {computed}')
                with open(fpath, 'w') as fh:
                    fh.write(new_content)
                print(f"  [FIXED] {rel}: '{stored[:20]}...' -> {computed[:16]}...")
            fixed += 1

    print(f"\n{'Would fix' if dry_run else 'Fixed'}: {fixed} | Already valid: {skipped}")
    return fixed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fix placeholder SHA256 hashes in wiki raw sources')
    parser.add_argument('wiki_path', help='Path to the wiki directory')
    parser.add_argument('--dry-run', action='store_true', help='Show fixes without applying')
    args = parser.parse_args()
    fix_hashes(args.wiki_path, args.dry_run)
