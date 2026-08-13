# Math Components

Reusable HyperFrames sub-composition templates for math tutorial videos. Each component is a complete `<template>`-wrapped HTML file. Copy the template, replace placeholder content, and adjust GSAP timing to match transcript timestamps.

All components use tokens from [design-system.md](../design-system.md). Load KaTeX in every composition that renders equations. All components use the aurora mesh theme with hardcoded color values from design-system.md.

## Required Setup (copy into every composition)

> ⚠️ **Offline / box-proof overrides (MANDATORY — these templates predate them).** When you copy ANY template below you MUST: (1) replace its Google-Fonts `<link>` with the self-hosted `@font-face` block (embedded once in `index.html`'s `<head>`, see step-6 / design-system) and use a CJK-first `font-family: "Noto Sans SC", Inter, sans-serif`; (2) load KaTeX from the local `./katex/` copy and **inline** `katex.min.css` as `<style id="katex-inline-css">` with `url(./katex/fonts/` — never a CDN `<link>` (see step-5); (3) pass `output: "html"` to every `katex.render(...)`; (4) load GSAP from the local `./gsap/gsap.min.js` copy — **never** from `cdn.jsdelivr.net` or any other CDN (the templates below already use `./gsap/gsap.min.js`). **No Google Fonts / CDN** — the sandbox is air-gapped, and a CDN resource that fails to load breaks fonts, equations, and animations.

> 🆔 **`data-composition-id` is NOT a DOM `id` — if you scope CSS or JS to `#<composition-id>`, the root div MUST also carry a matching `id`.** A scene root written `<div data-composition-id="mt-formula" …>` has **no** element with `id="mt-formula"`, so any selector `#mt-formula` (container CSS, or a KaTeX loop like `document.querySelectorAll("#mt-formula [data-tex]")`) matches **nothing** — silently. The most common casualty: **every formula comes out blank** because `katex.render` never runs on the `[data-tex]`/`.cm` spans (`querySelectorAll` returning empty throws no error). Do ONE of: (a) give the root **both** attributes — `<div data-composition-id="mt-formula" id="mt-formula" …>`; or (b) never scope by the root id — render formulas by CLASS (`document.querySelectorAll(".cm")`, as `index.html` does) or via `getElementById` on real inner element ids (as the scene templates below do), and scope CSS with classes / `[data-composition-id="…"]`. The pre-render gate `scripts/check_composition_root_id.py` fails the build when a scene uses `#<composition-id>` without a matching root `id`.

### Chinese fonts (self-hosted, offline)

Embed once in `index.html`'s `<head>` (applies to all compositions). Fonts are shipped under `assets/fonts/` and copied to `dist/assets/fonts/` in step-5 Prerequisites:

```html
<style>
  @font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-Bold.woff2") format("woff2"); font-weight:400 700; font-display:swap; }
  @font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-ExtraBold.woff2") format("woff2"); font-weight:800; font-display:swap; }
  @font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-Black.woff2") format("woff2"); font-weight:900; font-display:swap; }
  @font-face { font-family:"Inter"; src:url("./assets/fonts/Inter-Variable.woff2") format("woff2"); font-weight:100 900; font-display:swap; }
  html, body { font-family:"Noto Sans SC", Inter, sans-serif; }
</style>
```

### KaTeX (self-hosted, offline)

```html
<!-- inline katex.min.css as <style id="katex-inline-css"> with url(./katex/fonts/ (see step-5) — NOT a CDN <link> -->
<script src="./katex/katex.min.js"></script>
```

Render an equation:
```js
katex.render("x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}", element, { displayMode: true, output: "html" });
```

**Important:** Always pass `output: "html"` to prevent KaTeX from generating MathML accessibility markup (`.katex-mathml`). Without this option, the HyperFrames compiler strips KaTeX's CDN CSS during compilation, causing the MathML markup to render as visible duplicate text below every equation.

---

## Component 1: Problem Display Card (题目展示卡片)

A glass-morphism panel with 3D perspective tilt displaying the problem statement or task overview. For experiment/concept topics, includes numbered key-point rows with sequential highlight cycling. For pure math problems, displays a KaTeX equation below the problem text.

```html
<template id="mt-problem-template">
  <div data-composition-id="mt-problem" data-width="1920" data-height="1080">

    <!-- Background layers -->
    <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb a1"></div>
      <div class="aurora-orb a2"></div>
      <div class="aurora-orb a3"></div>
    </div>

    <!-- Content -->
    <div class="scene-content">
      <div class="problem-card-wrapper">
        <div class="problem-card glass-panel">
          <div class="label" id="mt-p-label">EXPERIMENT TASK · 实验任务</div>
          <div class="problem-text" id="mt-p-text">
            <!-- Chinese problem text or task description here -->
            描述焰色反应的实验原理、操作步骤和常见金属元素的火焰颜色。
          </div>
          <div class="key-points" id="mt-p-points">
            <div class="formula-row" id="mt-p-row-1">
              <div class="step-badge" id="mt-p-badge-1">1</div>
              <div class="point-content">
                <div class="point-title-cn">知识要点一</div>
                <div class="point-title-en">Key Point 1</div>
              </div>
            </div>
            <div class="formula-row" id="mt-p-row-2">
              <div class="step-badge" id="mt-p-badge-2">2</div>
              <div class="point-content">
                <div class="point-title-cn">知识要点二</div>
                <div class="point-title-en">Key Point 2</div>
              </div>
            </div>
            <div class="formula-row" id="mt-p-row-3">
              <div class="step-badge" id="mt-p-badge-3">3</div>
              <div class="point-content">
                <div class="point-title-cn">知识要点三</div>
                <div class="point-title-en">Key Point 3</div>
              </div>
            </div>
          </div>
          <!-- Optional: KaTeX equation (for math problems, replace key-points with this) -->
          <div class="problem-equation" id="mt-p-eq"></div>
        </div>
      </div>
    </div>

    <style>
      [data-composition-id="mt-problem"] {
        position: relative; width: 100%; height: 100%;
        background: #f8fafc;
        font-family: "Noto Sans SC", Inter, sans-serif;
        color: #0f172a;
        overflow: hidden;
      }
      /* === MANDATORY: Global light-theme color reset === */
      .katex, .katex * { color: #0f172a; }
      .katex-mathml { display: none !important; }
      table, th, td { color: #0f172a; }

      .scene-bg { position: absolute; inset: 0; }
      .bg-texture { position: absolute; inset: 0; z-index: 0; background: url('../bg-texture.jpg') center/cover no-repeat; }
      .aurora-orb { position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none; }
      .a1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(99,102,241,0.55) 0%, transparent 70%); top: -10%; right: -5%; }
      .a2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(139,92,246,0.4) 0%, transparent 70%); bottom: -15%; left: -5%; }
      .a3 { width: 350px; height: 350px; background: radial-gradient(circle, rgba(6,182,212,0.32) 0%, transparent 70%); top: 40%; left: 50%; }

      .scene-content {
        position: relative; z-index: 5;
        width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 60px 100px 180px; box-sizing: border-box;
      }

      .problem-card-wrapper { perspective: 1200px; width: 100%; display: flex; justify-content: center; }
      .glass-panel {
        position: relative;
        background: #ffffff;

        border: 1px solid rgba(99,102,241,0.3);
        border-top: 2px solid rgba(99,102,241,0.25);
        border-radius: 20px;
        box-shadow:
          0 4px 16px rgba(99,102,241,0.08),
          0 16px 48px rgba(99,102,241,0.12),
          inset 0 1px 0 rgba(255,255,255,0.6);
      }
      .problem-card {
        transform: rotateY(-3deg) rotateX(2deg);
        padding: 56px 72px;
        max-width: 1500px;
        width: 100%;
      }

      .label {
        font-family: "Noto Sans SC", Inter, sans-serif;
        font-size: 20px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #6366f1;
        margin-bottom: 28px;
      }
      .problem-text {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 36px;
        font-weight: 500;
        color: #0f172a;
        line-height: 1.6;
        margin-bottom: 40px;
        padding-bottom: 28px;
        border-bottom: 1px solid rgba(99,102,241,0.1);
      }

      .key-points {
        display: flex;
        flex-direction: column;
        gap: 18px;
      }
      .formula-row {
        display: flex;
        align-items: center;
        gap: 28px;
        padding: 22px 32px;
        border-radius: 14px;
        border: 1px solid transparent;
        background: rgba(230,240,255,0.4);
        transition: border-color 0.3s, box-shadow 0.3s;
      }
      .step-badge {
        width: 56px; height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex; align-items: center; justify-content: center;
        font-family: "Noto Sans SC", Inter, sans-serif;
        font-weight: 700;
        font-size: 26px;
        color: #ffffff;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(99,102,241,0.25);
      }
      .point-content {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }
      .point-title-cn {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 32px;
        font-weight: 600;
        color: #0f172a;
        letter-spacing: 0.02em;
      }
      .point-title-en {
        font-family: "Noto Sans SC", Inter, sans-serif;
        font-size: 18px;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
      }

      .problem-equation {
        text-align: center; margin-top: 16px;
      }
      .problem-equation .katex { font-size: 48px; }
    </style>

    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <!-- KaTeX CSS: inline as <style id="katex-inline-css"> with local url(./katex/fonts/ — see step-5 (NOT a CDN <link>) -->
    <script src="./katex/katex.min.js"></script>
    <script src="./gsap/gsap.min.js"></script>
    <script>
      (function(){
        var SCENE_DURATION = 13;
        var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };

        window.__timelines = window.__timelines || {};
        var tl = gsap.timeline({ paused: true });

        // 0. Scene fade-in
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

        // 1. Card entrance
        tl.fromTo(".problem-card",
          { y: 60, opacity: 0, rotationX: 8 },
          { y: 0, opacity: 1, rotationX: 2, duration: 0.8, ease: "power3.out" }, 0.3);

        // 2. Label slide-in
        tl.fromTo("#mt-p-label",
          { x: -30, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5, ease: "expo.out" }, 0.7);

        // 3. Problem text
        tl.fromTo("#mt-p-text",
          { y: 20, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6, ease: "power2.out" }, 0.9);

        // 4. Three key-point rows stagger in
        tl.fromTo("#mt-p-row-1",
          { x: -30, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 1.5);
        tl.fromTo("#mt-p-row-2",
          { x: -30, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 2.1);
        tl.fromTo("#mt-p-row-3",
          { x: -30, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 2.7);

        // 5. Highlight cycle — each row gets ~3.3s active spotlight
        // Divide remaining time into 3 equal segments
        var hlDur = (SCENE_DURATION - 3.5) / 3;

        // Row 1 active
        tl.to("#mt-p-row-1", {
          borderColor: "rgba(99,102,241,0.5)",
          boxShadow: "0 0 20px rgba(99,102,241,0.1)",
          duration: 0.4, ease: "power2.out"
        }, 3.3);
        tl.to("#mt-p-badge-1", {
          boxShadow: "0 0 24px rgba(99,102,241,0.5)",
          scale: 1.08,
          duration: 0.5, ease: "sine.inOut"
        }, 3.3);
        tl.to(["#mt-p-row-2","#mt-p-row-3"], {
          opacity: 0.5, duration: 0.4
        }, 3.3);

        // Row 2 active
        var t2 = 3.3 + hlDur;
        tl.to("#mt-p-row-1", {
          borderColor: "rgba(0,0,0,0)",
          boxShadow: "0 0 0 rgba(99,102,241,0)",
          opacity: 0.5, duration: 0.4
        }, t2);
        tl.to("#mt-p-badge-1", {
          boxShadow: "0 2px 8px rgba(99,102,241,0.25)",
          scale: 1.0, duration: 0.4
        }, t2);
        tl.to("#mt-p-row-2", {
          opacity: 1,
          borderColor: "rgba(99,102,241,0.5)",
          boxShadow: "0 0 20px rgba(99,102,241,0.1)",
          duration: 0.4, ease: "power2.out"
        }, t2);
        tl.to("#mt-p-badge-2", {
          boxShadow: "0 0 24px rgba(99,102,241,0.5)",
          scale: 1.08,
          duration: 0.5, ease: "sine.inOut"
        }, t2);

        // Row 3 active
        var t3 = 3.3 + hlDur * 2;
        tl.to("#mt-p-row-2", {
          borderColor: "rgba(0,0,0,0)",
          boxShadow: "0 0 0 rgba(99,102,241,0)",
          opacity: 0.5, duration: 0.4
        }, t3);
        tl.to("#mt-p-badge-2", {
          boxShadow: "0 2px 8px rgba(99,102,241,0.25)",
          scale: 1.0, duration: 0.4
        }, t3);
        tl.to("#mt-p-row-3", {
          opacity: 1,
          borderColor: "rgba(99,102,241,0.5)",
          boxShadow: "0 0 20px rgba(99,102,241,0.1)",
          duration: 0.4, ease: "power2.out"
        }, t3);
        tl.to("#mt-p-badge-3", {
          boxShadow: "0 0 24px rgba(99,102,241,0.5)",
          scale: 1.08,
          duration: 0.5, ease: "sine.inOut"
        }, t3);

        // 6. Ambient: Aurora drift
        tl.fromTo(".a1", { x: 0, y: 0 }, { x: -40, y: 30, duration: 4, ease: "sine.inOut", yoyo: true, repeat: R(4) }, 0);
        tl.fromTo(".a2", { x: 0, y: 0 }, { x: 30, y: -20, duration: 3.5, ease: "sine.inOut", yoyo: true, repeat: R(3.5) }, 0.5);
        tl.fromTo(".a3", { x: 0, y: 0 }, { x: -25, y: 25, duration: 3, ease: "sine.inOut", yoyo: true, repeat: R(3) }, 0.3);

        // 7. Ambient: Panel shadow breathing
        tl.fromTo(".glass-panel",
          { boxShadow: "0 4px 16px rgba(99,102,241,0.08), 0 16px 48px rgba(99,102,241,0.12), inset 0 1px 0 rgba(255,255,255,0.6)" },
          { boxShadow: "0 4px 16px rgba(99,102,241,0.12), 0 16px 48px rgba(99,102,241,0.18), inset 0 1px 0 rgba(255,255,255,0.6)",
            duration: 2.5, ease: "sine.inOut", yoyo: true, repeat: R(2.5) }, 1.5);

        window.__timelines["mt-problem"] = tl;
      })();
    </script>
  </div>
</template>
```

**Adaptation notes:**
- For experiment topics: use the `.key-points` rows with Chinese + English titles. Set the label to "EXPERIMENT TASK · 实验任务" or "TOPIC OVERVIEW · 课题概述".
- For pure math problems: remove `.key-points` div and use `.problem-equation` instead for KaTeX display.
- Highlight cycling times (`3.3`, `t2`, `t3`) should be adjusted to match narration timestamps.
- Each row dims to `opacity: 0.5` when inactive; the active row gets an indigo border glow.
- Badge uses indigo→violet gradient (`#6366f1` → `#8b5cf6`).

---

## Component 2: Formula Derivation Panel (公式推导面板)

Step-by-step equation display with sequential reveal and active-step highlighting.

```html
<template id="mt-formula-template">
  <div data-composition-id="mt-formula" data-width="1920" data-height="1080">

        <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb a1"></div>
      <div class="aurora-orb a2"></div>
      <div class="aurora-orb a3"></div>
    </div>

    <div class="scene-content">
      <div class="formula-panel glass-panel">
        <div class="label" id="mt-f-label">SOLUTION</div>

        <div class="formula-steps" id="mt-f-steps">
          <!-- Repeat .formula-row for each step -->
          <div class="formula-row" id="mt-f-row-1">
            <div class="step-badge">1</div>
            <div class="formula-eq" id="mt-f-eq-1"></div>
            <div class="formula-note">identify coefficients</div>
          </div>
          <div class="formula-connector" id="mt-f-conn-1">
            <svg width="2" height="32"><line x1="1" y1="0" x2="1" y2="32" stroke="#6366f1" stroke-width="2"/></svg>
          </div>
          <div class="formula-row" id="mt-f-row-2">
            <div class="step-badge">2</div>
            <div class="formula-eq" id="mt-f-eq-2"></div>
            <div class="formula-note">apply formula</div>
          </div>
          <div class="formula-connector" id="mt-f-conn-2">
            <svg width="2" height="32"><line x1="1" y1="0" x2="1" y2="32" stroke="#6366f1" stroke-width="2"/></svg>
          </div>
          <div class="formula-row" id="mt-f-row-3">
            <div class="step-badge">3</div>
            <div class="formula-eq" id="mt-f-eq-3"></div>
            <div class="formula-note">simplify</div>
          </div>
        </div>
      </div>
    </div>

    <style>
      [data-composition-id="mt-formula"] {
        position: relative; width: 100%; height: 100%;
        background: #f8fafc;
        font-family: "Noto Sans SC", Inter, sans-serif;
        color: #0f172a;
        overflow: hidden;
      }
      /* === MANDATORY: Global light-theme color reset === */
      .katex, .katex * { color: #0f172a; }
      .katex-mathml { display: none !important; }
      table, th, td { color: #0f172a; }
      .scene-bg { position: absolute; inset: 0; }
      .bg-texture { position: absolute; inset: 0; z-index: 0; background: url('../bg-texture.jpg') center/cover no-repeat; }
      .aurora-orb { position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none; }
      .a1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(139,92,246,0.48) 0%, transparent 70%); top: -10%; right: -5%; }
      .a2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(99,102,241,0.35) 0%, transparent 70%); bottom: -15%; left: -5%; }
      .a3 { width: 350px; height: 350px; background: radial-gradient(circle, rgba(168,85,247,0.29) 0%, transparent 70%); top: 40%; left: 50%; }
      .scene-content {
        position: relative; z-index: 5;
        width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 60px 160px 180px; box-sizing: border-box;
      }
      .glass-panel {
        background: #ffffff;

        border: 1px solid rgba(99,102,241,0.3);
        border-top: 2px solid rgba(99,102,241,0.25); border-radius: 20px;
        box-shadow: 0 0 40px rgba(99,102,241,0.08), inset 0 1px 0 rgba(255,255,255,0.6);
      }
      .formula-panel {
        padding: 48px 64px; width: 100%; max-width: 1200px;
      }
      .label {
        font-size: 18px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.12em;
        color: #6366f1; margin-bottom: 32px;
      }
      .formula-steps {
        display: flex; flex-direction: column; align-items: flex-start; gap: 0;
      }
      .formula-row {
        display: flex; align-items: center; gap: 20px;
        padding: 16px 24px; border-radius: 12px;
        border: 1px solid transparent; width: 100%;
      }
      .formula-row.active {
        border-color: rgba(99,102,241,0.45);
        box-shadow: 0 0 20px rgba(99,102,241,0.08);
      }
      .step-badge {
        width: 40px; height: 40px; border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 18px; color: #fff; flex-shrink: 0;
      }
      .formula-eq { flex: 1; }
      .formula-eq .katex { font-size: 42px; color: #0f172a; }
      .formula-note {
        font-size: 16px; color: #64748b; font-style: italic;
        min-width: 160px; text-align: right;
      }
      .formula-connector {
        margin-left: 44px; height: 32px;
        display: flex; align-items: center;
      }
    </style>

    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <!-- KaTeX CSS: inline as <style id="katex-inline-css"> with local url(./katex/fonts/ — see step-5 (NOT a CDN <link>) -->
    <script src="./katex/katex.min.js"></script>
    <script src="./gsap/gsap.min.js"></script>
    <script>
      // Render equations (replace with actual LaTeX)
      katex.render("a=1,\\ b=-5,\\ c=6", document.getElementById("mt-f-eq-1"), { displayMode: true });
      katex.render("x = \\frac{5 \\pm \\sqrt{25-24}}{2}", document.getElementById("mt-f-eq-2"), { displayMode: true });
      katex.render("x_1 = 3,\\ x_2 = 2", document.getElementById("mt-f-eq-3"), { displayMode: true });

      var SCENE_DURATION = 10;
        var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };

        window.__timelines = window.__timelines || {};
      var tl = gsap.timeline({ paused: true });

        // 0. Scene fade-in
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

      // Panel entrance
      tl.fromTo(".formula-panel",
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.7, ease: "power3.out" }, 0.2);

      tl.fromTo("#mt-f-label",
        { x: -20, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.4, ease: "expo.out" }, 0.5);

      // Step 1: row enters + activates
      tl.fromTo("#mt-f-row-1",
        { x: -30, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 1.0);
      tl.to("#mt-f-row-1", {
        borderColor: "rgba(99,102,241,0.45)",
        boxShadow: "0 0 20px rgba(99,102,241,0.08)",
        duration: 0.3, ease: "power2.out"
      }, 1.3);

      // Connector 1 draws
      tl.fromTo("#mt-f-conn-1 line",
        { attr: { y2: 0 } },
        { attr: { y2: 32 }, duration: 0.3, ease: "power1.out" }, 2.0);

      // Step 1 dims, Step 2 enters + activates
      tl.to("#mt-f-row-1", { opacity: 0.5, borderColor: "transparent", boxShadow: "none", duration: 0.3 }, 2.3);
      tl.fromTo("#mt-f-row-2",
        { x: -30, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 2.3);
      tl.to("#mt-f-row-2", {
        borderColor: "rgba(99,102,241,0.45)",
        boxShadow: "0 0 20px rgba(99,102,241,0.08)",
        duration: 0.3, ease: "power2.out"
      }, 2.6);

      // Connector 2 draws
      tl.fromTo("#mt-f-conn-2 line",
        { attr: { y2: 0 } },
        { attr: { y2: 32 }, duration: 0.3, ease: "power1.out" }, 3.5);

      // Step 2 dims, Step 3 enters + activates
      tl.to("#mt-f-row-2", { opacity: 0.5, borderColor: "transparent", boxShadow: "none", duration: 0.3 }, 3.8);
      tl.fromTo("#mt-f-row-3",
        { x: -30, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 3.8);
      tl.to("#mt-f-row-3", {
        borderColor: "rgba(99,102,241,0.45)",
        boxShadow: "0 0 20px rgba(99,102,241,0.08)",
        duration: 0.3, ease: "power2.out"
      }, 4.1);

      // Ambient: Aurora drift
      tl.fromTo(".a1", { x: 0, y: 0 }, { x: -40, y: 30, duration: 4, ease: "sine.inOut", yoyo: true, repeat: R(4) }, 0);
      tl.fromTo(".a2", { x: 0, y: 0 }, { x: 30, y: -20, duration: 3.5, ease: "sine.inOut", yoyo: true, repeat: R(3.5) }, 0.5);
      tl.fromTo(".a3", { x: 0, y: 0 }, { x: -25, y: 25, duration: 3, ease: "sine.inOut", yoyo: true, repeat: R(3) }, 0.3);

      window.__timelines["mt-formula"] = tl;
    </script>
  </div>
</template>
```

**Adaptation notes:**
- Add/remove `.formula-row` + `.formula-connector` pairs for more/fewer steps
- Adjust GSAP timings to match transcript timestamps for each step
- Change note text from English to Chinese if desired (e.g., "识别系数")
- The dimming pattern (previous step opacity 0.5, current step active glow) keeps viewer focus

---

## Component 3: Geometry Canvas (几何图形渲染)

SVG-based geometric figure with path drawing animation. All shapes draw via `attr:{"stroke-dashoffset": 0}`.

```html
<template id="mt-geometry-template">
  <div data-composition-id="mt-geometry" data-width="1920" data-height="1080">

        <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb a1"></div>
      <div class="aurora-orb a2"></div>
      <div class="aurora-orb a3"></div>
    </div>

    <div class="scene-content">
      <div class="geo-wrapper">
        <div class="geo-canvas glass-panel">
          <svg id="mt-g-svg" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
            <!-- Grid -->
            <g class="grid-bg" id="mt-g-grid">
              <!-- generated programmatically or manually -->
            </g>
            <!-- Main figure: triangle example -->
            <polygon id="mt-g-tri" class="shape-primary"
              points="400,80 100,520 700,520" />
            <!-- Auxiliary: altitude -->
            <line id="mt-g-alt" class="shape-derived"
              x1="400" y1="80" x2="400" y2="520" />
            <!-- Labels -->
            <text id="mt-g-lbl-a" class="geo-label" x="400" y="60" text-anchor="middle">A</text>
            <text id="mt-g-lbl-b" class="geo-label" x="80" y="545" text-anchor="middle">B</text>
            <text id="mt-g-lbl-c" class="geo-label" x="720" y="545" text-anchor="middle">C</text>
            <text id="mt-g-lbl-h" class="geo-label" x="420" y="310" text-anchor="start">H</text>
          </svg>
        </div>

        <div class="geo-info glass-panel">
          <div class="label">GIVEN</div>
          <div class="geo-info-text" id="mt-g-info">
            <!-- Problem conditions rendered here -->
          </div>
        </div>
      </div>
    </div>

    <style>
      [data-composition-id="mt-geometry"] {
        position: relative; width: 100%; height: 100%;
        background: #f8fafc;
        font-family: "Noto Sans SC", Inter, sans-serif;
        color: #0f172a;
        overflow: hidden;
      }
      /* === MANDATORY: Global light-theme color reset === */
      .katex, .katex * { color: #0f172a; }
      .katex-mathml { display: none !important; }
      table, th, td { color: #0f172a; }
      .scene-bg { position: absolute; inset: 0; }
      .bg-texture { position: absolute; inset: 0; z-index: 0; background: url('../bg-texture.jpg') center/cover no-repeat; }
      .aurora-orb { position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none; }
      .a1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(6,182,212,0.48) 0%, transparent 70%); top: -10%; right: -5%; }
      .a2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(99,102,241,0.35) 0%, transparent 70%); bottom: -15%; left: -5%; }
      .a3 { width: 350px; height: 350px; background: radial-gradient(circle, rgba(139,92,246,0.29) 0%, transparent 70%); top: 40%; left: 50%; }
      .scene-content {
        position: relative; z-index: 5;
        width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 60px 80px 180px; box-sizing: border-box;
      }
      .geo-wrapper {
        display: flex; gap: 40px; align-items: stretch; width: 100%;
      }
      .glass-panel {
        background: #ffffff;

        border: 1px solid rgba(99,102,241,0.3);
        border-top: 2px solid rgba(99,102,241,0.25); border-radius: 20px;
        box-shadow: 0 0 40px rgba(99,102,241,0.08), inset 0 1px 0 rgba(255,255,255,0.6);
      }
      .geo-canvas { flex: 2; padding: 32px; }
      .geo-canvas svg { width: 100%; height: 100%; }
      .shape-primary { stroke: #6366f1; stroke-width: 3; fill: none; }
      .shape-derived { stroke: #8b5cf6; stroke-width: 2; fill: none; stroke-dasharray: 8 4; }
      .shape-answer { stroke: #10b981; stroke-width: 3; fill: rgba(16,185,129,0.1); }
      .geo-label { font-family: "KaTeX_Main"; font-size: 28px; fill: #0f172a; }
      .geo-info { flex: 1; padding: 40px; }
      .label {
        font-size: 18px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.12em;
        color: #6366f1; margin-bottom: 20px;
      }
      .geo-info-text {
        font-family: "Noto Sans SC", sans-serif;
        font-size: 24px; line-height: 1.8;
      }
    </style>

    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <script src="./gsap/gsap.min.js"></script>
    <script>
      // Calculate path lengths for drawing animation
      var tri = document.getElementById("mt-g-tri");
      var triLen = tri.getTotalLength();
      tri.setAttribute("stroke-dasharray", triLen);
      tri.setAttribute("stroke-dashoffset", triLen);

      var alt = document.getElementById("mt-g-alt");
      var altLen = alt.getTotalLength();
      alt.setAttribute("stroke-dasharray", altLen);
      alt.setAttribute("stroke-dashoffset", altLen);

      // Hide labels initially
      gsap.set(".geo-label", { opacity: 0 });

      var SCENE_DURATION = 10;
        var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };

        window.__timelines = window.__timelines || {};
      var tl = gsap.timeline({ paused: true });

        // 0. Scene fade-in
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

      // Canvas panel entrance
      tl.fromTo(".geo-canvas",
        { x: -40, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.6, ease: "power3.out" }, 0.2);

      // Info panel entrance
      tl.fromTo(".geo-info",
        { x: 40, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.6, ease: "power3.out" }, 0.4);

      // Draw triangle
      tl.to("#mt-g-tri", {
        attr: {"stroke-dashoffset": 0}, duration: 1.2, ease: "power1.inOut"
      }, 1.0);

      // Show vertex labels one by one
      tl.to("#mt-g-lbl-a", { opacity: 1, duration: 0.3, ease: "power2.out" }, 1.4);
      tl.to("#mt-g-lbl-b", { opacity: 1, duration: 0.3, ease: "power2.out" }, 1.7);
      tl.to("#mt-g-lbl-c", { opacity: 1, duration: 0.3, ease: "power2.out" }, 2.0);

      // Draw altitude (auxiliary line)
      tl.to("#mt-g-alt", {
        attr: {"stroke-dashoffset": 0}, duration: 0.8, ease: "power2.inOut"
      }, 2.5);

      // Show H label
      tl.to("#mt-g-lbl-h", { opacity: 1, duration: 0.3, ease: "power2.out" }, 3.0);

      // Ambient: Aurora drift
      tl.fromTo(".a1", { x: 0, y: 0 }, { x: -40, y: 30, duration: 4, ease: "sine.inOut", yoyo: true, repeat: R(4) }, 0);
      tl.fromTo(".a2", { x: 0, y: 0 }, { x: 30, y: -20, duration: 3.5, ease: "sine.inOut", yoyo: true, repeat: R(3.5) }, 0.5);
      tl.fromTo(".a3", { x: 0, y: 0 }, { x: -25, y: 25, duration: 3, ease: "sine.inOut", yoyo: true, repeat: R(3) }, 0.3);

      window.__timelines["mt-geometry"] = tl;
    </script>
  </div>
</template>
```

**Adaptation notes:**
- **Coordinate computation is mandatory.** Replace the example triangle with the problem's actual geometric figures. Compute ALL vertex coordinates from the problem's mathematical constraints (perpendicularity, similarity, length ratios, Pythagorean theorem) — **never estimate positions visually**. Follow the full workflow in step-5-build-components.md "Geometry Coordinate Accuracy".
- **Perpendicular lines**: before writing coordinates, verify dot product of direction vectors = 0. If two lines should be perpendicular but the dot product is non-zero, the coordinates are wrong — recompute them.
- **Right angle marks (直角符号)**: draw as a small L-shaped open square at the vertex, with edges computed from the actual line direction unit vectors (see step-5 "Right Angle Mark" for the algorithm and worked example). NEVER draw a V-shape or hardcode coordinates by eye.
- **Angle arcs**: for non-right angles, use SVG arc paths with radius ~30 (see step-5 "Angle Arc").
- **Geometry verification block**: write a `<!-- GEOMETRY VERIFICATION -->` block above the SVG with `POINTS:` and `ASSERT` lines for every constraint. The pre-render gate `check_geometry_verification.py` verifies assertions mathematically. See step-5-build-components.md "Geometry Coordinate Accuracy".
- Color code: given info in cyan (`shape-primary`), constructed in purple (`shape-derived`), answer in green (`shape-answer`)
- Use `getTotalLength()` for every path that needs drawing animation; set initial values via `el.setAttribute("stroke-dasharray", len)` and `el.setAttribute("stroke-dashoffset", len)` (NOT `el.style`); animate with `attr:{"stroke-dashoffset": 0}` (NOT raw `strokeDashoffset`)

---

## Component 4: Step Indicator (步骤指示器)

Horizontal progress tracker showing which step is currently active.

```html
<template id="mt-steps-template">
  <div data-composition-id="mt-steps" data-width="1920" data-height="80">

    <div class="step-bar">
      <div class="step-node" id="mt-s-1">1</div>
      <div class="step-connector" id="mt-s-c1"></div>
      <div class="step-node" id="mt-s-2">2</div>
      <div class="step-connector" id="mt-s-c2"></div>
      <div class="step-node" id="mt-s-3">3</div>
    </div>

    <style>
      [data-composition-id="mt-steps"] {
        display: flex; align-items: center; justify-content: center;
        height: 80px;
      }
      .step-bar {
        display: flex; align-items: center; gap: 0;
      }
      .step-node {
        width: 36px; height: 36px; border-radius: 50%;
        border: 2px solid #475569;
        display: flex; align-items: center; justify-content: center;
        font-family: Inter, "Noto Sans SC", sans-serif; font-weight: 700; font-size: 16px;
        color: #475569;
      }
      .step-node.active {
        background: #6366f1; border-color: #6366f1; color: #f8fafc;
        box-shadow: 0 0 16px rgba(99,102,241,0.3);
      }
      .step-node.completed {
        background: #6366f1; border-color: #6366f1; color: #fff;
      }
      .step-connector {
        width: 80px; height: 2px; background: #475569;
      }
      .step-connector.filled { background: #6366f1; }
    </style>

    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <script src="./gsap/gsap.min.js"></script>
    <script>
      var SCENE_DURATION = 10;
        var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };

        window.__timelines = window.__timelines || {};
      var tl = gsap.timeline({ paused: true });

        // 0. Scene fade-in
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

      // Activate step 1
      tl.to("#mt-s-1", {
        backgroundColor: "#6366f1", borderColor: "#6366f1", color: "#f8fafc",
        boxShadow: "0 0 16px rgba(99,102,241,0.3)", scale: 1.2,
        duration: 0.3, ease: "back.out(1.4)"
      }, 0.5);

      // Transition to step 2
      tl.to("#mt-s-1", {
        backgroundColor: "#6366f1", borderColor: "#6366f1", color: "#fff",
        boxShadow: "none", scale: 1, duration: 0.2
      }, 3.0);
      tl.to("#mt-s-c1", { backgroundColor: "#6366f1", duration: 0.3 }, 3.0);
      tl.to("#mt-s-2", {
        backgroundColor: "#6366f1", borderColor: "#6366f1", color: "#f8fafc",
        boxShadow: "0 0 16px rgba(99,102,241,0.3)", scale: 1.2,
        duration: 0.3, ease: "back.out(1.4)"
      }, 3.2);

      // Transition to step 3
      tl.to("#mt-s-2", {
        backgroundColor: "#6366f1", borderColor: "#6366f1", color: "#fff",
        boxShadow: "none", scale: 1, duration: 0.2
      }, 6.0);
      tl.to("#mt-s-c2", { backgroundColor: "#6366f1", duration: 0.3 }, 6.0);
      tl.to("#mt-s-3", {
        backgroundColor: "#6366f1", borderColor: "#6366f1", color: "#f8fafc",
        boxShadow: "0 0 16px rgba(99,102,241,0.3)", scale: 1.2,
        duration: 0.3, ease: "back.out(1.4)"
      }, 6.2);

      window.__timelines["mt-steps"] = tl;
    </script>
  </div>
</template>
```

**Adaptation notes:**
- Add/remove `.step-node` + `.step-connector` pairs to match step count
- Adjust transition timings to match when narration moves to each step
- Can be used as an overlay track (`data-track-index: 2`) at the top of the composition

---

## Component 5: Conclusion Panel (结论面板)

Final takeaway display with numbered summary rows, SVG mini-icons, highlight cycling, and a green-accented answer box with burst animation. For experiment topics, shows 3 key conclusions; for math problems, shows the final answer with a KaTeX equation.

```html
<template id="mt-conclusion-template">
  <div data-composition-id="mt-conclusion" data-width="1920" data-height="1080">

    <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb a1"></div>
      <div class="aurora-orb a2"></div>
      <div class="aurora-orb a3"></div>
    </div>

    <div class="scene-content">
      <div class="conclusion-wrapper">
        <div class="conclusion-panel glass-panel">
          <div class="header-row">
            <div class="label" id="mt-c-label">KEY TAKEAWAYS · 核心结论</div>
            <div class="formula-deco" id="mt-c-deco"></div>
          </div>

          <div class="answer-rows">
            <div class="answer-row" id="mt-c-row-1">
              <div class="step-badge" id="mt-c-badge-1">1</div>
              <div class="row-content">
                <div class="row-title">要点一标题</div>
                <div class="row-text">要点一描述内容</div>
              </div>
              <div class="row-icon">
                <svg width="56" height="56" viewBox="0 0 56 56">
                  <defs>
                    <filter id="mt-c-iconGlow1">
                      <feGaussianBlur stdDeviation="2.5" result="blur"/>
                      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                  </defs>
                  <circle cx="28" cy="28" r="6" fill="#8b5cf6" filter="url(#mt-c-iconGlow1)"/>
                  <circle cx="28" cy="28" r="14" fill="none" stroke="#6366f1" stroke-width="2" opacity="0.7"/>
                  <circle cx="28" cy="28" r="22" fill="none" stroke="#06b6d4" stroke-width="2" opacity="0.4"/>
                  <circle cx="28" cy="14" r="3" fill="#6366f1" filter="url(#mt-c-iconGlow1)"/>
                </svg>
              </div>
            </div>

            <div class="answer-row" id="mt-c-row-2">
              <div class="step-badge" id="mt-c-badge-2">2</div>
              <div class="row-content">
                <div class="row-title">要点二标题</div>
                <div class="row-text">要点二描述内容</div>
              </div>
              <div class="row-icon">
                <svg width="56" height="56" viewBox="0 0 56 56">
                  <defs>
                    <filter id="mt-c-iconGlow2">
                      <feGaussianBlur stdDeviation="3" result="blur"/>
                      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                  </defs>
                  <ellipse cx="28" cy="40" rx="10" ry="3" fill="#475569" stroke="#64748b" stroke-width="1.5"/>
                  <rect x="22" y="28" width="12" height="12" rx="2" fill="#475569" stroke="#64748b" stroke-width="1.5"/>
                  <ellipse cx="28" cy="20" rx="7" ry="11" fill="rgba(99,102,241,0.5)" filter="url(#mt-c-iconGlow2)"/>
                  <ellipse cx="28" cy="22" rx="3.5" ry="6" fill="rgba(139,92,246,0.5)"/>
                </svg>
              </div>
            </div>

            <div class="answer-row" id="mt-c-row-3">
              <div class="step-badge" id="mt-c-badge-3">3</div>
              <div class="row-content">
                <div class="row-title">要点三标题</div>
                <div class="row-text">要点三描述内容</div>
              </div>
              <div class="row-icon">
                <svg width="56" height="56" viewBox="0 0 56 56">
                  <defs>
                    <filter id="mt-c-iconGlow3">
                      <feGaussianBlur stdDeviation="2.5" result="blur"/>
                      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                  </defs>
                  <rect x="14" y="10" width="28" height="36" rx="3" fill="rgba(99,102,241,0.25)" stroke="#6366f1" stroke-width="2" filter="url(#mt-c-iconGlow3)"/>
                  <ellipse cx="28" cy="28" rx="6" ry="9" fill="rgba(139,92,246,0.45)"/>
                  <line x1="14" y1="18" x2="42" y2="18" stroke="#6366f1" stroke-width="1" opacity="0.4"/>
                </svg>
              </div>
            </div>
          </div>

          <div class="answer-box" id="mt-c-answer">
            <div class="answer-text">结论摘要文字</div>
          </div>
        </div>
      </div>
    </div>

    <style>
      [data-composition-id="mt-conclusion"] {
        position: relative; width: 100%; height: 100%;
        background: #f8fafc;
        font-family: "Noto Sans SC", Inter, sans-serif;
        color: #0f172a;
        overflow: hidden;
      }
      /* === MANDATORY: Global light-theme color reset === */
      .katex, .katex * { color: #0f172a; }
      .katex-mathml { display: none !important; }
      table, th, td { color: #0f172a; }

      .scene-bg { position: absolute; inset: 0; }
      .bg-texture { position: absolute; inset: 0; z-index: 0; background: url('../bg-texture.jpg') center/cover no-repeat; }
      .aurora-orb { position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none; }
      .a1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(16,185,129,0.55) 0%, transparent 70%); top: -10%; right: -5%; }
      .a2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(20,184,166,0.4) 0%, transparent 70%); bottom: -15%; left: -5%; }
      .a3 { width: 350px; height: 350px; background: radial-gradient(circle, rgba(6,182,212,0.32) 0%, transparent 70%); top: 40%; left: 50%; }

      .scene-content {
        position: relative; z-index: 5;
        width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 50px 80px 180px; box-sizing: border-box;
      }

      .conclusion-wrapper {
        width: 100%; max-width: 1400px;
        display: flex; flex-direction: column;
      }

      .glass-panel {
        background: #ffffff;

        border-radius: 20px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
      }

      .conclusion-panel {
        border: 1px solid rgba(16,185,129,0.3);
        box-shadow: 0 8px 32px rgba(16,185,129,0.1);
        padding: 50px 64px 56px 64px;
        display: flex; flex-direction: column;
        gap: 28px;
        position: relative;
      }

      .header-row {
        display: flex; align-items: center; justify-content: space-between;
        padding-bottom: 4px;
      }
      .label {
        font-size: 22px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.16em; color: #10b981;
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
      }
      .formula-deco {
        opacity: 0;
      }
      .formula-deco .katex {
        font-size: 30px;
        color: rgba(139,92,246,0.45);
      }
      .formula-deco .katex * {
        color: rgba(139,92,246,0.45);
      }

      .answer-rows {
        display: flex; flex-direction: column; gap: 18px;
      }
      .answer-row {
        display: flex; align-items: center;
        gap: 28px;
        padding: 22px 32px;
        background: rgba(230,240,255,0.4);
        border: 1.5px solid rgba(99,102,241,0.1);
        border-radius: 14px;
        opacity: 1;
      }
      .step-badge {
        width: 56px; height: 56px; border-radius: 50%;
        background: linear-gradient(135deg, #10b981, #6366f1);
        display: flex; align-items: center; justify-content: center;
        font-family: Inter, "Noto Sans SC", sans-serif; font-weight: 700; font-size: 24px; color: #fff;
        flex-shrink: 0;
        box-shadow: 0 2px 12px rgba(16,185,129,0.2);
      }
      .row-content {
        flex: 1; display: flex; align-items: baseline; gap: 24px;
      }
      .row-title {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 32px; font-weight: 700;
        color: #6366f1;
        min-width: 130px;
      }
      .row-text {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 28px; font-weight: 400;
        color: #0f172a;
        line-height: 1.5;
      }
      .row-icon {
        flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        width: 56px; height: 56px;
      }

      .answer-box {
        margin-top: 12px;
        border: 2.5px solid #10b981;
        border-radius: 14px;
        padding: 28px 40px;
        text-align: center;
        background: rgba(16,185,129,0.04);
        box-shadow: 0 4px 20px rgba(16,185,129,0.12);
      }
      .answer-text {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 44px; font-weight: 700;
        color: #10b981;
        letter-spacing: 0.04em;
      }
    </style>

    <!-- KaTeX CSS must be inlined, not loaded via <link> -->
    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <script src="./katex/katex.min.js"></script>
    <script src="./gsap/gsap.min.js"></script>
    <script>
      (function() {
        var SCENE_DURATION = 15;
        var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };

        // KaTeX decorative formula
        try {
          katex.render("E_{photon} = h\\nu", document.getElementById("mt-c-deco"),
            { displayMode: false, throwOnError: false, output: "html" });
        } catch (e) {}

        window.__timelines = window.__timelines || {};
        var tl = gsap.timeline({ paused: true });

        // 0. Scene fade-in
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

        // 1. Conclusion panel entrance
        tl.fromTo(".conclusion-panel",
          { y: 50, opacity: 0, scale: 0.95 },
          { y: 0, opacity: 1, scale: 1, duration: 0.7, ease: "power3.out" }, 0.3);

        // 2. Label slide-in
        tl.fromTo("#mt-c-label",
          { x: -30, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5, ease: "expo.out" }, 0.6);

        // 3. Three takeaway rows entrance
        var rows = [
          { id: "#mt-c-row-1", t: 1.0 },
          { id: "#mt-c-row-2", t: 3.5 },
          { id: "#mt-c-row-3", t: 6.0 }
        ];
        rows.forEach(function(r) {
          tl.fromTo(r.id,
            { x: -30, opacity: 0 },
            { x: 0, opacity: 1, duration: 0.6, ease: "power3.out" }, r.t);
        });

        // 4. Highlight rotation matching VO timing
        function highlight(id, time, hold) {
          tl.to(id, {
            borderColor: "rgba(99,102,241,0.45)",
            boxShadow: "0 0 20px rgba(99,102,241,0.1)",
            duration: 0.4, ease: "power2.out"
          }, time);
          tl.to(id, {
            borderColor: "rgba(99,102,241,0.1)",
            boxShadow: "0 0 0 rgba(99,102,241,0)",
            duration: 0.5, ease: "power2.in"
          }, time + hold);
        }
        function dim(id, time, hold) {
          tl.to(id, { opacity: 0.55, duration: 0.4, ease: "power2.out" }, time);
          tl.to(id, { opacity: 1.0, duration: 0.4, ease: "power2.out" }, time + hold);
        }

        // Row 1 highlight (1.6 - 4.0)
        highlight("#mt-c-row-1", 1.6, 2.4);
        dim("#mt-c-row-2", 1.6, 2.4);
        dim("#mt-c-row-3", 1.6, 2.4);

        // Row 2 highlight (4.2 - 7.5)
        highlight("#mt-c-row-2", 4.2, 3.3);
        dim("#mt-c-row-1", 4.2, 3.3);
        dim("#mt-c-row-3", 4.2, 3.3);

        // Row 3 highlight (7.8 - 11.5)
        highlight("#mt-c-row-3", 7.8, 3.7);
        dim("#mt-c-row-1", 7.8, 3.7);
        dim("#mt-c-row-2", 7.8, 3.7);

        // 5. Badge pulses (continuous)
        var badges = ["#mt-c-badge-1", "#mt-c-badge-2", "#mt-c-badge-3"];
        badges.forEach(function(id, i) {
          tl.fromTo(id,
            { boxShadow: "0 2px 12px rgba(16,185,129,0.15)" },
            { boxShadow: "0 2px 20px rgba(16,185,129,0.4)",
              duration: 1.2, ease: "sine.inOut",
              yoyo: true,
              repeat: R(1.2) },
            1.5 + i * 0.3);
        });

        // 6. Answer-box appears with green burst
        tl.fromTo("#mt-c-answer",
          { y: 30, opacity: 0, scale: 0.85 },
          { y: 0, opacity: 1, scale: 1, duration: 0.7, ease: "back.out(1.4)" }, 12.0);
        tl.to("#mt-c-answer", {
          boxShadow: "0 4px 40px rgba(16,185,129,0.35)",
          duration: 0.5, ease: "power2.out"
        }, 12.5);
        tl.to("#mt-c-answer", {
          boxShadow: "0 4px 20px rgba(16,185,129,0.12)",
          duration: 0.6, ease: "sine.inOut"
        }, 13.0);
        // continuous breathing on answer-box
        tl.fromTo("#mt-c-answer",
          { boxShadow: "0 4px 20px rgba(16,185,129,0.12)" },
          { boxShadow: "0 4px 32px rgba(16,185,129,0.3)",
            duration: 2.0, ease: "sine.inOut",
            yoyo: true, repeat: R(2.0) }, 13.8);

        // 7. Decorative formula fade in
        tl.fromTo("#mt-c-deco",
          { opacity: 0, x: 10 },
          { opacity: 1, x: 0, duration: 0.7, ease: "power2.out" }, 13.5);

        // 8. Ambient: Aurora drift
        tl.fromTo(".a1", { x: 0, y: 0 }, { x: -40, y: 30, duration: 4, ease: "sine.inOut", yoyo: true, repeat: R(4) }, 0);
        tl.fromTo(".a2", { x: 0, y: 0 }, { x: 30, y: -20, duration: 3.5, ease: "sine.inOut", yoyo: true, repeat: R(3.5) }, 0.5);
        tl.fromTo(".a3", { x: 0, y: 0 }, { x: -25, y: 25, duration: 3, ease: "sine.inOut", yoyo: true, repeat: R(3) }, 0.3);

        // 9. Panel shadow breathing
        tl.fromTo(".conclusion-panel",
          { boxShadow: "0 8px 32px rgba(16,185,129,0.10)" },
          { boxShadow: "0 8px 48px rgba(16,185,129,0.22)",
            duration: 2.5, ease: "sine.inOut", yoyo: true, repeat: R(2.5) }, 1.0);

        window.__timelines["mt-conclusion"] = tl;
      })();
    </script>
  </div>
</template>
```

**Adaptation notes:**
- Replace row titles (`.row-title`) and descriptions (`.row-text`) with actual takeaway content.
- SVG icons in `.row-icon` are illustrative placeholders — replace with topic-appropriate 56x56 SVG mini-illustrations (atom model, equipment, glass filter, etc.).
- Highlight cycling times (`1.6`, `4.2`, `7.8`) should align with narration timestamps for each takeaway.
- Answer box text (`.answer-text`) should contain the topic's one-line summary.
- The KaTeX decorative formula in `.formula-deco` is optional — use a relevant equation or remove.
- Badge gradient uses green→indigo (`#10b981` → `#6366f1`) for conclusion emphasis.

---

## Component 6: Flame Color Display (焰色展示)

Grid display of element flame colors using SVG flames on burner bases with glow filters. Layout: 3 core elements (top row) + 3 extension elements (bottom row) + tagline. Each cell enters sequentially, active cell gets highlight border glow. Flames flicker continuously via GSAP yoyo. KaTeX renders element symbols.

```html
<template id="mt-flames-template">
  <div data-composition-id="mt-flames" data-width="1920" data-height="1080">

    <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb a1"></div>
      <div class="aurora-orb a2"></div>
      <div class="aurora-orb a3"></div>
    </div>

    <div class="scene-content">
      <div class="colors-wrapper">
        <div class="header-row">
          <div class="label" id="mt-fl-label">FLAME COLORS · 元素焰色对照</div>
        </div>

        <div class="colors-grid-row" id="mt-fl-row-core">
          <!-- Na -->
          <div class="color-cell core-cell" id="mt-fl-na">
            <div class="cell-top">
              <div class="cell-symbol" id="mt-fl-sym-na"></div>
              <div class="cell-name">钠</div>
            </div>
            <div class="cell-flame">
              <svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <filter id="mt-fl-glow-na"><feGaussianBlur stdDeviation="6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                  <filter id="mt-fl-glow-sm-na"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                </defs>
                <ellipse cx="100" cy="220" rx="48" ry="10" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <rect x="78" y="195" width="44" height="22" rx="4" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <rect x="96" y="178" width="8" height="18" fill="#94a3b8" rx="2"/>
                <ellipse class="flame-outer" id="mt-fl-flame-na" cx="100" cy="120" rx="44" ry="74"
                         fill="rgba(251,191,36,0.5)" filter="url(#mt-fl-glow-na)"/>
                <ellipse class="flame-inner" cx="100" cy="135" rx="24" ry="48"
                         fill="rgba(253,224,71,0.6)" filter="url(#mt-fl-glow-sm-na)"/>
                <ellipse cx="100" cy="155" rx="10" ry="22" fill="rgba(255,255,255,0.5)"/>
              </svg>
            </div>
            <div class="cell-color-label" style="color:#d97706;">黄色 · Yellow</div>
          </div>

          <!-- K -->
          <div class="color-cell core-cell" id="mt-fl-k">
            <div class="cell-top">
              <div class="cell-symbol" id="mt-fl-sym-k"></div>
              <div class="cell-name">钾</div>
            </div>
            <div class="cell-flame">
              <svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <filter id="mt-fl-glow-k"><feGaussianBlur stdDeviation="6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                  <filter id="mt-fl-glow-sm-k"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                </defs>
                <ellipse cx="100" cy="220" rx="48" ry="10" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <rect x="78" y="195" width="44" height="22" rx="4" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <rect x="96" y="178" width="8" height="18" fill="#94a3b8" rx="2"/>
                <ellipse class="flame-outer" id="mt-fl-flame-k" cx="100" cy="120" rx="44" ry="74"
                         fill="rgba(192,132,252,0.5)" filter="url(#mt-fl-glow-k)"/>
                <ellipse class="flame-inner" cx="100" cy="135" rx="24" ry="48"
                         fill="rgba(216,180,254,0.6)" filter="url(#mt-fl-glow-sm-k)"/>
                <ellipse cx="100" cy="155" rx="10" ry="22" fill="rgba(243,232,255,0.55)"/>
              </svg>
            </div>
            <div class="cell-color-label" style="color:#7c3aed;">浅紫 · Light Purple</div>
          </div>

          <!-- Cu -->
          <div class="color-cell core-cell" id="mt-fl-cu">
            <div class="cell-top">
              <div class="cell-symbol" id="mt-fl-sym-cu"></div>
              <div class="cell-name">铜</div>
            </div>
            <div class="cell-flame">
              <svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <filter id="mt-fl-glow-cu"><feGaussianBlur stdDeviation="6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                  <filter id="mt-fl-glow-sm-cu"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                </defs>
                <ellipse cx="100" cy="220" rx="48" ry="10" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <rect x="78" y="195" width="44" height="22" rx="4" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <rect x="96" y="178" width="8" height="18" fill="#94a3b8" rx="2"/>
                <ellipse class="flame-outer" id="mt-fl-flame-cu" cx="100" cy="120" rx="44" ry="74"
                         fill="rgba(34,211,160,0.5)" filter="url(#mt-fl-glow-cu)"/>
                <ellipse class="flame-inner" cx="100" cy="135" rx="24" ry="48"
                         fill="rgba(110,231,183,0.6)" filter="url(#mt-fl-glow-sm-cu)"/>
                <ellipse cx="100" cy="155" rx="10" ry="22" fill="rgba(220,252,231,0.55)"/>
              </svg>
            </div>
            <div class="cell-color-label" style="color:#059669;">绿色 · Green</div>
          </div>
        </div>

        <div class="colors-grid-row ext-row" id="mt-fl-row-ext">
          <!-- Ca -->
          <div class="color-cell ext-cell" id="mt-fl-ca">
            <div class="cell-top">
              <div class="cell-symbol cell-symbol-ext" id="mt-fl-sym-ca"></div>
              <div class="cell-name cell-name-ext">钙</div>
            </div>
            <div class="cell-flame ext-flame">
              <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                <defs><filter id="mt-fl-glow-ca"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
                <ellipse cx="100" cy="184" rx="40" ry="8" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <rect x="82" y="164" width="36" height="18" rx="4" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <ellipse class="flame-outer" id="mt-fl-flame-ca" cx="100" cy="100" rx="36" ry="58"
                         fill="rgba(217,119,87,0.5)" filter="url(#mt-fl-glow-ca)"/>
                <ellipse class="flame-inner" cx="100" cy="115" rx="18" ry="36" fill="rgba(251,146,60,0.55)"/>
                <ellipse cx="100" cy="130" rx="7" ry="16" fill="rgba(254,215,170,0.5)"/>
              </svg>
            </div>
            <div class="cell-color-label cell-color-label-ext" style="color:#c2410c;">砖红色 · Brick Red</div>
          </div>

          <!-- Sr -->
          <div class="color-cell ext-cell" id="mt-fl-sr">
            <div class="cell-top">
              <div class="cell-symbol cell-symbol-ext" id="mt-fl-sym-sr"></div>
              <div class="cell-name cell-name-ext">锶</div>
            </div>
            <div class="cell-flame ext-flame">
              <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                <defs><filter id="mt-fl-glow-sr"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
                <ellipse cx="100" cy="184" rx="40" ry="8" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <rect x="82" y="164" width="36" height="18" rx="4" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <ellipse class="flame-outer" id="mt-fl-flame-sr" cx="100" cy="100" rx="36" ry="58"
                         fill="rgba(244,63,94,0.5)" filter="url(#mt-fl-glow-sr)"/>
                <ellipse class="flame-inner" cx="100" cy="115" rx="18" ry="36" fill="rgba(251,113,133,0.55)"/>
                <ellipse cx="100" cy="130" rx="7" ry="16" fill="rgba(254,205,211,0.5)"/>
              </svg>
            </div>
            <div class="cell-color-label cell-color-label-ext" style="color:#e11d48;">洋红色 · Magenta</div>
          </div>

          <!-- Ba -->
          <div class="color-cell ext-cell" id="mt-fl-ba">
            <div class="cell-top">
              <div class="cell-symbol cell-symbol-ext" id="mt-fl-sym-ba"></div>
              <div class="cell-name cell-name-ext">钡</div>
            </div>
            <div class="cell-flame ext-flame">
              <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
                <defs><filter id="mt-fl-glow-ba"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
                <ellipse cx="100" cy="184" rx="40" ry="8" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <rect x="82" y="164" width="36" height="18" rx="4" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <ellipse class="flame-outer" id="mt-fl-flame-ba" cx="100" cy="100" rx="36" ry="58"
                         fill="rgba(163,230,53,0.5)" filter="url(#mt-fl-glow-ba)"/>
                <ellipse class="flame-inner" cx="100" cy="115" rx="18" ry="36" fill="rgba(190,242,100,0.55)"/>
                <ellipse cx="100" cy="130" rx="7" ry="16" fill="rgba(236,252,203,0.5)"/>
              </svg>
            </div>
            <div class="cell-color-label cell-color-label-ext" style="color:#4d7c0f;">黄绿色 · Yellow-Green</div>
          </div>
        </div>

        <div class="tagline-row" id="mt-fl-tagline">
          <span class="tag-text">颜色即指纹 · Color = Fingerprint</span>
        </div>
      </div>
    </div>

    <style>
      [data-composition-id="mt-flames"] {
        position: relative; width: 100%; height: 100%;
        background: #f8fafc;
        font-family: "Noto Sans SC", Inter, sans-serif;
        color: #0f172a;
        overflow: hidden;
      }
      .katex, .katex * { color: #0f172a; }
      .katex-mathml { display: none !important; }

      .scene-bg { position: absolute; inset: 0; }
      .bg-texture { position: absolute; inset: 0; z-index: 0; background: url('../bg-texture.jpg') center/cover no-repeat; }
      .aurora-orb { position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none; }
      .a1 { width: 460px; height: 460px; background: radial-gradient(circle, rgba(99,102,241,0.45) 0%, transparent 70%); top: -10%; left: -5%; }
      .a2 { width: 380px; height: 380px; background: radial-gradient(circle, rgba(6,182,212,0.35) 0%, transparent 70%); bottom: -12%; right: -3%; }
      .a3 { width: 340px; height: 340px; background: radial-gradient(circle, rgba(139,92,246,0.29) 0%, transparent 70%); top: 35%; left: 60%; }

      .scene-content {
        position: relative; z-index: 5;
        width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 50px 70px 180px; box-sizing: border-box;
      }

      .colors-wrapper {
        width: 100%; max-width: 1760px;
        display: flex; flex-direction: column;
        gap: 24px;
      }

      .header-row {
        display: flex; align-items: center; justify-content: flex-start;
        padding-left: 8px;
      }
      .label {
        font-size: 22px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.16em; color: #6366f1;
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
      }

      .colors-grid-row {
        display: grid; grid-template-columns: repeat(3, 1fr);
      }
      #mt-fl-row-core { gap: 28px; }
      #mt-fl-row-ext { gap: 24px; opacity: 0; }

      .color-cell {
        background: #ffffff;

        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(99,102,241,0.04);
        padding: 22px 24px;
        display: flex; flex-direction: column; align-items: center;
        transition: border-color 0.3s, box-shadow 0.3s;
      }
      .color-cell.active {
        border-color: rgba(99,102,241,0.5);
        box-shadow: 0 4px 24px rgba(99,102,241,0.12);
      }

      .core-cell { padding: 26px 28px; gap: 14px; }
      .ext-cell { padding: 18px 22px; gap: 10px; }

      .cell-top {
        display: flex; align-items: baseline; gap: 16px;
      }
      .cell-symbol .katex { font-size: 44px; }
      .cell-symbol-ext .katex { font-size: 32px; }
      .cell-name {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 30px; font-weight: 600; color: #0f172a;
      }
      .cell-name-ext { font-size: 24px; }

      .cell-flame {
        width: 160px; height: 200px;
        display: flex; align-items: center; justify-content: center;
      }
      .ext-flame { width: 130px; height: 150px; }
      .cell-flame svg { width: 100%; height: 100%; }

      .cell-color-label {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 24px; font-weight: 700;
        text-align: center;
      }
      .cell-color-label-ext { font-size: 20px; }

      .tagline-row {
        display: flex; align-items: center; justify-content: center;
        gap: 20px; margin-top: 8px;
        opacity: 0;
      }
      /* ⚠️ Gradient text below is OK because .tag-text holds PLAIN TEXT.
         NEVER copy this trio (background-clip:text + -webkit-text-fill-color:transparent) onto an
         element that contains a KaTeX formula — the glyphs go transparent and only the fraction bar
         remains, so the equation renders as a stray horizontal dash. Formulas use a solid color. */
      .tag-text {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 32px; font-weight: 700;
        letter-spacing: 0.06em;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
      }
    </style>

    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <!-- KaTeX CSS: inline as <style id="katex-inline-css"> with local url(./katex/fonts/ — see step-5 (NOT a CDN <link>) -->
    <script src="./katex/katex.min.js"></script>
    <script src="./gsap/gsap.min.js"></script>
    <script>
      (function() {
        // KaTeX render element symbols
        katex.render("\\mathrm{Na}", document.getElementById("mt-fl-sym-na"), { displayMode: false, output: "html" });
        katex.render("\\mathrm{K}", document.getElementById("mt-fl-sym-k"), { displayMode: false, output: "html" });
        katex.render("\\mathrm{Cu}", document.getElementById("mt-fl-sym-cu"), { displayMode: false, output: "html" });
        katex.render("\\mathrm{Ca}", document.getElementById("mt-fl-sym-ca"), { displayMode: false, output: "html" });
        katex.render("\\mathrm{Sr}", document.getElementById("mt-fl-sym-sr"), { displayMode: false, output: "html" });
        katex.render("\\mathrm{Ba}", document.getElementById("mt-fl-sym-ba"), { displayMode: false, output: "html" });

        var SCENE_DURATION = 19.5;
        var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };

        window.__timelines = window.__timelines || {};
        var tl = gsap.timeline({ paused: true });

        // 0. Scene fade-in
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

        // 1. Label slide-in
        tl.fromTo("#mt-fl-label",
          { x: -30, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5, ease: "expo.out" }, 0.3);

        // 2. Core row cells stagger entrance
        var coreCells = [
          { id: "#mt-fl-na", t: 0.5 },
          { id: "#mt-fl-k",  t: 1.5 },
          { id: "#mt-fl-cu", t: 2.5 }
        ];
        coreCells.forEach(function(c) {
          tl.fromTo(c.id,
            { y: 40, opacity: 0, scale: 0.9 },
            { y: 0, opacity: 1, scale: 1, duration: 0.7, ease: "back.out(1.4)" }, c.t);
        });

        // 3. Highlight rotation matching VO
        function highlightCell(id, time, hold) {
          tl.to(id, {
            borderColor: "rgba(99,102,241,0.5)",
            boxShadow: "0 4px 24px rgba(99,102,241,0.15)",
            duration: 0.4, ease: "power2.out"
          }, time);
          tl.to(id, {
            borderColor: "rgba(99,102,241,0.15)",
            boxShadow: "0 2px 12px rgba(99,102,241,0.04)",
            duration: 0.4, ease: "power2.in"
          }, time + hold);
        }
        highlightCell("#mt-fl-na", 5.0, 1.3);
        highlightCell("#mt-fl-k",  6.5, 1.3);
        highlightCell("#mt-fl-cu", 8.0, 1.5);

        // 4. Extension row entrance at 11.0s
        tl.to("#mt-fl-row-ext",
          { opacity: 0.85, duration: 0.5, ease: "power2.out" }, 11.0);
        var extCells = [
          { id: "#mt-fl-ca", t: 11.2 },
          { id: "#mt-fl-sr", t: 12.0 },
          { id: "#mt-fl-ba", t: 12.8 }
        ];
        extCells.forEach(function(c) {
          tl.fromTo(c.id,
            { y: 30, opacity: 0, scale: 0.92 },
            { y: 0, opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.3)" }, c.t);
        });

        // 5. Tagline at 17.5s
        tl.fromTo("#mt-fl-tagline",
          { opacity: 0, y: 20, scale: 0.95 },
          { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: "back.out(1.4)" }, 17.5);

        // 6. Continuous flame flicker (staggered)
        var flames = [
          { id: "#mt-fl-flame-na", dur: 0.42, off: 0.00 },
          { id: "#mt-fl-flame-k",  dur: 0.46, off: 0.05 },
          { id: "#mt-fl-flame-cu", dur: 0.44, off: 0.10 },
          { id: "#mt-fl-flame-ca", dur: 0.48, off: 0.15 },
          { id: "#mt-fl-flame-sr", dur: 0.47, off: 0.20 },
          { id: "#mt-fl-flame-ba", dur: 0.43, off: 0.25 }
        ];
        flames.forEach(function(f) {
          tl.fromTo(f.id,
            { scaleY: 0.9, scaleX: 0.95, transformOrigin: "50% 100%" },
            { scaleY: 1.1, scaleX: 1.05, transformOrigin: "50% 100%",
              duration: f.dur, ease: "sine.inOut",
              yoyo: true, repeat: R(f.dur) },
            0.3 + f.off);
          tl.fromTo(f.id,
            { opacity: 0.8 },
            { opacity: 1.0, duration: f.dur * 1.3, ease: "sine.inOut",
              yoyo: true, repeat: R(f.dur * 1.3) },
            0.4 + f.off);
        });

        // 7. Inner flame subtle pulse
        var innerFlames = document.querySelectorAll("[data-composition-id='mt-flames'] .flame-inner");
        for (var i = 0; i < innerFlames.length; i++) {
          var el = innerFlames[i];
          tl.fromTo(el,
            { scaleY: 0.92, transformOrigin: "50% 100%" },
            { scaleY: 1.08, transformOrigin: "50% 100%",
              duration: 0.55 + i * 0.03, ease: "sine.inOut",
              yoyo: true, repeat: R(0.55 + i * 0.03) },
            0.5 + i * 0.07);
        }

        // 8. Ambient: Aurora drift
        tl.fromTo(".a1", { x: 0, y: 0 }, { x: -40, y: 30, duration: 4, ease: "sine.inOut", yoyo: true, repeat: R(4) }, 0);
        tl.fromTo(".a2", { x: 0, y: 0 }, { x: 30, y: -20, duration: 3.5, ease: "sine.inOut", yoyo: true, repeat: R(3.5) }, 0.5);
        tl.fromTo(".a3", { x: 0, y: 0 }, { x: -25, y: 25, duration: 3, ease: "sine.inOut", yoyo: true, repeat: R(3) }, 0.3);

        window.__timelines["mt-flames"] = tl;
      })();
    </script>
  </div>
</template>
```

**Adaptation notes:**
- Cell entrance timings (`.coreCells`, `.extCells`) should match narration timestamps.
- Highlight cycling times (`5.0`, `6.5`, `8.0`) should match when narration describes each element.
- SVG flames use 3-layer ellipses (outer/inner/core) with glow filters on burner bases — much more realistic than CSS-only flames.
- KaTeX element symbols use `\mathrm{Na}` format with `output: "html"`.
- Extension row (Ca, Sr, Ba) enters as a group with staggered cell pop-ins.
- Tagline uses indigo→violet gradient text for the light theme.
- Burner bases use neutral gray `#475569` which works on both light and dark backgrounds.
- For other elements, copy a cell block and change: SVG fill colors, element symbol, Chinese name, color label text + inline color.

---

## Component 7: Title Opening (标题开场)

Full-screen title card introducing the tutorial topic. Features an aurora mesh background with three drifting gradient orbs, a subtle dot grid overlay, floating academic symbols at low opacity with continuous drift, decorative SVG particle bursts (six radial clusters in varied colors), and a staggered character reveal for the main Chinese title with indigo gradient fill. The title block sits on a frosted glass panel with breathing box-shadow. All GSAP animations are seek-safe (`paused: true`, `fromTo()` only, no `@keyframes` or `Math.random()`). Replace placeholder text with actual topic content before use.

```html
<template id="mt-title-template">
  <div data-composition-id="mt-title" data-width="1920" data-height="1080">
    <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb a1"></div>
      <div class="aurora-orb a2"></div>
      <div class="aurora-orb a3"></div>
      <!-- Floating academic symbols (background decoration) -->
      <div class="float-symbol" id="mt-sym-1" style="top:18%; left:12%;">x&#178;</div>
      <div class="float-symbol" id="mt-sym-2" style="top:28%; right:14%;">&#960;</div>
      <div class="float-symbol" id="mt-sym-3" style="top:72%; left:18%;">&#931;</div>
      <div class="float-symbol" id="mt-sym-4" style="top:78%; right:20%;">&#8747;</div>
      <div class="float-symbol" id="mt-sym-5" style="top:14%; right:38%;">&#8734;</div>
    </div>
    <div class="scene-content">
      <!-- Decorative particle bursts SVG layer -->
      <svg class="firework-layer" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <filter id="bigGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          <filter id="rayGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        <!-- Particle cluster 1: yellow, top-left -->
        <g id="mt-fw-1" transform="translate(380,260)">
          <circle class="fw-core" cx="0" cy="0" r="20" fill="#fbbf24" filter="url(#bigGlow)" opacity="0"/>
          <g class="fw-particles">
            <circle cx="0" cy="-90" r="10" fill="#fbbf24" filter="url(#rayGlow)"/>
            <circle cx="64" cy="-64" r="10" fill="#fde68a" filter="url(#rayGlow)"/>
            <circle cx="90" cy="0" r="10" fill="#fbbf24" filter="url(#rayGlow)"/>
            <circle cx="64" cy="64" r="10" fill="#fde68a" filter="url(#rayGlow)"/>
            <circle cx="0" cy="90" r="10" fill="#fbbf24" filter="url(#rayGlow)"/>
            <circle cx="-64" cy="64" r="10" fill="#fde68a" filter="url(#rayGlow)"/>
            <circle cx="-90" cy="0" r="10" fill="#fbbf24" filter="url(#rayGlow)"/>
            <circle cx="-64" cy="-64" r="10" fill="#fde68a" filter="url(#rayGlow)"/>
          </g>
        </g>

        <!-- Particle cluster 2: violet, top-right -->
        <g id="mt-fw-2" transform="translate(1520,240)">
          <circle class="fw-core" cx="0" cy="0" r="22" fill="#8b5cf6" filter="url(#bigGlow)" opacity="0"/>
          <g class="fw-particles">
            <circle cx="0" cy="-100" r="11" fill="#8b5cf6" filter="url(#rayGlow)"/>
            <circle cx="71" cy="-71" r="11" fill="#a78bfa" filter="url(#rayGlow)"/>
            <circle cx="100" cy="0" r="11" fill="#8b5cf6" filter="url(#rayGlow)"/>
            <circle cx="71" cy="71" r="11" fill="#a78bfa" filter="url(#rayGlow)"/>
            <circle cx="0" cy="100" r="11" fill="#8b5cf6" filter="url(#rayGlow)"/>
            <circle cx="-71" cy="71" r="11" fill="#a78bfa" filter="url(#rayGlow)"/>
            <circle cx="-100" cy="0" r="11" fill="#8b5cf6" filter="url(#rayGlow)"/>
            <circle cx="-71" cy="-71" r="11" fill="#a78bfa" filter="url(#rayGlow)"/>
          </g>
        </g>

        <!-- Particle cluster 3: emerald, bottom-left -->
        <g id="mt-fw-3" transform="translate(320,820)">
          <circle class="fw-core" cx="0" cy="0" r="20" fill="#10b981" filter="url(#bigGlow)" opacity="0"/>
          <g class="fw-particles">
            <circle cx="0" cy="-85" r="10" fill="#10b981" filter="url(#rayGlow)"/>
            <circle cx="60" cy="-60" r="10" fill="#34d399" filter="url(#rayGlow)"/>
            <circle cx="85" cy="0" r="10" fill="#10b981" filter="url(#rayGlow)"/>
            <circle cx="60" cy="60" r="10" fill="#34d399" filter="url(#rayGlow)"/>
            <circle cx="0" cy="85" r="10" fill="#10b981" filter="url(#rayGlow)"/>
            <circle cx="-60" cy="60" r="10" fill="#34d399" filter="url(#rayGlow)"/>
            <circle cx="-85" cy="0" r="10" fill="#10b981" filter="url(#rayGlow)"/>
            <circle cx="-60" cy="-60" r="10" fill="#34d399" filter="url(#rayGlow)"/>
          </g>
        </g>

        <!-- Particle cluster 4: indigo, bottom-right -->
        <g id="mt-fw-4" transform="translate(1580,840)">
          <circle class="fw-core" cx="0" cy="0" r="22" fill="#6366f1" filter="url(#bigGlow)" opacity="0"/>
          <g class="fw-particles">
            <circle cx="0" cy="-95" r="11" fill="#6366f1" filter="url(#rayGlow)"/>
            <circle cx="67" cy="-67" r="11" fill="#a5b4fc" filter="url(#rayGlow)"/>
            <circle cx="95" cy="0" r="11" fill="#6366f1" filter="url(#rayGlow)"/>
            <circle cx="67" cy="67" r="11" fill="#a5b4fc" filter="url(#rayGlow)"/>
            <circle cx="0" cy="95" r="11" fill="#6366f1" filter="url(#rayGlow)"/>
            <circle cx="-67" cy="67" r="11" fill="#a5b4fc" filter="url(#rayGlow)"/>
            <circle cx="-95" cy="0" r="11" fill="#6366f1" filter="url(#rayGlow)"/>
            <circle cx="-67" cy="-67" r="11" fill="#a5b4fc" filter="url(#rayGlow)"/>
          </g>
        </g>

        <!-- Particle cluster 5: magenta, top-center -->
        <g id="mt-fw-5" transform="translate(960,180)">
          <circle class="fw-core" cx="0" cy="0" r="18" fill="#ec4899" filter="url(#bigGlow)" opacity="0"/>
          <g class="fw-particles">
            <circle cx="0" cy="-75" r="9" fill="#ec4899" filter="url(#rayGlow)"/>
            <circle cx="53" cy="-53" r="9" fill="#f9a8d4" filter="url(#rayGlow)"/>
            <circle cx="75" cy="0" r="9" fill="#ec4899" filter="url(#rayGlow)"/>
            <circle cx="53" cy="53" r="9" fill="#f9a8d4" filter="url(#rayGlow)"/>
            <circle cx="0" cy="75" r="9" fill="#ec4899" filter="url(#rayGlow)"/>
            <circle cx="-53" cy="53" r="9" fill="#f9a8d4" filter="url(#rayGlow)"/>
            <circle cx="-75" cy="0" r="9" fill="#ec4899" filter="url(#rayGlow)"/>
            <circle cx="-53" cy="-53" r="9" fill="#f9a8d4" filter="url(#rayGlow)"/>
          </g>
        </g>

        <!-- Particle cluster 6: orange, bottom-center -->
        <g id="mt-fw-6" transform="translate(960,920)">
          <circle class="fw-core" cx="0" cy="0" r="20" fill="#fb923c" filter="url(#bigGlow)" opacity="0"/>
          <g class="fw-particles">
            <circle cx="0" cy="-80" r="10" fill="#fb923c" filter="url(#rayGlow)"/>
            <circle cx="57" cy="-57" r="10" fill="#fdba74" filter="url(#rayGlow)"/>
            <circle cx="80" cy="0" r="10" fill="#fb923c" filter="url(#rayGlow)"/>
            <circle cx="57" cy="57" r="10" fill="#fdba74" filter="url(#rayGlow)"/>
            <circle cx="0" cy="80" r="10" fill="#fb923c" filter="url(#rayGlow)"/>
            <circle cx="-57" cy="57" r="10" fill="#fdba74" filter="url(#rayGlow)"/>
            <circle cx="-80" cy="0" r="10" fill="#fb923c" filter="url(#rayGlow)"/>
            <circle cx="-57" cy="-57" r="10" fill="#fdba74" filter="url(#rayGlow)"/>
          </g>
        </g>
      </svg>

      <!-- Title block (glass panel) -->
      <div class="title-block">
        <div class="eyebrow" id="mt-eyebrow">MATH · 数学课堂</div>
        <h1 class="main-title">
          <span class="title-char">课</span><span class="title-char">题</span><span class="title-char">标</span><span class="title-char">题</span>
        </h1>
        <div class="subtitle" id="mt-subtitle">Subtitle · 知识要点全面解析</div>
        <div class="title-underline" id="mt-underline"></div>
      </div>
    </div>

    <style>
      [data-composition-id="mt-title"] {
        position: relative; width: 100%; height: 100%;
        background: #f8fafc;
        font-family: "Noto Sans SC", Inter, sans-serif;
        color: #0f172a;
        overflow: hidden;
      }

      /* KaTeX & table overrides */
      [data-composition-id="mt-title"] .katex,
      [data-composition-id="mt-title"] .katex * { color: #0f172a; }
      .katex-mathml { display: none !important; }
      table, th, td { color: #0f172a; }

      /* Aurora mesh background */
      .scene-bg { position: absolute; inset: 0; }
      .bg-texture { position: absolute; inset: 0; z-index: 0; background: url('../bg-texture.jpg') center/cover no-repeat; }
      .aurora-orb { position: absolute; border-radius: 50%; filter: blur(80px); pointer-events: none; }
      .a1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(99,102,241,0.55) 0%, transparent 70%); top: -10%; right: -5%; }
      .a2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(139,92,246,0.4) 0%, transparent 70%); bottom: -15%; left: -5%; }
      .a3 { width: 350px; height: 350px; background: radial-gradient(circle, rgba(6,182,212,0.32) 0%, transparent 70%); top: 40%; left: 50%; }

      .float-symbol {
        position: absolute;
        font-family: "KaTeX_Main", "Inter", serif;
        font-size: 96px;
        font-weight: 700;
        color: #0f172a;
        opacity: 0;
        letter-spacing: 0.02em;
        pointer-events: none;
        z-index: 3;
        text-shadow: 0 0 20px rgba(99,102,241,0.15);
      }

      .scene-content {
        position: relative; z-index: 4;
        width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 0 0 180px; box-sizing: border-box;
      }

      .firework-layer {
        position: absolute;
        inset: 0;
        width: 100%; height: 100%;
        pointer-events: none;
      }

      .title-block {
        position: relative;
        z-index: 2;
        text-align: center;
        max-width: 1400px;
        padding: 60px 80px;
        border-radius: 24px;
        background: #ffffff;


        border: 1px solid rgba(99,102,241,0.3);
        border-top: 2px solid rgba(99,102,241,0.25);
        box-shadow: 0 4px 30px rgba(99,102,241,0.08);
      }
      .eyebrow {
        font-family: "Noto Sans SC", Inter, sans-serif;
        font-size: 22px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.32em;
        color: #6366f1;
        margin-bottom: 36px;
        opacity: 0;
      }
      .main-title {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 180px;
        font-weight: 700;
        line-height: 1.05;
        letter-spacing: 0.08em;
        margin: 0 0 28px 0;
        color: #0f172a;
        display: flex;
        justify-content: center;
        gap: 16px;
      }
      /* ⚠️ Gradient text below is OK because .title-char holds a PLAIN-TEXT character.
         NEVER copy this trio onto a KaTeX formula element — glyphs go transparent and only the
         fraction bar survives, so the equation shows as a stray horizontal dash. Formulas use a solid color. */
      .title-char {
        display: inline-block;
        background: linear-gradient(180deg, #1e1b4b 0%, #4338ca 50%, #6366f1 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow:
          0 0 30px rgba(99,102,241,0.3),
          0 0 60px rgba(99,102,241,0.15);
        opacity: 0;
      }
      .subtitle {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 38px;
        font-weight: 400;
        color: #64748b;
        letter-spacing: 0.06em;
        margin-top: 24px;
        opacity: 0;
      }
      .title-underline {
        width: 0px; height: 4px;
        margin: 36px auto 0 auto;
        background: linear-gradient(90deg, transparent 0%, #6366f1 50%, transparent 100%);
        box-shadow: 0 0 20px rgba(99,102,241,0.4);
        border-radius: 2px;
      }

      /* Initial state: hide all particle burst circles */
      .fw-particles circle { opacity: 0; }
    </style>

    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <script src="./gsap/gsap.min.js"></script>
    <script>
      (function(){
        var SCENE_DURATION = 12.2;
        var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };
        window.__timelines = window.__timelines || {};
        var tl = gsap.timeline({ paused: true });

        // 0. Scene fade-in
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

        // 1. Aurora orb drift (3 orbs, yoyo motion)
        tl.fromTo(".a1",
          { x: 0, y: 0 },
          { x: -30, y: 20, duration: 4, ease: "sine.inOut",
            yoyo: true, repeat: R(4) }, 0);
        tl.fromTo(".a2",
          { x: 0, y: 0 },
          { x: 25, y: -18, duration: 5, ease: "sine.inOut",
            yoyo: true, repeat: R(5) }, 0);
        tl.fromTo(".a3",
          { x: 0, y: 0 },
          { x: -20, y: 25, duration: 3.5, ease: "sine.inOut",
            yoyo: true, repeat: R(3.5) }, 0);

        // 2. Panel shadow breathing on title-block
        tl.fromTo(".title-block",
          { boxShadow: "0 4px 30px rgba(99,102,241,0.08)" },
          { boxShadow: "0 4px 40px rgba(99,102,241,0.18)",
            duration: 2.0, ease: "sine.inOut",
            yoyo: true, repeat: R(2.0) }, 0);

        // 3. Floating academic symbols drift (continuous)
        var symbols = [
          { id: "#mt-sym-1", dx: 14, dy: -10, dur: 3.5 },
          { id: "#mt-sym-2", dx: -12, dy: 14, dur: 4.0 },
          { id: "#mt-sym-3", dx: 16, dy: 12, dur: 3.2 },
          { id: "#mt-sym-4", dx: -14, dy: -12, dur: 3.8 },
          { id: "#mt-sym-5", dx: 10, dy: 16, dur: 4.2 }
        ];
        symbols.forEach(function(s, i) {
          tl.fromTo(s.id,
            { x: 0, y: 0, opacity: 0 },
            { opacity: 0.05, duration: 1.2, ease: "power2.out" }, 0.4 + i * 0.1);
          tl.fromTo(s.id,
            { x: 0, y: 0 },
            { x: s.dx, y: s.dy, duration: s.dur, ease: "sine.inOut",
              yoyo: true, repeat: R(s.dur) },
            0.5);
        });

        // 4. Particle burst explosions -- staggered with periodic re-explosion
        var fireworks = [
          { id: "#mt-fw-1", start: 0.5, period: 2.5 },
          { id: "#mt-fw-2", start: 0.7, period: 3.0 },
          { id: "#mt-fw-3", start: 0.9, period: 2.8 },
          { id: "#mt-fw-4", start: 1.1, period: 2.6 },
          { id: "#mt-fw-5", start: 0.6, period: 3.2 },
          { id: "#mt-fw-6", start: 1.0, period: 2.7 }
        ];

        fireworks.forEach(function(fw) {
          var coreSel = fw.id + " .fw-core";
          var partSel = fw.id + " .fw-particles circle";
          var groupSel = fw.id + " .fw-particles";
          var reps = Math.ceil((SCENE_DURATION - fw.start) / fw.period) - 1;

          // Core flash
          tl.fromTo(coreSel,
            { opacity: 0, attr: { r: 6 } },
            { opacity: 0.9, attr: { r: 24 }, duration: 0.25, ease: "power2.out",
              repeat: reps, repeatDelay: fw.period - 0.25 },
            fw.start);
          tl.fromTo(coreSel,
            { opacity: 0.9 },
            { opacity: 0, duration: 0.6, ease: "power2.in",
              repeat: reps, repeatDelay: fw.period - 0.6 },
            fw.start + 0.25);

          // Particle radial burst
          tl.fromTo(partSel,
            { opacity: 0, scale: 0.1, transformOrigin: "0px 0px" },
            { opacity: 1, scale: 1.0, duration: 0.7, ease: "power2.out",
              transformOrigin: "0px 0px",
              repeat: reps, repeatDelay: fw.period - 0.7 },
            fw.start);
          tl.fromTo(partSel,
            { opacity: 1, scale: 1.0 },
            { opacity: 0, scale: 1.5, duration: 0.9, ease: "power1.in",
              transformOrigin: "0px 0px",
              repeat: reps, repeatDelay: fw.period - 0.9 },
            fw.start + 0.7);

          // Group rotation for variation
          tl.fromTo(groupSel,
            { rotation: 0, transformOrigin: "0px 0px" },
            { rotation: 22.5, duration: fw.period, ease: "none",
              transformOrigin: "0px 0px",
              repeat: R(fw.period) },
            fw.start);
        });

        // 5. Eyebrow label
        tl.fromTo("#mt-eyebrow",
          { y: -10, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6, ease: "power2.out" }, 1.0);

        // 6. Main title -- character stagger reveal
        tl.fromTo(".title-char",
          { y: 40, opacity: 0, scale: 0.85 },
          { y: 0, opacity: 1, scale: 1, duration: 0.7, ease: "back.out(1.4)",
            stagger: 0.12 }, 1.5);

        // 7. Indigo glow pulse on title chars
        tl.fromTo(".title-char",
          { textShadow: "0 0 30px rgba(99,102,241,0.3), 0 0 60px rgba(99,102,241,0.15)" },
          { textShadow: "0 0 50px rgba(99,102,241,0.6), 0 0 90px rgba(99,102,241,0.3)",
            duration: 1.6, ease: "sine.inOut",
            yoyo: true, repeat: Math.ceil((SCENE_DURATION - 2.4) / 1.6) - 1 },
          2.4);

        // 8. Subtitle
        tl.fromTo("#mt-subtitle",
          { y: 20, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.7, ease: "power2.out" }, 2.5);

        // 9. Underline expand
        tl.fromTo("#mt-underline",
          { width: 0 },
          { width: 480, duration: 0.9, ease: "power3.out" }, 2.9);

        window.__timelines["mt-title"] = tl;
      })();
    </script>
  </div>
</template>
```

**Adaptation notes:**
- Replace the four `<span class="title-char">` placeholder characters ("课题标题") with your topic title (e.g., "二次函数", "勾股定理"). Add or remove spans to match the character count of the real title.
- Update `.eyebrow` text ("MATH · 数学课堂") to match the subject area (e.g., "ALGEBRA · 代数" or "GEOMETRY · 几何").
- Update `.subtitle` text ("Subtitle · 知识要点全面解析") with a descriptive tagline for the specific lesson.
- Floating math symbols (x-squared, pi, Sigma, integral, infinity) can be swapped for topic-relevant notation by editing the `.float-symbol` div contents.
- Adjust `SCENE_DURATION` to match your voiceover length; the `R()` helper and inline repeat counts scale automatically.
- The `.title-block` panel is OPAQUE (`#ffffff`, no backdrop-filter) — depth via border + layered box-shadow.
- Particle cluster colors (yellow, violet, emerald, indigo, magenta, orange) are decorative and can be recolored per-topic by updating the SVG `fill` attributes on each cluster.
- All Chinese text elements expect `"Noto Sans SC"` or `"PingFang SC"` to be available; load the font via a `<link>` tag if rendering outside a CJK-capable system.
- The `data-composition-id` is `mt-title`; reference this ID when wiring into an index.html timeline for seek binding.

---

## Component 8: Experiment Equipment Cards (实验器材展示)

Displays a row of five equipment cards with SVG illustrations, staggered entrance animations, sequential highlight cycling, and continuous micro-animations (element pulses, liquid waves, cap bobs). Uses the Aurora Scholar light theme with frosted-glass card panels, aurora mesh background, and indigo/violet accents. Equipment names and notes are generic placeholders for adaptation to any experiment type.

```html
<template id="mt-equipment-template">
  <div data-composition-id="mt-equipment" data-width="1920" data-height="1080">
    <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb a1"></div>
      <div class="aurora-orb a2"></div>
      <div class="aurora-orb a3"></div>
    </div>
    <div class="scene-content">
      <div class="equipment-wrapper">
        <div class="header-row">
          <div class="label" id="mt-eq-label">EQUIPMENT · 实验器材</div>
        </div>
        <div class="cards-grid">

          <!-- Card 1: 器材 A -->
          <div class="eq-card glass-mini" id="mt-card-1">
            <div class="eq-svg">
              <svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <filter id="bigGlow1"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                  <filter id="rayGlow1"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                </defs>
                <!-- outer flame -->
                <ellipse id="mt-flame-outer" cx="100" cy="80" rx="32" ry="55"
                         fill="rgba(99,102,241,0.35)" filter="url(#bigGlow1)"/>
                <!-- inner flame -->
                <ellipse id="mt-flame-inner" cx="100" cy="90" rx="18" ry="38"
                         fill="rgba(99,102,241,0.55)" filter="url(#rayGlow1)"/>
                <!-- core -->
                <ellipse cx="100" cy="105" rx="9" ry="20" fill="rgba(139,92,246,0.6)"/>
                <!-- wick -->
                <rect x="96" y="130" width="8" height="22" fill="#64748b" rx="2"/>
                <!-- lamp neck -->
                <rect x="80" y="148" width="40" height="14" rx="3"
                      fill="#1e293b" stroke="#475569" stroke-width="2"/>
                <!-- lamp body (glass) -->
                <path d="M 60,162 L 60,210 Q 60,222 72,222 L 128,222 Q 140,222 140,210 L 140,162 Z"
                      fill="rgba(99,102,241,0.18)" stroke="#6366f1" stroke-width="3"/>
                <!-- liquid level -->
                <line x1="65" y1="190" x2="135" y2="190" stroke="rgba(99,102,241,0.4)" stroke-width="2"/>
              </svg>
            </div>
            <div class="eq-name">器材 A</div>
            <div class="eq-note">用途说明 A</div>
          </div>

          <!-- Card 2: 器材 B -->
          <div class="eq-card glass-mini" id="mt-card-2">
            <div class="eq-svg">
              <svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <filter id="rayGlow2"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                </defs>
                <!-- wooden handle -->
                <rect x="55" y="160" width="90" height="32" rx="6"
                      fill="#7c4a1f" stroke="#a06a35" stroke-width="2"/>
                <rect x="55" y="160" width="90" height="6" fill="rgba(0,0,0,0.05)"/>
                <!-- ferrule -->
                <rect x="138" y="166" width="14" height="20" rx="2"
                      fill="#475569" stroke="#64748b" stroke-width="2"/>
                <!-- wire -->
                <line x1="152" y1="176" x2="100" y2="60"
                      stroke="#64748b" stroke-width="4" stroke-linecap="round" filter="url(#rayGlow2)"/>
                <!-- wire tip glow -->
                <circle id="mt-wire-tip" cx="100" cy="60" r="6"
                        fill="#6366f1" filter="url(#rayGlow2)"/>
                <!-- handle label -->
                <rect x="70" y="172" width="50" height="10" rx="2" fill="rgba(0,0,0,0.15)"/>
              </svg>
            </div>
            <div class="eq-name">器材 B</div>
            <div class="eq-note">用途说明 B</div>
          </div>

          <!-- Card 3: 器材 C -->
          <div class="eq-card glass-mini" id="mt-card-3">
            <div class="eq-svg">
              <svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <filter id="rayGlow3"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                </defs>
                <!-- bottle neck -->
                <rect x="88" y="40" width="24" height="22" fill="#1e293b" stroke="#475569" stroke-width="2"/>
                <!-- stopper -->
                <rect x="84" y="32" width="32" height="12" rx="2" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <!-- conical flask body -->
                <path d="M 92,62 L 92,100 L 50,210 Q 48,220 60,220 L 140,220 Q 152,220 150,210 L 108,100 L 108,62 Z"
                      fill="rgba(148,163,184,0.15)" stroke="#64748b" stroke-width="3"/>
                <!-- liquid -->
                <path id="mt-liquid" d="M 65,170 L 135,170 L 145,210 Q 147,218 138,218 L 62,218 Q 53,218 55,210 Z"
                      fill="rgba(99,102,241,0.25)" stroke="rgba(99,102,241,0.5)" stroke-width="2" filter="url(#rayGlow3)"/>
                <!-- label -->
                <rect x="70" y="135" width="60" height="32" rx="3" fill="rgba(255,255,255,0.95)" stroke="#64748b" stroke-width="2"/>
                <text x="100" y="156" text-anchor="middle"
                      font-family="'Noto Sans SC','PingFang SC',sans-serif" font-size="20" font-weight="700" fill="#0f172a">试剂</text>
              </svg>
            </div>
            <div class="eq-name">器材 C</div>
            <div class="eq-note">用途说明 C</div>
          </div>

          <!-- Card 4: 器材 D -->
          <div class="eq-card glass-mini" id="mt-card-4">
            <div class="eq-svg">
              <svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <filter id="rayGlow4"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                </defs>
                <!-- Bottle 1 yellow cap -->
                <g id="mt-bot-1">
                  <rect x="22" y="70" width="48" height="14" rx="3" fill="#fbbf24" stroke="#fde68a" stroke-width="2"/>
                  <rect x="28" y="64" width="36" height="10" rx="2" fill="#fbbf24"/>
                  <rect x="20" y="84" width="52" height="120" rx="6"
                        fill="rgba(148,163,184,0.2)" stroke="#64748b" stroke-width="3"/>
                  <rect x="26" y="170" width="40" height="28" fill="rgba(251,191,36,0.25)"/>
                  <rect x="24" y="120" width="44" height="22" rx="2" fill="rgba(255,255,255,0.95)"/>
                  <text x="46" y="136" text-anchor="middle"
                        font-family="'Noto Sans SC','PingFang SC',sans-serif" font-size="20" font-weight="700" fill="#0f172a">样品A</text>
                </g>
                <!-- Bottle 2 violet cap -->
                <g id="mt-bot-2">
                  <rect x="96" y="70" width="48" height="14" rx="3" fill="#8b5cf6" stroke="#a78bfa" stroke-width="2"/>
                  <rect x="102" y="64" width="36" height="10" rx="2" fill="#8b5cf6"/>
                  <rect x="94" y="84" width="52" height="120" rx="6"
                        fill="rgba(148,163,184,0.2)" stroke="#64748b" stroke-width="3"/>
                  <rect x="100" y="170" width="40" height="28" fill="rgba(139,92,246,0.25)"/>
                  <rect x="98" y="120" width="44" height="22" rx="2" fill="rgba(255,255,255,0.95)"/>
                  <text x="120" y="136" text-anchor="middle"
                        font-family="'Noto Sans SC','PingFang SC',sans-serif" font-size="20" font-weight="700" fill="#0f172a">样品B</text>
                </g>
                <!-- Bottle 3 emerald cap -->
                <g id="mt-bot-3">
                  <rect x="170" y="70" width="48" height="14" rx="3" fill="#10b981" stroke="#6ee7b7" stroke-width="2"/>
                  <rect x="176" y="64" width="36" height="10" rx="2" fill="#10b981"/>
                  <rect x="168" y="84" width="52" height="120" rx="6"
                        fill="rgba(148,163,184,0.2)" stroke="#64748b" stroke-width="3"/>
                  <rect x="174" y="170" width="40" height="28" fill="rgba(16,185,129,0.3)"/>
                  <rect x="172" y="120" width="44" height="22" rx="2" fill="rgba(255,255,255,0.95)"/>
                  <text x="194" y="136" text-anchor="middle"
                        font-family="'Noto Sans SC','PingFang SC',sans-serif" font-size="20" font-weight="700" fill="#0f172a">样品C</text>
                </g>
              </svg>
            </div>
            <div class="eq-name">器材 D</div>
            <div class="eq-note">用途说明 D</div>
          </div>

          <!-- Card 5: 器材 E -->
          <div class="eq-card glass-mini" id="mt-card-5">
            <div class="eq-svg">
              <svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <filter id="bigGlow5"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                  <filter id="rayGlow5"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                </defs>
                <!-- frame -->
                <rect x="40" y="50" width="120" height="150" rx="8"
                      fill="rgba(99,102,241,0.4)" stroke="#6366f1" stroke-width="4" filter="url(#bigGlow5)"/>
                <!-- inner glass shimmer -->
                <rect id="mt-cobalt" x="50" y="60" width="100" height="130" rx="4"
                      fill="rgba(99,102,241,0.5)" stroke="rgba(99,102,241,0.5)" stroke-width="2"/>
                <!-- highlight stripe -->
                <line x1="60" y1="70" x2="60" y2="180" stroke="rgba(255,255,255,0.6)" stroke-width="3"/>
                <!-- handle -->
                <rect x="92" y="200" width="16" height="26" rx="3" fill="#475569" stroke="#64748b" stroke-width="2"/>
                <!-- corner highlights -->
                <circle cx="55" cy="65" r="3" fill="rgba(255,255,255,0.8)"/>
              </svg>
            </div>
            <div class="eq-name">器材 E</div>
            <div class="eq-note">用途说明 E</div>
          </div>

        </div>
      </div>
    </div>

    <style>
      [data-composition-id="mt-equipment"] {
        position: relative; width: 100%; height: 100%;
        background: #f8fafc;
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        color: #0f172a;
        overflow: hidden;
      }

      /* --- KaTeX & table overrides --- */
      .katex, .katex * { color: #0f172a; }
      .katex-mathml { display: none !important; }
      table, th, td { color: #0f172a; }

      /* --- Aurora mesh background --- */
      .scene-bg { position: absolute; inset: 0; }
      .bg-texture { position: absolute; inset: 0; z-index: 0; background: url('../bg-texture.jpg') center/cover no-repeat; }
      .aurora-orb {
        position: absolute; border-radius: 50%;
        filter: blur(90px); will-change: transform;
      }
      .aurora-orb.a1 {
        width: 600px; height: 600px;
        background: rgba(6,182,212,0.3);
        top: -10%; left: -5%;
      }
      .aurora-orb.a2 {
        width: 500px; height: 500px;
        background: rgba(99,102,241,0.22);
        top: 40%; right: -8%;
      }
      .aurora-orb.a3 {
        width: 450px; height: 450px;
        background: rgba(16,185,129,0.18);
        bottom: -12%; left: 30%;
      }

      /* --- Layout --- */
      .scene-content {
        position: relative; z-index: 1;
        width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 60px 80px 180px; box-sizing: border-box;
      }

      .equipment-wrapper {
        width: 100%; max-width: 1760px;
        display: flex; flex-direction: column;
        align-items: stretch; gap: 36px;
      }

      .header-row {
        display: flex; align-items: center; justify-content: flex-start;
        padding-left: 16px;
      }
      .label {
        font-size: 22px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.16em; color: #6366f1;
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
      }

      .cards-grid {
        display: flex; gap: 28px; align-items: stretch;
        justify-content: space-between;
      }

      /* --- Glass cards --- */
      .glass-mini {
        background: #ffffff;

        border: 1px solid rgba(99,102,241,0.3);
        border-top: 2px solid rgba(99,102,241,0.25);
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(99,102,241,0.08);
      }
      .eq-card {
        flex: 1; min-width: 0;
        padding: 24px 18px 22px 18px;
        display: flex; flex-direction: column; align-items: center;
        gap: 14px;
        transition: border-color 0.3s, box-shadow 0.3s, opacity 0.3s;
      }
      .eq-card.dimmed { opacity: 0.55; }
      .eq-card.active {
        border-color: rgba(99,102,241,0.65);
        box-shadow: 0 4px 35px rgba(99,102,241,0.18), inset 0 1px 0 rgba(255,255,255,0.3);
      }

      /* --- Card internals --- */
      .eq-svg {
        width: 100%; height: 280px;
        display: flex; align-items: center; justify-content: center;
      }
      .eq-svg svg { width: 100%; height: 100%; }

      .eq-name {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 30px; font-weight: 700;
        color: #0f172a;
        text-align: center;
      }
      .eq-note {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 20px; font-weight: 500;
        color: #64748b;
        text-align: center;
        padding: 6px 14px;
        border-radius: 8px;
        border: 1px solid rgba(99,102,241,0.15);
        background: rgba(99,102,241,0.06);
      }
    </style>

    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <script src="./gsap/gsap.min.js"></script>
    <script>
      (function() {
        var SCENE_DURATION = 22.3;
        var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };

        window.__timelines = window.__timelines || {};
        var tl = gsap.timeline({ paused: true });

        /* 0. Scene fade-in */
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

        /* 1. Aurora drift (replaces bg-glow breathing) */
        tl.fromTo(".aurora-orb.a1",
          { x: 0, y: 0 },
          { x: 40, y: 30, duration: 6, ease: "sine.inOut",
            yoyo: true, repeat: R(6) }, 0);
        tl.fromTo(".aurora-orb.a2",
          { x: 0, y: 0 },
          { x: -35, y: -25, duration: 7, ease: "sine.inOut",
            yoyo: true, repeat: R(7) }, 0);
        tl.fromTo(".aurora-orb.a3",
          { x: 0, y: 0 },
          { x: 30, y: -20, duration: 8, ease: "sine.inOut",
            yoyo: true, repeat: R(8) }, 0);

        /* 1b. Panel shadow breathing */
        tl.fromTo(".glass-mini",
          { boxShadow: "0 4px 24px rgba(99,102,241,0.08)" },
          { boxShadow: "0 4px 32px rgba(99,102,241,0.16)", duration: 2.5, ease: "sine.inOut",
            yoyo: true, repeat: R(2.5) }, 0);

        /* 2. Label slide-in */
        tl.fromTo("#mt-eq-label",
          { x: -30, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5, ease: "expo.out" }, 0.3);

        /* 3. Card entrances (staggered) */
        var cards = [
          { id: "#mt-card-1", t: 0.5 },
          { id: "#mt-card-2", t: 4.6 },
          { id: "#mt-card-3", t: 8.1 },
          { id: "#mt-card-4", t: 11.0 },
          { id: "#mt-card-5", t: 16.1 }
        ];
        cards.forEach(function(c) {
          tl.fromTo(c.id,
            { y: 40, opacity: 0, scale: 0.9 },
            { y: 0, opacity: 1, scale: 1, duration: 0.7, ease: "back.out(1.4)" }, c.t);
        });

        /* 4. Highlight rotation -- active card gets indigo glow, others dim */
        function setHighlight(activeIdx, time) {
          cards.forEach(function(c, i) {
            if (i === activeIdx) {
              tl.to(c.id, {
                borderColor: "rgba(99,102,241,0.65)",
                boxShadow: "0 4px 35px rgba(99,102,241,0.18), inset 0 1px 0 rgba(255,255,255,0.3)",
                opacity: 1,
                duration: 0.4, ease: "power2.out"
              }, time);
            } else {
              tl.to(c.id, {
                borderColor: "rgba(99,102,241,0.15)",
                boxShadow: "0 4px 20px rgba(99,102,241,0.05), inset 0 1px 0 rgba(255,255,255,0.15)",
                opacity: 0.55,
                duration: 0.4, ease: "power2.out"
              }, time);
            }
          });
        }
        setHighlight(0, 1.3);
        setHighlight(1, 5.4);
        setHighlight(2, 8.9);
        setHighlight(3, 11.8);
        setHighlight(4, 16.9);

        /* Final state -- all visible */
        cards.forEach(function(c) {
          tl.to(c.id, {
            borderColor: "rgba(99,102,241,0.3)",
            boxShadow: "0 4px 25px rgba(99,102,241,0.1), inset 0 1px 0 rgba(255,255,255,0.2)",
            opacity: 1,
            duration: 0.5, ease: "power2.out"
          }, 20.3);
        });

        /* 5. Flame flicker (Card 1 SVG) */
        tl.fromTo("#mt-flame-outer",
          { scaleY: 0.92, scaleX: 0.96, transformOrigin: "100px 135px" },
          { scaleY: 1.1, scaleX: 1.05, duration: 0.45, ease: "sine.inOut",
            yoyo: true, repeat: R(0.45),
            transformOrigin: "100px 135px" }, 0.8);
        tl.fromTo("#mt-flame-inner",
          { scaleY: 0.9, scaleX: 0.94, transformOrigin: "100px 128px" },
          { scaleY: 1.12, scaleX: 1.06, duration: 0.38, ease: "sine.inOut",
            yoyo: true, repeat: R(0.38),
            transformOrigin: "100px 128px" }, 0.9);

        /* 6. Wire tip subtle pulse (Card 2 SVG) */
        tl.fromTo("#mt-wire-tip",
          { opacity: 0.7 },
          { opacity: 1, duration: 1.0, ease: "sine.inOut",
            yoyo: true, repeat: R(1.0) }, 5.0);

        /* 7. Liquid wave (Card 3 SVG) */
        tl.fromTo("#mt-liquid",
          { y: 0 },
          { y: -2, duration: 1.5, ease: "sine.inOut",
            yoyo: true, repeat: R(1.5) }, 8.5);

        /* 8. Sample bottle caps gentle bob (Card 4 SVG) */
        ["#mt-bot-1", "#mt-bot-2", "#mt-bot-3"].forEach(function(id, i) {
          tl.fromTo(id,
            { y: 0 },
            { y: -3, duration: 1.4 + i * 0.15, ease: "sine.inOut",
              yoyo: true, repeat: R(1.4 + i * 0.15) },
            11.4 + i * 0.2);
        });

        /* 9. Glass panel shimmer (Card 5 SVG) */
        tl.fromTo("#mt-cobalt",
          { opacity: 0.6 },
          { opacity: 0.9, duration: 1.5, ease: "sine.inOut",
            yoyo: true, repeat: R(1.5) }, 16.8);

        window.__timelines["mt-equipment"] = tl;
      })();
    </script>
  </div>
</template>
```

**Adaptation notes:**
- Equipment names (`器材 A`--`器材 E`) and usage notes (`用途说明 A`--`用途说明 E`) are placeholders. Replace with actual experiment equipment names and descriptions in Chinese.
- SVG illustrations are preserved from the original scene (lamp, wire, flask, sample bottles, observation glass). Replace or redraw SVGs to match the target experiment's actual equipment.
- Bottle labels (`样品A`, `样品B`, `样品C`) and reagent label (`试剂`) are generic placeholders. Substitute with actual chemical formulas or compound names.
- Card entrance timings in the `cards` array (0.5s, 4.6s, 8.1s, 11.0s, 16.1s) and highlight timings in `setHighlight` calls (1.3s, 5.4s, 8.9s, 11.8s, 16.9s) should be synchronized to voiceover cue points for each equipment item.
- `SCENE_DURATION` (currently 22.3s) must be updated to match the actual scene audio length.
- SVG filter IDs (`bigGlow1`, `rayGlow1`, etc.) are locally scoped. If multiple instances of this component appear in one document, append a unique suffix to avoid collisions.
- All SVG text elements use font-size >= 20px and stroke-widths use >= 3px (primary) / >= 2px (secondary) for render legibility.
- Chinese text uses the `"Noto Sans SC", "PingFang SC", sans-serif` font stack throughout.

---

## Component 9: Operation Flow Panel (操作流程面板)

A full-screen procedure visualization with a horizontal step indicator bar (pending/active/completed state machine) across the top and an SVG demonstration stage below. Steps activate sequentially, connectors fill between them, and apparatus objects choreograph across the SVG stage in sync with each step transition. Light aurora mesh background with frosted-glass panels.

```html
<template id="mt-procedure-template">
  <div data-composition-id="mt-procedure" data-width="1920" data-height="1080">
    <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb"></div>
      <div class="aurora-orb"></div>
      <div class="aurora-orb"></div>
    </div>
    <div class="scene-content">
      <div class="procedure-wrapper">
        <!-- TOP: Seven-step indicator (35%) -->
        <div class="steps-panel glass-panel">
          <div class="header-row">
            <div class="label">操作流程 &middot; OPERATION FLOW</div>
            <div class="status-bar" id="mt-status">
              <span id="mt-status-text">准备开始流程</span>
            </div>
          </div>
          <div class="step-indicator" id="mt-step-indicator">
            <!-- Step 1 -->
            <div class="step-block" id="mt-step-1">
              <div class="step-node">1</div>
              <div class="step-char">备</div>
              <div class="step-desc">准备就绪</div>
            </div>
            <div class="step-connector" id="mt-conn-1"></div>
            <!-- Step 2 -->
            <div class="step-block" id="mt-step-2">
              <div class="step-node">2</div>
              <div class="step-char">清</div>
              <div class="step-desc">清洁处理</div>
            </div>
            <div class="step-connector" id="mt-conn-2"></div>
            <!-- Step 3 -->
            <div class="step-block" id="mt-step-3">
              <div class="step-node">3</div>
              <div class="step-char">校</div>
              <div class="step-desc">校准验证</div>
            </div>
            <div class="step-connector" id="mt-conn-3"></div>
            <!-- Step 4 -->
            <div class="step-block" id="mt-step-4">
              <div class="step-node">4</div>
              <div class="step-char">取</div>
              <div class="step-desc">取用材料</div>
            </div>
            <div class="step-connector" id="mt-conn-4"></div>
            <!-- Step 5 -->
            <div class="step-block" id="mt-step-5">
              <div class="step-node">5</div>
              <div class="step-char">行</div>
              <div class="step-desc">执行操作</div>
            </div>
            <div class="step-connector" id="mt-conn-5"></div>
            <!-- Step 6 -->
            <div class="step-block" id="mt-step-6">
              <div class="step-node">6</div>
              <div class="step-char">察</div>
              <div class="step-desc">观察记录</div>
            </div>
            <div class="step-connector" id="mt-conn-6"></div>
            <!-- Step 7 -->
            <div class="step-block" id="mt-step-7">
              <div class="step-node">7</div>
              <div class="step-char">理</div>
              <div class="step-desc">整理归位</div>
            </div>
          </div>
        </div>

        <!-- BOTTOM: SVG demonstration stage (65%) -->
        <div class="stage-panel glass-panel">
          <svg id="mt-stage-svg" viewBox="0 0 1700 580" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <filter id="rayGlow">
                <feGaussianBlur stdDeviation="3" result="blur"/>
                <feMerge>
                  <feMergeNode in="blur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <filter id="bigGlow">
                <feGaussianBlur stdDeviation="6" result="blur"/>
                <feMerge>
                  <feMergeNode in="blur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <radialGradient id="flameGrad" cx="50%" cy="60%" r="50%">
                <stop offset="0%" stop-color="rgba(255,220,150,0.9)"/>
                <stop offset="60%" stop-color="rgba(96,180,255,0.5)"/>
                <stop offset="100%" stop-color="rgba(96,180,255,0)"/>
              </radialGradient>
            </defs>

            <!-- Floor reference line -->
            <line x1="80" y1="490" x2="1620" y2="490" stroke="rgba(99,102,241,0.1)" stroke-width="2" stroke-dasharray="6 8"/>

            <!-- LEFT: Apparatus A (heat source) -->
            <g id="mt-burner" transform="translate(280,350)">
              <!-- Base -->
              <ellipse cx="0" cy="140" rx="80" ry="14" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
              <!-- Glass body -->
              <path d="M -55,140 L -55,40 Q -55,20 -35,15 L 35,15 Q 55,20 55,40 L 55,140 Z"
                    fill="rgba(99,102,241,0.1)" stroke="#6366f1" stroke-width="3"/>
              <!-- Liquid level -->
              <rect x="-50" y="70" width="100" height="65" fill="rgba(99,102,241,0.12)"/>
              <line x1="-50" y1="70" x2="50" y2="70" stroke="#6366f1" stroke-width="2" opacity="0.5"/>
              <!-- Cap -->
              <rect x="-22" y="-8" width="44" height="22" rx="3" fill="#64748b" stroke="#94a3b8" stroke-width="2"/>
              <!-- Wick -->
              <rect x="-4" y="-25" width="8" height="20" fill="#64748b" rx="2"/>
              <!-- Outer flame -->
              <ellipse id="mt-flame-outer" cx="0" cy="-90" rx="34" ry="70"
                       fill="rgba(96,180,255,0.35)" filter="url(#bigGlow)"/>
              <!-- Inner flame -->
              <ellipse id="mt-flame-inner" cx="0" cy="-75" rx="18" ry="48"
                       fill="url(#flameGrad)" opacity="0.85"/>
              <!-- Core flame -->
              <ellipse id="mt-flame-core" cx="0" cy="-60" rx="8" ry="22"
                       fill="rgba(255,255,255,0.7)"/>
              <!-- Label -->
              <text x="0" y="170" text-anchor="middle" font-family="Noto Sans SC" font-size="22" font-weight="600" fill="#64748b">设备A</text>
              <text x="0" y="-175" text-anchor="middle" font-family="Inter" font-size="20" fill="#6366f1" letter-spacing="2">热区</text>
            </g>

            <!-- CENTER: Tool (movable probe) -->
            <g id="mt-wire" transform="translate(700,200)">
              <!-- Insulated handle -->
              <rect x="-60" y="-10" width="80" height="20" rx="6" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
              <rect x="-58" y="-7" width="76" height="4" fill="#94a3b8" rx="2"/>
              <!-- Wire connector -->
              <rect x="20" y="-3" width="14" height="6" fill="#64748b"/>
              <!-- Probe wire -->
              <line id="mt-wire-line" x1="34" y1="0" x2="140" y2="0"
                    stroke="#94a3b8" stroke-width="4" stroke-linecap="round" filter="url(#rayGlow)"/>
              <!-- Wire tip glow (changes color) -->
              <circle id="mt-wire-tip" cx="140" cy="0" r="6" fill="#94a3b8" filter="url(#rayGlow)"/>
              <!-- Sample droplet on tip (visible after dipping) -->
              <circle id="mt-droplet" cx="140" cy="0" r="0" fill="rgba(255,220,150,0.7)" filter="url(#rayGlow)"/>
              <!-- Label -->
              <text x="-20" y="-25" text-anchor="middle" font-family="Noto Sans SC" font-size="20" font-weight="600" fill="#0f172a">工具</text>
            </g>

            <!-- RIGHT: Reagent bottle -->
            <g id="mt-hcl-bottle" transform="translate(1100,360)">
              <!-- Base -->
              <ellipse cx="0" cy="120" rx="60" ry="10" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
              <!-- Bottle body -->
              <path d="M -45,120 L -45,30 Q -45,15 -30,10 L -10,10 L -10,-15 L 10,-15 L 10,10 L 30,10 Q 45,15 45,30 L 45,120 Z"
                    fill="rgba(16,185,129,0.08)" stroke="#10b981" stroke-width="3"/>
              <!-- Liquid -->
              <rect x="-42" y="50" width="84" height="68" fill="rgba(16,185,129,0.15)"/>
              <!-- Liquid surface -->
              <ellipse id="mt-hcl-surface" cx="0" cy="50" rx="42" ry="4" fill="rgba(16,185,129,0.45)"/>
              <!-- Ripple (animated) -->
              <ellipse id="mt-hcl-ripple" cx="0" cy="50" rx="0" ry="0" fill="none" stroke="#10b981" stroke-width="2" opacity="0"/>
              <!-- Label -->
              <rect x="-30" y="70" width="60" height="30" rx="3" fill="#f1f5f9" stroke="#10b981" stroke-width="2"/>
              <text x="0" y="90" text-anchor="middle" font-family="Inter" font-size="20" font-weight="700" fill="#10b981">试剂</text>
              <text x="0" y="150" text-anchor="middle" font-family="Noto Sans SC" font-size="20" font-weight="600" fill="#64748b">清洗液</text>
            </g>

            <!-- RIGHT: Sample bottles -->
            <g id="mt-samples" transform="translate(1340,380)">
              <!-- Sample A -->
              <g transform="translate(0,0)">
                <rect x="-30" y="-10" width="60" height="100" rx="6" fill="rgba(251,191,36,0.08)" stroke="#fbbf24" stroke-width="3"/>
                <rect x="-22" y="0" width="44" height="20" fill="rgba(251,191,36,0.35)"/>
                <rect x="-15" y="-22" width="30" height="14" rx="3" fill="#94a3b8"/>
                <text x="0" y="50" text-anchor="middle" font-family="Inter" font-size="20" font-weight="700" fill="#fbbf24">A</text>
                <circle id="mt-sample-flash-1" cx="0" cy="-22" r="0" fill="rgba(251,191,36,0.6)" filter="url(#bigGlow)"/>
              </g>
              <!-- Sample B -->
              <g transform="translate(75,0)">
                <rect x="-30" y="-10" width="60" height="100" rx="6" fill="rgba(139,92,246,0.08)" stroke="#8b5cf6" stroke-width="3"/>
                <rect x="-22" y="0" width="44" height="20" fill="rgba(139,92,246,0.35)"/>
                <rect x="-15" y="-22" width="30" height="14" rx="3" fill="#94a3b8"/>
                <text x="0" y="50" text-anchor="middle" font-family="Inter" font-size="20" font-weight="700" fill="#8b5cf6">B</text>
              </g>
              <!-- Sample C -->
              <g transform="translate(150,0)">
                <rect x="-30" y="-10" width="60" height="100" rx="6" fill="rgba(16,185,129,0.08)" stroke="#10b981" stroke-width="3"/>
                <rect x="-22" y="0" width="44" height="20" fill="rgba(16,185,129,0.35)"/>
                <rect x="-15" y="-22" width="30" height="14" rx="3" fill="#94a3b8"/>
                <text x="0" y="50" text-anchor="middle" font-family="Inter" font-size="20" font-weight="700" fill="#10b981">C</text>
              </g>
              <text x="75" y="115" text-anchor="middle" font-family="Noto Sans SC" font-size="20" font-weight="600" fill="#64748b">待测样品</text>
            </g>

            <!-- Observer eye icon (appears at observe step) -->
            <g id="mt-eye" transform="translate(450,180)" opacity="0">
              <ellipse cx="0" cy="0" rx="40" ry="24" fill="none" stroke="#6366f1" stroke-width="3" filter="url(#rayGlow)"/>
              <circle cx="0" cy="0" r="14" fill="#f1f5f9" stroke="#6366f1" stroke-width="2"/>
              <circle cx="0" cy="0" r="7" fill="#6366f1"/>
              <!-- Sight lines -->
              <line x1="40" y1="0" x2="80" y2="0" stroke="#6366f1" stroke-width="2" stroke-dasharray="4 4" opacity="0.6"/>
              <text x="0" y="-40" text-anchor="middle" font-family="Noto Sans SC" font-size="20" font-weight="600" fill="#6366f1">观察</text>
            </g>
          </svg>
        </div>
      </div>
    </div>

    <style>
      [data-composition-id="mt-procedure"] {
        position: relative; width: 100%; height: 100%;
        background: #f8fafc;
        font-family: "Noto Sans SC", Inter, sans-serif;
        color: #0f172a;
        overflow: hidden;
      }

      /* --- KaTeX & table resets --- */
      .katex, .katex * { color: #0f172a; }
      .katex-mathml { display: none !important; }
      table, th, td { color: #0f172a; }

      /* --- Aurora background --- */
      .scene-bg { position: absolute; inset: 0; }
      .bg-texture { position: absolute; inset: 0; z-index: 0; background: url('../bg-texture.jpg') center/cover no-repeat; }
      .aurora-orb {
        position: absolute; border-radius: 50%;
        filter: blur(80px); opacity: 0.3;
        will-change: transform;
      }
      .aurora-orb:nth-child(1) {
        width: 600px; height: 600px;
        background: radial-gradient(circle, rgba(6,182,212,0.4), transparent 70%);
        top: -10%; left: -5%;
      }
      .aurora-orb:nth-child(2) {
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(99,102,241,0.35), transparent 70%);
        bottom: -10%; right: 10%;
      }
      .aurora-orb:nth-child(3) {
        width: 450px; height: 450px;
        background: radial-gradient(circle, rgba(16,185,129,0.3), transparent 70%);
        top: 30%; right: -5%;
      }

      /* --- Layout --- */
      .scene-content {
        position: relative; z-index: 1;
        width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 40px 60px 180px; box-sizing: border-box;
      }
      .procedure-wrapper {
        width: 100%; max-width: 1760px; height: 100%;
        display: flex; flex-direction: column; gap: 24px;
      }

      /* --- Glass panels --- */
      .glass-panel {
        background: #ffffff;

        border: 1px solid rgba(99,102,241,0.3);
        border-top: 2px solid rgba(99,102,241,0.25);
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(99,102,241,0.06), inset 0 1px 0 rgba(255,255,255,0.6);
      }

      /* --- Steps panel --- */
      .steps-panel {
        flex: 0 0 auto; padding: 28px 40px;
        display: flex; flex-direction: column; gap: 20px;
      }
      .header-row {
        display: flex; align-items: center; justify-content: space-between;
        gap: 32px;
      }
      .label {
        font-size: 20px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.16em; color: #6366f1;
      }
      .status-bar {
        flex: 1; padding: 10px 24px;
        background: rgba(99,102,241,0.06);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 8px;
        text-align: center;
        font-family: "Noto Sans SC", sans-serif;
        font-size: 22px; font-weight: 600; color: #6366f1;
        max-width: 720px;
      }

      /* --- Step indicator --- */
      .step-indicator {
        display: flex; align-items: center; justify-content: space-between;
        width: 100%;
      }
      .step-block {
        display: flex; flex-direction: column; align-items: center; gap: 8px;
        opacity: 0.5;
      }
      .step-block.active { opacity: 1; }
      .step-block.completed { opacity: 0.85; }

      .step-node {
        width: 60px; height: 60px; border-radius: 50%;
        border: 2px solid #cbd5e1;
        background: #f1f5f9;
        display: flex; align-items: center; justify-content: center;
        font-family: Inter, "Noto Sans SC", sans-serif; font-weight: 700; font-size: 22px; color: #64748b;
      }
      .step-block.active .step-node {
        background: #6366f1; border-color: #6366f1; color: #ffffff;
        box-shadow: 0 0 24px rgba(99,102,241,0.5);
        transform: scale(1.15);
      }
      .step-block.completed .step-node {
        background: #818cf8; border-color: #818cf8; color: #ffffff;
        box-shadow: 0 0 12px rgba(99,102,241,0.3);
      }
      .step-char {
        font-family: "Noto Sans SC", sans-serif;
        font-size: 28px; font-weight: 700; color: #0f172a;
        margin-top: 4px;
      }
      .step-block.active .step-char { color: #6366f1; }
      .step-desc {
        font-family: "Noto Sans SC", sans-serif;
        font-size: 14px; color: #64748b; font-weight: 400;
      }
      .step-block.active .step-desc { color: #0f172a; }

      /* --- Connectors --- */
      .step-connector {
        flex: 1;
        height: 3px; max-width: 80px;
        background: #cbd5e1;
        margin-bottom: 50px;
        position: relative; overflow: hidden;
      }
      .step-connector.filled { background: #6366f1; }
      .step-connector.flowing {
        background: linear-gradient(90deg, transparent, #6366f1, transparent);
        background-size: 40px 100%;
      }

      /* --- Stage panel --- */
      .stage-panel {
        flex: 1 1 auto;
        padding: 20px 40px;
        position: relative;
        min-height: 0;
      }
      .stage-panel svg {
        width: 100%; height: 100%;
      }
    </style>

    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <script src="./gsap/gsap.min.js"></script>
    <script>
      (function() {
        var SCENE_DURATION = 28.0;
        function R(d, off) { return Math.floor((SCENE_DURATION - (off || 0)) / d) - 1; }

        window.__timelines = window.__timelines || {};
        var tl = gsap.timeline({ paused: true });

        /* ===== 0. Scene fade-in ===== */
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

        /* ===== 1. Aurora orb drift ===== */
        tl.fromTo(".aurora-orb:nth-child(1)",
          { x: 0, y: 0 },
          { x: 40, y: 30, duration: 6, ease: "sine.inOut",
            yoyo: true, repeat: R(6) }, 0);
        tl.fromTo(".aurora-orb:nth-child(2)",
          { x: 0, y: 0 },
          { x: -35, y: -25, duration: 7, ease: "sine.inOut",
            yoyo: true, repeat: R(7) }, 0);
        tl.fromTo(".aurora-orb:nth-child(3)",
          { x: 0, y: 0 },
          { x: 25, y: -35, duration: 5, ease: "sine.inOut",
            yoyo: true, repeat: R(5) }, 0);

        /* ===== 2. Glass panel shadow breathing ===== */
        tl.fromTo(".glass-panel",
          { boxShadow: "0 4px 24px rgba(99,102,241,0.06)" },
          { boxShadow: "0 4px 32px rgba(99,102,241,0.14)", duration: 3, ease: "sine.inOut",
            yoyo: true, repeat: R(3) }, 0);

        /* ===== 3. Steps panel entrance ===== */
        tl.fromTo(".steps-panel",
          { y: -30, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6, ease: "power3.out" }, 0.2);

        /* ===== 4. Step blocks stagger entrance ===== */
        var stepIds = ["#mt-step-1","#mt-step-2","#mt-step-3","#mt-step-4","#mt-step-5","#mt-step-6","#mt-step-7"];
        stepIds.forEach(function(id, i) {
          tl.fromTo(id,
            { x: -20, opacity: 0 },
            { x: 0, opacity: 0.5, duration: 0.4, ease: "expo.out" },
            0.5 + i * 0.1);
        });

        /* Connector entrance */
        var connIds = ["#mt-conn-1","#mt-conn-2","#mt-conn-3","#mt-conn-4","#mt-conn-5","#mt-conn-6"];
        connIds.forEach(function(id, i) {
          tl.fromTo(id,
            { scaleX: 0, transformOrigin: "left center" },
            { scaleX: 1, duration: 0.3, ease: "power2.out" },
            0.6 + i * 0.1);
        });

        /* ===== 5. Stage panel entrance ===== */
        tl.fromTo(".stage-panel",
          { y: 30, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6, ease: "power3.out" }, 1.0);

        /* ===== 6. Continuous flame flicker ===== */
        tl.fromTo("#mt-flame-outer",
          { scaleY: 0.92, scaleX: 0.96 },
          { scaleY: 1.08, scaleX: 1.04, duration: 0.45, ease: "sine.inOut",
            yoyo: true, repeat: R(0.45, 1.5),
            transformOrigin: "50% 100%" }, 1.5);
        tl.fromTo("#mt-flame-inner",
          { scaleY: 0.88, scaleX: 0.94 },
          { scaleY: 1.12, scaleX: 1.06, duration: 0.38, ease: "sine.inOut",
            yoyo: true, repeat: R(0.38, 1.5),
            transformOrigin: "50% 100%" }, 1.5);
        tl.fromTo("#mt-flame-core",
          { scaleY: 0.85, opacity: 0.6 },
          { scaleY: 1.15, opacity: 0.9, duration: 0.32, ease: "sine.inOut",
            yoyo: true, repeat: R(0.32, 1.5),
            transformOrigin: "50% 100%" }, 1.5);

        /* ========================================
           STEP CHOREOGRAPHY
           ======================================== */
        function activate(stepId, time) {
          tl.to(stepId, { duration: 0.01,
            onStart: function() {
              var allSteps = document.querySelectorAll('.step-block');
              allSteps.forEach(function(el) {
                el.classList.remove('active');
              });
              var el = document.querySelector(stepId);
              if (el) el.classList.add('active');
            }
          }, time);
        }
        function complete(stepId, time) {
          tl.to(stepId, { duration: 0.01,
            onStart: function() {
              var el = document.querySelector(stepId);
              if (el) {
                el.classList.remove('active');
                el.classList.add('completed');
              }
            }
          }, time);
        }
        function fillConn(connId, time) {
          tl.to(connId, { duration: 0.01,
            onStart: function() {
              var el = document.querySelector(connId);
              if (el) el.classList.add('filled');
            }
          }, time);
        }
        function setStatus(text, time) {
          tl.to("#mt-status-text", { duration: 0.01,
            onStart: function() {
              var el = document.getElementById("mt-status-text");
              if (el) el.textContent = text;
            }
          }, time);
        }

        /* === T=2.0 START === */
        setStatus("操作流程：准备开始", 2.0);

        /* === STEP 1 (t=2.5-6.0): Prepare -- move tool to heat source === */
        activate("#mt-step-1", 2.5);
        setStatus("第一步：准备就绪，加热工具", 2.5);
        tl.fromTo("#mt-wire",
          { x: 0, y: 0 },
          { x: -440, y: 60, duration: 1.5, ease: "power2.inOut" }, 2.5);
        tl.fromTo("#mt-wire-tip",
          { fill: "#94a3b8" },
          { fill: "#ff7a3d", duration: 0.8, ease: "power1.in" }, 4.0);
        tl.to("#mt-wire-line", { stroke: "#ff7a3d", duration: 0.8, ease: "power1.in" }, 4.0);

        /* === STEP 2 (t=6.0-9.5): Clean -- tool to reagent bottle === */
        complete("#mt-step-1", 6.0);
        fillConn("#mt-conn-1", 6.0);
        activate("#mt-step-2", 6.0);
        setStatus("第二步：清洁处理，蘸取试剂", 6.0);
        tl.to("#mt-wire-tip", { fill: "#94a3b8", duration: 0.5 }, 6.0);
        tl.to("#mt-wire-line", { stroke: "#94a3b8", duration: 0.5 }, 6.0);
        tl.to("#mt-wire", { x: 360, y: 120, duration: 1.5, ease: "power2.inOut" }, 6.2);
        tl.fromTo("#mt-hcl-ripple",
          { attr: { rx: 0, ry: 0 }, opacity: 0.8 },
          { attr: { rx: 50, ry: 6 }, opacity: 0, duration: 1.0, ease: "power2.out",
            repeat: 2 }, 7.8);
        tl.fromTo("#mt-droplet",
          { attr: { r: 0 }, fill: "rgba(16,185,129,0.7)" },
          { attr: { r: 8 }, duration: 0.5, ease: "power2.out" }, 8.2);

        /* === STEP 3 (t=9.5-12.5): Verify -- back to heat source === */
        complete("#mt-step-2", 9.5);
        fillConn("#mt-conn-2", 9.5);
        activate("#mt-step-3", 9.5);
        setStatus("第三步：校准验证，再次加热确认", 9.5);
        tl.to("#mt-wire", { x: -440, y: 60, duration: 1.3, ease: "power2.inOut" }, 9.7);
        tl.to("#mt-droplet", { attr: { r: 0 }, duration: 0.6, ease: "power2.in" }, 10.6);
        tl.to("#mt-wire-tip", { fill: "#ff7a3d", duration: 0.6 }, 11.0);
        tl.to("#mt-wire-line", { stroke: "#ff7a3d", duration: 0.6 }, 11.0);

        /* === STEP 4 (t=12.5-15.5): Collect -- tool to sample === */
        complete("#mt-step-3", 12.5);
        fillConn("#mt-conn-3", 12.5);
        activate("#mt-step-4", 12.5);
        setStatus("第四步：取用待测样品", 12.5);
        tl.to("#mt-wire-tip", { fill: "#94a3b8", duration: 0.4 }, 12.5);
        tl.to("#mt-wire-line", { stroke: "#94a3b8", duration: 0.4 }, 12.5);
        tl.to("#mt-wire", { x: 640, y: 140, duration: 1.4, ease: "power2.inOut" }, 12.7);
        tl.fromTo("#mt-sample-flash-1",
          { attr: { r: 0 }, opacity: 1 },
          { attr: { r: 30 }, opacity: 0, duration: 0.8, ease: "power2.out" }, 14.2);
        tl.fromTo("#mt-droplet",
          { attr: { r: 0 }, fill: "rgba(251,191,36,0.8)" },
          { attr: { r: 9 }, duration: 0.5, ease: "power2.out" }, 14.4);

        /* === STEP 5 (t=15.5-19.0): Execute -- back to heat source, color change === */
        complete("#mt-step-4", 15.5);
        fillConn("#mt-conn-4", 15.5);
        activate("#mt-step-5", 15.5);
        setStatus("第五步：执行主要操作", 15.5);
        tl.to("#mt-wire", { x: -440, y: 60, duration: 1.3, ease: "power2.inOut" }, 15.7);
        tl.to("#mt-droplet", { attr: { r: 0 }, duration: 0.4, ease: "power2.in" }, 17.0);
        tl.to("#mt-flame-outer", { fill: "rgba(251,191,36,0.55)", duration: 0.4 }, 17.0);
        tl.to("#mt-flame-inner", { fill: "rgba(251,191,36,0.85)", duration: 0.4 }, 17.0);
        tl.to("#mt-flame-core", { fill: "rgba(255,240,180,0.9)", duration: 0.4 }, 17.0);
        tl.to("#mt-wire-tip", { fill: "#fbbf24", duration: 0.5 }, 17.2);
        tl.to("#mt-wire-line", { stroke: "#fbbf24", duration: 0.5 }, 17.2);

        /* === STEP 6 (t=19.0-23.0): Observe -- eye icon appears === */
        complete("#mt-step-5", 19.0);
        fillConn("#mt-conn-5", 19.0);
        activate("#mt-step-6", 19.0);
        setStatus("第六步：观察并记录结果", 19.0);
        tl.fromTo("#mt-eye",
          { opacity: 0, x: 30 },
          { opacity: 1, x: 0, duration: 0.7, ease: "power3.out" }, 19.3);
        tl.to("#mt-eye",
          { scale: 1.1, transformOrigin: "450px 180px",
            duration: 0.8, ease: "sine.inOut",
            yoyo: true, repeat: 4 }, 20.0);

        /* === STEP 7 (t=23.0-27.5): Reset -- clean and restore === */
        complete("#mt-step-6", 23.0);
        fillConn("#mt-conn-6", 23.0);
        activate("#mt-step-7", 23.0);
        setStatus("第七步：清洗整理，准备下一次操作", 23.0);
        tl.to("#mt-eye", { opacity: 0, duration: 0.5 }, 23.0);
        tl.to("#mt-flame-outer", { fill: "rgba(96,180,255,0.35)", duration: 0.6 }, 23.0);
        tl.to("#mt-flame-inner", { fill: "rgba(96,180,255,0.5)", duration: 0.6 }, 23.0);
        tl.to("#mt-flame-core", { fill: "rgba(255,255,255,0.7)", duration: 0.6 }, 23.0);
        tl.to("#mt-wire-tip", { fill: "#94a3b8", duration: 0.5 }, 23.2);
        tl.to("#mt-wire-line", { stroke: "#94a3b8", duration: 0.5 }, 23.2);
        tl.to("#mt-wire", { x: 360, y: 120, duration: 1.4, ease: "power2.inOut" }, 23.5);
        tl.fromTo("#mt-hcl-ripple",
          { attr: { rx: 0, ry: 0 }, opacity: 0.8 },
          { attr: { rx: 50, ry: 6 }, opacity: 0, duration: 0.9, ease: "power2.out",
            repeat: 3 }, 25.0);

        /* Final completion */
        tl.to("#mt-step-7", { duration: 0.01,
          onStart: function() {
            var el = document.querySelector("#mt-step-7");
            if (el) {
              el.classList.remove('active');
              el.classList.add('completed');
            }
          }
        }, 27.5);

        window.__timelines["mt-procedure"] = tl;
      })();
    </script>
  </div>
</template>
```

**Adaptation notes:**
- Background converted from dark (`#0a0e17`) to light (`#f8fafc`) with three aurora orbs (cyan `rgba(6,182,212,0.4)`, indigo `rgba(99,102,241,0.35)`, emerald `rgba(16,185,129,0.3)`) providing ambient color wash; `bg-glow` replaced by orb drift driven entirely by GSAP `fromTo()`.
- Opaque panels use `#ffffff` background (border + layered box-shadow for depth).
- All accent colors remapped: `#00e5ff` and `#4d7cff` to `#6366f1` (indigo-500), `#a855f7` to `#8b5cf6` (violet-500), `#22d3a0` to `#10b981` (emerald-500), muted `#94a3b8` to `#64748b`.
- Text inverted: primary `#e8ecf4` to `#0f172a`; completed-step nodes use `#818cf8` (indigo-400) for softer contrast on white.
- SVG dark fills (`#1e293b`, `#141b2d`) replaced with light surfaces (`#e2e8f0`, `#f1f5f9`); default wire/tip color changed from `#cbd5e1` to `#64748b`/`#94a3b8` for visibility on light background.
- KaTeX and table color resets included for `#0f172a`.
- All SVG text elements meet the 20px minimum; all strokes meet 3px/2px minimums.
- Seven procedure steps generalized to placeholder labels (备/清/校/取/行/察/理) with generic status messages; SVG apparatus labels generalized (设备A, 工具, 试剂, 清洗液, A/B/C samples).
- Ambient effects use GSAP-only aurora drift (`sine.inOut`, yoyo) and glass-panel shadow breathing; no CSS `@keyframes`, no `Math.random()`.
- Deterministic repeat counts via `R(duration, offset)` helper wrapping `Math.floor((SCENE_DURATION - offset) / duration) - 1`.
- Timeline registered on `window.__timelines["mt-procedure"]` in paused state; composition id is `mt-procedure`.
- Chinese text uses `"Noto Sans SC"` throughout; no emoji characters present.
- **Apparatus sizing rule:** In the SVG stage (viewBox `0 0 1700 580`), primary apparatus (burner, flask, bottle) must occupy at least **40-60% of the viewBox height** (230-350 SVG units tall including flame/labels). The burner body alone spans ~300 units in the template. Never shrink apparatus below these proportions — a tiny apparatus in a large stage is a critical visual error.

---

## Component 10: Comparison Panel (对比说明面板)

A side-by-side comparison layout with left (negative/red) and right (positive/green)
panels, each containing an SVG illustration stage, a result verdict box, and a shared
warning bar at top and summary quote bar at bottom. The center dashed divider visually
separates the two options. Aurora Scholar light theme with amber/indigo/red aurora mesh
background. All emojis replaced with inline SVGs. GSAP paused timeline drives entrance
choreography, element-level flicker/pulse loops, and aurora orb drift.

```html
<template id="mt-comparison-template">
  <div data-composition-id="mt-comparison" data-width="1920" data-height="1080">
    <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb orb-a1"></div>
      <div class="aurora-orb orb-a2"></div>
      <div class="aurora-orb orb-a3"></div>
    </div>
    <div class="scene-content">
      <div class="comparison-wrapper">
        <!-- Top warning / title bar -->
        <div class="warning-bar" id="mt-c-warning">
          <svg class="warn-icon" viewBox="0 0 32 32" width="32" height="32" fill="none">
            <path d="M16 3L2 28h28L16 3z" stroke="#d97706" stroke-width="2.5" fill="rgba(217,119,6,0.12)" stroke-linejoin="round"/>
            <line x1="16" y1="13" x2="16" y2="20" stroke="#d97706" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="16" cy="24" r="1.5" fill="#d97706"/>
          </svg>
          <span class="warn-text">要点对比 COMPARISON</span>
        </div>

        <!-- Compare panels -->
        <div class="compare-row">
          <!-- LEFT panel: negative / option A -->
          <div class="compare-panel left-panel glass-panel" id="mt-c-left">
            <div class="panel-title left-title">方案A</div>
            <div class="svg-stage">
              <svg viewBox="0 0 700 480" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
                <defs>
                  <filter id="mt-c-rayGlowL">
                    <feGaussianBlur stdDeviation="3" result="blur"/>
                    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                  </filter>
                  <filter id="mt-c-bigGlowL">
                    <feGaussianBlur stdDeviation="6" result="blur"/>
                    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                  </filter>
                </defs>

                <!-- Apparatus base (placeholder illustration) -->
                <g transform="translate(120,330)">
                  <ellipse cx="0" cy="60" rx="50" ry="14" fill="#e2e8f0" stroke="#94a3b8" stroke-width="3"/>
                  <rect x="-38" y="10" width="76" height="55" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="3"/>
                  <rect x="-8" y="-18" width="16" height="32" fill="#64748b" rx="3"/>
                  <!-- Outer emission (warm dominant) -->
                  <ellipse id="mt-c-flameL-out" cx="0" cy="-60" rx="40" ry="68"
                           fill="rgba(251,191,36,0.45)" filter="url(#mt-c-bigGlowL)"/>
                  <!-- Mid emission -->
                  <ellipse id="mt-c-flameL-mid" cx="0" cy="-50" rx="22" ry="42"
                           fill="rgba(251,191,36,0.55)"/>
                  <!-- Inner emission (accent hint) -->
                  <ellipse id="mt-c-flameL-in" cx="0" cy="-44" rx="10" ry="22"
                           fill="rgba(139,92,246,0.4)"/>
                </g>

                <!-- Primary signal rays (dominant, warm) -->
                <line id="mt-c-rayL-y1" x1="170" y1="270" x2="430" y2="220"
                      stroke="#fbbf24" stroke-width="5" opacity="0.7" filter="url(#mt-c-rayGlowL)"/>
                <line id="mt-c-rayL-y2" x1="170" y1="270" x2="450" y2="260"
                      stroke="#fbbf24" stroke-width="5" opacity="0.7" filter="url(#mt-c-rayGlowL)"/>
                <line id="mt-c-rayL-y3" x1="170" y1="270" x2="440" y2="305"
                      stroke="#fbbf24" stroke-width="5" opacity="0.7" filter="url(#mt-c-rayGlowL)"/>
                <line id="mt-c-rayL-y4" x1="170" y1="270" x2="430" y2="195"
                      stroke="#fbbf24" stroke-width="5" opacity="0.7" filter="url(#mt-c-rayGlowL)"/>
                <!-- Secondary signal rays (faint) -->
                <line id="mt-c-rayL-p1" x1="170" y1="270" x2="445" y2="240"
                      stroke="#8b5cf6" stroke-width="3" opacity="0.45" filter="url(#mt-c-rayGlowL)"/>
                <line id="mt-c-rayL-p2" x1="170" y1="270" x2="445" y2="285"
                      stroke="#8b5cf6" stroke-width="3" opacity="0.45" filter="url(#mt-c-rayGlowL)"/>

                <!-- Observer -->
                <g id="mt-c-eyeL" transform="translate(560,260)" opacity="0">
                  <ellipse cx="0" cy="0" rx="40" ry="26" fill="none" stroke="#0f172a" stroke-width="3"/>
                  <circle cx="0" cy="0" r="14" fill="#f1f5f9" stroke="#0f172a" stroke-width="2"/>
                  <circle cx="0" cy="0" r="7" fill="#fbbf24"/>
                </g>
              </svg>
            </div>
            <div class="result-box result-bad" id="mt-c-resultL">
              <span class="result-label">结论：</span>
              <span class="result-value color-bad">方案A结果</span>
              <svg class="mark-bad" viewBox="0 0 28 28" width="28" height="28" fill="none">
                <line x1="7" y1="7" x2="21" y2="21" stroke="#dc2626" stroke-width="3" stroke-linecap="round"/>
                <line x1="21" y1="7" x2="7" y2="21" stroke="#dc2626" stroke-width="3" stroke-linecap="round"/>
              </svg>
            </div>
          </div>

          <!-- Center divider -->
          <div class="center-divider" id="mt-c-divider"></div>

          <!-- RIGHT panel: positive / option B -->
          <div class="compare-panel right-panel glass-panel" id="mt-c-right">
            <div class="panel-title right-title">方案B</div>
            <div class="svg-stage">
              <svg viewBox="0 0 700 480" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
                <defs>
                  <filter id="mt-c-rayGlowR">
                    <feGaussianBlur stdDeviation="3" result="blur"/>
                    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                  </filter>
                  <filter id="mt-c-bigGlowR">
                    <feGaussianBlur stdDeviation="6" result="blur"/>
                    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                  </filter>
                </defs>

                <!-- Apparatus base (placeholder illustration) -->
                <g transform="translate(110,330)">
                  <ellipse cx="0" cy="60" rx="50" ry="14" fill="#e2e8f0" stroke="#94a3b8" stroke-width="3"/>
                  <rect x="-38" y="10" width="76" height="55" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="3"/>
                  <rect x="-8" y="-18" width="16" height="32" fill="#64748b" rx="3"/>
                  <ellipse id="mt-c-flameR-out" cx="0" cy="-60" rx="40" ry="68"
                           fill="rgba(251,191,36,0.4)" filter="url(#mt-c-bigGlowR)"/>
                  <ellipse id="mt-c-flameR-mid" cx="0" cy="-50" rx="22" ry="42"
                           fill="rgba(251,191,36,0.5)"/>
                  <ellipse id="mt-c-flameR-in" cx="0" cy="-44" rx="10" ry="22"
                           fill="rgba(139,92,246,0.45)"/>
                </g>

                <!-- Primary signal rays (will be filtered) -->
                <line id="mt-c-rayR-y1" x1="160" y1="270" x2="380" y2="220"
                      stroke="#fbbf24" stroke-width="5" opacity="0.7" filter="url(#mt-c-rayGlowR)"/>
                <line id="mt-c-rayR-y2" x1="160" y1="270" x2="380" y2="260"
                      stroke="#fbbf24" stroke-width="5" opacity="0.7" filter="url(#mt-c-rayGlowR)"/>
                <line id="mt-c-rayR-y3" x1="160" y1="270" x2="380" y2="305"
                      stroke="#fbbf24" stroke-width="5" opacity="0.7" filter="url(#mt-c-rayGlowR)"/>
                <!-- Secondary signal rays (will pass through) -->
                <line id="mt-c-rayR-p1" x1="160" y1="270" x2="380" y2="240"
                      stroke="#8b5cf6" stroke-width="4" opacity="0.7" filter="url(#mt-c-rayGlowR)"/>
                <line id="mt-c-rayR-p2" x1="160" y1="270" x2="380" y2="285"
                      stroke="#8b5cf6" stroke-width="4" opacity="0.7" filter="url(#mt-c-rayGlowR)"/>

                <!-- Filter / processor element -->
                <g id="mt-c-glass" opacity="0">
                  <rect x="380" y="160" width="46" height="200" rx="8"
                        fill="rgba(30,80,220,0.42)" stroke="#6366f1" stroke-width="4"
                        filter="url(#mt-c-rayGlowR)"/>
                  <rect x="380" y="160" width="46" height="200" rx="8"
                        fill="none" stroke="rgba(99,102,241,0.45)" stroke-width="2"/>
                  <text x="403" y="385" text-anchor="middle"
                        fill="#6366f1" font-family="'Noto Sans SC', Inter, sans-serif"
                        font-size="20" font-weight="700">过滤器</text>
                </g>

                <!-- Passed secondary rays (right of filter) -->
                <line id="mt-c-passedP1" x1="426" y1="240" x2="600" y2="225"
                      stroke="#8b5cf6" stroke-width="5" opacity="0" filter="url(#mt-c-rayGlowR)"/>
                <line id="mt-c-passedP2" x1="426" y1="285" x2="600" y2="295"
                      stroke="#8b5cf6" stroke-width="5" opacity="0" filter="url(#mt-c-rayGlowR)"/>

                <!-- Block marks for filtered rays -->
                <g id="mt-c-blocks" opacity="0">
                  <g transform="translate(395,220)">
                    <line x1="-9" y1="-9" x2="9" y2="9" stroke="#dc2626" stroke-width="4" stroke-linecap="round"/>
                    <line x1="9" y1="-9" x2="-9" y2="9" stroke="#dc2626" stroke-width="4" stroke-linecap="round"/>
                  </g>
                  <g transform="translate(395,260)">
                    <line x1="-9" y1="-9" x2="9" y2="9" stroke="#dc2626" stroke-width="4" stroke-linecap="round"/>
                    <line x1="9" y1="-9" x2="-9" y2="9" stroke="#dc2626" stroke-width="4" stroke-linecap="round"/>
                  </g>
                  <g transform="translate(395,305)">
                    <line x1="-9" y1="-9" x2="9" y2="9" stroke="#dc2626" stroke-width="4" stroke-linecap="round"/>
                    <line x1="9" y1="-9" x2="-9" y2="9" stroke="#dc2626" stroke-width="4" stroke-linecap="round"/>
                  </g>
                </g>

                <!-- Observer -->
                <g id="mt-c-eyeR" transform="translate(625,260)" opacity="0">
                  <ellipse cx="0" cy="0" rx="40" ry="26" fill="none" stroke="#0f172a" stroke-width="3"/>
                  <circle cx="0" cy="0" r="14" fill="#f1f5f9" stroke="#0f172a" stroke-width="2"/>
                  <circle cx="0" cy="0" r="7" fill="#8b5cf6"/>
                </g>
              </svg>
            </div>
            <div class="result-box result-good" id="mt-c-resultR">
              <span class="result-label">结论：</span>
              <span class="result-value color-good">方案B结果</span>
              <svg class="mark-good" viewBox="0 0 28 28" width="28" height="28" fill="none">
                <polyline points="6,15 12,21 22,8" stroke="#10b981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Bottom summary quote bar -->
        <div class="quote-bar" id="mt-c-quote">
          <svg class="quote-icon" viewBox="0 0 24 24" width="24" height="24">
            <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="#6366f1"/>
          </svg>
          <span class="quote-text">核心结论说明文字</span>
          <svg class="quote-icon" viewBox="0 0 24 24" width="24" height="24">
            <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="#6366f1"/>
          </svg>
        </div>
      </div>
    </div>

    <style>
      [data-composition-id="mt-comparison"] {
        position: relative; width: 100%; height: 100%;
        background: #f8fafc;
        font-family: "Noto Sans SC", Inter, sans-serif;
        color: #0f172a;
        overflow: hidden;
      }

      /* ---- background ---- */
      [data-composition-id="mt-comparison"] .scene-bg {
        position: absolute; inset: 0; overflow: hidden;
      }
      [data-composition-id="mt-comparison"] .bg-texture {
        position: absolute; inset: 0; z-index: 0;
        background: url('../bg-texture.jpg') center/cover no-repeat;
      }
      [data-composition-id="mt-comparison"] .aurora-orb {
        position: absolute; border-radius: 50%;
        filter: blur(80px); pointer-events: none;
      }
      [data-composition-id="mt-comparison"] .orb-a1 {
        width: 500px; height: 500px;
        background: rgba(217,119,6,0.25);
        top: 10%; left: 15%;
      }
      [data-composition-id="mt-comparison"] .orb-a2 {
        width: 450px; height: 450px;
        background: rgba(99,102,241,0.2);
        top: 50%; right: 10%;
      }
      [data-composition-id="mt-comparison"] .orb-a3 {
        width: 400px; height: 400px;
        background: rgba(220,38,38,0.15);
        bottom: 10%; left: 45%;
      }
      [data-composition-id="mt-comparison"]

      /* ---- content layout ---- */
      [data-composition-id="mt-comparison"] .scene-content {
        position: relative; z-index: 1;
        width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 40px 60px 180px; box-sizing: border-box;
      }
      [data-composition-id="mt-comparison"] .comparison-wrapper {
        width: 100%; max-width: 1800px; height: 100%;
        display: flex; flex-direction: column; gap: 22px;
      }

      /* ---- glass panels ---- */
      [data-composition-id="mt-comparison"] .glass-panel {
        background: #ffffff;

        border: 1px solid rgba(99,102,241,0.3);
        border-top: 2px solid rgba(99,102,241,0.25);
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(99,102,241,0.06);
      }

      /* ---- warning bar ---- */
      [data-composition-id="mt-comparison"] .warning-bar {
        display: flex; align-items: center; justify-content: center; gap: 18px;
        padding: 14px 36px;
        background: rgba(217,119,6,0.08);
        border: 2px solid rgba(217,119,6,0.35);
        border-radius: 14px;
        align-self: center;
        box-shadow: 0 4px 24px rgba(217,119,6,0.08);
      }
      [data-composition-id="mt-comparison"] .warn-icon {
        filter: drop-shadow(0 0 8px rgba(217,119,6,0.4));
        flex-shrink: 0;
      }
      [data-composition-id="mt-comparison"] .warn-text {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 26px; font-weight: 700;
        letter-spacing: 0.10em;
        color: #d97706;
        text-transform: uppercase;
      }

      /* ---- compare row ---- */
      [data-composition-id="mt-comparison"] .compare-row {
        display: flex; flex-direction: row;
        align-items: stretch; justify-content: space-between;
        gap: 20px; flex: 1; min-height: 0;
      }
      [data-composition-id="mt-comparison"] .compare-panel {
        flex: 1; padding: 24px 28px;
        display: flex; flex-direction: column; gap: 14px;
        min-width: 0;
      }
      [data-composition-id="mt-comparison"] .left-panel {
        border-color: rgba(220,38,38,0.25);
        box-shadow: 0 4px 24px rgba(220,38,38,0.06);
      }
      [data-composition-id="mt-comparison"] .right-panel {
        border-color: rgba(16,185,129,0.25);
        box-shadow: 0 4px 24px rgba(16,185,129,0.06);
      }

      /* ---- panel titles ---- */
      [data-composition-id="mt-comparison"] .panel-title {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 26px; font-weight: 700;
        letter-spacing: 0.04em;
        text-align: center;
        padding: 8px 16px;
        border-radius: 10px;
      }
      [data-composition-id="mt-comparison"] .left-title {
        color: #dc2626;
        background: rgba(220,38,38,0.08);
        border: 1px solid rgba(220,38,38,0.2);
      }
      [data-composition-id="mt-comparison"] .right-title {
        color: #10b981;
        background: rgba(16,185,129,0.08);
        border: 1px solid rgba(16,185,129,0.2);
      }

      /* ---- SVG stage ---- */
      [data-composition-id="mt-comparison"] .svg-stage {
        flex: 1;
        background: rgba(230,240,255,0.4);
        border: 1px solid rgba(99,102,241,0.08);
        border-radius: 12px;
        padding: 10px;
        min-height: 0;
        display: flex; align-items: center; justify-content: center;
      }
      [data-composition-id="mt-comparison"] .svg-stage svg {
        width: 100%; height: 100%; max-height: 380px;
      }

      /* ---- result boxes ---- */
      [data-composition-id="mt-comparison"] .result-box {
        display: flex; align-items: center; justify-content: center; gap: 14px;
        padding: 14px 24px; border-radius: 12px;
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 26px; font-weight: 600;
      }
      [data-composition-id="mt-comparison"] .result-bad {
        background: rgba(220,38,38,0.06);
        border: 2px solid rgba(220,38,38,0.4);
        box-shadow: 0 4px 18px rgba(220,38,38,0.08);
        color: #dc2626;
      }
      [data-composition-id="mt-comparison"] .result-good {
        background: rgba(16,185,129,0.06);
        border: 2px solid rgba(16,185,129,0.4);
        box-shadow: 0 4px 18px rgba(16,185,129,0.08);
        color: #10b981;
      }
      [data-composition-id="mt-comparison"] .result-label { color: #64748b; font-weight: 500; }
      [data-composition-id="mt-comparison"] .color-bad { color: #dc2626; font-weight: 800; }
      [data-composition-id="mt-comparison"] .color-good { color: #10b981; font-weight: 800; }
      [data-composition-id="mt-comparison"] .mark-bad,
      [data-composition-id="mt-comparison"] .mark-good {
        flex-shrink: 0; display: inline-block; vertical-align: middle;
      }

      /* ---- center divider ---- */
      [data-composition-id="mt-comparison"] .center-divider {
        width: 2px; align-self: stretch;
        background: repeating-linear-gradient(
          to bottom,
          rgba(99,102,241,0.55) 0,
          rgba(99,102,241,0.55) 10px,
          transparent 10px,
          transparent 20px
        );
        box-shadow: 0 0 12px rgba(99,102,241,0.15);
      }

      /* ---- quote bar ---- */
      [data-composition-id="mt-comparison"] .quote-bar {
        display: flex; align-items: center; justify-content: center; gap: 22px;
        padding: 18px 40px;
        border-radius: 14px;
        background: #ffffff;
        border: 1px solid rgba(99,102,241,0.25);
        box-shadow: 0 4px 24px rgba(99,102,241,0.08);
        align-self: center;
        max-width: 1400px;
      }
      [data-composition-id="mt-comparison"] .quote-icon {
        filter: drop-shadow(0 0 8px rgba(99,102,241,0.4));
        flex-shrink: 0;
      }
      [data-composition-id="mt-comparison"] .quote-text {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 30px; font-weight: 700;
        color: #0f172a;
        letter-spacing: 0.04em;
      }

      /* ---- KaTeX / table resets ---- */
      [data-composition-id="mt-comparison"] .katex,
      [data-composition-id="mt-comparison"] .katex * { color: #0f172a; }
      [data-composition-id="mt-comparison"] .katex-mathml { display: none !important; }
      [data-composition-id="mt-comparison"] table,
      [data-composition-id="mt-comparison"] th,
      [data-composition-id="mt-comparison"] td { color: #0f172a; }
    </style>

    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <script src="./gsap/gsap.min.js"></script>
    <script>
      (function () {
        var SCENE_DURATION = 22.4;
        function R(d, s) { return Math.floor((SCENE_DURATION - (s || 0)) / d) - 1; }

        window.__timelines = window.__timelines || {};
        var tl = gsap.timeline({ paused: true });

        /* 0. Scene fade-in */
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

        /* 1. Aurora orb drift */
        tl.fromTo(".orb-a1",
          { x: 0, y: 0 },
          { x: 40, y: -30, duration: 4.0, ease: "sine.inOut",
            yoyo: true, repeat: R(4.0, 0) }, 0);
        tl.fromTo(".orb-a2",
          { x: 0, y: 0 },
          { x: -35, y: 25, duration: 4.5, ease: "sine.inOut",
            yoyo: true, repeat: R(4.5, 0) }, 0);
        tl.fromTo(".orb-a3",
          { x: 0, y: 0 },
          { x: 25, y: 35, duration: 3.8, ease: "sine.inOut",
            yoyo: true, repeat: R(3.8, 0) }, 0);

        /* 2. Warning label entrance + amber shadow breathing */
        tl.fromTo("#mt-c-warning",
          { y: -24, opacity: 0, scale: 0.94 },
          { y: 0, opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.4)" }, 0.3);
        tl.fromTo("#mt-c-warning",
          { boxShadow: "0 4px 24px rgba(217,119,6,0.08)" },
          { boxShadow: "0 4px 32px rgba(217,119,6,0.22)", duration: 1.2, ease: "sine.inOut",
            yoyo: true, repeat: R(1.2, 1.0) }, 1.0);

        /* 3. Left & right panels slide in */
        tl.fromTo("#mt-c-left",
          { x: -50, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.7, ease: "power3.out" }, 0.6);
        tl.fromTo("#mt-c-right",
          { x: 50, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.7, ease: "power3.out" }, 0.6);
        tl.fromTo("#mt-c-divider",
          { scaleY: 0, transformOrigin: "center top", opacity: 0 },
          { scaleY: 1, opacity: 1, duration: 0.6, ease: "power2.out" }, 0.9);

        /* Left panel shadow breathing */
        tl.fromTo("#mt-c-left",
          { boxShadow: "0 4px 24px rgba(220,38,38,0.06)" },
          { boxShadow: "0 4px 32px rgba(220,38,38,0.14)", duration: 2.5, ease: "sine.inOut",
            yoyo: true, repeat: R(2.5, 1.5) }, 1.5);

        /* 4. Source element flicker (both sides) */
        ["#mt-c-flameL-out","#mt-c-flameL-mid","#mt-c-flameL-in",
         "#mt-c-flameR-out","#mt-c-flameR-mid","#mt-c-flameR-in"].forEach(function(id, i) {
          var dur = 0.42 + (i % 3) * 0.08;
          tl.fromTo(id,
            { scaleY: 0.92, scaleX: 0.96, transformOrigin: "50% 100%" },
            { scaleY: 1.10, scaleX: 1.04, transformOrigin: "50% 100%",
              duration: dur, ease: "sine.inOut",
              yoyo: true, repeat: R(dur, 1.2) },
            1.2 + i * 0.05);
        });

        /* 5. LEFT side: primary rays pulse, secondary faint */
        ["#mt-c-rayL-y1","#mt-c-rayL-y2","#mt-c-rayL-y3","#mt-c-rayL-y4"].forEach(function(id, i) {
          tl.fromTo(id,
            { opacity: 0 },
            { opacity: 0.75, duration: 0.5, ease: "power2.out" }, 1.4 + i * 0.12);
          tl.fromTo(id,
            { opacity: 0.75 },
            { opacity: 0.45, duration: 0.7, ease: "sine.inOut",
              yoyo: true, repeat: R(0.7, 2.2) }, 2.2 + i * 0.1);
        });
        ["#mt-c-rayL-p1","#mt-c-rayL-p2"].forEach(function(id, i) {
          tl.fromTo(id,
            { opacity: 0 },
            { opacity: 0.30, duration: 0.5, ease: "power2.out" }, 1.6 + i * 0.15);
          tl.fromTo(id,
            { opacity: 0.30 },
            { opacity: 0.45, duration: 0.9, ease: "sine.inOut",
              yoyo: true, repeat: R(0.9, 2.5) }, 2.5 + i * 0.2);
        });

        /* 6. RIGHT side: rays start */
        ["#mt-c-rayR-y1","#mt-c-rayR-y2","#mt-c-rayR-y3"].forEach(function(id, i) {
          tl.fromTo(id,
            { opacity: 0 },
            { opacity: 0.7, duration: 0.5, ease: "power2.out" }, 1.4 + i * 0.12);
        });
        ["#mt-c-rayR-p1","#mt-c-rayR-p2"].forEach(function(id, i) {
          tl.fromTo(id,
            { opacity: 0 },
            { opacity: 0.65, duration: 0.5, ease: "power2.out" }, 1.6 + i * 0.15);
        });

        /* 7. LEFT observer + BAD result at 4.0s */
        tl.fromTo("#mt-c-eyeL",
          { opacity: 0, x: 24 },
          { opacity: 1, x: 0, duration: 0.6, ease: "power3.out" }, 4.0);
        tl.fromTo("#mt-c-resultL",
          { y: 16, opacity: 0, scale: 0.92 },
          { y: 0, opacity: 1, scale: 1, duration: 0.55, ease: "back.out(1.4)" }, 4.4);
        tl.fromTo("#mt-c-resultL .mark-bad",
          { scale: 1 },
          { scale: 1.18, duration: 0.55, ease: "sine.inOut",
            yoyo: true, repeat: R(0.55, 5.0),
            transformOrigin: "50% 50%" }, 5.0);

        /* 8. Filter element slides in at 7.0s */
        tl.fromTo("#mt-c-glass",
          { y: -90, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.8, ease: "back.out(1.6)" }, 7.0);
        tl.fromTo("#mt-c-right",
          { boxShadow: "0 4px 24px rgba(16,185,129,0.06)" },
          { boxShadow: "0 4px 32px rgba(99,102,241,0.22)",
            duration: 0.45, ease: "power2.out" }, 7.4);
        tl.fromTo("#mt-c-right",
          { boxShadow: "0 4px 32px rgba(99,102,241,0.22)" },
          { boxShadow: "0 4px 24px rgba(16,185,129,0.10)",
            duration: 0.6, ease: "power2.in" }, 7.85);

        /* Filter edge glow pulse */
        tl.fromTo("#mt-c-glass rect:nth-child(2)",
          { opacity: 1 },
          { opacity: 0.45, duration: 0.9, ease: "sine.inOut",
            yoyo: true, repeat: R(0.9, 8.0) }, 8.0);

        /* 9. Block marks appear at 9.0s */
        tl.fromTo("#mt-c-blocks",
          { opacity: 0, scale: 0.7, transformOrigin: "50% 50%" },
          { opacity: 1, scale: 1, duration: 0.55, ease: "back.out(1.5)" }, 9.0);
        tl.fromTo("#mt-c-blocks",
          { scale: 1 },
          { scale: 1.05, duration: 0.55, ease: "sine.inOut",
            yoyo: true, repeat: R(0.55, 9.6),
            transformOrigin: "50% 50%" }, 9.6);

        /* Primary rays on right fade (blocked) */
        ["#mt-c-rayR-y1","#mt-c-rayR-y2","#mt-c-rayR-y3"].forEach(function(id) {
          tl.fromTo(id,
            { opacity: 0.7 },
            { opacity: 0.18, duration: 0.6, ease: "power2.in" }, 9.2);
        });

        /* 10. Passed secondary rays at 9.8s */
        ["#mt-c-passedP1","#mt-c-passedP2"].forEach(function(id, i) {
          tl.fromTo(id,
            { opacity: 0 },
            { opacity: 0.85, duration: 0.5, ease: "power2.out" }, 9.8 + i * 0.15);
          tl.fromTo(id,
            { opacity: 0.85 },
            { opacity: 0.55, duration: 0.8, ease: "sine.inOut",
              yoyo: true, repeat: R(0.8, 10.6) }, 10.6 + i * 0.1);
        });
        ["#mt-c-rayR-p1","#mt-c-rayR-p2"].forEach(function(id) {
          tl.fromTo(id,
            { opacity: 0.65 },
            { opacity: 0.85, duration: 0.5, ease: "power2.out" }, 9.8);
        });

        /* 11. RIGHT observer + GOOD result at 11.5s */
        tl.fromTo("#mt-c-eyeR",
          { opacity: 0, x: 24 },
          { opacity: 1, x: 0, duration: 0.6, ease: "power3.out" }, 11.5);
        tl.fromTo("#mt-c-resultR",
          { y: 16, opacity: 0, scale: 0.92 },
          { y: 0, opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.4)" }, 11.9);
        tl.fromTo("#mt-c-resultR",
          { boxShadow: "0 0 18px rgba(16,185,129,0.08)" },
          { boxShadow: "0 0 38px rgba(16,185,129,0.22)", duration: 1.0, ease: "sine.inOut",
            yoyo: true, repeat: R(1.0, 12.6) }, 12.6);
        tl.fromTo("#mt-c-resultR .mark-good",
          { scale: 1 },
          { scale: 1.22, duration: 0.6, ease: "sine.inOut",
            yoyo: true, repeat: R(0.6, 12.6),
            transformOrigin: "50% 50%" }, 12.6);

        /* Right panel shadow breathing (after filter arrival settles) */
        tl.fromTo("#mt-c-right",
          { boxShadow: "0 4px 24px rgba(16,185,129,0.10)" },
          { boxShadow: "0 4px 32px rgba(16,185,129,0.18)", duration: 2.5, ease: "sine.inOut",
            yoyo: true, repeat: R(2.5, 13.0) }, 13.0);

        /* 12. Quote bar at 17.5s + indigo pulse */
        tl.fromTo("#mt-c-quote",
          { y: 24, opacity: 0, scale: 0.95 },
          { y: 0, opacity: 1, scale: 1, duration: 0.7, ease: "back.out(1.4)" }, 17.5);
        tl.fromTo("#mt-c-quote",
          { boxShadow: "0 4px 24px rgba(99,102,241,0.08)" },
          { boxShadow: "0 4px 32px rgba(99,102,241,0.22)",
            duration: 1.1, ease: "sine.inOut",
            yoyo: true, repeat: R(1.1, 18.4) }, 18.4);
        tl.fromTo("#mt-c-quote .quote-icon",
          { opacity: 0.75 },
          { opacity: 1, duration: 0.7, ease: "sine.inOut",
            yoyo: true, repeat: R(0.7, 18.2),
            stagger: 0.2 }, 18.2);

        window.__timelines["mt-comparison"] = tl;
      })();
    </script>
  </div>
</template>
```

**Adaptation notes:**
- Replace placeholder SVG illustrations (apparatus, rays, filter, observer) with domain-specific diagrams for the actual comparison subject. Keep the same `id` attributes so GSAP selectors remain valid.
- Update text content: warning bar title (`warn-text`), panel titles (`.left-title`, `.right-title`), result values (`.color-bad`, `.color-good`), and quote bar summary (`.quote-text`).
- Left panel uses red-negative theming (`rgba(220,38,38,...)` / `#dc2626`), right panel uses green-positive theming (`rgba(16,185,129,...)` / `#10b981`). Swap the polarity by exchanging the CSS classes if the left option should be positive.
- The warning bar uses amber theming (`rgba(217,119,6,...)` / `#d97706`) to draw attention without implying positive or negative.
- All emoji characters (warning triangle, X mark, checkmark, stars) replaced with inline SVGs meeting the minimum stroke-width of 3px and text size of 20px.
- `SCENE_DURATION` (default 22.4s) can be adjusted; all repeat counts recalculate via the `R(duration, startTime)` helper.
- The filter element SVG group (`#mt-c-glass`) animates in at 7.0s with a back-ease entrance; adjust timing or remove if no filtering concept applies.
- Chinese text rendered with `"Noto Sans SC"` as primary font; the font must be loaded externally or embedded.
- Aurora mesh orbs use the comparison palette (amber `a1`, indigo `a2`, red `a3`); change radial colors in `.orb-a1/a2/a3` to match alternate subject palettes.
- The center dashed divider uses indigo `rgba(99,102,241,0.55)`; it scales in from top at 0.9s.
- Opaque panels use `#ffffff` background (NO backdrop-filter; depth via border + layered box-shadow)
- Timeline registered on `window.__timelines["mt-comparison"]`; rename the key if multiple comparison panels coexist.

---

## Component 11: Science Principle Diagram (科学原理图解)

Dual-panel science principle layout with an interactive SVG diagram on the left (atom model with energy-level rings, nucleus, orbiting electron, heat-wave input, and photon emission) and sequentially-entering numbered explanation blocks on the right. Aurora Scholar light theme with indigo/violet/cyan aurora mesh background. All SVG animation cycles (electron transitions, photon ray emission, heat-wave pulses) are preserved in a single paused GSAP timeline driven by `hf-seek`. Bottom warning tag uses amber styling. Chinese labels rendered in Noto Sans SC; equations rendered via KaTeX.

```html
<template id="mt-principle-template">
  <div data-composition-id="mt-principle" data-width="1920" data-height="1080">
    <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb a1"></div>
      <div class="aurora-orb a2"></div>
      <div class="aurora-orb a3"></div>
    </div>
    <div class="scene-content">
      <div class="principle-wrapper">
        <!-- LEFT: Atom energy level diagram -->
        <div class="atom-panel glass-panel">
          <div class="panel-label">原子能级跃迁</div>
          <svg id="mt-atom-svg" viewBox="0 0 600 600" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <filter id="rayGlow">
                <feGaussianBlur stdDeviation="3" result="blur"/>
                <feMerge>
                  <feMergeNode in="blur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <filter id="bigGlow">
                <feGaussianBlur stdDeviation="6" result="blur"/>
                <feMerge>
                  <feMergeNode in="blur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <radialGradient id="nucleusGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#fbbf24" stop-opacity="0.95"/>
                <stop offset="60%" stop-color="#d97706" stop-opacity="0.85"/>
                <stop offset="100%" stop-color="#7c2d12" stop-opacity="0.6"/>
              </radialGradient>
            </defs>

            <!-- Energy level rings -->
            <circle id="mt-level-1" cx="300" cy="300" r="90"
                    fill="none" stroke="#6366f1" stroke-width="3"
                    opacity="0.85" filter="url(#rayGlow)"/>
            <circle id="mt-level-2" cx="300" cy="300" r="160"
                    fill="none" stroke="#6366f1" stroke-width="3"
                    opacity="0.75" filter="url(#rayGlow)"/>
            <circle id="mt-level-3" cx="300" cy="300" r="230"
                    fill="none" stroke="#8b5cf6" stroke-width="3"
                    opacity="0.7" filter="url(#rayGlow)"/>

            <!-- Level labels -->
            <text class="lvl-label" x="300" y="218" text-anchor="middle">E&#x2081; &#x57FA;&#x6001;</text>
            <text class="lvl-label" x="300" y="148" text-anchor="middle">E&#x2082;</text>
            <text class="lvl-label" x="300" y="78" text-anchor="middle">E&#x2083; &#x6FC0;&#x53D1;&#x6001;</text>

            <!-- Nucleus (atom core) -->
            <g id="mt-nucleus">
              <circle cx="300" cy="300" r="32" fill="url(#nucleusGrad)" filter="url(#bigGlow)"/>
              <circle cx="300" cy="300" r="32" fill="none" stroke="#fbbf24" stroke-width="2" opacity="0.6"/>
            </g>

            <!-- Heat wave (incoming energy from bottom-left) -->
            <g id="mt-heatwave">
              <path d="M 60 540 Q 130 510 200 480" fill="none"
                    stroke="#f97316" stroke-width="4" opacity="0" filter="url(#rayGlow)"
                    stroke-linecap="round"/>
              <path d="M 80 560 Q 150 525 215 495" fill="none"
                    stroke="#fb923c" stroke-width="4" opacity="0" filter="url(#rayGlow)"
                    stroke-linecap="round"/>
              <path d="M 40 520 Q 115 495 185 465" fill="none"
                    stroke="#fbbf24" stroke-width="4" opacity="0" filter="url(#rayGlow)"
                    stroke-linecap="round"/>
            </g>
            <text id="mt-heat-label" x="55" y="500" fill="#fb923c"
                  font-size="22" font-weight="600" opacity="0">&#x5438;&#x6536;&#x80FD;&#x91CF;</text>

            <!-- Emitted photon ray (top-right) -->
            <g id="mt-photon-ray">
              <line id="mt-photon-line" x1="300" y1="300" x2="300" y2="300"
                    stroke="#fbbf24" stroke-width="5" opacity="0"
                    filter="url(#rayGlow)" stroke-linecap="round"/>
              <circle id="mt-photon-dot" cx="300" cy="300" r="14"
                      fill="#fbbf24" opacity="0" filter="url(#bigGlow)"/>
            </g>
            <text id="mt-photon-label" x="490" y="135" fill="#0f172a"
                  font-size="22" font-weight="600" opacity="0">&#x91CA;&#x653E;&#x5149;&#x5B50; h&#x03BD;</text>

            <!-- Electron (orbits + jumps) -->
            <circle id="mt-electron" cx="390" cy="300" r="14"
                    fill="#fde047" filter="url(#bigGlow)"/>
            <circle id="mt-electron-trail" cx="390" cy="300" r="8"
                    fill="#fef3c7" opacity="0.5"/>
          </svg>
        </div>

        <!-- RIGHT: Explanation panel -->
        <div class="info-panel glass-panel">
          <div class="info-label">PRINCIPLE · &#x5FAE;&#x89C2;&#x672C;&#x8D28;</div>

          <div class="info-block" id="mt-block-1">
            <div class="info-num">&#x2460;</div>
            <div class="info-text">
              <div class="info-title">&#x5916;&#x5C42;&#x7535;&#x5B50;&#x5438;&#x6536;&#x80FD;&#x91CF;</div>
              <div class="info-desc">&#x9AD8;&#x6E29;&#x706B;&#x7130;&#x52A0;&#x70ED;&#xFF0C;&#x91D1;&#x5C5E;&#x539F;&#x5B50;&#x5916;&#x5C42;&#x7535;&#x5B50;&#x4ECE;&#x57FA;&#x6001;&#x8DC3;&#x8FC1;&#x5230;&#x6FC0;&#x53D1;&#x6001;&#x3002;</div>
            </div>
          </div>

          <div class="info-block" id="mt-block-2">
            <div class="info-num">&#x2461;</div>
            <div class="info-text">
              <div class="info-title">&#x6FC0;&#x53D1;&#x6001;&#x4E0D;&#x7A33;&#x5B9A; &#x2192; &#x56DE;&#x843D;</div>
              <div class="info-desc">&#x7535;&#x5B50;&#x4ECE;&#x9AD8;&#x80FD;&#x7EA7;&#x56DE;&#x843D;&#xFF0C;&#x4EE5;&#x5149;&#x5B50;&#x5F62;&#x5F0F;&#x91CA;&#x653E;&#x80FD;&#x91CF;&#x3002;</div>
              <div class="info-eq" id="mt-eq-1"></div>
            </div>
          </div>

          <div class="info-block" id="mt-block-3">
            <div class="info-num">&#x2462;</div>
            <div class="info-text">
              <div class="info-title">&#x80FD;&#x7EA7;&#x5DEE;&#x4E0D;&#x540C; &#x2192; &#x989C;&#x8272;&#x4E0D;&#x540C;</div>
              <div class="info-eq" id="mt-eq-2"></div>
            </div>
          </div>

          <div class="warning-tag" id="mt-warning">
            <span class="warn-icon">!</span>
            <span>&#x7269;&#x7406;&#x53D8;&#x5316; · NOT &#x5316;&#x5B66;&#x53CD;&#x5E94;</span>
          </div>
        </div>
      </div>
    </div>

    <style>
      [data-composition-id="mt-principle"] {
        position: relative; width: 100%; height: 100%;
        background: #f8fafc;
        font-family: "Noto Sans SC", Inter, sans-serif;
        color: #0f172a;
        overflow: hidden;
      }

      /* --- KaTeX & table resets --- */
      [data-composition-id="mt-principle"] .katex,
      [data-composition-id="mt-principle"] .katex * { color: #0f172a; }
      [data-composition-id="mt-principle"] .katex-mathml { display: none !important; }
      [data-composition-id="mt-principle"] table,
      [data-composition-id="mt-principle"] th,
      [data-composition-id="mt-principle"] td { color: #0f172a; }

      /* --- Aurora mesh background --- */
      .scene-bg { position: absolute; inset: 0; }
      .bg-texture { position: absolute; inset: 0; z-index: 0; background: url('../bg-texture.jpg') center/cover no-repeat; }

      .aurora-orb {
        position: absolute; border-radius: 50%;
        filter: blur(80px);
        will-change: transform;
      }
      .aurora-orb.a1 {
        width: 700px; height: 700px;
        background: rgba(139,92,246,0.3);
        top: -10%; left: -5%;
      }
      .aurora-orb.a2 {
        width: 600px; height: 600px;
        background: rgba(6,182,212,0.22);
        bottom: -10%; right: -5%;
      }
      .aurora-orb.a3 {
        width: 500px; height: 500px;
        background: rgba(99,102,241,0.18);
        top: 40%; left: 50%;
      }

      /* --- Layout --- */
      .scene-content {
        position: relative; z-index: 1;
        width: 100%; height: 100%;
        display: flex; align-items: center; justify-content: center;
        padding: 60px 60px 180px; box-sizing: border-box;
      }

      .principle-wrapper {
        display: flex; gap: 40px; align-items: stretch;
        width: 100%; height: 100%;
      }

      /* --- Glass panels --- */
      .glass-panel {
        background: #ffffff;

        border: 1px solid rgba(99,102,241,0.3);
        border-top: 2px solid rgba(99,102,241,0.25);
        border-radius: 16px;
        box-shadow:
          0 4px 30px rgba(99,102,241,0.08),
          inset 0 1px 0 rgba(255,255,255,0.6);
      }

      /* --- Left panel: SVG diagram --- */
      .atom-panel {
        flex: 1.2;
        padding: 32px;
        display: flex; flex-direction: column;
        position: relative;
      }
      .atom-panel svg {
        width: 100%; height: 100%; flex: 1;
      }
      .panel-label {
        font-size: 20px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.12em; color: #8b5cf6; margin-bottom: 12px;
        font-family: "Noto Sans SC", sans-serif;
      }
      .lvl-label {
        font-family: "KaTeX_Main", "Noto Sans SC", sans-serif;
        font-size: 22px; fill: #0f172a; opacity: 0.85;
        font-weight: 600;
      }

      /* --- Right panel: Explanation blocks --- */
      .info-panel {
        flex: 1;
        padding: 40px 36px;
        display: flex; flex-direction: column;
        gap: 22px;
      }
      .info-label {
        font-size: 20px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.12em; color: #6366f1;
        margin-bottom: 4px;
        font-family: "Noto Sans SC", sans-serif;
      }
      .info-block {
        display: flex; gap: 16px;
        padding: 16px 18px;
        border-radius: 12px;
        border: 1px solid rgba(99,102,241,0.15);
        background: rgba(99,102,241,0.04);
      }
      .info-num {
        font-family: "KaTeX_Main", serif;
        font-size: 36px; font-weight: 700;
        color: #8b5cf6;
        line-height: 1;
        flex-shrink: 0;
      }
      .info-text { flex: 1; }
      .info-title {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 24px; font-weight: 700;
        color: #0f172a; margin-bottom: 6px;
      }
      .info-desc {
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        font-size: 20px; line-height: 1.55;
        color: #64748b;
      }
      .info-eq {
        margin-top: 10px;
        text-align: left;
      }
      .info-eq .katex { font-size: 26px; }

      /* --- Warning tag (amber) --- */
      .warning-tag {
        margin-top: auto;
        display: flex; align-items: center; gap: 14px;
        padding: 18px 24px;
        border-radius: 12px;
        border: 2px solid rgba(217,119,6,0.35);
        background: rgba(217,119,6,0.06);
        font-family: "Noto Sans SC", sans-serif;
        font-size: 24px; font-weight: 700;
        color: #d97706;
        text-align: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(217,119,6,0.1);
      }
      .warn-icon {
        display: inline-flex; align-items: center; justify-content: center;
        width: 30px; height: 30px; border-radius: 50%;
        border: 2.5px solid #d97706;
        font-size: 20px; font-weight: 800;
        line-height: 1; color: #d97706;
        flex-shrink: 0;
      }
    </style>

    <!-- Fonts: use the self-hosted @font-face block from index.html <head> (NO Google Fonts / CDN — see step-6) -->
    <!-- KaTeX CSS: inline as <style id="katex-inline-css"> with local url(./katex/fonts/ — see step-5 (NOT a CDN <link>) -->
    <script src="./katex/katex.min.js"></script>
    <script src="./gsap/gsap.min.js"></script>

    <script>
      (function () {
        /* --- KaTeX render --- */
        katex.render("E_{\\text{photon}} = h\\nu = E_{\\text{激发}} - E_{\\text{基态}}",
          document.getElementById("mt-eq-1"), { displayMode: true, throwOnError: false });
        katex.render("\\Delta E \\neq \\text{常数}\\;\\Rightarrow\\;\\text{颜色因元素而异}",
          document.getElementById("mt-eq-2"), { displayMode: true, throwOnError: false });

        var SCENE_DURATION = 30.5;
        function R(d) { return Math.max(0, Math.floor((SCENE_DURATION - 2) / d) - 1); }

        window.__timelines = window.__timelines || {};
        var tl = gsap.timeline({ paused: true });

        /* 0. Scene fade-in */
        tl.fromTo(".scene-content",
          { opacity: 0 },
          { opacity: 1, duration: 0.3, ease: "power2.out" }, 0);

        /* 1. Aurora orb drift */
        tl.fromTo(".aurora-orb.a1",
          { x: 0, y: 0 },
          { x: 30, y: -20, duration: 4, ease: "sine.inOut",
            yoyo: true, repeat: R(4) }, 0);
        tl.fromTo(".aurora-orb.a2",
          { x: 0, y: 0 },
          { x: -25, y: 15, duration: 5, ease: "sine.inOut",
            yoyo: true, repeat: R(5) }, 0);
        tl.fromTo(".aurora-orb.a3",
          { x: 0, y: 0 },
          { x: 20, y: 25, duration: 3.5, ease: "sine.inOut",
            yoyo: true, repeat: R(3.5) }, 0);

        /* 2. Glass-panel shadow breathing */
        tl.fromTo(".glass-panel",
          { boxShadow: "0 4px 30px rgba(99,102,241,0.08), inset 0 1px 0 rgba(255,255,255,0.6)" },
          { boxShadow: "0 4px 40px rgba(99,102,241,0.18), inset 0 1px 0 rgba(255,255,255,0.6)",
            duration: 2.5, ease: "sine.inOut",
            yoyo: true, repeat: R(2.5) }, 0);

        /* 3. Atom panel entrance */
        tl.fromTo(".atom-panel",
          { x: -40, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.7, ease: "power3.out" }, 0.3);

        /* 4. Nucleus pop in */
        tl.fromTo("#mt-nucleus",
          { scale: 0, transformOrigin: "300px 300px" },
          { scale: 1, duration: 0.6, ease: "back.out(1.6)" }, 0.6);

        /* 5. Energy level rings draw in (scale-up + opacity) */
        tl.fromTo("#mt-level-1",
          { attr: { r: 0 }, opacity: 0 },
          { attr: { r: 90 }, opacity: 0.85, duration: 0.6, ease: "power2.out" }, 1.0);
        tl.fromTo("#mt-level-2",
          { attr: { r: 0 }, opacity: 0 },
          { attr: { r: 160 }, opacity: 0.75, duration: 0.6, ease: "power2.out" }, 1.3);
        tl.fromTo("#mt-level-3",
          { attr: { r: 0 }, opacity: 0 },
          { attr: { r: 230 }, opacity: 0.7, duration: 0.6, ease: "power2.out" }, 1.6);

        /* 6. Right panel entrance */
        tl.fromTo(".info-panel",
          { x: 40, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.7, ease: "power3.out" }, 1.8);
        tl.fromTo(".info-label",
          { y: -10, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.4, ease: "expo.out" }, 2.2);

        /* 7. Three info blocks staggered */
        tl.fromTo("#mt-block-1",
          { x: 25, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 3.0);
        tl.fromTo("#mt-block-2",
          { x: 25, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 8.0);
        tl.fromTo("#mt-block-3",
          { x: 25, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" }, 13.0);

        /* Active highlight pulses on each block when introduced */
        [["#mt-block-1", 3.5], ["#mt-block-2", 8.5], ["#mt-block-3", 13.5]].forEach(function(p) {
          tl.fromTo(p[0],
            { borderColor: "rgba(99,102,241,0.15)" },
            { borderColor: "rgba(99,102,241,0.5)", duration: 0.5, ease: "power2.out",
              yoyo: true, repeat: 1 }, p[1]);
        });

        /* 8. Energy level rings opacity micro-pulse (continuous) */
        ["#mt-level-1","#mt-level-2","#mt-level-3"].forEach(function(id, i) {
          tl.fromTo(id,
            { opacity: 0.85 - i * 0.07 },
            { opacity: 0.55 - i * 0.05, duration: 1.8, ease: "sine.inOut",
              yoyo: true, repeat: R(1.8) },
            2.0 + i * 0.2);
        });

        /* 9. Nucleus subtle breathing */
        tl.fromTo("#mt-nucleus",
          { scale: 1, transformOrigin: "300px 300px" },
          { scale: 1.08, duration: 1.4, ease: "sine.inOut",
            yoyo: true, repeat: R(1.4) }, 1.5);

        /* 10. ELECTRON TRANSITION CYCLES -- 4s per cycle, photon color rotates */
        var photonColors = ["#fde047", "#8b5cf6", "#10b981"];
        var cycleStart = 2.5;
        var cycleDur = 4.0;
        var nCycles = Math.floor((SCENE_DURATION - cycleStart) / cycleDur);

        for (var c = 0; c < nCycles; c++) {
          var t0 = cycleStart + c * cycleDur;
          var color = photonColors[c % 3];

          /* Phase A (0-1.0s): electron jumps from E1 to E3 */
          tl.fromTo("#mt-electron",
            { attr: { cx: 390, cy: 300 } },
            { attr: { cx: 530, cy: 300 }, duration: 1.0, ease: "power2.in" }, t0);
          tl.fromTo("#mt-electron-trail",
            { attr: { cx: 390, cy: 300 }, opacity: 0.5 },
            { attr: { cx: 530, cy: 300 }, opacity: 0.2, duration: 1.0, ease: "power2.in" }, t0);

          /* Heat wave pulse during phase A */
          ["#mt-heatwave path:nth-child(1)", "#mt-heatwave path:nth-child(2)", "#mt-heatwave path:nth-child(3)"].forEach(function(sel, i) {
            tl.fromTo(sel,
              { opacity: 0 },
              { opacity: 0.8, duration: 0.4, ease: "sine.out" }, t0 + i * 0.1);
            tl.to(sel, { opacity: 0, duration: 0.4, ease: "sine.in" }, t0 + 0.7 + i * 0.05);
          });
          if (c === 0) {
            tl.fromTo("#mt-heat-label",
              { opacity: 0 },
              { opacity: 0.95, duration: 0.4 }, t0 + 0.2);
          }

          /* Phase B (1.0-2.5s): electron jitters at E3 */
          tl.fromTo("#mt-electron",
            { attr: { cy: 300 } },
            { attr: { cy: 292 }, duration: 0.3, ease: "sine.inOut",
              yoyo: true, repeat: 4 }, t0 + 1.0);

          /* Phase C (2.5-4.0s): electron falls back to E1 + photon emits */
          tl.to("#mt-electron",
            { attr: { cx: 390, cy: 300 }, duration: 0.6, ease: "power2.out" }, t0 + 2.5);
          tl.to("#mt-electron-trail",
            { attr: { cx: 390, cy: 300 }, opacity: 0.5, duration: 0.6, ease: "power2.out" }, t0 + 2.5);

          /* Photon emission -- line stretches outward, dot flies upper-right */
          tl.set("#mt-photon-line", { attr: { x1: 300, y1: 300, x2: 300, y2: 300 } }, t0 + 2.5);
          tl.set("#mt-photon-line", { stroke: color }, t0 + 2.5);
          tl.set("#mt-photon-dot", { fill: color }, t0 + 2.5);
          tl.set("#mt-photon-dot", { attr: { cx: 300, cy: 300 } }, t0 + 2.5);

          tl.fromTo("#mt-photon-line",
            { opacity: 0, attr: { x2: 300, y2: 300 } },
            { opacity: 0.9, attr: { x2: 480, y2: 150 }, duration: 0.7, ease: "power2.out" }, t0 + 2.6);
          tl.fromTo("#mt-photon-dot",
            { opacity: 0, attr: { cx: 300, cy: 300 } },
            { opacity: 1, attr: { cx: 480, cy: 150 }, duration: 0.7, ease: "power2.out" }, t0 + 2.6);
          tl.to("#mt-photon-line", { opacity: 0, duration: 0.5, ease: "power1.in" }, t0 + 3.3);
          tl.to("#mt-photon-dot", { opacity: 0, duration: 0.5, ease: "power1.in" }, t0 + 3.3);

          if (c === 0) {
            tl.fromTo("#mt-photon-label",
              { opacity: 0 },
              { opacity: 0.95, duration: 0.5 }, t0 + 2.8);
          }
        }

        /* 11. Warning tag emphasis */
        tl.fromTo("#mt-warning",
          { scale: 0.85, opacity: 0 },
          { scale: 1, opacity: 1, duration: 0.6, ease: "back.out(1.5)" }, 17.0);

        /* Continuous amber pulse on warning */
        tl.fromTo("#mt-warning",
          { boxShadow: "0 0 20px rgba(217,119,6,0.1)" },
          { boxShadow: "0 0 40px rgba(217,119,6,0.4)", duration: 0.8, ease: "sine.inOut",
            yoyo: true, repeat: R(0.8) }, 26.0);
        tl.fromTo("#mt-warning",
          { scale: 1 },
          { scale: 1.04, duration: 0.8, ease: "sine.inOut",
            yoyo: true, repeat: R(0.8) }, 26.0);

        window.__timelines["mt-principle"] = tl;
      })();
    </script>
  </div>
</template>
```

**Adaptation notes:**
- Template ID and composition ID renamed from `mt-03-principle` to `mt-principle`; timeline registered on `window.__timelines["mt-principle"]`.
- Background converted from dark (`#0a0e17`) to light (`#f8fafc`) with three aurora orbs in the principle palette: violet `rgba(139,92,246,0.3)`, cyan `rgba(6,182,212,0.22)`, indigo `rgba(99,102,241,0.18)`. The old `.bg-glow` radial gradient is replaced by the aurora-orb structure with GSAP drift animations.
- Opaque panels use `#ffffff` background (border + layered box-shadow for depth).
- All text colors flipped: body `#0f172a`, muted descriptions `#64748b`. KaTeX reset forces `color: #0f172a` with `.katex-mathml { display: none !important; }`. Table color reset included.
- Accent colors remapped: `#00e5ff` to `#6366f1` (indigo), `#4d7cff` to `#6366f1`, `#a855f7` to `#8b5cf6` (violet). SVG energy-level ring strokes, info-num, panel-label, info-label all updated accordingly.
- Photon color array updated: `["#fde047", "#8b5cf6", "#10b981"]` (yellow, violet, emerald) to match the light-theme accent palette.
- Warning tag restyled to amber: `border: 2px solid rgba(217,119,6,0.35)`, `color: #d97706`, `background: rgba(217,119,6,0.06)`. The emoji warn icon replaced with a styled `!` in a circular border.
- `R(d)` helper function replaces all `Math.floor(SCENE_DURATION / d) - 1` patterns for repeat counts. No `Math.random()` or CSS `@keyframes` used.
- All SVG elements preserved: energy-level rings, nucleus with radialGradient, heat-wave paths, photon emission line+dot, electron+trail. All animation cycles (electron transition loop, photon ray, heat-wave pulses, nucleus breathing, ring micro-pulse) retained with identical timing choreography.
- SVG text minimum 22px, strokes 3-5px, electron/photon-dot radius 14px with `bigGlow` filter -- all above specified minimums.
- Chinese text rendered in `"Noto Sans SC"` throughout. To adapt for a different principle topic, replace the SVG diagram contents (rings, nucleus, electron paths), update the panel-label, info-label, and the three info-block titles/descriptions, and adjust the KaTeX equations.
- Left panel `flex: 1.2`, right panel `flex: 1` as specified.

---

## Component Composition Rules

1. Every component is a sub-composition file in `compositions/` using `<template>` wrapper
2. Naming convention: `mt-problem`, `mt-formula`, `mt-geometry`, `mt-steps`, `mt-conclusion`, `mt-flames`, `mt-title`, `mt-equipment`, `mt-procedure`, `mt-comparison`, `mt-principle`
3. All element IDs use `mt-` prefix to avoid collisions
4. KaTeX loads once per composition file from the local `./katex/` copy (inlined CSS + eager JS) — never via CDN
5. Chinese text always uses `font-family: "Noto Sans SC", "PingFang SC", sans-serif`
6. Colors come from design-system.md tokens only (light theme: `#f8fafc` bg, `#0f172a` text, `#6366f1` accent, `#8b5cf6` violet, `#10b981` green, `#d97706` amber, `#dc2626` red)
7. GSAP timelines must be `paused: true` and registered on `window.__timelines`
8. Use `fromTo()` over `from()` in sub-compositions for deterministic seeking
9. Every scene script defines `SCENE_DURATION` and the repeat helper `R(d) = Math.ceil(SCENE_DURATION / d) - 1`
10. Scene fade-in: `tl.fromTo(".scene-content", { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power2.out" }, 0)`
11. Only 2 ambient effects per scene: aurora drift (3 orbs with yoyo motion) + panel shadow breathing
12. No CSS `@keyframes`, no `Math.random()`, no async timeline construction
13. Mandatory color reset in every composition: `.katex, .katex * { color: #0f172a; }`, `.katex-mathml { display: none !important; }`, `table, th, td { color: #0f172a; }`
14. SVG minimum sizes: stroke-width 3px primary / 2px secondary, text 20px, particles radius >= 14px with glow filter
15. **Light rays / trajectories must use progressive drawing animation (光线必须逐段绘制，禁止整条淡入)** — SVG `<line>` rays animate via GSAP `attr` on endpoints (`x2`/`y2` from start to end), NOT `autoAlpha: 0 → 1`. Each segment (incident → refracted) draws sequentially so the viewer sees direction of travel. This applies to ALL scenes with light rays, including overview/principle scenes. See step-5 "Light Ray / Trajectory Drawing Animation" for the full pattern.

---

## Component 12: Circuit Wiring Operation Panel (电路接线操作面板)

A full-screen circuit wiring scene for physics tutorials. Shows a rectangular circuit loop with components distributed around the edges. Used for "连接主回路" (wire the main circuit) and "连接电表" (connect meters) operation scenes. **This is distinct from C9 (Operation Flow) which is for chemistry experiments.**

**Key design rules (from [circuit-schematic-guide.md](circuit-schematic-guide.md) Section 12):**
- Circuit forms a **rectangular loop** — never a flat horizontal line
- Components distributed across **2–3 sides** of the rectangle
- **Component inventory must match the problem (元件清单与题目一致)** — the L₁/L₂ two-bulb loop below is only an EXAMPLE. Replace the components with the problem's actual set (e.g. one 定值电阻 R + one 滑动变阻器). **Single-instance instruments (变阻器/电流表/电压表/开关/电源) appear EXACTLY ONCE** — never duplicate a component (e.g. two 变阻器) to fill a side of the loop; an empty side is just a wire. Gated by `check_circuit_inventory.py`.
- Ammeter is **ON the main loop wire** (bottom return wire), not floating outside
- Voltmeter on a **separate dashed-line branch**, not inline
- Wire routing is **compact** — bounding box tight around components
- Use pre-built CSS components from [ASSET_CATALOG.md](../assets/ASSET_CATALOG.md) (`battery`, `meter.meter-a`, `meter.meter-v`, `switch`, `bulb`, `wire`)

### Template: Circuit Wiring — Connect Meters (连接电表)

```html
<template id="mt-circuit-wiring-template">
  <div data-composition-id="mt-meters" data-width="1920" data-height="1080">
    <div class="scene-bg">
      <div class="bg-texture"></div>
      <div class="aurora-orb a1"></div>
      <div class="aurora-orb a2"></div>
      <div class="aurora-orb a3"></div>
    </div>
    <div class="scene-content">
      <!-- TOP: status bar + info pills -->
      <div class="operation-top">
        <div class="status-bar" id="mt-m-status">连接电表</div>
        <div class="info-pills">
          <div class="pill ammeter" id="pill-a">电流表 A : 串联在干路</div>
          <div class="pill voltmeter" id="pill-v">电压表 V : 并联在 L<sub>2</sub> 两端</div>
        </div>
      </div>

      <!-- BOTTOM: SVG circuit stage -->
      <div class="operation-stage">
        <svg viewBox="0 0 1400 560" xmlns="http://www.w3.org/2000/svg" fill="none">
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="g"/>
              <feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
          </defs>

          <!--
            RECTANGULAR LOOP LAYOUT:
            ┌── Battery ── Switch S ──┐
            │                          │
            │                         L₁
            │                          │
            │                    ┌─V─┐ │  (dashed)
            │                    └──L₂─┘
            │                          │
            └────── Ammeter A ────────┘

            Key coordinates (example):
            - Top-left corner: (120, 100)
            - Top-right corner: (1000, 100)
            - Bottom-right corner: (1000, 460)
            - Bottom-left corner: (120, 460)
            - Battery: top wire, x=250~450
            - Switch: top wire, x=600~750
            - L₁: right side, y=200
            - L₂: right side, y=340
            - Ammeter: bottom wire, x=500
            - Voltmeter: parallel branch left of L₂, x=800
          -->

          <!-- === EXISTING CIRCUIT (dimmed gray) === -->

          <!-- Wire segments (dimmed) — SEGMENTED, not one continuous path -->
          <!-- Top wire: left corner to battery- terminal -->
          <line x1="120" y1="100" x2="250" y2="100"
                stroke="#94a3b8" stroke-width="2.5"/>
          <!-- Top wire: battery+ terminal to switch pivot -->
          <line x1="450" y1="100" x2="600" y2="100"
                stroke="#94a3b8" stroke-width="2.5"/>
          <!-- Top wire: switch contact to top-right corner -->
          <line x1="750" y1="100" x2="1000" y2="100"
                stroke="#94a3b8" stroke-width="2.5"/>
          <!-- Right wire: corner to L₁ top terminal -->
          <line x1="1000" y1="100" x2="1000" y2="170"
                stroke="#94a3b8" stroke-width="2.5"/>
          <!-- Right wire: L₁ bottom terminal to L₂ top terminal -->
          <line x1="1000" y1="230" x2="1000" y2="310"
                stroke="#94a3b8" stroke-width="2.5"/>
          <!-- Right wire: L₂ bottom terminal to bottom-right corner -->
          <line x1="1000" y1="370" x2="1000" y2="460"
                stroke="#94a3b8" stroke-width="2.5"/>

          <!-- Battery (dimmed) -->
          <rect x="250" y="75" width="200" height="50" rx="8"
                fill="rgba(200,200,200,0.3)" stroke="#94a3b8" stroke-width="2"/>
          <text x="350" y="108" font-family="Noto Sans SC,sans-serif"
                font-size="20" fill="#94a3b8" text-anchor="middle">电源</text>

          <!-- Switch (dimmed) -->
          <rect x="600" y="78" width="150" height="44" rx="8"
                fill="rgba(200,200,200,0.3)" stroke="#94a3b8" stroke-width="2"/>
          <text x="675" y="108" font-family="Noto Sans SC,sans-serif"
                font-size="20" fill="#94a3b8" text-anchor="middle">S</text>

          <!-- L₁ (dimmed) -->
          <circle cx="1000" cy="200" r="30"
                  fill="rgba(255,255,200,0.2)" stroke="#94a3b8" stroke-width="2"/>
          <text x="1000" y="208" font-family="Noto Sans SC,sans-serif"
                font-size="20" fill="#94a3b8" text-anchor="middle">L₁</text>

          <!-- L₂ (dimmed) -->
          <circle cx="1000" cy="340" r="30"
                  fill="rgba(255,255,200,0.2)" stroke="#94a3b8" stroke-width="2"/>
          <text x="1000" y="348" font-family="Noto Sans SC,sans-serif"
                font-size="20" fill="#94a3b8" text-anchor="middle">L₂</text>

          <!-- === NEW: AMMETER (bright, on bottom return wire) === -->
          <g id="ammeter-group">
            <rect x="430" y="410" width="140" height="100" rx="14"
                  fill="rgba(255,255,255,0.7)" stroke="#dc2626" stroke-width="3"/>
            <circle cx="500" cy="450" r="32"
                    fill="rgba(255,240,240,0.5)" stroke="#dc2626" stroke-width="2.5"/>
            <line id="needle-a" x1="500" y1="450" x2="500" y2="424"
                  stroke="#dc2626" stroke-width="2.5" stroke-linecap="round"/>
            <text x="500" y="475" font-family="Inter,sans-serif"
                  font-size="24" font-weight="700" fill="#dc2626"
                  text-anchor="middle">A</text>
            <!-- +/- terminals -->
            <text x="540" y="405" font-family="Inter,sans-serif"
                  font-size="16" font-weight="700" fill="#dc2626">+</text>
            <text x="455" y="405" font-family="Inter,sans-serif"
                  font-size="16" font-weight="700" fill="#3b82f6">-</text>
          </g>

          <!-- Ammeter connection wires (bright cyan) -->
          <!-- Wire: bottom-right corner to ammeter+ terminal -->
          <path id="wire-to-a" d="M 1000 460 L 570 460"
                stroke="#06b6d4" stroke-width="4" fill="none"
                stroke-linecap="round" filter="url(#glow)"/>
          <!-- Wire: ammeter- terminal to bottom-left corner, then up to battery- -->
          <path id="wire-from-a" d="M 430 460 L 120 460 L 120 100"
                stroke="#06b6d4" stroke-width="4" fill="none"
                stroke-linecap="round" filter="url(#glow)"/>

          <!-- === NEW: VOLTMETER (bright, parallel branch across L₂) === -->
          <g id="voltmeter-group">
            <rect x="770" y="290" width="140" height="100" rx="14"
                  fill="rgba(255,255,255,0.7)" stroke="#3b82f6" stroke-width="3"/>
            <circle cx="840" cy="330" r="32"
                    fill="rgba(240,240,255,0.5)" stroke="#3b82f6" stroke-width="2.5"/>
            <line id="needle-v" x1="840" y1="330" x2="840" y2="304"
                  stroke="#3b82f6" stroke-width="2.5" stroke-linecap="round"/>
            <text x="840" y="355" font-family="Inter,sans-serif"
                  font-size="24" font-weight="700" fill="#3b82f6"
                  text-anchor="middle">V</text>
            <text x="855" y="287" font-family="Inter,sans-serif"
                  font-size="16" font-weight="700" fill="#dc2626">+</text>
            <text x="855" y="398" font-family="Inter,sans-serif"
                  font-size="16" font-weight="700" fill="#3b82f6">-</text>
          </g>

          <!-- Voltmeter dashed branch wires -->
          <!-- V+ to L₂ top (between L₁ and L₂) -->
          <path id="v-wire-top" d="M 840 290 L 840 240 L 1000 240"
                stroke="#3b82f6" stroke-width="3"
                stroke-dasharray="8,4" fill="none"/>
          <!-- V- to L₂ bottom (after L₂) -->
          <path id="v-wire-bot" d="M 840 390 L 840 440 L 1000 440"
                stroke="#3b82f6" stroke-width="3"
                stroke-dasharray="8,4" fill="none"/>

        </svg>
      </div>
    </div>
  </div>
</template>
```

### Animation Choreography

```js
window.__timelines = window.__timelines || {};
var SCENE_DURATION = 16;
var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };
var tl = gsap.timeline({ paused: true });

try {
  // Scene entrance
  tl.fromTo(".scene-content", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 0);
  tl.fromTo(".status-bar", { y: -20, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.5 }, 0.2);

  // Info pills
  tl.fromTo("#pill-a", { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "back.out(1.4)" }, 0.5);
  tl.fromTo("#pill-v", { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "back.out(1.4)" }, 0.8);

  // Initialize wire dash offsets
  ["#wire-to-a","#wire-from-a","#v-wire-top","#v-wire-bot"].forEach(function(id) {
    try {
      var el = document.querySelector(id);
      if (el) { var len = el.getTotalLength(); el.setAttribute("stroke-dasharray", len); el.setAttribute("stroke-dashoffset", len); }
    } catch(e) {}
  });

  // Phase 1: Ammeter connection (~1.5s to ~5.5s)
  tl.fromTo("#ammeter-group", { autoAlpha: 0, scale: 0.8, transformOrigin: "center" },
    { autoAlpha: 1, scale: 1, duration: 0.6, ease: "back.out(1.4)" }, 1.5);
  tl.to("#wire-to-a", { attr: {"stroke-dashoffset": 0}, duration: 1.2, ease: "power2.out" }, 2.2);
  tl.to("#wire-from-a", { attr: {"stroke-dashoffset": 0}, duration: 1.5, ease: "power2.out" }, 3.5);
  tl.fromTo("#needle-a", { rotation: 0, transformOrigin: "50% 100%" },
    { rotation: 45, duration: 0.8, ease: "elastic.out(1,0.5)" }, 5.0);

  // Phase 2: Voltmeter connection (~7s to ~10s)
  tl.fromTo("#voltmeter-group", { autoAlpha: 0, scale: 0.8, transformOrigin: "center" },
    { autoAlpha: 1, scale: 1, duration: 0.6, ease: "back.out(1.4)" }, 7.0);
  tl.to("#v-wire-top", { attr: {"stroke-dashoffset": 0}, duration: 0.8, ease: "power2.out" }, 7.8);
  tl.to("#v-wire-bot", { attr: {"stroke-dashoffset": 0}, duration: 0.8, ease: "power2.out" }, 8.5);
  tl.fromTo("#needle-v", { rotation: 0, transformOrigin: "50% 100%" },
    { rotation: 35, duration: 0.8, ease: "elastic.out(1,0.5)" }, 9.5);

  // Aurora drift
  tl.fromTo(".a1", { x: 0, y: 0 }, { x: -30, y: 20, duration: 4, ease: "sine.inOut", yoyo: true, repeat: R(4) }, 0);
  tl.fromTo(".a2", { x: 0, y: 0 }, { x: 25, y: -15, duration: 3.5, ease: "sine.inOut", yoyo: true, repeat: R(3.5) }, 0.3);
  tl.fromTo(".a3", { x: 0, y: 0 }, { x: -20, y: 20, duration: 3, ease: "sine.inOut", yoyo: true, repeat: R(3) }, 0.5);

} catch(e) { console.error("Timeline error:", e); }

window.__timelines["mt-meters"] = tl;
```

### Layout Notes

- **SVG viewBox**: `0 0 1400 560` — slightly narrower than C9's 1700px to keep the rectangular loop compact
- **Rectangular loop corners**: top-left (120,100), top-right (1000,100), bottom-right (1000,460), bottom-left (120,460)
- **Ammeter at (500,460)**: centered on the bottom wire, NOT at the far right
- **Voltmeter at (840,340)**: to the LEFT of L₂, on a clearly separate dashed branch
- **Wire segmentation**: each wire segment between components is a separate `<line>`, NOT one continuous path for the whole side
- All wire drawing rules from [circuit-schematic-guide.md](circuit-schematic-guide.md) Sections 8–9, 12 apply
- To adapt: replace component positions, adjust wire endpoints, change meter count. The layout pattern (rectangular loop + meter insertion) is fixed
