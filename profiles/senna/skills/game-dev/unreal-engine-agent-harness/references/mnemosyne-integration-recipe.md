# Mnemosyne Integration Recipe for a Python Agent Harness

Context: adding durable memory to a standalone Python agent (the AgentUnreal UE harness). The harness is not a Hermes profile; it runs its own Python process and owns its own SQLite DB.

## When to use this recipe

- You have a standalone Python agent that is NOT running inside Hermes.
- You want session-scoped memory (recall before task, remember after outcome).
- You want memory to be optional: disable it and the agent still works.

## What to install

```bash
pip install mnemosyne-hermes
```

This pulls `mnemosyne-memory` as a dependency. No separate Hermes install is required for the standalone use case.

## Minimal integration

```python
from pathlib import Path
from typing import Any
try:
    from mnemosyne.core.memory import Mnemosyne
    HAS_MNEMOSYNE = True
except Exception:
    HAS_MNEMOSYNE = False

class Agent:
    def __init__(self, config):
        self.config = config
        self.memory = self._init_memory()

    def _init_memory(self) -> Any:
        if not getattr(self.config, "memory_enabled", False) or not HAS_MNEMOSYNE:
            return None
        return Mnemosyne(
            session_id="agentunreal",
            db_path=Path(self.config.db_path),
            author_id="agentunreal",
            author_type="harness",
        )

    def _memory_remember(self, content: str, importance: float = 0.5, source: str = "tool") -> dict:
        memory_id = self.memory.remember(content, source=source, importance=importance, scope="session")
        return {"memory_id": memory_id, "stored": True}

    def _memory_recall(self, query: str, top_k: int = 5) -> dict:
        return {"memories": self.memory.recall(query, top_k=top_k)}

    def _recall_memory_context(self, user_prompt: str) -> str:
        if not self.memory:
            return ""
        memories = self.memory.recall(user_prompt, top_k=3)
        if not memories:
            return ""
        lines = ["Relevant memory context:"]
        for m in memories:
            lines.append(f"- {m.get('content', '')}")
        return "\n".join(lines)

    def _remember_outcome(self, user_prompt: str, summary: str) -> None:
        if not self.memory:
            return
        try:
            self.memory.remember(
                f"Task: {user_prompt}\nOutcome: {summary}",
                source="agent",
                importance=0.6,
                scope="session",
            )
        except Exception:
            pass
```

## Config fields

```yaml
agent:
  memory_enabled: true
  db_path: "./memory.db"
```

## Tool registration

Only add `memory_remember` and `memory_recall` to the tool registry when `self.memory` is not `None`. Otherwise the LLM may call them and the agent will return an error.

## Testing

A good self-test:

1. Enable memory in config.
2. Instantiate the agent.
3. Call `memory_remember` with a sample fact.
4. Call `memory_recall` with a related query and assert at least one result is returned.
5. Disable memory in config and assert the agent still loads and the memory tools are absent from the registry.

## Pitfall: importing the wrong module

`mnemosyne` is a package with many submodules. The class you want is:

```python
from mnemosyne.core.memory import Mnemosyne
```

NOT `from mnemosyne import memory` or `from mnemosyne import Mnemosyne` directly.

## Pitfall: stale config fields after enabling memory

If the `Config` dataclass gains a new `db_path` field, every constructor call (including tests) must pass it. Update `test_stub.py` or equivalent at the same time you add the field.

## Pitfall: legacy Mnemosyne config warning

On first run you may see stderr like:

```
Legacy provider defaults detected in .../mnemosyne/config.yaml; values may be explicit environment choices and were not rewritten.
```

This is informational. The standalone integration does not need the Hermes Mnemosyne provider config to function.
