# Gated X Article — technical recovery recipe

## Case: an X Article link (long-form, not a normal post)

Recovery path that worked on a July 2026 link:

1. `browser_navigate` to the status URL. The snapshot renders only a **cover card**
   (title + blurb) for Articles — the body is absent from the accessibility tree.

2. Click the cover card (`t.co/<id>`). Redirect lands on
   `x.com/i/jf/onboarding/web?redirect_after_login=%2Fi%2Farticle%2F<ARTICLE_ID>&mode=login`.
   Extract ARTICLE_ID from the `redirect_after_login` param even though login is gated.

3. With xurl authenticated, fetch via raw API:
   ```
   xurl --app APP_NAME '/2/tweets/<ARTICLE_ID>?expansions=author_id&tweet.fields=created_at,article'
   ```
   then read `data.article.plain_text`. Hits the API, bypassing the rendered-page login wall.

4. web_extract on the article URL returns "Website Not Supported"; on the status URL it
   returns a 504 UPSTREAM_ERROR (Firecrawl timeout). Skip both for X content.

## Why `xurl read` fails on Articles

`xurl read <ID>` expects a post ID and returns nothing for Article IDs. Articles require
the raw `/2/tweets` endpoint with `tweet.fields=article` and `data.article.plain_text`.

## Order of operations summary

browser snapshot (cover blurb) -> click cover -> capture ARTICLE_ID from redirect ->
xurl raw API with article field -> plain_text. Mirror search is the last-resort fallback.
