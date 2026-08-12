---
name: x-landscape-research
description: Use when researching X trends or creating content calendars.
version: 1.0.0
author: senna
triggers:
  - "research what's working"
  - "content calendar"
  - "find accounts to engage"
  - "growth strategy"
  - "what's trending"
  - "who should I follow"
metadata:
  hermes:
    tags: [social-media, x, twitter, research, content-calendar, engagement, growth]
    related_skills: [build-in-public, draft-post, reply-research, xurl]
---

# X Landscape Research

Tactical workflow for researching what's working in a niche, creating content calendars, and identifying accounts to engage with. This is the execution layer that feeds into the build-in-public strategy.

## When to Use

- User asks to research what's working in their niche
- User wants a content calendar for the next 2 weeks
- User wants to find accounts to engage with
- User is starting a build-in-public journey and needs a tactical plan
- User wants to understand engagement patterns in their space

## When NOT to Use

- High-level strategy (what to post, why, when) → use `build-in-public`
- Drafting a specific post or thread → use `draft-post`
- Researching a single account before replying → use `reply-research`

## Inputs to Gather

1. **Niche/topic**: What space are they in? (AI agents, indie hacking, web dev, etc.)
2. **Current account state**: How many followers? What have they posted so far?
3. **Goals**: Engagement, follower growth, lead-gen, community building?
4. **Time commitment**: How much time can they spend daily/weekly?

## Research Workflow

### Step 1: Pull Recent Posts from Target Niche

Use xurl search to gather recent posts in the target space:

```bash
# Search for specific tools/frameworks
xurl search "Hermes agent OR NousResearch OR AI agent" -n 30

# Search for build-in-public content
xurl search "#buildinpublic AI agent" -n 20

# Pull user's own recent posts for context
xurl search "from:username" -n 50
```

Raw `xurl search` JSON is verbose and floods context on multi-query sweeps. For a 4-8 query sweep (the typical landscape scan), use the bundled summarizer instead:

```bash
python3 scripts/x_landscape_sweep.py 12   # 12 results per query (default)
```

Edit the QUERIES list at the top of the script for the niche. Each result prints username, likes/RTs, and the first ~220 chars — enough to spot winners without eating the context window. Read-only (search only, never posts).

### Step 2: Analyze Content Patterns

Look for:
- **Content types getting engagement**: "I built X" posts, daily updates, multi-agent showcases, failure stories, skill comparisons
- **Hot topics**: What specific tools, techniques, or debates are active right now
- **Hashtag performance**: Which tags appear most frequently (#buildinpublic, #AIAgents, #indiehacker, etc.)
- **Engagement hooks**: What opening lines or formats get replies/likes

### Step 3: Identify Engagement Targets

**Already in network**: Look at who the user has replied to, mentioned, or retweeted. These are warm connections.

**New accounts to follow**: Search for accounts in the 1K-50K follower range who are:
- Building similar things
- Using similar tools
- Posting consistently about the topic
- Getting engagement on their content

**Larger accounts (50K+)**: Identify thought leaders for the reply game strategy.

### Step 4: Create Content Calendar

Map out 2 weeks of content using this cadence:

**Week 1: Foundation**
- Monday: Skill/tool deep dive (single post)
- Tuesday: Workflow/setup thread (3-4 tweets)
- Wednesday: Creative output showcase (image carousel)
- Thursday: Debugging/failure story (honest tone)
- Friday: Weekly progress thread (5-7 tweets)
- Weekend: Engagement only, no posting

**Week 2: Momentum**
- Monday: Automation win (demo post)
- Tuesday: Comparison thread (side-by-side outputs)
- Wednesday: Behind-the-scenes (architecture/setup)
- Thursday: Community question (engagement driver)
- Friday: Milestone/lessons learned thread

### Step 5: Document Engagement Strategy

For each target account, note:
- Why they're relevant (similar tools, same niche, complementary audience)
- Specific engagement angle (what to say in replies)
- Current relationship (cold, warm, already connected)

**Daily engagement (15-30 min)**:
- Find 5-10 posts from target accounts
- Reply with genuine value: insight, related experience, or thoughtful question
- Never pitch, never generic praise
- Be specific and authentic

## Output Format

Save the strategy as a markdown file with these sections:

1. **What's Working Right Now**: Content types, hot topics, hashtags
2. **Content Calendar**: 2-week plan with specific post ideas
3. **Accounts to Engage With**: Categorized by relationship status
4. **Quick Wins**: Immediate next steps
5. **Metrics to Track**: Impressions, reply rate, follower growth

## Key Insights

- **Multi-profile setups are unique**: If the user has multiple Hermes profiles (creative, social, dev), that's a differentiator worth showcasing
- **Failure stories outperform wins**: Honest debugging posts get 2-3x more engagement than polished success stories
- **Visual content is gold**: Screenshots, GIFs, and image carousels of actual outputs drive engagement
- **Non-tech backgrounds are strengths**: Emphasize accessibility and real-world application over technical jargon
- **Open source advocacy resonates**: The AI agent community values open source principles

## Example Engagement Angles

**For similar tool users**:
"Saw you're using [tool] for [use case]. I'm doing something similar with [different approach]. Curious how you handle [specific challenge]?"

**For comparison content**:
"Been testing [tool A] vs [tool B]. Here's what I've found: [specific insight]. What's your experience?"

**For educational content**:
"Your breakdown of [concept] is exactly what I needed. Question about [specific detail]—have you found that [specific scenario]?"

**For build-in-public posts**:
"Day [X] is impressive. I'm just starting my BIP journey. What's the biggest lesson you've learned so far?"

## Pitfalls

1. **Don't just list accounts without context.** Explain WHY each account is relevant and what angle to take when engaging. Generic "follow these people" lists are useless.

2. **Don't create a calendar without specific post ideas.** "Post about your progress" is not actionable. Give them the hook, the format, and the angle.

3. **Don't ignore the user's current network.** If they've already engaged with someone, that's a warm connection. Build on it, don't start from scratch.

4. **Don't overcomplicate the calendar.** 2 weeks is enough to plan. Beyond that, you're guessing. Keep it tactical and actionable.

5. **Don't skip the "why" behind content patterns.** If failure stories get more engagement, explain why (authenticity, relatability) so the user understands the principle, not just the tactic.

6. **Desktop/CLI cron jobs deliver locally, not to chat.** When the scan/draft pipeline is automated from a desktop or CLI session, cron output silently resolves to `deliver: local` (no live-delivery channel). Pattern: append a FINAL STEP to every cron prompt telling the agent to `write_file` its output to a dated file (e.g. `~/scratch/drafts/landscape-scan-YYYY-MM-DD.md`) and state the path in its final response. Point the user at the drafts folder; switch to a gateway platform (Telegram/Discord) if one is connected.

7. **Cadence is a user calibration, not a default.** The 2-week template below assumes a healthy posting volume. This user posts manually and prefers **3-5 originals/week (Mon–Fri) + one Friday thread, weekends engagement-only**. Ask or confirm volume before drafting a calendar — a manual poster who gets handed 6 posts/day will ignore the plan.

8. **External skills registry is thin for this niche (audited 2026-07).** If the user asks to "check the skills hub" (agentskills.io / iknowkungfu), expect little: searches for hermes-agent, social media, content calendar, local LLM, video/storyboard skills returned only `kriptoburak/hermes-tweet`, which duplicates `xurl`. The local social-media stack covers the full workflow — say so and move on. Re-audit if the user asks again later; registry contents change.

## Related Skills

- `build-in-public` — strategy layer (what to post, why, when)
- `draft-post` — execution layer (writing the actual posts)
- `reply-research` — engagement execution (research + draft replies)
- `xurl` — X API mechanics (search, post, reply)
