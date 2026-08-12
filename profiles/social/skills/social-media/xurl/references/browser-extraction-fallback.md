# Browser Extraction Fallback for X Posts

When `web_extract` fails on X/Twitter URLs (Firecrawl 504 timeout, rate limit, or empty response), the browser stack provides a reliable fallback.

## The Problem

- `web_extract` uses Firecrawl under the hood. X post scraping frequently times out (504) or returns empty content.
- `browser_snapshot` works but truncates long content (articles, threads). The snapshot caps at ~8K chars.
- X shows a login wall for many posts, but the **DOM still contains the full content** — it's just visually hidden.

## The Solution: browser_console

```python
# Step 1: Load the page
browser_navigate(url="https://x.com/user/status/POSTID")

# Step 2: Extract full text via JavaScript (no truncation)
browser_console(expression="document.querySelector('article')?.innerText")
```

## Why This Works

- X renders post content into the DOM even when the login wall is displayed. The `article` element contains the full post text, engagement metrics, and author info.
- `browser_console` evaluates JavaScript in the page context and returns the result — no character limit like `browser_snapshot`.
- The result is plain text (not HTML), which is ideal for LLM consumption.

## Output Shape

The returned string includes:
```
Display Name
@handle
<post text, full>
<N> replies, <N> reposts, <N> likes, <N> bookmarks, <N> views
```

For X Articles (long-form posts), the full article body is included with section headings preserved.

## Variations

```python
# Get just the tweet text (shorter posts)
browser_console(expression="document.querySelector('[data-testid=\"tweetText\"]')?.innerText")

# Get all tweets in a thread
browser_console(expression="[...document.querySelectorAll('article')].map(a => a.innerText).join('\\n---\\n')")

# Get engagement metrics
browser_console(expression="document.querySelector('article')?.querySelector('[role=\"group\"]')?.innerText")
```

## When to Use

| Condition | Use |
|-----------|-----|
| web_extract succeeded | Use its output (structured markdown, includes comments) |
| web_extract timed out / 504 | Use browser_console fallback |
| Need thread (multiple tweets) | Use browser_console with `querySelectorAll('article')` |
| Auth is available | Use `xurl read POST_ID` (best quality) |

## PITFALL: Login Wall

X sometimes requires login for full access. The browser approach works WITHOUT logging in because:
- The DOM contains the content even when the login overlay is shown
- `browser_console` reads the DOM, not the visual layer
- This may break if X changes their rendering approach

## PITFALL: Rate Limiting

Repeated browser navigations to X may trigger anti-bot detection. If you get a "Something went wrong" page, wait 30-60 seconds before retrying.
