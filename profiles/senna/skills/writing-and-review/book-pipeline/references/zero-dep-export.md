# Zero-dependency export (stdlib only) — CANONICAL (locked 2026-07-08)

**Canonical assembler:** `~/book-writer-pipeline/`  
(ebooklib/pandoc stack is DEPRECATED — see that tree's `DEPRECATED.md`.)

Emits valid EPUB + PDF + TTS tags using **only the Python standard library**
(Python 3.11+). No PyYAML, no reportlab, no network. Verified end-to-end on
macOS Python 3.14; designed for Windows parity.

## When to use
Always, unless the user explicitly wants covers/CSS/print-quality PDF and
accepts installing ebooklib + pandoc + wkhtmltopdf.

## EPUB via `zipfile` (EPUB 3, no library)
EPUB is just a ZIP with a fixed layout. Required pieces:
- `mimetype` — literally `application/epub+zip`, stored UNCOMPRESSED (ZIP_STORED),
  must be the first entry.
- `META-INF/container.xml` — points to `OEBPS/content.opf`.
- `OEBPS/content.opf` — package manifest + spine.
- `OEBPS/nav.xhtml` — the TOC (`<nav epub:type="toc">`).
- One `OEBPS/chap_NN.xhtml` per chapter.

Template constants that don't change:
```python
MIMETYPE = "application/epub+zip"
CONTAINER = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""
```
Write all other members with `ZIP_DEFLATED`. Use `xml.sax.saxutils.escape`
for any text dropped into XML; build manifest `<item>` + spine `<itemref>`
per chapter.

## PDF via hand-rolled writer (std-14 fonts, no embedding)
A minimal valid PDF needs: a header `%PDF-1.4`, a Catalog, a Pages tree, a
page object per page, a content stream per page, font objects, an `xref` table
with byte offsets, and `%%EOF`.
- Use **standard-14 Helvetica / Helvetica-Bold** (`/Subtype /Type1
  /BaseFont /Helvetica`). These need NO font embedding → fully offline.
- Page object: `/MediaBox [0 0 612 792]` (US Letter), `/Resources << /Font
  << /F1 3 0 R /F2 4 0 R >> >>`, `/Contents <content-id> 0 R`.
- Content stream draws text with `BT /F1 11 Tf 1 0 0 1 x y Tm (text) Tj ET`.
- Word-wrap is heuristic: `max_chars = int(usable_width / (size * 0.50))` —
  CHAR_W ≈ 0.50 is a usable average Helvetica advance width. Real widths vary
  (don't ship to print-critical work).
- **Object byte offsets are mandatory**: record `len(buf)` before each
  `f"{oid} 0 obj\n"` write, emit the `xref` table with 10-digit zero-padded
  offsets, then `trailer\n<< /Size N /Root 1 0 R >>\nstartxref\n<xref_pos>\n%%EOF`.
- Keep text latin-1 encodable: `content.encode("latin-1", "replace")` for the
  stream (Cp1252 is closer but latin-1 is the safe stdlib default).

## TTS paragraph tagging (markers, not HTML comments)
This scaffold uses **leading markers on the paragraph** (simpler to parse than
`<!-- tts: -->` comments, and they survive plain-text round-trips):
- emoji mood: `🗣️` narrator · `😊` happy · `😠` angry · `😢` sad · `😮` tense · `🤫` whisper
- `@@SpeakerName` — dialogue speaker (must come right after an optional emoji)
- `!(mood)` — explicit mood, e.g. `!(tense)`

Emit two artifacts:
- `manuscript.ssml` — combined SSML 1.1 (`<voice name=...><prosody ...>`),
  mood→prosody map (e.g. angry→rate fast/pitch high/volume loud).
- `manuscript.tts.json` — per-chapter list of `{text, speaker, mood}` for the
  downstream TTS engine (mapping speaker→voice is a config step, not hard-coded).

## Parser pitfall — regex char class with hyphen
`re.compile(r"^@@([A-Za-z0-9_'\\- ]+?)\b\s*")` RAISES
`re.PatternError: bad character range \\-` on Python 3.14 (an escaped hyphen
inside a class that the engine now rejects). **Fix:** put the hyphen last and
unescaped: `r"^@@([A-Za-z0-9_' \-]+?)\b\s*"` (or escape outside class by
placing it first/last). This cost one broken run before the fix.

## Frontmatter without PyYAML
A 30-line parser is enough for chapter/ledger YAML:
- `---` fenced header; keys `key: value`; inline lists `key: [a, b]`;
  ONE level of nested mapping via indent stack. Block sequences (`- item`)
  are out of scope for the minimal version.

## Verification recipe (run, don't eyeball)
```python
import zipfile, xml.dom.minidom as M, json
from pathlib import Path
# EPUB
z = zipfile.ZipFile("out/demo.epub")
assert z.testzip() is None                      # zip integrity
for n in ("META-INF/container.xml","OEBPS/content.opf","OEBPS/nav.xhtml","OEBPS/chap_01.xhtml"):
    M.parseString(z.read(n))                    # XML well-formed
assert "application/epub+zip" == z.read("mimetype").decode()  # uncompressed mimetype
# PDF
b = Path("out/demo.pdf").read_bytes()
assert b[:5]==b"%PDF-" and b"%%EOF" in b and b"startxref" in b
# TTS
M.parseString(Path("out/manuscript.ssml").read_text())   # SSML well-formed
json.loads(Path("out/manuscript.tts.json").read_text())
```
Assert non-empty + parseable. For the ledger consistency pass, assert an alias
was resolved in the EPUB body (e.g. `"E watched"` not in body and
`"Elara watched"` in body).

## Trade-offs vs the dependency scaffold
- Pros: zero install, offline, trivially Windows-portable, no native-build risk.
- Cons: PDF has no page numbers/images/custom fonts, heuristic wrapping,
  single column; markdown renderer is headings + *em* + **strong** only; EPUB
  has no cover/CSS. Fine for draft/proof/audiobook-prep, not for print master.
