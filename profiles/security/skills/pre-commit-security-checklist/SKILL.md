---
name: pre-commit-security-checklist
description: Run before committing code. Catches mistakes Katana can't — secrets in code, missing validation, weak auth, debug leftovers.
triggers:
  - "before commit"
  - "pre-commit"
  - "security check"
  - "ready to commit"
---

# Pre-Commit Security Checklist

Katana blocks attacks from outside. This checklist catches mistakes YOU make.

## When To Use
Run this before every `git commit`. Takes 30 seconds, prevents embarrassing leaks.

## Checklist

### 1. Secrets Scan
```bash
grep -rn 'password\|secret\|api_key\|token\|private_key\|AWS_\|OPENAI_' --include='*.{js,ts,py,env,yaml,yml,json,toml}' . | grep -v node_modules | grep -v .git | grep -v '.example'
```
- No hardcoded passwords, API keys, tokens, or secrets in ANY file
- Check .env files are in .gitignore
- Check config files use environment variables, not literal values

### 2. Input Validation
- All user inputs validated at system boundaries (API routes, form handlers)
- File path inputs checked for directory traversal (no `../`)
- Numeric inputs range-checked
- String inputs length-checked and sanitized

### 3. Injection Prevention
- SQL: Using parameterized queries or ORM (not string concatenation)
- HTML: Output escaped/sanitized (no raw user input in innerHTML)
- Shell: No unsanitized input in `exec`/`spawn`/`system` calls
- JSON: Parsed with try/catch, not eval()

### 4. Authentication & Authorization
- Protected routes actually check auth (not just "TODO: add auth")
- No `bypass_auth` or `skip_validation` flags left in code
- Token/session validation is not optional

### 5. Error Messages
- No stack traces in production responses
- No database table names or internal paths in error messages
- Errors log internally but return generic messages to users

### 6. Debug Leftovers
- No `console.log` in committed code (use logger)
- No `debugger` statements
- No commented-out code blocks (use git history)
- No `TODO: remove this` items that were never removed

### 7. Dependencies
- No `--legacy-peer-deps` or `--force` in lock files
- No known vulnerabilities: `npm audit` or `pip-audit` passes

## Quick One-Liner
```bash
grep -rn 'console\.log\|debugger\|TODO.*remove\|password.*=.*["\x27]\|api_key.*=.*["\x27]' --include='*.{js,ts,py}' . | grep -v node_modules | grep -v test | grep -v '.example'
```

## What To Do If Something Fails
1. Fix it before committing
2. If it's a false positive, document why it's safe in a comment
3. If it's a real secret that leaked, rotate it immediately
