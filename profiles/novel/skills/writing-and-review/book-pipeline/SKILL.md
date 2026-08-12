---
name: book-pipeline
description: Design and run an AI-assisted long-form fiction pipeline that turns small story ideas into publishable short novels / audiobooks. Covers the book-writer profile architecture, specialist-profile delegation lanes, manuscript folder convention, and the draft→review→revise→export loop. Use when the user wants to mass-produce books via Hermes, build a book-writer agent, or automate novel/audiobook production.
version: 1.1.0
---

# Book Pipeline — long-form AI fiction production

Turn many small story ideas into publishable short novels or audiobooks through a delegated, iterative pipeline. Built on `narrative` v2 (scene craft + project mode) and `narrative-revisor` (separate critic).

## When to use
- User wants to write a novel / short novel / audiobook with AI assistance.
- User is building or refining a `book-writer` profile.
- User has multiple story ideas to expand and publish.
- Any request combining "draft fiction" + "review loop" + "publish/export."

## Architecture

| Lane | Profile / skill | Deliverable |
|------|-----------------|-------------|
| Own the loop | **`book-writer` profile** | concept → chapters → export coordination |
| Scene craft | `narrative` v2 | draft scenes, project ledger schemas |
| Review | `narrative-revisor` | 3-pass critique + JSON handoff |
| Local model | `mlops` + `book-writer-pipeline/windows/` | Darwin server on your GPU |
| Assembler CLI | `code` / stdlib CLI | chapters → EPUB/PDF + TTS tags |
| Market intel | `research` | 1-page brief before writing |
| Publishing | `business` | KDP / D2D / Findaway matrix |

**Operating principle:** do NOT do all domain work in one profile. Orchestrator (Senna) routes; `book-writer` owns manuscript state. Lanes use `delegate_task` when multi-domain.

**Report protocol:** multi-lane fan-out → **wait for all** → **one consolidated brief**. See `references/orchestrator-fanout.md`.

**Locked decisions:** `references/locked-decisions.md` — Darwin-only; stdlib assembler canonical; Kokoro→Findaway.

---

## End-to-end loop (wired)

```
0 INIT     init_manuscript.py → scaffold tree
1 CONCEPT  user + book-writer → concept.md + tone
2 INTEL    research lane (optional but recommended pre-draft)
3 PLAN     character-sheet, plot-ledger, foreshadow-bank, worldbuilding, voice-profile
4 DRAFT    narrative skill → chapters/chNN.md  status:drafted
5 REVIEW   narrative-revisor → reviews/*.json   (fresh context)
6 REVISE   apply issues only → re-review until pass
7 GATE     check_manuscript.py + chapter checklist → status:done
8 EXPORT   python -m manuscript_pipeline.cli --book <name> --out out
9 PUBLISH  business lane (KDP Select → D2D; audio via Findaway)
```

### Stage contracts

| Stage | Input | Output | Gate |
|-------|-------|--------|------|
| INIT | slug | `manuscript/{slug}/` tree | dirs exist |
| CONCEPT | user brief | filled `concept.md` | logline + tone set |
| PLAN | concept | ledgers + voice | every named char has sliders + Lie/Want/Need |
| DRAFT | beat row + voice + chars | scene md `status:drafted` | frontmatter complete |
| REVIEW | scene + ledgers | JSON handoff | Pass 1–3 run; blockers listed |
| REVISE | issues JSON | updated scene | only listed fixes |
| GATE | chapter | `status:done` | zero blocker/major; mechanical check clean |
| EXPORT | all chapters done | EPUB/PDF/SSML/TTS-JSON | CLI smoke artifacts |

### Commands

```bash
# Scaffold (from repo or skill scripts dir)
python ~/.hermes/profiles/senna/skills/writing-and-review/book-pipeline/scripts/init_manuscript.py my-title \
  --root ~/book-writer-pipeline/manuscript --title "My Title"

# Mechanical scan
python ~/.hermes/profiles/senna/skills/narrative/scripts/check_manuscript.py \
  ~/book-writer-pipeline/manuscript/my-title

# Export (canonical zero-dep CLI)
cd ~/book-writer-pipeline
python -m manuscript_pipeline.cli --book my-title --out out
```

Windows Darwin stack: `book-writer-pipeline/windows/README.md` + `start-darwin-server.bat`.

---

## Manuscript folder convention

Copy `templates/manuscript-layout.md` or run `scripts/init_manuscript.py`.

```
manuscript/{project}/
  manuscript.yaml
  concept.md
  canon.md
  character-sheet.md
  plot-ledger.md
  foreshadow-bank.md
  worldbuilding.md
  voice-profile.md
  chapters/ch01.md …
  outlines/synopsis.md
  reviews/                 # revisor JSON
  exports/                 # CLI outputs (optional mirror)
```

## Model note (locked: Darwin-only)

Local: Windows your GPU / 32GB RAM. **Only local-36B-Opus APEX I-Mini.**  
llama.cpp `llama-server` + `--n-cpu-moe`. Sequential plan/draft/review — never concurrent loads.  
No speculative decoding on MoE. Inject ledger slices, never full manuscript.  
TTS: Kokoro-82M → Findaway/Spotify. ACX rejects third-party TTS.  
API fallback: OpenRouter DeepSeek V3.2 or Qwen3.6-Plus.

## Skills map

| Skill | Owns |
|-------|------|
| `narrative` v2 | craft, project mode, stability trap, check script |
| `narrative-revisor` | 3-pass review + JSON handoff |
| `book-pipeline` | this architecture + init + routing |
| assembler | `~/book-writer-pipeline/` (stdlib) |

## Pitfalls
- Consistency drift without ledger enforcement
- One profile drafting AND reviewing its own prose
- Context overflow from full-manuscript dumps
- Stability trap only at scene grain (must also run book-end)
- Market research after writing instead of before
- Dual local models when only Darwin is available
- Subagents inventing extra skills/CLIs — reconcile against locked-decisions

## Support files
- `references/locked-decisions.md`
- `references/orchestrator-fanout.md`
- `references/style-revision-playbook.md`
- `references/zero-dep-export.md`
- `references/build-export-scaffold.md` (deprecated)
- `templates/manuscript-layout.md`
- `scripts/init_manuscript.py`

## Verify
- [ ] Manuscript tree has state files before chapter 2
- [ ] Each chapter has reviewer pass JSON before assembly
- [ ] `check_manuscript.py` clean of blockers before export
- [ ] Export produces openable EPUB
- [ ] Multi-lane work ends in one synthesis report
