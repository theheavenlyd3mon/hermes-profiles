# Content-revamp audit recipe (Obsidian / large markdown vaults)

Run via `execute_code` (Python stdlib only). Adjust `VAULT` to the vault root.
This is the read-only scan that feeds the "audit-before-create" curation draft — it
must complete and be presented to the user BEFORE any kanban card is created.

```python
import os, re
from collections import defaultdict, Counter

VAULT = os.environ.get("VAULT") or os.path.expanduser("~/Documents/Unreal-Engine-Obsidian")
# Replace with the user-confirmed vault root for this session.
# If VAULT isn't set, choose the user's likely root or ask before scanning.
SKIP = {'.git', '.obsidian'}

# Read all .md files once and classify per-file below.

stale_token = re.compile(r'\b5\.(?:4|5|6|7)\b')
marker = re.compile(r'UNVERIFIED|\[UNVERIFIED|TODO|FIXME|placeholder|lorem ipsum', re.I)

cat_files = defaultdict(list)
cat_stale = defaultdict(list)
unverified, misplaced = [], set()
readme_locs = []

for root, dirs, files in os.walk(VAULT):
    dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith('.')]
    for f in files:
        if not f.endswith('.md'):
            continue
        rel = os.path.relpath(os.path.join(root, f), VAULT)
        top = rel.split('/')[0]
        cat_files[top].append(rel)
        if f == 'README.md':
            readme_locs.append(rel)
        if top in ('Hermes', 'templates'):
            misplaced.add(top)
        try:
            txt = open(os.path.join(VAULT, rel), 'r', encoding='utf-8', errors='ignore').read(30000)
        except Exception:
            continue
        if stale_token.search(txt):
            ctx = [f"L{i}: {ln.strip()[:90]}" for i, ln in enumerate(txt.splitlines()[:120], 1) if stale_token.search(ln)][:2]
            cat_stale[top].append((rel, len(stale_token.findall(txt)), ctx))
        if marker.search(txt):
            unverified.append(rel)

# 1) per-category counts + stale map
for top in sorted(cat_stale, key=lambda k: -len(cat_stale[k])):
    print(f"### {top}  ({len(cat_stale[top])} stale of {len(cat_files[top])} files)")
    for rel, n, ctx in cat_stale[top][:8]:
        print(f"  [{n:>2}] {rel}")
        for c in ctx: print(f"        {c}")

# 2) duplicate basenames (overlap candidates)
bases = Counter(os.path.basename(f) for files in cat_files.values() for f in files)
print("DUPLICATE BASENAMES:", {b: c for b, c in bases.items() if c > 1})

# 3) misplaced tooling
print("MISPLACED TOOLING FOLDERS:", misplaced)

# 4) unverified markers
print(f"UNVERIFIED/TODO FILES ({len(unverified)}):", unverified)

# 5) smallest categories (stub / merge candidates)
print("SMALL CATEGORIES:", sorted(cat_files.items(), key=lambda x: len(x[1]))[:8])
```

## Reading the output
- **`cat_stale`** = the real revamp surface. High counts (e.g. PCG, OW-RPG) drive the bulk of the work.
- **Duplicate basenames** at filename level are usually fine (one README per category); real overlap is *content* (same subsystem covered by 2-3 notes) — flag those from the review, not the scan.
- **`ue_version:` frontmatter** is the field to reconcile to the target version; body prose mentioning older versions may stay if historically accurate.
- Present all of this as a curation draft with keep/merge/drop/relocate per suspect item, then gate on `clarify` before creating cards.

## Annotation scheme + legacy quarantine (the "don't guess" refinement)

When the constraint is "all references must be version X, and anything not-in-X or
deprecated gets its own category so we can tell what's 5.7 / 5.8 / etc":

1. **Every revamped note carries frontmatter** so the vault reads version-status at a glance:
   ```yaml
   ue_version: "5.8"
   status: current | legacy | deprecated
   verified: source-checked | tutorial-derived | unverified
   historical_notes:
     - "Deprecated in UE 5.5: InstancedPerExecution removed"   # true history, KEEP — do not rewrite as current
   ```
   - `current` = valid in X after applying migration notes.
   - `legacy` = valid facts but bound to an earlier version; do not present as current workflow.
   - `deprecated` = removed/superseded — historical-only. Unsourced claims → `verified: unverified`, never into the vault as fact.

2. **Quarantine deprecated / not-in-X / legacy into a dedicated sibling category** (e.g.
   `Legacy_5.7_and_Earlier/` parallel to topic categories) rather than leaving stale notes
   scattered. Relocate (don't delete) kits/contrib to preserve provenance. A version-pinned
   folder gets an **alias note**, never a rename (rename breaks `[[wikilinks]]`).

3. **Split research so the deprecated list is sourced, not guessed.** Build:
   - `T0` curation report (`knowledge`, read-only) — classify + propose structure. USER GATE.
   - `T1a` deep research (`research`) — close brief gaps + produce the explicit
     DEPRECATED/NOT-IN-X list with migration paths, every claim carrying a primary source URL;
     unsourced → `[UNVERIFIED]`, excluded from confirmed lists.
   - `T1b` consolidate (`knowledge`, parent T1a) — one canonical standard doc (the
     DEPRECATED section + the frontmatter template) every per-category task cites.
   - Then per-category wave, parented to T1b.

   Confirmed this session (UE 5.8): **UE_LOG is NOT deprecated in 5.8** (Epic: "will
   eventually be deprecated"; ships `ConvertUELog.py`) — keep it, flag as future-migration.
   Mass scheduler rewrite, Incremental Cooking + ZenServer default store, iOS SM6 via Metal
   converter, Game Input redist — all confirmed against primary Epic sources.
