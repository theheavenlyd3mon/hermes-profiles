---
name: debug-artifact-cleanup
description: Scans modified files for debug leftovers before shipping. Catches console.log, debugger, test URLs, and commented-out code.
triggers:
  - "cleanup"
  - "debug artifacts"
  - "ready to ship"
  - "clean up"
  - "before push"
---

# Debug Artifact Cleanup

Find and remove debug leftovers before they reach production.

## When To Use
After a coding session, before `git push`. Also useful when reviewing a branch.

## Scan Commands

### Console.log / Print Debug
```bash
# JS/TS
grep -rn 'console\.log\|console\.debug\|console\.warn\|console\.error' --include='*.{js,ts,jsx,tsx}' . | grep -v node_modules | grep -v test | grep -v logger | grep -v '.min.'

# Python
grep -rn 'print(\|pdb\.\|breakpoint()\|import pdb' --include='*.py' . | grep -v __pycache__ | grep -v test
```

### Debugger Statements
```bash
grep -rn 'debugger' --include='*.{js,ts,jsx,tsx}' . | grep -v node_modules
```

### Commented-Out Code Blocks
```bash
# Look for 3+ consecutive commented lines (likely dead code)
grep -rn '^\s*//' --include='*.{js,ts}' . | grep -v node_modules | grep -v '@' | grep -v 'http' | head -30
```

### Test/Debug URLs
```bash
grep -rn 'localhost:3000\|localhost:8080\|127\.0\.0\.1\|test\.com\|example\.com' --include='*.{js,ts,jsx,tsx,env}' . | grep -v node_modules | grep -v test | grep -v '.example'
```

### TODO/FIXME/HACK Without Ticket
```bash
grep -rn 'TODO\|FIXME\|HACK\|XXX' --include='*.{js,ts,py}' . | grep -v node_modules | grep -v '#[0-9]'
```

### Temporary Hardcoded Values
```bash
grep -rn 'timeout.*=.*[0-9]\{4,\}\|sleep(\|setTimeout.*[0-9]\{4,\}' --include='*.{js,ts}' . | grep -v node_modules | grep -v config
```

## What Counts As An Artifact

| Artifact | Action |
|----------|--------|
| `console.log("test")` | Remove. Use logger. |
| `debugger` | Remove. Always. |
| Commented-out code (3+ lines) | Remove. Git has history. |
| `// TODO: fix this` without issue # | Either fix it or create an issue |
| Hardcoded `localhost` URLs | Move to env var |
| `setTimeout(x, 5000)` magic numbers | Move to config |
| `any` type assertions (TS) | Fix the actual type |

## Auto-Fix Pattern
If you find artifacts in files you edited this session, fix them in the same commit. Don't leave a separate "cleanup" commit — squash it.
