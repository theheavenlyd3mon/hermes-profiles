# Hermes Atlas — Structured Data Source

**URL**: https://hermesatlas.com/
**Maintainer**: ksimback (https://github.com/ksimback/hermes-ecosystem)
**Data**: ~110 repos across 12 categories, curated weekly, with live GitHub metadata.

## Available API Endpoints

All return JSON. No auth required. Rate-limit friendly (static generated files).

| Endpoint | Content | Use Case |
|----------|---------|----------|
| `/data/repos.json` | All repos with `owner`, `repo`, `description`, `stars`, `url`, `official`, `category` | Bulk catalog — 37KB, all 110 entries. Good for filtering/sorting by category or stars. |
| `/data/summaries.json` | Same repos with longer AI-generated summaries | Full-text analysis — 125KB. Good when you need richer descriptions. |
| `/data/list-summaries.json` | Curated list descriptions | For the 6 curated lists (lists not yet exposed in layout). |

## Data Structure (repos.json)

```json
{
  "owner": "outsourc-e",
  "repo": "hermes-workspace",
  "name": "hermes-workspace",
  "description": "Native web workspace — chat, terminal, ...",
  "stars": 830,
  "url": "https://github.com/outsourc-e/hermes-workspace",
  "official": false,
  "category": "Workspaces & GUIs"
}
```

## Known Categories (as of May 2026)

Core & Official, Skills & Skill Registries, Memory & Context, Workspaces & GUIs,
Plugins & Extensions, Guides & Docs, Deployment & Infra, Integrations & Bridges,
Developer Tools, Domain Applications, Multi-Agent & Orchestration, Forks & Derivatives

## Fetch Pattern (terminal + curl, no web tools)

```bash
# Full catalog
curl -sL "https://hermesatlas.com/data/repos.json" > /tmp/atlas_repos.json

# With summaries
curl -sL "https://hermesatlas.com/data/summaries.json" > /tmp/atlas_summaries.json

# Analysis: write a .py script, don't pipe to -c (timeout risk)
cat > /tmp/analyze.py << 'PYEOF'
import json
with open('/tmp/atlas_repos.json') as f:
    repos = json.load(f)
for r in sorted(repos, key=lambda x: -x["stars"]):
    print(f"★{r['stars']:>6d}  {r['owner']:25s}/{r['repo']:45s}  [{r['category']}]")
PYEOF
python3 /tmp/analyze.py
```

## Curation Notes

- ksimback runs weekly curation — repos get added/dropped based on quality and security review.
- The site also has a `/guide/` (Hermes Handbook) and `/reports/` section.
- RSS feed at `/rss.xml` for new project announcements.
