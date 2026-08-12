# Character Sheet Prompt Templates

## Original (ChatGPT-sourced, verbatim)

Create a professional AAA video game concept art character sheet/reference sheet on a clean light gray background.

The sheet should be organized like an official character design document used by a game studio for 3D modeling.

LAYOUT

• Large full-body front view
• Large full-body rear view
• Three head studies (front, 3/4, profile)
• Hair reference panel
• Eye close-up
• Clothing material/detail close-ups
• Weapon reference panel
• Color palette swatches
• Small information panel containing:
    - Character Name
    - Race
    - Age
    - Height
    - Build
    - Occupation
    - Alignment

STYLE

Highly realistic fantasy concept art.
Digital painting.
Crisp linework.
Neutral studio lighting.
Muted realistic colors.
No dramatic lighting.
No action pose.
No background scenery.
Designed specifically as a production-ready character turnaround for 3D artists.
Every panel should be proportionally consistent.
Show accurate anatomy.
Show clothing seams, stitching, belts, buckles, armor construction, and material textures.
The overall composition should resemble an official Blizzard, Riot Games, CD Projekt Red, or Naughty Dog concept sheet.

CHARACTER

(Insert character description here.)

OUTPUT

Ultra-high detail.
8k concept art quality.
Professional entertainment industry character design.
Sharp focus.
No watermark.
No logo.
No text errors.
No cropped body parts.

---

## fal.ai-Optimized Version

Key changes: layout front-loaded, negation → positive directives, explicit spatial language, redundant quality tokens consolidated.

---

Professional AAA video game concept art character sheet. Official character design reference document for 3D modeling. Clean flat light gray background. Neutral even studio lighting. Grid layout with labeled sections separated by thin hairline rules.

PANEL LAYOUT (top to bottom, left to right):

TOP LEFT — Information panel with uppercase serif labels: Character Name, Race, Age, Height, Build, Occupation, Alignment. Below it: a 3x3 grid of color palette swatches matching the character's tones.

CENTER (largest area) — Two full-body orthographic views side by side: front view (left) and rear view (right). Character standing upright, arms relaxed at sides. Both views show identical proportions, costume, and equipment.

RIGHT COLUMN — Detail studies stacked vertically with small uppercase labels:
• HEAD STUDIES: three portrait busts (frontal, three-quarter, profile)
• HAIR DETAIL: two cropped views showing construction, braids, undercut
• EYE CLOSE-UP: extreme macro of iris color and shape
• WEAPONS: isolated weapon designs in a row (sheathed and drawn)

BOTTOM LEFT — CLOTHING/DETAIL: three square close-up panels showing material textures (collar closure, belt hardware, bracer lacing).

STYLE DIRECTIVES:

Highly realistic fantasy concept art. Digital painting with crisp linework. Muted desaturated color palette. Flat neutral lighting with soft contact shadows only. Static standing pose. Plain background with zero scenery. Production-ready character turnaround. Proportionally consistent panels. Accurate anatomy. Visible construction details: clothing seams, stitching, belts, buckles, armor plates, material textures, wear marks. Composition matching official Blizzard, Riot Games, CD Projekt Red, or Naughty Dog concept sheets.

CHARACTER:

(Insert character description here.)

QUALITY:

Professional entertainment industry character design. Sharp focus throughout. Every element fully contained within its panel. Clean readable text labels. Pristine presentation.

---

## Model-Specific Notes

| Model | Size | Notes |
|-------|------|-------|
| GPT-Image 1.5 | 1536×1024 (landscape) | Strongest layout compliance. Handles original template equally well. |
| Ideogram V3 | "1536x1024" (string) | Best text rendering — lean into labeled sections. |
| Seedream 4.5 | 1920×1440 (landscape) | Budget option (~$0.03–0.04). Use optimized version only; negation breaks it. |
| Recraft V4 | 1536×1024 (dict) | Leans cinematic — add "flat reference sheet lighting" to counteract. |

## User File Locations

- Templates: `~/character designs/prompt-template-original.md`, `~/character designs/prompt-template-fal-optimized.md`
- Test renders: `~/character designs/model-test-*/` (filenames labeled by model)
