# Post-Extraction Organization & Obsidian Vault Formatting

## Overview

After extracting YouTube transcripts, the raw output needs organization before it's useful. This covers: deduplication, non-edu content triage, naming normalization, and Obsidian vault formatting.

## Phase 1: Deduplication

Multiple extraction runs create duplicates. Common patterns:

- **Same video, different names**: `ue5-rpg-80-save-and-load.md` vs `Unreal_Engine_5_RPG_Tutorial_Series_-_#80_Save_and_Load.md`
- **Nested copies**: `Folder/Folder/files` (identical content)
- **Naming variants**: `Part_1_Title.md` vs `ue5-starter-01-title.md`

### Dedup Strategy

```python
import os, re

def normalize(name):
    """Aggressive normalization for matching."""
    n = name.lower().replace(".md", "")
    n = re.sub(r'[^a-z0-9\s]', ' ', n)
    words = n.split()
    stop = {'a', 'an', 'the', 'in', 'on', 'of', 'to', 'for', 'and', 'or', 'by', 'with', 'from', 'over', 'using'}
    words = [w for w in words if w not in stop and len(w) > 1]
    return ''.join(words)

# Group files by normalized name
groups = {}
for f in files:
    key = normalize(f)
    groups.setdefault(key, []).append(f)

# For each group, keep largest file (most content)
for key, group in groups.items():
    if len(group) > 1:
        sizes = [(f, os.path.getsize(os.path.join(path, f))) for f in group]
        sizes.sort(key=lambda x: x[1], reverse=True)
        keep = sizes[0][0]
        for f, s in sizes[1:]:
            move_to_duplicates(f)
```

### Where to Put Duplicates

Create `_duplicates/` at the vault root. Preserve subfolder structure so the user can see where each came from. The user reviews and deletes when confident.

## Phase 2: Non-Educational Content Triage

Most playlist extractions are 70-90% YouTube descriptions (links, chapter timestamps, channel info) with no actual tutorial content.

### Detection Heuristics

```python
is_non_edu = False
reason = ""

# 1. Filename-based detection
fname_low = filename.lower()
if 'introduction' in fname_low and word_count < 150:
    is_non_edu, reason = True, "intro (short)"
elif 'conclusion' in fname_low or 'next_steps' in fname_low:
    is_non_edu, reason = True, "conclusion/wrap-up"
elif 'full_course' in fname_low:
    is_non_edu, reason = True, "course overview"
elif 'want_to_make_games' in fname_low:
    is_non_edu, reason = True, "promo/motivational"
elif 'thinking_like_a_programmer' in fname_low:
    is_non_edu, reason = True, "conceptual (no how-to)"

# 2. Content-based detection
has_steps = any(marker in body for marker in [
    '## Step', '### 1', '### 2', '## 1.', '## 2.',
    '**Step 1', '**Step 2', '1. **', '2. **',
    '## Core', '## Key', '## Overview\n', '## Tutorial',
])
has_chapters = body.count('00:') > 2 or body.count('0:0') > 3
link_count = body.count('http')

if not is_non_edu:
    if has_chapters and not has_steps and word_count < 250:
        is_non_edu, reason = True, f"chapter list only ({word_count}w)"
    elif link_count > 5 and not has_steps and word_count < 150:
        is_non_edu, reason = True, f"links/description only ({word_count}w)"
    elif word_count < 30 and not has_steps:
        is_non_edu, reason = True, f"nearly empty ({word_count}w)"

# 3. Borderline detection (150-250 words, no steps)
# Files with 150-250 words and no step markers are likely YouTube descriptions
# with extended channel info. Check for chapter markers as a signal.
if not is_non_edu and 150 <= word_count <= 250 and not has_steps:
    if has_chapters:
        is_non_edu, reason = True, f"chapter list only ({word_count}w)"
    elif link_count > 3:
        is_non_edu, reason = True, f"links/description only ({word_count}w)"
```

### Where to Put Non-Edu Files

Create `_non_educational/` at the vault root. NOT the same as `_duplicates/` — these are files that exist only once but lack educational value. Preserve subfolder structure. The user reviews and decides what to keep or delete.

## Phase 3: File Naming Normalization

### Target Format

```
NN_Topic_Name.md
```

- Episode-prefixed files: `01_Introduction.md`, `82_Bug_Fixing.md`
- Topic files: `Add_Water_Easily.md`, `Blueprint_Interface_Demystified.md`
- No special chars: remove `#`, `!`, `&`, `,`, `(`, `)`
- Underscores (not hyphens) for Obsidian compatibility
- Title Case for consistency

### Common Renames

```python
# Remove long prefixes
"Unreal_Engine_5_RPG_Tutorial_Series_-_#10_Title.md" → "10_Title.md"
"Learn_to_Code_in_UE5_-_5_-_Topic.md" → "05_Topic.md"
"ue5-starter-06-lighting.md" → "06_Lighting.md"

# Remove "How_to_" prefix
"How_to_Create_a_Landscape.md" → "Create_a_Landscape.md"

# Remove video tags from PCG files
"Title_tutorial_unrealengine_pcg.md" → "Title.md"
```

## Phase 4: Obsidian Vault Formatting

### YAML Frontmatter Schema

Every file should have consistent frontmatter:

```yaml
---
title: "Full Video Title"
source: "https://www.youtube.com/watch?v=VIDEO_ID"
video_id: "VIDEO_ID"
type: "youtube-transcript" | "youtube-summary" | "step-by-step-guide" | "article"
series: "Series Name"
episode: 0
tags: [ue5, topic1, topic2]
---
```

**Fields:**
- `title`: Full video title (quoted)
- `source`: YouTube URL
- `video_id`: 11-char YouTube ID
- `type`: Content type (transcript has timestamps, summary has structured breakdown, step-by-step has numbered instructions)
- `series`: Which playlist/series this belongs to
- `episode`: Episode number within series (0 if not part of a series)
- `tags`: Array of lowercase tags (include domain tags like `ue5`, `rpg`, `blueprint`)

### Wikilinks

Add a `## Related` section at the bottom of each file:

```markdown
---

## Related

- ← Previous: [[Previous_Episode_File]]
- → Next: [[Next_Episode_File]]
- 📚 Series: [[_MOC_Series_Name]]
```

For Step-by-Step guides, also link to the full transcript:

```markdown
- 📄 Full Transcript: [[Original_Transcript_File]]
```

### MOC (Map of Content) Files

Create one `_MOC_FolderName.md` per folder:

```yaml
---
title: "Series Name — Map of Content"
type: "moc"
tags: [ue5, moc, index]
---

# Series Name

Description of the series.

**Files:** N

## Episodes

- [[01_Introduction]]
- [[02_Topic]]
- ...

## Topics

- [[Non_Episode_File]]
- ...
```

## Phase 5: Verification

After all formatting, verify:

```python
for folder in active_folders:
    files = list_md_files(folder)
    for f in files:
        assert has_frontmatter(f), f"Missing frontmatter: {f}"
        assert has_title(f), f"Missing title: {f}"
        assert has_tags(f), f"Missing tags: {f}"
        assert not has_hash_in_filename(f), f"# in filename: {f}"
    
    assert exists(f"_MOC_{folder}.md"), f"Missing MOC: {folder}"
```

## Phase 6: Git Push

After user approval, commit and push to GitHub.

```bash
cd /path/to/vault
git add -A
git commit -m "Add N new tutorial files across M topics"
git push
```

### Credential Helper

If you get macOS keychain prompts on every push, the `osxkeychain` credential helper is interfering with `gh auth`. Fix:

```bash
git config --global credential.helper '!/usr/local/bin/gh auth git-credential'
```

This sets `gh auth` as the default for all remotes. The `osxkeychain` helper prompts the keychain on every push; `gh auth` uses the stored GitHub CLI token silently.

### .gitignore for Obsidian Vaults

```gitignore
# Obsidian workspace state (changes on every open)
.obsidian/workspace.json
.obsidian/workspace-mobile.json

# macOS metadata
.DS_Store

# Obsidian trash
_trash/
```

## Typical File Counts

After full extraction and cleanup:
- 10-30% educational content (transcripts + structured summaries)
- 70-90% non-educational (YouTube descriptions)
- 5-15% duplicates from multiple runs

Example from a 6-playlist UE5 extraction:
- 407 total files extracted
- 155 educational (active content)
- 91 non-educational (for user review)
- 170 duplicates (safe to delete)
