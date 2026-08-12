# YouTube Research Pipeline — Finding and Adding New Content

## Overview

When building a knowledge base, you eventually need to find NEW videos to add — not just process existing playlists. This covers the research → verify → extract → review pipeline.

## Phase 1: Gap Analysis

Before searching, identify what's missing from the existing vault.

```python
import os

# Scan all tags across the vault
all_tags = {}
for folder in os.listdir(base):
    path = os.path.join(base, folder)
    if not os.path.isdir(path) or folder.startswith('_'):
        continue
    for fname in os.listdir(path):
        if not fname.endswith('.md') or fname.startswith('_'):
            continue
        with open(os.path.join(path, fname), 'r', errors='ignore') as f:
            content = f.read()
        for line in content.split('\n'):
            if line.strip().startswith('tags:'):
                tags_str = line.split(':', 1)[1].strip().strip('[]')
                for t in tags_str.split(','):
                    t = t.strip().strip('"').strip("'")
                    if t:
                        all_tags[t] = all_tags.get(t, 0) + 1

# Topics with 0-2 files are gaps
gaps = {t: c for t, c in all_tags.items() if c <= 2}
```

Common UE5 knowledge base gaps:
- GAS (Gameplay Ability System)
- C++ for UE5
- Multiplayer/Networking
- Data Assets/Data Tables
- Niagara particles
- UI/UMG
- Enhanced Input
- Save Systems
- Animation Blueprints
- Audio/MetaSounds
- Optimization/Profiling
- World Partition

## Phase 2: Video Discovery

Use `delegate_task` with `toolsets=["web"]` to search for videos in parallel.

```
Search for the best UE5 [TOPIC] tutorials. Find 3-5 high-quality videos.
Return: video URLs, titles, channel names, durations.
Focus on practical how-to tutorials, not overviews or opinion pieces.
```

**Tips:**
- Search for specific channels known for quality (Gorka Games, Ryan Laley, Ali Elzoheiry, Ask A Dev, PolyBoost)
- Prefer videos with code/node examples in thumbnails
- Check view counts and like ratios as quality signals
- Include the UE version in the search query when possible

## Phase 3: Version Verification

Before extracting, verify videos are relevant to the target UE version.

```
Check each video for UE5 version relevance:
1. What UE5 version does it target? (from title, description, comments)
2. When was it published?
3. Is it still relevant for UE5.7/5.6?
Mark each as: KEEP / OUTDATED / UNCLEAR
```

**Version relevance rules:**
- UE5 core systems (GAS, Behavior Trees, UMG, Enhanced Input, SaveGame, Replication) are stable across 5.0-5.7
- Niagara had significant changes between EA and release (2021 vs 2022+)
- MetaSounds evolved between EA and release
- Materials, Blueprints, and C++ fundamentals are version-agnostic
- World Partition, HLODs, and Nanite improved significantly in 5.4+
- When in doubt, KEEP — most tutorials from 2022+ are still valid

## Phase 4: Extraction

Extract videos in priority order. Use `delegate_task` with `toolsets=["web", "terminal"]`.

**Priority levels:**
- HIGH: Topics with 0 files in vault (new coverage)
- MEDIUM: Topics with 1-3 files (thin coverage)
- LOW: Topics with 4+ files (supplementary)

**Extraction strategy:**
1. Try `youtube-transcript-api` first (best quality)
2. Fall back to `web_extract` on YouTube URLs
3. Fall back to `web_search` for companion written content
4. Synthesize into tutorial format with real steps/code

**Critical: Use `write_file` from main session for persistence.** Subagent file writes don't reliably persist. After each batch, verify files exist on disk before proceeding.

## Phase 5: Formatting

For each new folder:
1. Add frontmatter (title, source, video_id, type, series, episode, tags)
2. Add wikilinks (previous/next episodes, series MOC)
3. Create MOC index file
4. Verify all files persisted

## Phase 6: User Review

Present the batch for review before pushing:
- Show file counts per topic
- Show file sizes (quality indicator)
- List any files that are summaries vs transcripts
- Ask for approval before committing to Git

### Review Document Pattern

Create a `_REVIEW_New_Tutorials.md` at the vault root listing every new file with:
- Title, source URL, tags, size
- One-line summary of content
- Coverage status (NEW vs EXPANDED)

This gives the user a single document to review without opening each file.

### Multi-Reviewer Verification

Before presenting to the user, run independent reviews:

1. **File sweep** — Check for duplicates against existing vault:
   - video_id matches (exact duplicate)
   - source URL matches (exact duplicate)
   - Title similarity (3+ shared keywords after removing stop words)
   - Intra-new duplicates (new files matching each other)

2. **Independent review** — Delegate to a different agent profile:
   - Content quality spot-check (3-5 random files)
   - Wikilink verification (do Related links resolve?)
   - MOC completeness (do MOCs list all files?)
   - Frontmatter consistency (all required fields present?)
   - UE version relevance (no deprecated features?)

3. **Second opinion** — Optional second reviewer for critical batches:
   - Different focus (e.g., "would an RPG dev actually use this?")
   - Review document accuracy check
   - Broken link detection

Fix any issues found before presenting to user. Report all findings (pass/fail/warnings) in the summary.

### Git Push

After user approval, commit and push to GitHub.

```bash
cd /path/to/vault
git add -A
git commit -m "Add N new tutorial files across M topics"
git push
```

If push is rejected (non-fast-forward), pull with rebase first:
```bash
git pull origin main --rebase && git push
```

## Pitfalls

```
1. Gap analysis     → identify 14 topics with 0-3 files
2. Video discovery  → find 46 videos across 14 topics
3. Version check    → 45/46 relevant to UE5.7/5.6
4. Extract HIGH     → 13 files (GAS, C++, Data Assets)
5. Extract MEDIUM   → 24 files (AI, Niagara, UI, etc.)
6. Extract LOW      → 8 files (Audio, Materials, Multiplayer)
7. Format           → frontmatter + wikilinks + MOCs
8. Review           → present to user
9. Push             → commit to GitHub
```

## Pitfalls

- **Don't parallelize extraction batches too aggressively.** YouTube rate-limits are per-IP. Running 3 subagents in parallel means 3x the request rate, hitting blocks faster.
- **Subagent file writes don't persist.** Always verify and redo from main session if needed.
- **Version verification saves wasted effort.** Don't extract 10 videos only to find they're all for UE4.
- **User review is mandatory.** Never push to Git without the user seeing what was added.
