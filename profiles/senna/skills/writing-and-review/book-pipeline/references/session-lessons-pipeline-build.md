# Session lessons — pipeline build (2026-07-08)

Condensed so future agents do not re-learn the hard way.

## What landed (built, not just designed)

| Piece | Location |
|-------|----------|
| Profile | `~/.hermes/profiles/book-writer` (wrapper `book-writer`) |
| Craft | `narrative` v2 + `references/project-mode.md` + `scripts/check_manuscript.py` |
| Review | `narrative-revisor` (JSON handoff; no net-new plot) |
| Architecture | this skill (`book-pipeline`) + `scripts/init_manuscript.py` |
| Assembler | `~/book-writer-pipeline/` stdlib CLI (**CANONICAL**) |
| Deps CLI | `~/manuscript_pipeline/` (**DEPRECATED**) |
| Windows Darwin | `book-writer-pipeline/windows/{README,start-darwin-server,smoke-test,stop-server}.bat` |
| Senna routing | `Novel+Book+Ebook+StoryPipeline→book-writer` in senna SOUL |

## Fan-out protocol (user-enforced)

1. Split into research / code / creative / business / mlops (or similar) tasks.
2. Dispatch in parallel (`delegate_task` batches).
3. **Do not partial-report** when user said wait-all.
4. On completion: one table — status, artifact paths, **conflicts**, recommendation.
5. Reconcile duplicates before any further build.

## Duplicate-artifact pattern observed

Parallel agents produced:
- Two market briefs (template + filled + genre brief) — keep; complementary.
- Two publish docs — cross-check; no fatal contradiction on ACX/Findaway.
- Two model strategies — **lock Darwin-only** (user reality on 12GB), ignore dual Qwen planner+drafter as default.
- Two CLIs — **stdlib wins** for offline Windows cleanliness.

After any fan-out: open `locked-decisions.md` and rewrite locks if the user confirmed.

## Smoke sequence (must pass before calling the pipeline "done")

```bash
# scaffold
python …/book-pipeline/scripts/init_manuscript.py pipeline-smoke \
  --root ~/book-writer-pipeline/manuscript --title "Pipeline Smoke"

# mechanical
python …/narrative/scripts/check_manuscript.py \
  ~/book-writer-pipeline/manuscript/pipeline-smoke

# export (demo book layout in canonical repo)
cd ~/book-writer-pipeline
python -m manuscript_pipeline.cli --book demo --out out
# expect: demo.epub, demo.pdf, manuscript.ssml, manuscript.tts.json
```

## Init template rule

Scaffold bodies that contain YAML must **not** use `str.format` with `{key}` — braces in YAML/maps explode. Pattern:

```python
VOICE.replace("__SLUG__", slug)
MANIFEST.replace("__TITLE__", title).replace("__TODAY__", today)
```

## Reviewer separation (non-negotiable)

Draft and critique in **separate contexts**. Same model file (Darwin) is fine sequentially; same turn generating + self-scoring is not. Stability trap research: AI rounds its own edges.

## Commercial defaults (user niche)

- Open: murim noir / dark Eastern / cultivation×grimdark.
- Length: 40–50k short novel; series for KU math.
- Price: $3.99–4.99 e-book.
- Audio AI: Kokoro → Findaway/Spotify; **never ACX third-party TTS**.
