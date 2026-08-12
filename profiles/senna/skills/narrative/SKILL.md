---
name: narrative
description: Full-novel craft + anti-slop pipeline with project mode (ledger, characters, foreshadow, worldbuilding bible), draft→review→revise gates, and stability-trap enforcement at scene/chapter/manuscript scale. Single-scene mode retained. Use for fiction, lore, character docs, dialogue, worldbuilding, or book projects.
version: 2.0.1
---

# Narrative v2 — Craft + Slop Defense + Project Pipeline

Assist with narrative prose: fiction, lore, character backstories, quest text, dialogue, worldbuilding — and full short-novel projects. Grounded, buildable writing. Not abstract exposition.

**Reference files (verbatim, do not edit):**
- `references/autonovel-craft.md` — plot / character / worldbuilding / foreshadowing, each with a mechanical check.
- `references/autonovel-anti-slop.md` — banned words, structural slop, tone, detection signals.
- `references/project-mode.md` — manuscript tree, schemas, gates (this skill's project extension).

Load with `skill_view(name='narrative', file_path='references/…')` when you need exact rule text.

## Modes

| Mode | When | Requires |
|------|------|----------|
| **single-scene** | short tests, one-off prose, game text | nothing bound |
| **project** | multi-chapter novel / short novel | bound `manuscript/{project}/` with state files |

In project mode, refuse chapter assembly and export if ledger/canon/voice are missing or scenes are not reviewed.

**Skill tests / short samples** stay scene-scale. Do not expand into a full book pipeline unless the user asks.

## Tone defaults (this user)

Fantasy / murim / isekai / summoned-world with unspecified tone → **melancholy dark noir martial-arts weight** — cost over glory, irreversible loss, moral ambiguity. Grounded detail over abstract world-tour. Bright adventure only if asked.

---

## Single-scene procedure (v1, retained)

1. **Anchor tone** — name register (dread / restraint / melancholy / bright action). Ask if vague; use tone defaults above for this user's fantasy.
2. **Structure** — one framework from CRAFT §1 (Save-the-Cat | Harmon circle | Sanderson PPP). Prefer MICE + try-fail: middle beats mostly "yes, but…" / "no, and…".
3. **Character before prose** — Three Sliders (proactivity / likability / competence — ≥2 high, or one high with growth) + Wound→Lie→Want→Need (Want ⊥ Need).
4. **System / magic** — Three Laws (CRAFT §3): hard rules, limitations ≥ powers, costs drive decisions, no unforeshadowed power in final 25%.
5. **Draft show-don't-tell** (CRAFT §5) — concrete nouns, earned metaphor, rhythm variation (short → long → short). Zero telling at peaks.
6. **Dual-persona review** — A literary critic (prose, voice, monotony); B fiction professor (character, ethics, beats). Fix top items until "mostly qualified hedges."
7. **Kill slop** (ANTI-SLOP) — Tier-1 zero; Tier-3 delete; em dashes ≤2/page; kill "not just X, but Y"; break topic-sentence templates.
8. **Stability-trap check (mandatory)** — all 7 points below.

---

## Project mode

### Init
1. Scaffold `manuscript/{project}/` via `book-pipeline` `scripts/init_manuscript.py` (preferred) or templates.
2. Write `concept.md` with user (logline, tone, MICE, target length 40–50k default).
3. Seed character sheets, `plot-ledger.md`, `foreshadow-bank.md`, `worldbuilding.md`, `canon.md`.
4. One-time **voice calibration** → `voice-profile.md` (see book-pipeline style-revision playbook §3).
5. Bind via optional `manuscript.yaml` (`title`, `framework`, `target_words`, `voice_profile`).

### Continuity ledger (read every draft/review)

| File | Role |
|------|------|
| `canon.md` | Truth ledger — names, rules, geography, dates. New facts go here, not silent intro. |
| `plot-ledger.md` | Beats + %mark + status (`planned` / `drafted` / `reviewed` / `done`) |
| `foreshadow-bank.md` | plant → payoff (status: open / planted / payoff / dangling / red-herring) |
| `character-sheet.md` or `characters/*.md` | sliders, Lie/Truth, dialogue 8-dims |
| `worldbuilding.md` | pillars + Three Laws + societal implications |
| `voice-profile.md` | register, bans, rhythm targets, metaphor domains |

**Generator loads only what it needs** for the current scene (beat row + relevant characters + last chapter summary) — never the full manuscript.

### Draft (generator stage)
1. Read assigned beat from ledger + voice-profile + relevant character rows.
2. Run single-scene procedure steps 1–5.
3. Frontmatter on scene/chapter file:
   ```yaml
   ---
   scene_id: ch03-sc02
   beat: catalyst
   try_fail: no-and   # yes-but | no-and | no-but | yes-and
   pov: Jin
   status: drafted
   ---
   ```
4. Do **not** self-critique for stability trap at book scale — hand to reviewer.

### Review (separate stage — use `narrative-revisor` or style-revision playbook)
Fresh context. Loads ledger + canon + voice + **one** scene. Never generator reasoning.
- Pass 1 craft/structure
- Pass 2 anti-slop mechanical
- Pass 3 stability-trap 7-point
- Emit JSON handoff (`scene_id`, `issues[]`, `severity`)

### Revise
Drafting agent applies **only** reviewer issues. Re-submit until pass status with zero blocker/major.

### Assemble & chapter gates
Before marking a chapter `done`:
1. **Fact continuity** — new facts added to `canon.md`
2. **Ledger progression** — beats moved planned→drafted→reviewed; no silent skips
3. **Foreshadow** — no dangling past payoff window; no unforeshadowed climax element
4. **Character state** — sliders/arc match sheet
5. **Stability-trap** at chapter grain
6. **Anti-slop** per chapter (Tier-1 zero, em-dash cap)

Export (via `book-writer-pipeline` CLI) only when all chapters `done`.

### Scriptable checks
Run `scripts/check_manuscript.py <manuscript_dir>` for mechanical scans (Tier-1, em-dash density, dangling plants, beat status). Judgment items (moral ambiguity, emotional range) stay human/reviewer.

---

## Stability Trap — non-negotiable (all scales)

| Point | Scene | Chapter | Manuscript |
|-------|-------|---------|------------|
| Characters end truly different | arc advances | checkpoint hit | final vs opening |
| Bad things stay bad | not retconned | loss not undone | ≥1 unresolved |
| Irreversible loss | choice has cost | cost paid | no undo in ledger |
| Information withheld | mystery planted | not all revealed | reader incomplete |
| Moral ambiguity | unclear right | tension held | no clean ending |
| Emotional range | intensity varies | quiet + explosive | full register |
| Real cost per choice | cost stated | accumulates | no free climax |

If a draft rounds a sharp edge safer/generic → rewrite.

---

## Anti-slop (project + single)

- Tier-1 kill on sight; Tier-2 ≤2/paragraph; Tier-3 delete all filler
- Em dashes ≤2/page; zero "not just X, but Y"
- No topic-sentence machine, list abuse, hedge parade, transition addiction
- Fiction AI tells (CRAFT §6): "a sense of…", "eyes widened", "wave of emotion", etc. — kill

Full lists: `references/autonovel-anti-slop.md`.

---

## Pitfalls

- Lists instead of prose for weighty scenes
- Throat-clearing openings ("In this land…")
- Info-dump >100 words without action/dialogue
- Self-review at book scale (stability trap doubles) — use `narrative-revisor` / separate pass
- Ledger drift / voice drift across chapters
- Dumping full manuscript into a 16K–32K context
- Expanding a skill test into a pipeline without being asked (book-scale → `book-pipeline` / `book-writer`)
- Skipping `scripts/check_manuscript.py` before export-ready
- Offering "Act II next?" after a short sample when the user only wanted a test — stop at the sample

## Verify

- [ ] Read aloud — person who has lived, not press release
- [ ] Tier-1 search = zero
- [ ] ≥1 surprising sentence
- [ ] Stability 7/7 at the grain you shipped (scene / chapter / book)
- [ ] Project mode: ledger statuses match reality; no dangling plants at export

## Book-scale ownership

This skill owns **craft inside a scene/chapter**. The `book-pipeline` skill owns architecture, folder convention, export, publish routing, and multi-lane orchestration. The `book-writer` profile owns the loop end-to-end.

When book work spans craft + models + CLI + market + publish: **delegate lanes**. Do not solo the whole novel from one profile.
