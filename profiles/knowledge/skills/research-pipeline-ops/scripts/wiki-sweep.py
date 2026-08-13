#!/usr/bin/env python3
"""Full llm-wiki sweep — frontmatter, wikilinks, ghosts, orphans, index, size, raw, log.

Usage: python3 wiki-sweep.py [wiki_root]
Defaults to $WIKI_PATH, else /Users/noctis/Hermes Vault/Hermes/llm-wiki.

Audits all knowledge dirs (concepts/entities/comparisons/alloys/queries + solar/);
operational/ pages are reported informationally. Prints a sectioned plain-text
report to stdout. Read-only — never writes the wiki.

Companion to research-pipeline-ops SKILL.md. Cron-drift cross-check is manual:
compare `cronjob list` against operational/protocols/research-pipeline-categories.md
(retired crons may still fire; new categories may lack crons entirely).
"""
import os, re, sys, glob, datetime, collections

WIKI = (sys.argv[1] if len(sys.argv) > 1
        else os.environ.get("WIKI_PATH", "/Users/noctis/Hermes Vault/Hermes/llm-wiki"))
KNOWLEDGE = ["concepts", "entities", "comparisons", "alloys", "queries", "solar"]
TYPE_MAP = {"concepts": "concept", "entities": "entity", "comparisons": "comparison",
            "alloys": "alloy", "queries": "query"}
WF_ALLOWED = {"seedling", "developing", "stable", "needs-review", "stale"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def load_taxonomy():
    """Workflow states + topic tags from SCHEMA.md's Tag Taxonomy section."""
    schema = open(os.path.join(WIKI, "SCHEMA.md"), encoding="utf-8").read()
    tags = set("workflow:" + w for w in WF_ALLOWED)
    in_tax = False
    for line in schema.splitlines():
        if line.startswith("## Tag Taxonomy"):
            in_tax = True
            continue
        if in_tax and line.startswith("## "):
            break
        if in_tax:
            m = re.match(r"^[-*] `([^`]+)`", line)
            if m:
                tags.add(m.group(1).strip())
    return tags


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fields = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            k, _, v = line.partition(":")
            fields[k.strip()] = v.strip().strip('"').strip("'")
        elif line.startswith("  - "):
            fields["sources"] = fields.get("sources", "") + " " + line.strip()[2:]
    return fields


def split_tags(field):
    """Bracket/comma split — keeps 'workflow:seedling' as ONE token and
    preserves leading-digit tags like '3d-modeling'. Naive [a-z...] regex
    splits the colon and mangles digits (see SKILL.md pitfalls)."""
    raw = (field or "").strip("[]").replace('"', "").replace("'", "")
    return [t.strip() for t in raw.split(",") if t.strip()]


def slugify(name):
    name = name.split("|")[0].split("#")[0].strip()
    if "/" in name:
        name = name.split("/")[-1]
    return name


pages, op_pages = [], []
for d in KNOWLEDGE:
    base = os.path.join(WIKI, d)
    if not os.path.isdir(base):
        continue
    for fn in sorted(os.listdir(base)):
        if not fn.endswith(".md"):
            continue
        p = os.path.join(d, fn)
        text = open(os.path.join(WIKI, p), encoding="utf-8").read()
        pages.append({"path": p, "slug": fn[:-3], "dir": d, "fm": parse_frontmatter(text),
                      "body": text.split("\n---", 1)[1] if text.startswith("---") else text,
                      "text": text, "mtime": os.path.getmtime(os.path.join(WIKI, p))})
for root, dirs, files in os.walk(os.path.join(WIKI, "operational")):
    for fn in sorted(files):
        if fn.endswith(".md"):
            full = os.path.join(root, fn)
            text = open(full, encoding="utf-8").read()
            op_pages.append({"path": os.path.relpath(full, WIKI), "slug": fn[:-3],
                             "fm": parse_frontmatter(text)})

index_text = open(os.path.join(WIKI, "index.md"), encoding="utf-8").read()
log_text = open(os.path.join(WIKI, "log.md"), encoding="utf-8").read()
TAX = load_taxonomy()
existing = {p["slug"] for p in pages} | {p["slug"] for p in op_pages}

# ---- 1. Frontmatter ----
print("=" * 70); print("1. FRONTMATTER AUDIT (%d knowledge pages)" % len(pages)); print("=" * 70)
fm_issues, style = [], collections.Counter()
for p in pages:
    path, d, fm = p["path"], p["dir"], p["fm"]
    if fm is None:
        fm_issues.append(f"{path}: NO FRONTMATTER"); style["none"] += 1; continue
    for req in ["title", "created", "updated", "type", "tags", "sources"]:
        if req not in fm or not fm[req]:
            fm_issues.append(f"{path}: missing field '{req}'")
    if fm.get("type") and TYPE_MAP.get(d) and fm["type"] != TYPE_MAP.get(d):
        # Ruling 2026-08-10: 'summary' is valid for pages in concepts/ (research-report summaries)
        if not (d == "concepts" and fm["type"] == "summary"):
            fm_issues.append(f"{path}: type '{fm['type']}' != dir '{TYPE_MAP.get(d)}'")
    for k in ("created", "updated"):
        if fm.get(k) and not DATE_RE.match(fm[k]):
            fm_issues.append(f"{path}: {k} not ISO date '{fm[k]}'")
    tags = split_tags(fm.get("tags"))
    wf_in_tags = [t for t in tags if t.startswith("workflow:")]
    wf_key = fm.get("workflow")
    if wf_key in WF_ALLOWED:
        style["key-only"] += 1
    elif wf_in_tags:
        style["tag-style"] += 1
    elif wf_key or wf_in_tags:
        bad = wf_key or wf_in_tags[0]
        fm_issues.append(f"{path}: invalid workflow value '{bad}' (allowed: {sorted(WF_ALLOWED)})")
        style["invalid"] += 1
    else:
        fm_issues.append(f"{path}: NO workflow (neither 'workflow:' key nor workflow:xxx in tags)")
        style["neither"] += 1
    unknown = [t for t in tags if t not in TAX]
    if unknown:
        fm_issues.append(f"{path}: tags not in taxonomy: {unknown}")
    if fm.get("confidence") and fm["confidence"] not in ("high", "medium", "low"):
        fm_issues.append(f"{path}: bad confidence '{fm['confidence']}'")
    if fm.get("contested") == "true" and "contradictions" not in fm:
        fm_issues.append(f"{path}: contested=true but no contradictions field")
print("  workflow style split:", dict(style))
if fm_issues:
    for i in fm_issues:
        print("  ISSUE:", i)
else:
    print("  OK - all knowledge pages pass")
missing_op = [p["path"] for p in op_pages
              if p["fm"] is None or any(r not in p["fm"] for r in ["title", "type", "created", "updated"])]
print(f"  operational: {len(op_pages)} pages" + (f" — ISSUES: {missing_op}" if missing_op else " — ok"))
print()

# ---- 2. Wikilinks + ghosts ----
print("=" * 70); print("2. WIKILINKS (knowledge + operational)"); print("=" * 70)
outbound = collections.defaultdict(set); backlinks = collections.defaultdict(set)
for p in pages + op_pages:
    if p["fm"] is None:
        continue
    for l in LINK_RE.findall(p["body"]):
        target = slugify(l)
        if target:
            outbound[p["path"]].add(target)
            backlinks[target].add(p["path"])
index_links = {slugify(l) for l in LINK_RE.findall(index_text)}
ghost = collections.Counter({t: len(s) for t, s in backlinks.items() if t not in existing})
print(f"  outbound links: {sum(len(v) for v in outbound.values())}, distinct targets: {len(set().union(*outbound.values()) or set())}")
print(f"  ghost notes: {len(ghost)}")
for target, n in ghost.most_common():
    print(f"    {target}: {n}" + ("   <-- PROMOTE (3+)" if n >= 3 else ""))
stale = [t for t, n in ghost.items() if n == 0]
print("  stale ghosts (zero backlinks):", ", ".join(stale) if stale else "none")
print()

# ---- 3. Orphans ----
print("=" * 70); print("3. ORPHANS (no inbound links)"); print("=" * 70)
orphans = []
for p in pages:
    inbound = len(backlinks.get(p["slug"], set()))
    if inbound + (1 if p["slug"] in index_links else 0) == 0:
        orphans.append(p["path"])
    elif inbound == 0:
        orphans.append(p["path"] + " [index-only]")
print("\n".join("  " + o for o in orphans) if orphans else "  none")
print()

# ---- 4. Index completeness ----
print("=" * 70); print("4. INDEX COMPLETENESS"); print("=" * 70)
not_idx = [p["path"] for p in pages
           if p["slug"] not in index_text and (p["fm"] or {}).get("title", "") not in index_text]
idx_missing_pages = sorted(set(index_links) - existing)
print("\n".join("  NOT IN INDEX: " + x for x in not_idx) if not_idx else "  all knowledge pages in index.md")
print("\n".join("  INDEX LINK -> MISSING PAGE: " + x for x in idx_missing_pages) if idx_missing_pages
      else "  all index links resolve")
print()

# ---- 5. Outbound minimum ----
print("=" * 70); print("5. OUTBOUND MINIMUM (>=2 per page)"); print("=" * 70)
under = [p["path"] for p in pages if len(outbound.get(p["path"], set())) < 2]
print("\n".join(f"  {u} -> {sorted(outbound.get(u, set()))}" for u in under) if under else "  all pages >=2 links")
print()

# ---- 6. Oversized ----
print("=" * 70); print("6. OVERSIZED PAGES (>200 lines per SCHEMA)"); print("=" * 70)
big = sorted(((p["path"], p["text"].count("\n") + 1) for p in pages if p["text"].count("\n") + 1 > 200),
             key=lambda x: -x[1])
print("\n".join(f"  {x[0]}: {x[1]} lines" for x in big) if big else "  none")
print()

# ---- 7. Raw immutability ----
print("=" * 70); print("7. RAW/ MTIME (last 3 days — ingest writes expected)"); print("=" * 70)
now = datetime.datetime.now(); recent = []
for root, dirs, files in os.walk(os.path.join(WIKI, "raw")):
    for fn in files:
        if fn.endswith(".md"):
            full = os.path.join(root, fn)
            mt = datetime.datetime.fromtimestamp(os.path.getmtime(full))
            if (now - mt).days <= 3:
                recent.append((os.path.relpath(full, WIKI), mt.strftime("%Y-%m-%d %H:%M")))
print("\n".join(f"  {m} {p}" for p, m in sorted(recent, key=lambda x: x[1], reverse=True)) if recent
      else "  no raw files modified in last 3 days")
print()

# ---- 8. Log rotation ----
entries = [l for l in log_text.splitlines() if l.startswith("## ")]
print(f"8. LOG ENTRIES: {len(entries)} (rotate at 500)")
