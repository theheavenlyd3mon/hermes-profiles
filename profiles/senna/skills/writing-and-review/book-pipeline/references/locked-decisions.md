# Book-pipeline locked decisions (2026-07-08, updated build session)

Do not re-debate these unless the user reopens them.

## Assembler
- **Canonical:** `~/book-writer-pipeline/` — pure Python stdlib CLI.
- **Run:** `python -m manuscript_pipeline.cli --book <name> --out out`
- **Emits:** EPUB 3, PDF (std-14 Helvetica), `manuscript.ssml`, `manuscript.tts.json`
- **Deprecated:** `~/manuscript_pipeline/` (ebooklib/pandoc stack). Reference only.
- **Smoke-test:** re-run the demo book after any assembler change; all four artifacts must emit.

## Local model (Windows your GPU 12GB / 32GB RAM)
- **Only local model the user has:** local-36B-Opus APEX I-Mini (MoE GGUF).
- **Stack:** llama.cpp `llama-server` with `--n-cpu-moe` expert offload.
- **Scripts:** `~/book-writer-pipeline/windows/` (`start-darwin-server.bat`, `smoke-test.bat`).
- **No dual-model split.** Same Darwin instance does plan/review AND draft in sequential stages.
- **No speculative decoding on MoE** (net loss).
- Context: inject ledger/character-sheet slices — never full manuscript into one turn.
- Realistic speed: ~35–55 tok/s (not 60–80).
- API fallback only if local fails: OpenRouter DeepSeek V3.2 or Qwen3.6-Plus.

## TTS + distribution
- **Local TTS:** Kokoro-82M (CPU-friendly).
- **Upload route for AI audio:** Findaway / Spotify. **ACX rejects third-party TTS**.
- E-book: KDP Select 90d (KU) then wide via Draft2Digital. First-title length **40–50k**, price **$3.99–4.99**.
- Rights: pure-AI not copyrightable; AI-*assisted* human-authored work is — keep edit history.

## Skills + profile
- `narrative` v2 = scene/chapter craft + project mode + anti-slop + stability trap + `scripts/check_manuscript.py`.
- `narrative-revisor` = separate 3-pass critic + JSON handoff (do not self-review).
- `book-pipeline` = book-scale architecture, folders, loop, export, publish routing + `scripts/init_manuscript.py`.
- **`book-writer` profile EXISTS** at `~/.hermes/profiles/book-writer` — owns the loop; Senna routes Novel/Book/Ebook/StoryPipeline → book-writer.

## Genre defaults for this user
- Murim / dark Eastern fantasy / cultivation×grimdark / martial-arts noir.
- Melancholic, atmospheric, weight of violence. Cost over glory.
- Series model: many short novels, not one 100k standalone (KU math needs catalog).
