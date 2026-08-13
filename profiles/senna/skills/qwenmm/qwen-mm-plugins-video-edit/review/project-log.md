# Project Log — One File, Append-Only

The single persistence surface for a project: `<videos_dir>/edit/project.md`.
Replaces heavier per-stage checkpoint files — append sections as work
progresses. No task is "complete" without this file existing and current.

## What gets appended (and when)

| Section | When |
|---|---|
| Taste Contract | before planning (`craft/art-direction.md` §2) |
| Source Review | after probing/watching inputs (`review/source-review.md`) |
| Direction | after the three-direction gate — the pick, or the skip reason |
| Scene Ledger | at plan time for multi-scene pieces; rows updated in the SAME step as every change (see below) |
| Decision | any consequential choice: engine, look, downgrade, generation batch. Every deliverable has a `## Decision — Engine` entry (plan gate checks it) |
| Render | each versioned output: path, what changed |
| Final Review | verdict block from `review/final-review.md` |
| Session Notes | end of session: done / open issues / next steps |

Decision entries stay short but complete:

```markdown
## Decision — <topic> — YYYY-MM-DD HH:MM
**Chosen:** X   **Over:** Y, Z
**Why:** one or two sentences (trace to taste contract where relevant)
**User approval:** yes / not required / pending
```

## Scene Ledger (multi-scene pieces)

The addressability backbone of scene-loop assembly (mechanics:
`engines/hyperframes.md` § Scene-loop assembly). Built at plan time, every
row updated in the same step as the change it records — a ledger backfilled
at review time is fiction.

```markdown
| 场景 | 时间段(成片) | 契约设备 | 元素 id | 最新证据 | 状态 |
```

**The device cell is the per-scene DESIGN, filled at plan time** — this row
is where a piece gets rich or stays thin: name this scene's own devices
(footage devices first, `craft/snippets/`) AND its overlay anchor, different
from the neighbours'. A ledger built with only time boxes and no devices
turns the body into one badge per scene — exactly the "给录像加了标题"
failure. Rows with no devices FAIL the plan gate.

- **One row = one review unit** — a 5-15s beat you render and judge whole,
  not one camera shot; a 4-shot quick-cut montage is one row.
- **G- rows** for cross-scene work (transitions · unified grade · sound ·
  bookend echo), verified in the global pass; same status machine.
- **Status machine:** DRAFT → VERIFIED (evidence passes) → LOCKED (enters
  the master) → INVALIDATED (any edit to the scene, or an upstream
  duration change).
- **Time boxes lock at plan time:** edit freely inside a scene, never its
  duration; a duration change INVALIDATEs every downstream row — the
  ledger makes the blast radius explicit.
- **Device column:** recipe/tool names + params + timestamps / element ids
  / asset paths — never adjectives. Generative calls: tool + intent +
  ladder rung + product path + verification state. Cutout work adds the
  edge check (halo / jagged / hairline) and static-vs-sequence.
- **Evidence column, three layers:** scene render path (KEEP the file — it
  is the board preview) + the NL observation (what you saw, why it passes
  or worries you) + fixes applied.
- **Repair semantics:** feedback → scene row → INVALIDATED → fix that scene
  only → re-verify locally → re-LOCK → global pass → new versioned final.

### One file per scene (the table is a dashboard, not the record)

Every scene gets its own file: `<videos_dir>/edit/scenes/S<N>.md`. The
ledger row stays SHORT — a device summary, element ids, status, and a
pointer into that file; everything substantial (full device parameters, VFX
specs, mask/shader code, and every round of fixing) lives in the file.
Uniform, no judgement call: 8 scenes = 8 files, created at plan time with
the Design block filled, then appended to as the scene iterates. Precedent:
when detail was crammed into the table, evidence cells hit 400+ characters
and each scene's earlier rounds became unrecoverable.

```markdown
<!-- edit/scenes/S4.md -->
# S4 — 户外·冒险时间   (time box 33.5-45.5s)

**Design:** freeze-punch still (peak @seg 1.2s → assets/s4_freeze.png,
  `snap` 1→1.08) · speed-ramp bake 1.45x (setpts, seg_10_fast.mp4) ·
  polaroid morph (dual-still crossfade, tape corner) · tracking tag
  “飞起来啦!” path [[62,58],[54,50],[45,47]]
**Elements:** #s4-run #s4-fly #s4-freeze #s4-tag #s4-frame
**Sources:** prep/s4_fly.mp4 · prep/s4_run_fast.mp4

## iter 1 — 14:02 · renders/scene4_v1.mp4
**Checks:** devices ok · type FAIL · occlusion FAIL · motion ok · technical ok
**Frames:** scenes/frames/S4_iter1_3.95s.jpg
**Saw:** freeze lands 3.95s but the ring accent sits over the boy's face;
  tag 44px is under the type floor.
**Changed:** ring → 58%/20% (off-face), tag 44→56px.

## iter 2 — 14:11 · renders/scene4_v2.mp4 → VERIFIED → LOCKED
**Checks:** all six pass · black_check PASS
**Frames:** scenes/frames/S4_iter2_3.95s.jpg (same timestamp as iter 1)
**Saw:** ring clear of the face, tag legible at thumbnail zoom, freeze hold
  reads as a beat rather than a stall.
```

**Proof frames — what to keep and what not to.** Each iter keeps 1-3 stills
that PROVE its devices landed, named
`scenes/frames/S<N>_iter<K>_<t>s.jpg`. A fix iteration must grab the SAME
timestamp as the round it fixes — two files at the same `t` are the before/
after evidence that "I fixed it" is true. Frames are cheap (100-500KB) and
they are what board.html thumbnails, cross-session resume and final
regression checks (scene frame vs the same instant in the master) actually
read.

Do NOT hoard: keep only the LATEST scene render (`renders/sceneN.mp4`);
older iteration videos are overwritten — their frames carry the history.
Functional stills used BY the composition (a freeze-punch's
`assets/s4_freeze.png`) are assets, not evidence: they live in the project's
`assets/`, never in `scenes/frames/`.

Iteration entries are **append-only** — never rewrite an earlier iter. A
scene taking 2-4 iterations is normal; this log is what makes its history
recoverable and a late "why is it like this?" answerable. Gates check that
the files exist (plan gate) and that every LOCKED scene has at least one
iteration entry (review gate).

## Rules

- **Append, never rewrite history.** Corrections are new entries that say
  what they supersede.
- **Absolute paths** for all media artifacts.
- **Versioned outputs:** every re-render increments a suffix
  (`final.mp4` → `final_v2.mp4`); never overwrite a delivered file.
- **Stale-review marker:** if a fix mutates the deliverable after a Final
  Review entry, immediately append
  `Previous final review: STALE — output changed; new file: <path>` — the
  next Final Review entry must reference the new file.
- **Resume rule:** at session start, if `project.md` exists, read the last
  entries before making new decisions. If the last status is awaiting-user
  or blocked, do not proceed as if approved.
- Reasoning that only exists in chat does not satisfy any of the above —
  if it mattered, it's in the file.
