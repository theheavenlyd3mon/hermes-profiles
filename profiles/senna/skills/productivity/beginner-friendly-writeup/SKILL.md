---
name: beginner-friendly-writeup
description: Turn internal knowledge into clean, shareable guides for newcomers. Use when the user asks for a write-up, explainer, or guide that someone else will read — especially if they don't know the system.
triggers:
  - "write up for someone"
  - "explain this for someone new"
  - "make a guide"
  - "shareable doc"
  - "someone doesnt know how"
  - "beginner guide"
  - "how to explain"
---

# Beginner-Friendly Write-Up

Turn internal/complex knowledge into clean, shareable documents that work for someone who has never seen the system before.

## When to Use

- User asks for a "write up" or "guide" to share with others
- User says "for someone who doesn't know" or "for someone new"
- Converting internal documentation into public-facing content
- Creating onboarding materials

## The Methodology

### 1. Lead With Why

Don't start with setup steps. Start with what the reader gets out of it.

**Bad:** "First, create a directory at ~/Vault/."
**Good:** "Hermes agents accumulate knowledge across hundreds of sessions. Without a persistent store, that knowledge dies. Obsidian gives you a knowledge graph your agent reads and writes automatically."

The reader needs to care before they'll follow steps.

### 2. Big Picture Diagram (Early)

Within the first 3 sections, include a simple ASCII or text diagram showing how the pieces fit together. Readers need a mental model before they handle details.

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  Agent   │────▶│  Store   │────▶│  UI     │
└─────────┘     └─────────┘     └─────────┘
  does work       saves it        you see it
```

Label each box with what it DOES, not what it IS.

### 3. Numbered Steps With Exact Commands

Every step has:
- A clear action verb in the heading ("Create the vault", not "Vault creation")
- The exact command or file to create
- A copy-paste ready code block
- A "why" sentence after the code block

```bash
hermes profile create researcher
```

> This creates `~/.hermes/profiles/researcher/` with its own config, memory, and skills.

### 4. Copy-Paste Ready Content

If the reader needs to write a config file, SOUL.md, or schema — give them the FULL text they can paste. Don't describe what should go in it; hand them the document.

**Bad:** "Add a section about confidence levels to your SOUL.md."
**Good:** (full SOUL.md with confidence levels already written in)

### 5. Concrete Examples of Good vs Bad

Abstract advice doesn't stick. Show the difference:

**Bad approach (what chatbots do):**
> "Here are the top 10 tools according to [blog]..."

**Good approach (what the agent does):**
> "I searched GitHub stars, recent commits, and open issues. Tool A has 15K stars but 300 open issues. Tool B has 5K stars but active development..."

The reader immediately understands the methodology without you explaining it.

### 6. Strip Internal Specifics

Remove anything that's specific to YOUR setup:
- ❌ Your vault paths (`~/Hermes Vault/Hermes/icarus/`)
- ❌ Your agent names (`senna`, `foreman`, `researcher`)
- ❌ Your model choices (`deepseek-v4-pro`)
- ❌ Your channel IDs (`#research-lab`)
- ❌ Your team structure (10-agent team)
- ✅ Generic paths (`~/Hermes Vault/`)
- ✅ Role descriptions ("the research agent")
- ✅ Model categories ("cost-effective model" or "whatever you have access to")
- ✅ Generic channel names ("your research channel")

The reader should be able to substitute their own details without editing the structure.

### 7. Troubleshooting Table

End with a table of the 5-8 most common problems and their fixes. Pull these from real issues encountered during setup, not hypothetical ones.

| Problem | Fix |
|---------|-----|
| Agent doesn't write to vault | Check OBSIDIAN_VAULT_PATH is set |
| Entries not showing in Obsidian | Make sure FABRIC_DIR points INSIDE the vault |

### 8. Quick Reference Table

A scannable summary at the end — env vars, config values, directory conventions. Readers will come back to this table after the initial read.

| Variable | Example | Purpose |
|----------|---------|---------|
| `OBSIDIAN_VAULT_PATH` | `~/Hermes Vault` | Where the vault root is |

### 9. Progressive Disclosure

Structure the document so someone can stop at any section and have a working setup:

- **Steps 1-3:** Minimum viable setup (it works)
- **Steps 4-5:** Better setup (connected, persistent)
- **Step 6:** First test (verify it works)
- **Optional sections:** Advanced usage, customization

Don't front-load advanced concepts. Let the reader level up.

### 10. Closing Attribution

End with a one-liner linking back to the tool/platform. Keeps it professional and gives the reader a path to learn more.

---

## Document Template

```markdown
# Setting Up [Thing] in Hermes

> One-line pitch — what the reader gets.

---

## Why [Thing]?
2-3 sentences on the problem it solves.

## The Big Picture
ASCII diagram showing how pieces fit together.

## Step 1: [Action Verb]
Exact commands + copy-paste content.

## Step 2: [Action Verb]
...

(repeat for each step)

## Step N: First Run
How to verify everything works.

---

## [Optional] Advanced Usage
Customization, extensions, power-user features.

## Troubleshooting
| Problem | Fix |
|---------|-----|

## Quick Reference
| Item | Value | Purpose |
|------|-------|---------|

---

*Built with [Hermes Agent](https://hermes.nousresearch.com) by Nous Research.*
```

## Checklist Before Sharing

- [ ] Would someone with ZERO context understand this?
- [ ] Are all commands copy-paste ready?
- [ ] Are internal specifics stripped (paths, names, IDs)?
- [ ] Is there a big-picture diagram?
- [ ] Are there concrete good-vs-bad examples?
- [ ] Is there a troubleshooting table?
- [ ] Is there a quick reference table?
- [ ] Can the reader stop at any step and have a working setup?
- [ ] Does it lead with WHY, not HOW?

## Examples

Two guides produced with this methodology:
- `hermes-obsidian-setup-guide.md` — Obsidian as a second brain for Hermes
- `hermes-researcher-profile-guide.md` — Research agent profile and workflow

Both are on the Desktop, share-ready, zero internal references.
