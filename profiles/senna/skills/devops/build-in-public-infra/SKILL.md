---
name: build-in-public-infra
description: Build-in-public infrastructure plan — VPS setup, security hardening, social media manager profile, GitHub integration, content strategy. Use when setting up, expanding, or troubleshooting the build-in-public pipeline.
version: 1.0.0
author: senna
metadata:
  hermes:
    tags: [build-in-public, vps, security, social-media, github, x-twitter, infrastructure]
    related_skills: [xurl, hermes-security-hardening, supply-chain-hardening, github-pr-workflow, foreman-orchestration]
---

# Build-in-Public Infrastructure

Full plan at: `~/.hermes/profiles/senna/plans/2026-05-24-build-in-public-infra.md`

## Quick Reference

### 6 Phases
1. **Phase 0** — Prep: xurl auth + X Premium ($8/mo)
2. **Phase 1** — VPS + Security Hardening (day 1, before anything else)
3. **Phase 2** — GitHub Security for public repos
4. **Phase 3** — Social Media Manager Profile
5. **Phase 4** — GitHub Integration (changelog detector, gh CLI)
6. **Phase 5** — Bigger Projects (scaling compute/storage)
7. **Phase 6** — Content Strategy (@levelsio playbook)

### VPS Recommendation
- **Start:** Oracle Cloud Always Free ($0/mo, 4 ARM, 24GB RAM, 200GB)
- **Scale:** Hetzner CX32 ($8/mo, 4 vCPU, 8GB RAM, 80GB NVMe)
- **Never:** Expose VPS IP in public posts

### Security Checklist
**VPS:** SSH key-only, root disabled, UFW (SSH only), Fail2Ban, unattended-upgrades, auditd, non-root user for Hermes
**GitHub:** gitleaks pre-commit, .gitignore for secrets, secret scanning + Dependabot, minimal PAT scopes, branch protection
**Secrets:** Never in .env committed to git, use Keychain/secrets manager, separate keys for dev vs prod

### Cost
- Starting: ~$10-13/mo (X Premium + Oracle free + API)
- Growing: ~$21-26/mo (+ Hetzner CX32)
- Scaling: ~$32-49/mo (+ storage + domain)

### Content Strategy
- 3x/day posts at peak times (9 AM, 12 PM, 5 PM ET)
- Weekly Friday thread
- 15-30 min daily engagement (reply to builders)
- Hermes drafts, you approve — never auto-post without review

## Pitfalls
- Don't post VPS IP address publicly
- Don't use same API key for dev and production
- Don't commit .env files "just this once"
- Don't skip security hardening to save time
- Don't auto-post without human review (AI slop detection is real)
- Don't neglect engagement (replying grows followers, not posting)
