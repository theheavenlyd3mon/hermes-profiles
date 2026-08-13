# Golden Example: Geometry Proof (q064 — Rotation & Equilateral Triangle)

A complete worked pipeline from problem input to finished video. This example scored top quality for geometry proof tutorials. Study the patterns here before building geometry compositions.

**Problem type:** Geometry proof (旋转变换 + 等边三角形 + 垂直平分线)
**Theme:** `chinese-elegant` (清雅湖蓝)
**Duration:** ~111.5s, 7 scenes
**Key quality traits:** mathematically exact SVG coordinates, GEOMETRY VERIFICATION blocks, progressive draw-on animations synced to narration, split layout (geometry canvas + note blocks)

---

## Pipeline Step 1: PROBLEM.md

```markdown
# Problem Statement

## 校正后题目（视频讲解版本）

已知 ∠MON = 30°，点 A 在射线 OM 上。将线段 OA 绕点 O 顺时针旋转 60° 得到线段 OC（C 落在 ON 下方）。连接 AC 交射线 ON 于点 B；过点 C 作 OA 的垂线，交直线 OA 于垂足、交射线 ON 于点 D。

（1）求证：B 是 AC 的中点。
（2）用等式表示线段 CD 与 AD 的数量关系，并证明。

## Given Values
- ∠MON = 30°
- A 在射线 OM 上，OA 为任意正长度 a
- OC 由 OA 绕 O 顺时针旋转 60° 得到 ⇒ OC = OA = a，∠AOC = 60°
- CD ⊥ OA，D 在射线 ON 上

## Figures
- 顶点 O，射线 OM 与 ON 夹角 30°（OM 在上，ON 水平向右）
- A 在 OM 上；C 在 ON 下方（与 A 关于 ON 对称）
- △OAC 为等边三角形
- B = AC ∩ ON（AC 的中点）
- D = 过 C 垂直于 OA 的直线与 ON 的交点
- 关键：ON 是线段 AC 的垂直平分线
```

**Quality note:** The problem statement includes a correction from the original — the raw task said "B 是 AD 的中点" which is geometrically impossible. The analysis identified this, explained why, and corrected to the self-consistent version. This kind of mathematical rigor in Step 1 prevents downstream errors.

---

## Pipeline Step 2: ANALYSIS.md

```markdown
# Problem Analysis

## Classification
- Type: Geometry（平面几何）
- Sub-type: 旋转变换 + 等边三角形 + 垂直平分线
- Difficulty: intermediate

## Knowledge Points
1. 旋转的性质：对应线段相等（OA = OC），旋转角等于对应边夹角（∠AOC = 60°）。
2. 等边三角形判定：有一个角为 60° 的等腰三角形是等边三角形。
3. 等腰（等边）三角形三线合一：顶角平分线、底边中线、底边高线重合。
4. 线段垂直平分线性质：其上任一点到线段两端距离相等。
5. 角的和差计算。

## Solution Strategy
识别 △OAC 为等边三角形：OA = OC（旋转保长）且 ∠AOC = 60°（旋转角）。
因 ∠AON = ∠MON = 30°，∠CON = 60° − 30° = 30°，
故 ON 平分顶角 ∠AOC。等边三角形三线合一，ON 即 AC 的垂直平分线，两问随之解决。

## Solution Steps
### Step 1: 由旋转得等腰
OA 绕 O 旋转 60° 得 OC ⇒ OA = OC 且 ∠AOC = 60°。
### Step 2: 判定等边三角形
OA = OC，∠AOC = 60° ⇒ △OAC 等边，AC = OA = OC。
### Step 3: 证明 ON 平分 ∠AOC
∠AON = 30°，∠CON = 60° − 30° = 30° ⇒ ON 平分 ∠AOC。
### Step 4: 第一问 B 是 AC 中点
ON 平分等边 △OAC 顶角 ⇒ 顶角平分线也是中线 ⇒ B = AC ∩ ON 是 AC 中点。
### Step 5: 第二问 CD = AD
ON 是 AC 垂直平分线，D 在 ON 上 ⇒ DA = DC ⇒ CD = AD。

## Final Answer
（1）B 是 AC 的中点。（2）CD = AD。

## Coordinate Verification (SVG viewBox 单位)
- O=(140,400) A=(469.09,210) C=(469.09,590) B=(469.09,400) D=(359.39,400) E=(304.55,305)
- OA = OC = AC = 380 ⇒ 等边 ✓
- (A+C)/2 = B ⇒ B 是 AC 中点 ✓
- CD·OA 点积 ≈ 0 ⇒ CD⊥OA ✓
- |CD| = |AD| = 219.39 ⇒ CD = AD ✓

## Scene Plan
| Scene | Name | Duration | Content |
|-------|------|----------|---------|
| 1 | 标题开场 | 5-6s | 旋转变换与线段中点 |
| 2 | 题目呈现 | 14-16s | 题目与两问 |
| 3 | 图形构造 | 15-17s | 画角、旋转得 C、作垂线得 D |
| 4 | 等边三角形 | 13-15s | OA=OC 且 60° ⇒ 等边 |
| 5 | 第一问·B 是中点 | 17-19s | ON 平分顶角 ⇒ 三线合一 |
| 6 | 第二问·CD=AD | 17-19s | 垂直平分线性质 |
| 7 | 结论总结 | 9-11s | 两问结论与关键 |
```

**Quality note:** Coordinates are computed BEFORE any HTML is written. The Coordinate Verification block proves every geometric assertion holds numerically, catching errors before they become rendering bugs.

---

## Pipeline Step 3: SCRIPT.md

```markdown
## 标题开场 (5s)
旋转变换与线段中点。
我们一起攻克这道几何证明题。

## 题目呈现 (15s)
已知角MON等于三十度。
点A在射线OM上。
把OA绕点O顺时针旋转六十度，得到OC。
连接AC，交射线ON于点B。
过点C作OA的垂线，交射线ON于点D。
第一问，求证B是AC的中点。
第二问，求CD与AD的数量关系。

## 图形构造 (16s)
我们先把图形画出来。
射线OM与ON的夹角是三十度。
把OA顺时针旋转六十度，得到OC。
旋转不改变长度，所以OA等于OC。
再过C作OA的垂线，交ON于点D。

## 关键发现·等边三角形 (14s)
这里有一个关键的发现。
OA等于OC，而且它们的夹角是六十度。
有一个角是六十度的等腰三角形，一定是等边三角形。
所以三角形OAC是等边三角形。

## 第一问·B是中点 (18s)
下面证明第一问。
角AON就等于角MON，是三十度。
角CON等于六十度减三十度，也是三十度。
所以ON平分角AOC。
等边三角形三线合一，顶角平分线也是底边中线。
因此ON经过AC的中点，B就是AC的中点。

## 第二问·CD等于AD (18s)
接下来看第二问。
因为ON平分等边三角形的顶角。
所以ON是AC的垂直平分线。
点D在ON上，到A和到C的距离相等。
于是DA等于DC，也就是CD等于AD。

## 结论总结 (10s)
我们来总结一下。
旋转产生等边三角形，是解题的关键。
ON是AC的垂直平分线，一举解决两个问题。
```

**Quality note:** Each sentence is short and self-contained (one caption per sentence). Pacing is ~3.5-4 chars/sec. Math symbols are spoken in Chinese ("角MON等于三十度" not "∠MON=30°"). Section headers map 1:1 to storyboard scenes.

---

## Pipeline Step 4: STORYBOARD.md

```markdown
## Global Direction
- Format: 1920x1080
- Theme: chinese-elegant (lake-blue) for geometry scenes; title/problem aurora-scholar-ish; conclusion mint
- Transition: crossfade via per-scene 0.3s fade-in
- Total duration: ~111.5s

## Scene timing (from transcript.json)
| Scene | Start | Dur | Sentences |
|-------|-------|-----|-----------|
| title | 0.00 | 5.16 | 0-1 |
| problem | 5.16 | 24.82 | 2-8 |
| construct | 29.98 | 16.70 | 9-13 |
| equilateral | 46.68 | 14.24 | 14-17 |
| part1 | 60.92 | 22.92 | 18-23 |
| part2 | 83.84 | 16.70 | 24-28 |
| conclusion | 100.54 | 10.94 | 29-31 |

### Scene: mt-construct
- Component: Geometry Canvas (split). Content: 画角、旋转得 C、连 AC 得 B、作垂线得 D.
- Motion: draw-on rays/segments sequential, B pulse. Palette: teal/cyan.

### Scene: mt-equilateral
- Component: Geometry Canvas (split). Content: OA=OC & 60° ⇒ 等边三角形 OAC.
- Motion: triangle fill + equal-side ticks. Palette: cyan/teal.

### Scene: mt-part1
- Component: Geometry Canvas (split). Content: ON 平分顶角 ⇒ 三线合一 ⇒ B 是 AC 中点.
- Motion: ∠CON arc, OB bisector draw-on, right-angle at B, AB=BC ticks.

### Scene: mt-part2
- Component: Geometry Canvas (split). Content: ON 是 AC 垂直平分线 ⇒ DA=DC ⇒ CD=AD.
- Motion: draw AD/CD, equal double ticks, D pulse. Palette: emerald.
```

**Quality note:** Scene timing comes directly from `transcript.json` (measured TTS durations, not estimated). Each scene maps to exactly one teaching concept. The split layout (Geometry Canvas + note blocks) is used consistently for all proof scenes.

---

## Pipeline Step 5: Key Composition Examples

### Example A: Geometry Construction Scene (scene-construct.html)

This is the most instructive composition — it demonstrates progressive geometry drawing with draw-on animations synced to narration timing.

```html
<template id="mt-construct-template">
<div data-composition-id="mt-construct" id="mt-construct" data-width="1920" data-height="1080">
  <div class="scene-bg">
    <div class="bg-texture"></div>
    <div class="aurora-orb a1"></div>
    <div class="aurora-orb a2"></div>
    <div class="aurora-orb a3"></div>
  </div>

  <div class="scene-content">
    <div class="geo-wrap">
      <div class="geo-panel glass-panel">
        <!-- GEOMETRY VERIFICATION
        POINTS: O=(140,400) A=(469.09,210) B=(469.09,400) C=(469.09,590) D=(359.39,400) E=(304.55,305)
        ASSERT midpoint B A C
        ASSERT midpoint E O A
        ASSERT perpendicular C D O A
        ASSERT perpendicular A C O B
        ASSERT on_segment D O B
        ASSERT ratio |CD| |AD| 1.0
        -->
        <svg viewBox="60 120 680 540" id="mt-c-svg">
          <defs>
            <marker id="axArr" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="12" refX="12" refY="6" orient="auto">
              <polygon points="0 0, 14 6, 0 12" fill="#0f172a"/>
            </marker>
            <filter id="cGlow"><feGaussianBlur stdDeviation="2.4" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
          </defs>

          <line id="ln-on" x1="140" y1="400" x2="620" y2="400" class="shape-ray" marker-end="url(#axArr)"/>
          <line id="ln-om" x1="140" y1="400" x2="555.7" y2="160" class="shape-ray" marker-end="url(#axArr)"/>
          <line id="ln-oc" x1="140" y1="400" x2="469.09" y2="590" class="shape-oc"/>
          <line id="ln-ac" x1="469.09" y1="210" x2="469.09" y2="590" class="shape-ac"/>
          <line id="ln-perp" x1="469.09" y1="590" x2="304.55" y2="305" class="shape-perp"/>
          <path id="ra-mark" d="M313.55,320.59 L297.96,329.59 L288.96,314.0" class="ra"/>
          <path id="arc30" d="M178.1,378 A44,44 0 0,1 184,400" class="geo-ang"/>
          <text id="lb-ang" x="232" y="380" text-anchor="middle" class="ang-label">30&deg;</text>

          <circle id="dot-O" cx="140" cy="400" r="6" class="geo-dot" filter="url(#cGlow)"/>
          <circle id="dot-A" cx="469.09" cy="210" r="6" class="geo-dot" filter="url(#cGlow)"/>
          <circle id="dot-C" cx="469.09" cy="590" r="6" class="geo-dot" filter="url(#cGlow)"/>
          <circle id="dot-B" cx="469.09" cy="400" r="7" class="geo-dot-b" filter="url(#cGlow)"/>
          <circle id="dot-D" cx="359.39" cy="400" r="6" class="geo-dot-d" filter="url(#cGlow)"/>

          <text id="lb-O" x="116" y="432" text-anchor="end" class="geo-label">O</text>
          <text id="lb-A" x="456" y="186" text-anchor="end" class="geo-label">A</text>
          <text id="lb-B" x="492" y="382" text-anchor="start" class="geo-label-b">B</text>
          <text id="lb-C" x="492" y="610" text-anchor="start" class="geo-label">C</text>
          <text id="lb-D" x="352" y="436" text-anchor="middle" class="geo-label-d">D</text>
          <text id="lb-M" x="548" y="140" text-anchor="start" class="geo-label-r">M</text>
          <text id="lb-N" x="632" y="428" text-anchor="start" class="geo-label-r">N</text>
        </svg>
      </div>

      <div class="geo-notes">
        <div class="note-block nb1">
          <div class="nb-num">条件</div>
          <div class="nb-txt">射线 OM 与 ON 的夹角 角MON = 30&deg;</div>
        </div>
        <div class="note-block nb2">
          <div class="nb-num">旋转</div>
          <div class="nb-txt">OA 顺时针旋转 60&deg; 得 OC，旋转保长，OA = OC</div>
        </div>
        <div class="note-block nb3">
          <div class="nb-num">作图</div>
          <div class="nb-txt">连 AC 交 ON 于 B；过 C 作 OA 垂线，交 ON 于 D</div>
        </div>
      </div>
    </div>
  </div>

  <style>
    @font-face { font-family:"Noto Sans SC"; src:url("assets/fonts/NotoSansSC-Bold.woff2") format("woff2"); font-weight:400 700; font-display:swap; }
    @font-face { font-family:"Inter"; src:url("assets/fonts/Inter-Variable.woff2") format("woff2"); font-weight:100 900; font-display:swap; }
    #mt-construct{ position:relative; width:1920px; height:1080px; background:#e8f4f8; color:#0f172a;
      font-family:"Noto Sans SC", Inter, sans-serif; overflow:hidden; }
    #mt-construct .scene-bg{ position:absolute; inset:0; }
    /* chinese-elegant theme: CSS gradient instead of bg-texture.jpg */
    #mt-construct .bg-texture{ position:absolute; inset:0; z-index:0; background:linear-gradient(135deg, #e8f4f8 0%, #d1e8ef 40%, #bdd9e6 70%, #d6eaf0 100%); }
    #mt-construct .aurora-orb{ position:absolute; border-radius:50%; filter:blur(80px); pointer-events:none; }
    #mt-construct .a1{ width:520px; height:520px; background:radial-gradient(circle, rgba(20,184,166,0.5) 0%, transparent 70%); top:-10%; right:-5%; }
    #mt-construct .a2{ width:420px; height:420px; background:radial-gradient(circle, rgba(56,189,248,0.4) 0%, transparent 70%); bottom:-14%; left:-5%; }
    #mt-construct .a3{ width:360px; height:360px; background:radial-gradient(circle, rgba(6,182,212,0.35) 0%, transparent 70%); top:42%; left:46%; }
    #mt-construct .scene-content{ position:absolute; inset:0; z-index:1; display:flex; align-items:center; justify-content:center;
      padding:40px 60px 180px; box-sizing:border-box; }
    #mt-construct .glass-panel{ background:#ffffff; border:1px solid rgba(20,184,166,0.28); border-top:2px solid rgba(20,184,166,0.22);
      border-radius:22px; box-shadow:0 4px 16px rgba(20,184,166,0.08), 0 16px 48px rgba(20,184,166,0.12), inset 0 1px 0 rgba(255,255,255,0.6); }
    /* Split layout: geometry (left 1.35fr) + notes (right 1fr) */
    #mt-construct .geo-wrap{ display:flex; gap:40px; align-items:stretch; width:1680px; height:800px; }
    #mt-construct .geo-panel{ flex:1.35; padding:20px; display:flex; align-items:center; justify-content:center; }
    #mt-construct .geo-panel svg{ width:100%; height:100%; }
    #mt-construct .geo-notes{ flex:1; display:flex; flex-direction:column; gap:24px; justify-content:center; }
    #mt-construct .note-block{ background:#ffffff; border:1px solid rgba(20,184,166,0.22); border-left:5px solid #14b8a6;
      border-radius:16px; padding:26px 30px; box-shadow:0 4px 16px rgba(20,184,166,0.08); }
    #mt-construct .nb-num{ font-size:22px; font-weight:800; color:#0e9488; margin-bottom:10px; }
    #mt-construct .nb-txt{ font-size:30px; line-height:1.5; color:#0f172a; font-weight:600; }
    /* SVG styles */
    #mt-construct .shape-ray{ stroke:#0f172a; stroke-width:3; fill:none; }
    #mt-construct .shape-oc{ stroke:#06b6d4; stroke-width:4; fill:none; }
    #mt-construct .shape-ac{ stroke:#6366f1; stroke-width:4; fill:none; }
    #mt-construct .shape-perp{ stroke:#8b5cf6; stroke-width:3; fill:none; stroke-dasharray:9 6; }
    #mt-construct .ra{ stroke:#d97706; stroke-width:2.5; fill:none; }
    #mt-construct .geo-ang{ stroke:#d97706; stroke-width:3; fill:none; }
    #mt-construct .ang-label{ fill:#d97706; font-size:28px; font-weight:700; font-family:Inter, sans-serif; }
    #mt-construct .geo-dot{ fill:#6366f1; }
    #mt-construct .geo-dot-b{ fill:#10b981; }
    #mt-construct .geo-dot-d{ fill:#8b5cf6; }
    #mt-construct .geo-label{ fill:#0f172a; font-size:30px; font-weight:700; font-family:Inter, sans-serif; }
    #mt-construct .geo-label-b{ fill:#059669; font-size:30px; font-weight:800; font-family:Inter, sans-serif; }
    #mt-construct .geo-label-d{ fill:#7c3aed; font-size:30px; font-weight:800; font-family:Inter, sans-serif; }
    #mt-construct .geo-label-r{ fill:#334155; font-size:28px; font-weight:700; font-family:Inter, sans-serif; }
  </style>

  <script src="./gsap/gsap.min.js"></script>
  <script>
    (function(){
      window.__timelines = window.__timelines || {};
      var SCENE_DURATION = 16.5;
      var R = function(d){ return Math.ceil(SCENE_DURATION / d) - 1; };
      var tl = gsap.timeline({ paused:true });
      try {
        // fade in
        tl.fromTo(".scene-content", { autoAlpha:0 }, { autoAlpha:1, duration:0.3, ease:"power2.out" }, 0);
        tl.fromTo("#mt-construct .geo-panel", { y:40, autoAlpha:0 }, { y:0, autoAlpha:1, duration:0.6, ease:"power3.out" }, 0.2);
        // progressive draw-on: rays first, then points, then connections
        tl.fromTo("#ln-on", { attr:{ x2:140, y2:400 } }, { attr:{ x2:620, y2:400 }, duration:0.8, ease:"power2.inOut" }, 0.6);
        tl.fromTo("#ln-om", { attr:{ x2:140, y2:400 } }, { attr:{ x2:555.7, y2:160 }, duration:0.8, ease:"power2.inOut" }, 1.2);
        tl.fromTo(["#dot-O","#lb-O"], { autoAlpha:0 }, { autoAlpha:1, duration:0.3 }, 0.8);
        tl.fromTo(["#lb-M","#lb-N"], { autoAlpha:0 }, { autoAlpha:1, duration:0.3 }, 1.6);
        tl.fromTo(["#arc30","#lb-ang"], { autoAlpha:0 }, { autoAlpha:1, duration:0.4 }, 1.9);
        // A appears on OM
        tl.fromTo(["#dot-A","#lb-A"], { autoAlpha:0 }, { autoAlpha:1, duration:0.4, ease:"back.out(1.6)" }, 2.4);
        // rotate OA → OC (draw-on from O to C)
        tl.fromTo("#ln-oc", { attr:{ x2:140, y2:400 } }, { attr:{ x2:469.09, y2:590 }, duration:1.0, ease:"power2.inOut" }, 3.2);
        tl.fromTo(["#dot-C","#lb-C"], { autoAlpha:0 }, { autoAlpha:1, duration:0.4, ease:"back.out(1.6)" }, 4.2);
        // connect AC → B appears
        tl.fromTo("#ln-ac", { attr:{ x2:469.09, y2:210 } }, { attr:{ x2:469.09, y2:590 }, duration:0.9, ease:"power2.inOut" }, 4.8);
        tl.fromTo(["#dot-B","#lb-B"], { autoAlpha:0 }, { autoAlpha:1, duration:0.4, ease:"back.out(1.8)" }, 5.7);
        // perpendicular from C → D
        tl.fromTo("#ln-perp", { attr:{ x2:469.09, y2:590 } }, { attr:{ x2:304.55, y2:305 }, duration:1.0, ease:"power2.inOut" }, 6.3);
        tl.fromTo("#ra-mark", { autoAlpha:0 }, { autoAlpha:1, duration:0.3 }, 7.2);
        tl.fromTo(["#dot-D","#lb-D"], { autoAlpha:0 }, { autoAlpha:1, duration:0.4, ease:"back.out(1.6)" }, 7.0);
        // note blocks stagger in sync with narration
        tl.fromTo("#mt-construct .nb1", { x:30, autoAlpha:0 }, { x:0, autoAlpha:1, duration:0.5, ease:"power2.out" }, 1.6);
        tl.fromTo("#mt-construct .nb2", { x:30, autoAlpha:0 }, { x:0, autoAlpha:1, duration:0.5, ease:"power2.out" }, 3.4);
        tl.fromTo("#mt-construct .nb3", { x:30, autoAlpha:0 }, { x:0, autoAlpha:1, duration:0.5, ease:"power2.out" }, 6.4);
        // B pulses to draw attention
        tl.fromTo("#dot-B", { attr:{ r:7 } }, { attr:{ r:10 }, duration:0.9, ease:"sine.inOut", yoyo:true, repeat:R(0.9) }, 6.2);
        // ambient aurora drift
        tl.fromTo(".a1", { x:0, y:0 }, { x:-36, y:26, duration:4, ease:"sine.inOut", yoyo:true, repeat:R(4) }, 0);
        tl.fromTo(".a2", { x:0, y:0 }, { x:30, y:-18, duration:3.5, ease:"sine.inOut", yoyo:true, repeat:R(3.5) }, 0.5);
        tl.fromTo(".a3", { x:0, y:0 }, { x:-22, y:22, duration:3, ease:"sine.inOut", yoyo:true, repeat:R(3) }, 0.3);
      } catch(e){ console.error("mt-construct timeline error", e); }
      window.__timelines["mt-construct"] = tl;
    })();
  </script>
</div>
</template>
```

**Key patterns in this composition:**
1. **Draw-on animation** — lines start collapsed at origin (`attr:{x2:140, y2:400}`) and extend to their endpoint, simulating hand-drawing
2. **Progressive reveal** — elements appear in the order a teacher would draw them: rays → angle → point A → rotation to C → connect AC → B → perpendicular → D
3. **Narration sync** — note blocks appear at the same time the narrator mentions them (nb1 at 1.6s when "射线OM与ON" is spoken, nb2 at 3.4s for "旋转")
4. **Emphasis pulse** — key point B pulses via yoyo radius animation to highlight the answer
5. **GEOMETRY VERIFICATION block** — all assertions are mathematically verifiable from the declared coordinates

---

### Example B: Proof Step Scene (scene-part1.html)

This shows how a proof reasoning step builds on the same geometry with new visual overlays.

```html
<template id="mt-part1-template">
<div data-composition-id="mt-part1" id="mt-part1" data-width="1920" data-height="1080">
  <div class="scene-bg">
    <div class="bg-texture"></div>
    <div class="aurora-orb a1"></div>
    <div class="aurora-orb a2"></div>
    <div class="aurora-orb a3"></div>
  </div>

  <div class="scene-content">
    <div class="geo-wrap">
      <div class="geo-panel glass-panel">
        <!-- GEOMETRY VERIFICATION
        POINTS: O=(140,400) A=(469.09,210) B=(469.09,400) C=(469.09,590) D=(359.39,400) E=(304.55,305)
        ASSERT midpoint B A C
        ASSERT perpendicular A C O B
        ASSERT on_segment B A C
        ASSERT ratio |AB| |BC| 1.0
        -->
        <svg viewBox="60 120 680 540" id="mt-p1-svg">
          <defs>
            <marker id="axArr1" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="12" refX="12" refY="6" orient="auto">
              <polygon points="0 0, 14 6, 0 12" fill="#0f172a"/>
            </marker>
            <filter id="p1Glow"><feGaussianBlur stdDeviation="2.4" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
          </defs>

          <polygon points="140,400 469.09,210 469.09,590" class="tri-answer"/>

          <line x1="140" y1="400" x2="620" y2="400" class="shape-ray" marker-end="url(#axArr1)"/>
          <line x1="140" y1="400" x2="555.7" y2="160" class="shape-ray" marker-end="url(#axArr1)"/>
          <!-- OB bisector drawn via GSAP from O to B -->
          <line id="ob-hl" x1="140" y1="400" x2="469.09" y2="400" class="bisector"/>
          <line x1="140" y1="400" x2="469.09" y2="590" class="shape-oc"/>
          <line x1="469.09" y1="210" x2="469.09" y2="590" class="shape-ac"/>

          <!-- equal-length ticks on AB and BC -->
          <line id="tk-ab" x1="459.09" y1="305" x2="479.09" y2="305" class="tick"/>
          <line id="tk-bc" x1="459.09" y1="495" x2="479.09" y2="495" class="tick"/>
          <!-- right angle at B -->
          <path id="rab" d="M451.09,400 L451.09,382 L469.09,382" class="ra"/>

          <!-- existing 30° arc + new CON 30° arc -->
          <path d="M178.1,378 A44,44 0 0,1 184,400" class="geo-ang"/>
          <text x="232" y="380" text-anchor="middle" class="ang-label">30&deg;</text>
          <path id="arc-con" d="M184,400 A44,44 0 0,1 178.1,422" class="geo-ang"/>
          <text id="lb-con" x="232" y="424" text-anchor="middle" class="ang-label">30&deg;</text>

          <!-- dots and labels (same coordinates as construct scene) -->
          <circle cx="140" cy="400" r="6" class="geo-dot" filter="url(#p1Glow)"/>
          <circle cx="469.09" cy="210" r="6" class="geo-dot" filter="url(#p1Glow)"/>
          <circle cx="469.09" cy="590" r="6" class="geo-dot" filter="url(#p1Glow)"/>
          <circle id="dot-b1" cx="469.09" cy="400" r="8" class="geo-dot-b" filter="url(#p1Glow)"/>

          <text x="116" y="432" text-anchor="end" class="geo-label">O</text>
          <text x="456" y="186" text-anchor="end" class="geo-label">A</text>
          <text x="492" y="382" text-anchor="start" class="geo-label-b">B</text>
          <text x="492" y="610" text-anchor="start" class="geo-label">C</text>
          <text x="548" y="140" text-anchor="start" class="geo-label-r">M</text>
          <text x="632" y="428" text-anchor="start" class="geo-label-r">N</text>
        </svg>
      </div>

      <div class="geo-notes">
        <div class="note-block nb1">
          <div class="nb-num">第 1 步</div>
          <div class="nb-txt">角AON = 角MON = 30&deg;</div>
        </div>
        <div class="note-block nb2">
          <div class="nb-num">第 2 步</div>
          <div class="nb-txt">角CON = 60&deg; &minus; 30&deg; = 30&deg;，故 ON 平分 角AOC</div>
        </div>
        <div class="note-block nb3">
          <div class="nb-num">第 3 步</div>
          <div class="nb-txt">等边三角形三线合一：顶角平分线也是底边中线</div>
        </div>
        <div class="note-block nb4 hl">
          <div class="nb-num">结论 一</div>
          <div class="nb-txt">B 是 AC 的中点（同时 OB 垂直 AC）</div>
        </div>
      </div>
    </div>
  </div>

  <!-- CSS same structure as construct but with proof-specific elements (bisector, ticks) -->
  <!-- ... (same chinese-elegant theme, same split layout) ... -->

  <script src="./gsap/gsap.min.js"></script>
  <script>
    (function(){
      window.__timelines = window.__timelines || {};
      var SCENE_DURATION = 22.9;
      var R = function(d){ return Math.ceil(SCENE_DURATION / d) - 1; };
      var tl = gsap.timeline({ paused:true });
      try {
        tl.fromTo(".scene-content", { autoAlpha:0 }, { autoAlpha:1, duration:0.3, ease:"power2.out" }, 0);
        tl.fromTo("#mt-part1 .geo-panel", { y:40, autoAlpha:0 }, { y:0, autoAlpha:1, duration:0.6, ease:"power3.out" }, 0.2);
        // new ∠CON arc appears when narrator says "角CON"
        tl.fromTo(["#arc-con","#lb-con"], { autoAlpha:0 }, { autoAlpha:1, duration:0.4 }, 6.0);
        // OB bisector draws on when "ON平分角AOC" is spoken
        tl.fromTo("#ob-hl", { attr:{ x2:140 } }, { attr:{ x2:469.09 }, duration:1.0, ease:"power2.inOut" }, 9.5);
        // right angle mark at B
        tl.fromTo("#rab", { autoAlpha:0 }, { autoAlpha:1, duration:0.4 }, 12.5);
        // equal-length ticks pop in with back easing
        tl.fromTo(["#tk-ab","#tk-bc"], { autoAlpha:0, scale:0.4, transformOrigin:"center" }, { autoAlpha:1, scale:1, duration:0.5, ease:"back.out(2)", stagger:0.2 }, 15.5);
        // note blocks timed to narration
        tl.fromTo("#mt-part1 .nb1", { x:30, autoAlpha:0 }, { x:0, autoAlpha:1, duration:0.5, ease:"power2.out" }, 2.0);
        tl.fromTo("#mt-part1 .nb2", { x:30, autoAlpha:0 }, { x:0, autoAlpha:1, duration:0.5, ease:"power2.out" }, 6.0);
        tl.fromTo("#mt-part1 .nb3", { x:30, autoAlpha:0 }, { x:0, autoAlpha:1, duration:0.5, ease:"power2.out" }, 13.0);
        tl.fromTo("#mt-part1 .nb4", { x:30, autoAlpha:0 }, { x:0, autoAlpha:1, duration:0.6, ease:"back.out(1.3)" }, 18.0);
        // B pulses throughout
        tl.fromTo("#dot-b1", { attr:{ r:8 } }, { attr:{ r:11 }, duration:0.9, ease:"sine.inOut", yoyo:true, repeat:R(0.9) }, 15.5);
        // ambient
        tl.fromTo(".a1", { x:0, y:0 }, { x:-34, y:24, duration:4, ease:"sine.inOut", yoyo:true, repeat:R(4) }, 0);
        tl.fromTo(".a2", { x:0, y:0 }, { x:28, y:-18, duration:3.5, ease:"sine.inOut", yoyo:true, repeat:R(3.5) }, 0.5);
        tl.fromTo(".a3", { x:0, y:0 }, { x:-20, y:20, duration:3, ease:"sine.inOut", yoyo:true, repeat:R(3) }, 0.3);
      } catch(e){ console.error("mt-part1 timeline error", e); }
      window.__timelines["mt-part1"] = tl;
    })();
  </script>
</div>
</template>
```

**Key patterns in this proof scene:**
1. **Same geometry, new overlays** — the base figure (rays, points, triangle) is fully visible from the start; new elements (∠CON arc, OB bisector, ticks) are added as the proof progresses
2. **Conclusion highlight** — the final note block (nb4) has `.hl` class for green accent, emphasizing the answer
3. **Visual proof markers** — equal-length ticks appear with `back.out(2)` bounce to emphasize AB = BC
4. **4 note blocks** — proof scenes use 3 reasoning steps + 1 conclusion, vs construction scenes using 3 descriptive steps

---

## Pipeline Step 6: Root index.html Wiring

```html
<!doctype html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <style>
    /* @font-face blocks for Noto Sans SC, Inter, JetBrains Mono */
    /* ... */
    .caption-bar {
      position:absolute; bottom:48px; left:50%; transform:translateX(-50%);
      z-index:2147483647;
      font-family:"Noto Sans SC", Inter, sans-serif;
      font-size:38px; font-weight:700; line-height:1.4;
      color:#ffffff;
      background:rgba(15,23,42,0.86);
      border:1px solid rgba(99,102,241,0.35);
      border-radius:16px; padding:12px 36px;
      width:max-content; max-width:1600px;
      text-align:center; white-space:normal; overflow-wrap:break-word; text-wrap:balance;
      box-shadow:0 8px 28px rgba(15,23,42,0.35);
    }
  </style>
  <script src="./gsap/gsap.min.js"></script>
</head>
<body>
  <div data-composition-id="math-tutorial"
       data-start="0" data-duration="111.5" data-width="1920" data-height="1080">

    <audio data-start="0" data-duration="110.48" data-track-index="0" src="narration.wav" data-volume="1"></audio>

    <!-- Each scene: data-composition-src points to external HTML, timing from transcript.json -->
    <div data-composition-id="mt-title" data-composition-src="compositions/scene-title.html"
         data-start="0.0" data-duration="5.16" data-track-index="1" data-width="1920" data-height="1080"></div>
    <div data-composition-id="mt-problem" data-composition-src="compositions/scene-problem.html"
         data-start="5.16" data-duration="24.82" data-track-index="1" data-width="1920" data-height="1080"></div>
    <div data-composition-id="mt-construct" data-composition-src="compositions/scene-construct.html"
         data-start="29.98" data-duration="16.7" data-track-index="1" data-width="1920" data-height="1080"></div>
    <!-- ... equilateral, part1, part2, conclusion ... -->

    <!-- Captions: one per narration sentence, data-track-index="2" -->
    <div class="clip caption-bar" data-start="0.0" data-duration="2.16" data-track-index="2">旋转变换与线段中点。</div>
    <div class="clip caption-bar" data-start="2.46" data-duration="2.4" data-track-index="2">我们一起攻克这道几何证明题。</div>
    <!-- ... one caption per sentence, timing from transcript.json ... -->
  </div>

  <script>
    window.__timelines = window.__timelines || {};
    var tl = gsap.timeline({ paused:true });
    window.__timelines["math-tutorial"] = tl;
  </script>
</body>
</html>
```

---

## Quality Patterns Summary (Geometry Proofs)

### Coordinate Computation Workflow
1. Choose base length in viewBox units (e.g., OA = 380)
2. Place origin O (e.g., 140, 400)
3. Compute all other points from angles and lengths using trigonometry
4. Write GEOMETRY VERIFICATION block with all assertions
5. Run `check_geometry_verification.py` to validate

### Scene Progression Pattern
| Scene | Purpose | Layout | Key Animation |
|-------|---------|--------|---------------|
| title | Hook | Full-screen centered | Gradient text rise + underline sweep |
| problem | Statement | Single wide card | Card rise with 3D tilt |
| construct | Build figure | Split: SVG + notes | Progressive draw-on |
| key insight | Core theorem | Split: SVG + notes | Triangle fill + equal ticks |
| proof step | Reasoning | Split: SVG + notes | New overlays + step blocks |
| conclusion | Answer | Single wide card | Answer boxes + key summary |

### Animation Timing Rules
- Scene fade-in: always at t=0, duration 0.3s
- Geometry panel: rises at t=0.2s
- SVG elements: draw-on sequentially, ~0.8-1.0s each, 0.4-0.8s gaps
- Note blocks: stagger in from right (x:30 → 0), synced to narration timestamps
- Key dots: pulse via yoyo radius animation throughout scene
- Aurora drift: always present, fills scene duration via R() helper

### Split Layout CSS Skeleton
```css
.geo-wrap { display:flex; gap:40px; align-items:stretch; width:1680px; height:800px; }
.geo-panel { flex:1.35; }  /* SVG side — wider */
.geo-notes { flex:1; display:flex; flex-direction:column; gap:24px; justify-content:center; }
```

### Color Coding in Geometry SVGs
- Rays/axes: `#0f172a` (dark, stroke-width 3)
- Primary constructions (OC, AC): `#06b6d4` cyan / `#6366f1` indigo (stroke-width 4-5)
- Auxiliary lines (perpendiculars): `#8b5cf6` violet (dashed, stroke-width 3)
- Key points (B, answer): `#10b981` emerald with glow
- Angles: `#d97706` amber
- Equal ticks: `#0e7490` dark-cyan or `#dc2626` red
- Answer segments: `#10b981` emerald (stroke-width 5)
