---
name: hermes-update-review
description: "Use when checking what a Hermes update added or commits."
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [hermes, updates, changelog, release-notes]
    related_skills: [hermes-agent, fal-ai-generation]
---

# Hermes Update Review

Investigate what a Hermes update actually added — especially topic digests ("what's new for creativity / video / image gen"). This recurs after every `hermes update`.

## When to use
- User says "find what's new regarding X in the latest update" or "look at the recent commits for me"
- User wants to know if a capability (video gen, image model, skill) exists in their current install
- Auditing whether the local install matches the latest release

## Steps
1. **Local version & install state** — `hermes --version`. Gives version (e.g. `v0.20.0 (2026.8.3)`), install directory, Python version, and `Up to date` status.
2. **Checkout state** — `cd <installdir> && git describe --tags` shows how far the checkout is past the nearest tag (e.g. `v2026.7.20-5082-g03fa32c92`). Git-installed Hermes updates pull latest main, which can be AHEAD of the latest tagged release — commits after the tag ARE in the user's install even though the release notes never mention them.
3. **Release notes** — fetch the GitHub releases list (`https://github.com/NousResearch/hermes-agent/releases`) AND the full tag page for the latest version (`https://github.com/NousResearch/hermes-agent/releases/tag/v<version>`). Tag pages carry the full curated notes; the releases-list page truncates them.
4. **Keyword grep the local git log** (authoritative — catches post-tag commits):
   ```bash
   git log --format="%h %ad %s" --date=short -5000 | grep -iE "video|flux|image|creative|media"
   ```
   Then `git show <sha> --stat` for the shape of a commit and `git show <sha>` for what it actually added (model lists, endpoints, caveats).
5. **Cross-reference sources**: official tag notes > local git log > community mirrors (`hermes-ai.net` is an UNOFFICIAL community guide — GitHub is authoritative). Patch tags (e.g. v2026.7.30) sometimes summarize a window and defer full notes to the next minor ("Full curated release notes for this window will ship with v0.20.0") — treat them as pointers, not the full story.

## Pitfalls
- **web_extract truncates long pages** — the full text is saved to a cache file whose path is in the result footer (e.g. `~/.hermes/profiles/<profile>/cache/web/...`). Grep that file with `search_files` instead of re-fetching or reading 100K+ chars.
- **Release notes are not the whole story** — notes end at the tag date; fresh feature commits on main land in the install but never make the notes. Always grep the local git log for the topic.
- **The `hermes-agent` skill may be absent** in some profiles (`skill_view` returns "not found"). The docs at https://hermes-agent.nousresearch.com/docs are the authoritative reference for Hermes itself.
- Release pages use emoji section headers (🎬 🎨 🏗️) — grep for topic keywords, not section names.

## Session-specific detail
- `references/creative-video-whatsnew-2026-08.md` — worked example: v0.20.0 creative/video commit SHAs, FAL model families, portal caveats.
