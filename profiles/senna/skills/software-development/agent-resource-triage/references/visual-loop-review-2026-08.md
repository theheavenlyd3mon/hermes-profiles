# Visual-Loop bundle review (2026-08-03)

Repo: https://github.com/Salt-555/visual-loop — a 4-skill Hermes bundle
(author ALLMIND, MIT, v1.3.0, brand new at review: 5 commits, 1 star).
The latest commit scrubbed a specific game project ("neon-protocol", Pi 5)
out of it before publishing — so it was built on a real system, then generalized.

## Bundle contents (each dir under skills/ is a complete Hermes skill)
- `visual-loop` (v1.3.0) — critique-driven visual iteration, NO reference images
- `visual-reference-loop` (v1.1.0) — sibling loop WITH reference material to transfer
- `headless-visual-capture` (v1.1.0) — Playwright-core + system Chromium headless screenshot recipe
- `visual-tdd-patterns` (v1.1.0) — pure-data/descriptor seam TDD for rendering features

## The loop pattern (visual-loop)
Parent = orchestrator ONLY (never captures/critiques itself). Per iteration:
1. Capture worker — launches real target, reaches meaningful state, screenshots,
   verifies non-blank via pixel sampling
2. Hypercritical critic — gets ONLY the screenshot, returns exactly ONE
   highest-leverage slice with exact implementation contract, grounded in
   visible pixels ("make it premium" is rejected)
3. TDD worktree implementation — RED → GREEN → full tests → real runtime smoke →
   scoped commit (up to 3 non-overlapping worktrees)
4. Independent fresh reviewer — APPROVED / REQUEST_CHANGES only
5. Merge → recapture → fresh comparison worker returns IMPROVED / NO_GAIN / REGRESSION

## Regression policy (the part that matters — invariants, not suggestions)
- REGRESSION ⇒ `git revert` that merge, recapture, confirm baseline restored,
  THEN continue. Never "fix forward" on a regressed tree.
- Two REGRESSIONs anywhere ⇒ permanent stop (direction is wrong).
- Two consecutive NO_GAINs ⇒ stop (merge stays, but stop grinding).
- Success requires net improvement over the ORIGINAL baseline; reverted
  iterations contribute nothing. No success claim without a fresh after-merge capture.
- Mandatory worktree cleanup after each merge (worktrees share .git but NOT
  node_modules — every stale worktree is a duplicate install).

## Why it matters for this user
Direct instance of the AgentUnreal differentiator thesis ("self-growth VERIFIED,
not self-growth alone"): verdicts are mechanical binary truth (git revert +
fresh screenshot + fresh unbiased comparator), no worker judges its own work.
visual-tdd-patterns has transferable hard-won detail: pure descriptor seam
(logic in testable pure modules, rendering = thin data→mesh wiring), luminance-band
verification WITHOUT rendering (0.2126R+0.7152G+0.0722B invariants), real pitfall
taxonomies (InstancedMesh r128 frustum culling, vitest/rolldown em-dash parse
failure, module-bridge readiness gate, grid-fixture transposition false-REDs).

## Gaps / verdict
Capture skill is web-only (headless Chromium) — no UE5 path, and UE5 lives on the
user's Windows box, so a capture worker on this Mac can't reach it as-is. Loop
skeleton transfers; capture step needs a UE equivalent. Verdict: high-value
REFERENCE for AgentUnreal eval design; not installed. Install offered 2026-08-03,
user decision pending. If installing: their README says copy to
~/.hermes/skills/software-development/ but our setup is per-profile —
correct target is ~/.hermes/profiles/senna/skills/.
