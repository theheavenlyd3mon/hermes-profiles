# Finding Reference Images for Character-Based Banner Heroes

When a user wants a skin featuring a specific character, game boss, or anime/manga figure,
generic image searches return a lot of fan art — much of it stylistically different from
the canonical design. This file documents the search and verification workflow.

## The Problem

Wallpaper sites (WallpaperCave, Zedge, Pinterest) and image search engines aggregate
everything labeled with a character name. Many results are:

- **Fan art** with a very different art style from the original
- **AI-generated** images that approximate the design vaguely
- **Mislabeled** — not actually the character at all
- **Cropped or stylized** beyond recognition in ASCII conversion

If you convert the wrong image, the banner_hero won't look like what the user expects.

## Search Sources (ranked by reliability)

### 1. Fandom / Wiki sites (best for canonical references)
The character's fandom wiki page almost always has the most accurate reference image.
Look for the infobox image — it's usually a clean front-facing or 3/4 view.

- URL pattern: `https://<series>.fandom.com/wiki/<Character_Name>`
- Image URL pattern (nocookie): `https://static.wikia.nocookie.net/<series>/images/...`
- Remove `/scale-to-width-down/<N>` from the URL to get the full-resolution original
- The wiki often has a `/Gallery` subpage with more panels

### 2. ArtStation (best for high-quality, detailed reference)
Professional and semi-pro artists. Results are usually high quality, but may still be
stylized interpretations rather than canonical.

- Search: `https://www.artstation.com/search?query=<character>+<series>`
- Look for artists who worked on or closely reference the official material
- AJ Ramos, Ivan Aguirre, Davide Coleschi are common for Solo Leveling fan art

### 3. DuckDuckGo / Google Images
Broadest selection but lowest signal-to-noise ratio.

- Use the image-specific search (`&iax=images&ia=images`)
- Verify every candidate with `vision_analyze` before downloading
- Be especially skeptical of 4K/8K tagged wallpapers — many are AI upscales

### 4. Pinterest
Good for discovering specific panels/scenes, but links are usually indirect.
Extracting the actual image URL requires extra steps.

### 5. Direct webtoon/manga reader screenshots
The most accurate source. Search for e.g. "<series> chapter <N> panel <description>".
Harder to find as a standalone image but the most canonical.

## Verification Workflow (DO NOT SKIP)

When you find a candidate image:

1. **Call `vision_analyze`** with a specific question:
   ```
   "Is this the canonical [Character Name] from [Series]? Describe the face —
    front-facing or angled? Key features: [list expected features]. Does it match
    the official design?"
   ```

2. **Check for specific canonical features.** For example, the Statue of God from
   Solo Leveling must have: glowing red eyes with black sclera, a full stone beard,
   a crown/headpiece, stone texture, and a wide creepy smile. Missing features →
   fan art or a different character.

3. **If the image fails verification**, do NOT use it anyway. The user will notice
   when the ASCII version doesn't look right. Try a different source.

4. **Download at high enough resolution.** For jp2a conversion, at least 600×600
   pixels for a face-only crop. Less than that produces blocky output.

## Pitfalls

- **Fan art of popular characters rarely matches the canonical design.** The smile,
   proportions, and texture are always different. Always verify.
- **The image search alt text says a character name but the image isn't that character.**
   Both WallpaperCave and DuckDuckGo had this problem for "Statue of God" searches
   returning non-Solo-Leveling or heavily stylized images.
- **Anime-style static wallpapers sometimes use AI generation.** The faces are
   recognizably different in structure. Prefer artist-credited work.
- **The webtoon/manhwa art style is black-and-white line art with grayscale shading.**
   If you're looking for a manhwa character, color fan art will look different after
   jp2a conversion than the high-contrast monochrome originals.