# Discord Bot Fleet Config Reference (as of June 12, 2026)

## Active Bots (8 — 17-profile redesign)

| Profile | Discord Bot Name | Free Response Channel | Channel Name | Category | auto_thread |
|---|---|---|---|---|---|
| senna | Senna | <id> | #your-orchestrator-channel | (uncategorized) | true |
| code | Hermes Coder | <id> | #engineering | CODE | true |
| creative | Hermes Graphics | <id> | #design-studio | (uncategorized) | false |
| research | Hermes Researcher | <id> | #research-lab | RESEARCH | true |
| finance | Hermes Oracle | <id> | #market-intel | FINANCE | true |
| security | Hermes Architect | <id> | #security-ops | SECURITY | true |
| knowledge | Hermes Secretary | <id> | #writing-desk | KNOWLEDGE | true |
| infra | Hermes Foreman | <id> | #operations | INFRA | true |

**Token source mapping** (new profile ← old profile):
code←coder, creative←designer, research←researcher, finance←oracle, knowledge←secretary, infra←foreman, security←architect

**Creative is the exception**: `auto_thread: false` — replies directly in-channel for quick visual iteration. All other bots use `auto_thread: true`.

## Senna-Subordinated Profiles (no own Discord bot — 13 profiles)

These profiles report through Senna to #your-orchestrator-channel. No bot token, no dedicated channel.

| Profile | Domain |
|---|---|
| cyber-red | Offensive security (pen testing, red team, malware) |
| cyber-blue | Defensive security coordinator |
| cyber-blue-cloud | Cloud security (~86 skills) |
| cyber-blue-forensics | Forensics + threat intel (~117 skills) |
| cyber-blue-compliance | Compliance + IAM (~99 skills) |
| cyber-blue-soc | SOC + network + IR (~193 skills) |
| business | Strategy, marketing, product |
| mlops | ML training, inference, evaluation |
| homelab | Smart home, IoT |
| social | Social media, content |
| communication | Email, messaging |
| ue5 | Unreal Engine 5 (Windows PC) |
| media | *arr stack, music, gaming |

## Standard Discord Config (all bots except creative)

```yaml
discord:
  require_mention: true
  free_response_channels: '<channel-id>'  # one per bot (senna has two)
  allowed_channels: ''
  auto_thread: true
  thread_require_mention: true
  history_backfill: true
  history_backfill_limit: 50
  reactions: true
  channel_prompts: {}
  dm_role_auth_guild: ''
  server_actions: 'list_guilds,server_info,list_channels,channel_info,list_roles,member_info,search_members,fetch_messages,list_pins,pin_message,unpin_message,delete_message,create_thread,list_threads,list_archived_threads,delete_channel,add_role,remove_role'
  allow_any_attachment: false
  max_attachment_bytes: 33554432
```

## Creative Config Exception (auto_thread: false)

```yaml
discord:
  require_mention: true
  free_response_channels: '<id>'
  allowed_channels: ''
  auto_thread: false
  thread_require_mention: false
  history_backfill: true
  history_backfill_limit: 50
  reactions: true
  channel_prompts: {}
  dm_role_auth_guild: ''
  server_actions: 'list_guilds,server_info,list_channels,channel_info,list_roles,member_info,search_members,fetch_messages,list_pins,pin_message,unpin_message,delete_message,create_thread,list_threads,list_archived_threads,delete_channel,add_role,remove_role'
  allow_any_attachment: false
  max_attachment_bytes: 33554432
```

## Config Drift Log

**May 27, 2026 (early)**: Found and fixed:
- Coder: `auto_thread: false` (was never threading), `thread_require_mention: true` → fixed to `auto_thread: true`
- Foreman: missing `thread_require_mention` entirely → added `thread_require_mention: true`
- Senna, Architect, Oracle, Researcher, Secretary: `thread_require_mention: false` → fixed to `true`
- Root cause of threading bug: patched wrong adapter file (`plugins/` instead of `gateway/platforms/`).

**May 27, 2026 (later)**: Discord tools activation:
- All 7 profiles: `server_actions: ''` → set to full 15-action whitelist
- All 7 bots re-invited with MANAGE_CHANNELS + MANAGE_MESSAGES + MANAGE_THREADS permissions

**May 27, 2026 (designer onboarding)**:
- Created Discord bot "Hermes Graphics" (app ID: <id>)
- Created #design-studio channel (ID: <channel-id>)
- Set `auto_thread: false` — designer replies directly in-channel for visual iteration

**June 12, 2026 (17-profile redesign)**:
- Discord restructuring: renamed 6 categories (RESEARCHER→RESEARCH, CODER→CODE, ARCHITECT→CREATIVE, SECRETARY→KNOWLEDGE, FOREMAN→INFRA, ORACLE→FINANCE)
- Created SECURITY category + #security-ops channel
- Archived #architecture (merged into #design-studio)
- Updated all 9 channel topics
- Copied bot tokens from old profiles to new ones (new profiles had truncated 13-char placeholder tokens)
- security←architect bot token reuse
- ⚠️ PATCH endpoint gotcha: used `/guilds/{guild}/channels/{id}` (404) instead of `/channels/{id}` — already documented in SKILL.md §1

## Guild Info

- Guild ID: <id>
- Channel map: see SKILL.md §6
