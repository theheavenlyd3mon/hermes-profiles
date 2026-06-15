---
name: reply-research
description: Research an X account or specific post before drafting a reply, then draft a value-add reply (not a pitch, not generic, not spam). The #1 growth lever for accounts under 5K followers — reply prioritization rewards quality engagement on bigger accounts. Use when targeting a specific tweet or account for engagement, when drafting reply threads, or when running the daily engagement cron.
version: 1.0.0
author: senna
triggers:
  - "reply to"
  - "respond to"
  - "engage with"
  - "research this account"
  - "draft a reply"
  - "reply guy"
metadata:
  hermes:
    tags: [social-media, x, twitter, engagement, growth, reply, build-in-public]
    related_skills: [build-in-public, draft-post, brand-review-content, xurl]
---

# Reply Research

Research-first reply workflow. Adapted from Anthropic's sales/draft-outreach skill, repurposed for X engagement (the #1 growth mechanic under 5K followers).

## When to Use

- User points at a specific tweet or account and asks for a reply
- Daily engagement cron is running (search trending posts → research → draft replies)
- User wants 5-10 quality replies queued for the day
- Replying to someone bigger and needs to bring real value (not generic "Great post!")

## When NOT to Use

- Drafting original content → use `draft-post`
- Reviewing a draft before posting → use `brand-review-content`
- Replying to a friend / known account where research is overkill → just draft directly

## Core Principle

**Research first, draft second.** Generic replies are worse than no reply — they signal you're farming engagement. A reply with one specific reference to the author's other work, a related experience, or a sharp follow-up question outperforms 10 generic "this!"s.

## Workflow

```
+------------------------------------------------------------+
|                     REPLY RESEARCH                          |
|                                                             |
|  Step 1: PARSE TARGET                                      |
|  - Account handle, specific tweet URL, or topic search     |
|                                                             |
|  Step 2: RESEARCH                                          |
|  - xurl: recent posts, pinned tweet, bio                   |
|  - Web search: their site, blog, GitHub, recent press      |
|  - Identify: their current focus, recent wins/losses,      |
|    repeated themes, what they engage with                  |
|                                                             |
|  Step 3: PICK ANGLE                                        |
|  - Trigger event (something they just shipped/posted)      |
|  - Specific reference to their other work                  |
|  - Related experience you can share                        |
|  - Sharp follow-up question                                |
|                                                             |
|  Step 4: DRAFT REPLY                                       |
|  - Short. Specific. Adds value.                            |
|  - No pitch. No "Check out my X". No emoji-spam.           |
|                                                             |
|  Step 5: DELIVER                                           |
|  - Output draft + 1-2 alternatives                         |
|  - User reviews and posts (or pass to brand-review-content)|
+------------------------------------------------------------+
```

## Step 1: Parse Target

Recognize input patterns:

- `"reply to https://x.com/user/status/123"` → specific tweet
- `"reply to @pieter_levels"` → account, find a recent tweet worth engaging
- `"engage with #buildinpublic"` → topic search, find 5-10 candidates
- `"reply to this:"` followed by pasted tweet text → specific content

If the input is ambiguous, ASK before researching. Don't burn API calls on a wrong target.

## Step 2: Research

### Always pull (via `xurl`)

- Last 10-20 tweets from the account
- Pinned tweet (their hill to die on)
- Bio (their self-positioning)
- The specific tweet being replied to and its existing reply chain (avoid duplicating an existing reply)

### Sometimes pull (via web)

- Their blog / site / GitHub if linked in bio
- Recent press, podcast appearances, launches
- Their X audience size (calibrate the reply — different bar for 5K vs 500K account)

### What to extract

- **Current focus** — what are they shipping/talking about this week?
- **Repeat themes** — what do they consistently engage with?
- **Engagement style** — do they reply to strangers? Long replies or one-liners? Friendly or sharp?
- **Trigger event** — did they just ship something, fail at something, ask a question?

## Step 3: Pick Reply Angle

Priority order (use the highest you can support with real research):

1. **Trigger event** — they just shipped, launched, or posted about something specific. Most timely. Engagement opens here.
2. **Specific reference to their other work** — "Reminds me of your point in [post] about X" — shows you're a real reader, not a drive-by
3. **Related experience** — share something you encountered that intersects with their tweet. Pattern: "Hit this exact thing last week with [specifics]"
4. **Sharp follow-up question** — pulls out a detail the original tweet glossed over. Pattern: "Curious — did you ship X first or Y? The order matters because…"
5. **Counter-take with respect** — disagree with substance, not snark. Only use if you can support the position. Reserve for when you genuinely disagree.

Skip if the only angle you have is "generic agreement". Move on to a different target.

## Step 4: Draft Reply

### Reply Templates

**Trigger Event:**
```
[Specific congrats/observation — NOT "congrats!"]. [Sharp follow-up question OR related insight].
```
Example: "The migration to Postgres timing tracks with where we hit pain on SQLite at ~50GB. Did you script the cutover or run them in parallel for a while?"

**Specific Reference:**
```
[Reference to their other work]. [How it connects to current tweet]. [Optional question].
```
Example: "Your thread on charging from day 1 is what made me flip the free tier off last month. Did you find the conversion uplift came mostly from existing free users or new signups?"

**Related Experience:**
```
Hit this exact thing [time context]. [Specific detail of your experience]. [What you learned OR question back].
```
Example: "Hit this exact thing last week with the rate limiter on Cloudflare Workers. Killed it for me at 50 req/s with zero warning. Switched to upstash redis — clean since."

**Sharp Follow-up:**
```
[Specific detail from their tweet they glossed]. [Reason it matters]. [Question].
```
Example: "The 3x conversion lift is interesting — was that 3x from baseline or 3x compared to the previous variant? Different implications either way."

### Reply Length Guide

- **Big account (100K+):** Short. 1-2 sentences. They get hundreds of replies; brevity wins.
- **Medium (10K-100K):** 2-3 sentences with specific detail. They can engage back.
- **Small (<10K):** Longer reply with genuine engagement signals OK; they remember who shows up.

### What to Cut

- "Great post!" / "This!" / "100%" openers — start with substance
- "Just my 2 cents..." — false humility, cut it
- "DM me / Check out my [thing]" — pitch in replies kills your reputation
- More than 1 emoji unless the account uses them heavily and you're matching tone
- Hashtags — never in replies

## Step 5: Output

```
## Reply Research: @[handle] — [tweet topic]

**Account context:**
- Audience: ~[size]
- Current focus: [1 line from research]
- Engagement style: [terse/expansive, friendly/sharp]

**Tweet being replied to:**
> [paste the tweet]

**Angle picked:** [trigger event / specific reference / related experience / sharp follow-up]
**Why:** [1 line]

---

**Draft 1:**
[reply text]

**Draft 2 (alt angle):**
[reply text]

**Draft 3 (shorter version):**
[reply text]

---

**Notes:**
- [Things you guessed / verified]
- [Risks — e.g. "I'm assuming they meant X by 'platform' but it could mean Y"]
```

## Capability by Tool Availability

| Capability | Web only | + xurl | + CRM/notes on account |
|------------|----------|--------|------------------------|
| Read target tweet | Manual paste | Auto-fetch | Same |
| Pull recent posts | Limited | Yes | Yes |
| Pull replies (avoid dupes) | No | Yes | Yes |
| Audience size | Bio scrape | Yes | Yes |
| Prior interaction history | No | Limited | Yes |

xurl is the bare minimum for this skill to be useful. Without it, fall back to manual paste of target tweet + web search for context.

## Daily Engagement Cron Usage

When run via a cron (see `build-in-public` skill for the cron setup):

1. Search recent posts in target tags / from target accounts
2. Filter for accounts in the 1K-100K range (under 1K = small upside, over 100K = noise)
3. Filter for tweets with <50 existing replies (still time to be seen)
4. Filter for trigger events (launches, fails, asks, hot takes)
5. Pick 5-10 candidates
6. Research and draft for each
7. Deliver as a batch for the user to review and post
8. Do NOT auto-post until voice is calibrated (see Pitfall #1)

## Pitfalls

1. **Don't auto-post replies until voice is calibrated.** First 50-100 replies should be human-reviewed. The bar is "would I be embarrassed if this got screenshot-quoted?" If yes, fix.

2. **Don't reply when you have nothing to add.** Skipping is free; bad replies cost reputation. The engagement metric is "quality engagement", not "reply count".

3. **Don't reply to mega-accounts (1M+) without an exceptional angle.** Their replies are saturated. Time better spent on 10K-100K range accounts where reply prioritization (X Premium feature) actually surfaces you.

4. **Don't pitch in replies. Ever.** No "Check out my product", no "I'm building something similar at X". The growth comes from compounding presence, not direct conversion.

5. **Don't farm trigger events you can't actually engage with.** If someone shipped a Rust GPU compiler and you don't write Rust, scroll past. Replying with vague enthusiasm is worse than not replying.

6. **Don't ignore existing replies.** Read the top 5 existing replies before drafting. If your point has been made, find a new angle or skip.

7. **Don't reply to the same account 3+ times in 24h.** Looks like stalking. Space engagement out across different accounts.

8. **Counter-takes are high-risk, high-reward.** Only use when you genuinely disagree, can support the position, and the author is the type to engage with disagreement (research their reply behavior first).

## Related Skills

- `build-in-public` — strategy layer (why reply engagement matters under 5K followers)
- `draft-post` — original content (not replies)
- `brand-review-content` — pass drafts through if voice consistency matters
- `xurl` — actually post the replies, search, pull account data
