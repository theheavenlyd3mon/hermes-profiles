# Source & Adaptation Notes

## Origin

Adapted from [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) (Apache-2.0, 13.7k stars as of May 2026).

Source skills:
- `marketing/skills/draft-content` (117 lines) → `draft-post`
- `marketing/skills/brand-review` (276 lines) → `brand-review-content`
- `sales/skills/draft-outreach` (440 lines) → `reply-research`

## What Was Changed

**Stripped:**
- Slash command syntax (`/draft-content`, `/brand-review`) — not Hermes-native
- MCP connector references (HubSpot, Slack, CRMs, QuickBooks, PayPal)
- Enterprise channels (press release, case study, sales collateral)
- B2B sales framing in outreach skill
- `CONNECTORS.md` references

**Added:**
- AI-ism blocklist as highest-severity check in brand-review
- Indie-hacker voice defaults (specific numbers, failure framing, no corporate jargon)
- Reply angle templates repurposed from sales outreach hooks
- Channel-specific structures for X post/thread (not in original draft-content)
- Daily engagement cron integration notes in reply-research

**Rewritten:**
- Voice defaults from "neutral professional" to indie-hacker / build-in-public
- Output formats from Anthropic's table-heavy style to Hermes terminal-friendly
- Trigger phrases updated for Hermes skill conventions

## Further Mining

The source repo has 18 plugins, ~100+ skills. Most are enterprise-only (Snowflake, Jira, HubSpot). Skills worth considering for future porting:

- `product-management/skills/write-spec` — spec-writing template
- `product-management/skills/product-brainstorming` — structured ideation
- `engineering/skills/code-review` — generic enough to be useful
- `small-business/skills/canva-creator` — if adding visual asset generation

Repo structure: each plugin lives in `plugin-name/`, skills in `plugin-name/skills/`, each with `SKILL.md` + optional `reference/` subdirectory.
