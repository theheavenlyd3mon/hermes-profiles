# Kanban Worker — Detailed Reference

## Workspace Handling

| Kind | What it is | How to work |
|------|-----------|-------------|
| `scratch` | Fresh tmp dir, yours alone | Read/write freely; GC'd when archived |
| `dir:<path>` | Shared persistent directory | Other runs read what you write. Treat as long-lived state. Path guaranteed absolute |
| `worktree` | Git worktree at resolved path | If `.git` doesn't exist, run `git worktree add <path> ${HERMES_KANBAN_BRANCH:-wt/$HERMES_KANBAN_TASK}` from main repo |

## Tenant Isolation

If `$HERMES_TENANT` is set, prefix memory entries with the tenant:
- Good: `business-a: Acme is our biggest customer`
- Bad: `Acme is our biggest customer` (leaks across tenants)

## Good Summary + Metadata Shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, keys on user_id with IP fallback, 14 tests pass",
    metadata={
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14, "tests_passed": 14,
        "decisions": ["user_id primary, IP fallback for unauthenticated requests"],
    },
)
```

**Review-required coding task (block instead of complete):**
```python
import json
kanban_comment(
    body="review-required handoff:\n" + json.dumps({
        "changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"],
        "tests_run": 14, "tests_passed": 14,
        "diff_path": "/path/to/worktree",
        "decisions": ["user_id primary, IP fallback for unauthenticated requests"],
    }, indent=2),
)
kanban_block(
    reason="review-required: rate limiter shipped, 14/14 tests pass — needs eyes on the user_id/IP fallback choice before merging",
)
```

Use `kanban_complete` only when genuinely terminal (typo fix, docs change, research writeup).

**Research task:**
```python
kanban_complete(
    summary="3 competing libraries reviewed; vLLM wins on throughput, SGLang on latency, Tensorrt-LLM on memory efficiency",
    metadata={
        "sources_read": 12, "recommendation": "vLLM",
        "benchmarks": {"vllm": 1.0, "sglang": 0.87, "trtllm": 0.72},
    },
)
```

**Review task:**
```python
kanban_complete(
    summary="reviewed PR #123; 2 blocking issues found (SQL injection in /search, missing CSRF on /settings)",
    metadata={
        "pr_number": 123,
        "findings": [
            {"severity": "critical", "file": "api/search.py", "line": 42, "issue": "raw SQL concat"},
            {"severity": "high", "file": "api/settings.py", "issue": "missing CSRF middleware"},
        ],
        "approved": False,
    },
)
```

## Claiming Cards You Actually Created

Pass ids in `created_cards` on `kanban_complete`. The kernel verifies each id exists and was created by your profile. Phantom ids block the completion with an error.

```python
# GOOD — capture return values
c1 = kanban_create(title="remediate SQL injection", assignee="security-worker")
c2 = kanban_create(title="fix CSRF middleware", assignee="web-worker")
kanban_complete(
    summary="Review done; spawned remediations for both findings.",
    created_cards=[c1["task_id"], c2["task_id"]],
)
```

```python
# BAD — hallucinated ids
kanban_complete(
    summary="Created remediation cards t_a1b2c3d4, t_deadbeef",
    created_cards=["t_a1b2c3d4", "t_deadbeef"],  # gate rejects
)
```

If `kanban_create` fails, the card was NOT created — don't include a phantom id.

## Block Reasons That Get Answered Fast

Bad: `"stuck"` — no context.
Good: one sentence naming the specific decision. Leave longer context as a comment.

```python
kanban_comment(
    task_id=os.environ["HERMES_KANBAN_TASK"],
    body="Full context: I have user IPs from Cloudflare headers but some users are behind NATs with thousands of peers.",
)
kanban_block(reason="Rate limit key choice: IP (simple, NAT-unsafe) or user_id (requires auth, skips anonymous endpoints)?")
```

## Heartbeats Worth Sending

Good: `"epoch 12/50, loss 0.31"`, `"scanned 1.2M/2.4M rows"`, `"uploaded 47/120 videos"`.
Bad: `"still working"`, empty notes, sub-second intervals. Every few minutes max; skip entirely for tasks under ~2 minutes.

## Retry Scenarios

If `kanban_show` returns `runs: [...]` with closed runs, you're a retry. Don't repeat the failed path.

- `outcome: "timed_out"` — hit `max_runtime_seconds`. Chunk the work or shorten it.
- `outcome: "crashed"` — OOM or segfault. Reduce memory footprint.
- `outcome: "spawn_failed"` + error — usually profile config issue. Ask via `kanban_block`.
- `outcome: "reclaimed"` — operator archived the task. Check status carefully.
- `outcome: "blocked"` — previous attempt blocked; unblock comment should be in thread.

## Notification Routing

Add `notification_sources` to `~/.hermes/config.yaml` for cross-profile notifications:
- `notification_sources: ['*']` — all profiles
- `notification_sources: ['default', 'zilor-ppt']` — specific profiles
- Omitting keeps default (profile isolation)

## DO NOT

- Call `delegate_task` as substitute for `kanban_create`
- Call `clarify` — no live user. Use `kanban_comment` + `kanban_block` instead
- Modify files outside `$HERMES_KANBAN_WORKSPACE` unless task body says to
- Create follow-up tasks assigned to yourself
- Complete a task you didn't finish — block it instead

## Pitfalls

**Task state can change between dispatch and startup.** Always `kanban_show` first. If `blocked` or `archived`, stop.

**Workspace may have stale artifacts.** Read the comment thread — it explains why you're running again.

**Don't rely on CLI when tools are available.** `kanban_*` tools work across all backends. `hermes kanban` CLI fails in containerized backends.

## CLI Fallback

- `kanban_show` ↔ `hermes kanban show <id> --json`
- `kanban_complete` ↔ `hermes kanban complete <id> --summary "..." --metadata '{...}'`
- `kanban_block` ↔ `hermes kanban block <id> "reason"`
- `kanban_create` ↔ `hermes kanban create "title" --assignee <profile> [--parent <id>]`
