# Step 6: Compose & Render

Assemble the root composition, validate, preview, and render. Invoke the `hyperframes-cli` skill for detailed CLI options.

**All commands in this step run inside `dist/`.** Use `cd dist` before running any hyperframes CLI command.

## Root Composition Assembly

Build `dist/index.html` as the root composition (standalone, NOT template-wrapped):

> ⚠️ **只有根 `index.html` 是完整HTML文档 (`<!doctype html><html>...`)。** `dist/compositions/*.html` 里的子合成文件必须是HTML片段 — 以 `<div data-composition-id="...">` 为根,不能有 `<!doctype>`/`<html>`/`<head>`/`<body>` 标签。完整HTML文档格式会导致渲染器无法执行子合成内的GSAP脚本,场景内容全部空白(只剩背景纹理和空白面板)。pre-render 闸门 `scripts/check_composition_format.py` 会拦截此问题。

> 🚫 **每个场景 clip 必须用精确属性 `data-composition-src="compositions/scene-X.html"` 引用子合成。**
> HyperFrames 只认 `data-composition-src` 才会加载/编译外部场景文件。写成 `data-src` / `src` / 漏写,
> **所有场景都不会加载,渲染出来整片全白(只剩字幕条)**——这是最致命的失败之一。
> 同时:① 每个 clip 的 `data-composition-id` 必须与该场景内 `window.__timelines["<id>"]` 注册的 id **完全一致**;
> ② 不要把场景再套进一个额外的 `data-composition-id="mt-root"` 容器,按下面模板的结构直接平铺在根 div 内。
> pre-render 闸门 `scripts/check_root_compositions.py` 会拦截 `data-src`/孤立未引用/指向不存在文件 的情况。

```html
<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <!-- Self-hosted offline fonts (NO Google Fonts / CDN — the render sandbox is air-gapped). -->
  <!-- Copy skill assets into dist/ first: assets/fonts → dist/assets/fonts, assets/katex → dist/katex -->
  <style>
    @font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-Bold.woff2") format("woff2"); font-weight:400 700; font-display:swap; }
    @font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-ExtraBold.woff2") format("woff2"); font-weight:800; font-display:swap; }
    @font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-Black.woff2") format("woff2"); font-weight:900; font-display:swap; }
    @font-face { font-family:"Inter"; src:url("./assets/fonts/Inter-Variable.woff2") format("woff2"); font-weight:100 900; font-display:swap; }
    @font-face { font-family:"JetBrains Mono"; src:url("./assets/fonts/JetBrainsMono-Bold.woff2") format("woff2"); font-weight:700; font-display:swap; }
    html, body { font-family:"Noto Sans SC", Inter, sans-serif; }
  </style>
  <!-- Self-hosted GSAP (local, NOT a CDN — the render sandbox is air-gapped) -->
  <script src="./gsap/gsap.min.js"></script>
  <!-- Self-hosted KaTeX JS for caption formula rendering (local, NOT a CDN) -->
  <script src="./katex/katex.min.js"></script>
  <!-- KaTeX CSS MUST be inlined as <style>, NOT loaded via <link> -->
  <!-- The HyperFrames compiler strips non-@font-face CSS from <link> stylesheets -->
  <style id="katex-inline-css">
    /* Paste full contents of dist/katex/katex.min.css here */
    /* (with font URLs rewritten: url(fonts/ → url(./katex/fonts/ — local, offline) */
  </style>
</head>
<body>
  <div data-composition-id="math-tutorial"
       data-start="0"
       data-duration="[TOTAL_DURATION]"
       data-width="1920"
       data-height="1080">

    <!-- No theme selection needed — aurora mesh theme is the default -->
    <script>
      // Light-theme setup (no randomization needed)
    </script>

    <!-- Track 0: Narration audio -->
    <audio id="narration"
      data-start="0"
      data-duration="[TOTAL_DURATION]"
      data-track-index="0"
      src="narration.wav"
      data-volume="1">
    </audio>

    <!-- Track 1: Scene compositions (sequential, same track) -->
    <div id="scene-problem"
      data-composition-id="mt-problem"
      data-composition-src="compositions/scene-problem.html"
      data-start="0"
      data-duration="[SCENE_DURATION]"
      data-track-index="1"
      data-width="1920"
      data-height="1080">
    </div>

    <div id="scene-step-1"
      data-composition-id="mt-step-1"
      data-composition-src="compositions/scene-step-1.html"
      data-start="[TIMESTAMP]"
      data-duration="[SCENE_DURATION]"
      data-track-index="1"
      data-width="1920"
      data-height="1080">
    </div>

    <!-- Add more scenes as needed -->

    <div id="scene-conclusion"
      data-composition-id="mt-conclusion"
      data-composition-src="compositions/scene-conclusion.html"
      data-start="[TIMESTAMP]"
      data-duration="[SCENE_DURATION]"
      data-track-index="1"
      data-width="1920"
      data-height="1080">
    </div>

    <!-- Track 2: Inline captions with KaTeX formula rendering -->
    <!-- IMPORTANT: Use text from captions.json (original script text with TTS-measured timestamps). -->
    <!-- For math expressions in captions, wrap them in <span class="cm">LaTeX code</span>. -->
    <!-- The JS at the bottom renders these spans with KaTeX inline mode. -->
    <!-- Keep Chinese text as-is; only replace math expressions with KaTeX spans. -->
    <!-- Example (values from captions.json, with math formatted): -->
    <div id="cap-1" class="clip caption-bar"
      data-start="0.0" data-duration="3.86" data-track-index="2">
      今天我们来看一道关于二次方程的问题。</div>
    <div id="cap-2" class="clip caption-bar"
      data-start="5.2" data-duration="4.5" data-track-index="2">
      在地表，重力 <span class="cm">W_0 = \tfrac{GMm}{R_E^{\,2}}</span></div>
    <div id="cap-3" class="clip caption-bar"
      data-start="9.7" data-duration="3.0" data-track-index="2">
      因此 <span class="cm">h = R_E\!\left(\!\sqrt{\tfrac{3}{2}} - 1\right)</span></div>
    <!-- ... one <div> per captions.json entry, with math spans ... -->

    <style>
      .caption-bar {
        position:absolute; bottom:36px; left:50%; transform:translateX(-50%);
        z-index:2147483647; /* MANDATORY: caption is ALWAYS topmost — above every scene layer,
                               panel, and diagram. Scenes must use small z-index (<100); never
                               let a scene element sit above this or it will cover the subtitle. */
        font-family:"Noto Sans SC",sans-serif;
        font-size:36px; font-weight:600; line-height:1.35;
        color:#0f172a;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
        background:#ffffff;
        /* CRITICAL: `width:max-content` — with only `left:50%`+translateX and no width, an
           absolutely-positioned bar shrink-to-fits to the *available* half-frame (~960px),
           so even a short caption wraps early. `max-content` sizes it to the text on ONE line
           (independent of available space), then `max-width` caps it so it never bleeds
           off-frame; if content still exceeds 1600px it wraps balanced & centered. */
        width:max-content; max-width:1600px; box-sizing:border-box;
        border: 1px solid rgba(99,102,241,0.15);
        padding:10px 32px; border-radius:12px;
        box-shadow: 0 2px 8px rgba(99,102,241,0.06);
        text-align:center; white-space:normal; overflow-wrap:break-word; text-wrap:balance;
        pointer-events:none;
        display:flex; flex-wrap:wrap; align-items:center; justify-content:center; gap:4px 8px;
      }
      .caption-bar .katex, .caption-bar .katex * { color: #0f172a; }
      .caption-bar .katex { font-size: 34px; }
      .katex-mathml { display: none !important; }
    </style>

  </div>

  <script>
    // Render KaTeX formulas in caption spans
    document.querySelectorAll(".cm").forEach(function(el) {
      var tex = el.textContent;
      try {
        katex.render(tex, el, { displayMode: false, output: "html", throwOnError: false });
      } catch(e) {
        console.warn("KaTeX caption render error:", tex, e);
      }
    });

    window.__timelines = window.__timelines || {};
    var tl = gsap.timeline({ paused: true });
    window.__timelines["math-tutorial"] = tl;
  </script>
</body>
</html>
```

### Timing Rules

- Replace `[TOTAL_DURATION]` with last scene end + 1.0s buffer
- Replace `[TIMESTAMP]` and `[SCENE_DURATION]` with values from Step 4 storyboard
- Scenes on the same `data-track-index` must NOT overlap in time
- Captions on a separate track (index 2) span the entire duration
- Audio on track 0 spans the entire duration
- **Caption text source:** Each caption `<div>` must use `text` from `captions.json` (original script text with TTS-measured timestamps), with `data-start` and `data-duration` derived from its `start` and `end` fields (`data-duration = end - start`). Both `captions.json` and `transcript.json` contain the same original script text — no speech recognition artifacts.

### Caption position — ALWAYS bottom (字幕固定在视频下方)

Every caption `<div class="clip caption-bar">` is a **root-level element in `index.html`** (track 2) — NEVER place a caption inside a scene composition (inside a scene it inherits the scene's flex/stacking context and drifts to the top or middle, differing scene to scene). The `.caption-bar` rule MUST be `position:absolute; bottom:36px; left:50%; transform:translateX(-50%)` — **anchor with `bottom:` only, never `top:`** (a `top:` value pulls the bar to the top/middle). The offset parent is the 1920×1080 frame, so `bottom` pins the bar to the bottom band in every scene. Gate: `scripts/check_caption_position.py`.

### Caption length — keep each cue ONE line (字幕过长必须拆分，不要靠换行)

A long caption is the #1 cause of subtitles running off the frame edge. The fix is to **split a long sentence into several short sequential cues**, NOT to let one cue wrap into a big multi-line block (wrapping is only the CSS safety net, kept as a last resort).

Rule: **each caption cue ≤ ~22 Chinese characters** (roughly one line at 36px inside the 1600px bar; punctuation and a short formula count too). If a `captions.json` entry is longer, break it at a natural punctuation boundary (`，` `。` `；` `、` `：`) into 2–3 cues and **subdivide that entry's time window proportionally by character count**, so each sub-cue is a single short line shown in sequence:

```
# captions.json entry (too long, ~34 chars, start=12.0 end=20.0 → dur=8.0)
#   "平行于主轴的光线经过凸透镜折射后，一定会通过另一侧的焦点。"
# → split at "，" into two single-line cues, time split by char ratio (16:18 ≈ 3.8s : 4.2s)
<div class="clip caption-bar" data-start="12.0"  data-duration="3.8" data-track-index="2">
  平行于主轴的光线经过凸透镜折射后</div>
<div class="clip caption-bar" data-start="15.8"  data-duration="4.2" data-track-index="2">
  一定会通过另一侧的焦点。</div>
```

Guidance: prefer 2 balanced halves over one long + one tiny; never split inside a `<span class="cm">` formula (keep each formula whole in one cue); sub-cues stay on caption track (index 2) and must not overlap in time. Best of all, keep narration sentences short at Step 2 so most cues need no splitting. The pre-render gate `scripts/check_caption_overflow.py` flags `white-space:nowrap` / missing `max-width` and over-long cues.

### Caption Formula Formatting (字幕公式格式化)

**Captions must display proper math notation, not spoken-form Chinese.** The `captions.json` text is the TTS spoken form (e.g., "G M m除以R的平方"). When writing caption `<div>` elements, replace all spoken-form math expressions with `<span class="cm">LaTeX</span>` inline elements. Keep non-math Chinese text as-is.

**How it works:**
1. Each `<span class="cm">` element contains raw LaTeX code as its text content
2. The `<script>` block at the bottom of `index.html` iterates over all `.cm` spans and calls `katex.render()` with `displayMode: false` (inline mode)
3. Use `\tfrac{}{}` for fractions (compact text-style, fits single-line captions)
4. Use `\sqrt{}` for square roots, `^{2}` for exponents, `_{E}` for subscripts

**Common replacements:**

| Spoken form in captions.json | KaTeX span in caption div |
|------------------------------|---------------------------|
| G M m除以R的平方 | `<span class="cm">\tfrac{GMm}{R^2}</span>` |
| R加h的平方 | `<span class="cm">(R+h)^2</span>` |
| 三分之二 / 三分之二 | `<span class="cm">\tfrac{2}{3}</span>` |
| x的平方 | `<span class="cm">x^2</span>` |
| 根号x | `<span class="cm">\sqrt{x}</span>` |
| R等于6371千米 | `<span class="cm">R_E = 6371\,\text{km}</span>` |
| h约等于1430千米 | `<span class="cm">h \approx 1430\,\text{km}</span>` |
| 重力W等于... | 重力 `<span class="cm">W = ...</span>` |
| 41度49分 | `<span class="cm">41^\circ 49'</span>` |
| 30度 | `<span class="cm">30^\circ</span>` |
| 60度30分45秒 | `<span class="cm">60^\circ 30' 45''</span>` |
| sinC等于三分之二 | `<span class="cm">\sin C = \tfrac{2}{3}</span>` |

**KaTeX pitfalls — MUST AVOID:**

| Wrong | Correct | Why |
|-------|---------|-----|
| `49\'` | `49'` | `\'` is a text-mode accent command, NOT a math-mode prime/minute symbol. Use a plain ASCII single quote `'` for arcminutes (′). |
| `49\"` | `49''` | Same issue — use two plain ASCII single quotes for arcseconds (″). |
| `\arcsin\tfrac{2}{3}` | `\arcsin \tfrac{2}{3}` | Add a space after `\arcsin` for readability (both parse, but the space is safer). |
| `\\sin` (in HTML) | `\sin` | Do NOT double-escape backslashes in HTML text content. Only double-escape inside JS string literals or Python f-strings. The `<span class="cm">` text content must contain single backslashes as-is in the raw HTML. |

> **Key rule:** In KaTeX math mode, the ASCII single quote `'` renders as a prime symbol (′). Never use `\'`, `\prime` in caption spans — just write `'` directly. For degrees use `^\circ`, for arcminutes use `'`, for arcseconds use `''`.

**Example — original vs formatted caption:**

```
<!-- WRONG: spoken-form text (what captions.json contains) -->
<div class="clip caption-bar" ...>在地表，重力为G M m除以R的平方。</div>

<!-- CORRECT: math expressions replaced with KaTeX spans -->
<div class="clip caption-bar" ...>在地表，重力 <span class="cm">W_0 = \tfrac{GMm}{R_E^{\,2}}</span></div>
```

**Rules:**
- Pure Chinese text captions (no math) need no changes — use as-is from `captions.json`
- Mixed captions: keep Chinese text, wrap only the math parts in `<span class="cm">`
- Multiple formulas in one caption: use multiple `<span class="cm">` elements
- Use `\tfrac` (not `\frac` or `\dfrac`) for fractions — they must fit in a single-line caption bar
- Variable names should match what the scene panels show (e.g., `R_E` not just `R`)
- **Angle symbols:** degrees = `^\circ`, arcminutes = `'` (plain quote), arcseconds = `''`. **NEVER** use `\'` or `\"` — these are text-mode accent commands that cause KaTeX to display raw LaTeX as red error text
- **No double-escaping in HTML:** The `<span class="cm">` text content in the HTML file must contain literal single backslashes (e.g., `\sin`, `\tfrac`). Only double-escape when writing LaTeX inside JS string literals (`"\\sin"`) or Python string literals (`"\\sin"`). If using a Python build script with f-strings, write the caption HTML directly (not through f-string interpolation) to avoid escaping issues

### Transition Setup

Every sub-composition should include a **0.3s fade-in** at the start of its own GSAP timeline. This is done inside each `compositions/scene-*.html` file, not in the root `index.html`:

```js
// Inside each scene's <script> block, as the FIRST tween:
// Use autoAlpha (NOT CSS opacity:0) — if JS fails, content stays visible
tl.fromTo(".scene-content",
  { autoAlpha: 0 },
  { autoAlpha: 1, duration: 0.3, ease: "power2.out" }, 0);
```

This ensures every scene gracefully fades in rather than hard-cutting. The scene's panel entrance animation (e.g., `y: 40 → 0`) runs concurrently with the fade, creating a smooth combined transition. **Important: do NOT set `opacity: 0` on `.scene-content` in CSS — the `autoAlpha: 0` in GSAP's `fromTo()` handles the initial hidden state dynamically.**

**Do NOT** add scene-level transitions in `index.html` — each sub-composition owns its own entrance/exit animations via its internal GSAP timeline.

## Validation

Run these commands from inside `dist/`:

```bash
cd dist
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect
```

### MANDATORY pre-render gate — run `precheck.py` and fix until it passes

One command runs ALL render gates (no CJK inside KaTeX, LaTeX in JS strings double-escaped,
caption font-size ≤44px, `.scene-content` fills the frame, no CSS-hidden content, and scene
coverage = one composition per storyboard scene). **Run it from the project root
(the parent of `dist/`) and DO NOT render until it prints `ALL CHECKS PASSED`:**

```bash
EDU_SKILL_ROOT="<absolute directory containing qwen-mm-plugins-edu-agent/SKILL.md>"
python3 "$EDU_SKILL_ROOT/scripts/precheck.py" dist
```

**Self-correction loop (required):**
1. Run `precheck.py dist`.
2. If it exits non-zero, read each `FAIL` block — every line gives `file:line` and the exact fix:
   - **CJK in KaTeX** → move the Chinese out of KaTeX (`需要 <span data-tex="50"></span> 秒`, or use Latin `\text{s}`).
   - **single-backslash LaTeX in JS string** → double the backslash (`tex:"4 \\times 3"`); LaTeX in HTML `data-tex` stays single.
   - **caption font-size too large** → set it to 36–40px.
   - **`.scene-content` not centered / no height** → make it a centering box that fills the frame: `.scene-content{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}`. `position:absolute;inset:0` ALONE is not enough — without the flex-center trio a single panel piles at the top.
   - **CSS-hidden content** → remove `opacity:0` / `visibility:hidden` from CSS; hide via GSAP `autoAlpha:0` in `fromTo()` only.
   - **scene coverage** → you built fewer compositions than `STORYBOARD.md` plans (or a referenced scene is missing / has no timeline). Build one composition per planned scene, wire each into `index.html`, register `window.__timelines[...]`.
3. Apply every fix, then **re-run `precheck.py` and repeat until it prints `ALL CHECKS PASSED`**.
4. Only then run the renderer.

(Each check can still be run individually — `check_katex_cjk.py`, `check_katex_escaping.py`,
`check_caption_size.py`, `check_scene_layout.py`, `check_no_hidden_content.py`,
`check_svg_filter_bbox.py`, `check_scene_coverage.py` — but `precheck.py` runs all of them so none is missed.)

### Common Issues

| Issue | Fix |
|-------|-----|
| Missing `data-composition-id` | Add to root div |
| Overlapping clips on same track | Adjust `data-start` / `data-duration` |
| Unregistered timeline | Ensure `window.__timelines[id]` matches `data-composition-id` |
| Text overflow | Reduce font size or increase container padding |
| KaTeX not rendering | Verify local `./katex/katex.min.js` exists in `dist/` and loads — do NOT use a CDN |
| Chinese shows □ boxes (tofu) | Embed the self-hosted `@font-face` block and use `"Noto Sans SC", Inter, sans-serif`; confirm `dist/assets/fonts/` exists. Do NOT use Google Fonts / CDN |
| KaTeX equations appear as broken plain text | KaTeX CSS was loaded via `<link>` and stripped by compiler. Inline it as `<style>` instead (see step-5) |
| Caption shows "G M m除以R的平方" | Caption text not formatted. Replace spoken-form math with `<span class="cm">LaTeX</span>` |
| Caption formula shows as red raw LaTeX text | KaTeX parse error. Check for `\'` (should be `'`), `\"` (should be `''`), or double-escaped backslashes (`\\sin` should be `\sin` in HTML). See "KaTeX pitfalls" table above |
| **Formula shows only a horizontal dash (—), digits/letters invisible** | **Gradient text was applied to a KaTeX element.** `background-clip:text` + `-webkit-text-fill-color:transparent` makes the glyphs transparent, but the fraction bar (`.mfrac .frac-line`, a CSS border) survives → equation collapses to a stray dash. **Fix:** remove the gradient-text trio from any element containing a `.katex` formula and give it a solid `color` (e.g. `color:#059669; .katex,.katex *{color:#059669}`). Gradient text is for plain-text titles ONLY. |
| **Pattern/grid figure has wrong shape, a stray dangling line, or its stick count ≠ the stated number** | Figure was drawn with hand-typed `<line>` coordinates → wrong cell layout, duplicated or missing edges. **Fix:** regenerate it from a cell-list with deduped edges (see step-5 "Grid / lattice figures — GENERATE PROGRAMMATICALLY"); the drawn element count must equal the problem's stated number (4/10/18/…). Take the geometry from `ANALYSIS.md`/standard answer, not loose prose wording (e.g. draw the 1+2+…+n staircase, not an "L"). |
| **Chinese still shows □ tofu even though font files exist** | The `@font-face` `src:` lists many subset files (`...subset-100.woff2, ...subset-101.woff2, …`) — a CSS fallback list loads only the FIRST. **Fix:** use ONE full shipped file per weight (`NotoSansSC-Bold.woff2`) in a single `url(...)`; never subset. `ls dist/assets/fonts | grep -c subset` must be 0. |
| **A single unit/word is a □ box right after a formula number (e.g. "50□"), but plain Chinese elsewhere is fine** | A Chinese character was put INSIDE KaTeX, e.g. `data-tex="50\,\text{秒}"`. KaTeX math fonts have no CJK glyphs → □. **Fix:** move the Chinese out of KaTeX: `需要 <span data-tex="50"></span> 秒` (or use a Latin unit `\text{s}`). Catch every occurrence with the pre-render gate `check_katex_cjk.py` (see Validation above). |
| **Caption/subtitle is huge, wraps to 2 lines, dominates the frame** | Caption `font-size` is too large (e.g. `.caption-text{font-size:64px}`). On 1920×1080 captions belong at 36–40px. **Fix:** set caption `font-size:36-40px` (skill template = 36px). Catch it with the pre-render gate `check_caption_size.py` (see Validation above). |
| **Formula shows "imes" / "eq" / "rac" instead of × / ≠ / a fraction** | LaTeX was written in a JS string with a single backslash: `tex:"4 \times 3"`. JS eats `\t` as a tab, so KaTeX gets "4 imes 3". **Fix:** double-escape in JS strings: `tex:"4 \\times 3"` (or move LaTeX to an HTML `data-tex="4\times3"` where single backslash is fine). Catch it with the pre-render gate `check_katex_escaping.py` (see Validation above). |
| **Content piles at the top / a side panel is empty / a diagram is invisible** | The `.scene-content` wrapper is not vertically centering its content. Most common: it fills the frame (`position:absolute;inset:0`) but is **not a flex-center container**, so a single-panel child (problem card / step panel / 结论 panel — a normal-flow block with only `max-width`) collapses to its content height and sticks to the top; the bottom ~40-50% stays empty. (The other cause: the wrapper has no definite height at all, so an inner `height:100%` collapses.) **Fix:** make `.scene-content` a centering box that fills the frame — `.scene-content { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; padding:40px 60px 180px; box-sizing:border-box; }`. `position:absolute;inset:0` ALONE does NOT fix it — the flex-center trio is required (or give the content wrapper `height:100%` so it fills the frame itself, as split-layout diagram rows do). Catch it with the pre-render gate `check_scene_layout.py` (see Validation above). |
| **Force arrow / axis line is missing — only its letter (F/G/N/v) shows, no line or arrowhead** | A glow/blur `filter="url(#…)"` was applied to an **axis-aligned `<line>`** (horizontal velocity arrow, vertical gravity/normal arrow). A horizontal/vertical line has a zero-area bounding box, so the default `objectBoundingBox` filter region collapses to nothing and the line + `marker-end` render **completely invisible** (the `<text>` label has no filter, so it survives). **Fix:** remove `filter="url(#…)"` from the arrow (use a solid `stroke` 4–6 + marker), or make the filter absolute (`filterUnits="userSpaceOnUse" x="0" y="0" width="<vbW>" height="<vbH>"`). Diagonal rays are unaffected. Catch it with the pre-render gate `check_svg_filter_bbox.py` (see Validation above). |
| **Scene shows dots/axes/labels but the connecting curves or lines are MISSING (有点、没线)** | The curve's path `d` is generated at load by inline JS, but that JS never ran in the render — almost always because a hand-rolled renderer stripped `<script src="./gsap/gsap.min.js">` without re-injecting GSAP by absolute path, so `gsap` is `undefined`, `gsap.timeline()` throws, and `setup()` never builds the geometry → `<path>` stays `d="M0 0"`. Static dots/axes/labels still show, hiding the loss. **Fix:** render with `npx hyperframes render` (don't hand-roll a renderer); if you must, re-inject GSAP/KaTeX/fonts via absolute `file://` paths. Ensure any curve-geometry JS runs before/independent of `gsap.timeline()`. **Catch it with the POST-render gate `python3 "$EDU_SKILL_ROOT/scripts/postcheck.py" dist`** (`check_curves_rendered.py`) — see "Post-Render Line/Curve Render-Truth Gate". |

## Preview

```bash
npx hyperframes preview
```

Report the Studio URL to the user:
```
http://localhost:[PORT]/#project/[PROJECT_NAME]
```

## Render

Rendering to MP4 is mandatory — the pipeline is not complete until a video file exists. Run from inside `dist/`:

```bash
cd dist
npx hyperframes render --output output.mp4 --quality standard
```

For final delivery: `--quality high --fps 30`

Report the output file path and size to the user. The final video will be at `dist/output.mp4`.

## Post-Render Blank Frame Detection (渲染后空白帧检测)

**MANDATORY** — after rendering, extract frames from the video and verify no scene is blank. A blank frame (pure white or near-white) means a composition failed to render and must be fixed.

### Step 1: Extract one frame per scene

Extract a frame from the middle of each scene (not the start, which may be mid-fade-in):

```bash
# Extract one frame from the midpoint of each scene
# Replace timestamps with actual scene midpoints from STORYBOARD.md
ffmpeg -i output.mp4 -vf "select='eq(n\,FRAME_NUMBER)'" -vsync vfr -frames:v 1 /tmp/scene-check-%d.png
```

Or extract a frame every N seconds to cover all scenes:

```bash
# Extract one frame every 10 seconds throughout the video
ffmpeg -i output.mp4 -vf "fps=1/10" /tmp/frame-check-%03d.png 2>/dev/null
ls -la /tmp/frame-check-*.png
```

### Step 2: Check for blank frames

Blank frames are extremely small in file size (under 15KB for a 1920x1080 PNG) because they contain almost no visual information. Check:

```bash
# Find suspiciously small frames (likely blank)
find /tmp -name "frame-check-*.png" -size -15k -exec echo "BLANK FRAME DETECTED: {}" \;
```

Alternatively, use ImageMagick to check the standard deviation of pixel values (blank = near-zero deviation):

```bash
# Check each frame — std_dev < 5 means the frame is essentially blank
for f in /tmp/frame-check-*.png; do
  std=$(identify -verbose "$f" 2>/dev/null | grep "standard deviation" | head -1 | awk '{print $3}')
  if [ "$(echo "$std < 5" | bc -l 2>/dev/null)" = "1" ]; then
    echo "BLANK FRAME: $f (std_dev=$std)"
  fi
done
```

### Step 3: Fix or re-render

If any blank frames are detected:

1. Identify which scene is blank by matching the frame timestamp to `data-start` values in `index.html`
2. Open the corresponding composition HTML and check the browser console for JS errors
3. Common fixes:
   - KaTeX error → fix the LaTeX string, ensure `throwOnError: false`
   - GSAP selector miss → verify element IDs match between HTML and JS
   - Missing try-catch → wrap the script in the defensive pattern from step-5
4. Re-render and re-verify

**The video MUST pass blank frame detection before delivery.**

## Post-Render Visual Overlap Self-Check (渲染后重叠自查闭环) — MANDATORY

Blank-frame detection only catches *empty* scenes. It does NOT catch the most common "观感很差"
defects: **a `<text>` label clipped/covered by a box (取食→取, 捕食→捕), a connector line running into
a box, boxes not flush/aligned, a highlight ring bleeding onto an arrow.** These come from hand-placed
coordinates that *look* clear in the source viewBox but collide in the real render (scaling + CJK glyph
width + SVG paint order — a later `<rect>` paints over an earlier `<text>`). **You cannot verify this by
reading the code — you MUST look at the rendered pixels and iterate until they are clean.**

### Step 1 — the automated render-truth gate must pass
`precheck.py` includes `check_render_overlap.py`, which loads each scene in headless Chrome, settles the
timeline, and measures the REAL bounding boxes — it FAILS if any `<text>` overlaps a box it doesn't
belong to. It must print PASS. (If Chrome is unavailable it SKIPs — then Step 2 is your only safety net,
so do not skip Step 2.)

### Step 2 — LOOK at every scene and iterate (self-correction loop)
For **every scene** (especially any with node/flow boxes, connectors/arrows, labeled diagrams, charts):

1. Extract a settled frame from that scene (use its midpoint from `index.html` `data-start`+`data-duration`):
   ```bash
   ffmpeg -y -ss <scene_midpoint_seconds> -i output.mp4 -frames:v 1 /tmp/ov-<scene>.png -loglevel error
   ```
2. **Open the PNG with the Read tool and actually look at it.** Scan specifically for:
   - **文字被框压/裁切** — any label showing only part of a word (e.g. `取1` where `食` is hidden), any text sitting on top of / behind a box or another element;
   - **框和线重叠** — a connector line/arrow running into or overlapping a box instead of ending in the clean gap with clearance; a highlight ring/glow touching a neighbouring box or arrow;
   - **框对不齐** — sibling boxes whose edges are not flush (one bulges wider/taller — often a highlight `ring` drawn at `inset:-Npx` outside the box);
   - label-vs-label or label-vs-line collisions, off-frame content.
   - **方向 / 朝向 / 语义错误 (orientation & semantics — code gates can't judge "which way")** — the figure is drawn but pointing/facing the WRONG way or contradicting the physics/操作. Check every domain figure against the problem: **燃着/带火星木条伸入集气瓶** → the flame (burning end) must be DOWN INSIDE the jar, not above the mouth (木条画反); **斜面/incline** → slope rises toward the correct side, object/forces on the ramp surface; **箭头/矢量** (力/电流/速度/光线) → points in the physically correct direction; **仪器插入** (导管/温度计/漏斗/木条) → inserted end goes into the vessel through the opening, correct end down; **倾倒** → mouth points down into the target; **电池极性 / 电流回路方向**; a chart/curve actually shows the stated trend/phase. If the picture would confuse or mislead a student, it's wrong even if nothing "overlaps".
   - **动效与物理不符 (motion mismatched to the physics)** — **该动的过程没动**: a process verb (伸入/插入/放入/滴入/倒入/通入/加热) is drawn already in its end state and only a secondary effect fades — the action never happens on screen (e.g. 木条一开始就在瓶里、只是火焰淡出，而不是**木条下降伸入**再熄灭). **该原地生成的却在动/散落/飞入**: an adhesion/surface-precipitate/in-place change (附着/镀/表面沉淀/变色) is shown as loose particles floating in the solution or flying/staggering in from elsewhere instead of sitting ON the target surface and appearing in place (e.g. 红铜散在液体里像扩散，而不是**贴着铝丝**原地析出). Fix by animating the real motion, or by placing the product on the surface and revealing it in place. (see step-5 "Animation semantics: what MOVES vs what forms IN PLACE")
3. **If you see ANY overlap/misalignment, FIX THE COORDINATES and re-render:**
   - move the connector/edge label into the true centre of the gap with real clearance, or raise its `y`
     above the box band, so its whole bbox is clear of every box it isn't the caption of;
   - shorten the arrow / add clearance so the line ends before the box edge;
   - draw highlight rings *inside* the box (`inset:` positive) or add spacing so the ring+glow doesn't
     reach a neighbour; make all sibling boxes the same size and flush;
   - then `npx hyperframes render` again, re-extract the frame, and **look again**.
4. **Repeat 1–3 until the frame is visually clean.** Do not deliver a scene with a visible overlap. Do
   not claim "visually verified" without having actually extracted and read the frames.

> Rule of thumb: if you hand-typed absolute coordinates for boxes/arrows/labels, assume they collide
> until a rendered frame proves otherwise. `check_render_overlap.py` PASS **and** your own eyes on the
> frame are both required.

## Post-Render Line/Curve Render-Truth Gate (线/曲线漏画检测) — MANDATORY

Blank-frame detection catches *empty* scenes; the overlap gate catches text/box collisions. **Neither
catches a scene that renders ALMOST completely but silently drops a line or curve** — e.g. an energy
graph that shows its dots, axes and labels but NONE of the connecting curves ("有点、没线"). This is the
single most deceptive render bug and it passes every pre-render gate, because **the composition is
correct** — the loss happens at RENDER time.

**Root cause seen in the wild:** a hand-rolled renderer (custom CDP/puppeteer script) that copies each
composition into its own harness page and **strips the `<script src="./gsap/gsap.min.js">` tag without
re-injecting GSAP via an absolute `file://` path** (it correctly rewrites `bg-texture.jpg` to an
absolute path but forgets GSAP). In the render page `gsap` is then `undefined`, so `gsap.timeline()`
throws *before* the composition's inline `setup()` builds the curve geometry — every `<path>` keeps its
placeholder `d="M0 0"` and paints nothing, while the static dots/axes/labels still show.

### The gate
`scripts/check_curves_rendered.py` (run via `scripts/postcheck.py`) is renderer-agnostic. For each
scene it renders a KNOWN-GOOD reference in headless Chrome (GSAP + the self-hosted fonts injected via
absolute `file://`, timeline settled at 0.85·dur), records every solid content line/curve's color and
pixel-space sample points, then extracts the matching frame from `output.mp4` at the same local time and
verifies those pixels are actually painted. It FAILs a scene when a static line/curve that the
reference draws is absent from the video **while other lines in the same scene ARE present** — the
present lines prove the frame is aligned, so an absent curve is a real "线画不出来" (no false positives on
a correct render: validated PASS on a good render, FAIL on the "有点、没线" render). Moving arrows and
thin/decorative-dashed guides are deliberately not asserted (they can't be pixel-matched reliably).

```bash
# after `npx hyperframes render` produced dist/output.mp4:
EDU_SKILL_ROOT="<absolute directory containing qwen-mm-plugins-edu-agent/SKILL.md>"
python3 "$EDU_SKILL_ROOT/scripts/postcheck.py" dist
```

Loop: render → `postcheck.py dist` → if it FAILs, fix the renderer/composition → re-render → repeat
until it prints `ALL POST-RENDER CHECKS PASSED`. A missing `dist/` or output MP4 is a failure. If Chrome,
Node, ffmpeg, or GSAP is unavailable, `postcheck.py` reports `POSTCHECK INCOMPLETE` and exits non-zero;
the corresponding visual property was not verified. You can also point the curve check at a specific file:
`python3 "$EDU_SKILL_ROOT/scripts/check_curves_rendered.py" dist path/to/video.mp4`.

### Prevention — do NOT hand-roll a renderer that strips GSAP
**Render with `npx hyperframes render` (above).** Do not write a bespoke CDP/puppeteer renderer. If you
absolutely must drive Chrome yourself, then whatever you strip you MUST re-inject with a working
absolute path — GSAP (`<script src="file://<abs>/gsap/gsap.min.js">`), KaTeX, and the `@font-face`
fonts — exactly as you already do for `bg-texture.jpg`. A relative `./gsap/gsap.min.js` in a `/tmp`
harness resolves to nothing; dropping it silently kills every timeline and all JS-generated geometry.

## Gate

Final checklist:
- [ ] `npx hyperframes lint` — zero errors
- [ ] `npx hyperframes validate` — zero errors
- [ ] **Root references every scene via `data-composition-src`** — each scene clip uses the exact attribute `data-composition-src="compositions/scene-X.html"` (NOT `data-src`/`src`), `data-composition-id` matches each scene's `window.__timelines[id]`; otherwise scenes don't load → all-white video. Verified by `scripts/check_root_compositions.py`
- [ ] `npx hyperframes inspect` — no unexpected overflow
- [ ] **Render-truth overlap gate** — `check_render_overlap.py` (in `precheck.py`) PASSES: no `<text>` painted under/over a box it doesn't belong to (文字被框覆盖/压框)
- [ ] **Visual overlap self-check done** — for every scene with boxes/connectors/labels/charts you extracted a settled frame, opened it with Read, and confirmed by eye: no clipped/covered text, no line-into-box, no misaligned/bulging boxes; any defect was fixed by editing coordinates and re-rendering until the frame is clean
- [ ] Audio plays in sync with scene transitions
- [ ] Captions align with narration
- [ ] KaTeX equations render at all timeline positions
- [ ] **KaTeX CSS inlined** — `<style id="katex-inline-css">` present in index.html and all compositions (NOT `<link>`)
- [ ] **GSAP loaded offline** — `<script src="./gsap/gsap.min.js"></script>` in index.html (NOT a CDN URL)
- [ ] **No CDN/external URLs** — zero `cdn.jsdelivr.net`, `cdnjs.cloudflare.com`, `unpkg.com`, or any other external `<script src>` / `<link href>` in index.html or any composition
- [ ] **Caption formulas formatted** — all math expressions in captions use `<span class="cm">LaTeX</span>`, no spoken-form Chinese math text remaining
- [ ] **No CSS opacity:0 on content elements** — all content elements default to visible in CSS; GSAP handles hiding via `autoAlpha: 0` in `fromTo()`
- [ ] **No glow/blur filter on axis-aligned lines** — zero `filter="url(#…)"` on any horizontal/vertical `<line>` (force arrow, axis, ray, wire). A degenerate bbox collapses the filter region → the line + arrowhead vanish, leaving only the letter label. Use a solid stroke, or an absolute `filterUnits="userSpaceOnUse"` filter. Verified by `scripts/check_svg_filter_bbox.py`
- [ ] **All GSAP code wrapped in try-catch** — timeline construction is inside `try {}` block in every composition
- [ ] **Each KaTeX render call has individual try-catch** — one bad formula cannot crash the entire scene
- [ ] **No gradient text on formulas** — zero `background-clip:text` / `-webkit-text-fill-color:transparent` on any element that holds a `.katex` formula (it makes glyphs vanish, leaving only the fraction bar as a stray dash). Formula elements use a solid `color`
- [ ] **Pattern/grid figures match their stated counts** — every matchstick/grid figure's drawn element count equals the number the problem states (4/10/18/…), every unit cell is closed (no stray dangling line), and the geometry follows `ANALYSIS.md`/standard answer
- [ ] **Chinese font not subsetted** — `ls dist/assets/fonts | grep -c subset` is 0; each "Noto Sans SC" `@font-face` has exactly one `url(...)`
- [ ] **`precheck.py dist` prints `ALL CHECKS PASSED`** — one command runs all four render gates and they all pass: no CJK inside KaTeX (no `\text{秒}`), LaTeX in JS strings double-escaped (`"4 \\times 3"`, no "imes"/"eq"/"rac"), caption font-size 36–40px (≤44px), and every `.scene-content` is a centering box that fills the frame (`display:flex;align-items:center;justify-content:center` — no content piled at the top / blank side panels)
- [ ] **Blank frame detection passed** — extracted frames from rendered video verified non-blank (no scene is pure white). See "Post-Render Blank Frame Detection" above
- [ ] **Line/curve render-truth passed (线/曲线没漏画)** — `python3 "$EDU_SKILL_ROOT/scripts/postcheck.py" dist` prints `ALL POST-RENDER CHECKS PASSED`: every solid line/curve the scene should draw is actually painted in `output.mp4` (catches the "有点、没线" bug where JS-generated path `d` never drew because the renderer didn't load GSAP). See "Post-Render Line/Curve Render-Truth Gate" above
- [ ] **Video rendered to MP4** — `npx hyperframes render` completed successfully
- [ ] Output `.mp4` file path and size reported to user
