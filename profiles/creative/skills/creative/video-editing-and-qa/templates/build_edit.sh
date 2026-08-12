#!/bin/bash
# Beat-grid edit builder. Copy, then edit the SHOTS table + paths.
# Each shot: source file, in-point (-ss), duration (-t), optional slow push-in.
# Concatenates, then lays the music track under with a fade-out.
set -e
cd "$(dirname "$0")/.."   # run from project root

CLIPS=01_raw_clips
AUDIO=04_audio/track.mp3
OUT=02_final_edits/final.mp4
FPS=24
mkdir -p build

# --- Ken Burns slow push-in (15%), crop-based, frame-driven. See references. ---
#   zin <input> <start_s> <dur_s> <output> [push]   push=in(default)|out
zin () {
  local in="$1" ss="$2" dur="$3" out="$4" push="${5:-in}"
  local frames=$(( dur * FPS ))
  local expr
  if [ "$push" = "out" ]; then expr="0.15*($frames-n)/$frames"; else expr="0.15*n/$frames"; fi
  ffmpeg -y -v error -ss "$ss" -t "$dur" -i "$in" \
    -vf "crop=w='iw/(1+$expr)':h='ih/(1+$expr)',scale=1280:704:flags=lanczos" \
    -an -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -r $FPS "$out"
}
# --- No-motion variant (hard static shot) ---
static () {
  ffmpeg -y -v error -ss "$2" -t "$3" -i "$1" \
    -vf "scale=1280:704:flags=lanczos" \
    -an -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -r $FPS "$4"
}

# ===== SHOTS — edit this block to your cut map =====
# zin <file> <in-point> <duration> <build/n.mp4> [in|out]
zin "$CLIPS/shot1.mp4" 0 3 build/1.mp4
zin "$CLIPS/shot2.mp4" 0 5 build/2.mp4
zin "$CLIPS/shot3.mp4" 3 3 build/5.mp4      # in-point at 3s into the clip
zin "$CLIPS/outro.mp4" 0 4 build/9.mp4 out  # push OUT = exhale
# ===================================================

# Build the concat list from whatever build/*.mp4 exist, in numeric order
: > build/filelist.txt
for f in $(ls build/[0-9]*.mp4 | sort -V); do echo "file '$(basename "$f")'" >> build/filelist.txt; done

ffmpeg -y -v error -f concat -safe 0 -i build/filelist.txt -c copy build/video_only.mp4
VDUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 build/video_only.mp4)
echo "Video duration: ${VDUR}s"

FADE_START=$(echo "$VDUR - 2.5" | bc)
ffmpeg -y -v error -i build/video_only.mp4 -i "$AUDIO" \
  -filter_complex "[1:a]atrim=0:${VDUR},afade=t=out:st=${FADE_START}:d=2.5[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "$OUT"

echo "Done: $OUT"
ls -la "$OUT"
