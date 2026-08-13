# Step 4: Storyboard

Design per-scene visual layout, assign component templates, and plan transitions. Read [design-system.md](../design-system.md) for visual tokens.

## Global Direction

```
Format: 1920x1080
Audio: narration.wav (Mandarin TTS voiceover)
Style: Aurora Scholar (aurora mesh aesthetic, see design-system.md)
Theme: aurora-scholar | chinese-elegant | lavender-soft | mint-fresh | warm-art
Transition: Use transitions between every scene. No jump cuts.
```

**Theme** selects the background visual from design-system.md "Background Theme Catalog". Default is `aurora-scholar` (blue ripple texture). Pick based on problem category — see the Theme Selection Guide below. All scenes in one video share the same theme.

## Scene-Component Mapping

Map each section from `SCRIPT.md` to a visual component from [math-components.md](math-components.md):

| Scene ID | Script Section | Component | Notes |
|----------|---------------|-----------|-------|
| scene-title | 标题开场 | Title Opening (C7) | Cinematic title with particles, gradient text |
| scene-problem | 开场引入 + 题目朗读 | Problem Card (C1) | Glass panel with 3D tilt, KaTeX equation |
| scene-analysis | 思路分析 | Formula Panel (C3, single row) | Highlight approach, step indicator enters |
| scene-step-1 | 解题步骤一 | Formula Panel (C3) | First equation row active |
| scene-step-2 | 解题步骤二 | Formula Panel (C3) | Second row enters, first dims |
| scene-step-N | 解题步骤N | Formula Panel (C3) | Continue pattern |
| scene-geometry | (if applicable) | Geometry Canvas (C5) | SVG drawing animation |
| scene-equipment | 实验器材 | Equipment Cards (C8) | 5-card row with highlight cycling |
| scene-procedure | 操作流程 | Operation Flow (C9) | Step bar + SVG stage choreography |
| scene-wiring | 电路连接操作 | Circuit Wiring Operation (C12) | Rectangular loop wiring with step indicator |
| scene-meters | 连接电表 | Circuit Wiring Operation (C12) | Meter insertion into existing rectangular loop |
| scene-principle | 原理讲解 | Principle Diagram (C11) | Dual-panel: SVG diagram + explanation blocks |
| scene-comparison | 对比/要点 | Comparison Panel (C10) | Side-by-side correct vs incorrect |
| scene-conclusion | 结论总结 | Conclusion Panel (C6) | Green accent, answer emphasis |

### Problem Type Guidance

| Problem Type | Recommended Scene Flow | Min Scenes |
|---|---|---|
| Algebra | Problem Card → Formula Panel (all steps in one panel) → Conclusion | 4-5 |
| Geometry | Problem Card → Geometry Canvas (draw figure) → Formula Panel (calculations) → Conclusion | 5-6 |
| Word Problem | Problem Card → Analysis Panel (model setup) → Formula Panel (solve) → Conclusion | 5-6 |
| Calculus | Problem Card → Formula Panel (setup) → Formula Panel (compute) → Conclusion | 4-5 |
| Chemistry Experiment | Title Opening → Problem Card → Principle Diagram → Equipment Cards → Operation Flow → Results Display → Comparison Panel → Conclusion | 7-8 |
| Physics Experiment | Title Opening → Problem Card → Principle Diagram → Equipment Cards → Operation Flow → Conclusion | 6-8 |
| Physics Circuit (电路题) | Title Opening → Problem Card → Principle Diagram (C11, circuit schematic) → Circuit Wiring Operation (C12, wire main loop) → Circuit Wiring Operation (C12, connect meters) → Conclusion | 6-8 |
| Physics Concept | Title Opening → Problem Card → Principle Diagram → Formula Panel → Conclusion | 5-6 |

**Scene Count Rule:** For experiment-type problems, generate **7-8 scenes minimum**. The visual variety from multiple component types (cards, flow panels, comparison panels, SVG diagrams) creates significantly more engaging videos than reusing the same template repeatedly. For conceptual/math problems, 5-6 scenes. More scenes with distinct visual languages = better engagement.

**One concept per scene (一个场景一个概念 — 稳定复现的关键).** Give each distinct idea its OWN scene: e.g. for a lens ray-tracing problem make a separate scene for the setup/principle AND one scene per special ray (`scene-ray1` 平行于主轴, `scene-ray2` 过焦点, `scene-ray3` 过光心) AND one for verifying the image point — do NOT merge them into a single `scene-optics`. Merging is the #1 cause of under-rendered, half-blank scenes and of the same problem looking great one run and broken the next.

**Coverage contract (Step 5 will be checked against this).** List EVERY scene below with its own `### Scene: <scene-id>` heading. Step 5 must build exactly one `dist/compositions/<scene-id>.html` per heading and wire each into `index.html`. The pre-render gate `scripts/check_scene_coverage.py` fails the render if fewer compositions are wired than scenes planned here, so plan the scene list deliberately and then build all of it.

## Per-Scene Direction Template

For each scene, specify:

```markdown
### Scene: [scene-id]
- **VO cue:** [which narration lines play during this scene]
- **Start:** [timestamp from transcript mapping]
- **Duration:** [seconds]
- **Component:** [from math-components.md]
- **Background theme:** [from Global Direction — typically omit if same as video-wide theme; only specify if overriding per-scene]
- **Aurora palette:** [from design-system.md scene-aurora-palette — e.g., "indigo + violet + cyan" for problem scenes; use the theme-specific palette if a non-default theme is selected]
- **Content:**
  - Equation: [LaTeX source]
  - Text: [Chinese text content]
- **Layout:** [center / left-right split / full-width]
- **Entrance:** [describe animation — e.g., "panel rises from bottom with 3D rotation"]
- **Continuous motion:** [what moves throughout the scene — e.g., "electrons flow along wire left→right, H₂ bubbles rise from copper surface, ions drift in solution". Use "none" only for static text/equation scenes. See design-system.md Continuous Motion Patterns]
- **Highlight:** [what gets emphasized during this scene — e.g., "step 2 border glows cyan"]
- **Transition to next:** [type — e.g., crossfade 0.5s]
```

### Aurora Palette Selection Guide

Pick a different aurora palette for each scene to create visual variety. Recommended mapping:

| Scene Type | Aurora Palette | Why |
|---|---|---|
| Title Opening | indigo + violet + cyan (`title` palette) | Cinematic first impression with premium feel |
| Intro / Problem | indigo + violet + cyan | Most visually striking — sets a premium first impression |
| Analysis / Derivation | violet + indigo + pink | Rich warm tones convey depth and complexity |
| Solution steps (odd) | cyan + indigo + teal | Cool tones keep focus on equations |
| Solution steps (even) | indigo (lighter) + cyan + violet | Subtle palette alternation prevents visual monotony |
| Equipment showcase | cyan + indigo + emerald (`experiment` palette) | Cool scientific tones for apparatus display |
| Operation procedure | cyan + indigo + emerald (`experiment` palette) | Consistent with equipment scene for continuity |
| Science principle | violet + cyan + indigo (`principle` palette) | Purple/cyan evokes energy levels and physics |
| Comparison / Reminder | amber + indigo + red (`comparison` palette) | Warm warning tones for correct/incorrect contrast |
| Conclusion | emerald + teal + cyan | Distinctive green accent marks the ending |

For videos with many step scenes, alternate between the step palettes. Each scene's aurora orb colors are defined in its own CSS — see design-system.md "Background Treatment" for the exact gradient values.

### Theme Selection Guide

Pick a background theme based on the problem's subject area. The theme applies to the entire video (all scenes share the same background treatment). Set it in the Global Direction block above.

| Problem Category | Theme | Visual Feel |
|---|---|---|
| General / mixed / default | `aurora-scholar` | Blue ripple wave + indigo/violet/cyan aurora — premium tech-educational |
| Geometry, proofs, constructions | `chinese-elegant` | Lake-blue gradient + teal/cyan orbs — serene, precise |
| Algebra, equations, functions | `lavender-soft` | Pale lavender gradient + purple orbs — gentle, focused |
| Statistics, probability, data | `mint-fresh` | Mint-green gradient + emerald/teal orbs — fresh, clean |
| Elementary arithmetic, fractions | `warm-art` | Cream-yellow gradient + golden/amber orbs — warm, friendly |
| Physics, chemistry, experiments | `aurora-scholar` | Default aurora mesh suits science-lab aesthetic |

When uncertain, use `aurora-scholar` — it works well for all problem types.

**Continuous Motion Rule:** Any scene depicting a physical/chemical process (reaction, circuit, flow, experiment) MUST specify at least one continuously moving element. Static diagrams of dynamic processes are visually incorrect and make the video feel like a slideshow.

## Project File Structure

Each platform job has its own isolated working directory. All artifacts go in the working directory root, HyperFrames project goes in `dist/`.

```
./
├── ANALYSIS.md              # Problem analysis
├── SCRIPT.md                # Teaching script
├── narration.wav            # TTS audio (copied into dist/)
├── transcript.json          # Sentence-level timestamps (copied into dist/)
├── STORYBOARD.md            # This storyboard document
└── dist/
    ├── index.html           # Root composition
    ├── narration.wav        # TTS audio
    ├── transcript.json      # Sentence-level timestamps
    └── compositions/
        ├── scene-problem.html   # Problem display
        ├── scene-step-1.html    # Solution step 1
        ├── scene-step-2.html    # Solution step 2 (add more as needed)
        └── scene-conclusion.html # Final answer
```

## Transition Guidelines

- **Between content scenes:** Use crossfade (0.4-0.6s) as default
- **Problem → first step:** Slightly longer transition (0.6-0.8s) to mark the shift from problem to solution
- **Last step → conclusion:** Use a distinctive transition to mark finality
- Follow the hyperframes non-negotiable rule: entrance animations only (no exit animations), the transition handles scene exits
- Final scene may fade elements out

## Timing Guidelines

- Allow **0.3s** before first narration for scene entrance animation
- Allow **0.5s** after last narration word for visual settling
- Scene overlap (for transitions): subtract transition duration from the gap between scenes
- Total video duration = last scene end + 1.0s buffer

## Gate

Before proceeding to Step 5:
- [ ] `STORYBOARD.md` exists with per-scene direction
- [ ] Every scene has: component type, content, layout, entrance animation, transition
- [ ] Timestamps from Step 3 are applied to scene starts and durations
- [ ] File structure planned
