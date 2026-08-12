# X Article retrieval — command recipes & failure modes

## Exact xurl fetch (Route A)
```bash
# 1. Confirm an app has an oauth2 token
xurl auth status

# 2. Fetch the article body to a file (NEVER pipe xurl straight into python3)
xurl --app <APP> '/2/tweets/<ARTICLE_ID>?expansions=author_id,attachments.media_keys&tweet.fields=created_at,article' > /tmp/article.json 2>/tmp/article.err

# 3. Parse (file-based, avoids the warning-line JSONDecodeError)
python3 - <<'PY'
import json
d=json.load(open('/tmp/article.json'))      # if this still errors, the warning line is present:
                                            # inspect /tmp/article.json head; xurl may prefix a line
a=d.get('data',{}).get('article',{})
print('TITLE:', a.get('title'))
print(a.get('plain_text','<none>')[:12000])
PY
```
Body lives at `data.article.plain_text`; headline at `data.article.title`.

## Why the other routes fail (observed)
| Route | Result |
|---|---|
| `web_extract` on x.com status | HTTP 504 `FetchTimeoutError` (Firecrawl) |
| `web_extract` on `x.com/i/article/<id>` | "Website Not Supported" |
| `x_search` (Grok) | `personal-team-blocked:spending-limit` (no credits) |
| `xurl` with depleted app | `402 ... credits-depleted` (type `.../credits-depleted`) |
| `browser_navigate` (logged-out) | redirects to `/i/jf/onboarding/web?...mode=login` — gate |

## Browserbase session (Route B)
- One `browser_navigate` → one session, agent-driven over CDP AND human-visible
  via dashboard → Sessions → Live View (`keepAlive` default true).
- For X Articles the snapshot truncates → use `browser_console` JS eval on the
  `data.article.plain_text` field; fallback `browser_snapshot(full=true)`.
- Paid backend; free plan drops proxies/keepAlive on a 402 but session survives.
