---
name: draft-post
description: Draft a single piece of social content — X post, X thread, LinkedIn post, blog post, or short email — with channel-specific structure, hook patterns, and brand-voice application. Use when the user asks to "write a tweet about X", "draft a thread on Y", "post about today's progress", or any other single-asset content request. Pairs with brand-review (check before posting) and build-in-public (strategy layer).
version: 1.0.0
author: senna
triggers:
  - "draft a post"
  - "write a tweet"
  - "draft a thread"
  - "write a LinkedIn post"
  - "post about"
  - "blog post about"
metadata:
  hermes:
    tags: [social-media, x, twitter, linkedin, content, writing, build-in-public]
    related_skills: [build-in-public, brand-review-content, reply-research, xurl]
---

# Draft Post

Generate a single content asset tailored to one channel. Strategic layer lives in `build-in-public` — this is the execution layer for "I need to ship one good post right now."

## When to Use

- User says "draft a tweet/thread/post about X"
- A cron job from `build-in-public` is triggered and needs to produce the actual draft
- User wants 2-3 variations of the same idea for different channels

## When NOT to Use

- Multi-asset campaign with a calendar → use `campaign-plan` (TBD) or just iterate this skill
- Quality check on existing draft → use `brand-review-content`
- Engagement reply to someone else's post → use `reply-research`

## Inputs to Gather

If any of these are unclear, ASK before drafting. Do not invent context.

1. **Channel** — X post, X thread, LinkedIn, blog, email. Default to X if unspecified.
2. **Topic/Trigger** — what shipped, what failed, what you're thinking about. Specific > abstract.
3. **Goal** — engagement, build-in-public transparency, lead-gen, education, or community signal.
4. **Length constraint** — auto-derived from channel but override if user asks.
5. **Voice** — if user has a configured brand voice (see `brand-review-content` skill for the framework), apply it. Otherwise default to: first-person, specific, no AI-isms, no corporate jargon, dry humor OK, never "leverage" / "game-changer" / "unlock".

## Channel-Specific Structure

### X Post (single tweet, ≤280 chars)

Pattern:
- **Hook in first 8 words** — concrete detail, surprising number, contrarian take, or sharp question
- **One specific point** — never two. Threads exist for that reason.
- **Optional CTA** — only if there's a real ask (link, reply prompt, follow). Don't manufacture one.

Avoid:
- Opening with "Just" or "So"
- Generic engagement bait ("agree?", "thoughts?")
- More than 1 emoji unless writing in a tone where 2-3 fit
- Hashtags inside body text (max 1-2 at the end if needed)

Output 2-3 variants when possible. Different hook angles, same point.

### X Thread (5-10 tweets, optional 25k mode for power users)

Structure:
1. **Hook tweet** — earn the click. Promise something specific.
2. **Setup** — 1 tweet of context for people who don't know you
3. **Body** — 3-7 tweets, one idea per tweet. Use line breaks aggressively.
4. **Reversal or insight** — the moment readers screenshot
5. **CTA** — soft. Follow, reply, link out. Match the goal.

Pitfalls:
- Don't start tweet 2 with "A thread 🧵" — the hook should make people want it
- Don't number tweets unless the content is genuinely a list
- End on substance, not "follow for more"

### LinkedIn Post (150-300 words, paragraph breaks every 1-2 lines)

Structure:
- Hook line, then a blank line
- Setup paragraph (2-3 short lines)
- Substance (3-5 short paragraphs, one idea each)
- Takeaway / insight
- Optional question to drive comments

Tone shift from X: more professional framing, less in-jokes, no shitposting. Same authenticity, dressed differently.

### Blog Post (500-2000 words)

Structure:
- **Headline** — provide 2-3 options. Specific beats clever.
- **Lede** — first paragraph promises what the reader gets and proves the writer earned the read
- **3-5 H2 sections** with descriptive headings
- **Code blocks, screenshots, or specific numbers** wherever possible
- **Conclusion** — what changed for you, what the reader should try
- **CTA** — relevant link, follow, newsletter

SEO is secondary for build-in-public blogs. Voice and specificity win.

### Short Email (newsletter, ≤300 words)

- **Subject line** — provide 2-3 options. Curiosity > clickbait.
- **Preview text** — extends the subject, doesn't repeat it
- **One main idea**, treated like a long-form tweet
- **Sign-off** consistent with brand voice

## Voice Defaults (when no brand voice configured)

If the user hasn't defined their voice, apply these defaults — they match indie-hacker / build-in-public conventions:

- First person, present tense for what's happening now
- Past tense for stories — "I shipped X and Y broke" beats "shipping X"
- Specific numbers over vague claims: "47 users" not "some users"
- Name the thing — products, tools, libraries by name
- Failure stories outperform success stories — write the honest version
- Dry humor lands; forced humor doesn't. Skip if unsure.
- Never use these words: leverage, unlock, game-changer, revolutionize, seamless, holistic, robust, cutting-edge, synergy
- Never start a post with "Just" or "So" (filler openers)

## Workflow

1. **Confirm channel and topic.** Ask if either is unclear. Do not guess.
2. **Pull context.** Check recent git activity, recent posts (via `xurl` if relevant), notes the user references.
3. **Pick the hook angle.** State which hook pattern you're using and why (1 line, not a paragraph).
4. **Draft.** Output 2-3 variants for short content, one full draft for long content.
5. **Annotate.** Brief note on which voice rules were applied, any guesses you made.
6. **Offer next step.** "Want me to run this through brand-review-content?" or "Adapt for LinkedIn?" or "Tighten one of these variants?"

## Output Format

```
## Draft: [Channel] — [Topic]

**Hook angle:** [which pattern, 1 line]

---

[Variant 1 or full draft]

---

[Variant 2 if short content]

---

[Variant 3 if short content]

---

**Voice notes:** [what was applied, e.g. "specific numbers, failure framing, no corporate words"]
**Open questions:** [anything you guessed and want the user to confirm, e.g. "I assumed your goal was engagement — if it's lead-gen, the CTA should change"]
```

## Pitfalls

1. **Don't draft without a trigger.** Generic "thoughts on building in public" posts are filler. If the user can't name what happened today, push back: "What specifically shipped or broke? That's the post."

2. **Don't auto-add hashtags.** Most indie-hacker accounts under 10K followers get nothing from hashtags. Only add if user asks or the post genuinely fits a tagged community.

3. **Don't manufacture stakes.** "This changed everything" when it didn't is the loudest tell of AI-generated content. If the impact was small, say it was small.

4. **Don't write threads when a single tweet works.** Most build-in-public updates are single tweets. Reserve threads for genuine deep-dives.

5. **Don't write in someone else's voice.** If the user has 50+ existing posts, reference 2-3 of them in your draft logic. If they don't, draft conservatively and ask for feedback to calibrate.

6. **Don't end with "DM me if interested" unless that's the real ask.** Most CTAs are filler. Cut them.

## Source

Adapted from Anthropic's knowledge-work-plugins (Apache-2.0). See `references/anthropic-source-notes.md` for origin repo, adaptation decisions, and further mining candidates.

## Related Skills

- `build-in-public` — strategy layer (cadence, X Premium, VPS, cron setup)
- `brand-review-content` — run drafts through voice/quality check before posting
- `reply-research` — drafting replies to other accounts (different workflow)
- `xurl` — actually posting to X
