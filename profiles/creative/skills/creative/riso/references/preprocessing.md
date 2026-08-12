# Image Preprocessing for ASCII Conversion

Session-specific techniques and code patterns for preparing source images before running through the riso pipeline. All code uses Pillow (PIL) + NumPy.

## Core Insight

The pipeline's `_map_intensity()` maps pixel brightness 0–255 linearly to character indices:

```python
pixels = np.array(img, dtype=np.float32) / 255.0  # 0–1
n = len(charset)  # 12 for stroke-clarity, 68 for d30-dense
indices = np.minimum(np.floor(pixels * n), n - 1).astype(np.uint8)
```

**Black (0) → index 0 → `@`** (darkest character). Pure black backgrounds render as `@` fill, not space.

**White (255) → index n-1 → `.`** (lightest character). White backgrounds render as near-invisible dots.

## Preprocessing Pattern

```python
from PIL import Image, ImageFilter
import numpy as np

img = Image.open('source.png').convert('RGB')
arr = np.array(img)
gray = np.mean(arr, axis=2)

# 1. Find threshold — check histogram for valley between bg peak and fg peak
hist, bins = np.histogram(gray, bins=60)
# Background peak is at the dark end; subject peak is brighter

# 2. Create mask (True = subject pixels to keep)
mask = gray > threshold  # typical threshold: 50–65 for dark-bg portraits

# 3. Replace background with white (255)
result = np.full_like(arr, 255)
for c in range(3):
    result[:,:,c] = np.where(mask, arr[:,:,c], 255)

# 4. Median filter to clean mask boundary
out = Image.fromarray(result.astype(np.uint8))
out = out.filter(ImageFilter.MedianFilter(3))
out.save('preprocessed.png')
```

## Session Example: Dark Background Portrait

**Source:** 1152×1920 portrait, character (white hair, dark mask, black jacket) against dark gradient sky + snowy mountains. Character positioned off-center right.

**Crop strategy:**
- Locate character via edge-density peak: find the 50×50 block with highest mean edge value
- Tight crop around face: `(720, 230, 1050, 580)` → 330×350 (head + shoulders)
- Broader upper-body crop: `(500, 50, 1152, 750)` → 652×700

**Crop code:**
```python
# Edge detection to find character position
from PIL import ImageFilter
edges = img.convert('L').filter(ImageFilter.FIND_EDGES)
earr = np.array(edges)
# Find rows/columns with most edge content
edge_density_rows = [earr[y:y+50, :].mean() for y in range(0, h-50, 50)]
peak_row = np.argmax(edge_density_rows) * 50
edge_density_cols = [earr[:, x:x+50].mean() for x in range(0, w-50, 50)]
peak_col = np.argmax(edge_density_cols) * 50
```

**Threshold value:** 50–55 for tight face crop, confirmed by histogram analysis showing background peak at brightness 38–42.

**Results with `stroke-clarity --scale 2` (96×48):**
- `high-contrast` verdict ✅
- fill_ratio: 0.675 (32% space from white background)
- heavy_ratio: 0.311 (good character density)
- Character silhouette clearly discernible: face, white hair, mask, jacket

## Edge Cases

| Situation | Adjustments |
|-----------|-------------|
| Subject has bright elements (white hair) against dark bg | Low threshold works well (45–55) — the bright subject is well above bg noise |
| Subject has dark elements against dark bg | May need higher threshold (60–80). Consider boosting contrast on source first: `ImageEnhance.Contrast(img).enhance(1.5)` |
| Background contains stars/noise | MedianFilter(3) or MedianFilter(5) after thresholding cleans specular artifacts |
| Multiple brightness peaks in subject | Try Otsu threshold or use edge-density for crop then per-patch threshold |
| Source is already on white/transparent bg | No preprocessing needed — run directly. Check fill_ratio; if near 1.0, bg may not actually be white |
