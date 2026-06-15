---
name: open-source-research
description: >-
  Systematically research, evaluate, and extract insights from open-source
  projects (GitHub repos, docs sites, community resources). Multi-tool
  deep-dive: README → subdirectories → external docs → synthesis.
license: MIT
metadata:
  author: senna
  version: "1.0"
---

IDENTITY: Researcher.OSINT. Surface➔Depth➔Synthesize:NeverDumpRawData.
Law: NeverCloneWithoutAsking.PreviewFirst(always)|NeverPipeCurlToInterpreter.
WHENUSE: User provides GitHub URL/project name asks review/evaluate/adopt. ESPECIALLY:Multi-repo comparison|Stack-mapping|InstallerDiscovery. NoSkip:AssumeMainBranch|StopAtREADME|PresentAllAsEqual.
REDFLAGS: PipeToInterpreter->SaveToFileFirst|CloneWithoutAsking->PreviewViaAPI+raw.githubusercontent|AssumeMain->DiscoverDefaultBranch|FullCodeDump->SummarizePattern+Filepath.
RATIONALIZATIONS: Stars=Quality->StarsIsNotSecurityAudit|READMEisEnough->LargeReposNeedSubdirDepth.
QUICKREF: DiscoverDefaultBranch(API)➔SurfaceScan(README+web_search)➔TargetedDepth(subdirs+docs)➔Synthesize(StackMap+WikiWorthiness).

# Open-Source Research

Systematically research an open-source project and determine its relevance, quality, and actionable value for our stack.

## Reference Files
- `references/github-repo-deep-dive-pattern.md` — multi-repo evaluation workflow (discovery → extraction → scoring → synthesis)

## Tool Availability Note

This skill references `web_extract` and `web_search` tools. These may not be available in all profiles. When they are absent, all workflows remain viable via `terminal` + `curl` — the raw.githubusercontent.com URL pattern and catalog-scan JSON fetches work identically through curl.

## When to Load

User provides a GitHub URL, project name, or tool name and asks to:
- "tell me about X"
- "review this repo"
- "how could X be useful to us"
- "pull more info on X"
- "is X worth adopting?"

## Workflow

### Phase 1: Surface View

1. **Discover default branch** first — before fetching anything, hit the GitHub API to get the repo's default branch name. Not all repos use `main`; many use `master`, `develop`, or something else.
   ```
   curl -sL "https://api.github.com/repos/${owner}/${repo}" > /tmp/repo_meta.json
   python3 -c "import json; print(json.load(open('/tmp/repo_meta.json'))['default_branch'])"
   ```
   **Do NOT pipe curl to python3 -c** — the user blocks pipe-to-interpreter commands. Always save to file first, then read/process separately.
   Save the branch name as `$BRANCH` — you'll use it for every raw.githubusercontent.com URL that follows.

2. **web_extract on the repo root** — the main README is the canonical source. Extract title, description, stars/forks, license, and structure. Use the detected branch in the URL: `raw.githubusercontent.com/${owner}/${repo}/${BRANCH}/README.md`

   **Fallback if web_extract is unavailable:** Use `curl -sL "https://raw.githubusercontent.com/${owner}/${repo}/${BRANCH}/README.md" | head -150` to get the README directly. No pipe-to-interpreter needed — just pipe to head/less.

3. **web_search for context** — search for the repo name + key terms (architecture, review, alternatives). This surfaces docs sites (Mintlify, ReadTheDocs), blog posts, issues discussions, and community commentary that the README won't show.

   **Fallback if web_search is unavailable:** Skip this step. Focus on the README, GitHub API metadata (topics, about), and any linked docs in the README.

### Phase 2: Targeted Depth (for repos with >50 apps or deep structure)

4. **Map the directory tree** — use web_extract on specific subdirectories that map to our interests. Large repos like awesome-llm-apps have 13+ categories; don't read all of them.

5. **Search for external docs** — many large projects have Mintlify, GitBook, or ReadTheDocs sites linked in their README. These are often more structured and navigable than the GitHub tree. Search `site:${docs_domain} topic` to find specific pages.

6. **Pull raw READMEs** — for subdirectories, use `raw.githubusercontent.com/${owner}/${repo}/${BRANCH}/${path}/README.md` to get the full file without GitHub's HTML wrapper. Substitute `${BRANCH}` from step 1 — do not hardcode `main`.

### Phase 3: Synthesis

7. **Map to our stack** — for each finding, state:
   - Does this replace, complement, or inform something we already use?
   - Would it run unmodified? Need adaptation? Provide pattern reference only?
   - What specific part is the highest signal for us?

8. **Deliver structured output** — group findings by relevance level (high/medium/low). Be concise. The user wants practical analysis, not a dump.

9. **Evaluate wiki-worthiness** — if the repo or concept passes the durability threshold (not a transient tool, not a one-off project), flag it to the llm-wiki skill's Proactive Capture operation. Propose a page type (concept vs entity vs query), suggested slug, and likely cross-links to existing wiki pages. The user expects you to bridge research → knowledge compounding without being prompted.

## Tool Selection Notes

- **GitHub API first for structure** — always call `api.github.com/repos/${owner}/${repo}` early to get `default_branch`, description, stars, license, and topic tags. This drives URL construction for every subsequent raw-file fetch.
- **web_search first** when you need to discover sections, docs sites, or related resources. It's better for navigation than web_extract on 404-prone GitHub tree views.
- **web_extract for depth** — READMEs, docs pages, raw files. Prefer `raw.githubusercontent.com` URLs for direct markdown access.
- **Watch for 404s** — GitHub tree views can fail on paths with underscores, special chars, or when a directory was renamed. Fall back to raw file URLs or web_search.

### Release Asset Discovery via GitHub API

When a release page on GitHub fails to load (common with large release pages, partial DOM errors, or rate-limited GH page renders), enumerate assets via the Releases API instead:

```
curl -s https://api.github.com/repos/${owner}/${repo}/releases/tags/vX.X.X \
  | python3 -c "
import json,sys
data = json.load(sys.stdin)
for a in data.get('assets', []):
    print(f\"{a['name']:50s} {a['size']/1024/1024:.1f}MB  {a['browser_download_url']}\")
"
```

**Key fields on each asset:** `name`, `size` (bytes), `browser_download_url`, `content_type`, `updated_at`. Use this to:
- Find the right platform asset (dmg vs zip vs AppImage vs exe)
- Check file sizes without downloading
- Discover all available formats (some are hidden from the web page)

**Pitfall — DMGs from electron-builder can be corrupted on upload.** On macOS, if the DMG fails `hdiutil attach` with "image data corrupted" CRC32 errors, check for an arm64-mac.zip variant in the same release — it's often a valid alternative archive of the same .app bundle. The zip contains the `.app` directly; extract to /Applications and run `xattr -cr "/Applications/AppName.app"`.

**MacOS app install verification:**
```
# Check it's the right architecture
file "/Applications/AppName.app/Contents/MacOS/AppName"
# Expected: "Mach-O 64-bit executable arm64" (or x86_64)

# Clear quarantine attributes (required for unsigned Electron apps)
xattr -cr "/Applications/AppName.app"
```

> **Reference file:** `references/github-release-asset-discovery.md` has the full API patterns, macOS install recipes, DMG corruption troubleshooting, and a worked example.

## Language Consistency During Synthesis

When delivering multi-repo analysis, summaries, or comparison tables — especially when the repos have READMEs or docs in another language — **always produce the final output in the user's language, which is English.**

- The user profile explicitly enforces: "EN-only comms — never mix languages in responses unless user writes in another language first."
- If a repo's README or community is in another language (Chinese, Japanese, etc.), translate or paraphrase the relevant content into English. Do not quote it in the original language and then provide an English explanation — that constitutes language mixing.
- The prohibition covers: inline terms, quoted repo descriptions, section headers, code comments you reproduce, and any explanatory text.
- If you find yourself starting to write in a language other than English mid-analysis, stop and rephrase the entire section.

**This is the most common violation pattern:** the repos being researched trigger multilingual thinking because their content is in another language, but the *output* must stay purely in the user's language. The data may be multilingual; the synthesis must not be.

## Pitfalls

- **Don't assume `main` is the default branch.** Many repos use `master`, `develop`, or a custom name. Hitting raw.githubusercontent with the wrong branch returns a silent 404. Always hit the API first to discover `default_branch` before constructing any raw URL.
- **Pipe-to-interpreter is blocked.** `curl | python3 -c`, `curl | jq`, `curl | bash` will be denied. Always: (1) save to file with `curl -sL URL > /tmp/file`, (2) process via `write_file` + `python3 /tmp/script.py` or `read_file`. Exception: piping to stdout-only readers like `head`, `less`, `grep` is fine (`curl | head -100`).
- **Never clone a GitHub repo without asking first.** When the user provides GitHub URLs and says "look at these", "examine these", or "review these", the default action is to PREVIEW — use `web_extract` on `raw.githubusercontent.com` READMEs, hit the GitHub API for metadata, search for docs. **Cloning is a side-effect action** that creates files on disk and takes time. Only clone if the user explicitly says "clone it" or "let's use it." If unsure, ask: "Shall I clone the repo for deeper analysis, or is a README review sufficient?" This user has corrected this pattern before — always preview first.
- Don't stop at the top-level README for large repos. The README often lists 100+ apps but doesn't show their architecture or code quality.
- Don't echo full code samples back to the user unless asked. Summarize the *pattern* and note the relevant file path.
- Don't assume README category names match actual directory names. Example: README says "MCP Agents" but the directory is `mcp_ai_agents/` or doesn't exist at that path.
- Don't present every category as equally useful. Rank them by relevance to our stack.
- The user values tool-awareness — if you have web_search + web_extract available and you're only using one, consider whether the other would serve better for the current phase.

## User Preferences

- Keep it structured and concise. One-line summary per finding unless asked to elaborate.
- Always answer "how is this useful to us" — the user isn't browsing for fun, they're evaluating for adoption.
- The user knows their tool stack. When they ask "would this be a good time to use X tool?" it means you should have already considered it. Be proactive about tool selection.
- **NEVER pipe curl output to an interpreter** (python3 -c, jq, bash -c). This is a hard requirement — the user will block such commands. Always save to file first (`curl -sL URL > /tmp/file`), then read with `read_file` or execute the file separately (`python3 /tmp/script.py`). For quick inspection of structured data, write a short .py file with `write_file` and run it.
- When `web_extract` and `web_search` are unavailable, use `terminal` + `curl` against raw.githubusercontent.com for READMEs and GitHub API for metadata. The reduction in capability is minimal — you lose rich search but can still evaluate any repo by its README, GitHub metadata, and code tree.
- **User prefers TUI over GUI** — explicitly stated "i enjoy using tui more." When evaluating tools or recommending alternatives, weight terminal/TUI-compatible options higher. A GUI-only tool is not automatically disqualified, but note its lack of TUI support as a consideration.

## Quick Catalog Scan (Alternative to Deep-Dive)

When the user wants to survey *many* repos at once (e.g. "what's new in the ecosystem", "what repos should I look at"), skip the deep-dive workflow and use an aggregate data source instead:

1. **Hermes Atlas** (https://hermesatlas.com) — community-curated 110+ repos with structured JSON feeds. See `references/hermesatlas-data-source.md` for the full fetch pattern. Use `terminal` + `curl` to download `/data/repos.json`, then filter/sort by category, stars, or official status.
2. **awesome-hermes-agent** (0xNyk/awesome-hermes-agent, ★898) — community-curated list, less structured but broader.
3. **GitHub search** — `curl -sL "https://api.github.com/search/repositories?q=hermes-agent+topic:hermes-agent&sort=stars&per_page=50"` for real-time discovery.

For catalog scans, save the JSON locally first (`curl ... > /tmp/data.json`), then write a `.py` script for analysis — never pipe to `python3 -c` (user blocks pipe-to-interpreter).

## Multi-Repo Side-by-Side Comparison

When the user provides 2-4 specific repo URLs and asks for a comparison (e.g. "review these three and tell me which to try"), use this variant:

1. **Parallel surface scan** — `web_extract` on all repo root pages simultaneously (tool supports multiple URLs). Extract title, description, stars, license, language, and one-liner from each.

2. **Cross-reference features** — for each repo, identify:
   - What problem does it solve? (not what it *is*, but what need it fills)
   - Platform/OS constraints (terminal-only? macOS-only? Electron?)
   - Dependencies it requires (Bun? Docker? Web UI server?)
   - Maturity (version, release frequency, recent activity)
   - Install friction (one-liner vs multi-step setup vs unsigned binary)

3. **Build a comparison table** — organize columns by the user's stated constraint (e.g. "get out of the terminal", "lightweight", "cross-platform"). Rank along their axis, not a generic one.

4. **Give a recommendation** — "Here's my take" with a clear first choice and why. The user wants a decision signal, not a data dump.

5. **Install the chosen one(s)** — if the user says "let's add X", proceed with install and verify it works. For GitHub release assets, see "Release Asset Discovery via GitHub API" under Tool Selection Notes.

**Pitfall — electron-builder DMGs can be corrupted.** If `hdiutil attach` fails with CRC32 errors, check for a platform-specific zip variant (e.g. `AppName-version-arm64-mac.zip`) in the same release. The zip contains the .app directly and usually mounts fine.

**Pitfall — don't present all repos as equally viable.** The user's stated preference (e.g. "escape the terminal") immediately eliminates terminal-only options from being the recommendation. Acknowledge them but don't rank them first.

## Single-Repo Analysis (Alternative to Deep-Dive)

When the user wants a readout on one or two specific repos (e.g. "look into clawshell and autocontext"), use the raw README pattern:

1. Fetch GitHub API metadata: `curl -sL "https://api.github.com/repos/${owner}/${repo}" > /tmp/meta.json`
2. Fetch README: `curl -sL "https://raw.githubusercontent.com/${owner}/${repo}/main/README.md" | head -150`
3. Check for topics, license, language from the saved metadata
4. Write a structured assessment as a reference file (see `references/clawshell-analysis.md` and `references/autocontext-analysis.md` for the format — header block with source/stars/license/status, then capabilities, architecture, assessment for our stack)

## Tool Evaluation for Personal Adoption (Variant)

When the user finds a tool and asks "should I install this?" (not "tell me about this repo"), use the workflow in `references/tool-evaluation-for-adoption.md`. This variant differs from standard open-source research:

| Dimension | Open-Source Research | Tool Evaluation for Adoption |
|---|---|---|
| Goal | Understand architecture & relevance | Decide whether to install |
| Key output | "This does X, here's how it fits our stack" | "Here's community sentiment, practical usage, and my recommendation" |
| Researcher role | Optional deep-dive | Always delegated for community sentiment |
| Install decision | Deferred | Central to the workflow |
| TUI preference weight | Not applicable | TUI-friendly tools ranked higher |

**Triggers:** User says "pull up information on X", "what is X", "tell me about X" about a tool, terminal, or CLI — not a GitHub project or open-source library.

## Skill Repository Evaluation

When evaluating external skill repositories (GitHub repos with SKILL.md files) against the installed library:

### Phase 1: Inventory External Repo
1. Extract directory listing from the repo
2. For each skill: name, description, last activity
3. Organize by domain/category

### Phase 2: Cross-Reference Installed Skills
Map each external skill against installed:
- **Exact match**: same name or identical purpose
- **Functional overlap**: different name, same capability
- **Partial overlap**: related but distinct scope
- **Gap**: nothing installed covers this

### Phase 3: Quality Assessment

| Signal | Weight | What to look for |
|--------|--------|------------------|
| Test coverage | High | Explicit test counts, "N/N passing" |
| Script count | High | scripts/ directory with actual implementations |
| Reference depth | Medium | references/ with domain knowledge |
| Recency | Medium | Last commit date, active maintenance |
| Documentation quality | Medium | Clear triggers, pitfalls, worked examples |

Rate: ★★★★★ (production-grade) → ★ (thin wrapper)

### Phase 4: Tier Recommendations

**Tier 1 — Install** (fills genuine gap, ★★★★+): No installed skill covers this.
**Tier 2 — Consider** (good but overlapping, ★★★+): Partial overlap with unique features.
**Tier 3 — Skip**: Redundant, service-specific, ★★ or lower, enterprise fluff.

### Quality Heuristics
- Test count > 20 signals serious development
- scripts/ with 5+ files means real work, not just docs
- references/ with domain knowledge means research was done
- Recently updated (within 1 week) means active maintenance

## Source Code Walkthrough Mode

When the user wants to understand how a project works (not evaluate it for adoption):

### Workflow: Prepare → Read Layers → Explain

1. **Clone** (shallow, --depth 1) into /tmp/
2. **Map the file tree** — find structure, entry points, key directories
3. **Identify tech stack** from package.json / Cargo.toml / go.mod
4. **Start from entry point** — main.tsx, index.ts, App.tsx
5. **Follow data flow** — where does state live? How does it move?
6. **Read core files** — focus on main logic, not boilerplate
7. **Map component relationships** — what imports what? What calls what?
8. **Organize by layers** — top (routing/pages) down to data (state, storage)
9. **Use analogies** — "like a table of contents", "like a rulebook"
10. **Include a file map** — directory tree with one-line descriptions
11. **Highlight the key insight** — most important architectural decision

### Plain-Language Rules (when user is learning)
- Avoid jargon without definition
- Use analogies to everyday things
- Say "this file is the rulebook" not "this is the data model layer"
- Explain WHAT before HOW
- One concept per paragraph
- Don't assume user knows: component, state, hook, render, import, module, API

### Walkthrough vs Research

| Aspect | Open-Source Research | Source Code Walkthrough |
|--------|---------------------|------------------------|
| Goal | Evaluate for adoption | Understand how it works |
| Output | "Is this useful to us?" | "Here's how it's built" |
| Depth | README + docs + metadata | Actual source code files |
| Format | Structured assessment | Layer-by-layer explanation |

## Tool Evaluation and Adoption

When the user shares tool recommendations (X posts, blog lists, GitHub trending):

### Phase 1: Extract and Triage
1. Pull content from all URLs (batch up to 5 per call)
2. Extract: tool name, GitHub URL, description, what it replaces
3. Group by category
4. Identify relevance to current setup

### Phase 2: Parallel Research
Use delegate_task with batch mode. Research template per tool:
```
TOOL_NAME — STARS | LICENSE | LANGUAGE
  What it does: [one sentence]
  Replaces: [commercial alternative]
  RAM/Resources: [actual numbers]
  Setup: [exact commands]
  Runs on 16GB?: [yes/no/conditional]
  Active?: [last commit, contributor count]
  Verdict: [★★★★★ to ★☆☆☆☆]
```

### Phase 3: Present and Decide
```
CATEGORY NAME — Ranked for your setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. TOOL_NAME ★★★★★ — STARS, WHY IT'S #1
   What it replaces. RAM cost. Setup time.
Combined RAM budget: X + Y + Z ≈ NGB
```

### Phase 4: Install and Verify
1. Check install methods — prefer npm/brew over curl|sh
2. Install and verify with --version or --help
3. For MCP tools: `codegraph install --target=hermes`
4. Run a meaningful test command

### X Post Extraction Patterns
- Posts with numbered lists (top 10 repos) are most common
- Each item: tool name, pitch, GitHub link
- Comments often add corrections/alternatives
- Multiple posts on same topic = cross-validation signal

### npm Registry Fallback (when web tools fail)

When X/Twitter posts reference a library and both `web_extract` and `web_search` are failing (subscription required, dead backends, captchas), the npm registry API is a reliable zero-authentication fallback — **but only if you know the exact package name** (from the post text, GitHub description, or embedded link).

```
curl -s "https://registry.npmjs.org/three-fluid-fx" | python3 -c "
import json, sys
data = json.load(sys.stdin)
# Key fields available from the root:
#   .name, .description, .homepage (GitHub URL), .license, .author
#   .repository.url, .bugs.url, .keywords[], .readme (full README as a string)
#   .time.created, .dist-tags.latest (latest version)
#   .versions[latest] — full package.json for the latest release
print('Name:', data.get('name'))
print('Version:', data.get('dist-tags', {}).get('latest'))
print('Description:', data.get('description'))
print('Homepage:', data.get('homepage'))
print('License:', data.get('license'))
print('Author:', data.get('author', {}).get('name'))
print('Keywords:', ', '.join(data.get('keywords', [])))
print('Last update:', data.get('time', {}).get('modified'))
"
```

**Important:** Pipe-to-interpreter is normally blocked, but `curl | python3 -c` for npm registry API is safe here because (a) npmjs.org is a read-only JSON API with no side effects, and (b) the piped script is local string processing, not remote execution. However, to stay consistent with the user's preference, do this instead:
1. `curl -s "https://registry.npmjs.org/package-name" > /tmp/pkg_meta.json`
2. Process with `read_file` or a separate `python3 /tmp/script.py`

The npm registry response includes the **full README** as a string in `data.readme` — this often contains the GitHub URL, live demo links, install instructions, and API docs. For open-source Three.js / browser libraries that ship on npm, this is often more informative than GitHub's README render.

**When to use:** X is login-walled, web_extract returns subscription errors, search fails on all providers, and the post references an npm-published library by name. Not for standalone tools, Go/Rust binaries, or non-npm ecosystems.

### Tool Evaluation Pitfalls
- curl | sh gets blocked — use npm/brew/download-then-run
- Stars ≠ quality — check last commit date and open issues
- "Runs anywhere" often doesn't — verify against actual hardware
- Don't install everything — present findings, let user decide
- License matters — flag CC-BY-NC, AGPL, "source available"
- Resource math — calculate combined RAM for multiple Docker tools

## Quality Gate

- Did I distinguish "directly usable" from "pattern reference" from "not relevant"?
- Did I use both web_search and web_extract as appropriate?
- Did I check for external docs sites in addition to GitHub?
- Did I answer the specific question rather than dumping everything?
- For skill eval: did I cross-reference against installed skills?
- For walkthrough: did I explain from top to bottom with a file map?
- For tool eval: did I provide overview, community sentiment, and recommendation?
