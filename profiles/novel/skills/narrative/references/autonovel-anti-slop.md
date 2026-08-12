# ANTI-SLOP REFERENCE

A field guide to AI-generated writing patterns. Use this to catch and kill slop in any text.

"Slop" = text that reads like unedited LLM output. Low information density, predictable structure, and vocabulary no human would reach for. The word became [Macquarie Dictionary's 2025 word of the year](https://theconversation.com/slop-vibe-coding-and-glazing-ai-dominates-2025s-words-of-the-year-269688).

---

## BANNED WORDS AND PHRASES

These words are statistically overrepresented in LLM output vs. human writing, per the [slop-forensics](https://github.com/sam-paech/slop-forensics) analysis and [EQ-Bench Slop Score](https://eqbench.com/slop-score.html). Not every use is wrong, but clusters of these are a dead giveaway.

### Tier 1: Kill on sight

These almost never appear in casual human writing. If you see one, rewrite the sentence.

| Slop word | What a human would write |
|---|---|
| delve | dig into, look at, examine |
| utilize | use |
| leverage (verb) | use, take advantage of |
| facilitate | help, enable, make possible |
| elucidate | explain, clarify |
| embark | start, begin |
| endeavor | effort, try |
| encompass | include, cover |
| multifaceted | complex, varied |
| tapestry | (just don't. describe the actual thing.) |
| testament (as in "a testament to") | shows, proves, demonstrates |
| paradigm | model, approach, framework |
| synergy / synergize | (delete the sentence and start over) |
| holistic | whole, complete, full-picture |
| catalyze / catalyst | trigger, cause, spark |
| juxtapose | compare, contrast, set against |
| nuanced (as filler) | (cut it. if the thing is nuanced, show how.) |
| realm | area, field, domain |
| landscape (metaphorical) | field, space, situation |
| tapestry of | (always delete) |
| myriad | many, lots of |
| plethora | many, a lot |

### Tier 2: Suspicious in clusters

Fine in isolation. Three in one paragraph = rewrite.

| Slop word | Plainer alternative |
|---|---|
| robust | strong, solid, reliable |
| comprehensive | complete, thorough, full |
| seamless / seamlessly | smooth, easy, without friction |
| cutting-edge | new, latest, modern |
| innovative | new, original, clever |
| streamline | simplify, speed up |
| empower | let, help, give (someone) the ability |
| foster | encourage, grow, support |
| enhance | improve, boost |
| elevate | raise, improve |
| optimize | improve, tune, tweak |
| scalable | grows with you, handles more load |
| pivotal | important, key, central |
| intricate | complex, detailed |
| profound | deep, significant |
| resonate | connect with, hit home |
| underscore | highlight, stress, show |
| harness | use, put to work |
| navigate (metaphorical) | deal with, work through, handle |
| cultivate | build, grow, develop |
| bolster | strengthen, support |
| galvanize | motivate, push, rally |
| cornerstone | foundation, basis, core |
| game-changer | (be specific about what changed) |

### Tier 3: Filler phrases that add zero information

These are verbal tics. LLMs insert them reflexively. Delete them.

| Phrase | What to do |
|---|---|
| "It's worth noting that..." | Just state the thing. |
| "It's important to note that..." | Just state the thing. |
| "Importantly, ..." | Just state the thing. |
| "Notably, ..." | Just state the thing. |
| "Interestingly, ..." | Just state the thing. (If it's interesting, readers will notice.) |
| "Let's dive into..." | (Delete. Start with the content.) |
| "Let's explore..." | (Delete. Start with the content.) |
| "In this section, we will..." | (Delete. The section heading already says this.) |
| "As we can see..." | (Delete. They can see.) |
| "As mentioned earlier..." | (Delete or just reference the thing directly.) |
| "In conclusion, ..." | (Delete. The reader knows it's the end.) |
| "To summarize, ..." | (Delete or just... summarize.) |
| "Furthermore, ..." | and, also, (or just start a new sentence) |
| "Moreover, ..." | also, and, plus |
| "Additionally, ..." | also, and |
| "In today's [fast-paced/digital/modern] world..." | (Delete the whole clause.) |
| "At the end of the day..." | (Delete.) |
| "It goes without saying..." | (Then don't say it.) |
| "Without further ado..." | (Delete.) |
| "When it comes to..." | (Rewrite: just talk about the thing.) |
| "In the realm of..." | in |
| "One might argue that..." | (Either argue it or don't.) |
| "It could be suggested that..." | (Say it or don't.) |
| "This begs the question..." | (Almost always misused anyway. Delete.) |
| "A [comprehensive/holistic/nuanced] approach to..." | an approach to |
| "Not just X, but Y" | (Restructure. This is the #1 LLM rhetorical crutch.) |

---

## STRUCTURAL SLOP PATTERNS

Slop isn't just vocabulary. The skeleton of the writing betrays it.

### The "topic sentence" machine

LLMs default to a rigid paragraph template: **topic sentence -> elaboration -> example -> wrap-up**. Every paragraph. Same rhythm. Human writing varies: sometimes the point comes last, sometimes there's no explicit topic sentence, sometimes a paragraph is one line.

**Slop:**
> Error handling is a crucial aspect of software development. When errors occur, they can lead to unexpected behavior and poor user experience. For example, an unhandled null pointer exception might crash the entire application. Therefore, implementing proper error handling is essential for building reliable software.

**Human:**
> Your app will crash. Not "might crash" -- it will. The question is whether you wrote a try/catch or whether your user gets a stack trace at 2 AM.

### List abuse

LLMs love bulleted lists. They use them where prose would be clearer, where a table would be better, and where a single sentence would suffice. Watch for:

- Lists where every item starts with the same grammatical structure ("Ensures...", "Provides...", "Enables...")
- Lists used as a substitute for actually explaining something
- Lists nested 3+ levels deep
- Lists of exactly 3 or 5 items (LLMs gravitate to these counts)

### Symmetry addiction

AI text tends toward suspicious balance. Three pros, three cons. Five steps. Equal-length sections. Real writing is lumpy. Some sections are long because the topic is complex. Some are two sentences because that's all there is to say.

### The hedge parade

LLMs hedge constantly: "can", "may", "might", "could potentially", "it's possible that". Human experts state things. If you know it, say it. If you don't, say you don't.

**Slop:** "This approach may potentially help improve performance in some cases."
**Human:** "This is faster." (or "We haven't benchmarked this yet.")

### Transition word addiction

If every paragraph starts with a transition word, the text is probably AI. Scan paragraph openings:

- "However, ..."
- "Furthermore, ..."
- "Additionally, ..."
- "Moreover, ..."
- "Consequently, ..."
- "Nevertheless, ..."

Human writers don't chain these. They start paragraphs with the actual subject.

### The "not just X, but Y" construction

This is the single most overused rhetorical pattern in LLM output. It appears in nearly every model's top trigram lists per [slop-forensics](https://github.com/sam-paech/slop-forensics). Kill it.

**Slop:** "This isn't just a tool -- it's a paradigm shift in how we think about development."
**Human:** "This tool changes how we develop." (or better: show how, specifically)

### Em dash overload

LLMs overuse em dashes (--) where humans would use commas, parentheses, or just write two sentences. One or two em dashes per page is fine. Five per paragraph is a tell. [Source](https://arxiv.org/html/2509.19163v1)

### Sycophantic openings

Watch for responses that start by praising the question or rephrasing it:

- "Great question!"
- "That's an excellent point."
- "Absolutely! Let me explain..."
- "You raise an important consideration."

This is called "glazing" -- excessive flattery. [Collins Dictionary shortlisted it for 2025 word of the year](https://phys.org/news/2025-12-slop-vibe-coding-glazing-ai.html).

### The false-depth pattern

LLMs simulate depth by:
1. Restating the problem in fancier words
2. Listing obvious considerations
3. Concluding with a vague call to action or "it depends"

None of this adds information. Real depth comes from specific details, data, edge cases, and hard-won experience.

---

## TONE GUIDELINES BY CONTEXT

### Academic paper

**Goal:** Dense, precise, every claim backed by citation. No performative enthusiasm.

| DO | DON'T |
|---|---|
| "We observed a 12% reduction in loss (Table 2)." | "We observed a significant and noteworthy reduction in loss." |
| "This contradicts prior work [3]." | "Interestingly, this finding challenges the conventional wisdom." |
| "The method fails on sequences longer than 512 tokens." | "While the method performs well in many cases, there may be limitations with longer sequences." |
| State findings directly. Short sentences. | Hedge with "may", "might", "could potentially" unless genuinely uncertain. |
| Use field-specific jargon precisely. | Use fancy words for their own sake ("utilize" instead of "use"). |
| "Prior work shows X [ref]. We show Y." | "It is worth noting that previous research has delved into this area extensively." |

### Blog post

**Goal:** Has a voice. Opinionated. Uses "I" and "we". Can be funny. Reads like a person wrote it, because a person did.

| DO | DON'T |
|---|---|
| "I spent two days debugging this. Here's what I found." | "In this comprehensive guide, we will explore the intricacies of debugging." |
| "This is broken and everyone knows it." | "While there are certainly areas for improvement, the current approach has its merits." |
| Start with the punchline. | Warm up for three paragraphs before getting to the point. |
| Use contractions. Write how you talk. | Write like you're defending a thesis. |
| Have opinions. Be wrong sometimes. | Present perfectly balanced "on the other hand" takes on everything. |

### README

**Goal:** Get the reader from zero to running as fast as possible. Terse. Show, don't describe.

| DO | DON'T |
|---|---|
| `pip install thing && thing run` | "To get started with this powerful tool, first ensure you have Python installed..." |
| Show a code example in the first 10 lines. | "This comprehensive library provides a robust set of tools for..." |
| "Requires Python 3.10+." | "This project leverages cutting-edge Python features." |
| Bullet the 3 things it does. | Write a 4-paragraph intro about why the project exists. |
| Link to docs for details. | Put all the docs in the README. |

### Notebook / tutorial

**Goal:** Like talking to a colleague at a whiteboard. Informal but precise. Show your reasoning, not just results.

| DO | DON'T |
|---|---|
| "Here's the weird part --" | "In this fascinating section, we will explore an unexpected finding." |
| "The loss is still garbage. Let's try dropout." | "The results suggest that further optimization may be beneficial." |
| "I expected X. Got Y. That's strange." | "Interestingly, the results deviate from our initial hypothesis." |
| Write like you're pair programming. | Write like you're presenting at a conference. |
| Leave mistakes and corrections visible. | Present a clean linear narrative like everything worked first try. |

---

## AI DETECTION SIGNALS

What detection tools actually look for, based on [Pangram](https://www.pangram.com/research/how-it-works), [GPTZero](https://gptzero.me/), and academic research.

### Statistical signals

| Signal | What it means |
|---|---|
| **Low perplexity** | Text is predictable. Each word is what a model would most likely predict next. Human writing is more surprising. Threshold: perplexity < 50 flags synthetic. |
| **Low burstiness** | Sentence lengths are uniform. Humans mix short punchy sentences with long winding ones. AI stays in a narrow band. Measured as coefficient of variation in sentence length. |
| **Uniform entropy** | Information density stays constant. Humans write dense paragraphs and sparse ones. AI maintains steady density throughout. |
| **Token probability patterns** | Pangram tokenizes text and checks if word choices consistently align with what a language model's probability distribution would predict. |

### Vocabulary signals

| Signal | What it means |
|---|---|
| **Slop word frequency** | [EQ-Bench slop score](https://eqbench.com/slop-score.html) tracks words overrepresented in LLM output vs. human text. Weighted 60% of their composite metric. |
| **Low vocabulary diversity** | LLMs reuse the same words more than humans. Measured by MATTR (Moving Average Type-Token Ratio). |
| **Trigram overrepresentation** | Three-word phrases that appear way more in AI text than human text. Weighted 15% of slop score. |

### Structural signals

| Signal | What it means |
|---|---|
| **Consistent paragraph template** | Same structure repeated across paragraphs. |
| **List-heavy formatting** | Markdown bullet lists where prose would be natural. |
| **Balanced section lengths** | Suspiciously even distribution of content across sections. |
| **Opening/closing formulae** | "In this article..." / "In conclusion..." |
| **Missing personal markers** | No "I", no anecdotes, no specific experiences, no mistakes. |

### What Pangram specifically does

[Pangram](https://www.pangram.com/) uses a deep learning classifier (not perplexity/burstiness heuristics) trained on ~1M documents. It:
1. Tokenizes input text
2. Creates embeddings for each token
3. Runs a classifier that outputs human/AI/AI-assisted probability
4. Highlights specific phrases with elevated AI-signal probability

It flags phrases that are statistically more common in AI output and tells you *how much* more common. [Technical report](https://arxiv.org/html/2402.14873v3).

### Limitations

- All detectors have non-trivial false positive rates
- Short texts (< 100 words) are unreliable to classify
- Newer models are harder to detect than older ones
- Non-native English writers get flagged more often (perplexity-based tools are biased)
- Paraphrased/edited AI text is much harder to detect
- Heavy LLM users can spot AI text ~90% of the time; tools do worse ([source](https://arxiv.org/html/2509.19163v1))

---

## THE ANTI-SLOP CHECKLIST

Run through this after writing or editing any text.

### Word-level

- [ ] Search for Tier 1 banned words. Replace or delete every one.
- [ ] Search for Tier 2 words. If 3+ appear in one paragraph, rewrite.
- [ ] Search for Tier 3 filler phrases. Delete all of them.
- [ ] Count em dashes. More than 2 per page? Cut some.
- [ ] Count "not just X, but Y" constructions. Kill them.

### Sentence-level

- [ ] Read the first word of every sentence in a paragraph. If they're all transitions ("However", "Additionally", "Moreover"), rewrite.
- [ ] Check sentence length variation. If every sentence is 15-25 words, mix in some short ones. And some long ones.
- [ ] Look for hedging chains ("may potentially", "could possibly"). State things or don't.

### Paragraph-level

- [ ] Does every paragraph follow the same template? Break the pattern.
- [ ] Are all paragraphs roughly the same length? Vary them.
- [ ] Does the text have a voice? Could you tell who wrote it? If not, add personality.

### Structure-level

- [ ] Are sections suspiciously balanced in length? Real topics aren't symmetric.
- [ ] Is there list abuse? Convert some lists to prose.
- [ ] Does it start with throat-clearing ("In today's world...", "As we all know...")? Cut to the point.
- [ ] Does it end with a generic call to action or "In conclusion"? End with your actual last point.

### The smell test

- [ ] Read it aloud. Does it sound like a person talking? Or a corporate press release?
- [ ] Would you be embarrassed if someone asked "did AI write this?" If yes, rewrite.
- [ ] Does it say anything specific? Or could you swap the topic and the text would still work? Specificity is the antidote to slop.
- [ ] Is there a single surprising sentence? Human writing surprises. Slop never does.

---

## SOURCES

- [Measuring AI "Slop" in Text (2025)](https://arxiv.org/html/2509.19163v1) - academic paper on slop measurement
- [slop-forensics](https://github.com/sam-paech/slop-forensics) - word/phrase overrepresentation analysis
- [antislop-sampler](https://github.com/sam-paech/antislop-sampler) - runtime slop suppression for LLMs
- [EQ-Bench Slop Score](https://eqbench.com/slop-score.html) - composite slop metric
- [Pangram Labs](https://www.pangram.com/) - AI detection tool and research
- [Pangram technical report](https://arxiv.org/html/2402.14873v3)
- [GPTZero](https://gptzero.me/) - perplexity/burstiness-based detection
- [AI Slop, Suspicion, and Writing Back](https://benjamincongdon.me/blog/2025/01/25/AI-Slop-Suspicion-and-Writing-Back/)
- [Literary Hub: Spotting AI writing](https://lithub.com/heres-a-handy-guide-to-help-you-spot-ai-writing/)
- [Red Flag Words](https://www.blakestockton.com/red-flag-words/)
- [Detecting AI Slop: Techniques & Red Flags](https://www.glukhov.org/post/2025/12/ai-slop-detection/)