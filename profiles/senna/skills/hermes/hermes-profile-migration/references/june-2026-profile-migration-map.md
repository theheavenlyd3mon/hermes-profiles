# June 2026 Profile Migration Map

**Date:** 2026-06-12 to 2026-06-16  
**Type:** 17-profile domain-based redesign  
**Old structure:** Role-based (architect, coder, debugger, reviewer, data-analyst, researcher, secretary, designer, devops, security, oracle, foreman, senna)  
**New structure:** Domain-based (21 profiles)

## Old → New Mapping

| Old Profile | New Profile(s) | Merge Type | Notes |
|-------------|---------------|------------|-------|
| architect | security | Rename + role change | Bot token reused. Original SOUL.md was systems architecture; new SOUL.md is cybersecurity |
| coder | code | Rename | Merged coder + debugger + reviewer functionality |
| debugger | code | Absorbed | Into domain orchestrator |
| reviewer | code | Absorbed | Into domain orchestrator |
| data-analyst | research | Rename + expansion | Merged with researcher |
| researcher | research | Absorbed | Into domain orchestrator |
| designer | creative | Rename + expansion | Merged with architect's design side |
| secretary | knowledge | Rename | Knowledge/docs/wiki focus |
| oracle | finance | Rename | Trading/market analysis focus |
| foreman | infra | Rename | DevOps/deployment focus |
| devops | infra | Absorbed | Into domain orchestrator |
| senna | senna | Unchanged | Top orchestrator |

## Profiles Added (no old counterpart)

- `communication` (email/messaging)
- `business` (strategy/marketing)
- `homelab` (smart home/IoT)
- `social` (social media/content)
- `media` (arr stack/music/gaming)
- `ue5` (Unreal Engine specialist)
- `mlops` (ML training/inference)
- `cyber-red` (offensive security)
- `cyber-blue` (defensive security) + sub-profiles (cloud, compliance, forensics, soc)
- `educate` (tutoring/pedagogy)

## Bot Token Reuse

| Old Bot | New Bot | Channel Impact |
|---------|---------|----------------|
| Hermes Architect | Security | Still had access to #architecture until manually removed |
| Hermes Coder | Code | Clean transition |
| Hermes Oracle | Finance | Clean transition |

## SOUL.md Status

| Old Profile | SOUL.md Archived? | Status |
|-------------|-------------------|--------|
| architect | ❌ No | **LOST** — directory deleted before archival |
| coder | ❌ No | **LOST** — absorbed into code |
| debugger | ❌ No | **LOST** — absorbed into code |
| reviewer | ❌ No | **LOST** — absorbed into code |
| data-analyst | ❌ No | **LOST** — absorbed into research |
| researcher | ❌ No | **LOST** — absorbed into research |
| designer | ❌ No | **LOST** — absorbed into creative |
| secretary | ❌ No | **LOST** — absorbed into knowledge |
| oracle | ❌ No | **LOST** — absorbed into finance |
| foreman | ❌ No | **LOST** — absorbed into infra |
| devops | ❌ No | **LOST** — absorbed into infra |

**Lesson:** None of the old SOUL.md files were archived. The soul-drafts directory (`~/Downloads/soul-drafts/`) only contains the NEW profile drafts (21 files from 2026-06-12). The old identities are permanently gone.

## Recovery Options (if old SOUL.md needed)

1. **Session transcripts** — `session_search` for the session where the SOUL.md was written. Content may be in an assistant message.
2. **LCM database** — `lcm_grep` for the profile name + "SOUL" across all sessions.
3. **Mnemosyne** — `mnemosyne_recall` for any saved memory about the profile's identity.
4. **Reconstruct from role** — if the old profile was well-understood, draft a new SOUL.md from the role description. The model fleet assignment (`Architect=deepseek-v3.2`) may hint at the intended personality.
