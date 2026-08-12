---
name: x-content-extraction
description: >
  Recover and review content from X/Twitter links — especially long-form X Articles
  (x.com/i/article/ID) and gated posts — when the normal web tools fail, and review
  promotional X articles for affiliate/funnel framing. Use whenever the user drops an
  x.com link, says "review this article on X", or asks to read an X post/thread that
  web_extract or Firecrawl can't reach.
category: social-media
tags: [x, twitter, xurl, article, content-extraction, funnel-review, affiliate-spotting]
---

# X Content Extraction & Review

Recovering X article/post text is non-trivial because X gates long-form **Articles**
behind a login wall and the standard web-scraping path is unreliable. This skill is the
fallback ladder that actually works, plus a review pattern for the promotional articles
that dominate X AI-content.

## Trigger

- User shares an `x.com/.../status/...` or `x.com/i/article/...` link.
- User says "review this article on X", "read this post", "what does this X thread say".
- web_extract / Firecrawl returned empty, timed out (504 UPSTREAM_ERROR), or said
  "Website Not Supported" for an X URL.

## Recovery ladder (try in order)

1. **Browser snapshot (works for most posts).** `browser_navigate` to the status URL.
   The accessibility-tree snapshot often reveals the post text, author, timestamp, and
   view count without a login. Long-form **Articles** show only a cover card + blurb here
   (the click-to-open article view is login-gated) — see step 3.

2. **`t.co` redirect resolution.** X post cover cards link through `t.co/<id>`. Following
   that redirect lands on `x.com/i/article/<ARTICLE_ID>` (extracted from the
   `redirect_after_login` query param). Note the ARTICLE_ID even if login is required.

3. **xurl raw API (best for X Articles, requires xurl auth).** If xurl is authenticated
   on the machine, the bundled `social-media/xurl` skill documents the exact call:
   ```
   xurl --app APP_NAME '/2/tweets/<ARTICLE_ID>?expansions=author_id&tweet.fields=created_at,article'
   ```
   then read `data.article.plain_text` from the JSON. This bypasses the login wall
   because it hits the API, not the rendered page. (APP_NAME = the user's authenticated
   X app; don't inline secrets — see the xurl skill's secret-safety rules.)

4. **Mirror / search fallback.** `web_search` the article title or a distinctive quoted
   phrase — promo pieces are often reposted to Instagram, YouTube, Skool, or blogs where
   the full text is readable. Last resort only.

## Review pattern for promotional X articles

AI-content X articles are frequently **affiliate lead-gen**. Don't take the framing at
face value. Apply:

- **Separate marketing claim from technical fact.** Verify each load-bearing claim against
  an official source (e.g. for "Hermes ships xurl" → the Hermes docs; for model claims →
  the vendor's own announcement). Mark verified (✅), overstated (⚠️), or unverified.
- **Spot the funnel.** Search the author handle + the promo's named product/person. Paid
  communities ("boardroom", "$X custom automations", coaching), affiliate-portal domains
  (goaffpro, *-goaffpro.com), and "affiliate partner / we earn commission" terms in their
  Terms signal the piece is a funnel, not a neutral tutorial.
- **Flag hidden costs the pitch omits:** you still need your own developer app + OAuth
  credentials, API rate limits apply, and "set-and-forget" quality is on you.
- **State the access caveat first.** If you could not read the full article (login wall /
  tool failure), say so explicitly before reviewing — review the public framing + verified
  claims, not an imagined full text.

## Pitfalls

- web_extract on `x.com` reliably fails (504 timeout or "not supported") — skip it first,
  go straight to the browser or xurl.
- Clicking the article's cover card in the browser often throws "Something went wrong" /
  a login interstitial. Don't loop on it — capture the cover blurb, then use xurl (step 3).
- `xurl read <ID>` is for posts, NOT Articles — Articles require the raw `/2/tweets`
  endpoint with `tweet.fields=article`. Using `read` on an article ID returns nothing.
- X search tool (`x_search`) may be credit-blocked ("personal-team-blocked:
  spending-limit") — don't rely on it; the browser + web_search ladder is more robust.

## Support files

- `references/gated-x-article-recovery.md` — worked example (cover-card → t.co → article
  ID → xurl call) and the funnel-spotting checklist distilled.
