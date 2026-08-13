# Step 5: Build Components

Build each scene composition as a HyperFrames sub-composition. Read the `hyperframes` skill for all composition authoring rules. Read the `gsap` skill for animation patterns. Read [math-components.md](math-components.md) for component templates.

> ⚠️ **Formula color rule (avoids a common, silent failure):** Any element that holds a KaTeX-rendered formula (`katex.render(...)` target, or a `.cm` span) MUST use a **solid `color`** — never the gradient-text trick (`background:linear-gradient(...)` + `-webkit-background-clip:text` + `-webkit-text-fill-color:transparent`). On a KaTeX formula the gradient-text trick turns every glyph transparent while the fraction bar (a CSS border) stays, so a fraction like `\dfrac{n(n+1)(2n+1)}{6}` renders as a lone horizontal dash. Gradient text is fine on **plain-text** titles/taglines only. Recommended: `.your-eq{ color:#059669 } .your-eq .katex,.your-eq .katex *{ color:#059669 }`.

> 🔤 **Multiple-choice options (选择题) must show the OPTION CONTENT, not just the letters.** If the problem has choices, the problem scene MUST render each option as **letter + full content** (`A 1/2`, `B 1/3`, `C 1/4`, `D 1/5`) — never bare `A B C D` badges with nothing beside them. Two ways this breaks: (1) the author writes only the letters and drops the text; (2) the option content is put in a `data-tex`/`.cm` span that never renders and shows blank — most often the missing-root-`id` bug (a KaTeX loop scoped to `#<composition-id>` with no matching root `id`, so `querySelectorAll` matches nothing → every option value is empty). Guard both: put the real content next to every letter, render option formulas the same robust way as other formulas (class `.cm` / `getElementById` / an `id`-bearing root), and after building, **confirm each option visibly shows its value** (gate: `check_composition_root_id.py` catches the blank-render case).

## Prerequisites

Scaffold the project:

```bash
npx hyperframes init dist --non-interactive --example blank
```

> `--example blank` is REQUIRED for non-interactive init (hyperframes ≥0.7.77 rejects a bare `--non-interactive` with "requires --example, --video, or --audio").

**The project directory MUST be named `dist`.** The platform evaluates `dist/index.html`.

Copy `narration.wav` and `transcript.json` into `dist/`. All subsequent file operations (creating compositions, building index.html) happen inside `dist/`.

**Copy the self-hosted offline fonts and KaTeX shipped with this skill into `dist/` (REQUIRED — without this, Chinese and equations render as tofu boxes □ in the air-gapped sandbox):**

```bash
EDU_SKILL_ROOT="<absolute directory containing qwen-mm-plugins-edu-agent/SKILL.md>"
mkdir -p dist/assets/fonts dist/katex dist/gsap

# EDU_SKILL_ROOT is the absolute directory containing this skill's SKILL.md.
SKILL_ASSETS="$EDU_SKILL_ROOT/assets"
if [ ! -f "$SKILL_ASSETS/fonts/NotoSansSC-Bold.woff2" ]; then
  echo "ERROR: Skill assets not found under EDU_SKILL_ROOT: $SKILL_ASSETS"
  exit 1
fi

echo "Using assets from: $SKILL_ASSETS"
cp -r "$SKILL_ASSETS/fonts/."  dist/assets/fonts/
cp -r "$SKILL_ASSETS/gsap/."   dist/gsap/

# KaTeX: try skill assets first, fallback to GitHub release download
if [ -f "$SKILL_ASSETS/katex/katex.min.js" ]; then
  cp -r "$SKILL_ASSETS/katex/."  dist/katex/
else
  echo "KaTeX not found in skill assets, downloading from GitHub..."
  KATEX_VERSION="0.16.11"
  curl -SL "https://github.com/KaTeX/KaTeX/releases/download/v${KATEX_VERSION}/katex.tar.gz" | tar xz -C dist/
  echo "KaTeX ${KATEX_VERSION} downloaded"
fi

# GSAP: verify, fallback to npm download
if [ ! -f "dist/gsap/gsap.min.js" ]; then
  echo "GSAP not found in skill assets, downloading from npm..."
  npm pack gsap --pack-destination /tmp && tar xzf /tmp/gsap-*.tgz -C /tmp
  cp /tmp/package/dist/gsap.min.js dist/gsap/gsap.min.js
  rm -rf /tmp/package /tmp/gsap-*.tgz
  echo "GSAP downloaded"
fi
```

**Mirror assets into `dist/compositions/` (MANDATORY — sub-compositions resolve `./` paths relative to their own directory, NOT `dist/`):**

Sub-composition HTML files live in `dist/compositions/`. When they reference `<script src="./gsap/gsap.min.js">` or `url(./katex/fonts/...)`, the browser resolves these relative to `dist/compositions/`, NOT `dist/`. Without mirroring, GSAP fails to load → all GSAP animations silently break → elements set to `autoAlpha:0` in `fromTo()` stay invisible → **blank scenes with only the background visible**. The same applies to KaTeX JS (formulas don't render) and fonts (Chinese becomes tofu).

```bash
# Mirror assets so ./gsap/, ./katex/, ./assets/ resolve from dist/compositions/
cp -r dist/gsap dist/compositions/gsap
cp -r dist/katex dist/compositions/katex
cp -r dist/assets dist/compositions/assets
```

**Verify the mirror:**

```bash
test -f "dist/compositions/gsap/gsap.min.js" || { echo "FATAL: compositions/gsap mirror missing"; exit 1; }
test -f "dist/compositions/katex/katex.min.js" || { echo "FATAL: compositions/katex mirror missing"; exit 1; }
test -f "dist/compositions/assets/fonts/NotoSansSC-Bold.woff2" || { echo "FATAL: compositions/assets/fonts mirror missing"; exit 1; }
echo "Asset mirror verified"
```

After this, `dist/assets/fonts/*.woff2`, `dist/katex/katex.min.css`, `dist/katex/katex.min.js`, `dist/katex/fonts/`, and `dist/gsap/gsap.min.js` must all exist — **both in `dist/` AND in `dist/compositions/`**. Everything is referenced by relative path — no network is used at render time. **Never use a CDN `<script>` tag for GSAP** — the AP render sandbox is air-gapped.

**Font file verification (MUST pass before writing any composition):**

```bash
# All 5 font files must exist and be >10KB
for f in NotoSansSC-Bold.woff2 NotoSansSC-ExtraBold.woff2 NotoSansSC-Black.woff2 Inter-Variable.woff2 JetBrainsMono-Bold.woff2; do
  test -s "dist/assets/fonts/$f" || { echo "MISSING: dist/assets/fonts/$f"; exit 1; }
done
echo "All fonts verified"
```

If any font file is missing, the skill assets were not copied correctly. **Do NOT download fonts from Google Fonts or any CDN** — the shipped woff2 files are complete single-file fonts (not split subsets). Google Fonts splits Noto Sans SC into ~120 numbered subset files with discontinuous numbering; downloading them and re-numbering causes 404s and tofu boxes. Always use the 5 pre-built woff2 files from this skill's `assets/fonts/` directory.

> 🚫 **NEVER subset the Chinese font, and NEVER put more than one font file in a single `@font-face src` list.** Use exactly one full file per weight, e.g.:
> ```css
> @font-face { font-family:"Noto Sans SC"; font-weight:400 900;
>   src:url("./assets/fonts/NotoSansSC-Bold.woff2") format("woff2"); font-display:swap; }
> ```
> A comma-separated `src:` list (`url(...subset-100.woff2), url(...subset-101.woff2), …`) is a CSS *fallback* list — the browser loads **only the first file**, so every glyph outside that one subset renders as a □ tofu box. This is exactly what breaks Chinese in the air-gapped sandbox. If you ever do have per-subset files, each subset MUST be its own `@font-face` with its own `unicode-range` — but the shipped single-file fonts make that unnecessary, so just use them.
>
> **Self-check after copying fonts:** `ls dist/assets/fonts/ | grep -c subset` must be `0`, and each `@font-face` for "Noto Sans SC" must reference exactly one `url(...)`. If either fails, you subsetted by mistake — revert to the shipped single-file woff2.

## Background Setup

Copy the texture background image from the skill's assets into the project:

```bash
EDU_SKILL_ROOT="<absolute directory containing qwen-mm-plugins-edu-agent/SKILL.md>"
cp "$EDU_SKILL_ROOT/assets/backgrounds/bg-texture.jpg" dist/bg-texture.jpg
```

Every scene composition references this image as `../bg-texture.jpg` (relative to `dist/compositions/`). The image is rendered as a blurred full-bleed background layer beneath the aurora orbs. See design-system.md "Background Treatment" for the full layer stack, `.bg-texture` CSS, and per-scene aurora palette guide.

### Background Theme Application

If the storyboard specifies a non-default theme (from the Background Theme Catalog in design-system.md), apply the theme's CSS in **every composition** by replacing the `.bg-texture` and `.a1`/`.a2`/`.a3` CSS rules with the theme-specific versions. The HTML structure stays the same:

```html
<!-- Same structure for ALL themes — only the CSS changes -->
<div class="scene-bg">
  <div class="bg-texture"></div>
  <div class="aurora-orb a1"></div>
  <div class="aurora-orb a2"></div>
  <div class="aurora-orb a3"></div>
</div>
```

**For the default `aurora-scholar` theme:** use the standard `.bg-texture { background: url('../bg-texture.jpg') ... }` CSS from design-system.md — no changes needed.

**For alternative themes (`chinese-elegant`, `lavender-soft`, `mint-fresh`, `warm-art`):**

1. Replace the `.bg-texture` CSS rule with the theme's gradient-based version (from design-system.md). These themes do NOT use `bg-texture.jpg` — the gradient replaces the image.
2. Replace the `.a1`, `.a2`, `.a3` CSS rules with the theme's aurora orb colors.
3. Optionally apply the theme's accent tint overrides for `.glass-panel` and `.step-badge` if the storyboard calls for it.
4. Set the composition root `background` to the theme's fallback color:
   - `aurora-scholar`: `#f8fafc`
   - `chinese-elegant`: `#e8f4f8`
   - `lavender-soft`: `#faf8ff`
   - `mint-fresh`: `#f0fdf9`
   - `warm-art`: `#fffbf0`
5. Use the theme's scene-specific aurora palette from design-system.md to vary orb colors per scene type.

**What stays the same across ALL themes:** white opaque panels (`background: #ffffff`), dark text (`color: #0f172a`), KaTeX colors, the mandatory global color reset block, all panel/component CSS, and the GSAP ambient effects (aurora drift + panel shadow breathing).

## Composition File Format (CRITICAL — 子合成文件格式)

**Sub-composition files in `dist/compositions/*.html` must be HTML fragments, NOT full HTML documents.** This is the #1 cause of blank-panel videos: content shows only background texture + empty white panels with no text, formulas, or geometry visible, while audio and captions play normally.

HyperFrames loads sub-compositions by injecting their content into the parent document. A full HTML document wrapper (`<!doctype html>`, `<html>`, `<head>`, `<body>`) prevents the renderer from properly executing GSAP scripts inside the sub-composition. All content elements remain at their initial hidden state (`autoAlpha:0`) → blank white panels.

**Only the root `index.html` is a full HTML document.** Every composition in `compositions/` is a fragment.

### CORRECT format (HTML fragment):

```html
<div data-composition-id="mt-problem" data-width="1920" data-height="1080">
  <div class="scene-bg">
    <div class="bg-texture"></div>
    <div class="aurora-orb a1"></div>
    <div class="aurora-orb a2"></div>
    <div class="aurora-orb a3"></div>
  </div>

  <div class="scene-content">
    <!-- scene content here — laid out in the top ~900px; bottom 180px is the caption safe zone -->
  </div>

  <style>
    /* scene CSS */
  </style>

  <script src="./gsap/gsap.min.js"></script>
  <script>
    window.__timelines = window.__timelines || {};
    var tl = gsap.timeline({ paused: true });
    // ... animations ...
    window.__timelines["mt-problem"] = tl;
  </script>
</div>
```

### Bottom caption safe zone (底部字幕安全区 — MANDATORY)

The caption bar lives in the bottom ~180px of the frame. **Scene content must stay in the
top ~900px so the subtitle never covers it.** Every `.scene-content` wrapper MUST reserve
that band with a bottom inset:

```css
.scene-content {
  position: relative; z-index: 1;
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  padding: 40px 60px 180px;   /* ← bottom 180px = caption safe zone (REQUIRED) */
  box-sizing: border-box;
}
```

- Keep `height: 100%` (vertical centering) — the `box-sizing: border-box` + `padding-bottom:180px`
  simply floats the flex-centered content up, so it ends around y≈900px, clear of the caption.
- The full-bleed `.scene-bg` layer still fills the whole 1080px — only `.scene-content` is inset.
- Do NOT push panels/diagrams below ~900px to "use more space"; that is what makes the
  subtitle overlap content. `check_caption_safe_zone.py` fails the render if the band is not reserved.
- This is why captions are also kept small (38px) and ≤2 lines — see design-system.md *Caption Style*.

### WRONG format (full HTML document — causes blank panels):

```html
<!doctype html>
<html lang="zh">
<head>
<meta charset="UTF-8" />
</head>
<body>
<div data-composition-id="mt-problem" data-width="1920" data-height="1080">
  <!-- ... -->
</div>
</body>
</html>
```

Enforced by `scripts/check_composition_format.py` in `precheck.py`.

## KaTeX vs Plain Text Decision Guide (简单符号用HTML，复杂公式用KaTeX)

**Before using `katex.render()`, ask: does this expression need math layout (fractions, roots, matrices)?** If not, use plain HTML entities or Chinese text instead. KaTeX in JS strings requires double-escaped backslashes — a single-backslash error is **silent** and produces garbled text (e.g., `\leq` → `leq`, `\angle` → `angle`, `\circ` → `circ`).

### When to use plain HTML (no KaTeX needed)

```html
<!-- Simple comparisons — HTML entities -->
<span class="formula">OP' ≤ 1</span>           <!-- ≤ is &le; -->
<span class="formula">x ≥ 5</span>              <!-- ≥ is &ge; -->
<span class="formula">a ≠ b</span>              <!-- ≠ is &ne; -->

<!-- Angle/degree expressions — Chinese + HTML entities -->
<span class="formula">角MPN ≤ 90°</span>        <!-- 角 for ∠, ° is &deg; -->
<span class="formula">角A = 60°</span>

<!-- Multiplication/operators -->
<span class="formula">3 × 4 = 12</span>          <!-- × is &times; -->

<!-- Subscripts — HTML tags -->
<span>F<sub>1</sub> + F<sub>2</sub></span>
```

### When to use KaTeX (layout features needed)

```js
// Fractions — need KaTeX layout
katex.render("\\frac{1}{2}", el, { output: "html" });

// Complex formulas — need KaTeX layout
katex.render("\\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}", el, { output: "html" });

// Square roots — need KaTeX layout
katex.render("\\sqrt{a^2 + b^2}", el, { output: "html" });
```

### Safe HTML entity reference

| Symbol | Entity | Character | Use for |
|---|---|---|---|
| ≤ | `&le;` | ≤ | less than or equal |
| ≥ | `&ge;` | ≥ | greater than or equal |
| ≠ | `&ne;` | ≠ | not equal |
| ° | `&deg;` | ° | degree |
| × | `&times;` | × | multiplication |
| ÷ | `&divide;` | ÷ | division |
| ± | `&plusmn;` | ± | plus-minus |
| ² | `&sup2;` | ² | squared |
| ³ | `&sup3;` | ³ | cubed |

> 🚨 **平方根禁止用裸 `√` 字符（会显示成缺上横线的逗号状）。** The bare Unicode radical `√` (U+221A)
> has **no vinculum/overbar** in Noto Sans SC / Inter, so `√x` renders as a comma-like tick next to `x`
> (looks broken). **ALWAYS render roots with KaTeX**: `katex.render("\\sqrt{x}", el)` → proper radical
> with the horizontal bar over the radicand. Same for `\\sqrt[3]{x}` (cube root), `\\sqrt{a^2+b^2}`.
> This applies everywhere the symbol is user-visible — formulas, function lists, axis/label text.
> (Bare `√` is already banned by SKILL rule 12's specialized-symbol list; this is the concrete symptom.)

### Greek letters (希腊字母)

Greek letters are safe as **Unicode characters** in HTML — Inter-Variable.woff2 contains all Greek glyphs (Noto Sans SC does NOT, so the font stack falls back to Inter for Greek).

> 🚨 **SVG `<text>` with Chinese MUST use a CJK font stack — never `Inter`/`sans-serif` alone.**
> The sandbox ships only ONE CJK face: `Noto Sans SC`. Inter, JetBrains Mono, serif and the bare
> `sans-serif` fallback have NO Chinese glyphs, so a label like
> `<text font-family="Inter, sans-serif">v = 常量</text>` draws the Latin part but renders 常量 as
> **"NO GLYPH" / 豆腐块 (.notdef boxes)**. Unlike HTML, SVG `<text>` does NOT inherit the CJK-first
> body stack — it uses whatever `font-family` you give it. Rules:
> - Any `<text>`/`<tspan>` (or inline-styled element) whose text contains **any** Chinese char →
>   `font-family="Noto Sans SC, Inter, sans-serif"` (Noto Sans SC FIRST).
> - Pure-Latin labels (`v`, `F`, `N`, digits, units, Greek) may use `Inter` — that is fine.
> - **Best practice: don't mix scripts in one `<text>`.** Put "v = " (Inter) and "常量" (Noto Sans SC)
>   in separate `<tspan>`/`<text>` elements, each with the right font. Gate: `scripts/check_cjk_font.py`.

**NEVER write the English word** — always use the Unicode character:

```html
<!-- WRONG — renders as the English word "alpha" -->
<span style="font-style:italic">alpha</span>

<!-- CORRECT — renders as the Greek letter α -->
<span style="font-style:italic">α</span>
```

| Character | Unicode | Use for |
|---|---|---|
| α | U+03B1 | alpha — angles, coefficients |
| β | U+03B2 | beta — angles, coefficients |
| γ | U+03B3 | gamma |
| δ | U+03B4 | delta |
| θ | U+03B8 | theta — angles |
| π | U+03C0 | pi — circle constant |
| φ | U+03C6 | phi — golden ratio, angles |

For geometric symbols in non-formula context, use Chinese: "角" (∠), "三角形" (△), "垂直于" (⊥), "平行于" (∥).

## KaTeX Integration

**CRITICAL: KaTeX CSS must be inlined, not loaded via `<link>`.** The HyperFrames compiler processes CDN `<link rel="stylesheet">` tags by extracting ONLY `@font-face` rules and discarding all other CSS. This means KaTeX's layout CSS (fractions, subscripts, spacing) is silently stripped, causing equations to render as broken plain text (e.g., "W0 = RE2GMm" instead of proper fractions).

### Step 1: Provide KaTeX CSS (offline — from shipped assets)

The KaTeX assets were copied into `dist/katex/` in the Prerequisites step (no network). If you skipped it, copy them now:

```bash
EDU_SKILL_ROOT="<absolute directory containing qwen-mm-plugins-edu-agent/SKILL.md>"
mkdir -p dist/katex && cp -r "$EDU_SKILL_ROOT/assets/katex/." dist/katex/
```

### Step 2: Inline KaTeX CSS into every composition

For each composition that renders equations, add the KaTeX CSS as an inline `<style>` tag (NOT a `<link>`). Rewrite font URLs to point to the local `./katex/fonts/` path:

```python
# Run once to inline KaTeX CSS into all composition files
import re
from pathlib import Path

katex_css = Path("dist/katex/katex.min.css").read_text()
# Rewrite relative font URLs to the LOCAL self-hosted KaTeX fonts (offline — no CDN)
katex_css = katex_css.replace(
    "url(fonts/",
    "url(./katex/fonts/"
)

for html_file in Path("dist/compositions").glob("*.html"):
    content = html_file.read_text()
    # Replace <link> tag with inline <style>
    content = re.sub(
        r'<link[^>]*katex[^>]*\.css[^>]*/?>',
        f'<style id="katex-inline-css">\n{katex_css}\n</style>',
        content
    )
    html_file.write_text(content)
```

Alternatively, when writing each composition manually, include:

```html
<!-- DO NOT use <link> for KaTeX CSS — it gets stripped by the compiler -->
<style id="katex-inline-css">
  /* Paste full contents of dist/katex/katex.min.css here, with font URLs rewritten to url(./katex/fonts/ (local, offline) */
</style>
<script src="./katex/katex.min.js"></script>
```

### Step 3: Render equations

Render equations synchronously with `output: "html"` (critical for deterministic capture):

```js
katex.render("x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}", element, { displayMode: true, output: "html" });
```

> **CRITICAL PITFALL — `\dfrac` in JS strings (最常见的公式渲染故障)**
>
> In a JavaScript string, a single backslash starts an escape sequence. `\d` is not a recognized escape, so JS **silently discards the backslash** and passes `d` to KaTeX. The result: `\dfrac{1}{2}` becomes `dfrac{1}{2}` → rendered as italic text "dfrac12" instead of a fraction ½. **This is the #1 cause of broken math rendering.**
>
> ```js
> // WRONG — \d becomes d, KaTeX receives "dfrac{1}{4}" and renders "dfrac14"
> katex.render("\dfrac{1}{4}", el, { displayMode: false, output: "html" });
>
> // RIGHT — \\d is interpreted as literal \d, KaTeX receives "\dfrac{1}{4}"
> katex.render("\\dfrac{1}{4}", el, { displayMode: false, output: "html" });
> ```
>
> Other common victims: `\frac` (`\f` = form-feed → `rac`), `\times` (`\t` = tab → `imes`), `\neq` (`\n` = newline → `eq`). **Every `\` in a JS string must be `\\`.** This only applies to JS strings — HTML `data-tex="\dfrac{1}{2}"` is correct with single `\`.
>
> **After building all compositions**, run `python3 "$EDU_SKILL_ROOT/scripts/check_katex_escaping.py" dist` and fix every reported line before proceeding.

KaTeX renders synchronously — no async wait needed. Place the render call before timeline construction. Always use `output: "html"` to avoid MathML fallback text appearing as duplicated content.

## Chinese Font Loading (MANDATORY — 中文字体必须离线内嵌)

**The render sandbox is air-gapped and has no CJK system font.** Do NOT use a Google Fonts / CDN `<link>` (it fails to load → all Chinese renders as garbled boxes 乱码), and do NOT rely on the compiler's built-in embedding or system fonts (PingFang SC). Instead, embed the self-hosted fonts shipped with this skill (copied into `dist/assets/fonts/` in Prerequisites) via an inline `@font-face` `<style>` block.

Put this block in the root `index.html` `<head>` — it applies document-wide to every composition:

```html
<style>
  @font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-Bold.woff2") format("woff2"); font-weight:400 700; font-display:swap; }
  @font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-ExtraBold.woff2") format("woff2"); font-weight:800; font-display:swap; }
  @font-face { font-family:"Noto Sans SC"; src:url("./assets/fonts/NotoSansSC-Black.woff2") format("woff2"); font-weight:900; font-display:swap; }
  @font-face { font-family:"Inter"; src:url("./assets/fonts/Inter-Variable.woff2") format("woff2"); font-weight:100 900; font-display:swap; }
  @font-face { font-family:"JetBrains Mono"; src:url("./assets/fonts/JetBrainsMono-Bold.woff2") format("woff2"); font-weight:700; font-display:swap; }
  html, body { font-family:"Noto Sans SC", Inter, sans-serif; }
</style>
```

Then in every composition declare a **CJK-first** stack (never `Inter, sans-serif` alone, never `PingFang SC`):

```css
font-family: "Noto Sans SC", Inter, sans-serif;
```

## SVG Diagram Authoring Rules

When building scenes that use SVG diagrams (Components 8, 9, 10, 11, or any custom SVG-based scene):

### Vessels & tubes (容器与导管) — a tube enters through the OPENING, never pierces the glass

> 🧪 **A pipe/导管/thermometer/funnel-stem that goes into a flask, bottle, test-tube, beaker or gas-jar MUST pass in through the vessel's MOUTH (the top opening) — it may NEVER cross a side wall or the bottom, and must never poke out through the glass.** Real bug (锥形瓶 + CO₂ 导管): the vessel mouth was at the top (`y=120`, between neck walls `x∈[210,310]`), but the delivery tube was drawn `M 60 200 L 250 200 L 250 470` — its horizontal run at `y=200` starts far left at `x=60` and stabs straight **through the left neck wall** (`x=210`), so the tube appears to come out of / go through the side of the bottle ("管子从瓶子里伸出来了"). 

Rules to guarantee a correct insertion:

1. **Draw the vessel first and know its opening.** Note the mouth's x-span `[xL,xR]` and its top y (`yMouth`), plus where the walls and bottom are.
2. **Keep the tube's OUTSIDE part fully outside the outline, then enter only through the opening.** The external (horizontal) segment must sit **above** the mouth (`y < yMouth`); bend down at an x **inside** the opening (`xL < xBend < xR`); the descending segment passes through the mouth gap — it must **not** share an x with either neck wall and must **not** intersect any glass stroke.
3. **Tip depth by purpose:** gas bubbled *into* liquid (e.g. CO₂ into 石灰水, 洗气long-in) → tip **below** the liquid surface; gas/vapour collected or tested *above* liquid (向上排空气, 检验) → tip **above** the surface. Follow the problem.
4. **Never:** a tube crossing/overlapping a wall stroke; exiting the side or bottom; floating disconnected above the mouth; or a tip resting on/through the vessel floor.

```html
<!-- viewBox 0 0 520 600.  Flask mouth = top opening at y=120, between neck walls x=210..310; liquid surface y≈400; body bottom ≈520. -->
<!-- ✗ WRONG: horizontal at y=200 from x=60 crosses the neck wall at x=210 (pierces the glass) -->
<!--   <path d="M 60 200 L 250 200 L 250 470" .../> -->
<!-- ✓ RIGHT: inlet ABOVE the mouth (y=70<120); bend at x=260 (inside 210..310); descend through the opening to a tip below the liquid surface -->
<path d="M 60 70 L 260 70 L 260 460" fill="none" stroke="#64748b" stroke-width="7"
      stroke-linecap="round" stroke-linejoin="round"/>
<!-- (260 is between the neck walls, 70 is above the rim → the tube enters cleanly through the mouth, never touching the glass) -->
```

Prefer the pre-built vessels in `assets/components/` (`chemistry/flask`, `chemistry/test-tube`, `chemistry/gas-bottle`, `fluid/beaker`) and add the tube relative to their known mouth coordinates.

### Pouring one vessel into another (倾倒) — the lip touches the rim, and a real stream flows down

> 🫗 **When one vessel pours into another (倒水、沿杯壁倾倒二氧化碳、把 A 瓶倒入 B 杯), the pouring vessel's LIP must sit right at the receiving container's rim, and a visible STREAM must connect lip → contents. Do NOT leave the tilted vessel floating in space with only a thin dashed arc pointing at the target.** Real bug (沿杯壁缓慢倾倒 CO₂): the CO₂ jar was `rotate(-42 470 250)` centred at x≈470 while the beaker's left wall was at x=640 — a ~120 px gap — and the "pour" was a thin dashed curve `M520,250 C…660,360` ending in mid-air inside the beaker. It reads as "a jar floating nearby with an arrow", not pouring.

Rules for a correct pour:

1. **Lip AT the rim (no gap).** Position the pouring vessel so its lower pour-lip is directly above/touching the receiving container's rim corner (for 沿杯壁 / "down the wall", put the lip just over the *near inner wall*). The horizontal gap between lip and rim should be ~0.
2. **Tilt about the lip.** Rotate the vessel (~110°–140°, mouth pointing down toward the target) with the **transform-origin AT the pour-lip point**, so as it tilts the lip stays parked over the rim (not swinging away). GSAP: set `transform-box:fill-box` and rotate the `<g>` about the lip.
3. **Draw a real stream, not a dashed arrow.** The stream is a **solid, slightly-tapering flow** from the lip to the contents: a filled `<path>` or a thick semi-transparent line in the liquid/gas colour (water → blue solid; gas like CO₂ → a translucent falling band or a few descending particle dots). Never a thin `stroke-dasharray` line (that looks like a motion/trajectory arrow). For 沿杯壁, route the stream **down along the inner wall** to the surface/bottom, not diagonally through open space.
4. **The receiving container responds.** Its liquid level **rises** during the pour (animate the liquid rect/path height); for a dense gas (CO₂) it **fills from the bottom up** — animate a bottom-anchored fill rect growing upward, and trigger effects bottom-first (e.g. lower candle goes out before the higher one).
5. **Never:** a big gap between vessels bridged only by a dashed arc; the mouth pointing up/away from the target; the stream ending in mid-air; the vessel overlapping/piercing the receiving container's walls (see 容器与导管 rule).

```html
<!-- Beaker: inner walls x=640 & x=940, rim y=210, bottom y=470. Pour CO₂ down the LEFT inner wall. -->
<!-- ✗ WRONG: jar centred at x≈470 (120px gap) + thin dashed arc to mid-air -->
<!--   <g transform="rotate(-42 470 250)">…</g>
       <path d="M520,250 C560,300 600,330 660,360" stroke-dasharray="16 16" stroke-width="9"/> -->
<!-- ✓ RIGHT: lip parked over the left rim corner (~648,205); tilt about the lip; solid translucent stream down the wall -->
<g id="pour-jar" transform="rotate(125 648 205)">   <!-- mouth points down-right into the beaker -->
  <rect x="600" y="120" width="96" height="150" rx="8" fill="rgba(99,102,241,0.14)" stroke="#6366f1" stroke-width="3"/>
  <text x="648" y="205" text-anchor="middle" font-size="24" font-weight="800" fill="#1e3a8a">CO2</text>
</g>
<!-- stream: solid, semi-transparent, hugs the inner wall (x≈655) from lip down to the rising CO₂ layer -->
<path id="pour-stream" d="M650,210 C650,300 652,380 652,455" fill="none"
      stroke="rgba(99,102,241,0.5)" stroke-width="14" stroke-linecap="round"/>
<!-- CO₂ fills the beaker bottom-up (animate height 0 → full), lower candle extinguishes first -->
<rect id="co2-layer" x="642" y="468" width="296" height="0" fill="rgba(99,102,241,0.30)"/>
```

Reveal the stream with `stroke-dashoffset` draw-on (a *solid* stroke, dashoffset for the draw-on only) and grow `#co2-layer` upward; keep the lip glued to the rim for the whole tilt.

### Burning splint / glowing splint inserted into a vessel (燃着/带火星木条 伸入 集气瓶/试管) — the FLAME (burning end) goes DOWN INTO the vessel

> 🔥 **When "将燃着的木条伸入集气瓶/试管" (or 带火星的木条检验 O₂), the BURNING END — the flame — is lowered DOWN INTO the vessel to meet the gas; the plain (held) end sticks OUT the top.** The classic reversal: the model uses the everyday "lit stick = flame on top" schema and puts the flame at the TOP end, above the jar mouth, with the plain wood dipping in — so the flame is OUTSIDE the gas and "木条熄灭 / 带火星木条复燃" can't physically happen. Real bug: splint `<line x1=280 y1=170 x2=280 y2=330>` (top y=170 above the jar mouth y=200) with the flame group `translate(280,150)` → flame floats **above** the mouth, outside the jar.

Rules for a correct burning-splint-into-vessel:

1. **Flame at the INSERTED end, inside the vessel.** The vessel is mouth-up (opening at the top, e.g. glass body `y=200..436`). The splint runs vertically; its **burning/flame end is the LOWER end, INSIDE the vessel** (e.g. flame base at `y≈330`, well below the mouth `y≈200` and above the gas layer / bottom). The **held (plain wood) end sticks up OUT of the mouth** (e.g. top at `y≈120`, above `y=200`).
2. **Flame still points up** (flames always rise: the teardrop tip is above its base), but the **whole flame must be BELOW the mouth line (inside the jar)** — `flame_y > mouth_y`. Do NOT put the flame above the opening.
3. **Wood colour on the stick, flame only at the in-jar end.** The brown splint `<line>`/`<rect>` spans held-end→flame; put the flame `<g>` at the lower (in-jar) end, not the top.
4. **The effect happens inside:** 木条熄灭 (CO₂/N₂ 等) → shrink/fade the flame that is *inside* the jar; 带火星木条复燃 (O₂) → the glow bursts into flame *inside* the jar. If the flame is outside, none of this reads.
5. **Never:** flame above the jar mouth; plain (non-burning) end inserted while the flame is held outside; flame not overlapping the vessel interior.

```html
<!-- Jar mouth-up: glass body y=200..436, mouth at y≈200. -->
<!-- ✗ WRONG: flame at top (y≈150, above mouth), plain end dips in -->
<!--   <line x1=280 y1=170 x2=280 y2=330 stroke="#b45309"/>  <g transform="translate(280,150)">…flame…</g> -->
<!-- ✓ RIGHT: held end up OUT of the mouth (y≈120), burning end + flame DOWN inside the jar (y≈330) -->
<line id="splint" x1="280" y1="120" x2="280" y2="330" stroke="#b45309" stroke-width="8" stroke-linecap="round"/>
<g transform="translate(280,330)">           <!-- flame base INSIDE the jar (330 > mouth 200) -->
  <path d="M0,6 C-18,-8 -14,-40 0,-60 C14,-40 18,-8 0,6 Z" fill="url(#flameGrad)"/>  <!-- tip up, whole flame below mouth -->
</g>
```

Gate: `scripts/check_splint_orientation.py` (FAILs when a 木条+伸入 scene has its flame at/above the vessel mouth).

### Animation semantics: what MOVES vs what forms IN PLACE (动效要匹配物理：过程要"动"，附着/沉淀要"原地生成")

The single biggest动效 failure is **mismatching motion to the physics**: animating a thing that should stay put (so it looks like it *flies/scatters*), or NOT animating a process that is inherently a motion (so the "过程" never happens on screen). Decide per object from the **verb / phenomenon**, not from a generic entrance template.

**A. Process verbs → you MUST animate the process (物体真的移动/进入/变化，而不是"一开始就在终态 + 淡入").**
Verbs like **伸入 / 插入 / 放入 / 浸入 / 滴入 / 倒入 / 通入 / 加入 / 移近 / 加热(升温)** describe an ACTION over time. The actor must visibly TRAVEL / ENTER / CHANGE:
- 燃着木条**伸入**集气瓶 → the splint **descends from above the mouth down into the jar** (`attr:{transform}` / y tween over ~1s), THEN the flame reacts (熄灭/复燃) *inside*. Do NOT draw it already inside and merely fade the flame. (Real bug: splint sat static in the jar, only the flame faded — the "伸入" never happened.)
- 滴入/倒入液体 → a drop/stream **falls in**, then the liquid level rises / colour changes.
- 通入气体 → bubbles **travel up** through the liquid.
- Choreograph: enter (move) → react (the phenomenon) → settle. The motion is the point of a "过程" scene.

**B. Adhesion / surface-precipitate / in-place state change → draw it ON the surface and reveal it IN PLACE (原地淡入/生长)，绝不位移、绝不散落、绝不从别处飞入/弹入.**
Phenomena like **附着 / 镀(析出金属镀层) / (表面)沉淀 / 变色 / 生成(附在某物上)** happen AT a fixed location on a specific object. The product MUST:
- be **positioned ON that object's surface** — its coordinates hug the object's outline (within a few px of its stroke), as a cluster/coating **on** it, NOT scattered out in the surrounding liquid/space;
- be revealed **in place** by `autoAlpha`/`scale` **with `transform-box:fill-box; transform-origin:center`** (so it grows where it is), or by a growing-thickness coating — **never** a `translate`, a fly-in, a stagger-from-elsewhere, or particles drifting in the solution. Motion here reads as "扩散/飞走", the opposite of 附着.
- Real bug (铝丝放入硫酸铜→铝丝上**附着**红色铜): the copper was drawn as **loose red dots floating in the solution beside the wire** and popped in with a scale/stagger effect → looked like particles dispersing, not copper plating the wire. Correct: red copper dots/coating placed **right on the aluminium wire's outline**, revealed by in-place fade/grow (no translate); optionally the solution's blue **fades lighter in place**.

**Rule of thumb:** ask "在真实实验里，这个东西是**移动**发生的，还是**在某个表面/位置原地出现/变化**的？" 移动类→动它(enter→react→settle)；原地类→贴着目标表面、原地淡入/生长，坐标就画在该表面上。After rendering, **watch the frame**: a process scene must show the actor moving in; an adhesion scene must show the product sitting ON the surface (not floating/flown). (step-6 视觉自查闭环会抓"该动没动 / 该贴的飞走了"。)

### Grid / lattice figures (matchsticks, square arrays, dot patterns) — GENERATE PROGRAMMATICALLY (do NOT hand-type coordinates)

Figures made of repeated unit cells (火柴棒拼正方形、方格阵列、点阵找规律) are the #1 source of wrong diagrams when coordinates are typed by hand: cells get placed in the wrong shape, shared edges get duplicated, and individual edges get forgotten (leaving a stray dangling line). **Never hand-write each `<line>`.** Instead:

1. **Express the figure as a list of unit cells** `[[col,row], ...]` using the geometry from `ANALYSIS.md` (NOT a loose word in the problem text — see the conflict rule below). For "第 n 个由 1+2+…+n 个正方形组成的阶梯三角形", figure 3 is the 6 cells `[[0,0],[1,0],[2,0],[0,1],[1,1],[0,2]]` (a staircase of rows 3,2,1), **not** an L.
2. **Generate the matchsticks by deduping shared edges in a loop** — this makes the stick count automatically correct:

```html
<svg viewBox="0 0 320 320" class="pattern-svg"><g id="fig3"></g></svg>
<script>
(function(){
  try {
    var cells = [[0,0],[1,0],[2,0],[0,1],[1,1],[0,2]]; // from ANALYSIS.md geometry
    var U = 70, OX = 20, OY = 20;            // unit size + origin
    var edges = new Map();                    // key -> count; dedup shared edges
    function add(x1,y1,x2,y2){ var k=[x1,y1,x2,y2].join(','); edges.set(k,(edges.get(k)||0)+1); }
    cells.forEach(function(c){
      var x=c[0], y=c[1];
      add(x,y,   x+1,y  ); // top
      add(x+1,y, x+1,y+1); // right
      add(x,y+1, x+1,y+1); // bottom
      add(x,y,   x,  y+1); // left
    });
    var g = document.getElementById('fig3'), n = 0;
    edges.forEach(function(_,k){
      var p=k.split(',').map(Number), ln=document.createElementNS('http://www.w3.org/2000/svg','line');
      ln.setAttribute('x1',OX+p[0]*U); ln.setAttribute('y1',OY+p[1]*U);
      ln.setAttribute('x2',OX+p[2]*U); ln.setAttribute('y2',OY+p[3]*U);
      ln.setAttribute('class','stick'); g.appendChild(ln); n++;
    });
    // SELF-CHECK: deduped stick count MUST equal the number stated in the problem.
    var EXPECTED = 18;                         // the "18 根" stated for 第3个
    if (n !== EXPECTED) console.error('MATCHSTICK COUNT MISMATCH: drew '+n+', expected '+EXPECTED);
  } catch(e) { console.error('grid figure error', e); }
})();
</script>
```

   `edges` is keyed by the edge endpoints, so a shared edge between two adjacent cells is stored once → the number of `<line>`s equals the true matchstick count. Every cell automatically gets all 4 of its edges, so there are **no missing edges and no stray dangling lines**.
3. **MANDATORY self-check:** the deduped stick/element count for each figure MUST equal the number the problem states for that figure (e.g. 4, 10, 18). If they differ, the cell list (the shape) is wrong — fix the cell list, do not nudge coordinates.
4. **Conflict rule (geometry source of truth):** when the problem's prose wording conflicts with `ANALYSIS.md` / the standard answer (e.g. prose says "更大的 L 形" but the standard answer says "1+2+…+n 个正方形的阶梯三角形"), **draw the geometry from the standard answer / `ANALYSIS.md`**, because that is what makes the stated counts (4,10,18,…) and the final formula consistent. A figure that does not produce the stated count is wrong by definition.

### Scalability
- Always use `viewBox` for scalable SVG (never fixed `width`/`height` in px on the `<svg>` element)
- Set the SVG container to fill its parent: `width: 100%; height: 100%;`
- **NEVER size a content SVG as `width:100%; height:auto` (SVG高度必须有界 — 否则场景突然变大).** With `height:auto` the rendered height follows the viewBox aspect ratio, so at full panel width a near-square viewBox (e.g. `0 0 1000 760`) becomes ~1050px tall and overflows the ~860px usable height — the scene "suddenly gets big" and is clipped. Instead **bound the height** one of three ways: (a) `width:100%; height:100%` inside a container whose height is fixed/stretched (e.g. `.geo-canvas{flex:2}` in a `display:flex;align-items:stretch` row — the canonical geometry-canvas pattern); (b) add an explicit `max-height` in px (e.g. `#mt-g-svg{width:100%; max-height:760px}`) plus `preserveAspectRatio="xMidYMid meet"` so it letterboxes; (c) pick a landscape viewBox (ratio height/width ≲ 0.5) so `width:100%` keeps the height small. Gate: `scripts/check_svg_height_bound.py`.
- Common viewBox sizes: `0 0 1700 580` for wide stages, `0 0 600 600` for square diagrams

### Reusable Filters
Define glow filters in `<defs>` and reference them with `filter="url(#filterName)"`:

```html
<defs>
  <filter id="rayGlow"><feGaussianBlur stdDeviation="3" /></filter>
  <filter id="bigGlow"><feGaussianBlur stdDeviation="6" /></filter>
  <filter id="subtleGlow"><feGaussianBlur stdDeviation="2" /></filter>
</defs>
```

> 🚨 **NEVER put a glow/blur filter directly on an axis-aligned `<line>` (force arrow, axis, horizontal/vertical ray, wire, tick).** A perfectly horizontal or vertical line has a **degenerate bounding box** (zero height or zero width). SVG filters default to `filterUnits="objectBoundingBox"` with a region of `-10%…120%` of that bbox, so a zero dimension makes the filter region **zero-area → the line AND its `marker-end` arrowhead render nothing at all**, while the `<text>` label (no filter) still shows. Symptom: **受力示意图里"只有力的字，没有力的线条"** — the force letter appears but the arrow is invisible. This bites ONLY axis-aligned strokes — a slanted ray has a nonzero-area bbox and survives, so the bug hides until you draw a vertical gravity/normal arrow or horizontal velocity arrow.
>
> **Force arrows / axis lines — do this instead:**
> - **BEST:** give the arrow a solid `stroke` (width 4–6) + `marker-end` and **no filter**. A force arrow reads perfectly without a glow.
> - If you truly want a glow on straight strokes, make the filter absolute so it ignores the bbox: `<filter id="fGlow" filterUnits="userSpaceOnUse" x="0" y="0" width="<viewBoxW>" height="<viewBoxH>">…</filter>`.
> - Glow filters (`objectBoundingBox` default) are safe on **circles, particles, ions, text, and 2-D shapes** (non-degenerate bbox) — that is what the minimum-size rules below refer to.
>
> The pre-render gate `scripts/check_svg_filter_bbox.py` fails the build if any axis-aligned `<line>` carries a bbox-relative filter.

> 🚨 **Arrowheads must be a FIXED size, POINT THE RIGHT WAY, and force lines must be drawn at FULL length (箭头太大 / 方向画错 / 线没画出来).** Three very common, severe SVG-arrow bugs:
> - **Giant arrowhead (箭头太大):** a `<marker>` with **no `markerUnits`** defaults to `markerUnits="strokeWidth"`, so the head is *multiplied by the line's stroke-width*. With a thick force stroke (6–8) a `markerWidth="12"` head becomes ~72–96px — a huge triangle. **Fix:** always `<marker markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="…" refY="…" orient="auto">` and size the head in absolute px.
> - **🧭 Arrowhead drawn the WRONG direction (箭头方向画错 — 该向下的箭头，头部却是水平的):** with `orient="auto"` (the normal case), SVG rotates the marker so its **local `+x` axis (向右) follows the line's travel direction**. So the arrowhead triangle **MUST be drawn pointing RIGHT (`+x`)** — e.g. `points="0,0 0,16 14,8"` (apex on the right, `refX≈14 refY≈8`). If you instead draw it pointing **down (`+y`)** like `points="0,0 16,0 8,14"` (apex at the bottom, thinking of the final on-screen look), `orient="auto"` adds the line's rotation *on top*, so on a straight-down line the head comes out **sideways/horizontal**. Golden rule: **draw every `orient="auto"` head pointing `+x`; let `orient` do the rotating.** (If you truly want a non-rotating fixed arrow, keep the `+y` geometry but set a *numeric* `orient` such as `orient="90"`, never `"auto"`.)
> - **Sideways / missing arrow (方向不对 + 线没画出来):** authors draw a `<line>` collapsed to a point (`x1==x2 && y1==y2`) and grow it with GSAP `attr:{y2}`. A zero-length line has **no shaft**, and `orient="auto"` on it is undefined → the arrowhead points sideways; if the `attr` tween doesn't seek at render the shaft never shows. **Fix:** draw the line at its **full, correct length** (so `orient` is right and the shaft always exists) and reveal it with `stroke-dashoffset` draw-on — never animate a marker line's length from zero.
> - **BEST:** reuse the prebuilt CSS `force-arrow` component (`assets/components/mechanics/force-arrow.html`) — fixed-size head, rotate via `transform` for direction, scale via `--arrow-length`. No marker/stroke-width pitfalls.
>
> The pre-render gate `scripts/check_svg_arrow.py` fails the build on: a marker without `userSpaceOnUse`; an `orient="auto"` arrowhead whose triangle points `+y`/`−x` instead of `+x` (wrong-direction head); or a zero-length line carrying a marker.

> 🛖 **Inclined-plane force diagrams (斜面受力图) — draw the wedge right-side-up.** A ramp/wedge is a solid triangle **sitting on the ground: horizontal base at the BOTTOM (largest SVG y), peak at the TOP**. Do NOT draw it flat-side-up with the point at the bottom (that's an inverted funnel — "斜面画反了"). The object rests on the upper face; the **normal force N is perpendicular to the slope and points up-and-OUT (an upward component; never downward)**; gravity G points straight down; friction f (rough only) lies along the surface opposing motion. Full coordinates, the outward-normal formula, and a self-check are in **[geometry-construction-guide.md](geometry-construction-guide.md) → Pattern 8: Inclined Plane / Wedge**.

### Minimum Sizes (critical for 1080p readability)
- Primary shape stroke-width: **3px** minimum
- Secondary/auxiliary stroke-width: **2px** minimum
- Circle/particle radius: **14px** minimum (with glow filter applied)
- SVG text font-size: **20px** minimum, use `font-family: "Noto Sans SC"` for Chinese labels
- No element smaller than **30px** in either dimension without a glow halo

### Light Ray / Trajectory Drawing Animation (光线/轨迹绘制动画 — 禁止整条淡入)

When a scene contains SVG light rays, projectile trajectories, or any path that represents motion through space, **each segment MUST be animated as a progressive drawing** — never a whole-line fade-in (`autoAlpha: 0 → 1`). A fade-in makes the ray appear static and hides the physical direction of travel.

**Required pattern — GSAP `attr` on `<line>` endpoints:**

```js
/* Incident ray: extend from source to lens */
tl.fromTo("#ray-inc",
  { attr: { x2: /*startX*/ 60,  y2: /*startY*/ 140 } },
  { attr: { x2: /*endX*/  350, y2: /*endY*/  140 }, duration: 1.2, ease: "power2.inOut" }, 1.0);

/* Refracted ray: extend from lens to exit (starts after incident finishes) */
tl.fromTo("#ray-ref",
  { attr: { x2: /*lensX*/ 350, y2: /*lensY*/ 140 } },
  { attr: { x2: /*exitX*/ 620, y2: /*exitY*/ 295 }, duration: 1.2, ease: "power2.inOut" }, 2.3);
```

**Rules:**
1. Each ray segment (incident + refracted) animates **sequentially** — incident first, then refracted — so the viewer sees light travel from source → lens → exit.
2. The `fromTo` start values collapse the line to zero length at its origin point (`x2=x1, y2=y1`), then extend it to the target endpoint.
3. Duration per segment: **0.8–1.5s** (fast enough to feel dynamic, slow enough to follow).
4. This applies to **every scene containing light rays** — including overview/principle scenes that show multiple rays. Each ray still draws sequentially (ray 1 incident → ray 1 refracted → ray 2 incident → ray 2 refracted → …), not all at once.
5. For `<path>` elements (curved rays, arcs), use `stroke-dasharray` + `stroke-dashoffset` drawing instead:
   ```js
   var len = el.getTotalLength();
   el.setAttribute("stroke-dasharray", len);
   el.setAttribute("stroke-dashoffset", len);
   tl.to(el, { attr: {"stroke-dashoffset": 0}, duration: 1.2, ease: "power2.inOut" }, startTime);
   ```
6. **Do NOT add a glow/blur `filter` to a horizontal or vertical draw-on `<line>`** (e.g. a horizontal velocity/light ray, or a vertical force arrow). Its start state `x2=x1,y2=y1` is a zero-area point and its end state is axis-aligned, so a bbox-relative filter deletes the whole line + arrowhead (see the 🚨 note under "Reusable Filters"). Use a solid stroke, or an absolute `filterUnits="userSpaceOnUse"` filter.

### Smooth curves (顺滑曲线) — never a handful of straight chords

> 🌊 **Any continuous curve MUST render as a smooth curve, not a `<polyline>` of a few straight segments (不要用分段直线逼近曲线).** This covers function graphs (抛物线/双曲线/正弦/指数衰减 `y=x²`, `1/x`, `sin`, `e^{-x}`), and any "用曲线呈现" trend such as population/oscillation dynamics (种群数量波动、阻尼振荡、生态平衡恢复). Real bug: a damped population oscillation drawn as `<polyline points="120,380 236.7,380 353.3,308 470,212 …">` with ~13 vertices — each ~117 px apart — so the "curve" is a visible jagged zig-zag of straight chords (`stroke-linejoin="round"` only rounds the corners, the segments stay straight).

Do ONE of these (prefer the first):

1. **Emit a smooth `<path>` with cubic Béziers** through your data points using a Catmull-Rom→Bézier helper. Sparse control points are fine because the curve is interpolated smoothly:
   ```js
   // points = [[x0,y0],[x1,y1],…]  ->  smooth SVG path "d" (Catmull-Rom, tension 0.5)
   function smoothPath(pts){
     if (pts.length < 3) return "M" + pts.map(p=>p.join(",")).join(" L ");
     var d = "M" + pts[0][0] + "," + pts[0][1];
     for (var i=0; i<pts.length-1; i++){
       var p0 = pts[i-1] || pts[i], p1 = pts[i], p2 = pts[i+1], p3 = pts[i+2] || p2;
       var c1x = p1[0] + (p2[0]-p0[0])/6, c1y = p1[1] + (p2[1]-p0[1])/6;
       var c2x = p2[0] - (p3[0]-p1[0])/6, c2y = p2[1] - (p3[1]-p1[1])/6;
       d += " C" + c1x.toFixed(1)+","+c1y.toFixed(1)+" "+c2x.toFixed(1)+","+c2y.toFixed(1)+" "+p2[0]+","+p2[1];
     }
     return d;
   }
   document.getElementById("mt-cc-fish").setAttribute("d", smoothPath(fishPts));  // on a <path fill="none" stroke=…>
   ```
   Use a `<path fill="none" stroke="…">` (not `<polyline>`), then draw it on with `stroke-dashoffset` exactly as in rule 5 above — `getTotalLength()` works on paths.
2. **Or sample the function densely** — if you must use a `<polyline>`/point list, compute the actual function at **many** points (roughly **1 point per ≤10 px of width**, i.e. ~120+ points across a 1400 px axis), not 10–15. At that density straight segments are visually indistinguishable from a curve.

**Exception — keep straight segments only when the graph is genuinely piecewise-linear:** `y=|x|`, 分段函数, 折线统计图 (line charts of discrete data), distance–time graphs made of constant-velocity legs. Those are *supposed* to have corners; do not "smooth" them. Everything that is mathematically a smooth/continuous curve gets rule 1 or 2.

### Movable Objects
- Wrap each movable object in a `<g>` group with `transform="translate(x,y)"`
- Animate via GSAP: `tl.to("#wire-group", { attr: { transform: "translate(850,200)" }, ... })`
- Give each group a unique `id` for GSAP targeting (e.g., `id="wire-group"`, `id="bottle-hcl"`)
- **⚠️ NEVER tween a bare transform shorthand (`x`/`y`/`rotation`/`scale`) on a group that has a `transform="translate(...) rotate(...)"` attribute — the object will FLY OFF-SCREEN (物体飞出画面).** GSAP parses the existing `translate(390,364)` into its model, then `fromTo("#blk",{y:10},{y:0})` overwrites translateY from 364 → 0, so the object jumps ~364px off its spot. This is the #1 "物体飞出去" bug.
  - **Reveal a positioned object** → animate ONLY `autoAlpha`/`opacity`: `tl.fromTo("#blk",{autoAlpha:0},{autoAlpha:1,duration:0.5})` (never add `y:`/`x:`/`scale:` here).
  - **Also fade+slide it in** → NEST: static outer `<g transform="translate(390,364) rotate(-30)">` for position, inner `<g>` for the motion: `tl.fromTo("#blk-inner",{autoAlpha:0,y:10},{autoAlpha:1,y:0})`.
  - **Actually move it** → use the FULL transform via `attr` (as above): `tl.to("#blk",{attr:{transform:"translate(390,300) rotate(-30)"}})` — never a bare `x`/`y`.
  - **Never** target positioned groups with a broad selector like `"g[transform]"` or a bare `"g"`/`"rect"` — it will hit and clobber every positioned group. Gate: `scripts/check_svg_transform_anim.py`.
- **⚠️ 缩放/旋转 SVG 元素必须用 `svgOrigin`，禁用 px 的 `transformOrigin`(否则元素飞出/错位).** 想让一个 SVG 元素（如"变阻器随风速变短"的 `<g id="r1">`）就地缩放/旋转时，**不要**写 `tl.to("#r1",{scale:0.72, transformOrigin:"470px 270px"})` —— 在 SVG 上 `transformOrigin` 按元素**包围盒本地坐标**换算，对一个子元素坐标远离 SVG 原点的组缩放会附带一个很大的平移，把整个元件甩到画面外（真实事故：R₁ 缩短动画把变阻器甩飞、电路显示崩坏；即使该 `<g>` 没有 transform 属性、纯靠子坐标定位也会飞）。**正确做法**：用 GSAP 专给 SVG 的 **`svgOrigin:"x y"`**（用户坐标系，如 `svgOrigin:"470 270"`）；或把该元素套进 `<g transform="translate(cx,cy)">`、内部元素改用**相对原点的坐标**、再对内层 `scale`。`transformOrigin` 用**百分比**（`"50% 50%"`=包围盒中心）在 SVG 上是安全的。Gate: `scripts/check_svg_transform_anim.py`(规则2)。

### Color Coding
- **Primary objects:** indigo `#6366f1` or cyan `#06b6d4`
- **Derived/auxiliary:** violet `#8b5cf6`
- **Results/answers:** green `#10b981`
- **Warnings/caution:** amber `#d97706`
- **Error/incorrect:** red `#dc2626`
- **Element-specific colors** (flame colors, chemical indicators) should use their real-world colors (Na yellow `#fbbf24`, K violet `#a78bfa`, Cu green `#34d399`)

### Step Choreography Pattern
For multi-step animated procedures, use `onStart` callbacks to manage DOM state:

```js
tl.to("#wire-group", {
  attr: { transform: "translate(850,200)" },
  duration: 1.5,
  ease: "power2.inOut",
  onStart: function() {
    document.getElementById("node-2").classList.add("active");
    document.getElementById("node-1").classList.remove("active");
    document.getElementById("node-1").classList.add("completed");
  }
}, 8.0);
```

### Continuous Motion
- Flame flicker: `scaleY` oscillation with `yoyo: true` and repeat count `R(dur)`
- Electron orbit: circular motion via `motionPath` or alternating `cx`/`cy` with `yoyo`
- Liquid wave: `d` path morph or `y` offset oscillation
- Use the repeat helper: `var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };`

## Geometry Coordinate Accuracy (几何图形坐标精度)

When building Geometry Canvas scenes (Component 3), vertex coordinates MUST be computed from the problem's mathematical constraints — **never placed by visual estimation**. Estimated coordinates cause lines that should be perpendicular to visibly slant, length ratios to be wrong, and right angle marks to point in the wrong direction.

### Mandatory Workflow

**Step 1 — Solve for ratios first.** From the problem conditions (perpendicularity, similarity, length ratios, Pythagorean theorem), derive the exact proportional relationships between all segments before writing any SVG.

Example: "正方形ABCD, E在BC上, AE⊥EF, AE=2, EF=1"
- Triangle ABE ~ Triangle ECF (AA similarity) → AE/EF = AB/EC = 2/1
- Let AB=a, BE=x → a = 2(a-x) → a = 2x → BE/AB = 1/2
- Pythagorean: a² + x² = 4, 5x² = 4

**Step 2 — Choose a base unit and compute coordinates.** Pick the figure's base size in SVG units (e.g., square side = 320), then compute every point from the ratios.

Example (square side = 320, origin at (80,80)):
- A=(80,80), B=(400,80), C=(400,400), D=(80,400)
- BE/AB = 1/2 → BE = 160 → E = (400, 80+160) = (400, 240)
- EF perpendicular to AE, direction of AE = (320,160)
  → perpendicular direction = (-160, 320), simplified (-1, 2)
  → from E(400,240) along (-1,2): parametric (400-t, 240+2t)
  → hits DC at y=400: t=80 → F = (320, 400)

**Step 3 — Verify constraints numerically.** Before writing the SVG, check:

- **Perpendicularity:** dot product of direction vectors = 0
  ```
  AE = (320, 160), EF = (-80, 160)
  dot = 320×(-80) + 160×160 = -25600 + 25600 = 0 ✓
  ```
- **Length ratios:** Euclidean distances match the problem's ratios
  ```
  |AE| = √(320² + 160²) = √128000 ≈ 357.8
  |EF| = √(80² + 160²) = √32000 ≈ 178.9
  |AE|/|EF| = 2.0 ✓
  ```
- **Point-on-line:** E is on BC (x=400 ✓), F is on DC (y=400 ✓)

**Step 4 — Write a `<!-- GEOMETRY VERIFICATION -->` block** above the SVG. This block is **machine-checked** by `scripts/check_geometry_verification.py` — the pre-render gate will FAIL if the assertions don't match the coordinates.

The block has two sections:
- `POINTS:` — declares all vertex coordinates
- `ASSERT` lines — declares every geometric constraint from the problem statement

```html
<!-- GEOMETRY VERIFICATION
POINTS: A=(80,80) B=(400,80) C=(400,400) D=(80,400) E=(400,240) F=(320,400)
ASSERT perpendicular A E E F
ASSERT on_segment E B C
ASSERT on_segment F D C
ASSERT ratio |AE| |EF| 2.0
-->
<svg viewBox="0 0 500 500" id="mt-g-svg">
  ...
</svg>
```

**Assertion types** (copy every relevant condition from the problem statement):

| Syntax | What it checks | Example |
|---|---|---|
| `parallel P1 P2 P3 P4` | Line P1P2 ∥ P3P4 (cross product ≈ 0) | `ASSERT parallel A B D C` → AB ∥ DC |
| `perpendicular P1 P2 P3 P4` | Line P1P2 ⊥ P3P4 (dot product ≈ 0) | `ASSERT perpendicular A E E F` → AE ⊥ EF |
| `midpoint M P1 P2` | M = (P1+P2)/2 | `ASSERT midpoint E B C` → E is midpoint of BC |
| `on_line P L1 L2` | P on infinite line through L1, L2 | `ASSERT on_line F A E` → F on line AE |
| `on_segment P L1 L2` | P on segment L1–L2 (on_line + between) | `ASSERT on_segment E B C` → E on segment BC |
| `intersection I L1 L2 L3 L4` | I = intersection of lines L1L2 and L3L4 | `ASSERT intersection F A E B D` → F = AE ∩ BD |
| `ratio \|P1P2\| \|P3P4\| R` | dist(P1,P2) / dist(P3,P4) = R (±2%) | `ASSERT ratio \|AE\| \|EF\| 2.0` |
| `collinear P1 P2 P3` | Three points are collinear | `ASSERT collinear A E F` |

**Tolerances:** 1.0 SVG unit for positions, 2% for ratios. SVG coordinates are typically integers or 1-decimal floats.

**Important:** The ASSERT lines come directly from the problem statement — e.g., "AB // DC" → `ASSERT parallel A B D C`, "E是BC中点" → `ASSERT midpoint E B C`, "F是AE与BD的交点" → `ASSERT intersection F A E B D`. The script verifies the POINTS coordinates satisfy these constraints. If coordinates are wrong, the gate catches it.

### Right Angle Mark (直角符号)

The standard right angle symbol is a **small L-shaped square** at the vertex — NOT a V-shape, NOT an arc, NOT a closed square. It is an open path with exactly 3 points forming two perpendicular edges.

**Construction algorithm** (at vertex E where lines EA and EF meet at 90°):

```
size = 20  (SVG units — adjust for viewBox scale)

1. Compute unit vectors from the vertex along each arm:
   uEA = normalize(A - E)    // direction from E toward A
   uEF = normalize(F - E)    // direction from E toward F

2. Compute three path points:
   P1 = E + size × uEA       // offset along EA direction
   P2 = P1 + size × uEF      // the corner (diagonal offset)
   P3 = E + size × uEF       // offset along EF direction

3. SVG path: M P1 L P2 L P3  (open path — no Z)
```

**Worked example** (E=(400,240), A=(80,80), F=(320,400)):
```
EA = A - E = (-320, -160), |EA| = √128000 = 160√5
uEA = (-320/160√5, -160/160√5) = (-2/√5, -1/√5) ≈ (-0.894, -0.447)

EF = F - E = (-80, 160), |EF| = √32000 = 80√5
uEF = (-80/80√5, 160/80√5) = (-1/√5, 2/√5) ≈ (-0.447, 0.894)

P1 = (400 + 20×(-0.894), 240 + 20×(-0.447)) = (382.1, 231.1)
P2 = (382.1 + 20×(-0.447), 231.1 + 20×0.894) = (373.2, 248.9)
P3 = (400 + 20×(-0.447), 240 + 20×0.894)     = (391.1, 257.9)
```
```html
<path d="M 382.1,231.1 L 373.2,248.9 L 391.1,257.9"
      stroke="#d97706" stroke-width="2" fill="none"/>
```

**Common mistakes to avoid:**
- Drawing a V-shape (two lines meeting at a point) instead of an L-shape (the square corner)
- Hardcoding mark coordinates by eye without computing from the actual line direction vectors
- Placing the mark at the wrong vertex
- Using arc paths for right angles (arcs are for non-right angles only)
- Drawing a closed square (adding Z to close the path) — the standard symbol is open

### Angle Arc (非直角的角度标记)

For angles that are NOT 90°, use SVG arc paths. Compute the start and end angles from the two direction vectors at the vertex:

```
radius = 30  (SVG units)

1. Compute angles of the two arms:
   angle1 = atan2(dy1, dx1)   // direction of arm 1 from vertex
   angle2 = atan2(dy2, dx2)   // direction of arm 2 from vertex

2. Compute arc start/end points:
   startX = vertex.x + radius × cos(angle1)
   startY = vertex.y + radius × sin(angle1)
   endX   = vertex.x + radius × cos(angle2)
   endY   = vertex.y + radius × sin(angle2)

3. SVG arc: M startX,startY A radius,radius 0 0,sweep endX,endY
   (sweep = 1 for counter-clockwise interior angle, 0 for clockwise)
```

Place the angle label (e.g., "角BAE") at the midpoint of the arc, offset outward by ~15 units.

### Geometry Self-Review Checklist

Before finalizing any Geometry Canvas scene, verify ALL of the following:

- [ ] All vertex coordinates computed from mathematical constraints (not estimated)
- [ ] Perpendicular lines verified: dot product of direction vectors = 0
- [ ] Length ratios verified: computed Euclidean distances match problem ratios
- [ ] Points verified to lie on their specified edges (e.g., E on BC, F on DC)
- [ ] Right angle marks are L-shaped open squares (not V-shapes, arcs, or closed squares)
- [ ] Right angle mark edges aligned with actual line direction unit vectors
- [ ] Coordinate table written as `<!-- GEOMETRY VERIFICATION -->` block above the SVG with POINTS and ASSERTs
- [ ] `python3 "$EDU_SKILL_ROOT/scripts/check_geometry_verification.py" dist` exits 0
- [ ] Triangle fill regions use the correct computed vertex coordinates
- [ ] Labels positioned near their corresponding points (offset 15-25 units to avoid overlap)
- [ ] No two SVG `<text>` labels overlap each other — never stack fulcrum/center + arm labels on one line (center above, arms below, anchored outward); stagger point labels sharing an axis; don't bury tick numbers. `python3 "$EDU_SKILL_ROOT/scripts/check_svg_label_overlap.py" dist` exits 0 (SKILL.md Rule #28)
- [ ] No label overlaps the DRAWING (文字不压线不压点) — every letter is offset OUTWARD ~18–24u from its point/line/curve, never on a stroke/axis/vertex dot; axis-point labels sit just below/above the axis, origin `O` in a quadrant, labels near a vertical/symmetry line anchored to clear it. `python3 "$EDU_SKILL_ROOT/scripts/check_svg_label_on_figure.py" dist` exits 0 (SKILL.md Rule #30)

## Build Order

For each scene in `STORYBOARD.md`:

1. Create `compositions/scene-[name].html`
2. Copy the matching template from [math-components.md](math-components.md)
3. Replace placeholder content:
   - KaTeX equations with actual LaTeX from `ANALYSIS.md`
   - Chinese text from `SCRIPT.md`
   - Element IDs if needed (keep `mt-` prefix)
4. Set `data-composition-id` to a unique value (e.g., `mt-problem`, `mt-step-1`)
5. Register timeline: `window.__timelines["mt-step-1"] = tl;`
6. Adjust GSAP timings to match `transcript.json` timestamps:
   - Each element's entrance should align with when narration mentions it
   - Step highlights should activate when narration reaches that step
7. Apply design-system.md tokens (colors, fonts, spacing)
8. Add aurora mesh background per design-system.md "Background Treatment" (wave texture + 3 gradient orbs)

### Step 9 (MANDATORY): Run precheck and fix-loop

After building ALL compositions, you MUST run the automated validation:

```bash
EDU_SKILL_ROOT="<absolute directory containing qwen-mm-plugins-edu-agent/SKILL.md>"
python3 "$EDU_SKILL_ROOT/scripts/precheck.py" dist
```

**If the output does NOT contain `ALL CHECKS PASSED`:**
1. Read each `FAIL` line — it tells you the exact file, problem, and fix
2. Apply the fix
3. Re-run `python3 "$EDU_SKILL_ROOT/scripts/precheck.py" dist`
4. Repeat until `ALL CHECKS PASSED` appears

**Common failures and their fixes:**
| Failure | Root cause | Fix |
|---------|-----------|-----|
| `[asset-mirror] compositions/gsap/ missing` | GSAP not mirrored | `cp -R dist/gsap dist/compositions/gsap` |
| `[asset-mirror] compositions/katex/ missing` | KaTeX not mirrored | `cp -R dist/katex dist/compositions/katex` |
| `[no-css-hidden] opacity: 0 in CSS` | CSS hides content | Remove `opacity:0` from CSS, use GSAP `autoAlpha:0` in JS instead |
| `[composition-format] full HTML document` | `<!doctype>` or `<html>` in sub-composition | Remove `<!doctype>`, `<html>`, `<head>`, `<body>` — sub-compositions are HTML fragments |
| `[katex-escape] \dfrac in JS string` | Single backslash in JS | Change `"\dfrac"` to `"\\dfrac"` |
| `[scene-coverage] missing composition` | Planned scene has no file | Create the missing `compositions/scene-xxx.html` |

**Do NOT proceed to Step 6 until precheck passes.**

## Defensive Script Pattern (防御性脚本 — 防止空白视频)

**This is the #1 cause of blank videos in batch processing.** Any JS error in a composition (KaTeX crash, GSAP selector miss, typo) will abort the entire script. If content is hidden by CSS `opacity: 0` waiting for GSAP to reveal it, a JS error means the content stays invisible forever → blank white frame.

### Rule 1: CSS must never hide content

**Never set `opacity: 0`, `visibility: hidden`, or `display: none` on `.scene-content` or any content element in CSS.** Let GSAP handle the initial hidden state dynamically via `autoAlpha: 0` in `fromTo()`. If GSAP fails, content remains visible (static but not blank).

```css
/* CORRECT: content visible by default AND vertically centered */
.scene-content {
  position: absolute; inset: 0; z-index: 1;
  display: flex; align-items: center; justify-content: center;  /* ← MANDATORY: centers content */
  padding: 40px 60px 180px; box-sizing: border-box;             /* bottom 180px = caption safe zone */
  /* NO opacity:0 here — GSAP handles fade-in dynamically */
}
```

```css
/* WRONG — causes blank scene on ANY JS error */
.scene-content {
  opacity: 0;  /* ← FORBIDDEN */
}
```

### Rule 2: Wrap ALL GSAP code in try-catch

Every composition's `<script>` block must wrap the entire timeline construction in a `try-catch`. If any tween fails, the timeline still gets registered (even if empty), and the content remains visible because CSS never hid it.

```js
window.__timelines = window.__timelines || {};

var SCENE_DURATION = 10;
var R = function(d) { return Math.ceil(SCENE_DURATION / d) - 1; };

var tl = gsap.timeline({ paused: true });

try {
  // --- KaTeX rendering ---
  try {
    katex.render("x^2", document.getElementById("eq-1"), { displayMode: true, output: "html" });
  } catch(e) { console.warn("KaTeX error:", e); }

  // --- GSAP animations ---
  // Scene fade-in (autoAlpha, not CSS opacity)
  tl.fromTo(".scene-content",
    { autoAlpha: 0 },
    { autoAlpha: 1, duration: 0.3, ease: "power2.out" }, 0);

  // Content animations...
  tl.fromTo(".glass-panel",
    { y: 60, autoAlpha: 0 },
    { y: 0, autoAlpha: 1, duration: 0.8, ease: "power3.out" }, 0.2);

  // Aurora drift...
  tl.fromTo(".a1", { x: 0, y: 0 },
    { x: -40, y: 30, duration: 4, ease: "sine.inOut", yoyo: true, repeat: R(4) }, 0);

} catch(e) {
  console.error("Timeline construction error in composition:", e);
  // Content stays visible because CSS never set opacity:0
  // Timeline may be partial but won't cause blank scene
}

// ALWAYS register the timeline, even if empty
window.__timelines["mt-step-1"] = tl;
```

### Rule 3: KaTeX render calls must each have individual try-catch

A single bad LaTeX string can crash `katex.render()` and abort the entire script. Wrap each call independently:

```js
// CORRECT: each KaTeX call isolated
var equations = [
  { id: "eq-1", tex: "f = \\frac{1}{T}", display: true },
  { id: "eq-2", tex: "A = \\frac{|x_2 - x_1|}{2}", display: true }
];

equations.forEach(function(eq) {
  try {
    var el = document.getElementById(eq.id);
    if (el) katex.render(eq.tex, el, { displayMode: eq.display, output: "html", throwOnError: false });
  } catch(e) { console.warn("KaTeX error for " + eq.id + ":", e); }
});
```

```js
// WRONG: one bad equation kills all subsequent renders
katex.render("bad \\ latex", el1, { displayMode: true });  // ← crashes here
katex.render("x^2", el2, { displayMode: true });           // ← never runs
```

### Rule 4: KaTeX must render at load, scoped by id (公式空白的两个已确认坑)

Two confirmed causes of blank formulas (public exam videos), both leaving the target element EMPTY:

**(1) Missing root `id` (deterministic — most common).** The root is `<div data-composition-id="mt-x">` (a data-attribute, NOT a DOM id) but the render loop scopes to `document.querySelectorAll("#mt-x [data-tex]")`. `#mt-x` matches **nothing** → 0 renders → every formula blank. **Fix:** give the root BOTH attributes `<div data-composition-id="mt-x" id="mt-x">`, or scope id-independently with `[data-composition-id="mt-x"]` / `document.currentScript.closest('[data-composition-id]')`. Enforced by `scripts/check_composition_root_id.py`.

**(2) Render synchronously at load — do NOT defer.** The HyperFrames renderer captures deterministically by seeking the GSAP timeline; it does **not** reliably flush `setTimeout`/`requestAnimationFrame` or other async work you schedule. So render KaTeX **synchronously in the composition's inline `<script>` at load time** (as the working scenes do) — never wrap `katex.render` in `setTimeout`/polling, and don't rely on a late/`onload` re-render. KaTeX is already available synchronously at that point (index.html loads it in `<head>`).

Canonical synchronous, id-independent render for all `[data-tex]` nodes in the composition:

```js
try {
  var _root = (document.currentScript && document.currentScript.closest('[data-composition-id]')) || document;
  _root.querySelectorAll('[data-tex]').forEach(function(el){
    try { katex.render(el.getAttribute('data-tex'), el,
          { displayMode: el.hasAttribute('data-display'), output:'html', throwOnError:false }); }
    catch(e){ console.warn('katex', e); }
  });
} catch(e){}
```

Prefer static `data-tex` attributes over building latex in JS strings (avoids the double-escape trap). Put the render loop **inside** the composition root's inline script (a `<script>` appended AFTER the root `</div>` is dropped on injection and never runs).

> ⚠️ Known unresolved edge case: a scene whose formula renders fine in `hyperframes validate`/standalone but is > still blank in the final MP4 has been observed (imperative KaTeX not surviving capture in that one scene). If > you hit this, verify against the rendered MP4 (not just validate) and rebuild the scene's markup from scratch.

## Caption Composition

**IMPORTANT: Inline captions in root index.html, NOT as a sub-composition.**

Captions placed in a `compositions/captions.html` sub-composition will have incorrect `position:absolute` positioning because the sub-composition container does not reliably fill the full 1080p frame height. This causes captions to overlap with scene content instead of sitting at the bottom.

**Correct approach — inline captions directly in index.html on Track 2:**

1. Load `captions.json` segments (original script text with TTS-measured timestamps)
2. For each segment, create a `<div>` with `class="clip caption-bar"` directly inside the root `data-composition-id` div
3. Each caption gets `data-start`, `data-duration`, `data-track-index="2"`, and a unique `id`
4. **Format math expressions:** Replace spoken-form Chinese math text with `<span class="cm">LaTeX</span>` elements (see step-6 for the replacement table and examples)
4. Style in the root `<style>` block:

```css
.caption-bar {
  position:absolute;
  bottom:20px;
  left:50%;
  transform:translateX(-50%);
  z-index:999;
  font-family:"Noto Sans SC",sans-serif;
  font-size:36px;
  font-weight:600;
  color:#0f172a;
  text-shadow: 0 1px 4px rgba(0,0,0,0.08);
  background:#ffffff;


  border: 1px solid rgba(99,102,241,0.2);
  border-top: 2px solid rgba(99,102,241,0.2);
  padding:10px 32px;
  border-radius:12px;
  box-shadow: 0 4px 20px rgba(99,102,241,0.1);
  text-align:center;
  white-space:nowrap;
  pointer-events:none;
}
```

5. `bottom:20px` positions captions at the very bottom of the 1920×1080 root container — no overlap with scene content
6. Avoid floating-point overlaps: if segment N ends at exactly the same time segment N+1 starts, trim segment N's duration by 0.01s
7. **Caption `font-size` MUST be 36–40px (use 36px). Never larger** — on the 1920×1080 canvas a bigger value (e.g. 64px) makes the subtitle huge, wrap to two lines, and dominate the frame. Use the `.caption-bar` class above; do not invent a custom caption class with a larger size. The pre-render gate `scripts/check_caption_size.py dist` enforces this (fails over 44px).

## Self-Review Checklist

For each composition file, verify:

**Structure & Timeline:**
- [ ] **File is an HTML fragment** — no `<!doctype>`, `<html>`, `<head>`, `<body>` tags; root element is `<div data-composition-id="...">` (a full HTML document wrapper causes blank panels)
- [ ] `data-composition-id` is set and unique
- [ ] GSAP timeline is `paused: true` and registered on `window.__timelines`
- [ ] All animations on the seekable timeline (no bare `gsap.to()`)
- [ ] Uses `fromTo()` instead of `from()` for deterministic seeking
- [ ] **No CSS `opacity: 0` on any content element** — GSAP handles hiding dynamically via `autoAlpha: 0` in `fromTo()`. CSS-hidden content + JS error = blank scene
- [ ] **Entire GSAP timeline wrapped in try-catch** — timeline still registers even if construction partially fails
- [ ] **Each KaTeX render call has individual try-catch** — one bad formula must not kill the entire scene
- [ ] No `Math.random()`, `Date.now()`, or async timeline construction

**Visual Quality:**
- [ ] Panel is OPAQUE (`background:#ffffff`, NO `backdrop-filter`) — depth comes from border + layered box-shadow (never a see-through / blurred panel that occludes content)
- [ ] 3D perspective is subtle (under 5 degrees rotation)
- [ ] KaTeX renders correctly (no raw LaTeX visible in the output)
- [ ] **KaTeX CSS inlined as `<style>`** — no `<link rel="stylesheet" href="...katex.min.css">`; KaTeX JS and fonts loaded from the local `./katex/` copy, NOT a CDN
- [ ] **Self-hosted `@font-face` embedded (offline)** — the Noto Sans SC / Inter / JetBrains `@font-face` block is present and `dist/assets/fonts/` exists; NO Google Fonts / CDN `<link>` (prevents garbled Chinese 乱码 in the air-gapped render)
- [ ] **No CDN `<script>` tags** — GSAP loaded from local `./gsap/gsap.min.js` (NOT `cdn.jsdelivr.net`); all `<script src>`, `<link href>`, and `url()` use local relative paths only
- [ ] Equations are readable at rendered resolution (minimum 48px effective)
- [ ] Colors use design-system.md tokens (light-theme color values)
- [ ] Chinese text uses a CJK-first stack (`"Noto Sans SC", Inter, sans-serif`) — never `Inter, sans-serif` alone
- [ ] **Dark text on light backgrounds** — Full "Mandatory Global Color Reset" from design-system.md is present: root selector has `color: #0f172a`; `.katex, .katex * { color: #0f172a; }` overrides KaTeX defaults; `.katex-mathml { display: none !important; }` hides MathML fallback text; `table, th, td { color: #0f172a; }` covers HTML tables; all SVG text `fill` uses `#0f172a`
- [ ] **No emoji characters** — zero emoji in titles, labels, notes, captions, or any visible string (they render as boxes in headless Chromium)
- [ ] **Simple symbols use HTML entities, not KaTeX** — for comparisons (≤, ≥, ≠), degrees (°), multiplication (×), use HTML entities or Chinese text directly; reserve `katex.render()` for expressions that need layout features (fractions, roots, matrices). Write `<span>OP' ≤ 1</span>` not `katex.render("OP' \\leq 1", ...)`
- [ ] **No Chinese inside KaTeX** — never use `\text{中文}` in any KaTeX expression. KaTeX math fonts lack CJK glyphs → Chinese renders as □ tofu. When mixing formula with Chinese, use separate HTML `<span>` elements for Chinese text and KaTeX `<span>` for math symbols
- [ ] **LaTeX in JS strings is double-escaped** — inside `katex.render("…")` or a `tex:`/`latex:` field, every backslash is doubled (`"4 \\times 3"`, `"\\frac{a}{b}"`, `"x \\neq y"`). A single backslash is eaten by JS (`\t`→tab, `\n`→newline, `\f`→form-feed) and KaTeX then renders "imes"/"eq"/"rac". LaTeX in HTML `data-tex="4\times3"` stays single-backslash
- [ ] **Scene content wrapper centers AND fills the frame** — `.scene-content` is a centering box that fills the frame: `position:absolute; inset:0; display:flex; align-items:center; justify-content:center` (root is `position:relative; height:1080px`). The `display:flex; align-items:center; justify-content:center` trio is **mandatory** — filling the frame alone (`position:absolute;inset:0` with no flex-center) lets a single panel collapse to its content height and pile at the TOP with the bottom half empty. Only exception: a content wrapper that fills the height itself (`width:100%; height:100%` split-layout row, or a title container that is `position:absolute; inset:0`). Enforced by `check_scene_layout.py`
- [ ] **Scene content FITS inside the frame — never taller than one screen (内容不超出一屏被裁切)** — a scene's content column must fit within the usable height ≈ **1080 − top padding − 180px caption safe zone ≈ 860px**. Because `.scene-content` centers vertically inside an `overflow:hidden` root, content taller than the frame spills off BOTH the top and bottom and gets **clipped** (e.g. the top panel's first row chopped off) — a severe layout failure. Cause is almost always **cramming several ideas into one scene** (a big diagram + a full data table + a conclusion bar stacked vertically). FIX: obey **one concept per scene** — split the overflowing scene into multiple scenes; or shrink fonts/panels / use a more compact 2-column layout; or wrap the content in an outer element with `transform: scale(min(1, 860/contentHeight)); transform-origin: top center` to fit. This is **headless-measured** and enforced by `check_scene_fit.py` — a scene whose content is clipped by the 1920×1080 edge FAILS the build.
- [ ] **No gradient text on formulas** — any element holding a KaTeX formula uses a solid `color`; zero `background-clip:text` + `-webkit-text-fill-color:transparent` on it (otherwise glyphs vanish and only the fraction bar shows as a stray dash). Gradient text is for plain-text titles only
- [ ] **Chinese font NOT subsetted** — `dist/assets/fonts/` has no `*subset*` files; each "Noto Sans SC" `@font-face` references exactly ONE `url(...)` (a comma-separated multi-file `src` loads only the first → tofu)
- [ ] **Grid/lattice figures generated programmatically** — matchstick/square-array/dot diagrams are built from a cell list with deduped edges (not hand-typed `<line>`s); each figure's drawn element count EQUALS the number the problem states for it (e.g. 4 / 10 / 18); figure geometry follows `ANALYSIS.md` / the standard answer when the prose wording conflicts
- [ ] **Continuous curves are SMOOTH, not straight-chord polylines** — function graphs (抛物线/双曲线/sin/指数衰减) and trend/oscillation curves (种群波动、阻尼振荡) are drawn as a smooth `<path>` Bézier (Catmull-Rom helper) or a densely-sampled point list (~1 pt per ≤10 px), never a `<polyline>` of ~10–15 straight segments. Genuinely piecewise-linear graphs (`y=|x|`, 分段函数, 折线统计图) are the only exception (see "Smooth curves (顺滑曲线)")
- [ ] **Multiple-choice options show their CONTENT** — for 选择题, every option renders as letter + full value (`A 1/2`, `B 1/3`, …), not bare `A B C D`; each option's value is actually visible (not a blank `data-tex`/`.cm` span from the missing-root-`id` bug)
- [ ] **Tubes enter vessels through the OPENING, not the glass** — any 导管/thermometer/funnel-stem going into a flask/bottle/test-tube/beaker/gas-jar passes in through the mouth (external part above the rim, descends through the opening between the neck walls); it never crosses a side/bottom wall stroke, never pokes out through the glass, and its tip depth (below vs above the liquid surface) matches the experiment (容器与导管 rule)
- [ ] **Pouring (倾倒) reads as pouring** — the pouring vessel's lip sits at the receiving container's rim (no floating gap), tilted about its lip with the mouth pointing down into the target; a SOLID tapering stream (not a thin dashed arc) flows lip→contents (down the wall for 沿杯壁); the target's level rises / dense gas fills bottom-up (倾倒 rule)
- [ ] **动效匹配物理 (process moves / adhesion forms in place)** — process verbs (伸入/插入/放入/滴入/倒入/通入/加热) are ANIMATED as the actual motion (actor enters/travels → reacts → settles; e.g. 燃着木条**下降进瓶**再熄灭, not static-in-jar + flame fade); adhesion/surface-precipitate/color-change (附着/镀/表面沉淀/变色) is drawn **ON the target's surface** (coords hug its outline) and revealed **in place** (`autoAlpha`/`scale` with `transform-box:fill-box;transform-origin:center`), **never** scattered in the solution or flown/staggered in from elsewhere (e.g. 铝丝上的红铜贴着丝原地生成, not loose dots drifting in the liquid). (see "Animation semantics: what MOVES vs what forms IN PLACE")

**Video-Scale Sizing (critical — web sizes look broken in 1080p):**
- [ ] SVG rects/plates are at least 30px wide (not 16px web-scale)
- [ ] SVG stroke-widths are at least 3px
- [ ] Particles/ions/bubbles have radius >= 14px AND glow filter applied
- [ ] All annotation text inside SVG is >= 20px font-size
- [ ] No elements smaller than 30px in either dimension without glow halo
- [ ] **Apparatus components (alcohol lamp, flask, burner, test tube) must be at least 200px tall** in any layout — if the catalog component's default size is smaller, apply `transform: scale()` on the container element to reach the target size

**Layout & Space:**
- [ ] Content fills at least 70% of the 1920×1080 frame
- [ ] No large empty light areas (panels should use max-width >= 1400px for single-panel scenes)
- [ ] Multi-card layouts span the full width (not clustered in center)
- [ ] **In split-panel apparatus scenes** (left panel showing equipment, right panel showing steps/text), the primary apparatus must fill at least **30-45% of the left panel height** and be centered vertically — a tiny apparatus floating in a large empty panel is a critical layout error

**Dynamic Effects (critical — static science diagrams look broken):**
- [ ] Process scenes (reactions, circuits, flows) have at least ONE continuously moving element
- [ ] Particle/electron motion uses `repeat: Math.ceil(SCENE_DURATION / dur) - 1` to fill the scene
- [ ] Multiple particles are staggered (not starting simultaneously)
- [ ] Gas generation scenes have rising bubble animations
- [ ] Flow direction is shown with animated dashes or moving particles, not static arrows
- [ ] Dissolving/consuming elements show gradual size/opacity change over the scene

**Circuit Schematic (电路原理图 — read [circuit-schematic-guide.md](circuit-schematic-guide.md)):**
- [ ] Battery symbol: **long line** has `+` label, **short line** has `-` label (never reversed)
- [ ] Battery `+`/`-` text positions match the physical symbol on the correct side
- [ ] Current direction arrows form a consistent closed loop from `+` to `-` through external circuit
- [ ] No arrow points backward against the current flow direction
- [ ] Ammeter wired in SERIES (part of main loop), `+` terminal faces battery `+` side
- [ ] Voltmeter wired in PARALLEL, `+` terminal on higher-potential side, dashed branch wires
- [ ] Used `sch-*` SVG templates from assets/components/circuit/ (not custom-drawn symbols)

**Physical Wiring Diagram (实物连接图 — read [circuit-schematic-guide.md](circuit-schematic-guide.md) Section 12):**
- [ ] Circuit forms a **rectangular loop** — NOT a flat horizontal line of components
- [ ] Ammeter is **ON the main loop wire** (bottom return wire), NOT floating outside the loop
- [ ] Voltmeter on a **separate dashed branch**, NOT squeezed inline between components
- [ ] Wire routing is **compact** — bounding box ≤100px margin beyond outermost components
- [ ] Components distributed across **2–3 sides** of the rectangle
- [ ] "Existing circuit" (if dimmed) uses a **rectangular loop**, not a straight line
- [ ] New meters inserted by **breaking existing wire** at the correct position
- [ ] Used **pre-built CSS components** from ASSET_CATALOG (`battery`, `meter.meter-a`, `meter.meter-v`, `switch`, `bulb`, `wire`)
- [ ] Meter `+` terminal faces battery `+` side; voltmeter `+` on higher-potential side
- [ ] Meter needle animated with `elastic.out` easing
- [ ] No wires pass through components — segmentation rules apply
- [ ] Used **Circuit Wiring Operation (C12)** template from math-components.md, NOT Chemistry Operation Flow (C9)

**SVG Diagrams (for Components 7-11 and custom SVG scenes):**
- [ ] SVG uses `viewBox` and scales correctly (no fixed px width/height on `<svg>`)
- [ ] Content SVG height is **bounded** — NOT `width:100%; height:auto` (which follows the viewBox ratio and overflows → 场景突然变大); use `height:100%` in a stretched container, or `max-height:<px>` + `preserveAspectRatio="xMidYMid meet"`
- [ ] All SVG text is >= 20px font-size with `font-family: "Noto Sans SC"` for Chinese
- [ ] Glow filters defined in `<defs>` and applied to small elements (radius < 20px)
- [ ] Animated/movable objects wrapped in `<g>` groups with unique `id` attributes
- [ ] Multi-step choreography uses `onStart` callbacks for DOM class toggling (pending→active→completed)
- [ ] Step indicator nodes transition through 3 states: pending (gray), active (indigo glow + scale 1.15), completed (indigo fill)
- [ ] Connector lines fill progressively as steps complete
- [ ] Equipment highlight cycling dims inactive cards to `opacity: 0.55`

**Comparison Panels (Component 10):**
- [ ] Left panel has red-tinted border (`rgba(220,38,38,0.25)`)
- [ ] Right panel has green-tinted border (`rgba(16,185,129,0.25)`)
- [ ] Result boxes use distinct colors: red ❌ vs green ✓
- [ ] Warning bar uses amber `#d97706` with pulse animation
- [ ] Center dashed divider separates panels clearly

**Scene Transitions & Background:**
- [ ] Scene has a 0.3s fade-in at timeline start (`.scene-content` opacity 0 to 1)
- [ ] Aurora mesh background: 3 `.aurora-orb` divs inside `.scene-bg` with `filter: blur(80px)`
- [ ] Aurora orb colors use scene-appropriate palette from design-system.md `scene-aurora-palette`
- [ ] `.bg-texture` layer present as first child of `.scene-bg` (references `../bg-texture.jpg`)
- [ ] No photo images, bokeh particles, or light sweep effects
- [ ] No overlapping elements at any timeline position

**Aurora Visual Effects (2 effects only):**
- [ ] Aurora drift: 3 orbs animated with GSAP `fromTo()` + `yoyo: true` + `repeat: R(dur)`
- [ ] Panel shadow breathing: `.glass-panel` boxShadow cycles with GSAP `yoyo: true`
- [ ] Simple 3-property entrance: `{ y: 60, opacity: 0, rotationX: 8 }` (no scale, no blur, no glow burst)
- [ ] `SCENE_DURATION` variable and `R()` repeat-count helper defined in each scene script
- [ ] All effects use GSAP `fromTo()` on the seekable timeline (no CSS `@keyframes`)
- [ ] No more than 2 ambient effects per scene (aurora drift + shadow breathing)

## Gate

Before proceeding to Step 6:
- [ ] All scene composition files exist in `compositions/`
- [ ] Captions are inlined in root `index.html` on Track 2 (NOT in a separate `compositions/captions.html`)
- [ ] Self-review checklist passed for every composition
- [ ] KaTeX rendering verified
