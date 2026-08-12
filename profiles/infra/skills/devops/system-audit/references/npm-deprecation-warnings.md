# npm Deprecation Warnings After `hermes update`

## What They Are

During `hermes update`, npm may emit deprecation warnings like:

```
npm warn deprecated inflight@1.0.6: This module is not supported, and leaks memory.
npm warn deprecated glob@7.2.3: Old versions of glob are not supported...
npm warn deprecated rimraf@2.6.3: Rimraf versions prior to v4 are no longer supported
npm warn deprecated @babel/plugin-proposal-private-methods@7.18.6: This proposal has been merged...
npm warn deprecated rcedit@5.0.2: Package no longer supported.
npm warn deprecated boolean@3.2.0: Package no longer supported.
```

## Why They Happen

These are **transitive dependencies** — packages that Hermes's dependencies depend on.
They come from upstream libraries (electron-packager, jest, storybook, etc.) that
haven't updated their own dependency trees yet.

## Impact

**NONE.** These are warnings, not errors:
- The deprecated packages still work fine
- They don't affect runtime behavior
- They don't affect security in any meaningful way for a local agent
- There's even a GitHub issue on hermes-agent about it (#31818)

## What Would Fix It

The upstream packages need to update their deps. Nothing the user can do from the
Hermes side. Upgrading glob/rimraf/inflight locally won't help because npm will
just reinstall the versions the upstream packages require.

## User Guidance

Ignore them. If the user asks about them:
1. Confirm they're cosmetic warnings from transitive deps
2. Confirm no functional impact
3. Note the GitHub issue exists if they want to track it
4. Do NOT attempt to manually upgrade these packages — it won't stick

## Last Seen

2026-05-31: hermes update (v0.15.0 → v0.15.1), all 6 warnings present.
