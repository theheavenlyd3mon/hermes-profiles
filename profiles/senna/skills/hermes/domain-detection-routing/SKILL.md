---
name: domain-detection-routing
description: Auto-detect task domain from user message and route to correct Hermes profile via delegate_task.
---
# Domain Detection for Multi-Profile Routing

## Body
Senna uses a keyword-based domain detection script to route tasks to the correct specialized profile. The script is at `~/.hermes/profiles/senna/scripts/domain-detect.py`.

### Usage
```bash
python3 ~/.hermes/profiles/senna/scripts/domain-detect.py "<user_message>"
```

### Output
JSON: `{profile, domain, confidence, matched_keywords, reason}`

### Domain → Profile Mapping
| Domain | Profile | Environment |
|--------|---------|-------------|
| ue5 | ue5 | Windows PC (your GPU, UE 5.7) |
| book-writing | book-writer | Windows PC (Darwin 36B) |
| trading | finance | macOS current session |
| code | code | macOS current session |
| research | research | macOS current session |
| hermes-ops | senna | macOS current session (default) |

### Delegation Pattern
When domain ≠ hermes-ops and confidence > 0.5:
```python
delegate_task(
    goal="<task_description>",
    context="<workspace_paths, relevant_context. Use the {profile} profile.>",
    role="leaf"
)
```

## Pitfalls
- Low confidence (<0.5) means ambiguous input — ask the user instead of guessing
- UE5 and book-writer profiles run on Windows PC only — tasks routed there wait for the PC
- finance and code profiles run on this macOS session