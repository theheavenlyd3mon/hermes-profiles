# Morgan Blackhand operatorfile branch — 2026-05

## Trigger
Lucas shared a Higgsfield avatar breakdown image showing avatar evolution: rejected 48x24 grid test, stencil/glyph contrast test, photoreal final identity lock, and six state cards.

## Durable lesson
Use such breakdown images as **style/reference briefs**, not as direct eikon sources. The full UI sheet is too cluttered for 48x24 terminal rasterization, but its final portrait/state concepts are useful.

## Recommended operatorfile direction
Create a separate comparison candidate, e.g. `morgan-blackhand-operatorfile`:

- Use the original Morgan image as strict identity reference.
- Use the breakdown sheet only as art direction.
- Generate only the avatar portrait source, not the dashboard sheet.
- No UI panels, text, boxes, arrows, barcodes, warning icons, labels, or HUD in the actual eikon plates.
- Photoreal black/zinc/white close-up portrait.
- Pure black background.
- Head, neck, cigar, and high tactical collar fill the frame.
- Face lit like a glyph signal map: strong brow/nose/cheek/mouth planes, deep eye sockets, hard rim light on hair/collar.
- Subtle scanline/dither texture is fine only if it does not obscure the face.

## State overlay guidance
Keep state overlays behind or around the silhouette, never over the face:

- `idle`: cold standby, subtle breathing, cigar ember.
- `listening`: faint circular audio rings behind head.
- `thinking`: restrained particle/processing field behind silhouette.
- `speaking`: waveform behind shoulders; mouth/jaw visibly moves.
- `working`: small data glow behind collar, focused scan.
- `error`: glitch/rim distortion around silhouette; face remains readable.

## QA from generated operatorfile plates
The successful plate direction had clear face/collar/cigar and avoided UI clutter. It was more premium/human than `facecut`, but less glyph-safe. Treat it as the “human operator” branch, not a guaranteed terminal-readability winner.

## Fal balance / partial completion handling
If fal.ai balance dies mid-Kling run after some states finish:

1. Do not claim full animation is complete.
2. Ping-pong and install completed raw Kling states.
3. For missing states, temporary static MP4 placeholders can be generated from plates so Studio still sees a clean video-only source folder.
4. Label the source honestly as partial: list which states are real Kling loops and which are static placeholders.
5. After top-up, rerun only the missing states and replace the placeholders.

## Final handoff language
Tell Lucas the candidate is installed and usable, but clearly flag partial states. Example:

`idle/listening/thinking/speaking are real Kling loops; working/error are static MP4 placeholders because fal balance exhausted mid-run.`
