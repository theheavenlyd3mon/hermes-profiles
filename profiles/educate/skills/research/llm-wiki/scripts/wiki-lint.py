#!/usr/bin/env python3
"""
Wiki Lint — comprehensive health check for Karpathy-pattern LLM wikis.

Usage:
    python3 wiki-lint.py <wiki_path> [--sibling <other_wiki_path>]

Scans:
  • Orphaned pages (no inbound [[wikilinks]] from other content pages)
  • Broken wikilinks (links to nonexistent pages, with cross-wiki support)
  • Index completeness (every page in index.md, every index entry on disk)
  • Frontmatter validation (required fields, valid type)
  • Tag audit (tags not in SCHEMA.md taxonomy)
  • Page size (>200 lines candidates for splitting)
  • Stale content (>90 days since update)
  • Quality signals (confidence:low, contested:true, single-source with no confidence)
  • Source drift (SHA256 mismatches — validates stored hash looks real first)
  • Log rotation (lines >500)
  • Outbound wikilink count (minimum 2 per convention)
  • Raw source coverage (every raw article referenced by a content page)

Outputs findings grouped by severity. Zero edits — read-only audit.
"""

import os, re, sys, hashlib, argparse
from collections import defaultdict
from datetime import datetime, timezone, timedelta

NINETY_DAYS = timedelta(days=90)

def read_file_safe(p):
    try:
        with open(p, 'r') as f:
            return f.read()
    except Exception:
        return ""

def extract_frontmatter(content):
    fm = {}
    if not content.startswith('---'):
        return fm
    end = content.find('---', 3)
    if end == -1:
        return fm
    block = content[3:end].strip()
    for line in block.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            # Skip multi-colon lines that aren't list fields
            if line.count(':') > 1 and not any(line.startswith(k) for k in ['tags', 'sources', 'contradictions']):
                continue
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip()
            if val.startswith('[') and val.endswith(']'):
                val = [v.strip().strip("'\"") for v in val[1:-1].split(',') if v.strip()]
            fm[key] = val
    return fm

def extract_wikilinks(content, normalize=True):
    body = content
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            body = content[end+3:]
    links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', body)
    if normalize:
        return [l.strip().lower() for l in links]
    return [l.strip() for l in links]

def list_wiki_pages(base_dir, subdirs=None):
    if subdirs is None:
        subdirs = ['entities', 'concepts', 'comparisons', 'queries']
    # Dynamically discover operational/ and alloys/ if they exist — they're
    # valid wiki subdirectories that should be linted, not blind spots.
    all_subdirs = list(subdirs)
    for extra in ['operational', 'alloys']:
        d = os.path.join(base_dir, extra)
        if os.path.isdir(d):
            all_subdirs.append(extra)
    pages = {}
    for subdir in all_subdirs:
        d = os.path.join(base_dir, subdir)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith('.md') and f != 'README.md':
                    full_path = os.path.join(d, f)
                    rel = os.path.join(subdir, f)
                    pages[rel] = full_path
    return pages

def get_filename_slug(filepath):
    return os.path.splitext(os.path.basename(filepath))[0].lower()

def looks_like_real_sha256(val):
    """Check if a stored sha256 is a real digest vs. a placeholder/fake value."""
    if not val or val.lower() == 'placeholder':
        return False
    if len(val) != 64:
        return False
    # Check for obviously patterned hex values (repeating characters)
    try:
        int(val, 16)
    except ValueError:
        return False
    # Check for repeating patterns that real SHA256 never shows
    pairs = [val[i:i+2] for i in range(0, 64, 2)]
    unique_pairs = len(set(pairs))
    if unique_pairs < 8:  # Real SHA256 has high entropy
        return False
    return True

def lint_wiki(wiki_path, sibling_paths=None):
    print(f"WIKI: {wiki_path}")
    print()

    pages = list_wiki_pages(wiki_path)
    print(f"Content pages: {len(pages)}")
    print()

    page_content = {}
    for rel_path, full_path in pages.items():
        page_content[rel_path] = read_file_safe(full_path)

    schema_content = read_file_safe(os.path.join(wiki_path, 'SCHEMA.md'))
    index_content = read_file_safe(os.path.join(wiki_path, 'index.md'))
    log_content = read_file_safe(os.path.join(wiki_path, 'log.md'))

    index_links = extract_wikilinks(index_content)
    index_slugs = set(l.lower() for l in index_links)

    disk_slugs = set()
    for rel_path, full_path in pages.items():
        disk_slugs.add(get_filename_slug(full_path))

    # Build valid target set
    raw_dir = os.path.join(wiki_path, 'raw')
    raw_slugs = set()
    if os.path.isdir(raw_dir):
        for root, dirs, files in os.walk(raw_dir):
            for f in files:
                if f.endswith('.md'):
                    raw_slugs.add(os.path.splitext(f)[0].lower())

    all_known_slugs = set(disk_slugs)
    all_known_slugs.update(raw_slugs)
    all_known_slugs.update(['index', 'schema', 'log'])

    # Add sibling wiki slugs for cross-wiki validation
    cross_wiki_slugs = set()
    if sibling_paths:
        for sp in sibling_paths:
            sibling_pages = list_wiki_pages(sp)
            for rp, fp in sibling_pages.items():
                slug = get_filename_slug(fp)
                cross_wiki_slugs.add(slug)
            all_known_slugs.update(cross_wiki_slugs)

    # Inbound link map
    inbound = defaultdict(set)
    for rel_path, content in page_content.items():
        links = extract_wikilinks(content)
        for link in links:
            inbound[link].add(rel_path)

    # ── 1. Orphans ──
    print("─── ORPHANS ───")
    orphans = []
    for rel_path in sorted(pages.keys()):
        slug = get_filename_slug(pages[rel_path])
        inbound_sources = inbound.get(slug, set())
        if len(inbound_sources) == 0:
            orphans.append(rel_path)
    true_orphans = [p for p in orphans if get_filename_slug(pages[p]) not in index_slugs]
    if true_orphans:
        for p in true_orphans:
            print(f"[ERR] {p} — orphan (no inbound links, not in index)")
    else:
        print("OK — no true orphans")
    print()

    # ── 2. Broken Wikilinks ──
    print("─── BROKEN WIKILINKS ───")
    broken_links = {}
    cross_wiki_links = {}
    for rel_path, content in page_content.items():
        links = extract_wikilinks(content)
        broken = []
        cross = []
        for link in links:
            if link.startswith('http') or '/' in link:
                continue
            if link not in all_known_slugs:
                if link in cross_wiki_slugs:
                    cross.append(link)
                else:
                    broken.append(link)
        if broken:
            broken_links[rel_path] = broken
        if cross:
            cross_wiki_links[rel_path] = cross
    if cross_wiki_links:
        print(f"Cross-wiki references ({sum(len(v) for v in cross_wiki_links.values())} total):")
        for rel_path, links in sorted(cross_wiki_links.items()):
            print(f"  [→] {rel_path}: {links}")
    if broken_links:
        print(f"Truly broken links ({sum(len(v) for v in broken_links.values())} total):")
        for rel_path, links in sorted(broken_links.items()):
            print(f"  [ERR] {rel_path}: {links}")
    else:
        print("OK — no broken wikilinks")
    print()

    # ── 3. Index Completeness ──
    print("─── INDEX COMPLETENESS ───")
    missing_from_idx = disk_slugs - index_slugs
    extra_in_idx = index_slugs - disk_slugs
    if missing_from_idx:
        for slug in sorted(missing_from_idx):
            print(f"[WARN] '{slug}' on disk but not in index.md")
    if extra_in_idx:
        for slug in sorted(extra_in_idx):
            print(f"[WARN] '[[{slug}]]' in index.md but no page file")
    if not missing_from_idx and not extra_in_idx:
        print("OK — index is complete")
    print()

    # ── 4. Page Size ──
    print("─── PAGE SIZE (>200 lines) ───")
    big_pages = [(r, len(page_content[r].split('\n'))) for r in pages if len(page_content[r].split('\n')) > 200]
    if big_pages:
        for p, l in sorted(big_pages):
            print(f"[INFO] {p} — {l} lines")
    else:
        print("OK — no pages exceed 200 lines")
    print()

    # ── 5. Stale Content ──
    print("─── STALE CONTENT (>90 days) ───")
    stale = []
    nodate = []
    for rel_path, content in page_content.items():
        fm = extract_frontmatter(content)
        updated = fm.get('updated', '') or fm.get('created', '')
        if isinstance(updated, list):
            updated = updated[0] if updated else ''
        if updated:
            try:
                pd = datetime.strptime(updated, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                if (datetime.now(timezone.utc) - pd) > NINETY_DAYS:
                    stale.append((rel_path, updated))
            except:
                nodate.append(rel_path)
        else:
            nodate.append(rel_path)
    if stale:
        for p, d in stale:
            print(f"[WARN] {p} — last updated {d}")
    if nodate:
        print(f"[INFO] {len(nodate)} pages have unparseable dates")
    if not stale:
        print("OK — no stale pages")
    print()

    # ── 6. Frontmatter Validation ──
    print("─── FRONTMATTER VALIDATION ───")
    required_fm = ['title', 'created', 'updated', 'type', 'tags', 'sources']
    fm_issues = []
    valid_types = ['entity', 'concept', 'comparison', 'query', 'summary', 'alloy']
    for rel_path, content in page_content.items():
        fm = extract_frontmatter(content)
        missing = [f for f in required_fm if f not in fm]
        if missing:
            fm_issues.append((rel_path, f"missing: {missing}"))
        t = fm.get('type', '')
        if t and t not in valid_types:
            fm_issues.append((rel_path, f"invalid type: '{t}'"))
    if fm_issues:
        for p, issue in fm_issues:
            print(f"[WARN] {p}: {issue}")
    else:
        print("OK — all pages have valid frontmatter")
    print()

    # ── 7. Tag Audit ──
    print("─── TAG AUDIT ───")
    # Taxonomy extracted from SCHEMA.md (simple heuristic)
    tag_lines = re.findall(r'`([a-z0-9][a-z0-9-]+)`', schema_content)
    valid_tags = set(t.strip('`') for t in tag_lines if not t.startswith('type=') and '(' not in t and len(t) > 2)
    if not valid_tags or valid_tags == {'concept'}:  # fallback
        valid_tags = {'model','architecture','training','inference','agent-pattern',
                      'multi-agent','tools','memory','security','deployment','monitoring',
                      'config','research','concept','entity','comparison','prompt-engineering',
                      'workflow','handoff','decision','convention'}
    tag_issues = []
    for rel_path, content in page_content.items():
        fm = extract_frontmatter(content)
        tags = fm.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        if isinstance(tags, list):
            for tag in tags:
                if tag not in valid_tags:
                    tag_issues.append((rel_path, tag))
    if tag_issues:
        print(f"[WARN] {len(tag_issues)} tags not in taxonomy:")
        for p, t in sorted(tag_issues):
            print(f"       {p}: '{t}'")
    else:
        print("OK — all tags in taxonomy")
    print()

    # ── 8. Quality Signals ──
    print("─── QUALITY SIGNALS ───")
    signals = []
    for rel_path, content in page_content.items():
        fm = extract_frontmatter(content)
        conf = fm.get('confidence', '')
        if conf == 'low':
            signals.append((rel_path, 'confidence:low'))
        if fm.get('contested', '') == 'true':
            signals.append((rel_path, 'contested:true'))
        sources = fm.get('sources', [])
        if isinstance(sources, str):
            sources = [sources]
        if isinstance(sources, list) and len(sources) <= 1 and not conf:
            signals.append((rel_path, 'single-source, no confidence'))
    for p, s in signals:
        print(f"[INFO] {p} — {s}")
    if not signals:
        print("OK — no quality flags")
    print()

    # ── 9. Outbound Wikilinks ──
    print("─── OUTBOUND WIKILINKS (min 2) ───")
    few_links = []
    for rel_path, content in page_content.items():
        links = extract_wikilinks(content, normalize=False)
        internal = [l for l in links if not l.lower().startswith('raw/')
                     and l.lower() not in ['index','schema'] and '://' not in l]
        if len(internal) < 2:
            few_links.append((rel_path, len(internal)))
    if few_links:
        for p, n in few_links:
            print(f"[WARN] {p} — {n} outbound wikilinks")
    else:
        print("OK — all pages have 2+ outbound wikilinks")
    print()

    # ── 10. Log Rotation ──
    print("─── LOG ROTATION ───")
    log_lines = len(log_content.split('\n'))
    flag = "NEEDS ROTATION" if log_lines > 500 else "OK"
    print(f"log.md: {log_lines} lines — {flag}")
    print()

    # ── 11. Source Drift (SHA256) ──
    print("─── RAW SOURCE DRIFT ───")
    drift_found = False
    for root, dirs, files in os.walk(raw_dir):
        for f in sorted(files):
            if not f.endswith('.md'):
                continue
            fpath = os.path.join(root, f)
            content = read_file_safe(fpath)
            fm = extract_frontmatter(content)
            stored = fm.get('sha256', '').strip()
            rel = os.path.relpath(fpath, wiki_path)
            if not stored:
                print(f"[INFO] {rel} — no SHA256 stored")
                continue
            if not looks_like_real_sha256(stored):
                print(f"[INFO] {rel} — stored hash looks like placeholder ('{stored[:16]}...'), needs real computation")
                continue
            d_end = content.find('---', 3)
            body = content[d_end+4:] if d_end != -1 else content
            computed = hashlib.sha256(body.encode('utf-8')).hexdigest()
            if computed != stored:
                print(f"[WARN] {rel} — SHA256 mismatch (file modified after ingestion)")
                drift_found = True
            else:
                print(f"[OK]  {rel} — SHA256 verified")
    if not drift_found:
        print("No drift detected where real hashes exist.")
    print()

    # ── 12. Raw Source Coverage ──
    print("─── RAW SOURCE COVERAGE ───")
    all_text = '\n'.join(page_content.values()) + '\n' + schema_content + '\n' + log_content
    uncovered = []
    for root, dirs, files in os.walk(raw_dir):
        for f in sorted(files):
            if not f.endswith('.md'):
                continue
            fpath = os.path.join(root, f)
            slug = f.replace('.md', '')
            rel = os.path.relpath(fpath, wiki_path)
            if slug not in all_text and slug.replace('-', ' ') not in all_text:
                uncovered.append(rel)
    if uncovered:
        for r in uncovered:
            print(f"[INFO] {r} — not referenced by any content page")
    else:
        print("OK — all raw files referenced in content or log")
    print()

    return {
        'pages': len(pages),
        'orphans': len(true_orphans),
        'broken': len(broken_links),
        'cross_wiki': len(cross_wiki_links),
        'index_missing': len(missing_from_idx),
        'index_extra': len(extra_in_idx),
        'big_pages': len(big_pages),
        'stale': len(stale),
        'fm_issues': len(fm_issues),
        'tag_issues': len(tag_issues),
        'signals': len(signals),
        'few_links': len(few_links),
        'log_lines': log_lines,
        'uncovered_raw': len(uncovered),
        'drift_found': drift_found,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Wiki lint health check')
    parser.add_argument('wiki_path', help='Path to the wiki directory')
    parser.add_argument('--sibling', '-s', action='append', help='Sibling wiki path (for cross-wiki link validation)')
    args = parser.parse_args()
    lint_wiki(args.wiki_path, args.sibling)
