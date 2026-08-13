# Step 0: Image Input & Problem Extraction

Read math problem images from the `image_assets/` folder, extract the complete problem text via visual recognition, and produce a structured problem document.

## Runtime Environment

At runtime, the AP platform's `main.sh` downloads the instance data from OSS into `${WORKSPACE_DIR}/`. The working directory structure is:

```
${WORKSPACE_DIR}/                    (current working directory)
  task_instruction.txt               (task description — may contain context)
  template/                          (project template)
  image_assets/                      (problem images — downloaded from OSS)
    image_0.png
    image_1.png                      (optional — multi-image problems)
    ...
```

The skill is installed separately to `~/.claude/skills/`. The `image_assets/` directory is in the **current working directory**, not in the skill directory.

## Input

### Step 1: Discover Images

First, list the contents of `image_assets/` in the current working directory:

```bash
ls image_assets/
```

This confirms which image files are available (image_0.png, image_1.png, etc.).

### Step 2: Read task_instruction.txt (if present)

Read `task_instruction.txt` from the working directory — it may contain additional task context or instructions that supplement the image content.

### Metadata (Optional)

A JSON metadata object may be provided from the JSONL data source with fields such as:
- `subject` — 学科 (e.g., 化学, 数学, 物理)
- `sub_subject` — 子学科/知识点
- `question_type` — 题型 (e.g., 计算与填空, 实验探究题)
- `stepwise_explanation` — 解题步骤概述 (brief, not detailed)
- `fine_type` — 细分题型

These metadata fields serve as **hints** to aid understanding — the authoritative problem content comes from the images.

## Process

### 1. Read All Images

Use the `Read` tool to read every image file in `image_assets/` (relative to the current working directory), sorted by filename (image_0.png first, then image_1.png, etc.). Claude's multimodal vision directly interprets the image content — no external OCR tool is needed.

```
Read image_assets/image_0.png
Read image_assets/image_1.png   (if exists)
...
```

### 2. Extract Problem Text

From each image, extract:

- **题干 (Problem stem):** The main question text, verbatim in Chinese.
- **条件与已知量 (Conditions & given values):** Numbers, equations, chemical formulas, physical quantities, constraints.
- **子问题 (Sub-questions):** If the problem has numbered parts (（1）, （2）, etc.), extract each one separately.
- **选项 (Options):** For multiple-choice questions, list all options (A/B/C/D) with their content.

### 3. Convert Math to LaTeX

All mathematical expressions, chemical equations, and formulas must be converted to LaTeX:

| Image content | LaTeX output |
|---|---|
| Superscripts (x²) | `x^2` |
| Fractions (分数) | `\frac{a}{b}` |
| Square roots (√) | `\sqrt{x}` |
| Greek letters (Δ, θ) | `\Delta`, `\theta` |
| Chemical equations | `\text{2H}_2 + \text{O}_2 \rightarrow \text{2H}_2\text{O}` |
| Thermochemical ΔH | `\Delta H = -283.0\,\text{kJ/mol}` |
| Inequalities | `\geq`, `\leq`, `\neq` |
| Vectors | `\vec{F}`, `\overrightarrow{AB}` |

### 4. Describe Figures & Diagrams

If the image contains geometric figures, circuit diagrams, experiment setups, graphs, or other visual elements:

- Write a detailed textual description under a `## Figures` section.
- For geometry: describe shapes, labeled points, angles, line segments, parallel/perpendicular relationships.
- For circuits: describe components, connections, and topology.
- For graphs: describe axes, curves, key points, trends.
- For experiment setups: describe apparatus, materials, and arrangement.

This description will be used in later steps to generate SVG animations or select pre-built asset components.

### 5. Multi-Image Merging

When multiple images are present:

- image_0.png is typically the main problem.
- Additional images may contain supplementary figures, data tables, or answer sheets.
- Merge all content into a single coherent problem document.
- Label which content came from which image if relevant to understanding.

### 6. Cross-Reference with Metadata

If JSONL metadata is available:

- Use `subject` and `sub_subject` to confirm the domain context (helps disambiguate unclear handwriting or symbols).
- Use `question_type` to structure the extraction (e.g., for 实验探究题, look for experimental procedure descriptions).
- Use `stepwise_explanation` as a sanity check — the extracted problem should be consistent with the step hints.
- Do NOT use metadata as a substitute for image content. The image is the ground truth.

## Output

Generate `PROBLEM.md` with this structure:

```markdown
# Problem Extraction

## Source
- Images: [list of image files read]
- Subject: [from metadata or inferred]
- Sub-subject: [from metadata or inferred]
- Question type: [from metadata or inferred]

## Problem Statement
[Complete problem text in Chinese, with all math in LaTeX]

[If multiple sub-questions:]
### （1）
[Sub-question 1 text]

### （2）
[Sub-question 2 text]

## Options (if applicable)
- A. [option text]
- B. [option text]
- C. [option text]
- D. [option text]

## Given Values
- [Variable 1] = [value with units]
- [Variable 2] = [value with units]

## Figures
### Figure 1: [title]
[Detailed textual description of the figure/diagram]
- Key elements: [list]
- Relationships: [spatial/logical relationships between elements]

## Raw LaTeX
[All extracted equations collected in one place for easy reference]
```

## Gate

Before proceeding to Step 1, verify:

- [ ] All images in `image_assets/` have been read
- [ ] Problem text is complete — no missing sub-questions or conditions
- [ ] All mathematical expressions are valid LaTeX (no raw Unicode math symbols left unconverted)
- [ ] Figures are described in sufficient detail for SVG recreation
- [ ] `PROBLEM.md` file exists and is well-structured
- [ ] If metadata was available, the extraction is consistent with the metadata hints
