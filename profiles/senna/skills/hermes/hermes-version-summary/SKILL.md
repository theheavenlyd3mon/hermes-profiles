---
name: hermes-version-summary
description: Deliver Hermes agent version and update summaries in concise list format. Governs how to answer "what are the new updates" questions — structured, scannable, with clear section separation.
triggers:
  - "what are the new updates"
  - "what's new in hermes"
  - "hermes updates since"
  - "hermes changelog"
  - "hermes version changes"
  - "what changed in hermes"
  - "hermes release notes"
  - "is [feature] new"
  - "when did [feature] land"
  - "tell me about [feature page]"
author: Senna (from user preference + session pattern)
version: 0.2.0
---

IDENTITY: Summarizer.ChangelogReporter. Answer Hermes version/update queries in structured list format — never prose paragraphs, always header-delimited sections with emoji prefixes.
Law: ListFormatMandate — deliver in structured scannable sections, not prose paragraphs.
WHENUSE: UserAsks{WhatsNew,UpdatesSince,Changelog,ReleaseNotes,WhatChanged}|SpecificFeatureAge{IsItNew,WhenDidItLand}. ESPECIALLY:Don'tMixReleasedAndUnreleasedChanges. NoSkip:VersionStamp{lead with installed version + release date}|StatusStatement{released or post-release}.
REDFLAGS: NoReleaseVmdFound->FallbackToGitLogBetweenTags|SessionHistoryAsPrimary->ComplementaryOnlyNotAuthoritative|FeatureNotInReleaseNotes->CheckGitLogWith--grepDirectly|git logMissesBranch->Use--allFlag.
RATIONALIZATIONS: JustProseIt->UserSaidListFormat|MixReleasedAndUnreleased->SeparateSectionsWithClearBoundaries|OverExplain->ListFirstAdditionalProseOnlyOnFollowUp.
QUICKREF: GeneralQuery{Step1{hermes--version}->Step2{ReadReleaseVmdFiles}->Step3{GitLogSinceLastTag}->Step4{SessionSearch{lcm_grep}}->Step5{CrossCheckTagChronology}}->SpecificFeatureQuery{StepA{FetchDocsPage}->StepB{GrepReleaseNotes}->StepC{GitLog--grepFeature}->StepD{CompareCommitDateVsReleaseTag}->StepE{Summarize{Status,Date,What,Prerequisite,HowToUse}}}->Output{HeadersWithEmojis,SectionsWithSeparators,OneLinePerCommit,NeverParagraphExplanations}.

## Purpose

Answer "what's new/updated/changed in Hermes" questions in **list format** as explicitly requested by the user. This skill governs the presentation structure and investigation workflow for version/update Summary queries, including **specific feature age queries** ("is X new?").

## User Preference (Embedded)

**Format mandate:** Deliver information in a **list/structured format** — not prose paragraphs. The user said *"give this in a list format"*; treat this as a hard requirement for this class of query. Organize with clear headers, bullet points, and scannable sections.

**Conciseness tier:** High-level summary first (major version, key highlights), then details. Avoid conversational filler ("I found that...", "It looks like...").

## Trigger Phrases

### General version queries
- "what are the new updates to hermes"
- "what's new in hermes"
- "hermes updates since [date/version]"
- "hermes changelog"
- "hermes version changes"
- "hermes release notes"
- "what changed in hermes"

### Specific-feature age queries
- "tell me about [feature URL or name]"
- "is [feature] new"
- "when did [feature] land"
- "is this new"

## Investigation Workflow — General Version Summary

### Step 1 — Check Current Installation
```bash
hermes --version
```
Capture:
- Full version string (e.g., `v0.12.0 (2026.4.30)`)
- Any "Up to date" or update-available status

### Step 2 — Read Official Release Notes
Look for `RELEASE_v*.md` files in the Hermes agent directory:
```bash
ls ~/.hermes/hermes-agent/RELEASE_*.md
```
Read the latest matching version file. These contain curated, structured release documentation with Highlights, Features, Fixes sections.

### Step 3 — Check Recent Commits Since Tag
```bash
git -C ~/.hermes/hermes-agent/ log --oneline <last_tag>..HEAD
```
Where `<last_tag>` is the current installed version tag (from `git describe --tags --abbrev=0`). This shows unreleased fixes that landed after the official release.

### Step 4 — Search Session History
Use `lcm_grep` or `session_search` to find recent conversations mentioning Hermes updates, version checks, or installation/setup activity. This captures:
- Mid-cycle feature work (GBrain setup, NVIDIA NIM integration, provider additions)
- Security audits or configuration changes made since last release
- Unreleased work or experimental integrations

### Step 5 — Cross-check Version Tag Chronology
```bash
git -C ~/.hermes/hermes-agent/ tag --sort=-creatordate
```
Confirm which tag is newest and whether the installed version matches HEAD or is behind.

## Investigation Workflow — Specific Feature Age Query

When the user asks about a **specific feature** ("tell me about this [URL]", "is this new"), use this sub-workflow:

### Step A — Fetch the docs page
Extract the docs URL with `web_extract` to understand what the feature does. The docs site is `https://hermes-agent.nousresearch.com/docs/...`.

### Step B — Check release notes for mentions
```bash
grep -ri "feature_keyword" ~/.hermes/hermes-agent/RELEASE_v*.md
```
Search the latest two release files (current version and previous) for the feature name.

### Step C — Find the first LSP commit date
```bash
git -C ~/.hermes/hermes-agent/ log --all --oneline --format="%h %ai %s" --grep="<feature_keyword|related_keyword>"
```
Get every commit mentioning the feature. Look for the **earliest** `feat(<scope>):` commit — that's when it landed.

### Step D — Compare against last release tag
```bash
git -C ~/.hermes/hermes-agent/ log --oneline --format="%h %ai" <earliest_feat_commit> -1
git -C ~/.hermes/hermes-agent/ log --oneline --format="%h %ai" <last_tag> -1
```
- If the feature commit is **after** the tag → it's post-release, not in any official release yet
- If the feature commit is **between** two release tags → it landed in the older of the two releases
- Search the release notes between those tags to find the exact release

### Step E — Summarize findings
State clearly:
1. **Is it released?** Yes/No — based on tag comparison
2. **When it landed** — commit date
3. **What it adds** — brief description from the docs page
4. **What it builds on** — any prerequisite feature (e.g., LSP builds on post-write delta lint from v0.13.0)
5. **How to use it** — relevant CLI commands and config

## Output Structure (List Format Blueprint)

### General version summary
```
## 📦 vX.X.X Official Release (Date)

**Major Highlights:**
- Bullet 1
- Bullet 2
- Bullet 3

## 🔄 Post-Release Fixes (Date Range)

**Since vX.X.X, the following fixes have been merged but not yet released:**

1. **`category(scope): description`** — short summary (#PR)
...

---

**Installation status:** vX.X.X — Up to date / Update available: vX.X.X
```

### Specific feature age query
```
## Feature: [Name]

**Status:** Released in vX.X.X / Post-release (unreleased)
**Landed:** YYYY-MM-DD

**What it does:** [2-3 sentences]

**Prerequisite:** [feature it builds on, if any]

**CLI:**
```bash
hermes <subcommand>
```

**Config:**
```yaml
section:
  key: value
```
```

**Rules:**
- **Headers:** Emoji-prefixed section headers (`📦`, `🔄`, `⚙️`, etc.) for visual scanning.
- **Official release:** Use the RELEASE.md's "Highlights" section verbatim where possible; group by feature area.
- **Post-release commits:** List as numbered items with PR references in parentheses.
- **One-line per commit** — no paragraph explanations.
- **Separator:** Use `---` between major sections.
- **Feature age query:** Always state whether the feature is released or post-release. If unreleased, note "available on HEAD but not in any official release yet."

## Pitfalls

- **Don't mix released and unreleased changes.** Keep the official release highlights separate from post-tag commits.
- **Don't omit the version/date stamp.** Always lead with the installed version and release date.
- **Don't over-explain.** The format is list-first; additional prose only if the user asks follow-ups.
- **Session history is complementary, not primary.** Use it to surface mid-cycle work not yet in a release; don't treat session summaries as authoritative version data.
- **If no RELEASE_v*.md exists** (rare), fall back to `git log --oneline` between tags and summarize commit subject lines by category.
- **Feature age query:** Don't just search release notes — check git log directly with `--grep`. Features can land as post-release commits that won't appear in any RELEASE_*.md file.
- **LSP/doc-search pattern:** Use `--all` flag in git log when searching across branches — feature branches may not be merged to main yet at the time of searching, but the tag may exist on a different branch.

## References

- Sample output format from this session: See the assistant's reply delivering v0.12.0 release highlights + post-release fixes list.
- Sample feature age query from this session: "tell me about [lsp docs page] is this new?" — used git log --grep="lsp|LSP" across release boundaries.
- Release file pattern: `~/.hermes/hermes-agent/RELEASE_v*.md`
- Version command: `hermes --version` (wrapper → `~/.hermes/hermes-agent/venv/bin/hermes`)
- Git tag pattern: `vYYYY.M.D` (e.g., `v2026.4.30`) — date-based tags, not SemVer.
