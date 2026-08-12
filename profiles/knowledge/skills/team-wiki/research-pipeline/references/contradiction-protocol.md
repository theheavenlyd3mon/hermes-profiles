# Contradiction Protocol

Use this reference when the research pipeline surfaces conflicting claims between sources, between an existing page and new findings, or between multiple existing pages.

## When to mark `contested`

Mark a page `contested: true` only when:
- Two or more sources explicitly disagree about a factual claim
- An updated finding genuinely conflicts with an existing entry's dated findings or conclusions
- The conflict is material enough that a reader needs both positions to understand the state of knowledge

Do **not** mark contested when:
- One source is clearly older and the newer source supersedes it without explicit disagreement
- The conflict is terminological rather than factual
- The disagreement is marginal and does not affect the core claim
- The newer source simply extends or refines prior work

## When to supersede silently

Silent supersession is appropriate when:
- The new source is newer, more authoritative, and specifically replaces prior guidance
- The older claim is clearly rendered obsolete by newer evidence
- There is no explicit contradiction in sources, only evolution

In that case: replace the outdated claim, add a dated entry `YYYY-MM-DD — superseded by <new source>` for traceability, and do **not** set `contested: true`.

## Three-way contradictions

When three sources describe three distinct positions:
1. Add all three positions with dates and sources
2. Set `contested: true`
3. List all contradicting pages in `contradictions: [...]`
4. Consider creating a `comparison/` page if the disagreement itself is analytically useful

## Partial overlap

When sources disagree on one attribute but agree on others:
- Keep the agreed facts in the main body
- Isolate the disputed attribute in a `## Contradiction` section
- State both positions with dates and sources
- Set `contested: true`

## Nested contradictions

When Page A conflicts with Page B, and Page B conflicts with Page C:
1. Add `contradictions` links symmetrically where direct conflict exists
2. In each page's `## Contradiction` section, state only the position that conflicts with *that* page
3. Do not force every page to summarize the whole triangle; readers can follow the links

## Provenance under contradiction

Even when a page is contested, provenance markers remain additive:
- Append `^[raw/articles/source-file.md]` to paragraphs whose claims come from a specific source
- Each position in the contradiction section gets its own marker

## Logging

The batch log entry must note:
- Every page marked `contested: true`
- The other pages it contradicts
- A brief reason: factual conflict, supersession, three-way disagreement, etc.

## Canonical examples

### Example 1 — simple factual contradiction

Page: `vibe-coding`
Existing claim: code is ephemeral by default in agentic workflows
New finding: some 2026 tool narratives describe artifact preservation as default behavior
Action:
- `contested: true`
- `contradictions: [agentic-engineering]`
- Keep both positions in `## Contradiction` with dates and sources
- Log: `contradictions: vibe-coding ↔ agentic-engineering`

### Example 2 — silent supersession

Old claim: "Claude Opus 4 remains the recommended coding model."
New authoritative source: "Claude Opus 4 deprecated June 15, 2026; use Opus 4.5."
Action:
- Replace the outdated recommendation
- Add a dated note: `2026-06-15 — superseded by deprecation notice`
- No `contested: true`

### Example 3 — three-way disagreement

Sources recommend 4-bit, 8-bit, and no quantization for the same workload.
Action:
- Add all three positions to the concept page
- `contested: true`
- Consider `comparison/quantization-tradeoffs.md` if the disagreement itself is reusable

## Common mistakes

- **Over-contesting**: marking every update as contested when the norm is supersession. Reserve `contested` for genuine, material disagreement.
- **Under-contesting**: silently overwriting older claims when sources explicitly disagree. Add both positions.
- **Forgetting symmetric links**: if A contradicts B, B's `contradictions` should reference A.
