# Vault Maintenance

## Duplicate Detection via YAML Frontmatter

When a vault has structured YAML frontmatter with a unique identifier field (e.g., `video_id`, `uid`, `note_id`), find duplicates with Python:

```python
import os, re
from collections import defaultdict

vid_map = defaultdict(list)
for root, dirs, files in os.walk('.'):
    if '.git' in root: continue
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        with open(path) as fh:
            for line in fh:
                m = re.match(r'video_id:\s*"(.+?)"', line.strip())
                if m:
                    vid_map[m.group(1)].append(path)
                    break

for vid, paths in sorted(vid_map.items()):
    if len(paths) > 1:
        print(f'=== {vid} ===')
        for p in paths:
            lines = sum(1 for _ in open(p))
            print(f'  {lines:4d} lines: {p}')
```

Adapt the regex to match whatever unique field the vault uses. Output shows duplicate groups with line counts — the longer file is usually the better one.

## Common Duplicate Patterns

| Pattern | Example | Likely Cause |
|---------|---------|--------------|
| Slug vs Title_Case | `auto-landscape-generator.md` vs `Auto_Landscape_Generator_Full_Title.md` | Two extraction runs with different naming |
| Abbreviated vs Full | `BP_Class_4_Branches_Booleans.md` vs `BP_Class_4_Branches_and_Booleans.md` | Minor naming iteration |
| `aaa-` prefix | `aaa-wooden-fence-creation.md` | Debug/test artifact |

**Rule of thumb:** When two files share the same `video_id`, keep the longer one (more content) and remove the shorter one.

## Vault Migration Workflow

When replacing a loose collection of files with an official repo:

1. Clone the official repo to the target location
2. Identify all loose files that are superseded (scripts, outputs, old copies)
3. List them explicitly and get user confirmation before deleting
4. Leave historical references (e.g., Hermes Vault decisions) intact — they're audit trail, not content
5. After cleanup, run duplicate detection on the surviving vault

## Files That Look Like Duplicates But Aren't

- **Step-by-step guides vs full transcripts** — condensed, actionable versions of the same content are intentional. Keep both.
- **MOC files** — `_MOC_*.md` index files should never be treated as duplicates of the content they link to.
- **Articles vs tutorials** — same topic in different formats (written vs video transcript) is intentional.

## Bulk Deletion + Link Repair Workflow

After removing duplicates, you MUST fix all broken references. Skipping this leaves the vault in a worse state than before — Obsidian graph view shows orphan nodes, prev/next navigation breaks, and MOCs list dead links.

### Step 1: Delete the duplicate files

### Step 2: Update MOC files
Open the `_MOC_*.md` for each affected folder. Remove lines referencing deleted files. Update the `**Files:** N` count to match reality.

### Step 3: Find broken wikilinks across the vault
Use Python to scan all `.md` files for `[[...]]` links that point to deleted filenames:

```python
import os, re
deleted_names = ['Deleted_File_1', 'Deleted_File_2']  # fill in
broken = []
for root, dirs, files in os.walk('.'):
    if '.git' in root or '.obsidian' in root: continue
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        with open(path) as fh:
            content = fh.read()
        for m in re.finditer(r'\[\[([^\]|]+)', content):
            link = m.group(1)
            for d in deleted_names:
                if d in link:
                    broken.append(f'{path}: [[{link}]]')
```

### Step 4: Fix prev/next chains
Most tutorial files have `## Related` sections with `← Previous` and `→ Next` wikilinks. When a file in the chain is deleted, update the link to point to the surviving version (the one you kept).

### Step 5: Update README file counts
The README typically has tables with file counts per folder. Re-count each folder and patch the README to match.

### Step 6: Verify zero new broken links
Run the broken-link scanner again. Confirm that all remaining broken links are pre-existing (from earlier removals), not from your current cleanup. Report pre-existing broken links to the user as a separate finding.
