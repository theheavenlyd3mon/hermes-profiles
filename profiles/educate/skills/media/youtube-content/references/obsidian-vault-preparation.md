# Obsidian Vault Preparation from Extracted Transcripts

## When to use
After organizing extracted YouTube transcripts (dedup, non-edu triage, naming normalization), convert them into a proper Obsidian vault with frontmatter, wikilinks, and MOC index files.

## Phase 1 — Standardize Frontmatter

Every file needs consistent YAML frontmatter. Build a folder→series mapping and process all files:

```python
import os, re

folder_meta = {
    "Series_Name": {"series": "Series Display Name", "default_tags": ["tag1", "tag2"]},
}

def parse_frontmatter(content):
    if not content.startswith('---'):
        return {}, content
    end = content.find('---', 3)
    if end == -1:
        return {}, content
    yaml_block = content[3:end].strip()
    body = content[end+3:].strip()
    meta = {}
    for line in yaml_block.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key == 'tags':
                val = val.strip('[]')
                meta[key] = [t.strip().strip('"').strip("'") for t in val.split(',') if t.strip()]
            else:
                meta[key] = val
    return meta, body

def build_frontmatter(meta, folder_info, filename):
    title = meta.get('title', filename.replace('.md', '').replace('_', ' '))
    source = meta.get('source', '')
    video_id = meta.get('video_id', '')
    file_type = meta.get('type', 'youtube-summary')
    existing_tags = meta.get('tags', [])
    if isinstance(existing_tags, str):
        existing_tags = [t.strip() for t in existing_tags.split(',')]
    all_tags = list(dict.fromkeys(existing_tags + folder_info.get('default_tags', [])))
    episode = extract_episode(filename)  # from file-organization skill
    series = folder_info.get('series', '')
    tags_str = ", ".join(all_tags)
    return f'''---
title: "{title}"
source: "{source}"
video_id: "{video_id}"
type: "{file_type}"
series: "{series}"
episode: {episode}
tags: [{tags_str}]
---'''
```

## Phase 2 — Add Wikilinks

Add a `## Related` section at the bottom of each file with navigation links:

```python
# Build episode index per series
series_episodes = {}  # series_name → sorted list of {link, ep, folder}

for fname, meta in all_files:
    series = meta['series']
    episode = meta['episode']
    link = fname.replace('.md', '')
    series_episodes.setdefault(series, []).append({'link': link, 'ep': episode})

for series in series_episodes:
    series_episodes[series].sort(key=lambda x: x['ep'])

# Add wikilinks to each file
for fname in files:
    eps = series_episodes[series]
    current_idx = next((i for i, e in enumerate(eps) if e['link'] == link), None)
    
    related = []
    if current_idx > 0:
        related.append(f"← Previous: [[{eps[current_idx-1]['link']}]]")
    if current_idx < len(eps) - 1:
        related.append(f"→ Next: [[{eps[current_idx+1]['link']}]]")
    if len(eps) > 3:
        related.append(f"📚 Series: [[_MOC_{folder_name}]]")
    
    if related:
        content += "\n\n---\n\n## Related\n\n" + "\n".join(f"- {r}" for r in related) + "\n"
```

### Cross-folder references
For Step-by-Step guides extracted from transcripts, add a cross-reference:
```python
if folder == "Step_by_Step_Guides":
    rpg_link = find_corresponding_transcript(episode_number)
    if rpg_link:
        related.append(f"📄 Full Transcript: [[{rpg_link}]]")
```

## Phase 3 — Create MOC (Map of Content) Index Files

One MOC per folder. The MOC is the entry point for browsing a series:

```python
for folder, title, description in folders:
    files = sorted([f for f in os.listdir(path) if f.endswith('.md')])
    
    episodes = [(extract_episode(f), f.replace('.md', '')) for f in files]
    episodes.sort()
    
    lines = [
        '---',
        f'title: "{title} — Map of Content"',
        'type: "moc"',
        'tags: [ue5, moc, index]',
        '---',
        '',
        f'# {title}',
        '',
        description,
        '',
        f'**Files:** {len(files)}',
        '',
        '## Episodes',
        '',
    ]
    for ep, link in episodes:
        lines.append(f'- [[{link}]]')
    
    moc_path = f"{path}/_MOC_{folder}.md"
    with open(moc_path, 'w') as f:
        f.write('\n'.join(lines))
```

### MOC naming convention
`_MOC_FolderName.md` — the underscore prefix sorts it to the top in Obsidian's file explorer.

## Phase 4 — Verify

```python
# Check all files have frontmatter, wikilinks, tags
for folder in active_folders:
    for fname in files:
        content = open(path).read()
        assert content.startswith('---'), f"Missing frontmatter: {folder}/{fname}"
        assert '[[' in content, f"Missing wikilinks: {folder}/{fname}"
        assert 'tags:' in content, f"Missing tags: {folder}/{fname}"
    
    # Check MOC exists
    assert os.path.exists(f"{path}/_MOC_{folder}.md"), f"Missing MOC: {folder}"
```

Expected output:
```
✅ All files have frontmatter
✅ 99%+ files have wikilinks (first in series has no "Previous")
✅ All files have tags
✅ All folders have MOC index files
```

## Pitfalls

- **`#` in filenames breaks Obsidian tag parsing.** Obsidian interprets `#` as tag syntax. Rename files with `#` in the name before importing to the vault.
- **Series link should point to MOC, not first episode.** The `📚 Series: [[link]]` wikilink should point to `_MOC_FolderName`, not to the first episode file. The MOC is the canonical entry point.
- **Frontmatter `source` field may contain URLs with special chars.** Always quote the source URL in frontmatter: `source: "https://..."` not `source: https://...`.
- **MOC files don't need `source` or `video_id`.** They're index files, not content files. The triage script will flag them as "missing source" — this is expected, not an issue.
- **Episode extraction from Step-by-Step guide filenames.** Files like `13_RPG_Tutorial_10_Sword_Trace_Damage.md` have TWO numbers — the guide's sequence number (13) and the RPG episode number (10). When cross-referencing, extract the RPG episode from the filename content (`RPG_Tutorial_(\d+)`), not the prefix.
