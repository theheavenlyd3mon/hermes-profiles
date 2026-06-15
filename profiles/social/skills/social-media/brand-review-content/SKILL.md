---
name: brand-review-content
description: Review a content draft (X post, thread, LinkedIn post, blog, email) against brand voice and authenticity standards before it ships. Flags AI-isms, corporate jargon, unsubstantiated claims, manufactured stakes, and voice inconsistencies. Provides severity-rated findings with before/after fixes. Use after drafting and before posting.
version: 1.0.0
author: senna
triggers:
  - "review this draft"
  - "check this post"
  - "is this on-brand"
  - "audit this content"
  - "brand review"
metadata:
  hermes:
    tags: [social-media, content, review, qa, brand-voice, authenticity]
    related_skills: [draft-post, build-in-public, reply-research]
---

# Brand Review (Content)

Quality gate between drafting and posting. Optimized for indie-hacker / build-in-public content where authenticity is the moat. Adapted from Anthropic's marketing/brand-review skill, stripped of corporate-compliance framing.

## When to Use

- User pastes a draft and asks "is this good", "review this", "any feedback"
- Output of `draft-post` needs a second pass before shipping
- User wants to audit existing posts to catch voice drift over time

## When NOT to Use

- Initial drafting → use `draft-post`
- Reply to someone else's post → use `reply-research`
- Documenting brand voice from scratch → see the "Brand Voice Documentation" section below, then save the result somewhere persistent (skill, memory, or vault note)

## Inputs

1. **Content to review** — paste, file path, or URL. Accept multiple pieces for batch review.
2. **Channel context** — X, LinkedIn, blog, etc. Standards shift by channel.
3. **Brand voice source** — if user has documented voice (in this skill's reference files, memory, or vault), apply it. Otherwise use the defaults below and offer to document afterward.

## Review Dimensions

### 1. AI-ism Detection (the highest-severity check for indie content)

Flag any of these as **HIGH severity**:

| Pattern | Why it kills authenticity |
|---------|---------------------------|
| "leverage", "unlock", "game-changer", "revolutionize" | Universal corporate-AI tells |
| "seamless", "holistic", "robust", "synergy", "cutting-edge" | Same |
| "In today's fast-paced world..." | Opener used by every AI blog |
| "Let's dive in" / "Let's unpack" | Pure filler |
| "It's important to note that..." | Hedge that adds nothing |
| "This is a game-changer for X" | Manufactured stakes |
| Three-bullet structures where one sentence works | Listicle bloat |
| Em-dashes followed by reformulations of the same point | Padding |
| "Not just X, but Y" parallel structure repeated | AI rhythm tell |
| Tweets that end with engagement bait ("Thoughts?", "Agree?") | Generic |

Flag and propose a rewrite for every instance.

### 2. Specificity Check

For build-in-public content specifically:

- Are there real numbers? ("47 users" beats "some users")
- Are products/tools named? ("Hermes on a Hetzner CX22" beats "my server")
- Are failures named? Or only wins? (Failure stories drive 2-3x engagement)
- Is there a real trigger event? (What happened today, not "thoughts on X")

Flag vague claims as **MEDIUM**. Push the writer toward specifics.

### 3. Voice Consistency

If brand voice is documented (see Documentation Framework below), compare each section against:

- Defined voice attributes (e.g. "warm, dry, technical")
- Tone calibration for the channel (X is punchier than LinkedIn)
- Preferred vs avoided terms
- POV consistency (don't drift between "I" and "we")

If voice is undocumented, evaluate against generic indie-hacker defaults:

- First-person consistent
- Past tense for stories, present tense for live updates
- No marketing-speak
- Honest about scope and impact

### 4. Structural Hygiene

- **Hook** — does the first 8 words earn the click?
- **One idea** — single tweet should have one point, not three
- **Threads** — does each tweet stand alone? Is the structure (setup → body → reversal → CTA) intact?
- **CTAs** — only present if real. No manufactured "DM me" lines.
- **Length** — tight is better. Cut filler ruthlessly.

### 5. Authenticity Flags

Always check:

- **Manufactured stakes** — "This changed everything" when it didn't
- **Borrowed authority** — claims that imply expertise the writer doesn't have
- **Fake humility** — "I'm just a humble builder" patterns
- **Inflated metrics** — rounding, vanity numbers, cherry-picked timeframes
- **Stolen frames** — phrasing that's clearly lifted from another big account

### 6. Hard No's (rarely needed but worth checking)

- Unsubstantiated comparative claims about real competitors
- Health/financial/legal claims without grounding
- Quotes attributed without permission
- Content that punches down

## Output Format

```
## Brand Review: [Content type]

### Summary
- **Verdict:** [Ship / Ship after small fixes / Rework needed]
- **Strengths (1-2 lines):** [what's working]
- **Main issues (1-2 lines):** [headline problems]

### Findings

| # | Issue | Location | Severity | Fix |
|---|-------|----------|----------|-----|
| 1 | [issue] | [quote or section] | High/Med/Low | [specific rewrite] |

### Revised Sections (top 3-5 high-severity)

**Before:**
> [original quote]

**After:**
> [proposed rewrite]

**Why:** [1 line]

### Open Questions
[anything you need from the user to refine further]
```

## After Review

Offer one clear next step. Don't list a menu:

- If verdict is "Ship after small fixes" → "Want me to apply the highlighted fixes and give you the final version?"
- If verdict is "Rework needed" → "The hook needs to change before anything else lands. Want me to redraft from the hook down?"
- If verdict is "Ship" → "Looks good. Want me to post via xurl or hand it back to you?"

## Brand Voice Documentation Framework

When the user wants to define their voice (often after a few reviews), use the template at [`references/brand-voice-template.md`](references/brand-voice-template.md). It has pre-built tables for each section — the user fills it in, the skill references it on every review.

Minimum useful structure (see template for full detail):

1. **Personality** — describe the brand as a person (1 paragraph)
2. **Voice attributes** — 3-5 attributes, each with:
   - "We are: [what this means in practice]"
   - "We are not: [common misinterpretation]"
   - "This sounds like: [example]"
   - "This does NOT sound like: [example]"
3. **Tone calibration** — how voice shifts across X / LinkedIn / blog / email
4. **Preferred terms / avoided terms** — concrete list
5. **POV rules** — first person? "I" or "we"?

### Voice Attribute Spectrums (for picking attributes)

| Spectrum | One End | Other End |
|----------|---------|-----------|
| Formality | Formal, institutional | Casual, conversational |
| Authority | Expert, authoritative | Peer-level, collaborative |
| Emotion | Warm, empathetic | Direct, matter-of-fact |
| Complexity | Technical, precise | Simple, accessible |
| Energy | Bold, energetic | Calm, measured |
| Humor | Playful, witty | Serious, earnest |

Indie-hacker defaults usually land: casual, peer-level, direct, technical-but-accessible, calm, dry-humor.

## Pitfalls

1. **Don't be precious about the user's draft.** If something is mid, say so. Flattery hurts the writer.

2. **Don't auto-rewrite without permission.** Flag issues, propose fixes, let the user decide. Their voice > your suggestion.

3. **Don't over-flag on Low-severity issues.** If a post is 95% good, lead with that and surface only the High/Medium issues. Drowning the user in nitpicks is its own failure mode.

4. **Calibrate severity to channel.** A "leverage" in a LinkedIn post is Medium. In a build-in-public tweet, it's High — different audiences tolerate different things.

5. **Don't review your own drafts.** If `draft-post` produced the content in the same session, the writer's-block bias applies. Ask the user to read it first OR explicitly note "self-review, treat skeptically."

6. **Voice drift is real.** If the user has documented voice, compare to it directly. If they've been posting for 6+ months, the voice has probably evolved — offer to re-document after 5+ reviews.

## Related Skills

- `draft-post` — drafting layer (the thing this skill reviews)
- `build-in-public` — strategy layer (cadence, X Premium, infra)
- `reply-research` — replies are a different beast; this skill is for original content
