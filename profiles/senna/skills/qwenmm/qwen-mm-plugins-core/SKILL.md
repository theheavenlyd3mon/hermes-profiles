---
name: qwen-mm-plugins-core
description: Vision-Language MCP tools for reading/visualizing any file (images, videos, documents, code, data, 3D models, etc.) and calling VL APIs (caption, ASR, search, etc.).
---

# Qwen-MM-Plugins Core

You have `qwen-mm-plugins-core` MCP tools available. Use them to read and visualize any file (images, videos, documents, code, data, 3D models, notebooks, etc.) and to call vision-language APIs. Prefer these MCP tools over manual scripting.

Check the `qwen-mm-plugins-core` tools in your tool list for full schemas and parameters.

## When to Use Which Tool

Native reading (feeds content directly to you):
- **See a file** (PDF, Office, CSV, code, notebook, 3D, ...) → `visualize`
- **Read an image** with dynamic resolution → `read_image`
- **Read a video** (extract frames) → `read_video`
- **Get media metadata** (duration, resolution, fps, codecs, bitrate, audio/video/subtitle tracks, chapters) → `media_info`
- **Save specific frame(s)** of a video to file (for image_search) → `save_view` (pass `times=[...]`)

Producing / annotating (writes an image file):
- **Crop a rectangular region** from an image → `crop`
- **Draw bounding boxes** on an image (e.g. to visualize `grounding` output) → `draw_bbox`

External API calls (DashScope):
- **Call an external VLM** about images/videos → `vision_chat`
- **Transcribe speech** from audio/video → `transcribe_audio`
- **Detect/locate objects** in an image → `grounding`
- **Extract text** from an image → `ocr`
- **Segment objects** in an image → `segmentation`
- **Reverse image search** to identify an entity from a frame → `image_search`
- **Search the web** for facts → `web_search`
- **Read a web page** in depth → `web_extractor`

## Visualize — Supported Formats

| Category | Extensions | Notes |
|----------|-----------|-------|
| Documents | `.pdf`, `.svg` | Built-in (pypdfium2 + resvg) |
| Office | `.docx`, `.pptx`, `.vsdx` | Needs `libreoffice` |
| Data | `.csv`, `.xlsx` | Text table + chart image |
| Code | `.js`, `.ts`, `.py`, `.go`, `.rs`, `.md`, ... | Returns text (markdown code block) |
| Plain text | `.txt`, `.text`, `.log` | Returns text (fenced block) |
| Web pages | `.html`, `.htm`, `.mhtml` | Screenshot; needs `playwright` |
| Diagrams | `.drawio` | XML → SVG rendering |
| Subtitles | `.srt`, `.vtt` | Returns text |
| 3D Models | `.obj`, `.stl`, `.glb`, `.gltf`, `.fbx`, `.ply`, `.step`, `.stp` | Built-in; `blender` for best quality |
| GIS/Geo | `.geojson`, `.kml`, `.shp` | Built-in |
| Notebooks | `.ipynb` | Text cells + embedded images |
| LaTeX | `.tex` | Compiles to PDF; falls back to source on failure |
| Images/Videos | `.jpg`, `.mp4`, ... | Delegates to `read_image`/`read_video` |

Use `pages` for page ranges, `budget` for resolution, `max_pages` to cap output.

## Tips

**Resolution budgets**: `small` for preview, `normal` (~1024) default, `large` for fine detail.

**Video strategy**: `fps=0` auto-selects. Skim with `fps=1, budget="normal"` in 5-min chunks, then detail with `fps=2, budget="large"` on interesting segments. Use `start_time`/`end_time` for windowing. Before any editing/clipping task, run `media_info` first to learn the source properties (codecs, tracks, fps, rotation).

**Vision chat**: pass `images`/`videos` + `text` prompt. Default model `qwen3.7-plus`. Use `dry_run=true` to inspect payloads. Details in `references/vision_chat.md`.

**Video knowledge & search** (any video question that needs external knowledge — identify a specific thing, OR a fact about what's shown that you can't confirm from the frames alone): watch with `read_video` — for a long video do a low-fps overview first (~32 frames, `fps≈32/duration`) then zoom, and don't run `ffmpeg`/montage yourself — grab a frame with `save_view` (`times=[...]`), and you MUST confirm with `image_search` (reverse-search the frame) and/or `web_search` before answering — never commit from frames alone. Details in `references/video_search.md`.

**ASR**: accepts audio or video, auto-chunks long files. Formats: `srt` (default), `text`, `json`. Needs `DASHSCOPE_API_KEY`.

**Segmentation**: needs a SAM3 server (`SAM3_SERVER_URL`). To stand one up, run `references/launch_sam3_server.py` (multi-GPU HTTP server; see its header for prerequisites).