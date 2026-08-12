# UE Agent Harness Decisions

Context: a user asked for a review of a game-dev agent harness concept and then
scoped a v1 for a single C++ class task.

## Decisions made

### Bridge: standalone file-based protocol

The user explicitly chose a standalone agent over an editor-only script. The
bridge uses a single JSON file polled by both the agent process and a small
listener running inside the Unreal Editor. A stub mode lets the harness be
developed and tested without the editor open.

### Cross-platform dev split

- Build and test the harness on your main dev machine (macOS/Linux) using a
  **stub bridge** that returns canned responses.
- Move the same code to the Windows PC, set bridge to **file**, and run with
  the editor open.
- This avoids the trap of being unable to iterate until sitting at the gaming PC.

### Three lock decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Standalone vs. editor-only | Standalone with file bridge | User needs the agent as its own process; file bridge is the simplest protocol. |
| Sample UE system prompt | Ship one, replaceable | Generic prompt fails on UE macros. A sample UE-aware prompt helps the harness work out of the box. |
| Dry-run mode | Include v1 | Lets the user preview diffs before writes, cheap to add. |

### Memory: optional, behind flag

Mnemosyne (or any persistent memory) is a feature flag, not a dependency. The
agent works without it, using a `progress.md` journal. If enabled, it adds
`memory_remember` and `memory_recall` tools.

## Open questions deferred

- Should the harness support an HTTP bridge in v2?
- Should the sample prompt be shipped as a generic UE prompt or as a
  Tempest Combat Framework + Narrative Pro tuned prompt?
- Is a `snapshot` / `revert` safety tool worth adding before file writes?
