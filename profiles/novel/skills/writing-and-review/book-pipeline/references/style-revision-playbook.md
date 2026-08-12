# Book-Writer Style & Revision Playbook

CREATIVE lane deliverable for the `book-writer` pipeline. Defines (1) the per-project
voice profile, (2) the 3-pass revision loop, (3) author-voice calibration from a 500-word
sample, and (4) the critic/split-reviewer handoff. This is a *process* spec — it does not
draft prose.

Rule source of truth: `narrative` skill's two reference files
(`references/autonovel-craft.md`, `references/autonovel-anti-slop.md`). Where this playbook
says "CRAFT" it means `autonovel-craft.md`; "ANTI-SLOP" means `autonovel-anti-slop.md`.

The DRAFTING agent writes scenes. A SEPARATE REVIEWER stage (this playbook's loop) critiques
them. One profile must not generate and critique its own prose — see §4.

---

## 1. Per-Project Voice Profile

Created once at plan time, stored in `manuscript/{project}/voice-profile.md`, and fed to the
drafting agent in its system prompt. Revised only by the reviewer when calibration drifts.

```yaml
project: {name}
tone_anchor: {dread | restraint | melancholy | bright action}   # from concept.md
register:
  level: {oral | low-literary | literary | elevated}            # sets vocabulary ceiling
  person: {first | close-third | omniscient}
  tense: {past | present}
banned_by_author:        # author-specific additions ON TOP of ANTI-SLOP Tier 1
  - {word_or_phrase}
  - ...                   # e.g. a target author never uses "just", "really", "that"
allowed_register_words:  # words a target author uses OFTEN (calibration seeds, not mandates)
  - {word}
rhythm_targets:
  avg_sentence_len: {words}            # e.g. 14 (Hemingway) vs 28 (Faulkner)
  sentence_len_cv_min: {0.0-1.0}       # CRAFT §6: higher = more human; floor ~0.35
  em_dash_cap_per_page: {n}            # default 2 (ANTI-SLOP)
  paragraph_len_variance: {high|med}   # forbid uniform paragraph lengths
metaphor_domains:        # CRAFT §2 dialogue signatures + §6 earned metaphor
  global: [{domain}]                  # e.g. [maritime, weather]
  per_character:                      # character -> domain mapping
    {char}: {domain}
forbidden_patterns:      # project-specific mechanical bans (regex)
  - {regex}
```

Author-voice profiling fields (`banned_by_author`, `allowed_register_words`,
`metaphor_domains`, `rhythm_targets`) are populated by the calibration step in §3. Never
leave `banned_by_author` empty — even when matching a generic house voice, ban at minimum the
ANTI-SLOP Tier-1 list plus the fiction-specific AI tells in CRAFT §6.

---

## 2. The 3-Pass Revision Loop

Every scene/chapter that the drafting agent emits is run through all three passes IN ORDER.
A pass fails if any `blocker` or `major` item is open. The reviewer emits a handoff JSON
(§4) per pass; the reviser (drafting agent, acting only on the reviewer's issues — not
self-critiquing) applies fixes and re-submits. Loop until a pass returns zero blocker/major.

Scope rule: Pass 1 and Pass 3 read the manuscript state files (`character-sheet.md`,
`plot-ledger.md`, `foreshadow-bank.md`, `worldbuilding.md`) to check cross-chapter
consistency. Pass 2 is local to the scene text only.

### PASS 1 — Craft / Structure  (source: CRAFT)
Mechanical checklists derived from `autonovel-craft.md`. Each item is PASS/FAIL with a
rule_ref.

- [ ] **Plot beats** — `plot-ledger.md` beats present at ~correct % marks; Opening Image and
      Final Image mirror; Catalyst is EXTERNAL; Break Into Two is a CHOICE; Midpoint reverses
      trajectory; All Is Lost contains a death (literal or figurative). (CRAFT §1)
- [ ] **MICE closure** — threads close in reverse order of opening (open M-I-C ⇒ close C-I-M).
      (CRAFT §1)
- [ ] **Try-fail ratio** — ≥60% of middle scenes score "yes, but" or "no, and". (CRAFT §1)
- [ ] **Character sliders** — each named char HIGH on ≥2 of proactivity/likability/competence
      OR HIGH on one with visible growth; none all-low, none all-high-from-start. (CRAFT §2)
- [ ] **Wound→Lie→Want→Need** — Lie statable in one sentence; Truth is its direct opposite;
      Ghost causally explains Lie; Want/Need in tension; midpoint shows Want failing. (CRAFT §2)
- [ ] **Dialogue distinctiveness** — tagless test passes: remove all tags, speaker still
      identifiable via the 8 dims (vocab, length, contractions, tics, Q/vs statement,
      interruption, metaphor domain, directness). (CRAFT §2)
- [ ] **Magic 3 Laws** — limitations ≥ powers in prominence; costs DRIVE plot decisions; no
      unforeshadowed power in final 25%. (CRAFT §3)
- [ ] **Worldbuilding** — ≥1 pillar with depth; ≥2-3 societal implications per speculative
      element; no pure-exposition block >100 words without action/dialogue; iceberg hints
      present. (CRAFT §3)
- [ ] **Foreshadow** — every plant in `foreshadow-bank.md` has a payoff or explained red
      herring; ≥1 scene between plant and payoff; rule-of-three for major threads. (CRAFT §4)
- [ ] **Show-don't-tell** — ZERO telling at emotional peaks/revelations/climax; critical
      moments are action/sensory/dialogue. (CRAFT §5)
- [ ] **Prose craft** — specificity (concrete nouns), surprise (≥1 unpredicted word choice),
      rhythm variation (short→long→short), subtext, earned metaphor from character
      experience, sensory grounding, restraint, quiet scenes present. (CRAFT §6)

### PASS 2 — Anti-Slop Mechanical  (source: ANTI-SLOP)
Grep/regex-verifiable. Run a slop scanner; attach counts to the handoff.

- [ ] **Tier 1 banned words** — zero occurrences (delve, utilize, leverage, facilitate,
      elucidate, embark, endeavor, encompass, multifaceted, tapestry, testament, paradigm,
      synergy, holistic, catalyze, juxtapose, nuanced, realm, landscape, myriad, plethora…).
      Rewrite every sentence containing one. (ANTI-SLOP Tier 1)
- [ ] **Tier 2 cluster** — ≤2 Tier-2 words per paragraph (robust, comprehensive, seamless,
      cutting-edge, innovative, streamline, empower, foster, enhance, elevate, optimize,
      scalable, pivotal, intricate, profound, resonate, underscore, harness, navigate,
      cultivate, bolster, galvanize, cornerstone, game-changer). 3+ in a paragraph ⇒ rewrite.
      (ANTI-SLOP Tier 2)
- [ ] **Tier 3 filler** — delete all filler phrases ("it's worth noting that", "importantly",
      "interestingly", "let's dive into", "furthermore", "moreover", "in today's world",
      "at the end of the day", "when it comes to", "one might argue", …). (ANTI-SLOP Tier 3)
- [ ] **Em dash cap** — ≤2 per page. Over ⇒ convert to comma/paren/two sentences. (ANTI-SLOP)
- [ ] **"Not just X, but Y"** — zero. Restructure. (ANTI-SLOP, #1 crutch)
- [ ] **Topic-sentence template** — break paragraphs that follow
      topic→elaborate→example→wrap. Vary point placement. (ANTI-SLOP structural)
- [ ] **List abuse** — no list where prose/table is clearer; no parallel "Ensures/Provides/
      Enables" openers; no 3/5-item symmetry gravitation; no 3+ deep nesting. (ANTI-SLOP)
- [ ] **Symmetry addiction** — sections not suspiciously balanced in length. (ANTI-SLOP)
- [ ] **Hedge parade** — no "may potentially / could possibly / it's possible that" when the
      fact is known. State it. (ANTI-SLOP)
- [ ] **Transition-word addiction** — scan paragraph openers; not all "However/Furthermore/
      Additionally/Moreover/Consequently/Nevertheless". Start with the subject. (ANTI-SLOP)
- [ ] **False-depth pattern** — no restate-in-fancier-words → list-obvious → vague-CTA.
      (ANTI-SLOP)
- [ ] **Sycophantic openings** — no "Great question!", "Absolutely!", glazing. (ANTI-SLOP)
- [ ] **Fiction-specific AI tells** (CRAFT §6) — kill on sight: "a sense of [emotion]",
      "couldn't help but feel", "the weight of [abstract]", "the air was thick with",
      "eyes widened", "a wave of [emotion] washed over", "a pang of", "heart pounded in
      [his/her] chest", "[raven/dark/golden] hair [spilled/cascaded/tumbled]", "piercing
      [blue/green] eyes", "a knowing smile".

### PASS 3 — Stability-Trap Mandatory Check  (source: CRAFT §7 + book-pipeline pitfalls)
NON-NEGOTIABLE. Runs on the scene AND again at book end. A scene that rounds a sharp edge
into something safer/generic FAILS. All 7 items must hold.

- [ ] **Real change** — character(s) in this scene end TRULY different from how they entered.
- [ ] **Bad stays bad** — not everything is fixed; some harm is left unresolved.
- [ ] **Irreversible loss** — at least one irreversible decision or loss stands; nothing is
      quietly undone.
- [ ] **Withheld information** — reader does not know everything; mystery/delayed payoff
      intact.
- [ ] **Moral ambiguity** — the "right" choice is unclear; no clean good/evil framing.
- [ ] **Emotional range** — intensity varies (quiet, explosive, dread, relief, boredom,
      wonder) — not a flat line.
- [ ] **Real cost** — every consequential choice carries a real cost. No cost = no choice.

Per-chapter AND book-end: the 7 checks run on each scene; at manuscript completion they run
on the whole arc. Edges round off at scale if only the former runs (book-pipeline pitfall).

---

## 3. Author-Voice Calibration (500-word sample)

Goal: derive the voice-profile fields in §1 from a ~500-word target-author sample so the
drafting agent can match register without copying content.

**Input:** one contiguous ~500-word passage of the target author's prose (not the drafting
agent's own output, not a synopsis).

**Extraction (run a style scanner; record numbers):**

1. `avg_sentence_len` — mean words/sentence.
2. `sentence_len_cv` — stddev/mean of sentence lengths; floor target 0.35 (CRAFT §6, ANTI-SLOP
   burstiness). If sample CV < 0.35, set target to 0.35 and flag drafting agent to vary harder.
3. `metaphor_domains` — list the concrete image-sources the author reaches for (maritime,
   agricultural, medical, mechanical…). These become the allowed earned-metaphor domains
   (CRAFT §6); per-character mapping inferred from which domains attach to which viewpoint.
4. `em_dash_freq` — count; set `em_dash_cap_per_page` = observed/page-equivalent, capped at 2.
5. `vocabulary_level` — MATTR (moving-average type-token ratio) and average word length; sets
   `register.level` ceiling.
6. `banned_by_author` — words the sample NEVER uses but the drafting agent defaults to
   ("just", "really", "that", "simply", "quite"); add to ANTI-SLOP Tier 1.
7. `allowed_register_words` — words the sample uses at 3×+ corpus baseline; seed, not mandate.
8. `abstraction_ratio` — concrete nouns : abstract adjectives (CRAFT §6 pyramid of abstraction,
   Le Guin exercise). Low ratio ⇒ instruct "cut adjectives/adverbs, strengthen nouns/verbs."
9. `sentence_opener_diversity` — distribution of first words; flag if transition-word clustering
   (ANTI-SLOP) exceeds sample norm.

**Build the calibration prompt** (fed to drafting agent, not the reviewer):
> Write in the register of {author}: avg sentence ~{n} words with high length variation
> (CV ≥ {cv}); metaphor domains limited to {domains}; em dashes ≤ {cap}/page; never use
> {banned_by_author}; prefer concrete nouns over adjectives; opener diversity like sample.

**Verify calibration:** have the drafting agent generate a ~200-word uncontrolled sample;
re-run extraction 1–9; require ≤15% deviation from the sample on `avg_sentence_len`,
`sentence_len_cv`, `em_dash_freq`, `metaphor_domains`. If off, tighten the calibration prompt
or add `banned_by_author` entries; re-verify. Do not proceed to chapter drafting until
verified.

---

## 4. The Critic Conflict & Reviewer Handoff

### Why the drafting agent must NOT critique its own prose
- **Commitment bias.** The model that produced a choice cannot impartially flag the choice as
  wrong; it rationalizes.
- **Slop-blindness.** The drafting agent emits the ANTI-SLOP tells (em-dash overuse, "not just
  X but Y", Tier-1 words). It is the least able observer of its own tells — same generator,
  same priors.
- **Stability-trap blindness.** CRAFT §7 shows AI favors stability; a self-reviewer will
  "fix" by rounding edges further, the exact failure mode.
- **Context economy.** The drafting model runs at 16K context on a your GPU (book-pipeline model
  note). Re-reading its own long output while also holding drafting instructions splits the
  budget and degrades both jobs. Separating critic from drafter keeps each stage single-purpose.

Therefore: a SEPARATE REVIEWER stage runs §2. The drafting agent only ever *acts* on a
reviewer's issue list; it never originates critique of its own text.

### Handoff format — reviewer → reviser
The reviewer reads the scene + manuscript state files, runs the 3 passes, and emits a JSON
handoff. The drafting agent (reviser role) consumes `{issues}` and rewrites only those spans.

```json
{
  "scene_id": "ch07-sc03",
  "pass": 2,
  "status": "fail",
  "metrics": {
    "tier1_banned": 0,
    "tier2_per_para_max": 2,
    "em_dash_per_page": 2,
    "not_just_x_but_y": 0,
    "sentence_len_cv": 0.41
  },
  "issues": [
    {
      "id": "p2-014",
      "category": "anti-slop",
      "rule_ref": "ANTI-SLOP Tier 1",
      "severity": "blocker",
      "quote": "She delved into the ancient tome.",
      "line": 42,
      "suggestion": "Rewrite without 'delved'; use a concrete verb ('turned the brittle pages')."
    },
    {
      "id": "p1-007",
      "category": "craft",
      "rule_ref": "CRAFT §2 dialogue distinctiveness",
      "severity": "major",
      "quote": "— I will not allow it, he said. — Nor I, she said.",
      "line": 88,
      "suggestion": "Tagless test fails: both speakers use identical cadence. Differentiate via tics/length."
    },
    {
      "id": "p3-003",
      "category": "stability",
      "rule_ref": "CRAFT §7 real cost",
      "severity": "blocker",
      "quote": "He chose exile but kept his title and lands.",
      "line": 130,
      "suggestion": "Choice has no cost. Remove the cushion or add irreversible loss."
    }
  ],
  "severity_gate": {
    "blocker": "must fix before next chapter may draft",
    "major": "fix within this revision pass",
    "minor": "batch-fix; non-blocking"
  }
}
```

**Severity gate (enforced by orchestrator):**
- `blocker` → scene cannot advance; reviser must clear all before next chapter drafts.
- `major` → clear within the current pass loop.
- `minor` → accumulate; fix in a batch pass; non-blocking.

**Loop termination:** a pass returns `status: "pass"` with zero `blocker`/`major` issues.
All three passes must pass before the scene enters `chapters/` for assembly. The reviewer re-
emits `scene_id` + `pass` + `status` so the orchestrator tracks per-scene progress against
`plot-ledger.md`.

**Consistency hook:** the reviewer cross-checks `issues` against `character-sheet.md` (sliders,
dialogue signature), `plot-ledger.md` (beat % marks), `foreshadow-bank.md` (plant/payoff), and
`worldbuilding.md` (3 laws) — flagging drift the local Pass-2 scanner cannot see. This is the
cross-chapter enforcement the `narrative` skill explicitly does NOT provide at book scale.
