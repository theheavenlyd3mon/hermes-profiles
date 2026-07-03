# GitHub Release Asset Discovery & macOS Install

## Why This Exists

GitHub release pages sometimes fail to render the assets list (partial DOM errors, rate-limiting, or the page being too large). The GitHub Releases API is a reliable fallback that also returns structured metadata (file sizes, content types, exact timestamps) that the web page doesn't show.

## API Endpoint

```
GET https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}
GET https://api.github.com/repos/{owner}/{repo}/releases/latest
GET https://api.github.com/repos/{owner}/{repo}/releases        # paginated list
```

No authentication needed for public repos. Returns the full release object with an `assets` array.

## Structured Asset Listing (Python)

```bash
curl -s "https://api.github.com/repos/fathah/hermes-desktop/releases/tags/v0.3.6" \
  | python3 -c "
import json,sys
data = json.load(sys.stdin)
for a in data.get('assets', []):
    mb = a['size'] / 1024 / 1024
    print(f\"{a['name']:50s} {mb:5.1f}MB  {a['browser_download_url']}\")
"
```

Example output:
```
hermes-desktop-0.3.6.dmg                           127.4MB  https://github.com/...
Hermes.Agent-0.3.6-arm64-mac.zip                   117.4MB  https://github.com/...
Hermes.Agent-0.3.6-mac.zip                         122.6MB  https://github.com/...
hermes-desktop-0.3.6.AppImage                      127.5MB  https://github.com/...
hermes-desktop-0.3.6-setup.exe                     104.0MB  https://github.com/...
hermes-desktop_0.3.6_amd64.deb                      99.4MB  https://github.com/...
hermes-desktop-0.3.6.rpm                            86.7MB  https://github.com/...
latest-mac.yml                                       0.0MB  https://github.com/...
```

## Key Fields Per Asset

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Filename (e.g. `app-1.0.0.dmg`) |
| `size` | int | Size in bytes |
| `browser_download_url` | string | Direct download URL |
| `content_type` | string | MIME type |
| `updated_at` | ISO 8601 | Last modified timestamp |

## macOS Install Patterns

### DMG (standard)

```bash
curl -L -o /tmp/app.dmg "https://github.com/.../App.dmg"
hdiutil attach /tmp/app.dmg               # mount
cp -R "/Volumes/App/App.app" /Applications/
xattr -cr "/Applications/App.app"          # clear quarantine
hdiutil detach "/Volumes/App"
```

### DMG corruption (electron-builder)

**Symptom:** `hdiutil attach` fails with "image data corrupted" and a CRC32 checksum mismatch. This is a known electron-builder upload artifact — the DMG bytes were corrupted in transit or during CI upload.

**Fix:** Look for an alternate archive format in the same release. Electron-builder often produces both:
- `App-version.dmg` (127 MB) — the standard DMG
- `App-version-arm64-mac.zip` (117 MB) — zip containing the .app directly
- `App-version-mac.zip` (122 MB) — Intel variant

The zip is a valid archive that extracts the `.app` bundle directly:

```bash
unzip -q App-version-arm64-mac.zip -d /tmp/extracted
cp -R "/tmp/extracted/App.app" /Applications/
xattr -cr "/Applications/App.app"
```

### Verification

```bash
# Confirm architecture
file "/Applications/App.app/Contents/MacOS/App"
# → "Mach-O 64-bit executable arm64" (Apple Silicon)
# → "Mach-O 64-bit executable x86_64" (Intel)

# Check quarantine attributes
xattr "/Applications/App.app"
# Should NOT show com.apple.quarantine after xattr -cr

# Launch from CLI to see logs
open "/Applications/App.app"
```

## When to Use This Pattern

- GitHub release page fails to render assets (partial load, blank assets section)
- You need to know file sizes before downloading (large downloads on metered connections)
- You need to find a specific platform variant that isn't prominent on the web page
- The primary download (DMG) fails and you need alternatives
- You want to script asset discovery (the API output is machine-readable JSON)

## Pitfalls

- **DMG corruption is release-specific, not project-wide.** The next version may have a clean DMG. Always try the API first to see all available formats; don't assume the DMG is always broken.
- **electron-builder blockmap files** (`.dmg.blockmap`, `.zip.blockmap`) are for delta updates, not direct install. Ignore them.
- **`latest-mac.yml`** is metadata for the auto-updater (Sparkle/electron-updater), not an installable artifact.
- **The arm64 vs x64 distinction matters on macOS.** Apple Silicon (M1/M2/M3/M4) can run x64 via Rosetta 2, but arm64 native is preferred. The API output makes this easy to verify by checking the filename for `arm64` or `x64`.
- **Unsigned macOS apps** from GitHub releases will show Gatekeeper warnings. `xattr -cr` clears the quarantine flag without needing to right-click → Open.
