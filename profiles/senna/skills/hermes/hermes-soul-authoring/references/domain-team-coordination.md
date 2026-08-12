# Domain Team Coordination Patterns

> How to tie domain specialist profiles into a coordinated team. Covers delegate vs profile-native approaches, workflow patterns, and shared document structures.

## Two Approaches

### Delegate Pattern (Subagents)
- Foreman spawns subagents via `delegate_task` with each role's system prompt
- Each subagent gets a fresh context window — no persistent memory
- Good for: prototyping, one-off tasks, portable workflows
- Weakness: agents never learn, every run starts from scratch, token-expensive

### Profile-Native (Recommended for Long-Term)
- Each profile is a real Hermes instance with persistent memory
- Profiles accumulate expertise over time — worldbuilder learns YOUR world, designer learns YOUR style
- Past sessions become recallable context
- Good for: ongoing projects, game dev, any work where agents should get better over time
- Weakness: more setup upfront, need to wire handoffs or shared docs

**User preference (2026-06-08):** Profile-native, goal-based, independent work. User explicitly rejected delegate pattern for long-term game dev because "long term wise, is that the most efficient?" — agents should accumulate memory and expertise.

## Workflow Patterns

### Sequential (Traditional)
```
arch → abilities → worldbuilder → designer → ue5-coder
```
Each agent reads previous output, adds their domain. Good for new features with clear dependencies.

### Goal-Based (Recommended)
1. User writes a concept brief (shared doc)
2. User assigns goals to each profile (via kanban, direct message, or terminal)
3. Each profile works independently on their domain
4. User reviews, iterates, reassigns goals

**Why goal-based wins:**
- No coordination overhead
- Profiles work in parallel
- User maintains control over priorities
- Profiles read others' output as needed (not forced)

## Shared Document Structure

Use a shared vault (Obsidian, markdown directory) as the single source of truth:

```
vault/
├── Design/
│   ├── 00-concept.md        ← user writes the game brief
│   ├── 01-architecture.md   ← arch output
│   ├── 02-gameplay.md       ← abilities output
│   ├── 03-narrative.md      ← worldbuilder output
│   ├── 04-visuals.md        ← designer output
│   └── 05-implementation.md ← ue5-coder output
├── World/                   ← worldbuilder's domain
├── Systems/                 ← abilities' domain
└── References/              ← shared references
```

Each profile owns their section. They read others' sections as needed. No forced handoffs.

## Team Skill Pattern

Create a shared skill (e.g., `game-design-team`) that any profile can load to understand:
- Who the teammates are
- What each teammate owns
- Where the shared docs live
- Cross-domain rules (e.g., "lore is king", "abilities need counterplay")

This skill gets installed to all profiles via the installer's `install_shared_skills()` function.

## Pitfalls

### Creating profiles that already exist
**Always check existing repos/structures before creating new profiles.** The windowshermes repo already had worldbuilder, abilities, ue5-coder, designer, and arch — I wasted time creating duplicates in a temp directory.

### Over-coordinating
Don't force sequential handoffs when goal-based independent work is simpler. The user assigns goals, agents work, user reviews. That's it.

### Missing team context in SOUL.md
Domain specialists need to know who their teammates are, even if they work independently. Include a brief "Team Camaraderie" section in SOUL.md that names the other profiles and how they relate.

## Real Example: Eldrath Game Design Team

| Profile | Role | Domain | Model |
|---------|------|--------|-------|
| worldbuilder | Narrative & Lore | Factions, characters, history | qwen3-coder-next |
| abilities | Gameplay Systems | Combat, GAS, balance | qwen3-coder-next |
| ue5-coder | Implementation | UE5 C++, systems | atomicchat-udt |
| designer | Visual & UX | Art direction, UI | MiMo v2.5 Pro |
| arch | System Design | Architecture, tech choices | darwin-36b |

Shared skill: `game-design-team`
Shared vault: `vault/` (Obsidian)
Workflow: goal-based, user-assigned
