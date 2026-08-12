# Installing Skills from External Forgejo/Gitea Repos

**When to use:** User shares a Forgejo/Gitea repo URL containing skills to install.

## Forgejo API Pattern

### List all files in a skill directory

```bash
curl -s "https://<forgejo-host>/api/v1/repos/<owner>/<repo>/git/trees/main?recursive=true" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for entry in data.get('tree', []):
    if entry['path'].startswith('<skill-name>/'):
        print(entry['path'])
"
```

### Download raw file content

```
https://<forgejo-host>/<owner>/<repo>/raw/branch/main/<path>
```

### Install script pattern

```bash
REPO="https://git.example.com/owner/repo"
SKILL="skill-name"
TARGET="~/.hermes/profiles/<profile>/skills/<category>/$SKILL"

# 1. List files
FILES=$(curl -s "$REPO/api/v1/repos/owner/repo/git/trees/main?recursive=true" | \
  python3 -c "import json,sys; [print(e['path']) for e in json.load(sys.stdin).get('tree',[]) if e['path'].startswith('$SKILL/')]")

# 2. Download each file
for f in $FILES; do
  mkdir -p "$TARGET/$(dirname "$f")"
  curl -sL -o "$TARGET/$f" "$REPO/raw/branch/main/$f"
done

# 3. Make scripts executable
find "$TARGET/scripts/" -type f -exec chmod +x {} \; 2>/dev/null

# 4. Verify
find "$TARGET" -type f | wc -l
```

## GitHub API Pattern (for comparison)

```bash
# List files in a directory
curl -s "https://api.github.com/repos/<owner>/<repo>/contents/<path>" | \
  python3 -c "import json,sys; [print(f['name']) for f in json.load(sys.stdin)]"

# Download raw
curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>"
```

## Pitfalls

- **Forgejo API returns tree recursively** — filter by prefix, don't assume flat structure
- **Scripts need chmod +x** — Forgejo preserves executable bit in git but curl doesn't
- **Large repos** — use the tree API to list first, then download selectively. Don't clone the entire repo just for one skill.
- **SKILL.md validation** — always verify the first 5 lines contain valid YAML frontmatter after download
