# Platform Mapping

## The problem

`sys.platform` on macOS returns `"darwin"`, not `"macos"`. Skill frontmatter uses `"macos"` (the Hermes convention). Without mapping, macOS skills with `platforms: [macos]` are silently filtered out.

## The fix

```python
import sys
plat = sys.platform
if plat == "darwin":
    plat = "macos"
if plat not in platforms:
    continue
```

## Platform values

| sys.platform | frontmatter value |
|---|---|
| `darwin` | `macos` |
| `linux` | `linux` |
| `win32` | `windows`