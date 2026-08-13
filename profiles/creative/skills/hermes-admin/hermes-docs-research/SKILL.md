---
name: hermes-docs-research
description: Use when answering how a Hermes feature works.
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [hermes, docs, research, troubleshooting]
    related_skills: [web-integration-diagnostics, hermes-session-recovery]
---

# Hermes Docs Research

Answering "how does Hermes do X?" reliably means going to the official docs
(https://hermes-agent.nousresearch.com/docs) — the source of truth, always
fresher than memory or skills. This skill is the class-level procedure for
mining that corpus efficiently, plus a growing `references/` bank of
already-verified answers.

## When to use

- Any question about Hermes Agent behavior, config keys, platform setup, or desktop-app capabilities.
- Before claiming a feature does/doesn't exist — verify against the corpus first.
- Check `references/` here first: a verified answer may already be banked.

## Procedure

1. **Check `references/`** in this skill for an existing verified answer.
2. **Fetch the corpus** (stable URLs, generated fresh on every deploy):
   - Index (~17 KB): `https://hermes-agent.nousresearch.com/docs/llms.txt`
   - Full corpus (~3.7 MB): `https://hermes-agent.nousresearch.com/docs/llms-full.txt`
3. **Download locally, then search** — the corpus is far too big for `web_extract` (it truncates). Use terminal:
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/docs/llms-full.txt -o /tmp/hermes-docs-full.txt
   grep -in "keyword" /tmp/hermes-docs-full.txt | head -40
   sed -n 'START,ENDp' /tmp/hermes-docs-full.txt   # read context around hits
   ```
4. **Iterate synonyms**: a feature may be named differently in docs (e.g. "avatar" vs "userpic" vs "profile picture" vs "icon"). Run several greps before concluding absence.
5. **Read surrounding context** (±30 lines) before citing — grep hits are one-line fragments.
6. **Bank durable findings**: condense the verified answer into `references/<topic>.md` via `skill_manage write_file`, so the next session skips the dig.

## Pitfalls

- **Never `web_extract` the full corpus** — multi-MB pages come back truncated head+tail. curl to /tmp and grep.
- **Hashed asset URLs rot.** Doc pages link assets as `/docs/assets/files/llms-<hash>.txt` and the hash changes every deploy. Use the stable `/docs/llms.txt` / `/docs/llms-full.txt` aliases, or re-derive the current hash from the landing page each time. Never reuse a hashed URL from an old session.
- **False positives from third-party UI text**: greps like "avatar" also match instructions about *other* products' UIs (e.g. "click your avatar → Admin Settings" in an Open WebUI section). Always check which doc section a hit lives in (`# Heading` lines are section markers; the corpus marks each page with `<!-- source: ... -->` comments).
- **Absence of a grep hit ≠ absence of a feature** — try synonyms, related terms, and the index file before concluding.
- If the bundled `hermes-agent` skill exists in the profile, load it first for quick orientation; the docs corpus remains the tiebreaker when they disagree.

## References

- `references/hermes-bot-avatars.md` — where bot avatars/profile pictures are set per messaging platform (Telegram, Discord, WhatsApp, Google Chat, Slack) + desktop-app appearance model. Verified against docs 2026-08.
