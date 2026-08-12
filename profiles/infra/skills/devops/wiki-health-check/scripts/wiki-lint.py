#!/usr/bin/env python3
"""
wiki-lint: Comprehensive 12-point lint for the LLM Wiki.
Checks: orphans, broken links, index completeness, frontmatter, stale content,
quality signals, outbound links, log rotation, source drift, raw coverage, tag audit, page size.

Usage: python3 wiki-lint.py <WIKI_PATH> [--sibling <SIBLING_VAULT_PATH>]
"""

import os, re, json, hashlib, sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WIKI = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('WIKI', '~/wiki')
SIBLING = sys.argv[3] if len(sys.argv) > 3 else None

WIKI = Path(WIKI).expanduser()
if SIBLING:
    SIBLING = Path(SIBLING).expanduser()

def main():
    print(f"WIKI: {WIKI}")
    content_dirs = ['entities', 'concepts', 'comparisons', 'queries', 'alloys']
    
    # Scan content pages
    pages = []
    for d in content_dirs:
        pdir = WIKI / d
        if pdir.exists():
            for f in pdir.glob('*.md'):
                pages.append(f)

    print(f"\nContent pages: {len(pages)}\n")

    # 1. Orphans
    print("─── ORPHANS ───")
    inbound = defaultdict(int)
    for p in pages:
        text = p.read_text()
        # Extract [[wikilinks]]
        links = re.findall(r'\[\[([^\]]+)\]\]', text)
        for link in links:
            slug = link.split('|')[0].strip()
            inbound[slug] += 1

    orphans = [p for p in pages if p.stem not in inbound or inbound[p.stem] == 0]
    if orphans:
        print(f"Found {len(orphans)} orphans:")
        for o in orphans[:10]:
            print(f"  - {o.relative_to(WIKI)}")
        if len(orphans) > 10:
            print(f"  ... and {len(orphans) - 10} more")
    else:
        print("OK — no true orphans")

    # 2. Broken wikilinks
    print("\n─── BROKEN WIKILINKS ───")
    broken = []
    all_slugs = {p.stem for p in pages}
    if SIBLING:
        for d in content_dirs:
            pdir = SIBLING / d
            if pdir.exists():
                for f in pdir.glob('*.md'):
                    all_slugs.add(f.stem)

    for p in pages:
        text = p.read_text()
        links = re.findall(r'\[\[([^\]]+)\]\]', text)
        for link in links:
            slug = link.split('|')[0].strip()
            if slug not in all_slugs:
                broken.append((p, slug))

    if broken:
        print(f"Found {len(broken)} broken links:")
        seen = set()
        for f, slug in broken[:10]:
            key = (f.relative_to(WIKI), slug)
            if key not in seen:
                seen.add(key)
                print(f"  - {key[0]} → [[{key[1]}]]")
        if len(broken) > 10:
            print(f"  ... and {len(broken) - 10} more")
    else:
        print("OK — no broken wikilinks")

    # 3. Index completeness
    print("\n─── INDEX COMPLETENESS ───")
    index_path = WIKI / 'index.md'
    if index_path.exists():
        index_text = index_path.read_text()
        index_slugs = set(re.findall(r'\[\[([^\]]+)\]\]', index_text))
        missing = all_slugs - index_slugs
        if missing:
            print(f"Found {len(missing)} pages missing from index.md:")
            for m in list(missing)[:10]:
                print(f"  - {m}")
            if len(missing) > 10:
                print(f"  ... and {len(missing) - 10} more")
        else:
            print("OK — index is complete")
    else:
        print("WARN — index.md not found")

    # 4. Page size
    print("\n─── PAGE SIZE (>200 lines) ───")
    large = [p for p in pages if len(p.read_text().splitlines()) > 200]
    if large:
        print(f"Found {len(large)} pages >200 lines:")
        for p in large:
            lines = len(p.read_text().splitlines())
            print(f"  [INFO] {p.relative_to(WIKI)} — {lines} lines")
    else:
        print("OK — no pages over 200 lines")

    # 5. Stale content (>90 days)
    print("\n─── STALE CONTENT (>90 days) ───")
    now = datetime.now()
    stale = []
    for p in pages:
        text = p.read_text()
        updated = re.search(r'^updated:\s*([0-9-]+)', text, re.MULTILINE)
        if updated:
            upd = datetime.fromisoformat(updated.group(1))
            if (now - upd).days > 90:
                stale.append((p, (now - upd).days))
    if stale:
        print(f"Found {len(stale)} stale pages:")
        for p, days in stale[:10]:
            print(f"  - {p.relative_to(WIKI)} — {days} days since update")
        if len(stale) > 10:
            print(f"  ... and {len(stale) - 10} more")
    else:
        print("OK — no stale pages")

    # 6. Frontmatter validation
    print("\n─── FRONTMATTER VALIDATION ───")
    required = ['title', 'created', 'updated', 'type', 'tags', 'sources']
    valid_types = ['entity', 'concept', 'comparison', 'alloy', 'query', 'summary']
    bad_frontmatter = []
    for p in pages:
        text = p.read_text()
        match = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
        if not match:
            bad_frontmatter.append((p, "missing frontmatter"))
            continue
        fm_text = match.group(1)
        fm = {}
        for line in fm_text.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                fm[k.strip()] = v.strip()
        for req in required:
            if req not in fm:
                bad_frontmatter.append((p, f"missing {req}"))
                break
        else:
            # Check type is valid
            if 'type' in fm and fm['type'] not in valid_types:
                bad_frontmatter.append((p, f"invalid type: {fm['type']}"))
    if bad_frontmatter:
        print(f"Found {len(bad_frontmatter)} pages with invalid frontmatter:")
        for p, msg in bad_frontmatter[:10]:
            print(f"  - {p.relative_to(WIKI)} — {msg}")
        if len(bad_frontmatter) > 10:
            print(f"  ... and {len(bad_frontmatter) - 10} more")
    else:
        print("OK — all pages have valid frontmatter")

    # 7. Tag audit
    print("\n─── TAG AUDIT ───")
    schema_path = WIKI / 'SCHEMA.md'
    if not schema_path.exists():
        print("WARN — SCHEMA.md not found, cannot validate tags")
    else:
        schema_text = schema_path.read_text()
        # Extract topic tags from schema (simplified)
        tax_match = re.search(r'### Topic Tags\s*(.*?)(?:\n\n|$)', schema_text, re.DOTALL)
        if tax_match:
            tax_section = tax_match.group(1)
            tax_tags = set(re.findall(r'^- (`?[\w:-]+`?)', tax_section, re.MULTILINE))
        else:
            tax_tags = set()

        # Extract all tags in use
        all_tags = set()
        bad_tags = []
        for p in pages:
            text = p.read_text()
            tags_match = re.search(r'^tags:\s*\[(.*?)\]', text, re.MULTILINE)
            if tags_match:
                tag_str = tags_match.group(1)
                tags = [t.strip().strip("'\"") for t in tag_str.split(',')]
                for t in tags:
                    all_tags.add(t)
                    if t not in tax_tags:
                        bad_tags.append((p, t))

        if bad_tags:
            print(f"Found {len(bad_tags)} tags not in taxonomy:")
            seen = set()
            for p, tag in bad_tags[:20]:
                key = (p.relative_to(WIKI), tag)
                if key not in seen:
                    seen.add(key)
                    print(f"  [WARN] {key[0]}: '{key[1]}'")
        else:
            print("OK — all tags in taxonomy")

    # 8. Outbound links (min 2)
    print("\n─── OUTBOUND WIKILINKS (min 2) ───")
    low_links = []
    for p in pages:
        text = p.read_text()
        links = re.findall(r'\[\[([^\]]+)\]\]', text)
        if len(links) < 2:
            low_links.append((p, len(links)))
    if low_links:
        print(f"Found {len(low_links)} pages with <2 outbound links:")
        for p, n in low_links[:10]:
            print(f"  - {p.relative_to(WIKI)} — {n} links")
        if len(low_links) > 10:
            print(f"  ... and {len(low_links) - 10} more")
    else:
        print("OK — all pages have 2+ outbound wikilinks")

    # 9. Log rotation
    print("\n─── LOG ROTATION ───")
    log_path = WIKI / 'log.md'
    if log_path.exists():
        lines = log_path.read_text().splitlines()
        print(f"log.md: {len(lines)} lines — {'OK' if len(lines) <= 500 else 'WARN: exceeds 500'}")

    # 10. Source drift
    print("\n─── RAW SOURCE DRIFT ───")
    raw_path = WIKI / 'raw'
    if raw_path.exists():
        for f in raw_path.glob('**/*.md'):
            text = f.read_text()
            sha_match = re.search(r'^sha256:\s*(\S+)', text, re.MULTILINE)
            if sha_match:
                stored = sha_match.group(1)
                # Check if it's a placeholder
                if stored.startswith('placeholder') or re.match(r'^(.)\1{62}$', stored):
                    print(f"[INFO] {f.relative_to(WIKI)} — stored hash looks like placeholder ('{stored[:20]}...'), needs real computation")
                else:
                    # Compute actual hash of body (after first --- closing delimiter)
                    after_fm = re.split(r'^---\n.*?\n---\n', text, flags=re.DOTALL)
                    if len(after_fm) > 1:
                        body = after_fm[1]
                        actual = hashlib.sha256(body.encode()).hexdigest()
                        if actual != stored:
                            print(f"[WARN] {f.relative_to(WIKI)} — SHA256 mismatch (file modified after ingestion)")
            else:
                print(f"[INFO] {f.relative_to(WIKI)} — no SHA256 stored")

    # 11. Raw source coverage
    print("\n─── RAW SOURCE COVERAGE ───")
    # Check that all raw files are referenced in content or log
    raw_refs = set()
    for p in pages:
        text = p.read_text()
        # Look for ^[raw/...] markers
        refs = re.findall(r'\^\[(raw/[^\]]+)\]', text)
        raw_refs.update(refs)
        # Also check sources: frontmatter
        sources_match = re.search(r'^sources:\s*\[(.*?)\]', text, re.MULTILINE)
        if sources_match:
            for s in sources_match.group(1).split(','):
                raw_refs.add(s.strip().strip("'\""))
    log_refs = set()
    log_path = WIKI / 'log.md'
    if log_path.exists():
        log_text = log_path.read_text()
        log_refs = set(re.findall(r'raw/[\w/]+', log_text))

    raw_files = set()
    for f in (raw_path / 'articles').glob('*.md') if (raw_path / 'articles').exists() else []:
        raw_files.add(f'raw/articles/{f.name}')

    missing_refs = raw_files - raw_refs - log_refs
    if missing_refs:
        print(f"[WARN] {len(missing_refs)} raw files not referenced in content or log:")
        for m in sorted(missing_refs)[:10]:
            print(f"  - {m}")
        if len(missing_refs) > 10:
            print(f"  ... and {len(missing_refs) - 10} more")
    else:
        print("OK — all raw files referenced in content or log")

    print("\n─── Summary ───")
    print("Run complete. Fix issues above and re-run to verify.")

if __name__ == '__main__':
    main()