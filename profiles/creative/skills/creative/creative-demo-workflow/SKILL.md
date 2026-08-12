---
name: creative-demo-workflow
description: Organize creative skill demos for social posting.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, workflow, social-media, organization, x-com, posting]
---

# Creative Demo Workflow

Organize outputs from multiple creative skills into a structured folder for social media posting (X.com, Instagram, etc.).

## When to Use

- User wants to showcase multiple creative skill demos
- User has a social profile agent that views folders and drafts posts
- Need to organize HTML files, images, ASCII art, and other artifacts
- Creating a portfolio or demo reel from skill outputs

## Workflow

### Step 1: Create Folder Structure

```bash
mkdir -p ~/cheonma/skill-demos/{html,images,ascii-art,pixel-art,screenshots}
```

### Step 2: Organize Files with Numbered Prefixes

Number files sequentially so they appear in order when listed:

```
01-09: HTML files (need browser screenshots)
10-19: Generated images (ready to post)
20-29: ASCII art renders
30-39: Pixel art variants
40+: Design specs, documents
```

### Step 3: Write README.md

Include:
- **How to Post** section with step-by-step instructions
- **File Guide** table with columns: #, File, Skill, What it is
- **Suggested Post Structure** with 2-3 options (carousel, thread, single showcase)
- **Notes** about interactive demos, screenshot requirements, theme consistency

### Step 4: Serve HTML Files (if needed)

Browser tools block `file://` URLs. Start HTTP server:

```bash
cd /tmp && python3 -m http.server 8765
```

Then navigate to `http://localhost:8765/<path>/<file>.html`

### Step 5: Screenshot HTML Files

For each HTML file:
1. Navigate in browser
2. Use `browser_vision` to capture screenshot
3. Save to `screenshots/` folder

### Step 6: Final Checklist

- [ ] All files copied to organized folders
- [ ] README.md with complete file guide
- [ ] HTML files accessible via HTTP server or direct open
- [ ] Images in correct format (PNG for X.com)
- [ ] Post structure suggestions included

## Pitfalls

- **Browser tools block file:// URLs** — always use HTTP server for HTML files
- **Multiple skills have duplicate paths** — use full relative paths (e.g., `creative/pixel-art` not `pixel-art`)
- **RISO braille needs original black background** — don't preprocess to white for braille preset (black maps to empty cell U+2800)
- **Interactive demos need animation** — screenshot p5.js/pretext while animated, not static
- **X.com carousel limit** — 10 images max per post, plan accordingly

## Example README Structure

```markdown
# Creative Skill Demos — X.com Post Assets

## How to Post
1. Open HTML files in browser (double-click or drag)
2. Take screenshots of each
3. Use images + screenshots to compose post
4. Suggested: carousel or thread format

## File Guide
| # | File | Skill | What it is |
|---|------|-------|------------|
| 01 | `01-sketch-variant.html` | sketch | Dark terminal UI |
| 10 | `10-infographic.png` | baoyu-infographic | Power system diagram |

## Suggested Post Structure
**Option A — Carousel (10 images):**
1. Pixel art
2. ASCII art
3. Infographic
...

**Option B — Thread:**
- Post 1: Visual art (pixel + ASCII)
- Post 2: Educational (infographic + comic)
- Post 3: UI/UX designs
...
```

## Attribution

Workflow pattern developed during Tokyo Ghoul creative skill demo session (July 2026).
