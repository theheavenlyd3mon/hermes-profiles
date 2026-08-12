# Hermes Desktop — Patching the Default Active Profile

**Problem:** Hermes Desktop's React state initializes `activeProfile` as `"default"` on every launch, regardless of which profile is set as the CLI default via `hermes profile use <name>`.

**Root cause:** The line `const [activeProfile, setActiveProfile] = useState("default")` in the Layout component is hardcoded. The main process has `getActiveProfileName()` (reads `$HERMES_HOME/active_profile`) but it's not exposed via IPC to the renderer.

**Two approaches:**

---

## Approach A: Patch the bundled JS (no rebuild needed)

Fastest fix. Modify the compiled/bundled JS inside `app.asar` so the `useState("default")` becomes `useState("<your-profile>")`.

### Prerequisites

```bash
# electron/asar for extracting and repacking
npx @electron/asar --version   # verify available via npx
```

### Steps

1. Extract the entire asar to a working directory:

```bash
mkdir -p /tmp/hermes-patch && cd /tmp/hermes-patch
npx @electron/asar extract "/Applications/Hermes Agent.app/Contents/Resources/app.asar" ./extracted
```

2. Find the minified bundle that contains the Layout component. Look for `"default"` in the renderer assets. The current v0.3.6 uses `index-BmqpM1Xe.js` but this hash will change between versions:

```bash
grep -rn 'useState.*"default"' extracted/out/renderer/assets/
```

This should find exactly one line. Confirm it's the activeProfile init (not a different `useState("default")`):

```bash
grep -rn 'activeProfile.*useState.*"default"' extracted/out/renderer/assets/
```

3. Edit the line (e.g., change `"default"` → `"senna"`):

```bash
sed -i '' 's/useState("default")/useState("senna")/' extracted/out/renderer/assets/index-*.js
```

4. Repack the asar:

```bash
npx @electron/asar pack ./extracted ./patched.asar
```

5. Replace the original (backup first):

```bash
cp "/Applications/Hermes Agent.app/Contents/Resources/app.asar" \
   "/Applications/Hermes Agent.app/Contents/Resources/app.asar.backup"
cp ./patched.asar "/Applications/Hermes Agent.app/Contents/Resources/app.asar"
```

6. Clean up:

```bash
rm -rf /tmp/hermes-patch
```

7. Quit and relaunch Hermes Desktop. The footer/badge should show your profile name immediately.

### Pitfalls

- **Auto-update overwrites the patch.** If Hermes Desktop auto-updates (`electron-updater`), `app.asar` gets replaced and the patch is lost. Reapply after each update.
- **Version-dependent bundle hash.** The `index-*.js` filename changes per build. Always search for the pattern rather than hardcoding the filename.
- **Multiple `useState("default")` matches.** The search should find only one in an unmodified bundle. If there are multiple (unlikely in a clean build), verify the right one by checking for `activeProfile` on the same line.

---

## Approach B: Wire IPC for dynamic initialization (proper fix)

Add a `get-active-profile` IPC channel so the renderer reads the server-side active profile on mount. More work but survives updates.

### What needs changing

| File | Change |
|------|--------|
| `src/main/index.ts` | Add `ipcMain.handle("get-active-profile", () => getActiveProfileName())` |
| `src/preload/index.ts` | Add `getActiveProfile: () => ipcRenderer.invoke("get-active-profile")` to the `hermesAPI` object |
| `src/renderer/src/screens/Layout/Layout.tsx` | Replace `useState("default")` with a lazy initializer that calls `window.hermesAPI.getActiveProfile()` |

Source for reference (Hermes Desktop repo):
- `src/main/profiles.ts` — `getActiveProfileName()` reads `$HERMES_HOME/active_profile`
- `src/main/index.ts` — existing IPC handlers (around line 500+)
- `src/preload/index.ts` — existing hermesAPI bridge
- `src/renderer/src/screens/Layout/Layout.tsx` — Layout component, activeProfile state (line ~20)
