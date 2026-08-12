# Post-Extraction Organization & Deduplication

## When to use
After extracting YouTube transcripts/summaries to disk, the output directory typically has duplicates, inconsistent naming, and a mix of educational and non-educational files. This reference covers the cleanup workflow.

## Content Quality Triage

After extraction, classify files into educational vs non-educational. Most playlists produce a mix of both.

### Non-educational indicators (flag for removal)
- **YouTube descriptions only**: 50-200 words, multiple `http` links, chapter timestamps (`00:00`, `0:0`), but NO structured steps (`## Step`, `### 1`, `1. **`)
- **Intro/overview files**: filename contains `introduction`, `overview`, `full_course` AND content < 150 words
- **Conclusions**: filename contains `conclusion`, `next_steps`, `wrap-up`
- **Promo/motivational**: filename contains `want_to_make_games`, `getting_started` with no how-to content
- **Conceptual/philosophy**: "thinking like a programmer", "understanding the workflow" — no actionable steps

### Educational indicators (keep)
- Word count > 200 with structured steps (`## Step`, `### 1`, `1. **`, `## Key Concepts`)
- Full transcripts with timestamps (`[**0:00**]`) — verbose but contain every detail
- Files > 5KB with implementation details (Blueprint node names, parameter values, code snippets)

### Word count threshold: use 200, not 150

A threshold of 150 words lets too many YouTube descriptions through. Files with 150-169 words are almost always descriptions with links and channel promo — no instructional content. Set the cutoff at **200 words** for the `links/description only` check. Files between 150-200 words with no step markers should be flagged for manual review or moved to `_non_educational/`.

**Verified in practice:** In a 200+ file extraction, 7 files with 150-169 words slipped through the 150-word threshold. All 7 were YouTube descriptions with no educational content. The 200-word threshold catches these.

### Triage script pattern
```python
import os, re

def classify_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Strip frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        body = parts[2].strip() if len(parts) >= 3 else content
    else:
        body = content
    
    word_count = len(body.split())
    fname_low = os.path.basename(filepath).lower()
    
    has_steps = any(m in body for m in [
        '## Step', '### 1', '### 2', '## 1.', '## 2.',
        '**Step 1', '**Step 2', '1. **', '2. **',
        '## Core', '## Key', '## Overview\n', '## Tutorial',
        '### Setup', '### Creating', '### Building',
    ])
    has_chapters = body.count('00:') > 2 or body.count('0:0') > 3
    link_count = body.count('http')
    
    # Filename-based indicators
    if 'introduction' in fname_low and word_count < 150:
        return 'non-edu', 'intro (short)'
    if 'conclusion' in fname_low or 'next_steps' in fname_low:
        return 'non-edu', 'conclusion/wrap-up'
    if 'full_course' in fname_low:
        return 'non-edu', 'course overview'
    if 'want_to_make_games' in fname_low:
        return 'non-edu', 'promo/motivational'
    if 'thinking_like_a_programmer' in fname_low:
        return 'non-edu', 'conceptual (no how-to)'
    
    # Content-based indicators (200-word threshold)
    if has_chapters and not has_steps and word_count < 250:
        return 'non-edu', f'chapter list only ({word_count}w)'
    if link_count > 5 and not has_steps and word_count < 200:
        return 'non-edu', f'links/description only ({word_count}w)'
    if word_count < 30 and not has_steps:
        return 'non-edu', f'nearly empty ({word_count}w)'
    
    return 'edu', f'{word_count}w, steps={has_steps}'
```

**Important:** Always verify a sample of flagged files manually. The heuristic can misclassify — some "chapter list" files may have useful metadata, and some short files may contain critical configuration steps.

## Non-educational files: `_non_educational/` folder

`_duplicates/` holds same-content copies (true dupes). `_non_educational/` holds files that are unique but lack how-to value — YouTube descriptions, chapter lists, promo text, conceptual overviews. These are separate concerns:

```
YouTube-Transcripts/
├── Series_Name/            # Educational content only
├── _non_educational/       # Unique files with no how-to value (user reviews)
│   ├── Series_Name/
│   └── Other_Series/
└── _duplicates/            # Same-content copies (safe to delete)
```

Move non-edu files with `shutil.move()`, preserving the subfolder structure so the user can see where each came from. The user reviews `_non_educational/` and decides what to keep or delete — don't delete them automatically.

## Folder Deduplication Workflow

When the same content series exists across multiple folders (common after multiple extraction runs), merge and deduplicate.

### Step 1: Inventory all directories
```python
import os

base = "/path/to/YouTube-Transcripts"
for d in sorted(os.listdir(base)):
    path = os.path.join(base, d)
    if os.path.isdir(path) and not d.startswith('_'):
        count = len([f for f in os.listdir(path) if f.endswith('.md')])
        print(f"  {d}: {count} files")
```

### Step 2: Group files by episode/topic
Normalize filenames to extract episode numbers, then group:
```python
import re

def extract_episode(filename):
    """Extract episode number from various naming patterns."""
    m = re.search(r'#(\d+)', filename)        # #12, #80
    if not m:
        m = re.search(r'^(\d+)[_-]', filename) # 12_, 60-
    if not m:
        m = re.search(r'rpg-(\d+)', filename)  # ue5-rpg-80
    return int(m.group(1)) if m else None

def normalize_for_comparison(filename):
    """Aggressive normalization for finding duplicates."""
    n = filename.lower().replace('.md', '')
    n = re.sub(r'[^a-z0-9\s]', ' ', n)
    words = n.split()
    stop = {'a', 'an', 'the', 'in', 'on', 'of', 'to', 'for', 'and', 'or', 'by', 'with', 'from', 'over', 'using'}
    words = [w for w in words if w not in stop and len(w) > 1]
    return ''.join(words)
```

### Step 3: Compare and keep the best version
For each duplicate group, keep the file with the most content:
```python
def get_file_size(path):
    """Use os.path.getsize() — most reliable on macOS. stat -f '%z' and wc -c both fail with #, !, & in filenames."""
    return os.path.getsize(path)
```

**`os.path.getsize()` vs `stat -f '%z'` vs `wc -c`:** On macOS, `wc -c < 'file with #.md'` fails because `#` is interpreted as a shell comment. `stat -f '%z'` works but requires subprocess. `os.path.getsize()` is the most reliable — pure Python, no shell escaping, handles all characters.

### Step 4: Move duplicates to `_duplicates/`
```python
import shutil

dupes_dir = os.path.join(base, '_duplicates', folder_name)
os.makedirs(dupes_dir, exist_ok=True)
shutil.move(src_path, os.path.join(dupes_dir, filename))
```

**⚠️ CRITICAL: Protect `_duplicates/` and `_non_educational/` from cleanup commands.**
Never run broad destructive commands against the extraction root:
```bash
# DANGEROUS — can delete _duplicates/ and _non_educational/ contents
find /path/to/YouTube-Transcripts -name '.DS_Store' -delete

# SAFER — scope to specific directories, or use Python
find /path/to/YouTube-Transcripts -maxdepth 2 -name '.DS_Store' -delete
# Or in Python:
for root, dirs, files in os.walk(base):
    if '_duplicates' in root or '_non_educational' in root:
        continue
    for f in files:
        if f in ['.DS_Store', '.checkpoint.json']:
            os.remove(os.path.join(root, f))
```

### Step 5: Normalize file naming
Consistent naming across all folders:
- **Ordered series**: `NN_Topic_Name.md` (e.g., `01_Introduction.md`, `12_Target_Lock.md`)
- **Standalone**: `Topic_Name.md` (e.g., `Water_Plugin_Setup.md`)
- **Prefixes**: Remove long prefixes like `Unreal_Engine_5_RPG_Tutorial_Series_-_#`
- **Special chars**: Strip `!`, `#`, `&`, `(`, `)`, replace `+` with `and`
- **Underscores**: Collapse multiple `_` to single, strip leading/trailing

```python
def clean_filename(name):
    name = re.sub(r'^Unreal_Engine_5_RPG_Tutorial_Series_-_#(\d+)_', r'\1_', name)
    name = re.sub(r'^How_to_', '', name)
    name = name.replace('!', '').replace('#', '').replace('&', 'and')
    name = re.sub(r'_+', '_', name).strip('_')
    return name
```

**Use `os.rename()` for renames** — shell commands with special characters in filenames (`#`, `!`, `,`) cause quoting issues. Python's `os.rename()` handles them natively.

## Typical Output Structure After Cleanup
```
YouTube-Transcripts/
├── Series_Name_1/        # Canonical folder, cleaned names
├── Series_Name_2/
├── Step_by_Step_Guides/  # Extracted how-to steps (if generated)
├── Individual_Videos/    # Standalone tutorials
├── Articles/             # Non-video content
├── _non_educational/     # Non-edu files for user review
│   ├── Series_Name_1/
│   └── Series_Name_2/
└── _duplicates/          # True dupes, safe to delete when confident
    ├── Series_Name_1/
    └── Series_Name_2/
```
