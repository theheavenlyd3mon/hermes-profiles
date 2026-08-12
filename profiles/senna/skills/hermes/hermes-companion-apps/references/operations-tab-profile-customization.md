# Operations Tab — Profile Display & Customization

The Operations tab in Hermes Workspace (`/operations`) displays your actual Hermes profiles — it fetches them from `/api/profiles/list` which maps to `hermes profile list`. Each profile becomes an agent card in the grid.

## How agent metadata works

Agent metadata (emoji, description, color, system prompt) is stored in **browser localStorage** with keys like `operations:agents:foreman`, `operations:agents:coder`, etc.

### Seed data: `agent-presets.ts`

On first load, `seedAgentPresets()` populates localStorage from hardcoded presets in `hermes-workspace/src/screens/agents/agent-presets.ts`. The shipped presets (sage, builder, scribe, ops, trader, pc1-coder, pc1-planner, pc1-critic) are **examples** — they only matter if a profile happens to match one of those IDs.

### Fallback behavior

If no seed data exists for a profile name, `loadAgentMeta()` generates a hash-based emoji and color:
```ts
function createFallbackEmoji(agentId: string): string {
  const emojis = ['🤖', '🐦', '🔨', '✍️', '📊', '🛰️', '🧠', '🛠️']
  return emojis[hashString(agentId) % emojis.length]
}
```

The hash is deterministic — same profile name always gets the same emoji.

## Customizing for your profiles

Edit `agent-presets.ts` to add entries for your actual profile names. Each entry controls emoji, description, system prompt, and color:

```ts
export const AGENT_PRESETS: Record<string, AgentPreset> = {
  foreman: {
    emoji: '🧠',
    description: 'Orchestrator — routes tasks to the right specialist',
    systemPrompt: 'You are the swarm orchestrator...',
    color: '#3b82f6',
  },
  coder: {
    emoji: '💻',
    description: 'Implementation — builds features and fixes bugs',
    systemPrompt: 'You are a coding specialist...',
    color: '#10b981',
  },
  reviewer: {
    emoji: '🔍',
    description: 'Quality gate — reviews code before merge',
    systemPrompt: 'You are a code reviewer...',
    color: '#f59e0b',
  },
  // ... add as many profiles as needed
}
```

The `systemPrompt` field is cosmetic — it's stored in localStorage but the Operations tab currently doesn't use it for dispatch. It's there for future agent spawning features.

## Key insight for users migrating from defaults

The shipped presets (Sage/Builder/Scribe/Ops/Trader) are **not real agents** — they're just localStorage seed data. If those IDs don't match any profile name on your machine, they never appear in the Operations view. Your profiles appear automatically regardless of whether you customize the presets. The only reason to edit `agent-presets.ts` is cosmetic (emoji/color).