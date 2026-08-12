# Build & Export Scaffold (code lane) — working recipe

Companion to the SKILL.md "Assemble + export" step. Distilled from a verified,
runnable `manuscript_pipeline/` CLI that assembles per-chapter Markdown into
EPUB + PDF + TTS-tagged SSML. This file carries the *technique* and the two
non-obvious bugs that cost real debugging time — copy the structure, not the
exact paths (the scaffold lives at `manuscript_pipeline/` in the session that
produced this note).

## Pipeline shape (one command does everything)
```
manuscript/{project}/
  manifest.yaml          # title/author + tts.voices map
  chapters/01_*.md … NN_*.md   # ordered lexicographically (zero-pad)
  characters.md, plot_ledger.md, worldbuilding.md   # reference/state
  assets/cover.png, style.css
        │  manuscript build <project> --all
        ▼
[load] manifest + glob chapters (sorted by name)
[assemble] front matter, TOC, heading normalize, parse tts: tags
[export] manuscript.md (master) → ebooklib EPUB3 → pandoc PDF
[tts]    emit tts/manifest.json + per-segment *.ssml.xml
```

## Library choices (and why)
| Stage | Lib | Note |
|------|-----|------|
| CLI | `click`/`typer` | pure Python |
| MD parse | `markdown-it-py` + `mdit-py-plugins` (front_matter) | token AST |
| EPUB | `ebooklib` | EPUB3 + nav + metadata + cover |
| PDF | `pandoc` + portable engine | **see gotcha #1** |
| TTS out | `edge-tts` (optional) | pipeline only *emits* SSML |
| misc | `jinja2`, `rich`, `tqdm`, `bs4`/`lxml` | polish |

## Gotcha #1 — PDF on Windows: avoid WeasyPrint, use pandoc + portable engine
WeasyPrint depends on native cairo / Pango / GDK-PixBuf that **pip cannot install
on Windows**. A clean Windows box can't `pip install weasyprint` into a working
state without a separate MSYS2/GTK install. Reproducible fix: bundle a portable
`wkhtmltopdf.exe` (single ~30 MB exe) or point at headless Chrome, and drive it
via `pandoc`:
```python
# default engine: wkhtmltopdf. engine="chrome" -> --headless --print-to-pdf
cmd = [exe, "--quiet", "-c", css, str(master_md), str(out_pdf)]
subprocess.run(cmd, check=True)
```
Resolution order in code: explicit `pdf.engine_path` → `shutil.which(engine)`
→ clear "install or set path" error. Never assume WeasyPrint works on Windows.

## Gotcha #2 — ebooklib/lxml: "Unicode strings with encoding declaration…"
Passing a `str` that contains `<?xml version="1.0" encoding="utf-8"?>` to
`epub.EpubHtml(content=...)` makes lxml raise
`ParserError: Unicode strings with encoding declaration are not supported.
Please use bytes input or XML fragments without declaration.`
It only triggers when the body actually exercises lxml (e.g. a `©` or non-ASCII
in the title page) — silent until then. Fix:
```python
_CHAP_TPL = Template("""<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{{ title }}</title></head><body><h1>{{ title }}</h1>{{ body }}</body></html>""")
# NO <?xml ?> declaration — ebooklib writes its own. Pass bytes:
epub.EpubHtml(uid="ch01", file_name="ch01.xhtml",
              content=_CHAP_TPL.render(...).encode("utf-8"))
```
Also: title page must not emit a duplicate `<h1>` (template already renders one).

## TTS tagging convention (MD-native, tool-agnostic)
Place a comment immediately before the spoken block:
```markdown
<!-- tts: speaker=Elara emotion=angry cue=shout -->

"Get back here!" she shouted.
```
Keys: `speaker` (name or `NARRATOR`), `emotion`, `cue` (-> prosody hint),
`lang`, `rate`, `pitch`, `role`. A chapter `speaker:` front-matter becomes the
default for untagged blocks; else `NARRATOR`. Resolve `speaker -> voice` from
`manifest.tts.voices`; unknown speakers fall back to `tts.default_voice`.

The tagger pairs each `<!-- tts: … -->` with the next non-empty block, builds a
`TTSBlock`, then **strips the comments from the publishable prose** so they don't
leak into EPUB/PDF. Output per segment:
```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en">
  <voice name="en-US-JennyNeural"><prosody volume="loud">(urgent) "Get up!"</prosody></voice>
</speak>
```
`cue=shout|angry` -> `volume="loud"`; `emotion` is prepended as `(emotion) `
(parenthesis cue works with edge-tts). `manifest.json` is the hand-off artifact
for a later `edge-tts` loop (iterate segments in order, concat audio).

## Output contract (`_build/`)
```
_build/manuscript.md              # assembled master (feeds pandoc)
_build/<title>.epub
_build/<title>.pdf                # skipped with clear msg if no engine
_build/tts/manifest.json          # [{id, chapter, speaker, voice, emotion,
                                   #   cue, text, ssml_path, est_chars}]
_build/tts/segment_NNNN.ssml.xml
```

## Windows-specific hardening (verify before shipping)
- `PYTHONUTF8=1` so `print()` of curly quotes/emoji never mojibakes in `cmd.exe`.
- `pathlib.Path` everywhere; lowercase `.md` chapters (case-insensitive glob).
- `shutil.which("pandoc")`; fail clearly if missing.
- Long-path: keep `segment_NNNN` ids short; warn near 260 chars.
- PyInstaller: `collect_binary` for `pandoc.exe`/`wkhtmltopdf.exe` so they unpack
  at runtime.

## Verify (the checks that caught the bugs)
- `epub.write_epub` succeeds AND every `*.xhtml` + `nav.xhtml` parses as XML
  (zipfile + `xml.dom.minidom.parseString` on each entry).
- `build --all` PDF stage must skip gracefully (not crash) when no engine is
  installed — assert the "not on PATH" message, not a traceback.
- `tts-check`: every speaker resolves to a voice; report unresolved ones.
