# Code-Implementation Task Body Template

Use this structured format when creating kanban cards for **new features, components, or visual systems** — not fix/retry tasks or code reviews. The structure ensures the worker has clear scope, file boundaries, implementation constraints, and a concrete definition of done.

## Template

```markdown
**Workstream: <project-name-phase>**
**Task: <short task title>**
**Project:** <absolute-path-to-project>

<1-2 sentence description of what to build and why>

**Files:**
- Create: `<path/to/new/file>`
- Modify: `<path/to/existing/file>`
- (List all files that will be touched)

**Implementation:**
- <Specific implementation bullet. Numbered list preferred.>
- <Include visual/style constraints if relevant (color, glow, timing).>
- <Reference existing patterns or files the worker should study first.>
- <Include uniforms, parameters, or API contracts if known.>

**Verification:**
<Single clear criterion that proves the task is done. Not a test suite — a visual or behavioral check the developer does manually.>

**Test with headless commands only:**
<npm/pip/build command to verify no breakage>
<Note if testing requires manual browser open>
```

## Example (Three.js shader task)

```markdown
**Workstream: neon-approach-phase2**
**Task: T2.1 — Cruiser hull shader — Tron panel glow**
**Project:** ~/projects/neon-approach

Replace the cruiser's plain MeshStandardMaterial with a ShaderMaterial that adds neon panel-seam lines and subtle emissive grid pattern.

**Files:**
- Create: `src/shaders/hull.glsl.js`
- Modify: `src/ships.js`

**Implementation:**
- Vertex shader passes UV coordinates and world normal to fragment
- Fragment shader uses UV to draw grid lines (thin glowing lines at UV boundaries)
- Emissive color (cyan/blue) on grid lines, dark metallic base elsewhere
- Add time uniform for slow pulsing of the grid glow

**Verification:** Visual inspection in browser shows visible glowing panel lines in the intro/cruiser phases.

**Test with headless commands only:** `npx vite build` to verify build, open index.html in Chrome manually.
```

## Example (Python feature task)

```markdown
**Workstream: data-pipeline-metrics**
**Task: Add request latency histogram to monitoring endpoint**
**Project:** /home/user/projects/data-pipeline

Add a Prometheus histogram metric tracking request latency across all API endpoints.

**Files:**
- Create: `src/monitoring/metrics.py`
- Modify: `src/api/middleware.py`
- Modify: `src/config/defaults.py`

**Implementation:**
- Use prometheus_client Histogram with buckets [0.01, 0.05, 0.1, 0.5, 1, 5, 10]
- Label by endpoint path and HTTP method
- Middleware wraps each request, records duration on response
- Default config flag `metrics.enabled: true` in config
- Expose /metrics endpoint on port 9090

**Verification:** Hit /metrics endpoint — verify latency histogram appears with endpoint labels.

**Test:** `pytest tests/test_monitoring.py -v`
```

## When to use this template

Use for any task that is:
- Building a new feature, component, or visual system
- Adding a new file or module
- Implementing something from a spec, plan, or design doc
- A self-contained piece of work with clear file boundaries

Do **not** use for:
- Fix/retry tasks (use the retry-cycle body convention instead)
- Code review tasks (use the review body convention instead)
- Research tasks (use the research scoping template instead)