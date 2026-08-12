# web_extract Output Format for X/Twitter Posts

When using `web_extract` to read X posts (the zero-auth fallback), the output follows this structure:

## Per-Post Fields

```
# Post by @handle
Author: Display Name @handle
Posted: <RFC timestamp>
URL: <canonical post URL>
Likes: N | Retweets: N

## Post
> <full post text, blockquoted>

## Top Comments
### 1. @commenter
Author: display name
Posted: <timestamp>
URL: <comment URL>
> <comment text>
Likes: N
```

## Output Characteristics

- Posts over ~5K chars get a "Summary" variant (auto-summarized by the extraction engine).
- Long threads: each tweet in the thread is included sequentially.
- Top comments: typically 3-5 most-engaged replies, with like counts.
- Media descriptions: images/videos are not downloaded but may be described in alt text.
- Links in posts: preserved as-is (t.co shorteners); some resolve to full URLs.

## Batch Extraction Pattern

```python
# Up to 5 URLs per call — batch for efficiency
result = web_extract(urls=[
    "https://x.com/user1/status/AAA",
    "https://x.com/user2/status/BBB",
    "https://x.com/user3/status/CCC",
    "https://x.com/user4/status/DDD",
    "https://x.com/user5/status/EEE",
])
# result["results"] is a list of {url, title, content, error}
```

## Structuring Extracted Intelligence

When extracting actionable intel from post collections, organize by category:

| Category | Signal |
|----------|--------|
| Tools & repos | GitHub URLs, "alternative to X", pricing comparisons |
| Market intel | Mentions of companies, valuations, funding rounds |
| Techniques | Step-by-step instructions, workflows, "how I did X" |
| Opinions/trends | "The theme this week", predictions, hot takes |

For each extracted item, capture: name, what it replaces/does, key differentiator, and any pricing/star-count data mentioned.

## PITFALL: Rate Limits

web_extract does not use X API rate limits (it scrapes public pages). However:
- Excessive rapid-fire calls may trigger X's web anti-bot measures.
- Private/protected posts will return empty or error content.
- Deleted posts return an error object with the URL.
