# v0.20.0 creative/video what's-new — worked example (2026-08)

Context: user ran `hermes update`, asked "what was added regarding creativity and video?"
Local state found: `Hermes Agent v0.20.0 (2026.8.3)`, install dir `~/.hermes/hermes-agent`, git install, `Up to date` (checkout on latest main, ~1050 commits past the tag).

## Video — FLUX3 via Nous Portal (in v0.20.0, commits ~Jul 30)
- `07447bd5d` nous portal video gen (#74963) — core FLUX3 video gen through Nous Portal
- `4a798f4bc` improve polling for FLUX3 video gen (#75010)
- `97c6a183a` auto populate flux3 in tools for nous portal users
- `4c7cc62f9` flux3 messaging system fixes
- `061b04ebb` fix video delivery
- `126ff7071` Portal free user vision fix + flux3 polling improvements (#75448)

## Video — FAL families + upscaling (POST-tag, Aug 7-8, on main only — not in release notes)
- `70c6cf8e7` feat: add new FAL video families and image models (Aug 8)
  - Video (plugins/video_gen/fal): **Seedance 2.5, MiniMax H3, Seedance 2.0 Mini, FLUX 3, Grok Imagine 1.5, Gemini Omni Flash (i2v-only)**. New family capability flags: `duration_int`, `resolution_aliases` (maps 720p/1080p onto H3's 768P/2K/4K enums), `image_drop_keys` (strips `aspect_ratio` for Seedance 2.5 / H3 / Grok 1.5 i2v).
  - Image (tools/image_generation_tool): **Seedream 5.0 Pro (+edit) / Lite, Ideogram V4 instant + fast, Qwen Image 3 (+edit), MAI Image 2.5 Pro, Nano Banana 2 Lite (+edit), Recraft V4.1**
  - 18/18 endpoints live-tested against fal.run (t2v, i2v, t2i, edit probes).
- `137960c9a` feat(media): opt-in upscale pass for image_generate and video_generate across FAL and Krea
- `66ea4e686` feat(media): default-on upscaling for sub-2MP image models (FAL + Krea)
- `05330e804` fix(video): bind managed SeedVR to source request (SeedVR upscaler)
- `9eb3ac50f` / `b7eb97a83` — terminal-backend reads via shared media resolver; chunk-by-chunk download caps

## Creativity
- Comfy Cloud MCP catalog entry with curated 20-tool default (#66112) — user runs ComfyUI Cloud
- comfyui skill script fixes: `36f73df13` (BOM-tolerant workflow-JSON reads), `50f742f8e` (UTF-8 pinning)
- Skills tree debloat: heartmula, audiocraft → optional-skills
- New `social-media-content-calendar` skill (Aug 4; tightened/hardline, optional Aug 8)
- Desktop artifacts — sandboxed live preview rail for generated HTML/apps

## Post-tag wave (Aug 8-10, second review session — on main only)
- `e166159f2` feat(vision): `region` param on vision_analyze — Pillow crop BEFORE downscale, full-res zoom for small text/UI details (ported from QwenLM/qwen-code)
- `227805625` feat(vision): disclose downscale factor + crop offset for coordinate mapping (computer_use + vision_tools)
- `b7eb97a83` fix(vision): stream downloads chunk-by-chunk with running size cap (OOM guard on missing Content-Length)
- `89c14aeb9` fix(read_file): EXTRACTION COVERAGE WARNING when PDF pages yield no text (scanned docs) — recovery = pdftoppm + vision_analyze or ocr skill
- `a607b7628` render notebook outputs in read_file ipynb extraction (port from lobehub)
- `238351a60` gateway container->host media translation widened (home + cache mounts); `271867f6f`/`e52acf76a` bound media history workers off event loop
- `c8fdc5174` desktop renders remote PDFs in preview rail; `3c4f5c521` desktop recovers image attach after stale session drop
- `422733667` skills-hub falls back to live repo for optional skills missing from local checkout
- Mass skill install observed same day: whole `mengto/` web-design suite (82), codex (19), media/ui (3), higgsfield (8), qwenmm (2), productivity (8), apple iOS (4) — see skills_list for full inventory

## Caveats learned
- **FAL 409 from Nous Portal proxy**: several new FAL endpoints return HTTP 409 from the Nous Portal FAL proxy allowlist until it updates portal-side. BYOK `FAL_KEY` works today; existing 4xx guidance message covers it. Verify with a live probe before promising a new family.
- Patch tags (v2026.7.30) may say "full curated release notes will ship with v0.20.0" — the window IS rolled into the next minor's notes.
