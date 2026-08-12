# Skill Installation Patterns — Batch Profile Setup

When installing skills to profiles created with `--no-skills`, you need to discover where each skill actually lives, then copy it. This documents the patterns discovered during the 17-profile redesign (2026-06-12).

## `--no-skills` Behavior

`hermes profile create <name> --no-skills` does NOT create an empty profile. It still installs **bundled category directories** (apple, creative, data-science, devops, email, gaming, gifs, github, media, mlops, note-taking, productivity, research, smart-home, social-media, software-development, yuanbao, etc.) but with **no individual skills inside them** — just `DESCRIPTION.md` files.

Result: the profile's `skills/` dir has ~20-30 category subdirectories, but 0 actual skill content. This is the expected starting state for selective seeding.

## Skill Discovery Patterns

Skills live in 3 possible locations. Always check all three:

### 1. Root skills (`~/.hermes/skills/`)

Top-level skills and category directories. Structure:
```
~/.hermes/skills/
├── karpathy-guidelines/          ← top-level skill (SKILL.md + refs)
├── clean-code/                   ← top-level skill
├── blue-ocean-strategy/          ← top-level skill
├── creative/                     ← category directory
│   ├── architecture-diagram/     ← nested skill
│   ├── excalidraw/               ← nested skill
│   └── comfyui/                  ← nested skill
├── software-development/
│   ├── systematic-debugging/     ← nested skill
│   └── test-driven-development/  ← nested skill
├── mlops/                        ← DEEPER nesting
│   ├── inference/
│   │   ├── llama-cpp/            ← 2 levels deep
│   │   └── vllm/                 ← 2 levels deep
│   ├── training/
│   │   ├── axolotl/              ← 2 levels deep
│   │   └── unsloth/              ← 2 levels deep
│   └── huggingface-hub/          ← 1 level (skill is the dir itself)
└── Anthropic-Cybersecurity-Skills/
    └── skills/                   ← 754 skill dirs inside
        ├── analyzing-*/          ← individual skills
        └── ...
```

**Pitfall: Skills can be 2-3 levels deep.** The curation strategy document may list `mlops/llama-cpp` but the actual path is `mlops/inference/llama-cpp/`. Always `find` or `ls` the category directory before writing copy commands.

### 2. Existing profile skills

Skills already installed in other profiles (source profiles being replaced):
```
~/.hermes/profiles/oracle/skills/financial-markets/
├── oracle-aitrader/
├── oracle-market-intel/
└── oracle-tradingagents/
```

These are often the ONLY copy of profile-specific skills. The root `skills/` dir may not have them.

### 3. Senna's skills (coordinator dumping ground)

Senna accumulates skills from all domains. Many skills exist ONLY in senna's profile:
```
~/.hermes/profiles/senna/skills/
├── coding-size-limits/           ← not in root
├── debug-artifact-cleanup/       ← not in root
├── look-before-edit/             ← not in root
├── pre-commit-security-checklist/← not in root
├── social-media/build-in-public/ ← not in root
├── media/youtube-batch-extraction/← not in root
└── unreal-engine/ue-*/           ← 27 UE5 skills, not in root
```

## Discovery Script

Use this to find where a skill lives before copying:

```python
from hermes_tools import terminal

def find_skill(skill_name):
    """Find all locations of a skill across root and profiles."""
    result = terminal(
        f"find ~/.hermes/skills ~/.hermes/profiles/*/skills "
        f"-maxdepth 4 -type d -name '{skill_name}' 2>/dev/null"
    )
    locations = [l.strip() for l in result['output'].strip().split('\n') if l.strip()]
    return locations

# Example:
# find_skill("systematic-debugging")
# → ['~/.hermes/skills/software-development/systematic-debugging',
#    '~/.hermes/profiles/code/skills/software-development/systematic-debugging']
```

**Pitfall: `find` output can be garbled in `execute_code`.** The `find` command's output sometimes gets mangled when run inside `execute_code` scripts — line counts appear as `1F 1D:` prefixes instead of clean paths. Use `terminal()` directly for discovery commands, not `execute_code`.

## Batch Installation Pattern

For installing skills across many profiles, use a source mapping:

```python
from hermes_tools import terminal

PROFILES = "~/.hermes/profiles"
ROOT = "~/.hermes/skills"

def get_source(source_base, source_path):
    if source_base == "root":
        return f"{ROOT}/{source_path}"
    return f"{PROFILES}/{source_base}/skills/{source_path}"

# Install plan: target_profile -> [(source_base, source_path, target_path)]
install_plan = {
    "code": [
        ("root", "software-development/systematic-debugging", "software-development/systematic-debugging"),
        ("senna", "coding-size-limits", "coding-size-limits"),
        ("root", "github/codebase-inspection", "github/codebase-inspection"),
    ],
    # ... more profiles
}

for profile, skills in install_plan.items():
    copied, errors = 0, []
    for source_base, source_path, target_path in skills:
        src = get_source(source_base, source_path)
        dst = f"{PROFILES}/{profile}/skills/{target_path}"
        target_dir = "/".join(target_path.split("/")[:-1])
        result = terminal(
            f"mkdir -p '{PROFILES}/{profile}/skills/{target_dir}' && "
            f"cp -r '{src}' '{dst}' 2>&1"
        )
        if result['exit_code'] == 0:
            copied += 1
        else:
            errors.append(f"{target_path}: {result['output'][:100]}")
    print(f"{'✅' if not errors else '⚠️'} {profile}: {copied}/{len(skills)}")
```

## Anthropic Cybersecurity Skills (754)

Located at: `~/.hermes/skills/Anthropic-Cybersecurity-Skills/skills/`

Structure: flat directory with 754 individual skill directories. No categories in the metadata — all skills are at the same level.

For profiles that need these (cyber-red, cyber-blue):
```bash
# Copy entire set
cp -r ~/.hermes/skills/Anthropic-Cybersecurity-Skills/skills/ \
      ~/.hermes/profiles/cyber-red/skills/Anthropic-Cybersecurity-Skills/skills/
```

**Verification:** After copy, count should be ~755 (754 skills + the `skills/` dir itself).

**Pitfall: `maxdepth` filter affects skill counts.** When counting skills in cyber-red/cyber-blue, `find -maxdepth 2` shows only 6-7 directories because the Anthropic skills are nested deeper (inside `Anthropic-Cybersecurity-Skills/skills/`). Use `maxdepth 1` on the Anthropic skills subdirectory itself to get the real count (755).

## Nested Skill Paths (Common Gotchas)

| Expected Path | Actual Path | Why |
|---------------|-------------|-----|
| `mlops/llama-cpp` | `mlops/inference/llama-cpp` | Organized by function (inference/training/eval) |
| `mlops/axolotl` | `mlops/training/axolotl` | Same |
| `mlops/vllm` | `mlops/inference/vllm` | Same |
| `mlops/dspy` | `mlops/research/dspy` | Same |
| `mlops/audiocraft` | `mlops/models/audiocraft` | Same |
| `mlops/evaluating-llms-harness` | `mlops/evaluation/lm-evaluation-harness` | Different name + nested |
| `mlops/fine-tuning-with-trl` | `mlops/training/trl-fine-tuning` | Different name + nested |
| `github/github` | Does not exist | Category dir, not a skill |
| `github/git-master` | `senna/skills/github/git-master` | Only in senna's profile |
| `coding-size-limits` | `senna/skills/coding-size-limits` | Only in senna's profile |
| `safe-web-research` | `cyber-red/skills/red-teaming/safe-web-research` | Only in cyber-red's profile |

**Rule:** Never trust the curation strategy document's paths verbatim. Always verify with `find` or `ls` before writing copy commands.

## Magnus Skill Repo (git.brandyapple.com)

Skills from external repos (like Magnus's agent-skills) need to be installed via the `mcp_iknowkungfu_install_skill` tool or manually downloaded. They don't exist in the local skill tree until explicitly installed.

When evaluating external skills, check if the target profile already has an equivalent (e.g., Magnus's `systematic-debugging` vs the local version). Install the better version.

## Post-Installation Verification

After installing all skills for a profile:

```bash
# Count skill directories (excluding hidden dirs and DESCRIPTION.md)
find ~/.hermes/profiles/<name>/skills -maxdepth 2 -type d -not -name '.*' | wc -l

# Verify specific critical skills exist
ls ~/.hermes/profiles/<name>/skills/<category>/<skill-name>/

# Smoke test
hermes --profile <name> chat -q "What skills do you have?" -Q
```
