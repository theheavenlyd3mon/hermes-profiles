# Magnus Skills for Windows Team

Which Magnus Agent-Skills (git.brandyapple.com/magnus/agent-skills) are useful for Windows game dev profiles.

## Windows Profiles

| Profile | Domain | Local Model |
|---------|--------|-------------|
| ue5-coder | Unreal Engine 5 C++ | local-36B-Opus APEX I-Mini |
| blender-coder | Blender Python/MCP | local-36B-Opus APEX I-Mini |
| threejs-coder | Three.js web 3D | local-36B-Opus APEX I-Mini |
| designer | Visual design/UI | local-36B-Opus APEX I-Mini |

## Recommended Magnus Skills

| Skill | Priority | Install To | Why |
|---|---|---|---|
| **systematic-debugging** | ✅ High | All 4 profiles | 4-phase root cause debugging. "Rule of Three" (3+ failed fixes → question architecture). Already proven across 11 Mac profiles. Essential for UE5 debugging loops. |
| **software-architecture-analysis** | ✅ High | ue5-coder, threejs-coder | Reverse-engineer codebases, produce design docs, Mermaid diagrams. Useful for UE5 plugin/module analysis and understanding reference implementations. |
| **cli-builder** | ✅ Medium | ue5-coder | Design patterns for agent-built CLI tools. Useful if building scripts/tools on Windows side. |
| **agent-skills** | ✅ Medium | All 4 profiles | Foundation standard reference. Needed if creating new skills on Windows. |
| **opensource-contributions** | ⚠️ Low | Optional | Agent transparency rule matters if contributing to UE5/Blender/Three.js open source. |

## Not Recommended for Windows

| Skill | Why Skip |
|---|---|
| data-scientist | Trading/statistics focused, not game dev |
| epub | Obsidian pipeline, Windows team doesn't maintain vault |
| forgejo-cli | Only if using Forgejo; skip if GitHub-only |
| nous-branding | Nous Research specific, not game dev |
| All media pipeline skills | Windows team doesn't run *arr stack |
| confluence-cli, jira-cli, jira-jql | Enterprise tools not in stack |

## Tailscale Bundle (Infrastructure)

The 7-skill Tailscale/Headscale bundle is valuable if remote access to the Windows PC is needed:
- tailscale-client, headscale-deploy, headscale-node-lifecycle
- tailnet-policy, headscale-routing, headscale-derp, headscale-backup

Install when setting up mesh VPN connectivity between Mac fleet and Windows PC.

## Installation Notes

- Magnus skills are on Forgejo (git.brandyapple.com), not GitHub
- Raw URL pattern: `https://git.brandyapple.com/magnus/agent-skills/raw/branch/main/{skill-name}/SKILL.md`
- Use `curl` to download, extract SKILL.md + scripts/ + references/ to profile's skills directory
- Pin installed skills: `hermes --profile <name> curator pin <skill-name>`
- Local models (local-36B) have smaller context windows — keep SOUL.md compressed, pin only essential skills
