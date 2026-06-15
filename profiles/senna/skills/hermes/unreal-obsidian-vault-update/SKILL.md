---
name: unreal-obsidian-vault-update
description: "Update and release the UE5 Obsidian vault (Unreal-Engine-Obsidian) — research, extract, format, review, changelog, version tag, GitHub release."
platforms: [macos]
---

# UE5 Obsidian Vault — Full Pipeline

Vault location: `~/Documents/Unreal-Engine-Obsidian/`
GitHub repo: `<your-github-username>/Unreal-Engine-Obsidian`
Skill: `unreal-obsidian-vault-update`

## When to use

Adding new tutorial content, architecture docs, or making structural changes to the vault.

## Pipeline (5 phases)

### Phase 1: Research

1. Identify topic gaps — scan existing tags/folders to find what's missing
2. Search YouTube for quality tutorials on those topics
3. Verify UE5 version relevance (target 5.6/5.7, reject older deprecated content)
4. Compile a candidate video list with URLs, titles, channels, durations

### Phase 2: Extract

1. For each video, try `youtube-transcript-api` first for raw transcripts
2. Fall back to `web_extract` on YouTube URL
3. Fall back to `web_search` for companion written content
4. Save each file to the appropriate folder with frontmatter

**Critical pitfall:** Subagent `write_file` writes to sandbox, NOT the real filesystem. Files appear to succeed but don't persist. **Fix:** Use `terminal()` for file writes from subagents, or do writes from the main session directly.

### Phase 3: Format

For each new folder:
1. Add consistent YAML frontmatter to all files:
   ```yaml
   ---
   title: "Video Title"
   source: "https://www.youtube.com/watch?v=VIDEO_ID"
   video_id: "VIDEO_ID"
   type: "youtube-summary"
   series: "Series Name"
   episode: N
   tags: [ue5, topic1, topic2]
   ---
   ```
2. Add `## Related` section with wikilinks:
   - `← Previous: [[filename]]`
   - `→ Next: [[filename]]`
   - `📚 Series: [[_MOC_FolderName]]`
3. Create `_MOC_FolderName.md` index file linking all files in the folder

### Phase 4: Review (3-reviewer gate)

**MANDATORY before any push.** Three independent reviews:

1. **Self review** — file-by-file sweep checking for duplicates, content quality, format consistency
2. **Profile review 1** (e.g., Architect) — independent verification of duplicates, content quality, UE5 version compatibility
3. **Profile review 2** (e.g., Secretary) — wikilink validation, MOC completeness, review doc accuracy

Fix all issues found before proceeding. If any reviewer flags a FAIL, resolve and re-review.

### Phase 5: Release

1. Update `README.md` — ensure the folder tables, file counts, and version links match current vault state
2. Update `CHANGELOG.md` with new version section at the TOP:
   ```markdown
   ## [vX.Y.Z] — YYYY-MM-DD
   
   ### Added
   - Description of new files/folders
   
   ### Fixed
   - Description of fixes
   ```
2. Commit: `git add -A && git commit -m "vX.Y.Z — brief description"`
3. Pull and push: `git pull origin main --rebase && git push`
4. Create GitHub release:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z — Short Title" --notes "## What's New
   
   Human-readable summary of changes.
   
   **Vault total: N files across M folders**"
   ```

## Version numbering

- **Major (X)**: Major restructure, breaking changes
- **Minor (Y)**: New topic folders or significant new content
- **Patch (Z)**: Fixes, small additions, formatting

## Workflow B: Merge external PR + apply errata fixes

When a community contributor submits a PR that also flags issues in existing vault content:

1. **Review the PR** — check `gh pr view <N> --json body,files,additions,deletions,mergeable`
2. **Check for errata** — read the errata/alignment file from the PR branch (use `gh api` on the fork's branch ref)
3. **Merge the PR** — `gh pr merge <N> --repo <repo> --merge` then `git pull`
4. **Apply ALL fixes from the errata** — do NOT stop after merging. The PR documents issues but does NOT fix them in your files. You must apply each fix yourself.
5. **Update README.md** — add new folders/files to the appropriate tables
6. **Update CHANGELOG.md** — new version entry with both "Added" (PR content) and "Fixed" (errata corrections) sections
7. **Also update any stale references in prior CHANGELOG entries** — e.g., if the errata replaces "INI setup" with "module registration", the v1.3.0 entry that says "INI setup" should be updated too
8. **Commit, push, and create GitHub release** (Phase 5 steps)

**Critical:** Merging a PR and fixing the issues it flags are TWO SEPARATE STEPS. Never assume the PR fixes its own findings.

## Pitfalls

- **Always `git pull --rebase` before push** — remote may have changes from other sessions
- **Update CHANGELOG.md BEFORE committing**
- **Release notes should be human-readable** — explain what's useful, not commit messages
- **Credential helper**: `gh auth git-credential` is global default. No keychain prompts.
- **Subagent file writes** — see Phase 2 pitfall above
- **`stat -f '%z'` fails with `#` in filenames** — use `os.path.getsize()` in Python
- **Forgetting README + CHANGELOG after content changes** — any merge, fix, or content addition that changes the vault structure MUST update both. The user will call it out. Make it automatic: after every `git pull` that adds folders, immediately update README tables + CHANGELOG entry before committing.
- **GitHub Release is part of the workflow** — user preference is versioned releases (CHANGELOG + GitHub Release). Don't skip the `gh release create` step.
