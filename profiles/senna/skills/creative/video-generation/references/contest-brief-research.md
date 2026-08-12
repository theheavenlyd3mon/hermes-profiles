# Researching a contest/competition brief before dispatching a team

Learned 2026-07-30, Nous Research × Black Forest Labs FLUX 3 short-film contest.

## The pattern
When the user says "there's a new competition, help me enter," the FIRST move is
pulling the primary-source brief — not brainstorming, not dispatching specialists.

1. `web_search` for the announcement (often thin — marketing posts lack rules).
2. `x_search` with `allowed_x_handles` pinned to the org accounts (e.g.
   ["NousResearch", "bfl_ai"]) and `enable_image_understanding=true` (announcement
   images often carry the rules/prizes). This returned the full brief in one call:
   submission format, tags required, exact deadline with timezone, prize tiers,
   promo codes, and judging signals.
3. Restate the brief to the user as: WHAT to make, HOW to submit (exact tags/format),
   DEADLINE converted to hours remaining, and what's judged.

## What the brief must yield before any dispatch
- Submission artifact: file type + where posted + required tags/mentions.
- Deadline with timezone, converted to a work-backwards plan with buffer.
- Judging criteria or hints (for this contest: coherent motion, cinematic quality,
  narrative arc, suggested 10-40s length).
- Feasibility check against tool constraints (see SKILL.md) BEFORE promising a
  deliverable length/format.

## Feasibility framing that worked
Present constraints as a plan input, not a caveat: "one generation = one 5-20s clip,
several minutes each → a 20-40s film = 2-4 chained segments or one strong single
take; each retry costs minutes." This shaped the whole team plan.

## Multi-profile team shape (this user's preference)
Research brief first (senna) → parallel specialists (creative: concept/storyboard;
social: post copy + scan competing entries) → senna synthesizes ONE plan → user
green-lights → generate. User prefers batched numbered approvals ("1-3: yes/no/more")
over open questions.
