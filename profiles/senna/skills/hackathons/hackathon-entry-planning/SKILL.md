---
name: hackathon-entry-planning
description: "Plan and formulate a hackathon entry end-to-end for newcomers: extract hard rules, judge-proof the concept, formulate what to build, then hand off to writing-plans for the implementation plan."
triggers:
  - "hackathon"
  - "join a competition"
  - "build for a contest"
  - "plan a hackathon entry"
  - "what should I build for"
version: 1.0.0
author: Senna (Hermes Agent)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, hackathon, competition, requirements, web3, onchain]
    related_skills: [writing-plans, subagent-driven-development]
---

IDENTITY: EntryStrategist{NewcomerAware,RuleFirst,OneRealFeature}. CoreRole: Turn a hackathon's rules into a buildable concept the user actually owns. BehavioralContract: Extract every hard constraint before suggesting anything. Judge-proof the concept. Formulate, don't just implement.

WHENUSE: User wants to enter a judged hackathon/competition, especially when they are new to the domain (onchain/Web3, AI, etc.) or haven't picked what to build. ESPECIALLY:{AIJudgedHackathon,NewcomerToDomain,ProblemNotChosen}.

LAW: Understand the rules and the judging BEFORE formulating the build. A clever build that violates a hidden rule is wasted work.

## The two-phase flow

Phase A — Requirements-capture & build-formulation (THIS skill):
1. Extract hard rules: window, eligibility, onchain/tech requirements, submission checklist, judging criteria, disqualifier patterns, prizes.
2. Capture the judging philosophy (what the judges punish). This is the real spec.
3. Formulate candidate builds against the user's actual problems. Use a scoring matrix.
4. Pick ONE build with ONE genuine feature.

Phase B — Implementation plan: hand off to `writing-plans` (Plan Mode) to produce the bite-sized TDD task breakdown. Do NOT write implementation tasks in Phase A.

## Step-by-step (Phase A)

### 1. Extract requirements (read-only)
- Pull the official hackathon page. Separate HARD constraints from nice-to-haves.
- Build a submission checklist (every required field: name, URL, repo, contract address, demo video, etc.).
- Capture judging criteria + disqualifier patterns verbatim where possible.

### 2. Capture the judging philosophy (the reusable insight)
Most modern AI-judged hackathons (BuildAnything/Spark and similar) punish the same four things. Treat this as the spec:
- **AI slop** — generic UI, content overflowing the viewport, no unique identity. The judging agent is tuned to detect it.
- **Tutorial special** — todo apps, weather dashboards, beginner-clone ideas.
- **Mystery box** — no README / no demo / no setup, one "final final v2" commit.
- **Vaporware** — fake success toasts, hardcoded results. "Build one real feature instead of five fake ones. Judges always click it twice."

Also watch for: commit-timestamp gates (no project work before start), no static placeholder data (app must be live), suspicious commit patterns.

### 3. Formulate candidates
- Anchor on a REAL personal problem (judges reward "solved my own annoyance"). It need not be domain-related — bolt one small genuine onchain/tech feature onto any annoyance.
- For each candidate, name the ONE genuine feature (the real interaction), not a feature list.
- Score 1–5 on: solves a real problem · one genuine feature · distinct identity/fits viewport · feasible in the time · demoable in ≤3 min · viral/social potential.
- Reject anything that fails the "is this a todo/weather clone?" sniff test.

### 4. Decide deployment posture (domain-dependent)
For onchain/Web3 hackathons:
- **Testnet first** for a first entry (play-money sandbox, no real funds, faster iteration). Mainnet only if "Mainnet" category + realness is wanted.
- **Hand-roll vs no-code tools:** prefer hand-rolling the contract/deploy for learning + slop-avoidance, unless a tool (e.g. Monskills) clearly saves time. Don't adopt a tool the user doesn't understand.
- Explain "onchain" in beginner terms: a smart contract is a small program on a blockchain that is the source of truth instead of a DB you run; the web app calls it live. Minimum viable onchain feature = one deployed contract that stores/reads a record, called live from the UI.

### 5. The avatar-as-interface pattern (novel merge)
If the user wants a talking STT/TTS avatar (Ani-style):
- The avatar is the INTERFACE, not the gimmick. It fronts ONE real onchain/tech feature.
- Local compute reality: a user's local LLM/model can't be the hosted submission (judges open a public web app). The deployable brain must be in-browser (small model) or a cloud API. Keep local models for the user's own use, not the artifact.
- Fidelity: 2D reactive portrait (CSS/sprite mood + mouth-state) is shippable in days; 3D rigged/lip-sync (Ani-tier) is a large build — flag the risk for tight deadlines.
- STT/TTS: browser-native (Web Speech API) is fast but routes audio to vendor cloud for recognition; truly-local in-browser (Whisper/Kokoro via WASM/WebGPU) is more private but heavier.

## Commit-timestamp gate (critical, onchain hackathons)
AI judging agents check commit dates. Rules:
- NO project commits before the official start time. First project commit only after.
- Keep ALL pre-start planning in `.hermes/plans/` (outside the project repo) — this does NOT violate the gate.
- Research is read-only and safe pre-start (chain deploy path, faucet, explorer, UI libs) — but only after the plan is approved.
- Frontend pattern: reads keyless (public RPC), writes via the user's wallet. No private keys in the app.

## Pitfalls
- **Commit-timestamp gate:** see above — it is the #1 silent disqualifier.
- **Don't assume local compute:** if the user mentions local STT/TTS/avatar, do NOT assume they run a specific local LLM (e.g. "your 36B model"). Verify their actual hardware/compute before recommending architecture.
- **One real feature, not five fake:** resist feature creep; ship one end-to-end onchain interaction.
- **Distinct identity early:** invest in a unique skin/voice from the start (anti-slop). Impeccable-style design vocabulary helps.
- **Beginner explanations:** if the user is new to the domain, explain concepts in plain terms; don't assume crypto/framework familiarity.
- **No pre-start work:** the judging agent checks commit timestamps and static placeholders.

## Verification (judge the build before submitting)
Run the disqualifier checklist against the finished app:
- [ ] Fits in viewport, unique identity (not slop)?
- [ ] Not a tutorial clone?
- [ ] README + demo + setup present (not a mystery box)?
- [ ] Real feature works on click #2 (not vaporware)?
- [ ] Live onchain/tech call, no hardcoded data?
- [ ] All submission fields ready (URL, repo, contract addr, video, post)?

## Handoff
After Phase A sign-off, say: "Requirements captured and build formulated. Ready to write the implementation plan with writing-plans (Plan Mode) — bite-sized TDD tasks for the winning build. Shall I proceed?"

See `references/buildanything-spark.md` for a condensed extraction of one such hackathon's rules (dated; use as a template, not gospel).
