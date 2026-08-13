# Golden Example: Interactive HTML Explorer (交互式网页 — 函数与变换)

A **few-shot golden example** for producing a self-contained, offline **interactive HTML page**
(not a video) that lets the user manipulate a math concept and see BOTH a live graph and the
**live equation** update in real time. Distilled from a top-quality "函数变换" explorer so a weaker
model (e.g. qwen3.7) can reproduce the *exact* same effect by following the recipe + copying the
reference implementation and adapting it.

---

## When to use this (NOT the video pipeline)

Use this instead of the Step 0–6 video pipeline when the user asks for an **interactive page /
网页 / 交互式界面 / 让用户拖动体验 / explorer**, i.e. sliders/controls that update a graph AND the
formula live. Deliverable = a folder opened by **double-clicking `index.html`** (offline, no server).

If the user wants a *narrated MP4*, use the normal video pipeline instead.

---

## What the result MUST contain (proven recipe)

1. **Aurora Scholar aesthetic**, reusing this skill's design tokens + shipped assets — fully offline.
2. **Two-panel layout**: left = live **graph (Canvas)**; right = **controls** (function dropdown +
   sliders each with a value "pill" + checkboxes + a reset button).
3. **Dual visualization (核心卖点)**: every control change updates the **graph** AND the **real
   equation** (KaTeX) — "代数式 ↔ 几何图形" 双向联动.
4. **Single source of truth**: both the plotted curve and the displayed equation derive from the
   SAME parameter object — never compute them two different ways.

---

## Output structure (self-contained, offline)

```
<app-dir>/
├── index.html
├── gsap.min.js
├── katex/            katex.min.js  katex.min.css  fonts/…
└── assets/
    ├── fonts/        NotoSansSC-Bold.woff2  …-ExtraBold  …-Black  Inter-Variable  JetBrainsMono-Bold
    └── bg-texture.jpg
```

## Asset setup (copy from this skill — same sources as the video pipeline)

```bash
EDU_SKILL_ROOT="<absolute directory containing qwen-mm-plugins-edu-agent/SKILL.md>"
APP=<app-dir>; SK="$EDU_SKILL_ROOT"
mkdir -p "$APP/katex" "$APP/assets/fonts"
cp "$SK/assets/katex/katex.min.js" "$SK/assets/katex/katex.min.css" "$APP/katex/"
cp -r "$SK/assets/katex/fonts" "$APP/katex/fonts"
cp "$SK/assets/gsap/gsap.min.js" "$APP/"
cp "$SK/assets/fonts/"*.woff2 "$APP/assets/fonts/"
cp "$SK/assets/backgrounds/bg-texture.jpg" "$APP/assets/"
```

All references in `index.html` are **relative** (`./katex/…`, `./gsap.min.js`, `./assets/…`) so the
folder works offline by double-click. **Never** use a CDN `<script>`/`<link>`.

---

## The 6 rules that make it reproduce EXACTLY (每条都踩过坑，必须遵守)

1. **Offline + relative paths.** `./katex/katex.min.js`, `./gsap.min.js`, `./assets/fonts/…`,
   `url('./assets/bg-texture.jpg')`. No CDN, no absolute paths → works by double-click, no server.
2. **Roots/√ via KaTeX, never the bare `√` character.** A bare Unicode `√` (U+221A) has no overbar
   in Noto/Inter and renders as a **comma-like tick** (`√x` looks broken). Render every root — and
   the whole function list at the top — with `katex.render("\\sqrt{x}", el)`. (SKILL rule 12.)
3. **Show the LIVE REAL function, not the abstract form.** The graph panel's title must show the
   actual current equation (e.g. `y = 2·(1.9(x−5))² − 5`) and re-render on every change — NOT a
   static `y = b·f(a(x−h))+k`. Keep the page free of filler footer lines / formal-only expressions.
4. **Visible parentheses on power bases (关键).** The horizontal factor `a(x−h)` must sit **inside**
   the power: render `\left(1.9(x-5)\right)^{2}`, NOT `{1.9(x-5)}^{2}` — invisible braces make it
   look like `1.9(x−5)²` (coefficient outside the square = looks like vertical scaling, WRONG). Use a
   helper that wraps the argument in `\left(...\right)` unless it is a bare `±x`.
5. **Don't `String.replace` a plain letter to inject the argument.** `tex.replace(/t/g, arg)` also
   hits the `t` in `\sqrt` → `\sqrxx`. Build each function's TeX per-type (a `bodyTex(key,inner)`
   switch), or use a collision-free placeholder like `@`.
6. **One transform formula for both curve and equation.**
   `g(x) = sX · b · f( sY · a · (x − h) ) + k`, where `sX = reflectX ? −1 : 1`, `sY = reflectY ? −1 : 1`.
   The plotted function and the KaTeX equation are generated from the SAME `p` (params) object.
   Also: skip non-finite `y` (domain of `log₂`, `√`) and break the path across asymptotes.

---

## Complete reference implementation (copy, then adapt `FUNCS` / labels to the target concept)

This is the exact working `index.html` (function-transform explorer). To reproduce the effect for a
different concept, keep the whole skeleton (aurora bg → intro → left Canvas panel + right controls
panel → live KaTeX equation → offline `<script>`s) and change only `FUNCS`, the controls, and what is
plotted.

```html
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>函数变换 · 交互式探索</title>
<link rel="stylesheet" href="./katex/katex.min.css">
<style>
  @font-face{font-family:"Noto Sans SC";src:url("./assets/fonts/NotoSansSC-Bold.woff2") format("woff2");font-weight:400 700;font-display:swap;}
  @font-face{font-family:"Noto Sans SC";src:url("./assets/fonts/NotoSansSC-ExtraBold.woff2") format("woff2");font-weight:800;font-display:swap;}
  @font-face{font-family:"Noto Sans SC";src:url("./assets/fonts/NotoSansSC-Black.woff2") format("woff2");font-weight:900;font-display:swap;}
  @font-face{font-family:"Inter";src:url("./assets/fonts/Inter-Variable.woff2") format("woff2");font-weight:100 900;font-display:swap;}
  @font-face{font-family:"JetBrains Mono";src:url("./assets/fonts/JetBrainsMono-Bold.woff2") format("woff2");font-weight:700;font-display:swap;}
  :root{--bg:#f8fafc;--surface:#f1f5f9;--panel:#fff;--text:#0f172a;--sec:#64748b;--dim:#94a3b8;
    --indigo:#6366f1;--violet:#8b5cf6;--cyan:#06b6d4;--success:#10b981;--warning:#d97706;}
  *{box-sizing:border-box;}
  html,body{margin:0;background:var(--bg);color:var(--text);font-family:"Noto Sans SC",Inter,sans-serif;}
  .bg{position:fixed;inset:0;z-index:0;overflow:hidden;}
  .bg-tex{position:absolute;inset:0;background:url('./assets/bg-texture.jpg') center/cover no-repeat;opacity:.45;}
  .orb{position:absolute;border-radius:50%;filter:blur(80px);}
  .o1{width:560px;height:560px;background:radial-gradient(circle,rgba(6,182,212,.42),transparent 70%);top:-12%;right:-6%;}
  .o2{width:480px;height:480px;background:radial-gradient(circle,rgba(99,102,241,.36),transparent 70%);bottom:-16%;left:-6%;}
  .o3{width:400px;height:400px;background:radial-gradient(circle,rgba(139,92,246,.28),transparent 70%);top:44%;left:44%;}
  .wrap{position:relative;z-index:1;max-width:1220px;margin:0 auto;padding:28px 22px 56px;}
  .eyebrow{font-family:Inter;font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:12.5px;color:var(--indigo);margin-bottom:7px;}
  h1{margin:0 0 12px;font-weight:900;font-size:32px;}
  .intro{background:var(--panel);border:1px solid rgba(99,102,241,.2);border-left:4px solid var(--cyan);border-radius:14px;
    padding:15px 20px;font-size:15.5px;line-height:1.75;color:#334155;box-shadow:0 4px 16px rgba(99,102,241,.08);}
  .intro b{color:var(--text);}
  .main{display:grid;grid-template-columns:1.35fr 1fr;gap:20px;margin-top:20px;}
  @media(max-width:920px){.main{grid-template-columns:1fr;}}
  .panel{background:var(--panel);border:1px solid rgba(99,102,241,.2);border-top:2px solid rgba(99,102,241,.25);border-radius:18px;
    padding:18px 20px;box-shadow:0 4px 16px rgba(99,102,241,.08),0 16px 48px rgba(99,102,241,.12),inset 0 1px 0 rgba(255,255,255,.6);}
  .panel h2{margin:0 0 12px;font-size:16px;font-weight:800;display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
  .eqtitle .katex{font-size:1.15em;color:var(--indigo);}
  .tag{font-family:Inter;font-size:11px;font-weight:700;color:#fff;background:linear-gradient(135deg,var(--indigo),var(--violet));padding:3px 10px;border-radius:999px;}
  canvas{width:100%;height:auto;display:block;border-radius:12px;background:#fff;border:1px solid rgba(99,102,241,.15);}
  .eqbox{margin-top:14px;background:var(--surface);border:1px solid rgba(99,102,241,.18);border-radius:12px;padding:14px 16px;}
  .eqrow{display:flex;align-items:baseline;gap:10px;margin:6px 0;font-size:15px;flex-wrap:wrap;}
  .eqrow .lab{color:var(--sec);font-size:13px;min-width:56px;}
  .eqrow.base .katex{color:#94a3b8;}
  .legend{display:flex;gap:18px;margin-top:10px;font-size:13px;color:var(--sec);}
  .legend i{display:inline-block;width:22px;height:0;vertical-align:middle;margin-right:6px;}
  .legend .base i{border-top:2px dashed #94a3b8;}
  .legend .now i{border-top:3px solid var(--indigo);}
  .field{margin-bottom:14px;}
  .field>label{display:block;font-weight:700;font-size:14px;margin-bottom:7px;}
  select{width:100%;padding:11px 14px;font-size:15px;font-family:inherit;color:var(--text);background:#fff;
    border:1.5px solid rgba(99,102,241,.3);border-radius:10px;cursor:pointer;}
  .sld{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:5px;}
  .sld .name{font-weight:700;font-size:14px;}
  .pill{font-family:"JetBrains Mono",monospace;font-weight:700;font-size:14px;color:#fff;
    background:linear-gradient(135deg,var(--indigo),var(--violet));border-radius:999px;padding:3px 14px;min-width:52px;text-align:center;}
  input[type=range]{-webkit-appearance:none;width:100%;height:7px;border-radius:999px;background:#e2e8f0;outline:none;margin:3px 0 0;}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:22px;height:22px;border-radius:50%;background:#fff;border:3px solid var(--indigo);cursor:pointer;box-shadow:0 2px 8px rgba(99,102,241,.4);}
  input[type=range]::-moz-range-thumb{width:22px;height:22px;border-radius:50%;background:#fff;border:3px solid var(--indigo);cursor:pointer;}
  .row2{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  .checks{display:flex;gap:22px;margin:6px 0 16px;}
  .chk{display:flex;align-items:center;gap:8px;font-weight:700;font-size:14px;cursor:pointer;user-select:none;}
  .chk input{width:18px;height:18px;accent-color:var(--indigo);cursor:pointer;}
  .reset{width:100%;padding:13px;border:none;border-radius:12px;color:#fff;font-family:inherit;font-weight:800;font-size:15px;cursor:pointer;
    background:linear-gradient(135deg,var(--indigo),var(--violet));box-shadow:0 6px 18px rgba(99,102,241,.35);transition:transform .1s;}
  .reset:active{transform:scale(.98);}
</style>
</head>
<body>
<div class="bg"><div class="bg-tex"></div><div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div></div>
<div class="wrap">
  <div class="eyebrow">Interactive Math · 函数与变换</div>
  <h1>函数变换 · 交互式探索</h1>
  <div class="intro">
    从常见函数中选择（<span id="fnList"></span>），然后应用变换——
    <b>水平/垂直平移、拉伸、反射、缩放</b>——并实时观察图形更新。
    你不仅看到图形的移动与缩放，还会看到 <b>方程本身的变化</b>：这种"代数式 ↔ 几何图形"的双向可视化。
  </div>
  <div class="main">
    <div class="panel">
      <h2><span class="tag">图像</span><span id="eqTitle" class="eqtitle"></span></h2>
      <canvas id="cv" width="720" height="560"></canvas>
      <div class="legend"><span class="base"><i></i>原函数 f(x)</span><span class="now"><i></i>变换后</span></div>
      <div class="eqbox"><div class="eqrow base"><span class="lab">原函数</span><span id="eqBase"></span></div></div>
    </div>
    <div class="panel">
      <h2><span class="tag">控制</span>调节变换参数</h2>
      <div class="field"><label>选择函数</label>
        <select id="fn">
          <option value="linear">一次函数：f(x) = x</option>
          <option value="square" selected>二次函数：f(x) = x²</option>
          <option value="cubic">三次函数：f(x) = x³</option>
          <option value="log2">对数函数：f(x) = log₂(x)</option>
          <option value="sin">正弦函数：f(x) = sin(x)</option>
          <option value="abs">绝对值：f(x) = |x|</option>
          <option value="exp">指数函数：f(x) = eˣ</option>
          <option value="sqrt">平方根：f(x) = √x</option>
          <option value="cos">余弦函数：f(x) = cos(x)</option>
        </select>
      </div>
      <div class="row2">
        <div class="field"><div class="sld"><span class="name">水平平移 (h)</span><span class="pill" id="pH">0.0</span></div><input type="range" id="h" min="-5" max="5" step="0.1" value="0"></div>
        <div class="field"><div class="sld"><span class="name">垂直平移 (k)</span><span class="pill" id="pK">0.0</span></div><input type="range" id="k" min="-5" max="5" step="0.1" value="0"></div>
        <div class="field"><div class="sld"><span class="name">水平缩放 (a)</span><span class="pill" id="pA">1.0</span></div><input type="range" id="a" min="0.2" max="3" step="0.1" value="1"></div>
        <div class="field"><div class="sld"><span class="name">垂直缩放 (b)</span><span class="pill" id="pB">1.0</span></div><input type="range" id="b" min="0.2" max="3" step="0.1" value="1"></div>
      </div>
      <div class="checks">
        <label class="chk"><input type="checkbox" id="rx">关于 X 轴反射</label>
        <label class="chk"><input type="checkbox" id="ry">关于 Y 轴反射</label>
      </div>
      <button class="reset" id="reset">重置所有变换</button>
      <div style="margin-top:14px;font-size:13px;color:var(--sec);line-height:1.7;">
        提示：<b>a</b>&gt;1 水平压缩、&lt;1 水平拉伸；<b>b</b>&gt;1 垂直拉伸、&lt;1 垂直压缩；<b>h</b> 右移、<b>k</b> 上移。对数/平方根仅在定义域内绘制。
      </div>
    </div>
  </div>
</div>
<script src="./katex/katex.min.js"></script>
<script src="./gsap.min.js"></script>
<script>
(function(){
  // base functions: f is the numeric fn; equation TeX is built per-type in bodyTex() (NOT string-replaced).
  var FUNCS={
    linear:{f:function(t){return t;}},
    square:{f:function(t){return t*t;}},
    cubic:{f:function(t){return t*t*t;}},
    log2:{f:function(t){return t>0?Math.log(t)/Math.LN2:NaN;}},   // domain t>0
    sin:{f:function(t){return Math.sin(t);}},
    abs:{f:function(t){return Math.abs(t);}},
    exp:{f:function(t){return Math.exp(t);}},
    sqrt:{f:function(t){return t>=0?Math.sqrt(t):NaN;}},          // domain t>=0
    cos:{f:function(t){return Math.cos(t);}}
  };
  var cv=document.getElementById('cv'), ctx=cv.getContext('2d');
  var VIEW={xmin:-10,xmax:10,ymin:-10,ymax:10}, W=cv.width, H=cv.height;
  function sx(x){return (x-VIEW.xmin)/(VIEW.xmax-VIEW.xmin)*W;}
  function sy(y){return H-(y-VIEW.ymin)/(VIEW.ymax-VIEW.ymin)*H;}
  var el=function(id){return document.getElementById(id);};
  var ctrl={fn:el('fn'),h:el('h'),k:el('k'),a:el('a'),b:el('b'),rx:el('rx'),ry:el('ry')};
  var pill={h:el('pH'),k:el('pK'),a:el('pA'),b:el('pB')};
  function params(){return {key:ctrl.fn.value,h:+ctrl.h.value,k:+ctrl.k.value,a:+ctrl.a.value,b:+ctrl.b.value,rx:ctrl.rx.checked,ry:ctrl.ry.checked};}
  // RULE 6: one transform formula → drives BOTH curve and equation
  function transformed(p){var f=FUNCS[p.key].f,sX=p.rx?-1:1,sY=p.ry?-1:1;return function(x){return sX*p.b*f(sY*p.a*(x-p.h))+p.k;};}
  // ---- canvas ----
  function grid(){
    ctx.clearRect(0,0,W,H);ctx.lineWidth=1;ctx.strokeStyle='#eef2f7';
    for(var gx=VIEW.xmin;gx<=VIEW.xmax;gx++){ctx.beginPath();ctx.moveTo(sx(gx),0);ctx.lineTo(sx(gx),H);ctx.stroke();}
    for(var gy=VIEW.ymin;gy<=VIEW.ymax;gy++){ctx.beginPath();ctx.moveTo(0,sy(gy));ctx.lineTo(W,sy(gy));ctx.stroke();}
    ctx.lineWidth=2;ctx.strokeStyle='#94a3b8';
    ctx.beginPath();ctx.moveTo(0,sy(0));ctx.lineTo(W,sy(0));ctx.stroke();
    ctx.beginPath();ctx.moveTo(sx(0),0);ctx.lineTo(sx(0),H);ctx.stroke();
    ctx.fillStyle='#94a3b8';ctx.font='12px Inter, sans-serif';ctx.textAlign='center';ctx.textBaseline='top';
    for(var tx=VIEW.xmin+2;tx<VIEW.xmax;tx+=2){if(tx!==0)ctx.fillText(tx,sx(tx),sy(0)+5);}
    ctx.textAlign='right';ctx.textBaseline='middle';
    for(var ty=VIEW.ymin+2;ty<VIEW.ymax;ty+=2){if(ty!==0)ctx.fillText(ty,sx(0)-6,sy(ty));}
  }
  function plot(fn,color,width,dash){
    ctx.save();ctx.lineWidth=width;ctx.strokeStyle=color;ctx.setLineDash(dash||[]);
    if(width>=3){ctx.shadowColor='rgba(99,102,241,.35)';ctx.shadowBlur=6;}
    ctx.beginPath();var pen=false;
    for(var px=0;px<=W;px++){var x=VIEW.xmin+px/W*(VIEW.xmax-VIEW.xmin),y=fn(x);
      if(!isFinite(y)||Math.abs(y)>1e4){pen=false;continue;}                 // skip out-of-domain / asymptote
      if(pen)ctx.lineTo(sx(x),sy(y));else{ctx.moveTo(sx(x),sy(y));pen=true;}}
    ctx.stroke();ctx.restore();
  }
  // ---- equation building (RULES 3,4,5) ----
  function numStr(v){v=Math.round(v*10)/10;return (Math.abs(v-Math.round(v))<1e-9)?String(Math.round(v)):v.toFixed(1);}
  function innerTex(p){                                    // argument c*(x-h), c=(ry?-1:1)*a
    var c=(p.ry?-1:1)*p.a, xb;
    if(Math.abs(p.h)<1e-9)xb='x'; else if(p.h>0)xb='x - '+numStr(p.h); else xb='x + '+numStr(-p.h);
    if(Math.abs(c-1)<1e-9)return xb;                       // "x" / "x - 5"
    if(Math.abs(c+1)<1e-9)return (xb==='x')?'-x':'-('+xb+')';
    return numStr(c)+((xb==='x')?'x':'('+xb+')');          // "2x" / "1.9(x - 5)"
  }
  function argParen(inner){return /^-?x$/.test(inner)?inner:'\\left('+inner+'\\right)';}   // RULE 4
  function bodyTex(key,inner){                             // RULE 5: per-type, no naive replace
    switch(key){
      case 'linear':return inner;
      case 'square':return argParen(inner)+'^{2}';
      case 'cubic': return argParen(inner)+'^{3}';
      case 'log2':  return '\\log_{2}\\left('+inner+'\\right)';
      case 'sin':   return '\\sin\\left('+inner+'\\right)';
      case 'cos':   return '\\cos\\left('+inner+'\\right)';
      case 'abs':   return '\\left|'+inner+'\\right|';
      case 'exp':   return 'e^{'+inner+'}';
      case 'sqrt':  return '\\sqrt{'+inner+'}';            // RULE 2: real radical
      default:      return inner;
    }
  }
  function nowTex(p){
    var body=bodyTex(p.key,innerTex(p)), vb=(p.rx?-1:1)*p.b, s;
    if(Math.abs(vb-1)<1e-9)s=body; else if(Math.abs(vb+1)<1e-9)s='-'+body; else s=numStr(vb)+'\\cdot '+body;
    if(Math.abs(p.k)>1e-9)s+=(p.k>0?' + '+numStr(p.k):' - '+numStr(-p.k));
    return 'y = '+s;
  }
  function baseTex(p){return 'f(x) = '+bodyTex(p.key,'x');}
  function kd(id,tex){try{katex.render(tex,el(id),{throwOnError:false});}catch(e){el(id).textContent=tex;}}
  // ---- update: curve + equation from the SAME params ----
  function update(){
    var p=params();
    pill.h.textContent=numStr(p.h);pill.k.textContent=numStr(p.k);pill.a.textContent=numStr(p.a);pill.b.textContent=numStr(p.b);
    grid();
    plot(FUNCS[p.key].f,'#94a3b8',2,[7,6]);   // base dashed gray
    plot(transformed(p),'#6366f1',3.5);       // transformed indigo
    kd('eqBase',baseTex(p));
    kd('eqTitle',nowTex(p));                   // RULE 3: live real function in the title
  }
  ['fn','h','k','a','b'].forEach(function(id){ctrl[id].addEventListener('input',update);});
  ['rx','ry'].forEach(function(id){ctrl[id].addEventListener('change',update);});
  el('reset').addEventListener('click',function(){ctrl.h.value=0;ctrl.k.value=0;ctrl.a.value=1;ctrl.b.value=1;ctrl.rx.checked=false;ctrl.ry.checked=false;update();});
  kd('fnList','y=x,\\; x^2,\\; x^3,\\; \\log_2 x,\\; \\sin x,\\; |x|,\\; e^x,\\; \\sqrt{x},\\; \\cos x');  // RULE 2
  update();
  try{gsap.to('.o1',{x:-30,y:20,duration:8,ease:'sine.inOut',yoyo:true,repeat:-1});
      gsap.to('.o2',{x:26,y:-16,duration:7,ease:'sine.inOut',yoyo:true,repeat:-1});
      gsap.to('.o3',{x:-18,y:18,duration:6,ease:'sine.inOut',yoyo:true,repeat:-1});}catch(e){}
})();
</script>
</body>
</html>
```

---

## Adapting to another interactive concept (keep the skeleton, swap the core)

The skeleton is reusable for any "拖动参数看图形+公式一起变" explorer (e.g. 二次函数配方、正弦
振幅/周期/相位、指数增长、概率分布…). Change only:

- **`FUNCS` / the numeric model** → the quantity you plot.
- **the controls** (dropdown / sliders / checkboxes) → the parameters of your concept.
- **`bodyTex`/`nowTex`** → how the live equation is written (keep RULE 4 visible-paren discipline).
- **the plotted geometry** → a shape/diagram instead of a Canvas curve if the concept is geometric
  (then use SVG + the same "live equation" pattern).

Everything else — aurora background, panel styling, offline asset copy, KaTeX live rendering, sliders
with value pills, reset — stays identical, which is what makes the output look consistently polished.

## Self-check before delivering

- [ ] Double-click `index.html` (file://) renders fully — graph draws, sliders move the curve, the
      equation re-renders. (No server, no network.)
- [ ] Every `√`/root shows a proper radical bar (KaTeX), nowhere a bare comma-like `√`.
- [ ] With a horizontal scale ≠ 1 and a shift, the equation shows `…\left(a(x-h)\right)^n…`
      (coefficient INSIDE the power), and the drawn curve matches that equation.
- [ ] The graph-panel title shows the **actual** current function and updates on every change.
- [ ] No CDN links; all assets present under `katex/`, `gsap.min.js`, `assets/`.
