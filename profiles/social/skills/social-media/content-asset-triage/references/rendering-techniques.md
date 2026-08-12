# Rendering Techniques for Asset Triage

## Screenshotting HTML files (headless Chrome on macOS)

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-sandbox \
  --window-size=1400,900 \
  --screenshot="/path/to/output.png" \
  "file:///path/to/source.html"
```

- CVDisplayLinkCreateWithCGDisplay errors in stderr are harmless — ignore them.
- For tall pages, increase window height: `--window-size=1400,2400`.
- Interactive demos (p5.js, pretext) only show their initial state in a headless screenshot.
  Note this in triage — they need video/GIF to shine, or a manual screenshot mid-animation.

## Braille / Unicode text art rendering

When a folder contains `.txt` files with braille Unicode art (U+2800–U+28FF), the PNG
preview that shipped with the folder is often BROKEN — it renders as empty boxes ("tofu")
because the tool that made it used a font without braille glyph coverage.

**To produce a usable render:**

1. Embed the text directly in an HTML file (don't use fetch() over file:// — it's unreliable):
   ```html
   <pre style="font-family: 'Menlo', 'Apple Symbols', monospace;
               font-size: 9px; line-height: 1.05; color: #fff;">
   [paste braille text here]
   </pre>
   ```
2. Screenshot with headless Chrome (command above), black background.
3. Verify with vision_analyze that the shape is recognizable, not tofu boxes.

**Font notes (macOS):**
- `Menlo` — has full Unicode braille coverage. USE THIS.
- `Apple Symbols` — fallback, also works.
- `Apple Braille` / `Apple Braille Pinpoint` — DO NOT USE. These render tactile-style
  pin dots, not the Unicode braille glyphs. The art will look wrong.
- `Courier New` — no braille coverage. Will show tofu.

**Reading the .txt source:** Use `read_file` — it prefixes lines with "N|". Strip the
prefix (split on first `|`) before embedding in HTML.

## Batch screenshotting multiple HTML files

Use execute_code with a Python loop over the file list. Each Chrome call takes ~4-5s.
8 files ≈ 35s total. Check output file sizes — anything under 10KB is likely blank/broken.
