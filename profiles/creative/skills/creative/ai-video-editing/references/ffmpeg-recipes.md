# ffmpeg Recipes for AI Video Assembly

Verified commands from real edit sessions. All clips in these examples were
1280x704 @ 24fps (FLUX 3 output). Adjust W/H/fps to your sources.

## 0. Probe every source FIRST (never assume duration)
```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 clip.mp4
# resolution + fps:
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 clip.mp4
```
Generated clips are frequently 5.04s, not 5/6s. Build the beat grid on real numbers.

## 1. Ken Burns push-in (crop + frame variable `n`)
The reliable way to add a subtle camera move to an existing clip. `zoompan` does
NOT work on video input (it multiplies frames — a 3s clip became 216s). `crop`
has no `t`/time variable; it exposes `n` (frame number), so drive the move off `n`.

```bash
# $1=input  $2=start  $3=dur  $4=output   (assumes 24fps)
zin () {
  local frames=$(( $3 * 24 ))
  ffmpeg -y -v error -ss "$2" -t "$3" -i "$1" \
    -vf "crop=w='iw/(1+0.15*n/$frames)':h='ih/(1+0.15*n/$frames)',scale=1280:704:flags=lanczos" \
    -an -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -r 24 "$4"
}
```
`0.15` = 15% push over the shot (subtle "slow punch-in"). For a push-OUT (exhale),
invert the ramp: `crop=w='iw/(1.15-0.15*n/$frames)':h='ih/(1.15-0.15*n/$frames)'`.

## 2. Slow-mo to fill a target duration (+ trim + move)
When a clip is shorter than the beat needs, slow it. ALWAYS `trim=duration=` after
`setpts` or the slow-mo overshoots. Then re-anchor PTS and apply the move.
```bash
# 5.04s source -> exactly 6s, then punch-in over 144 frames (6s*24)
ffmpeg -y -v error -i src.mp4 \
  -vf "setpts=1.19*PTS,trim=duration=6,setpts=PTS-STARTPTS,crop=w='iw/(1+0.15*n/144)':h='ih/(1+0.15*n/144)',scale=1280:704:flags=lanczos" \
  -an -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -r 24 out.mp4
```
Note: slowing a clip that morphs (e.g. a spinning aerial) can HIDE the artifacts —
suspension masks spin warp. Slowing a near-static held pose is safest.

## 3. Concatenate (segments must share codec/res/fps/pix_fmt)
```bash
# filelist.txt: one  file 'NN.mp4'  line per segment, in order
ffmpeg -y -v error -f concat -safe 0 -i filelist.txt -c copy video_only.mp4
```

## 4. Mix the music track (trim to video length + fade-out tail)
```bash
VDUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 video_only.mp4)
FADE_START=$(echo "$VDUR - 2.5" | bc)
ffmpeg -y -v error -i video_only.mp4 -i track.mp3 \
  -filter_complex "[1:a]atrim=0:${VDUR},afade=t=out:st=${FADE_START}:d=2.5[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

## 5. Downscale a review copy (for video_analyze / quick QA)
Large or audio-bearing files break the analysis API. Make a light copy:
```bash
ffmpeg -y -v error -i final.mp4 -vf "scale=640:-2" -c:v libx264 -crf 30 -preset fast \
  -c:a aac -b:a 64k review.mp4
```
If the model rejects audio, strip it entirely: `-an -c:v copy review.mp4`.

## 6. RMS energy envelope — find the drops/breakdowns in a track
Decode to raw PCM, then compute per-window RMS to map quiet (breakdown) vs loud
(drop) sections. Snap key visuals to the drop hits and the breakdown.
```bash
ffmpeg -y -v error -i track.mp3 -ac 1 -ar 22050 -f s16le raw.pcm
```
Then in Python (stdlib only — `audioop` was removed in 3.13): read 16-bit mono,
window at 0.5s, RMS = sqrt(mean(sample^2)), normalize, print an ASCII bar per
second, and flag sharp onsets (rise > ~0.22 from a local low < ~0.55) as drop hits.
A full working script lived at `04_audio/analyze.py` in the snowboard project.
Typical pop/action structure it surfaces: quiet intro → DROP #1 → sustained energy
→ BREAKDOWN (drums cut) → DROP #2 (hardest) → outro fade.

## 7. Verify copies before deleting originals (md5)
```bash
[ "$(md5 -q src)" = "$(md5 -q dst)" ] && echo OK || echo MISMATCH
```
Only delete a source once its organized copy is confirmed byte-identical.

## 8. Detect + remove baked-in letterbox bars
Some generated clips (esp. FLUX 3 aerials) ship with cinematic black bars baked
in, so they shift aspect ratio mid-edit. First MEASURE the bars with cropdetect —
note it logs at INFO level, so don't use `-v error`, and grep the `crop=` output:
```bash
ffmpeg -i src.mp4 -vf "cropdetect=24:2:0" -frames:v 90 -f null - 2>&1 \
  | grep -o 'crop=[0-9:]*' | sort | uniq -c | sort -rn | head -3
# -> e.g. "crop=1280:544:0:80"  =  W:H:X:Y  (here 80px bars top AND bottom)
```
Then crop to the content region and scale back to project res (1280x544 -> 1280x704):
```bash
ffmpeg -y -v error -i src.mp4 \
  -vf "crop=1280:544:0:80,scale=1280:704:flags=lanczos" \
  -an -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -r 24 out.mp4
```
Chain this BEFORE any slow-mo/move so later filters see clean full-frame pixels.
To also drop a dead lead-in (e.g. ~1s of empty sky before the subject enters),
add `trim=start=1:end=5,setpts=PTS-STARTPTS` after the crop+scale.

## 9. Title cards / on-screen text (when drawtext is unavailable)
Some ffmpeg builds ship WITHOUT the `drawtext` filter (check first:
`ffmpeg -filters | grep drawtext`). If you call drawtext and it's missing, ffmpeg
errors "No such filter: 'drawtext'". The DANGEROUS case: if your command also
produces a plain black background (e.g. `color=` source with drawtext chained),
the filter failure can leave you a clean BLACK FRAME with no text — the segment
encodes fine, the concat works, and you only notice on visual QA.

FIX: render the title as a PNG with Pillow, then loop it into a segment:
```python
from PIL import Image, ImageDraw, ImageFont
img = Image.new("RGB", (W,H), (0,0,0)); d = ImageDraw.Draw(img)
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 44)
spaced = "   ".join("THE EVOLUTION")   # manual letter-spacing = cinematic tracked-out look
bbox = d.textbbox((0,0), spaced, font=font)
d.text(((W-(bbox[2]-bbox[0]))//2-bbox[0], (H-(bbox[3]-bbox[1]))//2-bbox[1]),
       spaced, font=font, fill=(245,245,245))
img.save("title.png")
```
```bash
ffmpeg -y -v error -loop 1 -i title.png -t 2.0 -vf "scale=1280:704:flags=lanczos" \
  -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -r 24 title_seg.mp4
```
VERIFY text actually rendered (never trust the encode alone) — count bright pixels
in a decoded frame; pure black = 0%, a tracked-out title ≈ 0.3–0.5%:
```python
raw = subprocess.run(["ffmpeg","-v","error","-i","title_seg.mp4","-frames:v","1",
    "-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
bright = sum(1 for i in range(0,len(raw),3) if raw[i] > 60)
print(100*bright/(len(raw)//3), "% bright")   # 0.0 == text FAILED to render
```
Run this bright-pixel check on EVERY title/text card before the final concat. It
also catches any silent filter failure on a generated background.
