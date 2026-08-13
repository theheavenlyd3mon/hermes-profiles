---
name: large-document-familiarization
description: "Use when a user drops a large document packet to review."
version: 1.0.0
author: senna
license: proprietary
metadata:
  hermes:
    tags: [document-review, familiarization, ingestion, html, research]
    related_skills: [markdown-corpus-digest, grounded-citations]
---

# Large Document Familiarization

## When to Use

- User says "review this", "get familiar with this", or "help out with this" while attaching a file >1 MB (or a multi-file export bundled into one HTML/zip snapshot).
- The document is an artifact bundle: manifests, digests, registers, templates — not a single narrative.
- You need a working model fast without burning the whole context budget on raw bytes.

Do NOT use for: small files you can read directly, or interactive/human-review workflows (see `human-review`).

The user frequently hands over big documents ("review this", "get familiar with this") — SOUL.md, research packets, master compliance packets, exported repo snapshots. A 5.8 MB / 140K-line file must NOT be read sequentially. Strategy: map structure cheaply, extract plain text once, jump to the sections that matter, then deliver a digest the user can correct and build on.

## Steps

1. **Size check before anything else.**
   ```bash
   wc -c <file> && wc -l <file>
   ```
   >5 MB or >50K lines → full structure-first flow below. Small files can be read directly.

2. **Extract the heading outline** (HTML only — cheapest map of the whole document):
   ```bash
   python3 -c "
   import re, html
   raw = open('FILE', encoding='utf-8', errors='replace').read()
   raw = re.sub(r'<script[\s\S]*?</script>', ' ', raw, flags=re.I)
   raw = re.sub(r'<style[\s\S]*?</style>', ' ', raw, flags=re.I)
   heads = re.findall(r'<h([1-6])[^>]*>(.*?)</h\1>', raw, flags=re.I|re.S)
   clean = lambda s: html.unescape(re.sub(r'<[^>]+>', ' ', s)).strip()
   for lvl, h in heads:
       print(f'H{lvl}: ' + re.sub(r'\s+', ' ', clean(h))[:120])
   " 2>/dev/null | head -200
   ```
   For markdown, `grep -n '^#'` works instead. The outline reveals section boundaries and file manifests — read it fully before touching content.

3. **Dump readable text once** to /tmp for cheap repeated reads:
   ```bash
   python3 -c "
   import re, html
   raw = open('FILE', encoding='utf-8', errors='replace').read()
   raw = re.sub(r'<script[\s\S]*?</script>', ' ', raw, flags=re.I)
   raw = re.sub(r'<style[\s\S]*?</style>', ' ', raw, flags=re.I)
   raw = re.sub(r'<[^>]+>', '\n', raw)
   text = html.unescape(raw)
   text = re.sub(r'[ \t]+', ' ', text)
   text = re.sub(r'\n{3,}', '\n\n', text)
   open('/tmp/doc.txt','w').write(text)
   print(f'text words: {len(text.split())}')
   "
   ```

4. **Grep section boundaries** by H1 titles, then `read_file` the core sections with offset/limit (~300-line chunks):
   ```bash
   grep -n -E "^(README|Title|...)" /tmp/doc.txt | head -40
   ```

5. **Skim, don't read**: manifests, artifact digests, byte tables, and file listings are metadata — skip past them to real content. Read core narrative docs in depth; spot-check templates/CSVs/JSON registers for status fields (e.g. `complete_verified: 0`, `NOT_READY`).

6. **Deliver a working-model summary**: what the document is (revision, digest, source), the system it describes, its current status/limits, key governance story, and the open decisions. End by asking what the user wants to do with it — the digest is a foundation, not the deliverable.

## Pitfalls

- `read_file` truncates around 100K chars per call and is useless on a 5.8MB raw HTML file — always extract text first.
- HTML regex extraction with `2>/dev/null` hides the "smart approval" flag noise; expected.
- Don't read section-by-section sequentially when the document is an artifact bundle — the heading outline shows you which files are real docs vs. manifests. Reading the manifest table wastes context.
- A document with a strong control discipline (compliance packets) usually has a "do-not-claim" / status register — that is often the single highest-signal section; read it even if you skim the rest.
- After building a working model of a specific large packet the user will return to, file the digest as `references/<packet-name>.md` under this skill so future sessions load it instead of re-reading the source.
- Existing digests: `references/onyx-aerial-mesh-packet.md` (Onyx Aerial Mesh R4-DRAFT, 2026-08-12) — a working model of that 5.8MB packet: system summary, compliance status, governance story, key internal documents.
