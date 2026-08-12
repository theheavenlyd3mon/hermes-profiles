# Profile Splitting Strategy

> When a profile accumulates too many skills for a single context window, split by sub-domain into child profiles. Parent becomes a lightweight router.

## When to Split

| Signal | Threshold |
|--------|-----------|
| Skill count | >150 skills in one profile |
| Context pressure | Progressive disclosure Level 0 listing >10K tokens |
| Domain breadth | Profile covers 3+ distinct sub-domains |

## Pattern: Parent Router + Child Workers

```
security (coordinator, ~7 skills)
├── cyber-red (offensive, ~230 skills)
├── cyber-blue-cloud (cloud sec, ~86 skills)
├── cyber-blue-forensics (forensics + threat intel, ~117 skills)
├── cyber-blue-compliance (compliance + IAM, ~99 skills)
└── cyber-blue-soc (SOC + network + IR, ~193 skills)
```

**Parent SOUL.md** gets:
- `## Sub-Profile Routing` section mapping domain → child
- Lightweight skills only (coordination, not domain expertise)
- ROUTE entries pointing to children by domain keyword

**Child SOUL.md** files get:
- `Reports→ParentName→User` in DECISIONS
- Parent's tag in KANBAN (e.g., `Tags=security,cloud`)
- Full domain skills

## Naming Convention

`{parent}-{subdomain}` — e.g., `cyber-blue-cloud`, `cyber-blue-forensics`

Keeps alphabetical grouping in profile listings. Parent name prefix signals lineage.

## Real Example: cyber-blue (2026-06-12)

530 Anthropic cybersecurity skills split into 4 child profiles:
- cyber-blue-cloud: 86 skills (Cloud Security)
- cyber-blue-forensics: 117 skills (Forensics 52 + Threat Intel 65)
- cyber-blue-compliance: 99 skills (Compliance 42 + IAM 57)
- cyber-blue-soc: 193 skills (SOC 31 + Network 48 + IR 17 + Vuln 25 + Mobile 7 + Supply Chain 5 + Other 62)

Each child stays under 200 skills. Parent retains 7 coordination skills.
