# Video Knowledge & Search — Reference

Use this approach whenever answering a question about a video (or image) needs **external knowledge** — anything you can't be certain of from the pixels alone. That includes, but is not limited to:

- **Identifying a specific thing**: what/who/which is this — a model, species, brand, vehicle, aircraft, plant, landmark, building, logo, person, team, product, artwork.
- **Facts about what's shown**: where was this filmed, when did it happen, who made/designed/owns it, what event/competition/edition is this, what is the name/title, what's its significance or backstory.
- **Anything ambiguous**: when the footage is consistent with several possible answers and you'd otherwise be guessing.

If the answer is genuinely obvious from the frames (a generic category like "a dog", "a city street") you don't need to search. But for any *specific* name or fact, ground it.

## Two rules

1. **Watch with `read_video`** (don't run `ffmpeg`/`montage` yourself to view frames — that's what `read_video` is for). To pull a specific frame out as a file, use `save_view` (pass `times=[...]`; it saves the frames and returns paths), NOT ffmpeg.
2. **Verify before you answer.** For any specific name or fact, you MUST confirm it with `image_search` on a clear frame and/or `web_search` before committing. Appearance is not proof — never answer a specific identity/fact from frames alone.

## Why

Frames tell you what something *looks like*, not its *exact name* or the *facts around it*. Many boats look alike; an aircraft silhouette fits several models; a skyline could be one of many cities; a building doesn't show you its architect or its build year. Web evidence is what turns a guess into a reliable answer.

## Tools

- `read_video` — watch the video (`fps`, `budget`, `start_time`, `end_time`).
- `save_view` — save specific frame(s) of a video to image files (pass `times=[...]`; returns the paths). Use this to grab a frame for `image_search` — no ffmpeg.
- `image_search` — reverse image search on an image **file path** (optional `bbox` `[x1,y1,x2,y2]` in 0–1000 coords to isolate the subject). Searching a local image uploads it to the third-party public host `uguu.se`; ask the user for consent and pass `allow_public_upload=true` only after they approve.
- `web_search` — text search to confirm a candidate, identify, or gather facts.
- `web_extractor` — read a promising page in depth.

## How to go about it (adapt to the question — no fixed sequence)

1. **Watch with `read_video` to find what matters.** For a long video, a low-fps overview is a cheap way to orient (e.g. ~32 frames across the whole video, `fps ≈ 32/duration`); then zoom into the relevant segments with higher `fps`/`budget` and `start_time`/`end_time`. Re-read freely.
2. **Decide what knowledge you actually need.** Name the gap: "I need to identify this aircraft", "I need the architect of this cathedral", "I need which championship this is". That gap drives the search.
3. **Ground it.**
   - To search a *visual* (identify an object/place/person): grab the clearest frame with `save_view`, then `image_search` it (use `bbox` to isolate the subject). Cross-check the candidate with `web_search`.
   - To answer a *fact* once you know what you're looking at: `web_search` the question (e.g. "New Cathedral of Cuenca architect"), and open the best source with `web_extractor`.
   - Combine: `image_search` to get a name → `web_search`/`web_extractor` for the fact about it.
4. **Loop as the evidence requires** — look again, search again, refine queries. Let the missing piece drive the next action.
5. **Commit only after verifying.** When independent sources agree, answer; if they conflict or are thin, look at more frames or search more. A specific name or fact always needs search confirmation first (rule 2).
