# Skill Audit & Profile Design Workflow

**When to use:** Redesigning the fleet's profile architecture. Auditing all skills across the installation. Categorizing skills by domain. Designing new profiles for uncovered skill clusters.

## The Problem

Profiles accumulate over time. Skills get copy-pasted across profiles. 70-80% of each profile's skills are duplicated. The coordinator (senna) becomes a dumping ground. Specialized profiles carry irrelevant skills (spotify, teams-meeting-pipeline, airtable on every profile). Context windows waste tokens loading skills that will never be used.

## Phase 1: Full Skill Inventory

### 1a. Root skills (shared across all profiles)

```bash
# Count all skills in root (excluding archive and large collections)
find ~/.hermes/skills/ -name "SKILL.md" -not -path "*/.archive/*" -not -path "*/Anthropic-*" | wc -l

# List by category
for dir in ~/.hermes/skills/*/; do
  name=$(basename "$dir")
  count=$(find "$dir" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "$name: $count"
done

# Check for large collections that load into every context window
find ~/.hermes/skills/ -maxdepth 1 -type d | while read d; do
  count=$(find "$d" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
  [ "$count" -gt 20 ] && echo "$(basename "$d"): $count skills ← REVIEW"
done
```

### 1b. Per-profile skills

```bash
for profile in ~/.hermes/profiles/*/; do
  name=$(basename "$profile")
  active=$(find "$profile/skills/" -name "SKILL.md" -not -path "*/.archive/*" 2>/dev/null | wc -l | tr -d ' ')
  archived=$(find "$profile/skills/.archive/" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "$name: $active active, $archived archived"
done
```

### 1c. Identify duplicates

```bash
# Find skills that appear in 3+ profiles
for profile in ~/.hermes/profiles/*/; do
  find "$profile/skills/" -name "SKILL.md" -not -path "*/.archive/*" 2>/dev/null
done | sed 's|.*/skills/||' | sort | uniq -c | sort -rn | head -30
```

### 1d. Read each skill's metadata

For each unique skill, read the first 20 lines to extract name, description, and triggers:
```bash
head -20 ~/.hermes/profiles/<name>/skills/<category>/<skill>/SKILL.md
```

**Batch approach for large collections (100+ skills):** Use a subagent to read SKILL.md headers in parallel. Group by filename pattern first (e.g., `analyzing-*-malware*` → malware analysis), then read only the ambiguous ones.

## Phase 2: Categorize by Domain

Group skills into natural domains. Look for:

1. **Directory structure** — skills already organized by category (`creative/`, `github/`, `mlops/`)
2. **Filename patterns** — `analyzing-*-forensics*` → forensics, `performing-*-pentest*` → pen testing
3. **Trigger keywords** — read SKILL.md frontmatter `triggers:` field
4. **Functional grouping** — what does this skill DO? Write code? Analyze data? Generate images?

### Output: Categorized inventory

Write a markdown file with:
- Category name
- Skill count
- Skill names with one-line descriptions
- Summary table

## Phase 3: Design Profile Architecture

### Principles

1. **Domain-based, not role-based** — "code" (all coding work) not "coder" + "debugger" + "reviewer" (three profiles doing the same thing)
2. **Every skill gets a home** — no skill left in the coordinator dumping ground
3. **Minimal overlap** — a skill belongs in ONE profile, not copy-pasted across five
4. **Right-sized** — profiles with <3 skills should be merged into related profiles
5. **No context pollution** — don't load 754 cybersecurity skills into a trading bot's context window

### Profile design process

1. List all skill categories from Phase 2
2. For each category, ask: "Does this warrant its own profile, or should it merge with a related one?"
3. Merge rule: if two categories share >50% of their use cases, merge them
4. Split rule: if one category has >100 skills, consider splitting by sub-domain
5. Create mock profiles with skill lists
6. Map existing profiles to new profiles (what merges, what splits, what renames)

### Common patterns

| Pattern | Example | Action |
|---------|---------|--------|
| **Role overlap** | coder + debugger + reviewer | Merge into "code" |
| **Dumping ground** | senna has 213 skills | Extract domain skills to dedicated profiles |
| **Massive collection** | 754 Anthropic cybersecurity | Split into sub-domains (cyber-red, cyber-blue) |
| **Knowledge skills** | 33 book/strategy .md files | Group into "business" profile |
| **Stale skills** | teams-meeting-pipeline on every profile | Move to single "communication" profile or archive |
| **Tiny profiles** | homelab (2 skills) | Merge into related profile (infra) or keep if distinct |

## Phase 4: Implementation

After the design is approved:

1. **Create new profiles** — `hermes profile create <name>`
2. **Merge profiles** — copy skills from source profiles to target, delete sources
3. **Relocate skills** — move skills from senna/root to correct profiles
4. **Strip external_dirs** — set `external_dirs: []` on specialized profiles to stop loading root skills
5. **Update SOUL.md** — rewrite each profile's persona to match its new domain
6. **Verify** — smoke test each profile

## Pitfalls

- **Don't skip the audit.** You can't redesign what you haven't measured. The audit reveals the real overlap.
- **Large collections hide in root.** The Anthropic Cybersecurity collection (754 skills) was loading into every profile's context window because it sat in `~/.hermes/skills/`. Nobody noticed until we audited.
- **external_dirs is a sledgehammer.** It loads EVERYTHING from the directory. For specialized profiles, use `skills.paths` (explicit per-skill) instead.
- **Profile rename ≠ profile create.** Renaming a profile requires creating a new one, migrating config/skills/SOUL.md, and deleting the old one. There's no `hermes profile rename`.
- **The user wants to see everything before deciding.** Don't start implementing changes mid-audit. Present the full inventory, get approval, then execute.
