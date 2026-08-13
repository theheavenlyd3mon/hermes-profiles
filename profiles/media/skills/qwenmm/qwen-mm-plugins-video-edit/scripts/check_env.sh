#!/usr/bin/env bash
# check_env.sh — environment self-check for video-edit.
# Run before first use (or when something fails). Reports each dependency as
# OK / MISSING / WARN with install hints. Exit code = number of hard misses.
#
# Usage: check_env.sh
set -uo pipefail
MISS=0

ok()   { printf "  OK      %s\n" "$1"; }
warn() { printf "  WARN    %s\n" "$1"; }
miss() { printf "  MISSING %s\n" "$1"; MISS=$((MISS+1)); }

echo "== Core (hard requirements) =="

if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then
  ok "ffmpeg/ffprobe ($(ffmpeg -version 2>/dev/null | head -1 | awk '{print $3}'))"
else
  miss "ffmpeg/ffprobe — macOS: brew install ffmpeg | Debian: sudo apt install ffmpeg"
fi

if command -v python3 >/dev/null; then
  if python3 -c "import PIL, numpy" >/dev/null 2>&1; then
    ok "python3 + PIL + numpy ($(command -v python3))"
  else
    miss "python3 PIL/numpy — pip3 install pillow numpy (needed by timeline_view.py)"
  fi
else
  miss "python3 — macOS: brew install python3"
fi

echo
echo "== Beat sync (needed only for music-beat-sync work) =="

LIBROSA_PY=""
for PY in python3 "$HOME/miniconda3/bin/python" /opt/homebrew/bin/python3; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c "import librosa, scipy" >/dev/null 2>&1; then
    LIBROSA_PY="$PY"; break
  fi
done
if [ -n "$LIBROSA_PY" ]; then
  ok "librosa+scipy via: $LIBROSA_PY  (use this interpreter for beat_grid.py)"
elif command -v uv >/dev/null; then
  warn "librosa not installed in any known python — beat_grid.py falls back to:
          uv run --with librosa --with scipy --python 3.11 beat_grid.py ...
          (slow on throttled networks; better: pip install librosa once)"
else
  miss "librosa (and no uv fallback) — pip install librosa, or install uv"
fi

echo
echo "== HyperFrames handoff (designed deliverables) =="

if command -v node >/dev/null; then
  NODE_MAJOR=$(node -v | sed 's/v\([0-9]*\).*/\1/')
  if [ "$NODE_MAJOR" -ge 22 ]; then ok "node $(node -v) (>=22)"; else miss "node >=22 (found $(node -v)) — upgrade Node.js"; fi
else
  miss "node — install Node.js >=22"
fi
command -v npm >/dev/null && ok "npm ($(npm -v))" || miss "npm (ships with Node.js)"
command -v npx >/dev/null && ok "npx ($(npx -v))" || miss "npx (ships with Node.js)"

if command -v hyperframes >/dev/null; then
  HF_VERSION=$(hyperframes --version 2>/dev/null | head -1)
  ok "hyperframes CLI${HF_VERSION:+ ($HF_VERSION)}"
elif command -v npm >/dev/null; then
  HF_TMP=$(mktemp)
  if npm exec --offline --yes --package hyperframes -- hyperframes --version >"$HF_TMP" 2>/dev/null; then
    HF_VERSION=$(head -1 "$HF_TMP")
    ok "hyperframes CLI via npm cache${HF_VERSION:+ ($HF_VERSION)}"
  else
    warn "hyperframes CLI not available offline — run: npx -y hyperframes doctor (if TLS fails, set NODE_EXTRA_CA_CERTS for your intranet CA)"
  fi
  rm -f "$HF_TMP"
else
  warn "hyperframes CLI not checked — npm is missing"
fi

if [ "${NODE_TLS_REJECT_UNAUTHORIZED:-}" = "0" ]; then
  warn "NODE_TLS_REJECT_UNAUTHORIZED=0 is set — insecure; use only for temporary intranet TLS interception workarounds"
elif [ -n "${NODE_EXTRA_CA_CERTS:-}" ]; then
  ok "NODE_EXTRA_CA_CERTS set ($NODE_EXTRA_CA_CERTS)"
else
  warn "Node extra CA not set — if GitHub downloads fail with SELF_SIGNED_CERT_IN_CHAIN, set NODE_EXTRA_CA_CERTS for your intranet CA"
fi

CHROME_FOUND=""
for C in "${PUPPETEER_EXECUTABLE_PATH:-}" \
         "$(command -v chrome-headless-shell 2>/dev/null || true)" \
         "$(command -v chromium 2>/dev/null || true)" \
         "$(command -v chromium-browser 2>/dev/null || true)" \
         "$(command -v google-chrome 2>/dev/null || true)"; do
  if [ -n "$C" ] && [ -x "$C" ]; then CHROME_FOUND="$C"; break; fi
done
if [ -z "$CHROME_FOUND" ]; then
  HF_BROWSER_TMP=$(mktemp)
  if command -v hyperframes >/dev/null && hyperframes browser path >"$HF_BROWSER_TMP" 2>/dev/null; then
    HF_BROWSER_PATH=$(tail -1 "$HF_BROWSER_TMP")
    [ -n "$HF_BROWSER_PATH" ] && [ -x "$HF_BROWSER_PATH" ] && CHROME_FOUND="$HF_BROWSER_PATH"
  elif command -v npm >/dev/null && npm exec --offline --yes --package hyperframes -- hyperframes browser path >"$HF_BROWSER_TMP" 2>/dev/null; then
    HF_BROWSER_PATH=$(tail -1 "$HF_BROWSER_TMP")
    [ -n "$HF_BROWSER_PATH" ] && [ -x "$HF_BROWSER_PATH" ] && CHROME_FOUND="$HF_BROWSER_PATH"
  fi
  rm -f "$HF_BROWSER_TMP"
fi
if [ -n "$CHROME_FOUND" ]; then
  ok "Chrome/Chromium ($CHROME_FOUND)"
else
  warn "Chrome Headless Shell not found — run: npx -y hyperframes browser ensure (if TLS fails, set NODE_EXTRA_CA_CERTS for your intranet CA)"
fi

GSAP_ROOT="${HF_PROJECT_DIR:-$PWD}"
if [ -f "$GSAP_ROOT/assets/gsap.min.js" ]; then
  ok "GSAP vendored ($GSAP_ROOT/assets/gsap.min.js)"
elif [ -f "$GSAP_ROOT/node_modules/gsap/dist/gsap.min.js" ]; then
  warn "GSAP installed but not vendored — copy node_modules/gsap/dist/gsap.min.js to assets/gsap.min.js"
elif [ -f "$GSAP_ROOT/package.json" ]; then
  warn "GSAP not installed in $GSAP_ROOT — run: npm install gsap && mkdir -p assets && cp node_modules/gsap/dist/gsap.min.js assets/gsap.min.js"
else
  warn "GSAP is project-local — in a HyperFrames project run npm install gsap and vendor assets/gsap.min.js"
fi

if [ "${QMP_CHECK_HYPERFRAMES_DOCTOR:-0}" = "1" ]; then
  if npx -y hyperframes doctor; then ok "hyperframes doctor"; else warn "hyperframes doctor failed — see output above"; fi
else
  echo "  NOTE    set QMP_CHECK_HYPERFRAMES_DOCTOR=1 to run 'npx hyperframes doctor' (may download)"
fi

echo
echo "== MCP services (verify in the AGENT runtime, not this shell) =="
echo "  NOTE    perception: read_video/read_image/visualize/transcribe_audio/vision_chat"
echo "  NOTE    generation: qwen_image/qwen_tts/wan_t2v/happyhorse/wan_s2v"
echo "  NOTE    a local schema file is NOT proof of availability — check the live tool list"

echo
[ -n "${DASHSCOPE_API_KEY:-}" ] && ok "DASHSCOPE_API_KEY set (len ${#DASHSCOPE_API_KEY})" \
  || warn "DASHSCOPE_API_KEY not set in this shell — this checks the shell only; DashScope-backed MCP tools also read it from ~/.qwen-mm-plugins/config (DASHSCOPE_API_KEY=sk-...)"

echo
if [ "$MISS" -eq 0 ]; then echo "RESULT: all hard requirements satisfied ($MISS missing)"; else echo "RESULT: $MISS hard requirement(s) missing — fix before editing work"; fi
exit "$MISS"
