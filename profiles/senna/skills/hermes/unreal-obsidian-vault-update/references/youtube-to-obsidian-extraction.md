# YouTube-to-Obsidian Extraction Patterns

Proven patterns for extracting YouTube tutorials into an Obsidian vault.

## Extraction Priority Order

1. youtube-transcript-api — best quality (raw transcripts with timestamps)
2. web_extract on YouTube URL — structured summaries (sometimes returns 403)
3. web_search for companion content — blog posts, docs, written tutorials
4. Synthesize from metadata + official docs — last resort, still produces useful content

## Folder Naming Convention

```
UE5_Topic_Name/
  01_First_Tutorial.md
  02_Second_Tutorial.md
  _MOC_UE5_Topic_Name.md
```

- Prefix with UE5_ for consistency
- Episode number prefix (01, 02, 03) for sort order
- Underscores, not hyphens (Obsidian compatibility)
- Title Case for file names
- No # in filenames (breaks Obsidian tag parsing)

## Non-Educational Content Filter

After extraction, sweep for files that are just YouTube descriptions:
- Word count less than 150 AND no step/numbered patterns
- Chapter timestamps (00:) but no structured steps
- Links/description only (5+ URLs, less than 150 words, no steps)

Move these to _non_educational/ preserving subfolder structure.

## Deduplication

Check by:
1. video_id match (exact duplicate)
2. source URL match (same video, different filename)
3. Title keyword overlap (3+ shared keywords after removing stop words)

## Quality Indicators

GOOD (educational):
- Step/numbered patterns
- Code blocks (cpp, blueprint)
- Overview, Key Concepts, Architecture sections
- 300+ words with structured content

BAD (non-educational):
- YouTube description with links and chapter timestamps
- Promo/motivational content
- Full course overview without actual steps
- Less than 150 words with no structure
