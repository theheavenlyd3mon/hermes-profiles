# Step 1: Problem Analysis

Parse the input math problem, classify its type, and produce a complete solution outline.

## Input Formats

Accept math problems in any of these forms (in priority order):

1. **`PROBLEM.md` from Step 0 (preferred):** When the input comes from `image_assets/` images, Step 0 produces `PROBLEM.md` with extracted problem text, LaTeX formulas, and figure descriptions. Read this file first — it is the primary input source.
2. Plain text in Chinese (e.g., "解方程 x^2 - 5x + 6 = 0")
3. LaTeX source (e.g., `$x^2 - 5x + 6 = 0$`)
4. Image description (user describes what they see)
5. Structured input: `{problem: "...", constraints: "...", variables: "..."}`

### Using PROBLEM.md

When `PROBLEM.md` exists (produced by Step 0):
- Use the `## Problem Statement` section as the problem text
- Use the `## Given Values` section to identify known quantities
- Use the `## Figures` section to understand geometric/visual elements (these will inform geometry canvas components in later steps)
- Use the `## Raw LaTeX` section for equation references
- If JSONL metadata provided `stepwise_explanation`, use it as a **hint** for the solution approach, but generate a complete, detailed solution independently

## Problem Classification

Categorize the problem into one of these types:

| Type | Sub-types | Example |
|------|-----------|---------|
| Algebra | Linear equations, quadratic, systems, inequalities | x^2 - 5x + 6 = 0 |
| Geometry | Plane geometry, solid geometry, analytic geometry | Triangle area proof |
| Functions | Polynomial, trigonometric, exponential, logarithmic | Find domain of f(x) |
| Calculus | Limits, derivatives, integrals, series | Integrate sin(x)dx |
| Probability | Combinatorics, probability distributions, statistics | Coin toss probability |
| Number Theory | Divisibility, primes, modular arithmetic | Prove n^2 is even |
| Chemistry Experiment | Flame test, titration, electrolysis, gas collection, precipitation | 焰色反应实验 |
| Physics Experiment | Optics (lens/mirror), mechanics (pulley/incline), circuit, wave, thermodynamics | 凸透镜成像规律 |

## Analysis Output

> 📋 **Multiple-choice questions (选择题): capture EVERY option's full content verbatim.** If the problem has options (A/B/C/D…), transcribe each option's complete text/formula into `ANALYSIS.md`'s `## Problem Statement` (and `PROBLEM.md` if you wrote one) — e.g. `A. 1/2   B. 1/3   C. 1/4   D. 1/5`, not just the letters. The video must later SHOW each option's content, so it must be preserved here first. Also record which option is correct in the solution. (If the source is an image and two options look identical after OCR, re-read the image — options are rarely truly duplicated.)

Generate `ANALYSIS.md` with this structure:

```markdown
# Problem Analysis

## Problem Statement
[Cleaned, standardized Chinese problem text]

## Classification
- Type: [algebra/geometry/functions/calculus/probability/number_theory]
- Sub-type: [e.g., quadratic equation]
- Difficulty: [basic/intermediate/advanced]

## Knowledge Points
1. [Key concept 1]
2. [Key concept 2]
3. ...

## Solution Strategy
[2-3 sentence overview of the approach]

## Solution Steps
### Step 1: [Name]
- Input: [what we start with]
- Operation: [what we do]
- Output: [what we get]

### Step 2: [Name]
...

## Final Answer
[Clear statement of the answer]

## Common Mistakes (Optional)
- [Mistake 1 and why it's wrong]
- [Mistake 2 and why it's wrong]

## Scene Plan
| Scene | Name | Duration | Component | Content |
|-------|------|----------|-----------|---------|
| 1 | Opening title | 5-6s | Title Opening (C7) | Topic name, decorative particles |
| 2 | Problem/overview | 8-10s | Problem Card (C1) | Problem statement or topic outline |
| 3 | Principle | 12-18s | Principle Diagram (C11) | Underlying science mechanism |
| 4 | Equipment | 10-14s | Equipment Cards (C8) | Apparatus needed |
| 5 | Procedure | 20-30s | Operation Flow (C9) | Step-by-step demonstration |
| 6 | Results/display | 12-18s | Formula Panel (C3) or custom | Observations, data, colors |
| 7 | Key reminder | 10-14s | Comparison Panel (C10) | Correct vs incorrect approach |
| 8 | Conclusion | 8-12s | Conclusion Panel (C6) | Summary and key takeaways |

*(Adjust scene count and order based on problem type. Math problems use 4-6 scenes; experiment problems use 7-8 scenes for richer visual variety.)*
```

## Gate

Before proceeding to Step 2, verify:
- [ ] Problem statement is clear and unambiguous
- [ ] Classification is correct
- [ ] Solution steps are complete and logically ordered
- [ ] Final answer is verified (solve the problem yourself)
- [ ] At least 2 knowledge points identified
