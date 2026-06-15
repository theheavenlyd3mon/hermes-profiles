---
name: coding-size-limits
description: Keeps code readable. File size limits, function length caps, nesting depth rules. Written for non-coders who need to understand what the AI wrote.
triggers:
  - "code standards"
  - "size limits"
  - "keep it readable"
  - "coding standards"
---

# Coding Size Limits

Code that's too big or too nested is hard to understand. These rules keep it manageable.

## Why This Matters
If code is hard for YOU to read, it's hard to fix when it breaks. Size limits are speed limits — they exist for safety.

## Rules

### File Size
- Sweet spot: 200-400 lines
- Maximum: 800 lines
- If a file exceeds 500 lines, consider splitting it
- Exception: auto-generated files, data files, config

### Function Length
- Maximum: 50 lines
- If a function needs more, break it into named sub-steps
- A function should do ONE thing (if the name needs "and", it's too big)

### Nesting Depth
- Maximum: 4 levels deep
- If you see 5+ levels of `{}`, extract inner logic to a function
- Early returns reduce nesting (return early, return often)

### Variable Naming
- Boolean variables: start with `is`, `has`, `should`, `can`
  - `isActive` not `active`
  - `hasPermission` not `permission`
  - `shouldRetry` not `retry`
- Functions: verb + noun
  - `getUser()` not `user()`
  - `validateInput()` not `input()`
- Constants: UPPER_SNAKE_CASE
  - `MAX_RETRIES` not `maxRetries` for true constants

### Immutability (CRITICAL)
- Never modify an existing object/array. Always create a new one.
- BAD: `user.name = 'new'`
- GOOD: `const updatedUser = { ...user, name: 'new' }`
- This prevents entire classes of bugs where changing one thing breaks another

### Magic Numbers
- No unexplained numbers in code
- BAD: `if (count > 42)`
- GOOD: `const MAX_ITEMS = 42; if (count > MAX_ITEMS)`
- Exception: 0, 1, -1 are usually obvious

### Imports
- Group imports: external libs first, then internal modules, then types
- No unused imports (clutters code, slows bundling)

## Enforcement
When writing or reviewing code, check against these rules. If something violates a rule, fix it in the same change — don't leave it for later.
