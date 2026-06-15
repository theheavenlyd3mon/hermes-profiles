---
name: build-in-public
description: Build-in-public X (Twitter) growth strategy using Hermes as an autonomous content engine — profile design, VPS deployment, content pipeline, engagement cadence, and X Premium tier guidance for indie hackers.
version: 1.0.0
author: senna
triggers:
  - "build in public"
  - "grow on X"
  - "social media manager profile"
  - "autonomous posting"
  - "indie hacker twitter"
  - "X growth strategy"
  - "VPS hermes"
metadata:
  hermes:
    tags: [social-media, x, twitter, build-in-public, growth, indie-hacker, vps, autonomous]
    related_skills: [xurl, github-pr-workflow, hermes-agent, draft-post, brand-review-content, reply-research]
---

# Build-in-Public with Hermes

Use Hermes as an autonomous build-in-public engine — ship code, post about it, grow an audience, build a community. Reference models: @levelsio (Pieter Levels), @marc_louvion, @tdinh_me, @outsource_.

## When to Use

- Setting up Hermes as an autonomous social media presence
- Designing a "social media manager" Hermes profile
- Deploying Hermes on a VPS for always-on posting
- Choosing X Premium tiers for growth
- Planning a build-in-public content strategy

## Prerequisites

- xurl CLI installed and authenticated (see `xurl` skill)
- gh CLI authenticated (for GitHub integration)
- Hermes running (local or VPS)

## X Premium Tier Recommendation

For build-in-public growth, **Premium ($8/mo)** is the right tier:

| Feature | Why it matters for BIP |
|---------|----------------------|
| Blue checkmark | Credibility at 0 followers; higher click-through on profile |
| Reply prioritization | Your replies show higher in threads of bigger accounts — #1 growth lever under 5K followers |
| Creator monetization | Revenue sharing + subscriptions unlock at Premium |
| 50% fewer ads | Followers see more of your content |

**Premium+ ($40/mo) is NOT worth it** because:
- Hermes replaces Grok (higher Grok limits irrelevant)
- xurl + web_search replaces Radar Search
- Articles → link to GitHub/blog instead
- $32/mo difference funds VPS + API costs

**Cost breakdown for the full stack:**
- X Premium: $8/mo
- VPS (Hetzner CX22 / DO): ~$5/mo
- Hermes API (Nous): ~$5-15/mo
- Total: ~$18-28/mo (less than Premium+ alone)

## Social Media Manager Profile Design

### Profile Config

```yaml
# ~/.hermes/profiles/social/config.yaml
model:
  provider: nous
  default: qwen/qwen3.6-flash
  base_url: https://inference-api.nousresearch.com/v1

tools:
  enabled: [web, terminal, file, x_search]
  disabled: [delegation, computer_use]

plugins:
  enabled: [disk-cleanup, icarus]

terminal:
  timeout: 120
```

**Model choice rationale:** Posting is high-volume, low-reasoning. Flash-tier ($0.19/$1.13 per 1M) is 3-5x cheaper than reasoning models with no quality loss for short-form content.

### SOUL.md Traits

The social profile's SOUL should encode:
- Concise, punchy copy (280-char default, use 25k when needed)
- Technical but not jargon-heavy
- Transparent: share failures alongside wins
- Never generic AI-isms ("game-changer", "leverage", "unlock")
- Authentic voice — first person, specific details
- Engagement-first: replies and conversations > broadcast

### Skills to Attach

- `xurl` — posting, replying, searching, engagement
- `draft-post` — execution layer for drafting individual posts/threads
- `brand-review-content` — quality gate before posting (AI-ism detection, voice check)
- `reply-research` — research-first reply drafting (the engagement growth lever)
- `github-pr-workflow` — detect new pushes/PRs for content triggers
- `youtube-content` — if doing video content

## Content Strategy

### Daily Cadence (3-4 posts/day)

| Time (ET) | Type | Example |
|-----------|------|---------|
| 9 AM | Morning intention | "Building X feature today — here's the approach" |
| 12 PM | Progress update | Screenshot/GIF of what's working |
| 5 PM | Wrap-up | "Shipped X. Y broke. Tomorrow: fix Y." |
| Varies | Reply engagement | 15-30 min replying to larger accounts |

### Content Types (rotate)

1. **"Built this today"** — feature, screenshot, GIF, demo
2. **"Debugging hell"** — honest failure story (gets MORE engagement than wins)
3. **"Lesson learned"** — actionable insight from the trenches
4. **"Revenue/metrics update"** — transparent numbers, even $0
5. **Thread** — deep-dive on a technical decision (hook → 5-7 value tweets → CTA)
6. **Question** — specific question to drive engagement

### Weekly Cadence

- **Friday:** Progress thread (like @levelsio's weekly summaries)
- **Monthly:** Revenue/metrics transparency post

### Peak Posting Times (2026 data)

- Primary: Wed–Fri, 9–11 AM ET
- Secondary: Mon–Tue ~10 AM; Sat 8–10 AM; Sun 9 AM–12 PM
- Experiment: Late-night (10 PM–12 AM) for international audiences

### Engagement Strategy (the growth lever)

Reply prioritization is the #1 growth mechanic for accounts under 5K followers:
- Search #buildinpublic, #indiehacker via `xurl search`
- Reply to accounts 2-10x your size with genuine value
- Target: 10-15 quality replies/day
- Never pitch in replies — add insight, ask questions, share related experience

## VPS Deployment Architecture

```
┌─────────────────────────────────────────────┐
│  Linux VPS (always-on)                      │
│  ├── Hermes installed headlessly             │
│  ├── Senna profile (orchestrator)            │
│  ├── Social profile (posting agent)          │
│  ├── Cron jobs (posting schedule)            │
│  ├── xurl (X API)                            │
│  ├── gh CLI (GitHub)                         │
│  └── Gateway (connects to user's devices)    │
└─────────────────────────────────────────────┘
```

### Content Pipeline Flow

```
You code (local Mac)
  → git push to GitHub
  → VPS Hermes detects push (cron poll or webhook)
  → Social profile drafts post about what changed
  → Posts at next peak-time window via xurl
  → Monitors replies via xurl mentions
  → Notifies you (Telegram/Discord) if reply needs personal response
  → Weekly: generates progress thread
```

### Cron Job Setup

```bash
# Morning post — what we're building today
hermes cronjob create \
  --name "bip-morning" \
  --schedule "0 9 * * *" \
  --profile social \
  --skills xurl \
  --prompt "Draft and post a build-in-public morning update. Check recent git commits for context on what's being worked on. Keep it concise, specific, authentic. Post via xurl." \
  --deliver origin

# Midday update — progress check
hermes cronjob create \
  --name "bip-midday" \
  --schedule "0 12 * * *" \
  --profile social \
  --skills xurl \
  --prompt "Draft a midday progress update. Check git log for today's commits. If nothing new, skip silently (don't post filler). If progress exists, post a concise update with specifics." \
  --deliver origin

# Evening wrap-up
hermes cronjob create \
  --name "bip-evening" \
  --schedule "0 17 * * *" \
  --profile social \
  --skills xurl \
  --prompt "Draft an end-of-day wrap-up. What shipped, what broke, what's next. Be honest about failures — they get more engagement than wins. Post via xurl." \
  --deliver origin

# Friday thread
hermes cronjob create \
  --name "bip-weekly-thread" \
  --schedule "0 10 * * 5" \
  --profile social \
  --skills xurl \
  --prompt "Draft a weekly progress thread (5-7 tweets). Hook tweet → what was built → challenges → lessons → what's next → CTA. Post as a thread via xurl." \
  --deliver origin
```

### Engagement Cron (replies)

```bash
# Daily engagement — reply to build-in-public community
hermes cronjob create \
  --name "bip-engagement" \
  --schedule "0 14 * * *" \
  --profile social \
  --skills xurl \
  --prompt "Search X for recent #buildinpublic and #indiehacker posts. Find 5-10 posts from accounts with 1K-100K followers. Reply to each with genuine value — insight, related experience, or a thoughtful question. Never pitch. Never generic. Be specific." \
  --deliver origin
```

## Pitfalls

1. **Don't post filler.** If nothing happened, skip silently. "Working on stuff" posts kill engagement. The cron prompts above check git activity before posting.

2. **Don't automate replies blindly.** The engagement cron should draft replies for review, not post autonomously, until the voice is calibrated. Start with `--deliver origin` so you see what's being posted.

3. **Don't start with automation.** Post manually for the first 200-500 followers to calibrate the voice, learn what resonates, and build authentic relationships. Then hand off to Hermes.

4. **Don't ignore replies.** The algorithm rewards fast reply engagement. If Hermes posts, you should still check replies personally within 1 hour for the first few months.

5. **Don't use Premium+.** The $32/mo savings over Premium+ funds your entire VPS + API stack.

6. **Don't post only wins.** Failure stories get 2-3x more engagement than success stories. Authenticity is the build-in-public moat.

7. **VPS credential management.** xurl credentials (`~/.xurl`) and GitHub tokens need to be set up on the VPS separately from your Mac. Don't copy them — run `xurl auth oauth2` and `gh auth login` on the VPS directly.

8. **Cron timezone.** VPS crons run in UTC. Convert peak ET times: 9 AM ET = 14:00 UTC (EST) or 13:00 UTC (EDT). Adjust seasonally.

## Growth Timeline (realistic expectations)

| Phase | Followers | Focus |
|-------|-----------|-------|
| Foundation (0-200) | Manual posting, voice calibration | Daily updates, engage manually |
| Consistency (200-500) | Reply guy strategy, weekly threads | Start automating posts |
| Momentum (500-1200) | Collaborate, share milestones | Full Hermes automation active |
| Acceleration (1200-2500) | Algorithm boost, inbound DMs | Community building |
| Pre-launch (2500-4000) | Announce products, early access | Monetization begins |

## Related Skills

- `draft-post` — execution layer: draft individual posts, threads, blog posts, emails
## Execution Layer Skills

This skill is the **strategy layer** — what to post, when, and why. The actual writing and quality-checking lives in dedicated execution skills:

| Skill | Purpose |
|-------|---------|
| `draft-post` | Write a single piece of content (X post, thread, LinkedIn, blog, email). Channel-specific structure, hook patterns, voice defaults. |
| `brand-review-content` | Quality gate before posting. AI-ism detection, specificity check, voice consistency, authenticity flags. |
| `reply-research` | Research an X account, then draft a value-add reply. The #1 growth lever under 5K followers. |

**Workflow:** Strategy (this skill) → Draft (`draft-post`) → Review (`brand-review-content`) → Post (`xurl`). For engagement: Research (`reply-research`) → Review → Reply (`xurl`).

These skills were adapted from [Anthropic's knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) (marketing/skills/draft-content, marketing/skills/brand-review, sales/skills/draft-outreach), stripped of enterprise/CRM framing and rewritten for indie-hacker voice.

## Related Skills

- `draft-post` — content execution layer (writing the actual posts)
- `brand-review-content` — quality gate (checking posts before shipping)
- `reply-research` — engagement execution (research + draft replies)
- `xurl` — X API posting mechanics (post, reply, search, media)
- `github-pr-workflow` — GitHub integration for content triggers
- `hermes-agent` — Hermes config, profiles, cron setup
- `foreman-orchestration` — Multi-agent orchestration for complex pipelines
