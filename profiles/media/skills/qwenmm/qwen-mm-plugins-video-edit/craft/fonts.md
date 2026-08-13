# Fonts Recipes — Curated Typography Library

A curated list of **free-for-commercial-use** fonts for video work, with genre-based pairings. Typography is the highest-leverage polish surface — a title set in the right face at the right weight does more for perceived quality than most effects. Declare the chosen faces in the taste contract's **Text treatment** (`craft/art-direction.md` §2).

License wording: fonts are not "copyright-free" in a literal sense. Prefer **OFL/open-license** fonts first; use **official free-commercial-use** fonts only when the official license page is available and saved/linked in the project notes. Non-OFL commercial-free fonts often restrict redistribution, resale, embedding, trademark/logo use, or font modification — verify those restrictions before shipping a client/commercial deliverable.

**Never assume system fonts.** `Helvetica` / `PingFang SC` exist on macOS only; a Linux render box silently falls back to something ugly. For deterministic output, download the font file into the project and reference it explicitly.

**Offline first: check the bundled library before downloading.** This skill
ships vetted font files in `<skill-root>/assets/fonts/` (browse them with
`assets/local-media.html`). Copy from there into the project. Downloads fail
(two fetches timed out and the piece shipped in a system 黑体). If the
contract's face is neither bundled nor downloadable, that is a
`[no-silent-downgrade]` event: pick another face **from the same register**
in this card (never a bare system default), log the substitution, and say so
in the verdict.

## Contents

Bundled offline library · Type scale floor · Latin display / body / mono /
script · Chinese · Cute sets (Latin + Chinese + pairings) · Genre pairings ·
Using downloaded fonts · Verification

## Bundled offline library — copy, don't download

These ship inside the skill and cover the common registers **including
Chinese**. Copy the whole family directory into the project's `assets/`,
link the CSS, use the exact `font-family` name. The `zh/` families are
split into unicode-range subsets — that is normal; the browser loads only
what the text needs, and everything stays offline.

### Chinese families — `zh/` subdirectory

| Family | `font-family` | Path under `<skill-root>/assets/fonts/` | Register |
|--------|---------------|------------------------------------------|----------|
| 霞鹜文楷 (reg+bold) | `"LXGW WenKai"` | `zh/lxgw-wenkai/` (link `lxgwwenkai-regular.css` / `-bold.css`) | warm diary, vlog, handwritten |
| 站酷快乐体 | `"ZCOOL KuaiLe"` | `zh/zcool-kuaile/` (link `chinese-simplified-400.css`) | cute, kids, playful |
| 马善政毛笔楷书 | `"Ma Shan Zheng"` | `zh/ma-shan-zheng/` (link `chinese-simplified-400.css`) | brush titles, food, tradition |
| 得意黑 | `"Smiley Sans Oblique"` | `zh/smiley-sans/` (link `font.css`) | sport, tech, punchy shorts |

### Latin families — `latin/` subdirectory (OFL, Google Fonts)

All files are latin-subset woff2, named `<slug>-latin-<weight>-<style>.woff2`.
Declare `@font-face` with the `font-family` name shown below.

| Family | `font-family` | Weights | Register | Best for |
|--------|---------------|---------|----------|----------|
| Anton | `"Anton"` | 400 | heavy impact | shorts hooks, captions, sports |
| Baloo 2 | `"Baloo 2"` | 400, 700 | puffy playful | kids titles, cute stickers |
| Bangers | `"Bangers"` | 400 | comic pop-culture | fun titles, comic-style overlays |
| Bodoni Moda | `"Bodoni Moda"` | 400, 700 | high-fashion serif | fashion, beauty, editorial luxury |
| Caveat | `"Caveat"` | 400, 700 | casual handwriting | vlog annotations, margin notes, cozy |
| Chakra Petch | `"Chakra Petch"` | 500, 700 | sci-fi tech | futuristic UI, sci-fi HUD, gaming |
| Cinzel | `"Cinzel"` | 400, 700 | classical monumental | epic trailers, history, cultural |
| Cormorant Garamond | `"Cormorant Garamond"` | 400, 700 | literary elegant serif | book-quality editorial, literary quotes |
| EB Garamond | `"EB Garamond"` | 400, 700 | traditional editorial serif | long-form documentary, press, journalism |
| Fredoka | `"Fredoka"` | 400, 700 | rounded friendly | cute but polished, product cards |
| IBM Plex Sans | `"IBM Plex Sans"` | 400, 700 | corporate warm | data readouts, corporate explainers |
| Inter | `"Inter"` | 400, 700 | neutral UI | subtitles, data overlays, tech body |
| JetBrains Mono | `"JetBrains Mono"` | 400, 700 | code aesthetic | build-log, terminal HUD, code demos |
| Manrope | `"Manrope"` | 400, 700 | rounded neutral | friendly products, warm vlog body |
| Montserrat | `"Montserrat"` | 400, 700 | geometric versatile | safe default for titles, brand films |
| Nunito | `"Nunito"` | 400, 700 | rounded soft | education, kids body text, gentle UI |
| Orbitron | `"Orbitron"` | 400, 700 | space-age tech | sci-fi, space, tech HUD, neon |
| Oswald | `"Oswald"` | 400, 700 | condensed authoritative | news, documentary, sport headlines |
| Permanent Marker | `"Permanent Marker"` | 400 | graffiti casual | street culture, casual annotations |
| Playfair Display | `"Playfair Display"` | 400, 700 | elegant high-contrast serif | luxury, travel, premium branding |
| Rajdhani | `"Rajdhani"` | 500, 700 | techy condensed | sport data, dashboards, stats |
| Sora | `"Sora"` | 400, 700 | modern geometric clean | UI demos, SaaS products, clean titles |
| Space Grotesk | `"Space Grotesk"` | 400, 700 | techy modern | AI/tech promos, product launches |
| Teko | `"Teko"` | 400, 700 | condensed bold sports | scoreboard, stats, big-number stage |

### Legacy top-level files (still valid)

| Family | `font-family` | Path | Register |
|--------|---------------|------|----------|
| Quicksand 700 | `"Quicksand"` | `Quicksand-700.woff2` | rounded friendly Latin |
| Bitter 300 | `"Bitter"` | `Bitter-300.woff2` | editorial serif Latin |
| Barlow 800 | `"Barlow"` | `barlow-800.woff2` | condensed impact Latin |

Wiring example (warm diary, Chinese titles):

```html
<link rel="stylesheet" href="assets/fonts/lxgw-wenkai/lxgwwenkai-bold.css">
<style>.title { font-family: "LXGW WenKai", serif; font-weight: 700; }</style>
```

Wiring example (tech promo, Latin titles):

```css
@font-face {
  font-family: "Space Grotesk";
  src: url("./assets/fonts/latin/space-grotesk-latin-700-normal.woff2") format("woff2");
  font-weight: 700;
}
.title { font-family: "Space Grotesk", sans-serif; font-weight: 700; }
```

**A Chinese-text piece set in `PingFang SC` / `Noto Sans SC` fallback is a
failed Text treatment** — the `zh/` families above exist so it never
happens again.

## Type scale floor — don't ship tiny text

Sizes below are **minimums** as % of the canvas's SHORT edge (1080px in
both 1920×1080 and 1080×1920). Going bigger is almost always right;
full-bleed footage eats small type.

| Role | Floor (% short edge) | On 1080 | Aim for |
|------|---------------------|---------|---------|
| Main title (opening/closing card) | 9% | ≥ 96px | 12-16% (130-170px) |
| Scene/section card main line | 6% | ≥ 64px | 7-9% |
| Badge / label / kicker | 4.5% | ≥ 48px | 5-6% |
| Caption / sub-line | 3.2% | ≥ 34px | 4% |

Quick self-test: zoom the frame to thumbnail size (~25%). If a text element
becomes unreadable there, it is under-sized for phone viewing (42px
badges on a portrait canvas — 3.9%, below floor — drew "字太小").


## Latin — Display / Titles

| Font | License | Personality | Get it |
|------|---------|-------------|--------|
| Bebas Neue | OFL | Tall condensed, poster energy | Google Fonts |
| Anton | OFL | Heavy impact, shorts/captions | **BUNDLED** `latin/anton-*` |
| Montserrat | OFL | Geometric, versatile, safe default | **BUNDLED** `latin/montserrat-*` |
| Oswald | OFL | Condensed, news/sport | **BUNDLED** `latin/oswald-*` |
| Archivo Black | OFL | Brutal weight, stat callouts | Google Fonts |
| Space Grotesk | OFL | Techy, product/AI promos | **BUNDLED** `latin/space-grotesk-*` |
| Clash Display | ITF FFL (free commercial use) | Modern premium, brand films | Fontshare |
| Playfair Display | OFL | Elegant serif, luxury/travel | **BUNDLED** `latin/playfair-display-*` |
| DM Serif Display | OFL | Editorial serif, quotes | Google Fonts |
| Bangers | OFL | Comic pop-culture energy, fun titles | **BUNDLED** `latin/bangers-*` |
| Bodoni Moda | OFL | High-fashion, editorial luxury | **BUNDLED** `latin/bodoni-moda-*` |
| Chakra Petch | OFL | Sci-fi tech, futuristic HUD | **BUNDLED** `latin/chakra-petch-*` |
| Cinzel | OFL | Classical monumental, epic/cultural | **BUNDLED** `latin/cinzel-*` |
| Orbitron | OFL | Space-age, sci-fi HUD, neon tech | **BUNDLED** `latin/orbitron-*` |
| Permanent Marker | OFL | Graffiti casual, street annotations | **BUNDLED** `latin/permanent-marker-*` |
| Teko | OFL | Condensed bold, sports/scoreboard | **BUNDLED** `latin/teko-*` |

## Latin — Body / Subtitles

| Font | License | Personality | Get it |
|------|---------|-------------|--------|
| Inter | OFL | Neutral UI, excellent small-size legibility | **BUNDLED** `latin/inter-*` |
| Manrope | OFL | Rounded-neutral, friendly products | **BUNDLED** `latin/manrope-*` |
| IBM Plex Sans | OFL | Corporate but warm | **BUNDLED** `latin/ibm-plex-sans-*` |
| Nunito | OFL | Rounded soft, gentle readability | **BUNDLED** `latin/nunito-*` |
| Sora | OFL | Modern geometric clean, UI body | **BUNDLED** `latin/sora-*` |
| Rajdhani | OFL | Techy condensed, data/sport body | **BUNDLED** `latin/rajdhani-*` |

## Mono — Code / Terminal / HUD

| Font | License | Personality | Get it |
|------|---------|-------------|--------|
| JetBrains Mono | OFL | Code overlays, build-log aesthetics | **BUNDLED** `latin/jetbrains-mono-*` |
| Space Mono | OFL | Retro-terminal, sci-fi HUD | Google Fonts |
| IBM Plex Mono | OFL | Clean data readouts | Google Fonts |

## Script / Handwritten

| Font | License | Personality | Get it |
|------|---------|-------------|--------|
| Caveat | OFL | Casual margin notes | **BUNDLED** `latin/caveat-*` |
| Pacifico | OFL | Playful, retro-fun | Google Fonts |
| Great Vibes | OFL | Formal elegance, weddings | Google Fonts |

## Chinese — 中文（均可免费商用）

| Font | License | Personality | Get it |
|------|---------|-------------|--------|
| 思源黑体 / Noto Sans SC | OFL | 万金油正文黑体，多字重 | Google Fonts / Adobe GitHub |
| 思源宋体 / Noto Serif SC | OFL | 高级感宋体，人文/纪录片 | Google Fonts / Adobe GitHub |
| 得意黑 Smiley Sans | OFL | 窄斜标题黑，运动/潮流短视频爆款 | **BUNDLED** `assets/fonts/zh/smiley-sans/` |
| 霞鹜文楷 LXGW WenKai | OFL | 温暖手写楷体，vlog/生活记录 | **BUNDLED** `assets/fonts/zh/lxgw-wenkai/` |
| 阿里巴巴普惠体 | Official free commercial use (restricted) | 品牌感黑体，电商/产品 | alibabafont.com |
| MiSans | Official free commercial use (restricted) | 现代 UI 黑体，科技感 | hyperos.mi.com/font |
| OPPO Sans | Official free commercial use (restricted) | 圆润友好 | coloros.com / open.oppomobile.com |
| 钉钉进步体 | Free commercial use (verify official license) | 略斜有冲劲，职场/效率主题 | 钉钉官网 |
| 优设标题黑 | Free commercial use (verify official license) | 短视频标题利器，粗壮倾斜 | uisdc.com |

## Cute / Friendly / Playful（可爱、亲子、宠物、治愈）

High-confidence set: prefer **OFL/open-license** fonts. These are safe defaults for cute videos without looking amateurish.

### Latin Cute Set

| Font | License | Personality | Best use | Get it |
|------|---------|-------------|----------|--------|
| Fredoka | OFL | Rounded, friendly, polished | Cute but professional subtitles / product cards | **BUNDLED** `latin/fredoka-*` |
| Baloo 2 | OFL | Puffy, energetic, childlike | Kids titles, stickers, playful lower-thirds | **BUNDLED** `latin/baloo-2-*` |
| Comic Neue | OFL | Casual comic handwriting, cleaner than Comic Sans | Dialogue captions, fun commentary | Google Fonts |
| DynaPuff | OFL | Soft sticker / scrapbook feel | Handcrafted title cards, cute overlays | Google Fonts |
| Chewy | OFL | Bouncy cartoon title face | Pet videos, funny punchlines, kids hooks | Google Fonts |
| Bubblegum Sans | OFL | Rounded bubblegum tone | Warm short-form titles, playful captions | Google Fonts |
| Patrick Hand | OFL | Classroom handwritten note | Annotation arrows, notebook-style explainers | Google Fonts |
| Nunito | OFL | Rounded UI sans, very readable | Body/subtitles when display fonts are too loud | **BUNDLED** `latin/nunito-*` |
| Quicksand | OFL | Soft geometric, gentle | Calm cute brands, minimal vlog overlays | **BUNDLED** `Quicksand-700.woff2` |

### Chinese Cute Set

| Font | License | Personality | Best use | Get it |
|------|---------|-------------|----------|--------|
| 霞鹜文楷 LXGW WenKai | OFL | Warm handwritten Kai style | Family vlog, travel diary, cozy subtitles | GitHub: lxgw/LxgwWenKai |
| 小赖字体 Xiaolai SC | OFL | Cute handwriting, student-notebook feel | Scrapbook captions, childlike title cards | GitHub: lxgw/kose-font |
| 芫荽 Iansui | OFL | Rounded handwritten, Japanese-cozy tone | Healing videos, soft narration subtitles | GitHub: ButTaiwan/iansui / Google Fonts |
| 得意黑 Smiley Sans | OFL | Slanted playful display sans | Cute but punchy titles, pet/funny shorts | GitHub: atelier-anchor/smiley-sans |
| 阿里妈妈方圆体 | Official free commercial use (restricted) | Rounded commercial brand tone | Cute product videos, polished brand captions | Alibaba font official site (verify restrictions) |
| 思源黑体 / Noto Sans SC | OFL | Neutral fallback with full CJK coverage | Subtitle fallback when cute display fonts miss glyphs | Google Fonts / Adobe GitHub |

### Cute Pairing Recipes

| Style | Latin | Chinese | Notes |
|-------|-------|---------|-------|
| Cozy family vlog | Fredoka + Nunito | 霞鹜文楷 + 思源黑体 | Warm, readable, not childish |
| Kids education | Baloo 2 + Comic Neue | 小赖字体 + 思源黑体 | Big title + friendly explanatory captions |
| Pet / funny short | Chewy + Fredoka | 得意黑 + 思源黑体 | Strong hook text; keep body text simple |
| Scrapbook sticker | DynaPuff + Patrick Hand | 芫荽 / 小赖字体 | Works well with doodles, arrows, tape labels |
| Cute product brand | Fredoka + Quicksand | 阿里妈妈方圆体 + 思源黑体 | Rounded commercial polish |

Rule: use the cute/display font for **titles and emphasis only**; use a readable fallback (`Nunito`, `Quicksand`, `Noto Sans SC`, `思源黑体`) for longer subtitles.

## Genre Pairings（标题 + 正文/字幕）

| Video genre | Latin pairing | 中文搭配 | Mood tags |
|-------------|--------------|----------|-----------|
| Tech / AI / product promo | Space Grotesk + Inter | MiSans / 思源黑体 | techy, clean, modern |
| Short-form punch (抖音/Shorts) | Anton + Inter | 得意黑 / 优设标题黑 + 思源黑体 | punchy, energetic, bold |
| Luxury / travel | Playfair Display + Montserrat Light | 思源宋体 | elegant, premium, serif |
| Warm vlog / family | Caveat + Manrope | 霞鹜文楷 | cozy, handwritten, warm |
| Terminal / build-log / dev | JetBrains Mono (all roles) | 思源黑体（辅助） | code, monospace, terminal |
| News / documentary | Oswald + IBM Plex Sans | 思源黑体 + 思源宋体（引言） | authoritative, condensed |
| Sci-fi / gaming / neon | Orbitron + Chakra Petch + Inter | 思源黑体 | futuristic, HUD, neon |
| Fashion / beauty | Bodoni Moda + Montserrat | 思源宋体 | high-fashion, editorial |
| Food / cooking / artisan | Cinzel + Cormorant Garamond | 马善政 + 思源黑体 | classical, cultural, warm |
| Sports / stats / data | Teko + Rajdhani + Inter | 得意黑 + 思源黑体 | condensed, scoreboard |
| Kids / education / cute | Fredoka + Baloo 2 + Nunito | 站酷快乐体 + 霞鹜文楷 | rounded, playful, friendly |
| Epic / cultural / history | Cinzel + EB Garamond | 思源宋体 + 马善政 | monumental, literary |

Pairing rules of thumb: max 2 families per video (3 if one is mono for HUD); contrast weight and width, not two similar sans; keep one family for all subtitles throughout.

**Fallback chains** — when the preferred face is unavailable, substitute within the same register:

| Register | Prefer | Then | Then |
|----------|--------|------|------|
| Techy display | Space Grotesk | Sora | Montserrat |
| Impact display | Anton | Teko | Oswald |
| Elegant serif | Playfair Display | Bodoni Moda | Cormorant Garamond |
| Handwritten | Caveat | Permanent Marker | (download Pacifico) |
| Sci-fi | Orbitron | Chakra Petch | Rajdhani |
| Neutral body | Inter | Manrope | IBM Plex Sans |
| Cute display | Fredoka | Baloo 2 | Nunito |
| Code/mono | JetBrains Mono | (download Space Mono) | (download IBM Plex Mono) |

## Font Selection Discipline

### Anti-defaults — overused combinations to avoid

These font treatments have become the "AI slop" of video typography. When the
brief does not demand them, pick something more specific to the piece:

1. **Inter for everything** — title, body, captions, data all in Inter. It is
excellent body text but too neutral to carry a video's personality alone.
The title face should be *memorable*, not invisible.
2. **Anton + slide transition** — the default "punchy short-form" recipe.
If the piece has a signature device other than impact text, reach for Teko,
Oswald, or Bangers instead.
3. **System default CJK** — `PingFang SC`, `Noto Sans SC`, or `Microsoft YaHei`
without explicitly choosing them. Always declare a bundled `zh/` face in the
taste contract; an undeclared CJK fallback is a contract violation.

### Signature font principle

Every video should have **one typographic choice that makes it memorable** —
a display face, a handwritten accent, or a mono-for-HUD decision that the
viewer would associate with this piece. Borrowed from `frontend-design`:
"Let the signature element be the one memorable thing, keep everything around
it quiet and disciplined."

If all three dials (`visual_variance`, `motion_intensity`, `information_density`)
are mid-range, the signature font is the easiest lever to pull for personality.
A tech piece using Orbitron for HUD elements reads differently from one using
JetBrains Mono — same register, different signature.

### Two-pass critique (before finalizing font choices in the taste contract)

**Pass 1 — propose**: pick fonts from the genre pairing table or the bundled
library based on the brief's register and mood tags.

**Pass 2 — challenge**: for each chosen face, ask:
> "Would I make this same choice for a completely different video in the
> same genre?"

If yes, the choice is too generic — revise to something more specific to *this*
piece's content, brand, or reference. Record the pass-2 reasoning in the taste
contract's Text treatment field.

### Mood-to-font quick lookup

When the brief names a mood or the register-to-text-treatment table
(`craft/art-direction.md` §2) points to a class of face, scan this table:

| Mood keyword | Reach for (display) | Reach for (body) | Avoid |
|-------------|---------------------|-------------------|-------|
| techy, modern, AI | Space Grotesk, Sora, Chakra Petch | Inter, IBM Plex Sans | brush, serif, handwritten |
| elegant, luxury, premium | Playfair Display, Bodoni Moda, Cinzel | Montserrat Light, Cormorant Garamond | condensed impact, comic |
| cozy, warm, personal | Caveat, Permanent Marker | Manrope, Nunito | geometric sans, mono |
| punchy, energetic, bold | Anton, Teko, Bangers, Oswald | Inter, Rajdhani | elegant serif, script |
| futuristic, sci-fi, neon | Orbitron, Chakra Petch | Inter, Rajdhani | serif, handwritten, classical |
| cute, playful, kids | Fredoka, Baloo 2, Bangers | Nunito, Quicksand | impact, monumental, serif |
| cultural, classical, epic | Cinzel, EB Garamond | Cormorant Garamond, IBM Plex Sans | comic, puffy, neon |
| editorial, press, literary | EB Garamond, Bodoni Moda, Playfair Display | IBM Plex Sans, Inter | techy, comic, space-age |
| sport, data, scoreboard | Teko, Rajdhani, Anton | IBM Plex Sans, Inter | script, elegant serif |

## Using Downloaded Fonts

Store project fonts in `<videos_dir>/edit/assets/fonts/` (never inside the skill directory).

**ffmpeg subtitle burn-in** — point libass at the font dir; `FontName` must match the font's internal family name (check with `fc-scan file.ttf | grep family`):

```bash
ffmpeg -i in.mp4 -vf "subtitles=subs.srt:fontsdir=<videos_dir>/edit/assets/fonts:force_style='FontName=Smiley Sans Oblique,FontSize=24'" out.mp4
```

**drawtext** — reference the file directly:

```bash
ffmpeg -i in.mp4 -vf "drawtext=fontfile=<videos_dir>/edit/assets/fonts/Anton-Regular.ttf:text='BIG TITLE':fontsize=120" out.mp4
```

**HyperFrames / HTML** — embed via `@font-face` with a **local file path**, never a CDN link (deterministic-render rule: network fetch mid-render can miss frames):

```css
@font-face {
  font-family: "Smiley Sans";
  src: url("./assets/fonts/SmileySans-Oblique.ttf") format("truetype");
}
```

## Verification (per platform principles)

- **Tofu check**: after burn-in / render, extract one text-bearing frame and confirm glyphs actually rendered — a wrong `FontName` fails silently to the fallback font, and CJK text turns into boxes when the face lacks Chinese glyphs
- **Cheap-probe**: test a new font on a single drawtext frame before wiring it through the whole composition
- Chinese display fonts often ship a limited glyph set — verify every character of your actual title text renders before committing to the face
