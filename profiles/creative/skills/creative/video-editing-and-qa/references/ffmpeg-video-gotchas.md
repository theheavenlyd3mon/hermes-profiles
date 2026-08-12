# ffmpeg + video_analyze Gotchas (transcripts)

Exact errors seen in production and the one-line fix for each. Recognize the message,
apply the fix — don't retry identical bytes.

## video_analyze rejects generator audio
FLUX 3 clips carry a baked-in audio track. Gemini's video backend has no audio modality:
```
Error code: 400 - 'Audio input modality is not enabled for this model'
provider_name: Google AI Studio
```
FIX — strip audio into a review copy (stream copy, fast):
```
ffmpeg -y -v error -i in.mp4 -an -c:v copy review.mp4
```

## video_analyze: file too heavy
Two flavors, same cause (file too large / slow to fetch):
```
Error code: 400 - 'Download multimodal file timed out'
Error code: 413 - 'Request body size exceeds maximum allowed size'
```
FIX — make a small proxy and analyze that:
```
ffmpeg -y -v error -i in.mp4 -an -vf "scale=640:-2" -c:v libx264 -crf 30 -preset fast proxy.mp4
```
A 5–10MB clip → ~100–200KB. A 20s 1080p edit → ~700KB–2MB (still fine).
If one file keeps timing out after a retry, re-encode it SMALLER (crf 32, scale 480) —
the bytes themselves are the problem, not the network.

## zoompan destroys video timing
`zoompan` is image-oriented: with video input it applies the frame count PER INPUT FRAME,
so a 3s/72-frame clip at d=72 renders as 72×72 = 5184 frames ≈ 216s. Symptoms: output
duration wildly wrong (3s→216s, 5s→600s), huge files, and the build times out.
FIX — don't use zoompan for video. Use crop+scale (below).

## crop filter has no time variable
Driving a crop-based Ken Burns with `t` fails:
```
[Parsed_crop_0] Error when evaluating the expression 'ih/(1+0.15*t/3)'
[Parsed_crop_0] Failed to configure input pad
```
The crop filter exposes `n` (frame number) and `pos`, NOT `t` (time).
FIX — drive the push with `n`, precompute total frames:
```
FRAMES=$(( DURATION_SECONDS * FPS ))
ffmpeg -y -ss START -t DUR -i in.mp4 \
  -vf "crop=w='iw/(1+0.15*n/$FRAMES)':h='ih/(1+0.15*n/$FRAMES)',scale=1280:704:flags=lanczos" \
  -an -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -r 24 out.mp4
```
Verified: 3s @24fps → exactly 3.000s / 72 frames. Push-in = `+0.15*n/FRAMES`;
push-out (exhale) = `+0.15*(FRAMES-n)/FRAMES`. Keep the magnitude ~0.15 (15%) for
"feel not see."

## BFL FLUX 3 submission rate limit
```
BFL submissions are limited to one attempt per minute. Wait N seconds...
```
FIX — serialize generations with a ~45–60s sleep between submissions. (A transient
504 "Azure Front Door / OriginTimeout" can also appear — just wait and resubmit.)
