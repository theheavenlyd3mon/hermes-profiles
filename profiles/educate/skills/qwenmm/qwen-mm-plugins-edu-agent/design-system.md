# Aurora Scholar Design System

Aurora mesh aesthetic for math tutorial videos. Animated gradient orb backgrounds with vivid indigo/violet/cyan accent colors, solid opaque panels (depth via borders + layered shadow, NO `backdrop-filter`, NO translucency — never frosted glass), and ambient drift effects.

## Tokens

```yaml
name: Aurora Scholar
mood: Aurora, precise, educational — animated mesh gradient aesthetic

colors:
  bg-primary: "#f8fafc"
  bg-surface: "#f1f5f9"
  bg-glass: "#ffffff"   # OPAQUE panel background (was translucent — translucency causes 毛玻璃遮挡; depth via border+shadow, never backdrop-filter)
  text-primary: "#0f172a"
  text-secondary: "#64748b"
  text-dim: "#94a3b8"
  accent-indigo: "#6366f1"
  accent-violet: "#8b5cf6"
  accent-cyan: "#06b6d4"
  success: "#10b981"
  warning: "#d97706"
  error: "#dc2626"
  border-glow: "rgba(99, 102, 241, 0.2)"
  border-subtle: "rgba(15, 23, 42, 0.06)"

typography:
  headline:
    family: '"Noto Sans SC", Inter, sans-serif'   # CJK-first — headings are often Chinese
    size: 72px
    weight: 700
  subhead:
    family: '"Noto Sans SC", Inter, sans-serif'
    size: 42px
    weight: 600
  body:
    family: '"Noto Sans SC", Inter, sans-serif'
    size: 28px
    weight: 400
  math:
    family: KaTeX_Main
    size: 48px
  label:
    family: '"Noto Sans SC", Inter, sans-serif'
    size: 18px
    weight: 600
    transform: uppercase
    spacing: 0.12em
  chinese:
    family: '"Noto Sans SC", Inter, sans-serif'   # self-hosted; NEVER Inter-only, NEVER a CDN font / PingFang SC
    weight: 400

corners:
  sm: 8px
  md: 16px
  lg: 24px

spacing:
  xs: 8px
  sm: 16px
  md: 32px
  lg: 64px

motion:
  easing:
    entry: "power3.out"
    exit: "power2.in"
    ambient: "sine.inOut"
    emphasis: "back.out(1.4)"
  duration:
    fast: 0.3
    normal: 0.6
    slow: 1.0
    ambient: 2.5
```

## Font Embedding (Offline — Mandatory)

Rendered in an air-gapped sandbox with no CJK system font. The font files are shipped with this skill under `assets/fonts/` and MUST be copied into `dist/assets/fonts/` and embedded via an inline `@font-face` `<style>` in `index.html`'s `<head>` (see [step-6](references/step-6-compose-render.md)). Use a CJK-first stack everywhere; never `Inter, sans-serif` alone, never Google Fonts / any CDN, never `PingFang SC` (absent from the sandbox).

```css
@font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-Bold.woff2") format("woff2"); font-weight:400 700; font-display:swap; }
@font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-ExtraBold.woff2") format("woff2"); font-weight:800; font-display:swap; }
@font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-Black.woff2") format("woff2"); font-weight:900; font-display:swap; }
@font-face { font-family:"Inter"; src:url("./assets/fonts/Inter-Variable.woff2") format("woff2"); font-weight:100 900; font-display:swap; }
@font-face { font-family:"JetBrains Mono"; src:url("./assets/fonts/JetBrainsMono-Bold.woff2") format("woff2"); font-weight:700; font-display:swap; }
html, body { font-family:"Noto Sans SC", Inter, sans-serif; }
```

Only Noto Sans SC weights 700/800/900 are shipped; body weight 400 maps onto the 700 face. KaTeX is likewise self-hosted in `dist/katex/` (see step-5/step-6).

## Content Panel (Base Component Style — Solid & Opaque)

Every content panel uses this pattern (class name stays `.glass-panel` for compatibility, but it is OPAQUE — no glass):

```css
.glass-panel {
  background: #ffffff;


  border: 1px solid rgba(99, 102, 241, 0.3);
  border-top: 2px solid rgba(99, 102, 241, 0.25);
  border-radius: 20px;
  box-shadow:
    0 4px 16px rgba(99, 102, 241, 0.08),
    0 16px 48px rgba(99, 102, 241, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  padding: 48px;
}
```

**Result:** solid-white panel over aurora mesh with layered indigo shadow + inset top highlight — clean, modern, and premium (opaque, never see-through; no `backdrop-filter`).

## Problem Card Style

Glass panel with subtle 3D perspective:

```css
.problem-card-wrapper {
  perspective: 1200px;
}
.problem-card {
  /* extends .glass-panel */
  transform: rotateY(-3deg) rotateX(2deg);
  padding: 56px 64px;
}
.problem-card .label {
  font-family: Inter, "Noto Sans SC", sans-serif;
  font-size: 18px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #6366f1;
  margin-bottom: 24px;
}
.problem-card .problem-text {
  font-family: "Noto Sans SC", "PingFang SC", sans-serif;
  font-size: 36px;
  color: #0f172a;
  line-height: 1.6;
}
```

## Formula Row Style

```css
.formula-row {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 24px;
  border-radius: 12px;
  border: 1px solid transparent;
  transition: border-color 0.3s;
}
.formula-row.active {
  border-color: rgba(99, 102, 241, 0.5);
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.1);
}
.formula-row.dimmed {
  opacity: 0.5;
}
.step-badge {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: Inter, "Noto Sans SC", sans-serif;
  font-weight: 700;
  font-size: 18px;
  color: #fff;
  flex-shrink: 0;
}
```

## Video-Scale Sizing Rules

All elements render at **1920×1080**. Web-scale sizes look paper-thin in video. Apply these minimums:

```yaml
video-minimums:
  svg-stroke-width: 3          # strokes < 3px vanish on video
  svg-element-min-width: 30px  # rects, plates, bars — never thinner than 30px
  svg-element-min-height: 30px
  particle-radius: 14px        # ions, electrons, bubbles — minimum radius
  annotation-font-size: 20px   # labels inside SVG
  body-font-size: 28px         # any readable body text
  icon-min-size: 40px          # any icon or badge
```

**Rule of thumb:** if an element is smaller than 30px in either dimension, it will be invisible or unreadable in the rendered video. Scale it up or add a glow halo.

## Particle & Ion Style

Small moving elements (ions, electrons, bubbles) need **glow halos** to be visible and look polished on light backgrounds. A bare circle without glow looks flat and amateurish in the final video.

```css
/* CSS particles */
.particle {
  min-width: 28px;
  min-height: 28px;
  border-radius: 50%;
  box-shadow: 0 0 12px currentColor;
}
```

SVG equivalent — always apply the glow filter:

```xml
<defs>
  <filter id="glow">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>
<!-- Minimum r=14, always with filter -->
<circle r="14" fill="#6366f1" filter="url(#glow)"/>
```

## Geometry Canvas Style

```css
.geometry-canvas {
  /* extends .glass-panel */
  padding: 32px;
  position: relative;
}
.geometry-canvas svg {
  width: 100%;
  height: 100%;
}
.geometry-canvas .grid-bg {
  stroke: rgba(30, 41, 59, 0.04);
  stroke-width: 1;
}
.geometry-canvas .shape-primary {
  stroke: #06b6d4;
  stroke-width: 3;
  fill: none;
}
.geometry-canvas .shape-derived {
  stroke: #8b5cf6;
  stroke-width: 2;
  fill: none;
  stroke-dasharray: 8 4;
}
.geometry-canvas .shape-answer {
  stroke: #10b981;
  stroke-width: 3;
  fill: rgba(16, 185, 129, 0.1);
}
.geometry-canvas .geo-label {
  font-family: "KaTeX_Main";
  font-size: 24px;
  fill: #0f172a;
}
```

## Step Indicator Style

```css
.step-indicator {
  display: flex;
  align-items: center;
  gap: 0;
}
.step-node {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: Inter, "Noto Sans SC", sans-serif;
  font-weight: 700;
  font-size: 16px;
  color: #94a3b8;
}
.step-node.active {
  background: #6366f1;
  border-color: #6366f1;
  color: #fff;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
  transform: scale(1.15);
}
.step-node.completed {
  background: #6366f1;
  border-color: #6366f1;
  color: #fff;
}
.step-connector {
  width: 60px;
  height: 2px;
  background: #94a3b8;
}
.step-connector.filled {
  background: #6366f1;
}
```

## Conclusion Panel Style

```css
.conclusion-panel {
  /* extends .glass-panel */
  border-color: rgba(16, 185, 129, 0.3);
  box-shadow: 0 1px 2px rgba(0,0,0,0.03), 0 4px 12px rgba(16,185,129,0.06), 0 16px 40px rgba(16,185,129,0.08);
}
.answer-box {
  border: 2px solid #10b981;
  border-radius: 12px;
  padding: 24px 40px;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.12);
  text-align: center;
}
```

## SVG Diagram Stage

For scenes that contain SVG-based diagrams (atom models, equipment illustrations, operation stages), use a dedicated stage container. The stage provides a subtle background that separates the SVG content from the aurora mesh.

```css
.svg-stage {
  background: rgba(230, 240, 255, 0.4);
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: 12px;
  padding: 10px;
  position: relative;
  overflow: hidden;
}
```

### SVG Authoring Rules

- Always use `viewBox` for scalable SVG — never fixed `width`/`height` in px on the `<svg>` element
- Use `<defs>` for reusable glow filters:
  ```xml
  <defs>
    <filter id="rayGlow"><feGaussianBlur stdDeviation="3" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="bigGlow"><feGaussianBlur stdDeviation="6" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  ```
- Minimum `stroke-width`: 3 for primary shapes, 2 for secondary
- Minimum circle `r`: 14px (with glow filter applied)
- **NEVER apply a glow/blur `filter` to an axis-aligned `<line>`** (force arrow, axis, horizontal/vertical ray, wire, tick). A horizontal/vertical line has a zero-area bounding box, and a default `objectBoundingBox` filter region collapses to nothing → the line and its `marker-end` arrowhead become **completely invisible** (only its `<text>` label shows — "有力的字没有力的线条"). Force arrows use a solid `stroke` (4–6) + marker and **no filter**; if a glow is required on straight strokes, make it absolute: `filterUnits="userSpaceOnUse" x="0" y="0" width="<vbW>" height="<vbH>"`. Glow filters are safe on circles/particles/text (non-degenerate bbox). Enforced by `scripts/check_svg_filter_bbox.py`.
- Label text in SVG: `font-size: 20px` minimum, use `font-family: "Noto Sans SC"` for Chinese
- **Labels must not overlap each other (标签禁止相互重叠)** — keep a clear gap of **≥ ~1 label-height** between any two SVG `<text>` boxes. Never stack a center/fulcrum label and its arm/segment labels on the same line: put the center label ABOVE the line and the arm labels BELOW (anchored `end` on the left, `start` on the right, pushed outward past the shape edge). Offset a label perpendicular to the line it names, stagger point labels that share an axis, and never let a point label bury an axis tick number. Enforced by `scripts/check_svg_label_overlap.py` (SKILL.md Rule #28).
- **Labels must not overlap the drawing (标签禁止压在图形上 / 文字不压线不压点)** — a letter (A/B/O/F/M…) must never sit ON a line, axis, curve, or vertex dot; it must be **offset OUTWARD, away from the figure, by ~18–24 units**. Rules: (a) a **point/vertex** label goes on the side pointing away from the shape centre (e.g. triangle vertex → outward from the centroid), never at the exact point coordinate; place a small dot at the point and the letter ~20u beside it. (b) a **point on an axis** gets its label just **above or below the axis** (not on it) — for a point on the x-axis, put the letter ~22u below; for the origin `O`, offset it into a quadrant (e.g. `x-14, y+20`), not onto the crossing. (c) a label near a **symmetry axis / vertical line** must clear that line's x — anchor it `end` and push left (or `start` and push right) so the stroke doesn't cut through the glyphs. (d) a **curve** label sits in the empty region beside the curve, not on it. It's fine to nudge a label a little to clear the figure. Enforced by `scripts/check_svg_label_on_figure.py`.
- **Node-and-connector diagrams (关系图/流程图/循环图 — 方框 + 箭头 + 图形内标签).** When you draw a food chain, feedback loop, or flow diagram from SVG boxes/circles and arrows, follow these or the diagram reads as broken (箭头和方框重叠 / 白字消失). Enforced by `scripts/check_svg_node_graph.py`.
  - **A label that sits INSIDE a shape MUST be in the SAME `<g>` as that shape** — `<g id="core"><circle .../><text .../><text .../></g>`, never the shape and its `<text>` as independent siblings. If they are separate, any transform on the shape (a GSAP `scale`/pulse, `back.out` overshoot, or `svgOrigin` residue) moves the shape but not the label, so the label **slides off the shape onto the light panel and vanishes** (this is the classic "白色文字没显示" bug: white `负反馈` drifting off its purple circle onto the white card). Grouping makes shape + label transform as one unit, exactly like the node boxes that render correctly. Animate/position the **group**, not the shape alone.
  - **White SVG `<text>` is allowed ONLY inside a dark shape that fully contains it.** White-on-light is invisible; the design system otherwise forbids `#ffffff` text (see *Light Theme Text Color Rule*). The only sanctioned white text is a label centered in a dark chip/circle/badge — and per the rule above it must be grouped with that dark shape. Size the shape big enough that the text fits with margin (a two-line label needs radius ≈ `1.6 × font-size` or more).
  - **Arrow/connector endpoints must stop ≥ ~10u BEFORE the target box edge** — never let a `<line>`/`<path>` that carries `marker-end` end inside or flush against a `<rect>` node, or the arrowhead hides under / pokes into the 方框. Compute the endpoint from the box edge minus a gap (e.g. box left = 670 → arrow `x2 = 660`, not `668`), and account for the arrowhead length (`markerWidth`) on top of that gap.
  - **Edge labels ("取食"/"捕食"/…) belong in the GAP between boxes, not against a box** — center the label at the midpoint of the connector with clearance from both boxes; don't let its text box touch a node rect.
  - **Space the boxes for the connectors** — leave a gap of at least `2 ×` the arrowhead length + label width between adjacent boxes so the connector + its label + both clearances fit without crowding.
- For movable objects, wrap in `<g>` groups with `transform="translate(x,y)"` and animate via GSAP `x`/`y` or `attr`
- Color coding: primary objects in indigo (`#6366f1`) / cyan (`#06b6d4`), derived/auxiliary in violet (`#8b5cf6`), results/answers in green (`#10b981`), warnings in amber (`#d97706`)

## Comparison Panel Style

For scenes comparing correct vs incorrect approaches (e.g., with/without cobalt glass filter).

```css
.compare-container {
  display: flex;
  gap: 40px;
  align-items: stretch;
}
.compare-panel {
  flex: 1;
  /* extends .glass-panel */
  padding: 32px;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
}
.compare-panel.left-panel {
  border-color: rgba(220, 38, 38, 0.25);
  box-shadow: 0 4px 20px rgba(220, 38, 38, 0.06);
}
.compare-panel.right-panel {
  border-color: rgba(16, 185, 129, 0.25);
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.06);
}
.compare-divider {
  width: 2px;
  background: repeating-linear-gradient(
    to bottom,
    rgba(15, 23, 42, 0.15) 0px,
    rgba(15, 23, 42, 0.15) 8px,
    transparent 8px,
    transparent 16px
  );
  align-self: stretch;
}
.result-bad {
  background: rgba(220, 38, 38, 0.06);
  border: 2px solid rgba(220, 38, 38, 0.4);
  border-radius: 12px;
  padding: 12px 24px;
  color: #dc2626;
  font-weight: 700;
  font-size: 28px;
  text-align: center;
}
.result-good {
  background: rgba(16, 185, 129, 0.06);
  border: 2px solid rgba(16, 185, 129, 0.4);
  border-radius: 12px;
  padding: 12px 24px;
  color: #10b981;
  font-weight: 700;
  font-size: 28px;
  text-align: center;
}
```

## Warning Bar Style

Used for highlighting important caution notes, key reminders, or distinction callouts (e.g., "物理变化 · NOT 化学反应").

```css
.warning-bar {
  background: rgba(217, 119, 6, 0.06);
  border: 2px solid rgba(217, 119, 6, 0.35);
  border-radius: 14px;
  padding: 12px 28px;
  color: #d97706;
  font-weight: 700;
  font-size: 26px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
```

## Title Opening Style

Cinematic full-screen title scene with decorative SVG particle layer, gradient text, and floating watermark symbols.

```css
.title-container {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}
.title-eyebrow {
  font-family: Inter, "Noto Sans SC", sans-serif;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 6px;
  text-transform: uppercase;
  color: #6366f1;
  opacity: 0.7;
  margin-bottom: 20px;
}
/* ⚠️ Gradient text (background-clip:text + -webkit-text-fill-color:transparent) is for PLAIN-TEXT titles ONLY.
   NEVER apply it to an element that holds a KaTeX formula: the glyphs become transparent and only the
   fraction bar (a CSS border) survives, so the equation shows as a stray horizontal dash. Formulas use a solid color. */
.title-main {
  font-family: "Noto Sans SC", sans-serif;
  font-size: 96px;
  font-weight: 900;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 40%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: none;
  filter: drop-shadow(0 4px 20px rgba(99, 102, 241, 0.25));
  line-height: 1.2;
}
.title-subtitle {
  font-family: "Noto Sans SC", sans-serif;
  font-size: 32px;
  font-weight: 400;
  color: #475569;
  margin-top: 16px;
}
.title-underline {
  width: 0;
  height: 4px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
  border-radius: 2px;
  margin-top: 20px;
}

/* Floating watermark symbols (element symbols, math symbols, etc.) */
.watermark-symbol {
  position: absolute;
  font-family: Inter, serif;
  font-size: 96px;
  font-weight: 900;
  color: rgba(99, 102, 241, 0.05);
  pointer-events: none;
  user-select: none;
  z-index: 1;
}

/* SVG particle layer */
.particle-layer {
  position: absolute;
  inset: 0;
  z-index: 5;
  pointer-events: none;
}
.particle-layer circle {
  fill: rgba(99, 102, 241, 0.3);
  filter: url(#rayGlow);
}
```

### Title GSAP Patterns

```js
// Character-by-character entrance with back.out easing
var chars = document.querySelectorAll(".title-char");
tl.fromTo(chars, { opacity: 0, y: 60, scale: 0.6 },
  { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "back.out(1.4)", stagger: 0.08 }, 0.5);

// Underline sweep
tl.fromTo(".title-underline", { width: 0 },
  { width: 320, duration: 0.8, ease: "power2.out" }, 1.5);

// Particle burst (radial expansion + fade)
tl.fromTo(".particle-layer circle",
  { attr: { r: 0 }, opacity: 0.6 },
  { attr: { r: 12 }, opacity: 0, duration: 2.5, ease: "power1.out",
    stagger: { each: 0.03, from: "center" } }, 0.2);

// Watermark symbol drift
tl.fromTo(".watermark-symbol",
  { y: 0 }, { y: -30, duration: 4, ease: "sine.inOut", yoyo: true, repeat: R(4) }, 0);
```

## Equipment Card Style

For scenes showcasing experiment equipment with SVG illustrations.

```css
.equipment-row {
  display: flex;
  gap: 28px;
  width: 100%;
}
.equipment-card {
  flex: 1;
  /* extends .glass-panel */
  padding: 24px 16px;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  transition: border-color 0.3s, opacity 0.3s;
}
.equipment-card.active {
  border-color: rgba(99, 102, 241, 0.65);
  box-shadow: 0 0 24px rgba(99, 102, 241, 0.15);
}
.equipment-card.dimmed {
  opacity: 0.55;
}
.equipment-card .card-name {
  font-family: "Noto Sans SC", sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
}
.equipment-card .card-role {
  font-family: "Noto Sans SC", sans-serif;
  font-size: 18px;
  color: #64748b;
}
```

## Operation Stage Style

For scenes demonstrating multi-step procedures with an animated SVG stage.

```css
.operation-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 20px;
}
.operation-top {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.status-bar {
  /* extends .glass-panel */
  padding: 12px 32px;
  border-radius: 14px;
  font-family: "Noto Sans SC", sans-serif;
  font-size: 26px;
  font-weight: 600;
  color: #0f172a;
  text-align: center;
  min-width: 500px;
}
.operation-stage {
  flex: 1;
  /* extends .svg-stage */
  display: flex;
  align-items: center;
  justify-content: center;
}
.step-char {
  font-family: "Noto Sans SC", sans-serif;
  font-size: 28px;
  font-weight: 700;
}
```

## Science Principle Diagram Style

Dual-panel layout for science principle explanations with SVG diagram + text blocks.

```css
.principle-layout {
  display: flex;
  gap: 40px;
  align-items: stretch;
  height: 100%;
}
.principle-diagram {
  flex: 1.2;
  /* extends .svg-stage */
  display: flex;
  align-items: center;
  justify-content: center;
}
.principle-explanations {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  justify-content: center;
}
.explanation-block {
  /* extends .glass-panel */
  padding: 24px 28px;
  border-radius: 16px;
  border-left: 4px solid #6366f1;
}
.explanation-block .block-number {
  font-family: "Noto Sans SC", Inter, sans-serif;  /* CJK-first: this eyebrow often holds Chinese (对称性/题目所给) → must include Noto Sans SC or it renders as 豆腐块 */
  font-size: 22px;
  font-weight: 800;
  color: #6366f1;
  margin-bottom: 8px;
}
.explanation-block .block-title {
  font-family: "Noto Sans SC", sans-serif;
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}
.explanation-block .block-desc {
  font-family: "Noto Sans SC", sans-serif;
  font-size: 20px;
  color: #475569;
  line-height: 1.5;
}
```

## Background Treatment: Textured Aurora Mesh

Every scene uses a **blurred texture + animated aurora mesh gradient** background. A soft concrete/plaster texture image provides organic warmth, while 3 large, heavily-blurred CSS gradient orbs drift slowly on top. This creates a premium, tactile feel with cinematic depth.

### Background Layer Stack (bottom to top)

1. **Texture image** — full-bleed wave pattern photo (`bg-texture.jpg`) providing organic, non-flat surface
2. **Aurora orbs** — 3 absolutely-positioned radial-gradient divs with `filter: blur(80px)`, creating vivid color washes

### Scene Aurora Palette

Each scene type uses different orb colors for visual variety:

```yaml
scene-aurora-palette:
  intro/problem:
    a1: "rgba(99,102,241,0.5)"     # indigo
    a2: "rgba(139,92,246,0.4)"     # violet
    a3: "rgba(6,182,212,0.35)"     # cyan
  derivation:
    a1: "rgba(139,92,246,0.5)"     # violet
    a2: "rgba(99,102,241,0.4)"     # indigo
    a3: "rgba(236,72,153,0.3)"     # pink
  geometry:
    a1: "rgba(6,182,212,0.5)"      # cyan
    a2: "rgba(99,102,241,0.4)"     # indigo
    a3: "rgba(20,184,166,0.35)"    # teal
  steps:
    a1: "rgba(99,102,241,0.45)"    # indigo
    a2: "rgba(6,182,212,0.35)"     # cyan
    a3: "rgba(139,92,246,0.3)"     # violet
  conclusion:
    a1: "rgba(16,185,129,0.5)"     # emerald
    a2: "rgba(20,184,166,0.4)"     # teal
    a3: "rgba(6,182,212,0.35)"     # cyan
  experiment:
    a1: "rgba(6,182,212,0.45)"     # cyan
    a2: "rgba(99,102,241,0.35)"    # indigo
    a3: "rgba(16,185,129,0.3)"     # emerald
  comparison:
    a1: "rgba(217,119,6,0.4)"      # amber
    a2: "rgba(99,102,241,0.35)"    # indigo
    a3: "rgba(220,38,38,0.25)"     # red (subtle)
  principle:
    a1: "rgba(139,92,246,0.45)"    # violet
    a2: "rgba(6,182,212,0.35)"     # cyan
    a3: "rgba(99,102,241,0.3)"     # indigo
  title:
    a1: "rgba(99,102,241,0.55)"    # indigo (strong)
    a2: "rgba(139,92,246,0.45)"    # violet
    a3: "rgba(6,182,212,0.35)"     # cyan
```

### Texture Asset

The texture image `bg-texture.jpg` is located in the skill's `assets/backgrounds/` directory. During project setup (Step 5), copy it to `dist/bg-texture.jpg`. Compositions reference it as `../bg-texture.jpg` (relative to `dist/compositions/`).

### CSS Implementation

```css
.scene-bg {
  position: absolute;
  inset: 0;
}

/* Wave texture background — no blur, the image is already smooth */
.bg-texture {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: url('../bg-texture.jpg') center/cover no-repeat;
}

/* Aurora gradient orbs */
.aurora-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}
.a1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(99,102,241,0.5) 0%, transparent 70%);
  top: -10%; right: -5%;
}
.a2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(139,92,246,0.4) 0%, transparent 70%);
  bottom: -15%; left: -5%;
}
.a3 {
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(6,182,212,0.35) 0%, transparent 70%);
  top: 40%; left: 50%;
}

/* Grid lines — omitted; textured background provides sufficient structure */
```

### HTML Template

```html
<div class="scene-bg">
  <div class="bg-texture"></div>
  <div class="aurora-orb a1"></div>
  <div class="aurora-orb a2"></div>
  <div class="aurora-orb a3"></div>
</div>
```

### Important Notes

- **Always include `.bg-texture`** as the first child of `.scene-bg` — it provides the organic texture base
- The texture image must be copied to `dist/bg-texture.jpg` before rendering (Step 5 handles this)
- Vary the aurora orb colors per scene type using `scene-aurora-palette` above — do NOT reuse the same indigo/violet/cyan for every scene
- Override `.a1`, `.a2`, `.a3` background colors inline or via scene-specific CSS to match the palette
- The composition root element should set `background: #f8fafc` as fallback
- `filter: blur(80px)` is GPU-accelerated and renders correctly in headless Chrome
- Orb positions (top/right/bottom/left percentages) should vary slightly between scenes for visual variety

## Ambient Effects (2 Effects Only)

Every scene includes exactly **2 ambient effects** to create a living, breathing feel without overwhelming the content. All effects are GSAP timeline-driven — no CSS `@keyframes`.

Use `var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };` as a repeat-count helper in every composition.

### Effect 1: Aurora Drift (极光漂移)

The 3 aurora orbs drift slowly with different speeds and directions using GSAP yoyo. This creates the "breathing" ambient feel.

**GSAP:**
```js
var SCENE_DURATION = 10;
var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };

tl.fromTo(".a1", { x: 0, y: 0 }, { x: -40, y: 30, duration: 4, ease: "sine.inOut", yoyo: true, repeat: R(4) }, 0);
tl.fromTo(".a2", { x: 0, y: 0 }, { x: 30, y: -20, duration: 3.5, ease: "sine.inOut", yoyo: true, repeat: R(3.5) }, 0.5);
tl.fromTo(".a3", { x: 0, y: 0 }, { x: -25, y: 25, duration: 3, ease: "sine.inOut", yoyo: true, repeat: R(3) }, 0.3);
```

Vary the x/y displacement values slightly per scene for variety (±10px from these defaults).

### Effect 2: Panel Shadow Breathing (面板阴影呼吸)

The glass panel's box-shadow subtly pulses — the outer shadow grows slightly brighter, then returns to normal. This makes panels feel alive.

**GSAP:**
```js
tl.fromTo(".glass-panel",
  { boxShadow: "0 4px 16px rgba(99,102,241,0.08), 0 16px 48px rgba(99,102,241,0.12), inset 0 1px 0 rgba(255,255,255,0.6)" },
  { boxShadow: "0 4px 16px rgba(99,102,241,0.12), 0 16px 48px rgba(99,102,241,0.18), inset 0 1px 0 rgba(255,255,255,0.6)",
    duration: 2.5, ease: "sine.inOut", yoyo: true,
    repeat: R(2.5) }, 1.5);
```

For conclusion panels (green-accented), replace `rgba(99,102,241,...)` with `rgba(16,185,129,...)`.

### Entrance Animation Pattern

Use a simple 3-property entrance for every main content panel — matching the proven dark theme approach:

```js
// Panel rises with subtle 3D tilt
tl.fromTo(".problem-card",
  { y: 60, opacity: 0, rotationX: 8 },
  { y: 0, opacity: 1, rotationX: 2, duration: 0.8, ease: "power3.out" }, 0.2);

// Label wipes in (simple, no textShadow glow)
tl.fromTo("#mt-p-label",
  { x: -30, opacity: 0 },
  { x: 0, opacity: 1, duration: 0.5, ease: "expo.out" }, 0.6);
```

**Do NOT use:** scale, filter blur, glow burst (boxShadow flash), textShadow glow-in, or letterSpacing animation. These create visual noise.

**Staggered entrances:** When multiple elements enter at different times (cards, steps, rows), **do NOT set `opacity: 0` in CSS** — if JS errors prevent GSAP from running, all those elements stay permanently invisible, producing blank scenes. Instead, let GSAP handle the initial hidden state dynamically via `autoAlpha: 0` in the `fromTo()` "from" values. **Panels MUST be OPAQUE (`background:#ffffff`, no `backdrop-filter`)** — never use `backdrop-filter` or a see-through panel background (it washes out / occludes the content behind it). Get the "glass/premium" look from borders + layered box-shadow only:

```css
/* CSS: elements default to VISIBLE (safe fallback if JS fails) */
/* Do NOT add opacity:0 or visibility:hidden here */
.stagger-card {


}
```

```js
// GSAP handles hiding → revealing dynamically
// If JS fails, elements still show (static but visible > blank)
tl.fromTo(c.id,
  { y: 30, autoAlpha: 0, scale: 0.9 },
  { y: 0, autoAlpha: 1, scale: 1, duration: 0.5, ease: "back.out(1.4)",
    onStart: function() {
      var el = this.targets()[0];
      el.style.backdropFilter = "blur(16px)";
      el.style.webkitBackdropFilter = "blur(16px)";
    }
  }, c.t);
```

**Rule: CSS must never hide content that GSAP is responsible for revealing.** If GSAP crashes, CSS-hidden elements stay hidden forever → blank video.

### Ambient Effects Quick Reference

| Effect | HTML elements | GSAP driven | Repeat pattern |
|--------|--------------|-------------|----------------|
| Aurora drift | `.aurora-orb.a1`, `.a2`, `.a3` | Yes — x/y with yoyo | `repeat: R(dur)` |
| Panel shadow breathing | `.glass-panel` boxShadow | Yes — shadow pulse yoyo | `repeat: R(2.5)` |

**Removed effects (do NOT use):** bokeh particles, light sweep, corner brackets, iridescent border shimmer, enhanced entrance (scale+blur+glow).

## Caption Style

The caption is a **single bottom bar**, sized so it never dominates the frame or covers
scene content. On a 1920×1080 canvas the caption font-size is **38px** (allowed range
36–40px; `check_caption_size.py` hard-fails anything > 44px). Do NOT set it to 48–64px —
that is the #1 cause of "字幕过大、遮挡画面". Keep the bar to **≤ 2 lines** (this is why
narration is split into short per-sentence captions in Step 3).

**Position — MANDATORY bottom (字幕必须固定在视频下方).** The caption is ALWAYS pinned to the
bottom, in every scene, with no exceptions. Enforced by `check_caption_position.py`:
- Caption bars live **only in `index.html`'s root track** (`data-track-index="2"`), never
  inside a scene composition. A caption placed inside a scene inherits that scene's flex/
  stacking context and drifts to the **top or middle** — and differs scene to scene.
- Style them `position: absolute; bottom: 48px; left: 50%; transform: translateX(-50%);`.
  **Anchor with `bottom:` only — NEVER use `top:`** (top pulls the bar up to the top/middle).
- The offset parent is the 1920×1080 frame root, so `bottom:48px` lands the bar in the
  reserved caption safe zone at the bottom every time.

```css
.caption-container {
  position: absolute;
  bottom: 48px;            /* sits inside the bottom caption safe zone (see below) */
  left: 50%;
  transform: translateX(-50%);
  width: max-content;      /* REQUIRED: else abs-pos shrink-to-fits to the ~960px half-frame and wraps early */
  max-width: 1500px;       /* not full-bleed — leaves side margins; caps before bleeding off-frame */
  text-align: center;
  z-index: 2147483647;     /* caption is ALWAYS topmost — above every scene layer/panel (never covered) */
}
.caption-text {
  font-family: "Noto Sans SC", "PingFang SC", sans-serif;
  font-weight: 700;
  font-size: 38px;         /* 36–40px only; NEVER 48–64px (giant subtitle) */
  line-height: 1.45;
  color: #ffffff;          /* white text on the dark bar */
  background: rgba(15, 23, 42, 0.82);   /* opaque-enough dark bar; no backdrop-filter */
  border: 1px solid rgba(99,102,241,0.35);
  border-radius: 16px;
  padding: 14px 36px;
  box-shadow: 0 8px 28px rgba(15,23,42,0.35);
}
.caption-text .highlight {
  color: #a5b4fc;
}
.caption-text sub, .caption-text sup { font-size: 0.7em; }
```

### Bottom Caption Safe Zone (底部字幕安全区) — MANDATORY

The caption bar occupies the bottom band of the frame (≈ bottom 48px + up to 2 lines).
**Scene content must not extend into this band, or the subtitle will cover it.** Reserve
the bottom **180px** of the 1080px frame for captions — i.e. lay every scene's content out
in the **top ~900px** and let it float slightly higher, leaving the bottom clear.

Implement it once, in the shared `.scene-content` wrapper, via `padding-bottom` (see the
`.scene-content` rule in *Layout & Space Usage* below). Because content is flex-centered
inside the wrapper, the extra bottom padding shifts the whole scene up and keeps the
caption band empty — the scene simply renders **a little smaller and higher**. Full-bleed
background layers (aurora orbs, `bg-texture`) still fill the whole 1080px; only the
foreground `.scene-content` is inset. `check_caption_safe_zone.py` enforces this.

## Continuous Motion Patterns

Static scenes look like slideshows. Any scene that depicts a process (reaction, flow, transformation, circuit) **MUST** include continuous motion animations — particles moving, arrows flowing, elements transforming. These run on the seekable GSAP timeline using `repeat` and `yoyo`.

### Pattern 1: Particle Path Flow (粒子沿路径流动)

For electrons along wires, ions through solutions, current flow arrows:

```js
// Single particle moving along a path (e.g., electron along wire)
// Use multiple x/y keyframes to follow a curved path
tl.fromTo("#electron-1",
  { x: 0, y: 0 },
  { x: 300, y: 0, duration: 2.0, ease: "none",
    repeat: Math.ceil(SCENE_DURATION / 2.0) - 1 }, 1.0);

// Multiple particles with staggered start for continuous stream
var electrons = ["#e1", "#e2", "#e3", "#e4"];
electrons.forEach(function(id, i) {
  tl.fromTo(id,
    { x: 0, opacity: 1 },
    { x: 300, opacity: 1, duration: 2.5, ease: "none",
      repeat: Math.ceil(SCENE_DURATION / 2.5) - 1 },
    1.0 + i * 0.6);  // stagger by 0.6s
});
```

### Pattern 2: Ambient Drift (持续漂浮)

For ions floating in solution, background particles:

```js
// Gentle random-looking drift using yoyo
tl.fromTo("#ion-1",
  { x: 0, y: 0 },
  { x: 15, y: -10, duration: 1.8, ease: "sine.inOut",
    yoyo: true, repeat: Math.ceil(SCENE_DURATION / 1.8) - 1 }, 0.5);

tl.fromTo("#ion-2",
  { x: 0, y: 0 },
  { x: -12, y: 8, duration: 2.2, ease: "sine.inOut",
    yoyo: true, repeat: Math.ceil(SCENE_DURATION / 2.2) - 1 }, 0.8);
```

### Pattern 3: Rising Bubbles (气泡上升)

For gas generation (H₂, O₂), boiling, effervescence:

```js
// Bubble rises and fades out, then resets
tl.fromTo("#bubble-1",
  { y: 0, opacity: 0.8, scale: 0.6 },
  { y: -120, opacity: 0, scale: 1.2, duration: 2.0, ease: "power1.out",
    repeat: Math.ceil(SCENE_DURATION / 2.0) - 1 }, 1.0);

// Multiple bubbles with different speeds and offsets
["#b1","#b2","#b3","#b4","#b5"].forEach(function(id, i) {
  var dur = 1.5 + i * 0.4;
  tl.fromTo(id,
    { y: 0, opacity: 0.7, scale: 0.5 + i * 0.1 },
    { y: -100 - i * 30, opacity: 0, scale: 1.0 + i * 0.15,
      duration: dur, ease: "power1.out",
      repeat: Math.ceil(SCENE_DURATION / dur) - 1 },
    0.5 + i * 0.3);
});
```

### Pattern 4: Dissolving Effect (溶解效果)

For metal dissolving, fading elements:

```js
// Electrode gradually shrinks/fades (non-repeating, slow progression)
tl.fromTo("#zinc-plate",
  { scaleY: 1, opacity: 1 },
  { scaleY: 0.7, opacity: 0.6, duration: SCENE_DURATION - 2,
    ease: "power1.in" }, 1.0);
```

### Pattern 5: Pulse Glow (脉冲发光)

For active elements, highlighting current flow:

```js
// Continuous pulsing glow on active element
tl.fromTo("#active-node",
  { boxShadow: "0 0 15px rgba(99,102,241,0.25)" },
  { boxShadow: "0 0 35px rgba(99,102,241,0.45)",
    duration: 0.8, ease: "sine.inOut",
    yoyo: true, repeat: Math.ceil(SCENE_DURATION / 0.8) - 1 }, 0.5);

// SVG circle radius pulsing
tl.fromTo("#glow-circle",
  { attr: { r: 14 } },
  { attr: { r: 18 }, duration: 1.0, ease: "sine.inOut",
    yoyo: true, repeat: Math.ceil(SCENE_DURATION / 1.0) - 1 }, 0);
```

### Pattern 6: Directional Arrow Flow (方向箭头流动)

For indicating flow direction continuously:

```js
// Animated dashes flowing along a path (simulates flowing arrow)
tl.fromTo("#flow-path",
  { attr: { "stroke-dashoffset": 0 } },
  { attr: { "stroke-dashoffset": -40 }, duration: 1.0, ease: "none",
    repeat: Math.ceil(SCENE_DURATION / 1.0) - 1 }, 0.5);
// Pair with: stroke-dasharray="20 20" on the SVG path
```

### Motion Rules

1. **All motion on the timeline** — never use `setInterval`, `requestAnimationFrame`, or bare `gsap.to()` outside the registered timeline
2. **Calculate repeats from scene duration** — use `Math.ceil(SCENE_DURATION / cycleDuration) - 1` so motion fills the entire scene
3. **Vary speed across particles** — identical speeds look mechanical; offset durations by ±0.3s
4. **Stagger start times** — particles entering simultaneously look unnatural; offset by 0.3–0.8s
5. **Science scenes require motion** — if a scene depicts a reaction, circuit, or flow, it MUST have at least one continuously moving element. A static diagram of a working battery is wrong.

### Colors in GSAP Animations

GSAP animations use JS strings for colors. Define color constants at the top of each composition's `<script>`:

```js
var COLORS = {
  accentIndigo: "#6366f1",
  accentViolet: "#8b5cf6",
  accentCyan: "#06b6d4",
  success: "#10b981",
  glowIndigo020: "rgba(99,102,241,0.2)",
  glowIndigo040: "rgba(99,102,241,0.4)",
  glowGreen025: "rgba(16,185,129,0.25)",
  bgPrimary: "#f8fafc",
  textPrimary: "#0f172a"
};

// Then use in GSAP tweens:
tl.fromTo("#active-node",
  { boxShadow: "0 0 15px " + COLORS.glowIndigo020 },
  { boxShadow: "0 0 35px " + COLORS.glowIndigo040, ... });
```

## Scene Transition Pattern

Every scene should include **fade-in at start** and **fade-out at end** in its GSAP timeline to avoid hard cuts. Hard cuts make the video feel like a slideshow.

**CRITICAL SAFETY RULE: `.scene-content` MUST default to `opacity: 1` in CSS.** The GSAP fade-in starts from `autoAlpha: 0` (GSAP sets it at tween start), so visually the effect is the same — but if JS errors prevent the timeline from running, the content remains visible instead of permanently invisible. **Never set `opacity: 0` on `.scene-content` in CSS.**

```css
/* CORRECT — content visible by default (safe fallback) AND vertically centered */
.scene-content {
  position: absolute; inset: 0; z-index: 1;
  display: flex; align-items: center; justify-content: center; /* ← MANDATORY: centers content */
  padding: 40px 60px 180px; box-sizing: border-box;  /* bottom 180px = caption safe zone */
  opacity: 1; /* ← DEFAULT VISIBLE — GSAP handles fade-in dynamically */
}
```

> ⚠️ **Never emit `.scene-content` without the `display:flex; align-items:center; justify-content:center`
> trio.** A wrapper that only fills the frame (`position:absolute; inset:0`) but does not center will
> let a single-panel child (problem card / step panel / 结论 panel — a normal-flow block with just
> `max-width`) collapse to its content height and **pile at the TOP**, leaving the bottom ~40-50% empty.
> This is the #1 "排版" bug. See *Layout & Space Usage* for the full rule; enforced by
> `scripts/check_scene_layout.py`.

```js
// First tween: fade in the entire scene content
// autoAlpha sets opacity:0 + visibility:hidden at tween START, then animates to 1
tl.fromTo(".scene-content",
  { autoAlpha: 0 },
  { autoAlpha: 1, duration: 0.3, ease: "power2.out" }, 0);

// Last tween: fade out before scene ends (placed 0.3s before scene duration)
// tl.to(".scene-content",
//   { autoAlpha: 0, duration: 0.3, ease: "power2.in" }, SCENE_DURATION - 0.3);
```

The fade-out is optional — if the next scene's fade-in provides enough visual separation. But fade-in is **mandatory** for every scene.

**Why this matters:** Setting `opacity: 0` in CSS means any JS error (KaTeX crash, GSAP selector miss, syntax error) causes the ENTIRE scene to render as blank white — the #1 cause of blank videos in batch processing. With `opacity: 1` as default, a failed animation still shows static content, which is far better than a white rectangle.

## Layout & Space Usage

**Content must fill at least 70% of the frame's usable area** — that usable area is the
**top ~900px** (1920×900), because the bottom **180px** is the reserved caption safe zone
(see *Bottom Caption Safe Zone* above). A glass panel floating in the center with 60% empty
background looks unfinished, not minimal — but do NOT reclaim space by pushing content down
into the caption band.

Guidelines:
- **Single-panel scenes** (problem card, conclusion): panel width should be `max-width: 1400px` or wider
- **Split-layout scenes** (diagram + info): use `flex` with `flex: 2` / `flex: 1` to fill the width
- **Multi-card scenes** (phenomena, steps): use 3-column grid or flex-row spanning the full width
- **SVG scenes**: set viewBox to fill the available panel area, not a small centered box
- **Apparatus in split panels**: primary equipment (alcohol lamp, burner, flask, test tube) must fill **30-45% of the panel height** (at least 230px in a 780px panel). A tiny apparatus floating in a large empty panel is a critical proportion error — scale up with `transform: scale()` or use larger SVG dimensions
- Scene padding from edges: `40px 60px` sides/top; **bottom must reserve the 180px caption safe zone** (see the `padding-bottom` below) — never let content sit lower than ~900px

```css
.scene-content {
  position: relative; z-index: 1;
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  /* top/side padding 40/60; bottom 180px = caption safe zone.
     Content is flex-centered in the remaining top ~900px, floating above the caption bar. */
  padding: 40px 60px 180px; box-sizing: border-box;
}
```

> The `180px` bottom padding is the enforced caption safe zone. `display:flex; align-items:center;
> justify-content:center` is **mandatory** — it is what vertically centers the content in the top
> ~900px; `box-sizing: border-box` makes the padding subtract from the 1080px box, so the centered
> content ends around y≈900px — clear of the caption bar. Do not remove the bottom padding to "use
> more space".
>
> **Do NOT drop the centering.** Emitting `.scene-content { position:absolute; inset:0 }` *without*
> the `display:flex; align-items:center; justify-content:center` trio makes single-panel content
> (problem / step / 结论) pile at the TOP with the bottom half empty — the most common 排版 bug.
> The only accepted alternative is a content wrapper that fills the height itself (e.g. a split-layout
> `display:flex; width:100%; height:100%` diagram row, or a title container that is `position:absolute;
> inset:0`). Enforced by `scripts/check_scene_layout.py`.

### Not too big either — avoid oversize / overflow (排版过大)

Filling the frame does NOT mean overflowing it. Content sized larger than the frame gets
**clipped at the edges** or pushes neighbours off-screen — as bad as content that is too small.
`check_scene_overflow.py` hard-fails the gross cases; stay well inside these bounds:

- **Everything fits in 1920×1080**, and the *content* fits the 1920×900 safe area with a comfortable
  edge margin (~40–60px). Never set a CSS `width` > 1920px or `height` > 1080px on any element.
- **Size by container, not by huge fixed pixels.** Prefer `%` / `max-width` / `max-height` / `flex` /
  `grid` so a panel shrinks to fit; avoid fixed `px` boxes bigger than their room.
- **Font ceilings**: hero/title ≤ ~96px, section headings ≤ ~56px, body ≤ ~40px, captions 38px.
  A `font-size` over ~120px almost always overflows its panel or wraps badly (hard-failed above 160px).
- **Scale SVG via `viewBox`, not giant px** — a diagram scales to its container when the viewBox
  matches the drawing. Keep `transform: scale()` modest (≤ ~1.5); large scales blow content off-frame.
- **Multi-item rows must wrap or shrink, not overflow** — use `flex-wrap` / `grid` with `gap`, and let
  cells size down; do not let 4–5 fixed-width cards run past the right edge.
- **Balance**: aim for content occupying ~70–90% of the safe area. 70% ≙ "don't leave it tiny";
  90% ≙ "don't jam it to the edges". Both extremes read as broken layout.

## Light Theme Text Color Rule

This is a light-theme design system (`bg-primary: #f8fafc`). **All visible text must use dark colors.** White or near-white text is invisible on light backgrounds and is the single most common rendering bug.

### Mandatory Global Color Reset

Every composition MUST include these rules in its `<style>` block. This is a single copy-paste block — do not omit any line:

```css
/* === MANDATORY: Global light-theme color reset === */
.katex, .katex * { color: #0f172a; }
.katex-mathml { display: none !important; }
table, th, td { color: #0f172a; }
```

Additionally, **every `katex.render()` call** MUST pass `output: "html"` to prevent KaTeX from generating MathML markup that renders as visible duplicate text when the HyperFrames compiler strips KaTeX's CDN CSS:

```js
katex.render("...", element, { displayMode: true, output: "html" });
```

Additionally, the composition's root selector (e.g., `#mt-problem` or `[data-composition-id="mt-problem"]`) MUST set `color: #0f172a` so all child elements inherit dark text by default:

```css
#mt-problem {
  background: #f8fafc;
  color: #0f172a;   /* ← REQUIRED — global text inheritance */
  /* ...other properties... */
}
```

**Why each line matters:**
- `.katex, .katex *` — KaTeX renders equations with default black text; using `#0f172a` ensures consistency with the design system's slate-tinted dark
- `.katex-mathml { display: none !important; }` — KaTeX generates hidden MathML accessibility markup; when the KaTeX CDN CSS fails to load in headless Chrome during rendering, this markup becomes visible as duplicate plain-text equations. Hiding it prevents the visual duplication
- `table, th, td` — HTML tables inherit the browser's default black text color
- Root `color: #0f172a` — CSS inheritance gives all child elements dark text without needing per-element overrides

Then override per-element where needed (e.g., `.answer-eq .katex { color: #10b981; }` for success-colored answers, `.label { color: #6366f1; }` for accent labels).

### Text Color Quick Reference

| Context | Color | Token |
|---|---|---|
| Body text / equations | `#0f172a` | text-primary |
| Secondary / notes | `#64748b` | text-secondary |
| Labels / accents | `#6366f1` | accent-indigo |
| Success / answers | `#10b981` | success |
| SVG labels (fill) | `#0f172a` | text-primary |

**Forbidden text colors on light backgrounds:** `#fff`, `#ffffff`, `#f8fafc`, `#f1f5f9`, `#e2e8f0`, `#e8ecf4`, `currentColor` (when inherited from a light parent), or any color with OKLCH lightness above 0.85.

## Do's and Don'ts

**Do:**
- Use glass panels for all content containers
- Use `#f8fafc` as base background (never pure `#fff`)
- Use KaTeX for all math rendering
- Use textured aurora mesh backgrounds (blurred texture + 3 gradient orbs) for every scene
- Use Noto Sans SC for all Chinese text
- Fill at least 70% of the frame with content
- Add fade-in (0.3s) to every scene entrance
- Use different aurora palette colors for different scene types (from scene-aurora-palette)
- Apply glow filters to all small particles/icons in SVG
- Size SVG elements for 1080p video, not web (min 30px width)
- **Override KaTeX default color** with `.katex, .katex * { color: #0f172a; }` in every composition
- Use vivid accent colors (`#6366f1`, `#8b5cf6`, `#06b6d4`) for labels, badges, and highlights
- Keep ambient effects to exactly 2 per scene (aurora drift + panel shadow breathing)

**Don't:**
- Use gradient text on **formulas / KaTeX elements** (`background-clip:text` + `-webkit-text-fill-color:transparent` makes glyphs transparent and leaves only the fraction bar as a stray horizontal dash — use a solid `color` for any element containing a `.katex` formula). Gradient text is acceptable on plain-text titles/taglines only.
- Display equations as plain text
- Use `backdrop-filter` / frosted glass / any translucent see-through panel background (panels MUST be opaque `#ffffff` or white alpha ≥ 0.92 — translucency occludes content)
- Set grid lines above 5% opacity (grid is removed — textured background provides structure)
- Use colors not defined in this file
- Hard-cut between scenes without any opacity transition
- Leave more than 30% of the frame as empty background without content
- Use photo backgrounds other than the designated `bg-texture.jpg` — no random stock photos or unblurred images
- Use SVG elements thinner than 3px stroke or smaller than 30px
- Create particles/ions without glow halos (they look flat on light backgrounds)
- **Use white or light text on light backgrounds.** KaTeX, SVG labels, and any rendered text must use dark colors (`#0f172a` or darker). KaTeX defaults to `#000` which is acceptable but `#0f172a` is preferred for design consistency
- **Use emoji characters.** Headless Chromium lacks emoji fonts — all emoji render as boxes. Use plain Chinese text or SVG/CSS icons instead
- **Use raw Unicode math symbols in HTML text.** Characters like special symbols are not guaranteed to render in Noto Sans SC / Inter. Use KaTeX for math, `<sub>`/`<sup>` for subscripts/superscripts, and Chinese text for geometric names
- Use more than 2 ambient effects per scene (aurora drift + panel shadow breathing is the maximum)
- Use bokeh particles, light sweep, corner brackets, or iridescent border shimmer (removed — they create visual chaos)
- Use enhanced entrance animations with scale + filter blur + glow burst (use simple y + opacity + rotationX instead)

## Background Theme Catalog

The default `aurora-scholar` theme (blue ripple texture + aurora orbs described above) is the primary visual identity. For visual variety across different problem types, 4 alternative light themes are available. **All themes keep the same white opaque panels (`#ffffff`), dark text (`#0f172a`), and KaTeX colors — only the `.scene-bg` layer and aurora orb colors change.** Panel border/shadow accent tints shift slightly per theme.

### Theme Selection Guide

| Problem Category | Recommended Theme | Why |
|---|---|---|
| General / default | `aurora-scholar` | Premium tech-educational feel, works for everything |
| Geometry, classical proofs | `chinese-elegant` | Lake-blue serenity suits precise geometric constructions |
| Algebra, equations, functions | `lavender-soft` | Gentle purple tones keep focus on symbolic manipulation |
| Statistics, probability, data | `mint-fresh` | Fresh green evokes growth/data/natural patterns |
| Elementary arithmetic, fractions | `warm-art` | Warm paper feel is approachable for younger learners |
| Physics, chemistry, experiments | `aurora-scholar` | Default aurora mesh matches science-lab aesthetic |

**Usage:** The storyboard (Step 4) specifies the theme in its `Global Direction` block. All scenes in one video typically share the same theme. The theme choice is a suggestion — `aurora-scholar` is always a safe default.

### Theme: `aurora-scholar` (极光蓝波) — DEFAULT

This is the existing default theme described in "Background Treatment" above. Uses `bg-texture.jpg` + 3 aurora gradient orbs. No changes needed — see the CSS above.

### Theme: `chinese-elegant` (清雅湖蓝)

Inspired by Neo-Chinese style courseware. Soft lake-blue gradient with a subtle wave pattern overlay via CSS, replacing the texture image. Calm, elegant, with ample visual breathing room.

**Background CSS (replaces `.bg-texture` and `.aurora-orb` colors):**

```css
/* chinese-elegant: lake-blue gradient with subtle wave pattern */
.bg-texture {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: linear-gradient(135deg, #e8f4f8 0%, #d1e8ef 40%, #bdd9e6 70%, #d6eaf0 100%);
}
/* Decorative wave overlay via repeating gradient */
.bg-texture::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 600px 100px at 20% 80%, rgba(255,255,255,0.3) 0%, transparent 70%),
    radial-gradient(ellipse 500px 80px at 70% 30%, rgba(255,255,255,0.25) 0%, transparent 70%),
    radial-gradient(ellipse 400px 60px at 40% 60%, rgba(255,255,255,0.2) 0%, transparent 70%);
  pointer-events: none;
}

/* Aurora orbs — teal/cyan/light-blue palette */
.a1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(20,184,166,0.45) 0%, transparent 70%);
  top: -10%; right: -5%;
}
.a2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(6,182,212,0.4) 0%, transparent 70%);
  bottom: -15%; left: -5%;
}
.a3 {
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(56,189,248,0.35) 0%, transparent 70%);
  top: 40%; left: 50%;
}
```

**Accent tint shift (optional):**

```css
/* Panel border shifts to teal — optional, default indigo also works */
.glass-panel {
  border: 1px solid rgba(20, 184, 166, 0.25);
  border-top: 2px solid rgba(20, 184, 166, 0.2);
  box-shadow:
    0 4px 16px rgba(20, 184, 166, 0.06),
    0 16px 48px rgba(20, 184, 166, 0.10),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}
.step-badge {
  background: linear-gradient(135deg, #14b8a6, #06b6d4);
}
```

**Scene-specific aurora palettes for `chinese-elegant`:**

```yaml
chinese-elegant-palette:
  intro/problem:
    a1: "rgba(20,184,166,0.45)"    # teal
    a2: "rgba(6,182,212,0.4)"      # cyan
    a3: "rgba(56,189,248,0.35)"    # sky-blue
  derivation:
    a1: "rgba(6,182,212,0.45)"     # cyan
    a2: "rgba(20,184,166,0.4)"     # teal
    a3: "rgba(99,102,241,0.3)"     # indigo hint
  geometry:
    a1: "rgba(20,184,166,0.5)"     # teal (strong)
    a2: "rgba(56,189,248,0.4)"     # sky-blue
    a3: "rgba(6,182,212,0.3)"      # cyan
  steps:
    a1: "rgba(6,182,212,0.4)"      # cyan
    a2: "rgba(20,184,166,0.35)"    # teal
    a3: "rgba(56,189,248,0.3)"     # sky-blue
  conclusion:
    a1: "rgba(16,185,129,0.45)"    # emerald
    a2: "rgba(20,184,166,0.4)"     # teal
    a3: "rgba(6,182,212,0.3)"      # cyan
```

### Theme: `lavender-soft` (柔紫轻盈)

Inspired by soft-lavender infographic style. Near-white to very pale lavender gradient. Gentle, modern, clean.

**Background CSS:**

```css
/* lavender-soft: near-white to pale lavender gradient */
.bg-texture {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: linear-gradient(160deg, #faf8ff 0%, #f3eeff 35%, #ede5ff 65%, #f5f0ff 100%);
}
/* Soft decorative capsule shapes at edges */
.bg-texture::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 200px 600px at -3% 50%, rgba(139,92,246,0.08) 0%, transparent 70%),
    radial-gradient(ellipse 180px 500px at 103% 40%, rgba(139,92,246,0.06) 0%, transparent 70%);
  pointer-events: none;
}

/* Aurora orbs — lavender/blue-purple/pink-purple palette */
.a1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(139,92,246,0.4) 0%, transparent 70%);
  top: -10%; right: -5%;
}
.a2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(124,58,237,0.35) 0%, transparent 70%);
  bottom: -15%; left: -5%;
}
.a3 {
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(192,132,252,0.3) 0%, transparent 70%);
  top: 40%; left: 50%;
}
```

**Accent tint shift (optional):**

```css
.glass-panel {
  border: 1px solid rgba(139, 92, 246, 0.25);
  border-top: 2px solid rgba(139, 92, 246, 0.2);
  box-shadow:
    0 4px 16px rgba(139, 92, 246, 0.06),
    0 16px 48px rgba(139, 92, 246, 0.10),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}
.step-badge {
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
}
```

**Scene-specific aurora palettes for `lavender-soft`:**

```yaml
lavender-soft-palette:
  intro/problem:
    a1: "rgba(139,92,246,0.4)"     # violet
    a2: "rgba(124,58,237,0.35)"    # blue-purple
    a3: "rgba(192,132,252,0.3)"    # pink-purple
  derivation:
    a1: "rgba(124,58,237,0.4)"     # blue-purple
    a2: "rgba(139,92,246,0.35)"    # violet
    a3: "rgba(99,102,241,0.3)"     # indigo
  steps:
    a1: "rgba(139,92,246,0.35)"    # violet
    a2: "rgba(192,132,252,0.3)"    # pink-purple
    a3: "rgba(124,58,237,0.25)"    # blue-purple
  conclusion:
    a1: "rgba(16,185,129,0.4)"     # emerald
    a2: "rgba(139,92,246,0.3)"     # violet
    a3: "rgba(20,184,166,0.3)"     # teal
```

### Theme: `mint-fresh` (薄荷清新)

Inspired by mint-watercolor business style. Light mint-green to white gradient with a fresh, clean feel.

**Background CSS:**

```css
/* mint-fresh: mint-green to white gradient */
.bg-texture {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: linear-gradient(150deg, #f0fdf9 0%, #e6faf2 30%, #d1fae5 60%, #ecfdf5 100%);
}
/* Watercolor-style brush marks at edges */
.bg-texture::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 350px 250px at 90% 15%, rgba(16,185,129,0.1) 0%, transparent 70%),
    radial-gradient(ellipse 300px 400px at 5% 85%, rgba(20,184,166,0.08) 0%, transparent 70%);
  pointer-events: none;
}

/* Aurora orbs — mint/cyan-green/teal palette */
.a1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(16,185,129,0.4) 0%, transparent 70%);
  top: -10%; right: -5%;
}
.a2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(20,184,166,0.35) 0%, transparent 70%);
  bottom: -15%; left: -5%;
}
.a3 {
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(52,211,153,0.3) 0%, transparent 70%);
  top: 40%; left: 50%;
}
```

**Accent tint shift (optional):**

```css
.glass-panel {
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-top: 2px solid rgba(16, 185, 129, 0.2);
  box-shadow:
    0 4px 16px rgba(16, 185, 129, 0.06),
    0 16px 48px rgba(16, 185, 129, 0.10),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}
.step-badge {
  background: linear-gradient(135deg, #10b981, #14b8a6);
}
```

**Scene-specific aurora palettes for `mint-fresh`:**

```yaml
mint-fresh-palette:
  intro/problem:
    a1: "rgba(16,185,129,0.4)"     # emerald
    a2: "rgba(20,184,166,0.35)"    # teal
    a3: "rgba(52,211,153,0.3)"     # green
  derivation:
    a1: "rgba(20,184,166,0.4)"     # teal
    a2: "rgba(16,185,129,0.35)"    # emerald
    a3: "rgba(6,182,212,0.3)"      # cyan
  steps:
    a1: "rgba(16,185,129,0.35)"    # emerald
    a2: "rgba(52,211,153,0.3)"     # green
    a3: "rgba(20,184,166,0.25)"    # teal
  conclusion:
    a1: "rgba(16,185,129,0.45)"    # emerald (strong)
    a2: "rgba(20,184,166,0.4)"     # teal
    a3: "rgba(52,211,153,0.3)"     # green
```

### Theme: `warm-art` (暖黄纸感)

Inspired by warm-art courseware style. Cream-yellow to light-golden gradient with a handcrafted paper feel. Friendly and approachable.

**Background CSS:**

```css
/* warm-art: cream-yellow to golden gradient with paper feel */
.bg-texture {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: linear-gradient(145deg, #fffbf0 0%, #fef3cd 30%, #fde68a40 55%, #fefce8 100%);
}
/* Paper grain texture via noise-like gradients */
.bg-texture::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 500px 300px at 25% 20%, rgba(251,191,36,0.08) 0%, transparent 70%),
    radial-gradient(ellipse 400px 350px at 75% 75%, rgba(245,158,11,0.06) 0%, transparent 70%),
    radial-gradient(ellipse 300px 200px at 60% 10%, rgba(252,211,77,0.07) 0%, transparent 70%);
  pointer-events: none;
}

/* Aurora orbs — golden/amber/soft-purple palette */
.a1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(251,191,36,0.35) 0%, transparent 70%);
  top: -10%; right: -5%;
}
.a2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(245,158,11,0.3) 0%, transparent 70%);
  bottom: -15%; left: -5%;
}
.a3 {
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(167,139,250,0.25) 0%, transparent 70%);
  top: 40%; left: 50%;
}
```

**Accent tint shift (optional):**

```css
.glass-panel {
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-top: 2px solid rgba(245, 158, 11, 0.15);
  box-shadow:
    0 4px 16px rgba(245, 158, 11, 0.06),
    0 16px 48px rgba(245, 158, 11, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}
.step-badge {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}
```

**Scene-specific aurora palettes for `warm-art`:**

```yaml
warm-art-palette:
  intro/problem:
    a1: "rgba(251,191,36,0.35)"    # golden
    a2: "rgba(245,158,11,0.3)"     # amber
    a3: "rgba(167,139,250,0.25)"   # soft-purple
  derivation:
    a1: "rgba(245,158,11,0.35)"    # amber
    a2: "rgba(251,191,36,0.3)"     # golden
    a3: "rgba(252,211,77,0.25)"    # light-gold
  steps:
    a1: "rgba(251,191,36,0.3)"     # golden
    a2: "rgba(167,139,250,0.25)"   # soft-purple
    a3: "rgba(245,158,11,0.2)"     # amber
  conclusion:
    a1: "rgba(16,185,129,0.4)"     # emerald
    a2: "rgba(251,191,36,0.3)"     # golden
    a3: "rgba(20,184,166,0.25)"    # teal
```

### How to Apply a Theme

1. In the **storyboard** (Step 4), set `Theme: <theme-id>` in the Global Direction block
2. In **each composition** (Step 5), replace the default `.bg-texture` and `.a1`/`.a2`/`.a3` CSS with the theme's CSS block
3. **Panels, text, KaTeX colors remain unchanged** — only the `.scene-bg` children change
4. The HTML template structure stays the same:
   ```html
   <div class="scene-bg">
     <div class="bg-texture"></div>
     <div class="aurora-orb a1"></div>
     <div class="aurora-orb a2"></div>
     <div class="aurora-orb a3"></div>
   </div>
   ```
5. For non-default themes, the `.bg-texture` div uses a CSS gradient instead of `url('../bg-texture.jpg')` — no image file needed
6. The root composition (`index.html`) background fallback should match the theme's lightest color:
   - `aurora-scholar`: `background: #f8fafc`
   - `chinese-elegant`: `background: #e8f4f8`
   - `lavender-soft`: `background: #faf8ff`
   - `mint-fresh`: `background: #f0fdf9`
   - `warm-art`: `background: #fffbf0`
7. The ambient aurora-drift GSAP animation works identically for all themes — only the orb colors differ
