# Tool Roundup — May 24, 2026
Source: 4 X/Twitter posts from @heynavtoor, @bayendor, @sharbel

## Document Tools (ranked for macOS i7/16GB)

1. **Stirling-PDF** ★★★★★ — 79.3K stars
   PDF toolkit: merge, split, OCR, sign, compress, redact, watermark. 50+ tools.
   Replaces: Adobe Acrobat, SmallPDF. Ultra-lite variant: ~512MB-1GB RAM.
   Run-on-demand (not always-on). Also has desktop app (no Docker).
   Setup: `docker run` or download desktop app.

2. **Paperless-ngx** ★★★★★ — 41K stars
   Document management with OCR + ML auto-tagging + full-text search.
   Replaces: Evernote, DevonThink. RAM: 2-3GB steady-state.
   Setup: Docker Compose. Feed via scanner, email, or file drop.
   Caveat: cleartext storage — don't expose to internet.

3. **Karakeep** ★★★★☆ — 25.3K stars
   AI link/article/PDF archiver. Browser extensions + mobile apps.
   Replaces: Pocket (shutting down!), Raindrop.io. RAM: 2-3GB (without local LLM).
   With Ollama: 8-12GB — skip local AI on 16GB, use API-based.

4. **Anytype** ★★★★☆ — 7.7K stars
   Local-first, E2E encrypted notes/knowledge base. Native Electron app.
   Replaces: Notion, Obsidian. RAM: ~300-500MB.
   Caveat: "Any Source Available" license (not true OSS). Still alpha (v0.55).

5. **Documenso** ★★★☆☆ — 13K stars
   Open-source DocuSign. Needs public URL + SMTP + signing cert for real use.
   Dev mode on laptop OK, production needs VPS or hosted cloud.

6. **Papermark** ★★☆☆☆ — 8.4K stars
   DocSend alternative. Needs S3 + PostgreSQL + analytics service. VPS only.

Combined budget: Stirling-PDF + Paperless-ngx + Karakeep ≈ 5-7GB. Leaves ~9GB free.

## Developer/GitHub Tools (ranked for Hermes Agent)

1. **CodeGraph** ★★★★★ — 21.6K stars, INSTALLED
   Pre-indexed code knowledge graph. Direct Hermes support.
   22 languages, 14 frameworks. 10 MCP tools.
   Claims: 35% cheaper, 57% fewer tokens, 71% fewer tool calls.
   Setup: `npm i -g @colbymchenry/codegraph && codegraph install --target=hermes --yes`
   Pitfall: curl | sh may be blocked; npm install works as alternative.

2. **Agentmemory** ★★★★☆ — 17.2K stars
   Persistent memory for coding agents. 95.2% retrieval R@5. 53 MCP tools.
   Supports Hermes natively. Setup: `npm install -g @agentmemory/agentmemory`

3. **CloakBrowser** ★★★★☆ — 20.1K stars
   Stealth Chromium, 58 C++ patches, passes 30/30 bot detection tests.
   Drop-in Playwright replacement. Setup: `pip install cloakbrowser`

4. **12-Factor Agents** — 22.1K stars, READ ONLY
   Design philosophy doc, not software. Bookmark the repo.

5. **Academic Research Skills** — ~19.9K stars, SKIP
   Claude Code only, CC-BY-NC license, niche.

## Email for Hermes

Hermes has bundled himalaya skill (IMAP/SMTP CLI).
Simplest path: Gmail + App Password + `brew install himalaya`.
Config: ~/.config/himalaya/config.toml
Alternative: Cloudflare domain email routing ($8-10/yr) or Zoho (free tier).
Autonomous loop: cron job every 5-15 min to check inbox and forward summaries.
