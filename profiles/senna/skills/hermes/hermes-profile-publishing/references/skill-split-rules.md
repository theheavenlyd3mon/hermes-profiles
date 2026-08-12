# Skill Split Rules for Security Profiles

These rules supersede the older “strip everything but domain skills” heuristic for `cyber-*` profiles.


## Goal

Keep the repo small without destroying what makes each profile distinctive.


## Default behavior

- In mirror/publish passes, remove generic default skills from every profile.
  Examples to strip: `apple/*`, `autonomous-ai-agents/*`, `github/*`, `mlops/*`,
  `social-media/*`, `software-development/*`, etc., EXCEPT where noted below.
- Keep only profile-specific skills plus README/SOUL/runtime essentials.


## Exception: bundled cybersecurity skill collections

- `profiles/cyber-red/skills/Anthropic-Cybersecurity-Skills/` is a core
  capability, not bloat. Restore it if removed by bulk cleanup.
- `profiles/cyber-blue-{cloud,compliance,forensics,soc}/skills/` each need
  their own `Anthropic-Cybersecurity-Skills/` revision if the live profile
  has it. Restore from `~/.hermes/profiles/<profile>/skills/...`.
- `profiles/cyber-blue/` without a specialization suffix stays minimal: keep
  `hermes/hermes-security-audit` plus `security/supply-chain-hardening` only.


## Verification checklist

1. `ls profiles/cyber-red/skills` must include `Anthropic-Cybersecurity-Skills`.
2. Each `cyber-blue-*` specialization must include its own
   `Anthropic-Cybersecurity-Skills` if that path exists in the live profile.
3. Each `cyber-blue-*` specialization must NOT contain generic default skill
   categories like `apple`, `github`, `mlops`, `productivity`, `social-media`,
   `software-development`, `yuanbao`, etc., unless they are the only
   specialized skill bundle available for that profile.


## Mirror command pattern

Use a whitelist/split pass, not a blanket delete-all-non-defensive pass:

- define `keep = {'Anthropic-Cybersecurity-Skills', 'dogfood'}`
- delete everything else under `skills/` except `SOUL.md`/`README.md`.
- for `cyber-blue`, keep `{'security', 'hermes'}`; do NOT add the generic
  categories back.
