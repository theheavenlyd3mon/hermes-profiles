# Character Intro Montage Techniques

Reusable implementation notes for character-introduction edits that combine film-reel browsing, freeze-frame emphasis, subject cutouts, brush banners, and beat-synced accents. These are technique notes, not a project log: keep them generic, portable, and independent of any local workspace.

## Film-reel carousel

Drive the whole reel with one horizontal strip coordinate. Each thumbnail occupies a fixed slot; centering any target clip is a deterministic offset calculation.

```python
slot_stride = thumb_width + gap
target_left = target_slot * slot_stride
strip_x = frame_center_x - thumb_width / 2 - target_left
```

Animate `strip_x` with smoothstep or an ease-out curve so the reel feels like it decelerates into the selected slot.

```python
def smoothstep(x):
    return 3 * x * x - 2 * x * x * x

strip_x = start_x + (end_x - start_x) * smoothstep(progress)
```

Once the target slot lands, interpolate that thumbnail's rectangle into the full-frame rectangle while fading the surrounding reel. This keeps the expansion motivated by the selected clip rather than feeling like a separate zoom effect.

```python
p = ease_out(progress)
x = thumb_x * (1 - p)
y = thumb_y * (1 - p)
w = thumb_w + (canvas_w - thumb_w) * p
h = thumb_h + (canvas_h - thumb_h) * p
```

Keep thumbnails alive by sampling short looping frame sequences instead of using static stills. A reel with moving thumbnails reads as footage browsing; static thumbnails read as a slideshow.

## Cutout outline

For sticker-style subject emphasis, build the keyline from the subject alpha rather than drawing a manual stroke.

1. Extract the subject as an RGBA image or alpha video.
2. Dilate the alpha mask by the desired outline width.
3. Subtract the original alpha from the dilated alpha.
4. Paint the resulting ring and composite it behind the subject.

For Pillow-style dilation, the max-filter size should be odd and roughly tied to the target outline width:

```python
filter_size = outline_px * 2 + 1
dilated_alpha = alpha.filter(ImageFilter.MaxFilter(filter_size))
outline_mask = dilated_alpha - alpha
```

This keeps the outline tied to the real silhouette and works across hair, shoulders, hands, props, and clothing edges. Always check the outline over both bright and dark backgrounds; white keylines that look clean on a dark test frame may disappear over pale footage.

## Brush-banner matting

For generated brush strokes on a white background, use continuous alpha from the pixel's distance from white instead of a hard threshold:

```python
min_channel = min(r, g, b)
alpha = 255 * (1 - min_channel / 255)
```

Continuous alpha preserves soft ink edges and semi-dry brush texture. Hard thresholds usually create jagged edges or gray halos. After matting, inspect the banner on at least one light frame and one dark frame before using it in a render.

Use brush banners as layout devices, not explosions: place them in negative space, size them to the text they carry, and reveal them along the stroke direction. Let the text land after the brush, then add small accents such as a seal or underline only if the frame still has breathing room.

## Shared beat metadata

When both picture and sound design need exact timing, write key moments once into a metadata file, then let the video renderer and audio generator read the same timestamps. Do not re-estimate the same beat positions in two different scripts.

Useful fields include:

```json
{
  "freeze_times": [3.35, 8.45],
  "slide_windows": [[0.0, 1.2], [5.1, 6.0]],
  "accent_times": [3.35, 8.45]
}
```

The video pass can use `freeze_times` for still holds and emphasis devices; the audio pass can place drops, bells, whooshes, or impacts on the same timestamps. Because both tracks consume one source of truth, the rendered cut and generated SFX cannot drift unless the metadata itself changes.

## Face-safe layout

Character-introduction cards usually need two clear zones:

- subject zone: face, body, action, and cutout silhouette;
- information zone: name, role, tag, brush banner, badge, and secondary copy.

Do not center banners over the subject. A reliable layout is text/banner on one side and subject on the other, with the cutout allowed to overlap the background but not the title block. If a moving label or ring participates in the action, verify the exact rendered frame where it is closest to the face.

## Verification checklist

- Reel: target slot lands centered before expansion begins.
- Expansion: thumbnail rectangle visually motivates the full-frame transition.
- Cutout: outline follows the silhouette without halos or jagged gaps.
- Brush: white background is fully removed while soft ink edges remain.
- Timing: visual freeze/accent and audio hit read from the same metadata.
- Occlusion: titles, banners, rings, and labels never cover faces.
- Render truth: verify these checks from rendered frames, not only from the plan or source assets.
