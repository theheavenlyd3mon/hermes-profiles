# The Unreasonable Effectiveness of HTML (Thariq, Anthropic — May 2026)

**Source:** x.com/i/article/2052796100608974848 (auth wall)  
**Author:** Thariq Shihipar (Claude Code engineering lead, Anthropic)  
**Article:** "Using Claude Code: The Unreasonable Effectiveness of HTML"  
**Companion site:** thariqs.github.io/html-effectiveness (20+ interactive demos)  
**Referenced by:** trq212, May 8, 2026

## Core Thesis

Markdown became the default AI output format in the GPT-4 era when 8K context windows made token efficiency critical. That constraint is gone. The default should be HTML.

## The Three Arguments

### 1. Spatial information is flattened by Markdown
Diffs, call graphs, data flows — these are inherently spatial. HTML renders them as annotated diffs with margin notes, SVG call graphs with hot paths highlighted, and side-by-side comparisons. Markdown turns them into paragraphs you have to mentally reconstruct.

### 2. The LLM is both generator and consumer
Markdown's primary advantage is human readability in a text editor. When the agent writes it and the agent reads it, that advantage evaporates. HTML wins on structure, interactivity, and shareability.

### 3. The format shift is also a workflow shift
Self-contained HTML files can be deployed via S3, Val Town, or any static host. One user (@closermethod) ships an entire product line as HTML artifacts — 7 live pages, one Stripe pipeline.

## The Nine Categories (from companion site)

01. Exploration & Planning — side-by-side approaches, visual design directions, implementation plans
02. Code Review — annotated diffs, PR writeups, module maps
03. Design — living design systems, component variant sheets
04. Prototyping — animation sandboxes, clickable interaction flows
05. Diagrams — SVG illustrations, annotated flowcharts
06. Decks — arrow-key slide decks as single HTML files
07. Research — feature explainers, concept tutorials with live demos
08. Reports — weekly status dashboards, incident timelines
09. Custom Editors — ticket triage boards, JSON editors, review UIs

## Counterarguments from the Discussion

- **Token cost:** HTML is 2-4x heavier than Markdown. Estimated $5K/yr extra on 425 files.
- **Editability:** HTML is harder for humans to co-author. Markdown diffs are readable; HTML diffs are noise.
- **Security:** Multiple HN commenters reported leaked data from agents publishing HTML dashboards to unauthenticated public URLs.
- **Alternatives:** MDX (Markdown + JSX), AsciiDoc, Typst, Org-mode, JSON/XML for spec writing.

## Relevance to Tool Call Efficiency

Thariq's principle complements the Mem0 input-side optimization:

- **Mem0 (input):** inject only relevant context → fewer tokens per turn
- **Thariq (output):** use HTML so the artifact absorbs complexity → fewer round-trips to clarify, visualize, or iterate

Both reduce the need for tool calls — one by shrinking what the agent must read, the other by expanding what each output can convey.
