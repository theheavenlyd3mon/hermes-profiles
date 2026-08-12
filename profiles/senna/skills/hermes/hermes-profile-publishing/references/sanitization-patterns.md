# Sanitization Patterns — Real-World Reference

Proven sed patterns and grep verification commands from the hermes-profiles repo build (2026-06-15).

## Pass 1: Home Directory Paths

```bash
find profiles -name '*.md' -type f -exec sed -i '' \
  -e 's|~|~|g' \
  -e 's|~|~|g' \
  {} \;
```

Catches: absolute paths in code examples, config snippets, installation instructions.

## Pass 2: Username in Text

```bash
find profiles -name '*.md' -type f -exec sed -i '' \
  -e 's|`<user>`|`<user>`|g' \
  -e 's|of the |of the |g' \
  -e 's|MAIN ACCOUNT (<user>)|MAIN ACCOUNT (<user>)|g' \
  -e 's|agent:<user>|agent:<user>|g' \
  -e 's|agent-<user>|agent-<user>|g' \
  {} \;
```

Catches: username appearing in prose, code comments, variable names.

## Pass 3: Context-Specific (Manual Review)

These patterns vary per user and can't be automated:
- GitHub usernames: `<your-github-username>` → `<your-github-username>`
- Project paths: `~/Unreal-Engine-Obsidian` → `~/obsidian-vault`
- Discord server IDs: `discord.gg/XXXXX` → `discord.gg/<server>`
- Hardware: `your GPU` → `your GPU` or remove
- Specific vault paths: `~/Documents/YouTube-Transcripts/` → `~/documents/transcripts/`

## Pass 4: Verification

```bash
# Check for remaining personal references
grep -r '<actual-username>' profiles/ --include='*.md' -l

# Check for hardcoded paths (excluding generic placeholders)
grep -rn '/Users/' profiles/ --include='*.md' | grep -v '<you>\|<user>\|name/\|\*/'

# Check for Discord references
grep -r 'discord\.gg/\|discord\.com/channels' profiles/ --include='*.md'

# Check for hardware-specific references
grep -rn 'RTX\|4070\|4080\|4090\|3080\|3090' profiles/ --include='*.md'
```

Expected result: all commands return empty or only generic placeholders.

## Patterns to PRESERVE

These look personal but are already generic — don't "fix" them:
- `/Users/$USER/` — shell variable, correct
- `/Users/<you>/` — generic placeholder in templates
- `/Users/name/` — generic example
- `/Users/*/` — glob pattern in find/ls examples
- `/mnt/evidence/Users/*/` — forensic skill example

## Pitfall: Python str.replace() is Unreliable for This

Python `str.replace()` fails on:
- Varying whitespace around paths
- Partial path matches (`~` vs `~/.hermes`)
- Case variations
- Multi-line patterns

**Always use `sed` for bulk cleanup.** It handles regex, character classes, and line-level matching. Use Python only for the initial file listing and counting, not for the actual text replacement.

## Stats from hermes-profiles Build (2026-06-15)

- 500 .md files scanned across 16 profiles
- 40 files needed path cleanup (pass 1 — sed)
- 22 files still had references after pass 1 (username in prose, not paths)
- 3 files needed targeted sed pass (MAIN ACCOUNT, agent:username patterns)
- Final grep: 0 personal references remaining
- 50 skills removed from public senna (apple/*, unreal-engine/*, game-dev/*, notion-*, yuanbao, dogfood, iknowkungfu-contrib)
- 2 skills removed from public code (hermes-s6-container-supervision, debugging-hermes-tui-commands)
- 162 Anthropic Cybersecurity Skills included under Apache 2.0
- Total: 693 files, ~660 skills committed
