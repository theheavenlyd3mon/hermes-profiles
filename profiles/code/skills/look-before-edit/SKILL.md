---
name: look-before-edit
description: Forces investigation before editing code. Prevents breaking things by checking who uses the file first. Inspired by ECC's GateGuard.
triggers:
  - "before editing"
  - "look before"
  - "check dependencies"
  - "safe to edit"
---

# Look Before Edit

Before changing a file, check what connects to it. Prevents cascade failures.

## When To Use
Before making any code change that isn't a brand-new file. Especially for:
- Modifying API routes or handlers
- Changing shared utilities or helpers
- Updating type definitions or interfaces
- Modifying config files
- Touching database schemas

## Steps

### 1. Find Who Imports This File
```bash
# For JS/TS files
grep -rn "from.*['\"].*FILENAME\|require.*FILENAME\|import.*FILENAME" --include='*.{js,ts,jsx,tsx}' . | grep -v node_modules

# For Python files
grep -rn "import.*FILENAME\|from.*FILENAME" --include='*.py' . | grep -v __pycache__
```

### 2. Check What This File Exports
- Read the file's exports/functions/types
- Understand what other code depends on

### 3. Check Data Flow
- What arguments does this function take?
- What does it return?
- What side effects does it have (DB writes, API calls, file I/O)?

### 4. Read The User's Actual Request
- What specifically did they ask for?
- What's the MINIMUM change needed?
- Am I about to change more than asked?

### 5. Make The Change
- Only after completing steps 1-4
- Change the minimum necessary
- Preserve existing behavior for anything not explicitly asked about

## Red Flags (Stop and Ask)
- The file is imported by 10+ other files → high blast radius
- Changing a function signature → will break callers
- Modifying a config that other services read
- Database schema change → needs migration plan
- Deleting exports that other files use

## What NOT To Do
- Don't refactor while fixing a bug (separate PR)
- Don't "improve" code that wasn't asked about
- Don't change variable names for style (breaks git blame)
- Don't add features the user didn't request
