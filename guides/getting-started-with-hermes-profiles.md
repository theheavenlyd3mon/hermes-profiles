# Getting Started With Hermes Profiles

> A beginner-friendly orientation to the Hermes Agent profile system: what each profile does, when to use it, and how to compose them into a fleet.

---

## Who This Is For

- New Hermes users who just cloned this repo
- Operators adding a profile to an existing fleet
- Contributors who want to understand the routing map before editing SOUL.md

If you already know what `senna` and `code` do, skip to [Cyber-Blue Specializations](#cyber-blue-specializations) and [Using Educate in the Fleet](#using-educate-in-the-fleet).

---

## How Profiles Fit Together

Hermes is not one agent. It is a team.

```text
You ask a question
    → Senna parses intent, identifies the domain
    → Routes to the right specialist profile
    → Specialist does the work
    → Results flow back through Senna to you
```

Some profiles are orchestrators: they plan, break work into subtasks, and delegate.  
Some are workers: they execute one job well and report back.  
`senna` is the top orchestrator: it never does the specialist work itself, it makes sure the right agent does.

---

## Profiles at a Glance

### Orchestrators

| Profile | Role | Default Model | Typical Use |
|---------|------|---------------|-------------|
| **senna** | Top orchestrator / fleet manager | strong | Single entry point for all requests |
| **code** | Implementation, debugging, review | strong | Features, bugs, PRs, tests |
| **creative** | Design, art, UI, media | strong | Mocks, diagrams, visuals |
| **research** | Investigation, evidence, knowledge | strong | Market research, literature review |
| **security** | Audit, vulnerability, compliance | strong | Code audits, supply chain |
| **infra** | DevOps, containers, deploy | cost-effective | Docker, CI/CD, networking |
| **mlops** | Training, inference, eval | strong | Fine-tuning, benchmarks |

### Workers

| Profile | Role | Default Model | Typical Use |
|---------|------|---------------|-------------|
| **finance** | Trading, market analysis, signals | cost-effective | Thesis, entry/target/stop |
| **knowledge** | Docs, wikis, Obsidian | cost-effective | Vault audits, note cleanup |
| **homelab** | Smart home, IoT, monitoring | cost-effective | Hue, sensors, automations |
| **media** | Library, music, gaming | cost-effective | Radarr/Lidarr, playlists |
| **social** | Content, engagement, voice | cost-effective | Posts, threads, drafts |
| **communication** | Email, messaging, meetings | cost-effective | Triage, summaries, drafts |
| **business** | Strategy, marketing, product | cost-effective | Frameworks, experiments |
| **cyber-red** | Offensive security | strong | Pen tests, exploit PoCs |
| **cyber-blue-cloud** | Cloud security | strong | IAM, GuardDuty/Sentinel/Defender |
| **cyber-blue-compliance** | Compliance & policy | strong | Evidence packs, policy-as-code |
| **cyber-blue-forensics** | Forensics & IR | strong | Preservation, acquisition, timeline |
| **cyber-blue-soc** | SOC & detection engineering | strong | Triage, rule tuning, runbooks |
| **educate** | Teaching design | strong | Lessons, adaptive tutoring, workshops |
| **novel** | Long-form fiction | strong | Plot ledgers, drafting, revision gates |
| **gamehub-mod** | Discord moderation | cost-effective | Triage cards, audit watch, announcements |

---

## Choosing a Model

Profile configs are starting points, not rules.

- **Strong models** when the task needs reasoning, judgment, or long-form synthesis.
- **Cost-effective models** when the task is mechanical, repetitive, or volume-heavy.

Recommendation: leave orchestrators and safety-critical workers on strong models. Use cheaper models for routine file work, batching, and drafts.

---

## How to Add a Profile

1. Create it in Hermes.
2. Copy `SOUL.md` from this repo.
3. Copy the `skills/` directory into your profile.
4. Edit `config.yaml` for your hardware, model access, and runtime needs.
5. Test one task before routing real work to it.

For examples, see the [Research Profile Guide](research-profile-guide.md).

---

## Cyber-Blue Specializations

Defensive security ships as four specialization paths rather than one monolith.

| Path | Best For | Distinct Behavior |
|------|----------|-------------------|
| **cyber-blue-cloud** | Cloud-heavy environments | IAM boundaries, runtime signals, infra hardening |
| **cyber-blue-compliance** | Continuous audit burden | Policy-as-code, evidence packs, review-ready artifacts |
| **cyber-blue-forensics** | Incident-driven work | Preservation-first, acquisition, timelines |
| **cyber-blue-soc** | Detection/SOC teams | Triage discipline, rule tuning, alert fatigue reduction |

**When to run all four:** if your team has separate owners for cloud vs. compliance vs. SOC, split.
**When to run fewer:** if one person wears all hats, pick the one or two that match your workload — **cyber-blue-soc** is the best generalist starting point.

---

## Using Educate in the Fleet

`educate` is your teaching layer. It converts operational output into reusable learning material.

### Common Uses
- Turn research findings into lesson plans and quizzes.
- Generate onboarding docs from real runbooks.
- Produce workshop agendas from incident postmortems.
- Explain newly added profiles to teammates.

### Example Compositions
- `research` + `educate` → investigation becomes a team tutorial.
- `code` + `educate` → PR becomes a teaching example.
- `cyber-blue-forensics` + `educate` → IR timeline becomes a scenario exercise.

### Placement in the Fleet
`educate` is a worker. It should not own production systems. It should consume their output and raise team capability. Route to `educate` only when the goal is teaching, assessment, or documentation for humans.

---

## Personality Rubric (`PersRubric`)

Profiles use the **PersRubric** block in `SOUL.md` to define behavior in a verifiable way. It is a NEO-PI-R–style dimensional personality model written as compact 0–100 scores.

### Why It Exists
- Consistency across sessions and models.
- Testable: you can rate an output against the rubric and spot drift.
- Tunable: change one score instead of rewriting prose rules.

### How to Read It
Each letter is a trait domain. Higher = stronger expression of that trait.

| Domain | Meaning | Example Effect |
|--------|---------|----------------|
| **O** | Openness | Creative exploration vs. standard playbook |
| **C** | Conscientiousness | Procedure adherence, documentation quality |
| **E** | Extraversion | Verbosity, assertiveness, outreach tone |
| **A** | Agreeableness | Conflict avoidance, diplomatic phrasing |
| **N** | Neuroticism | Stress reactivity, caution under threat |
| **etc.** | Supplementary axes (Warmth, Grit, Altruism, Modesty, etc.) | Refines behavioral edge cases |

Profiles are intentionally not neutral. `security` is high-compliance, low-warmth. `media` is higher openness, lower order. The rubric encodes that.

### Editing Safely
- Move one axis at a time.
- Re-test the profile after edits.
- Use org-mode-style markup or compact key=value if your toolchain needs it.

---

## Token Compression (`token-compression`)

### Why It Exists
Profiles accumulate rules, skills, and context over time. Raw context costs tokens. Token compression keeps behavior stable while shrinking prompt size.

### What It Does
- Distills repeated guidance into a compact DSL.
- Preserves edge cases as training pairs rather than long prose.
- Surfaces contradictions explicitly instead of hiding them in paragraphs.

### When to Use
- Long SOUL.md files with overlapping rules.
- Skill sets where only a subset applies to a given task.
- Fleet-wide prompt hygiene when costs or latency matter.

### Relationship to This Repo
- `SOUL.md` is the source of truth.
- `skills/` is the editable surface.
- Compressed artifacts are ephemeral; do not check them in unless they are reproducible build outputs.

---

## Routine Maintenance

- Review profile configs after Hermes updates.
- Trim skills that are not active; unused skills add context cost.
- Rotate stale models after eval review.
- Keep `config.yaml` local and private; keep `SOUL.md` and `skills/` in this repo.
- Revalidate `PersRubric` scores against real outputs when adding new behaviors.
- Rebuild compressed prompt bundles after rubric or skill changes.

