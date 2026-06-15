---
name: file-organization
description: "Organize messy directories — deduplicate files, normalize naming, clean junk, restructure folders. Use when the user says 'clean up', 'organize', 'deduplicate', or 'restructure' a folder of files."
triggers:
  - "organize files"
  - "clean up folder"
  - "deduplicate files"
  - "rename files consistently"
  - "restructure directory"
  - "find duplicates"
tags: [files, organization, dedup, cleanup, rename, productivity]
---

# File Organization & Deduplication

## When to Use
User has a messy directory with duplicate files, inconsistent naming, junk files (.DS_Store, .checkpoint.json), or scattered content that needs consolidation. Common after batch extraction runs, multi-session work, or inheriting someone else's file structure.

## Workflow

### Phase 1 — Survey the Damage

```python
from hermes_tools import terminal, read_file

base = "/path/to/target"

# Directory tree
r = terminal(f"find '{base}' -type d | sort")

# File counts per directory
r = terminal(f"find '{base}' -type f -name '*.md' -exec dirname {{}} \\; | sort | uniq -c | sort -rn")

# Find junk files
r = terminal(f"find '{base}' -name '.DS_Store' -o -name '.checkpoint.json' -o -name 'None.md'")
```

### Phase 2 — Find Duplicates

Two strategies, use both:

**A. Filename-based grouping** (fast, catches obvious dupes):
```python
import re

def normalize(name):
    """Aggressive normalization: strip stop words, punctuation, case."""
    n = name.lower().replace(".md", "")
    n = re.sub(r'[^a-z0-9\s]', ' ', n)
    words = n.split()
    stop = {'a', 'an', 'the', 'in', 'on', 'of', 'to', 'for', 'and', 'or', 'by', 'with', 'from', 'over', 'using'}
    words = [w for w in words if w not in stop and len(w) > 1]
    return ''.join(words)

groups = {}
for f in files:
    key = normalize(f)
    if key not in groups:
        groups[key] = []
    groups[key].append(f)

# Groups with >1 file are duplicate candidates
for key, group in groups.items():
    if len(group) > 1:
        # Compare sizes — keep largest
        sizes = [(f, os.path.getsize(os.path.join(path, f))) for f in group]
        sizes.sort(key=lambda x: x[1], reverse=True)
        best = sizes[0][0]
        # Move others to _duplicates/
```

**B. Episode/topic-number extraction** (for tutorial series):
```python
# Extract episode numbers from various naming patterns
m = re.search(r'#(\d+)', filename)     # #12, #80
m = re.search(r'^(\d+)[_-]', filename) # 12_, 60-
m = re.search(r'rpg-(\d+)', filename)  # ue5-rpg-80
m = re.search(r'Part[_\s]+(\d+)', filename) # Part_1, Part 16
m = re.search(r'ue5-starter-(\d+)', filename) # ue5-starter-01
```

### Phase 3 — Deduplicate

1. Create `_duplicates/` folder at the root
2. For each duplicate group, compare file sizes
3. Keep the largest (most content) or the one with the cleanest name
4. Move duplicates to `_duplicates/` — NEVER delete immediately
5. For mixed naming (long-name + short-name), keep whichever is larger

### Phase 4 — Normalize Names

Consistent pattern: `XX_Topic_Name.md` (episode prefix + underscore-separated title).

```python
import os, re

renames = {}
for f in files:
    new = f
    # Remove long prefixes
    new = re.sub(r'^Unreal_Engine_5_RPG_Tutorial_Series_-_#(\d+)_', r'\1_', new)
    # Remove special chars
    new = new.replace('!', '').replace(',', '').replace('#', '').replace('&', 'and')
    # Collapse underscores
    new = re.sub(r'_+', '_', new).strip('_')
    # Capitalize first letter of each segment
    if new != f:
        renames[f] = new

# Use os.rename for files with special chars (#, !, &, etc.)
# Shell mv commands fail on these — Python os.rename handles them natively
for old, new in renames.items():
    os.rename(os.path.join(path, old), os.path.join(path, new))
```

### Phase 5 — Clean Junk

```python
# Python approach — safest, avoids rtk find limitations and protects holding folders
import os

for root, dirs, files in os.walk(base):
    # Skip _duplicates/ and _non_educational/
    if '_duplicates' in root or '_non_educational' in root:
        continue
    for f in files:
        if f in ['.DS_Store', '.checkpoint.json', 'None.md']:
            os.remove(os.path.join(root, f))
```

**⚠️ Never run `find -delete` or `xargs rm` against the extraction root** — it can nuke `_duplicates/` and `_non_educational/` contents. Scope cleanup to specific directories or use Python with explicit path checks.

### Phase 6 — Verify

```python
# Final counts
for dirname in os.listdir(base):
    path = os.path.join(base, dirname)
    if os.path.isdir(path) and '_duplicates' not in path:
        count = len([f for f in os.listdir(path) if f.endswith('.md')])
        print(f"  {dirname}: {count} files")

# Count _duplicates
dupe_count = sum(1 for root, _, files in os.walk(f"{base}/_duplicates") for f in files if f.endswith('.md'))
print(f"  _duplicates: {dupe_count} files (safe to delete later)")
```

## Three-Folder Separation

When cleaning up content directories, separate three distinct categories:

1. **Active content** (keep in place) — files that are useful, educational, or functional
2. **`_duplicates/`** — same-content copies detected by size/name comparison. Safe to delete after user confirms.
3. **`_non_educational/`** — files that are unique but lack value (YouTube descriptions, chapter lists, promo text, conceptual overviews). User reviews and decides.

```
Target_Directory/
├── Folder_A/                # Active content only
├── Folder_B/
├── _non_educational/        # Unique but low-value (user reviews)
│   ├── Folder_A/
│   └── Folder_B/
└── _duplicates/             # Same-content copies (delete later)
    ├── Folder_A/
    └── Folder_B/
```

Move files with `shutil.move()`, preserving subfolder structure. Never auto-delete from either holding folder.

## Phase 7 — Obsidian Vault Preparation (Optional)

After organizing, if the user wants the directory as an Obsidian vault, add:

1. **Consistent frontmatter** to all files (title, source, type, series, episode, tags)
2. **Wikilinks** in a `## Related` section (previous/next episode, series MOC)
3. **MOC index files** per folder (`_MOC_FolderName.md` linking to all files)
4. **Verification** — 100% frontmatter, 99%+ wikilinks, all folders have MOC

For the full Obsidian preparation workflow with scripts, see the `youtube-batch-extraction` skill's `references/obsidian-vault-preparation.md`.

## Pitfalls

- **Shell `mv` fails on special characters.** Filenames with `#`, `!`, `&`, `,` break shell commands. Use Python `os.rename()` directly — it handles all characters natively. Write the rename loop in `execute_code` without calling `terminal()` for the actual move.
- **Normalization can false-match.** Overly aggressive normalization (stripping stop words like "to", "in", "a") can group different episodes together. Example: "ue5-pcg-tutorial-beginners-episode-1" and "ue5-pcg-tutorial-beginners-episode-2" normalize to the same key when stop words are stripped. Always verify groups manually before moving files. If two files in a group have different numbers in their names, they are NOT duplicates.
- **`find -exec` is blocked by rtk on macOS.** The `rtk` tool intercepts `find` commands and rejects compound predicates (`-exec`, `-not`). Use `find ... | xargs rm -f` instead.
- **`wc -l` reports 0 for heredoc-written files.** Heredocs strip trailing newlines. Use `wc -c` or `stat -f '%z'` for size checks.
- **`stat -f '%z'` fails with `#` in filenames.** On macOS, `stat -f '%z' 'file with #.md'` returns 0 or errors because `#` is interpreted as a shell comment. `wc -c < 'file'` has the same issue. **Use `os.path.getsize()` in Python** — it handles all special characters natively without shell escaping. This is critical when comparing file sizes across folders with inconsistent naming.
- **Keep _duplicates/ until user confirms.** Never delete files during reorganization. Move to `_duplicates/` and let the user verify before permanent deletion.
- **Title-case names > lowercase-hyphen names.** When choosing between `Adding_Realistic_Details.md` and `adding-realistic-details.md`, keep the title-case version — it's more readable and consistent with the naming convention.
