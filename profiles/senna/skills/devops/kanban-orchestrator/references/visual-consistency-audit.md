# Visual Consistency Audit (Manim / Generated Video)

## When to Use

When a user produces rendered video output (Manim, After Effects, HTML5, etc.) and some scenes don't match the visual language of a reference scene. Dispatch as a dependency chain: creative visual spec → code implementation.

## Workflow

```
Creative (audit reference vs incorrect → produce spec)
  ↓ complete (writes visual-spec.md to project dir)
Code (read spec → apply fixes to rendering code)
```

### Phase 1 — Creative: Visual Spec

Assign to a `creative` profile with `manim-video` skill loaded (or equivalent visual-design skill).

**Task body structure:**
- List the reference screenshot path (the "correct" scene)
- List each incorrect scene screenshot path
- Describe the reference visual language in detail (panel fill colors, border colors/widths, checkmark placement, text alignment, font sizes, stroke widths)
- For each incorrect scene, describe what's different from reference
- Deliverable: write a structured `visual-spec.md` to the project directory

**Key tool for creative:** `vision_analyze` on each screenshot to extract exact element positions, colors, and styling.

### Phase 2 — Code: Apply Fixes

Assign to a `code` profile with the rendering skill loaded (e.g. `manim-video`). Gate behind the creative task via `--parent`.

**Task body structure:**
- Read visual-spec.md first
- Reference the correct scene's rendering code for patterns to replicate
- Make targeted changes — don't rewrite scenes entirely, just adjust styling
- Do NOT change animation sequences or timing — only visual styling (fill colors, border colors/widths, checkmark addition, text alignment)
- Output: git diff + per-scene summary of changes

### Example Task Graph

```bash
hermes kanban create "creative: visual spec — compare Scenes 1-4 against reference" \
  --assignee creative \
  --body "<detailed spec task body>" \
  --workspace "dir:/path/to/project"

hermes kanban create "code: apply visual spec — fix scenes" \
  --assignee code \
  --body "<fix task body>" \
  --workspace "dir:/path/to/project" \
  --parent t_<creative_task_id>
```

### Pitfall: `--skill` flag fails when skill isn't in the orchestrator's profile index

The kanban dispatcher resolves `--skill` from the **orchestrator's profile** (the profile running `hermes kanban create`), not from the assignee's profile. A skill that exists on disk at `~/.hermes/skills/<category>/<name>/` or `~/.hermes/profiles/<assignee>/skills/` but isn't indexed in the orchestrator's skill registry will crash the worker at launch with:

```
Error: Unknown skill(s): <skill-name>
```

The worker exits immediately (`exit_code 1`) and the task blocks with `nonzero_exit(1)`. Even adding a comment telling the worker to read the skill from disk won't help — the crash happens before the agent loop starts.

**Recovery:** Omit `--skill` entirely. Embed the skill's key patterns (color palettes, typography, layout templates) directly in the task body, or instruct the worker to read the skill file from disk via `terminal cat ~/.hermes/skills/<category>/<skill-name>/SKILL.md`.

**Prevention:** Before using `--skill`, verify the skill exists in the orchestrator's index:
```bash
hermes skills list | grep <skill-name>
```
If empty, install it first: `hermes skills install <skill-name>`
