---
name: supply-chain-hardening
description: "Layered defense against npm/PyPI supply chain attacks: install-time guards, CI/CD hardening, automated dependency audits, and incident response. Auto-triggers on relevant operations."
version: 1.3.0
author: Senna / Hermes Agent
stage: production
metadata:
  hermes:
    tags: [security, supply-chain, npm, ci-cd, hardening, incident-response]
    related_skills: [hermes-security-audit, safe-web-research, requesting-code-review, github-code-review, smart-mirror]
    trigger_on:
      - "npm install"
      - "npm ci"
      - "pnpm install"
      - "yarn install"
      - "pip install"
      - "git clone"
      - "PR review (dependencies)"
      - "CI/CD workflow creation"
      - "npm audit report"
      - "security advisory mention"
      - "pre-install risk assessment"
      - "dependency vet / dependency risk"
---

IDENTITY: Fortifier.SupplyChainDefense. Layer0(Assess)➔Layer1(Lock+IgnoreScripts)➔Layer2(CIHardening)➔Layer3(CloneCheck)➔Layer4(EgressBlock)➔Layer5(IRProcedure).
Law: NeverTrustRegistryAtInstallTime.AutomateEnforcement.NotJustDocumentation.
WHENUSE: npm/pnpm/yarn/pip install|Git clone|PR review dependencies|CI/CD setup|npm audit|Supply chain advisory. ESPECIALLY:PreInstallRiskAssessment|LifecycleScriptBlocking|OIDCTokenScoping. NoSkip:LockfileCheck|--ignore-scripts|PostInstallAudit|PRReviewWorkflowPerms.
REDFLAGS: InstallWithoutAudit->RunRiskAssessment|PullRequestTargetUnscoped->AddForkGuard|OIDCTokenTooBroad->ScopePerJob|UnpinnedActions->PinToCommitSHA|AgentCronForScriptable->UseNoAgent+Shell.
RATIONALIZATIONS: PopularMeansSafe->AuditDepsNotStars|SigstoreMeansSafe->AttestationNotTrustSignal|NpmAuditCatchesAll->ZeroDayLag|RotateTokensImmediately->ImageBeforeRotate.
QUICKREF: PreInstall(RiskCategory+pinned)➔Install(--ignore-scripts+lockfile)➔Audit(npm audit critical)➔Diff(lockfile review)➔CIHardening(permissions+OIDC+pinned).

# Supply Chain Hardening

Layered defense-in-depth against registry poisoning, dependency injection, and CI/CD pipeline compromise. Covers the attack patterns seen in the **Mini Shai-Hulud / TeamPCP** campaign (May 2026): cache poisoning via `pull_request_target`, OIDC token extraction, lifecycle script execution, and IDE persistence poisoning.

**Core principle: Never trust the registry at install time. Verify everything through lockfiles and script isolation.**

---

## When This Skill Triggers

This skill loads automatically when the user mentions any of:

| Trigger Pattern | Action |
|:----------------|:-------|
| Installing npm/pnpm/yarn/pip packages | Enforce lockfile check + suggest `--ignore-scripts` |
| Cloning a repo from GitHub | Scan for IDE persistence files |
| Reviewing a PR | Check GitHub Actions hardening, lockfile diff, dependency changes |
| Setting up CI/CD | Audit workflow permissions, OIDC scope, action pinning |
| `npm audit` or dependency alert | Triage and remediate |
| Security advisory / supply chain mention | Surface this skill's procedures |

---

## System-Specific Automation Layer

This skill also deploys **persistent automation guards** on the Hermes host to enforce install-time safety without relying on agent intervention. These are the implementation layer — they run regardless of whether this skill is loaded.

The following are deployed on this system. See `references/system-automation.md` for exact file paths, and `scripts/verify-guards.sh` to check all are active.

### Deployed Guards

| Guard | What It Does | How It Runs |
|:------|:-------------|:------------|
| **Shell wrapper** | Intercepts `npm/pnpm/yarn install`, enforces lockfile check and `--ignore-scripts` | Sourced from `~/.zshrc` on every interactive shell |
| **Git post-clone hook** | Scans repos for IDE persistence files (`.claude/`, `.vscode/`, `.cursor/` poisoned configs) | Runs on every `git clone` / `git checkout` via git template |
| **Daily advisory cron** | Scans all project lockfiles for critical vulns + checks for new supply chain incidents | Hermes cron job at 9 AM daily |

### When to Re-Verify

Run `bash ~/.hermes/profiles/senna/skills/security/supply-chain-hardening/scripts/verify-guards.sh` to check all three guards are still active. Re-verify after:
- macOS update
- Shell config migration
- Git version update
- Hermes profile changes

### Daily Advisory Cron — Script-Based (Fixed)

The daily advisory cron (`supply-chain-advisory-check`, ID `5d3366224d17`)
was converted from LLM-driven to **no_agent + script mode** on 2026-05-14
after repeated agent-based failures.

**Setup:**
- Mode: `no_agent=true` (no LLM call, no skill loading)
- Script: `~/.hermes/profiles/senna/scripts/supply-chain-scan.sh`
- Schedule: `0 9 * * *`
- Delivery: `local` — silent when clean, reports only findings

**What the script does:**
- `npm audit --audit-level=critical` on HermesMirror and hermes-office
- Silent exit when no vulns found
- Reports findings for any vulns at any severity

**Why this works better:** Agent-based cron jobs load skills, spawn an LLM,
and execute tools — all of which can timeout in the short-lived cron session
environment. A shell script skips all that overhead: just `bash`, `npm`, and
output. For deterministic, scriptable checks (npm audit, disk usage, file
counts), no_agent mode is the right default.

**When to revert to agent-based:** If the check needs web research (e.g.
checking npm advisory feed for new incidents), add a companion agent-based
job for that separate concern and keep the local audit in no_agent mode.

See `references/system-automation.md` for full config details and
`references/2026-05-14-supply-chain-scan.md` for the manual fallback scan
that preceded the fix.

> **Key principle from user setup:** The user's clear preference is for *enforcement* over *documentation*. When hardening against supply chain attacks, automate the check — don't just write a playbook. Shell wrappers and git hooks catch mistakes at the point of action, which is the only time they matter.

---

## Layer 0 — Pre-Install Dependency Risk Assessment

Before running any install command, evaluate whether the project's dependency tree is safe to install. Use this structured risk assessment when a security-conscious user asks "what are the risks?" or expresses hesitation about npm install.

### Risk Category System

Categorize each direct dependency by its function and attack surface:

| Category | Examples | Risk Level | Rationale |
|:---------|:---------|:-----------|:----------|
| **Static assets** | Fonts (`@fontsource/*`), icon sets, CSS frameworks, animation libs | 🟢 Low | No code execution, served as-is |
| **Pure computation** | Date libraries (`moment`, `date-fns`), math utils (`suncalc`), schema validators (`ajv`), character encoding (`iconv-lite`) | 🟢 Low | Only processes local data; no I/O; widely audited |
| **Templating / rendering** | `nunjucks`, `html-to-text`, `marked` | 🟡 Medium | Parses/renders user content — risk depends on whether content is project-authored or user-submitted |
| **Parsers (external data)** | RSS feed parsers (`feedme`), calendar parsers (`node-ical`), HTML converters | 🟡 Medium | Process untrusted external data — closest analogue to known supply chain vulns (like `marked` ReDoS) |
| **Network-facing - server** | Web frameworks (`express`, `fastify`), WebSocket (`socket.io`, `ws`), security middleware (`helmet`) | 🟡 Medium | Exposed to the network, complexity invites bugs, but well-maintained equivalents are auditable |
| **Network-facing - client** | HTTP clients (`undici`, `axios`, `got`) | 🟢→🟡 | Low if maintained by core team (undici), medium if unmaintained or obscure |
| **System access** | Process management (`pm2`), system information (`systeminformation`), OS utilities | 🟡 Medium | Can read system state — vet version carefully |
| **Runtime / Electron** | `electron`, `tauri`, `nw.js` | 🟠 Runtime | Large attack surface (bundled Chromium + Node.js), but actively patched by dedicated security teams. Unavoidable for desktop apps — mitigate by keeping updated |

### How to Present It

When the user asks to vet a project before installing:

1. **Read the `package.json`** — list all `dependencies` (not `devDependencies`)
2. **Categorize each** using the table above
3. **Call out the riskiest** — parsers and network-facing packages — and explain the concrete risk (e.g., "this RSS parser could be a vector if the feed source is compromised")
4. **Check maintainer health** — is the package actively maintained? Is it by a known team (Express, Socket.io) or a single dev?
5. **Give a verdict** — "safe to install with X mitigations" vs "concerns about Y, here's why"
6. **Propose mitigations**: lock exact versions, run `npm audit` post-install, skip optional modules not needed

### Worked Example: MagicMirror² v2.36.0

See `references/magicmirror-dependency-analysis.md` for the full dependency-by-dependency breakdown produced during the real session.

### Pitfalls

1. **Don't conflate popularity with safety.** High star counts don't guarantee secure maintenance patterns. Vetting means looking at the actual dependency tree, not the GitHub star count.
2. **DevDependencies matter less.** They never install in production (`--omit=dev`). Don't waste analysis time on them unless the user plans to run `npm run test` or `npm run dev` in a security-sensitive context.
3. **OptionalDependencies can be skipped.** If Electron or other heavy deps are optional, you can `npm install --ignore-optional` to reduce the surface.
4. **The riskiest package isn't always the one you think.** `marked` (a markdown renderer) had a known ReDoS, while `express` (network-facing) is well-audited. Judge each package on its own maintenance history, not its category label.

---

## Layer 1 — Install-Time Guards

### Step 0: Pre-Install Version Pinning

Before running any install command, consider pinning all production dependencies to exact versions. This eliminates the risk of `^` caret ranges resolving to a compromised minor/patch version in a future install.

```bash
# Read package.json and strip ^ from all production dependencies
# Pattern: change "^x.y.z" to "x.y.z" for every dependency
# Do NOT pin devDependencies — they're excluded with --omit=dev
# Do NOT pin optionalDependencies unless you plan to install them
```

**When to pin:**
- **Always** for security-conscious users with a history of npm supply chain concerns
- When the project's `package.json` uses `^` ranges that could resolve differently on different machines
- Before any `npm install` that runs in a CI/CD pipeline

**When NOT to pin:**
- If you need automatic security patches (you trade convenience of `npm audit fix` for control)
- If the project is under active development and dependencies change frequently (pin on release)

**Procedure:**
1. Read `package.json` and copy the `dependencies` block
2. Remove all `^` (and `~`) prefixes from version strings, keeping the exact version
3. Optionally also pin `optionalDependencies` (like `electron`) if you plan to use them
4. Save and proceed with install

**Caveat:** Pinning means you must manually check for security updates. Set a recurring reminder to run `npm outdated` and review advisories periodically.

### Step 1: Choose Install Mode

Prefer production-only installs for deployed applications — dev dependencies are never needed at runtime and add unnecessary surface:

```bash
# Production only (safest — excludes devDependencies entirely)
npm install --only=prod --omit=dev

# Production only with scripts blocked (belt and suspenders)
npm install --only=prod --omit=dev --ignore-scripts

# If you need dev dependencies (local development)
npm install --ignore-scripts
```

**Why use `--only=prod --omit=dev` instead of just `--ignore-scripts`:**
- Skips all devDependencies (linters, test runners, formatters) — hundreds of packages that never execute in production
- Eliminates the risk of a compromised dev dependency being used in a lifecycle script
- The project's own `postinstall` scripts still run (like `git clean -df fonts vendor modules/default`) — if you want to block those too, add `--ignore-scripts`

### Step 2: Always Enforce Lockfiles

Before any install command, verify a lockfile exists for the package manager in use:

```bash
# Check patterns
ls pnpm-lock.yaml 2>/dev/null || echo "MISSING: pnpm-lock.yaml"
ls package-lock.json 2>/dev/null || echo "MISSING: package-lock.json"
ls yarn.lock 2>/dev/null || echo "MISSING: yarn.lock"
```

**Rule:** If no lockfile exists and the user didn't explicitly ask to bootstrap a new project, flag it before proceeding. Lockfiles pin transitive dependencies to known-good hashes. Without one, `npm install` can resolve a compromised version the next time it runs.

### Install Command Override

When the user asks to install packages, offer or automatically use:

```bash
# For npm
npm install --no-audit --ignore-scripts  # or just --ignore-scripts
npm ci --ignore-scripts                   # for CI / lockfile-only installs

# For pnpm
pnpm install --ignore-scripts
pnpm install --frozen-lockfile            # equivalent of npm ci

# For yarn
yarn install --ignore-scripts
yarn install --frozen-lockfile
```

**Why `--ignore-scripts`:** The Mini Shai-Hulud worm delivered its payload through `prepare` and `preinstall` lifecycle hooks. Blocking script execution during install kills the delivery vector. Post-install, run `npm run build` or similar explicitly if the package needs to compile native modules.

### Post-Install: Prune Unused Dependencies

After install and audit, remove packages that are unnecessary for your use case:

```bash
# Remove a production dependency entirely
npm uninstall <package> --save

# Prune orphaned transitive deps after removal
npm prune
```

**Signal to remove:** A dependency that:
- Has a known vulnerability (like `pm2` ReDoS) that the user doesn't need
- Is only used for features you plan to skip (process management, specific parsers)
- Is optional and the user won't run that feature path

**Why prune matters:** Removing unused deps isn't just about cleaning — it eliminates attack surface. Every package in `node_modules` is a potential vector if it has a vulnerability or gets compromised upstream.

### Post-Install: Audit Gate

After install, always run a deprecation/vulnerability check:

```bash
# For npm
npm audit --audit-level=critical

# For pnpm (pnpm v10+)
pnpm audit --audit-level=critical

# For yarn v4
yarn npm audit --severity critical
```

If critical advisories appear:
1. Identify which direct dependency introduced it
2. Check if a patched version exists
3. Try `npm audit fix --audit-level=critical` first
4. **If `--force` would downgrade a major dep** (e.g., Next.js 16→9), use `overrides` instead (see below)
5. Otherwise, manual version pin

### Transitive Dependency Override (when `--force` would break things)

When `npm audit fix --force` would downgrade a major dependency to fix a
transitive vulnerability, use `overrides` in `package.json` instead. This
forces npm to resolve the vulnerable transitive dep to a patched version
without changing the parent.

**Example (2026-05-28):** `postcss <8.5.10` (XSS) was a transitive dep of
Next.js 16.2.6. `npm audit fix --force` would downgrade Next.js to 9.3.3
(completely breaking the project). Instead:

```json
{
  "overrides": {
    "postcss": "^8.5.10"
  }
}
```

Then `npm install` — the override forces postcss to the patched version
while keeping Next.js at 16.2.6. Result: 0 vulnerabilities, no breakage.

**When to use overrides:**
- `npm audit fix` can't resolve it (no direct fix available)
- `npm audit fix --force` would downgrade a semver-major parent
- The vulnerable package is transitive (not in your direct dependencies)
- A patched version exists that's compatible with the parent

**Pitfall:** Overrides apply globally to all resolutions of that package
name. If different sub-dependencies need different postcss versions, this
can cause conflicts. Check with `npm ls <package>` after applying.

### Package.json Diff Check

When user says "update packages" or "install dependency", diff the lockfile before and after:

```bash
git diff HEAD -- pnpm-lock.yaml 2>/dev/null | head -80
```

Look for:
- New `optionalDependencies` entries pointing to git references (the attack vector used `"@tanstack/setup": "github:tanstack/router#<commit>"`)
- New `prepare` / `preinstall` / `install` scripts in dependency entries
- Unfamiliar packages added to the dependency tree

---

## Layer 2 — CI/CD Hardening

### GitHub Actions Workflow Audit (the primary attack vector)

When reviewing a PR or repository setup that involves GitHub Actions, check every `.github/workflows/*.yml` for:

#### 1. `pull_request_target` Usage
```yaml
# DANGEROUS — fires in the context of the base repo with secret access
on: pull_request_target
```
**Fix:** Only use `pull_request_target` when the workflow needs to write back to the base repo (e.g., labeler, auto-merge). Always add:
```yaml
on:
  pull_request_target:
    types: [opened]
jobs:
  safe:
    if: github.event.pull_request.head.repo.fork == false
```
Or use `pull_request` (safe by default — runs in fork context, no secret access).

#### 2. OIDC Token Scope
```yaml
# OVER-PERMISSIONED — every job gets OIDC access
permissions:
  id-token: write
```
**Fix:** Scope `id-token: write` only to the specific job that needs it:
```yaml
jobs:
  publish:
    permissions:
      id-token: write
      contents: read
  build:
    permissions:
      contents: read  # id-token defaults to 'none' here
```

#### 3. Unpinned Action Versions
```yaml
# INSECURE — tag can be retagged by a compromised owner
uses: actions/checkout@v4
```
**Fix:** Pin to the full commit SHA of the release:
```yaml
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
```

#### 4. Cache Key Injection
The Mini Shai-Hulud attack used cache poisoning across the fork↔base boundary. Review cache keys:
```yaml
# INSECURE — fork can influence cache key content
cache: npm
key: npm-${{ hashFiles('package-lock.json') }}
```
**Fix:** Include the runner context in the cache key to prevent cache sharing across fork boundaries.

### OIDC Federation Grants

If the user publishes npm packages from CI:
- List current OIDC publishers: `npm access list publishers <package>`
- Each entry should be a specific repo + environment, not `*:*`
- Revoke any grants with overly broad patterns

---

## Layer 3 — Repository Clone / IDE Poisoning Check

When cloning a repository or checking out a branch:

```bash
# Scan for known attack persistence files
find . -maxdepth 4 \( \
  -name "router_init.js" -o \
  -name "tanstack_runner.js" -o \
  -name "router_runtime.js" -o \
  -name "vite_setup.mjs" -o \
  -name ".claude" -type d -o \
  -name ".vscode" -type d \
\) 2>/dev/null
```

**What to look for specifically:**
- `.claude/settings.json` or `.claude/setup.mjs` — Mini Shai-Hulud planted hooks here that auto-run on Claude Code launch
- `.vscode/tasks.json` containing `setup.mjs` references — executes on VS Code folder open
- `.cursor/rules/` or `.cursor/setup.mjs` — same pattern for Cursor IDE
- Any `setup.mjs` or `*_runner.js` in project root with large obfuscated payloads

**Remediation:** If found, report and quarantine. Do not open the project in an IDE until the files are removed and their source (committed or injected) is identified.

---

## Layer 4 — Egress Blocking

Maintain a blocklist of known exfiltration endpoints from supply chain attacks:

```
# Mini Shai-Hulud (May 2026)
filev2.getsession.org
seed1.getsession.org
seed2.getsession.org
seed3.getsession.org

# Session P2P seed nodes (generic)
seed.getsession.org
```

**macOS:** Add to `/etc/hosts`:
```
127.0.0.1 filev2.getsession.org
127.0.0.1 seed1.getsession.org
127.0.0.1 seed2.getsession.org
127.0.0.1 seed3.getsession.org
```

**Linux:** Add to iptables/nftables:
```bash
# Block outbound to known exfiltration domains
iptables -A OUTPUT -d filev2.getsession.org -j DROP
```

---

## Layer 5 — Incident Response Procedure

If a compromise is suspected (affected package installed, unfamiliar scripts detected, credential alert):

### Immediate (within 5 minutes)
1. **Disconnect the host from the network** — stops exfiltration. On macOS: turn off Wi-Fi. On CI: cancel the workflow run.
2. **Do not revoke tokens yet** — forensics may need to trace which credentials were accessed. Image or snapshot the host first.
3. **Identify the affected package and version**:
   ```bash
   # Find installed versions
   npm ls @tanstack/react-router 2>/dev/null
   grep -r "tanstack" pnpm-lock.yaml | grep "version:"
   ```

### Short-term (within 1 hour)
4. **Rotate all secrets accessible from that host** — not just npm tokens. The Mini Shai-Hulud worm harvests:
   - AWS access keys (env vars + IMDS)
   - GCP service account tokens
   - Kubernetes service account tokens
   - HashiCorp Vault tokens
   - GitHub PATs / OIDC tokens
   - SSH private keys (`~/.ssh/*`)
   - npm tokens (`~/.npmrc`)
5. **Revoke GitHub OIDC federation grants** for any npm packages published from the affected repo.
6. **Run full credential sweep**:
   ```bash
   # Check for exfiltrated tokens in process memory
   # Check cloud provider audit logs for anomalous API calls
   # Review GitHub audit log for unexpected commits
   ```

### Recovery (within 24 hours)
7. **Image the filesystem** for forensics before cleanup.
8. **Wipe `node_modules`** and reinstall from clean lockfile.
9. **Scan for IDE persistence** — `.claude/`, `.vscode/`, `.cursor/` directories.
10. **Roll back any unintended commits** made by self-propagation (spoofed author commits from `claude@users.noreply.github.com`).
11. **Change CI/CD pipeline credentials** — all of them. Assume every workflow secret was harvested.

### Verification
```bash
# Confirm no compromised versions remain
npm ls <package> 2>/dev/null | grep <affected-range>

# Confirm no persistence files
find ~ -maxdepth 6 \( -name "router_init.js" -o -name "*_runner.js" -o -path "*/.claude/setup.mjs" \) 2>/dev/null

# Confirm lockfile is clean
grep -n "optionalDependencies\|prepare\|preinstall" pnpm-lock.yaml | grep -v "node_modules"
```

---

## Package Manager — Quick Reference

| Action | Safe Command | Why |
|:-------|:-------------|:----|
| Install deps | `npm install --ignore-scripts` | Blocks lifecycle script execution |
| CI install | `npm ci --ignore-scripts` | Fails if lockfile mismatch + blocks scripts |
| pnpm install | `pnpm install --ignore-scripts` | Same protection |
| yarn install | `yarn install --ignore-scripts` | Same protection |
| Add a dep | `npm install <pkg> --ignore-scripts --save-exact` | Pin exact version + block scripts |
| Audit | `npm audit --audit-level=critical` | High-signal vulnerability check |
| Add Pip dep | `pip install <pkg> --require-hashes -r requirements.txt` | Hash-pinned, no execution without verified checksum |
| Audit Pip | `pip-audit` | Check PyPI packages against advisory DB |

---

## Verification Checklist

Every time this skill is triggered, run:

- [ ] Lockfile present and committed?
- [ ] Install command includes `--ignore-scripts`?
- [ ] Post-install audit passed (no critical vulns)?
- [ ] Lockfile diff reviewed for suspicious additions?
- [ ] Known exfiltration endpoints blocked on this host?
- [ ] If cloning: scanned for IDE persistence files?
- [ ] If PR review: `pull_request_target` usage flagged?
- [ ] If PR review: OIDC token scope restricted?
- [ ] If PR review: GitHub Actions pinned to commit SHAs?
- [ ] If CI setup: publish job isolated from build/test job?

---

## Pitfalls

1. **`--ignore-scripts` is not set-and-forget.** Some legitimate packages need lifecycle scripts (node-gyp rebuild, postinstall patches). For known-safe packages, run scripts explicitly: `npm run rebuild` or `npx node-gyp rebuild`.

2. **Lockfiles can be compromised too.** If the attacker has write access to the repository, they can modify the lockfile to point to a malicious tarball. Lockfile review (git diff) is still necessary.

3. **OIDC tokens are ephemeral but dangerous.** They exist in runner memory for the job's duration and can be extracted at runtime (as this attack proved). The only defense is scoping: don't have publish-capable tokens in scope during install.

4. **Sigstore provenance is not a trust signal.** The Mini Shai-Hulud malware generated valid SLSA Build L3 attestations. A valid provenance badge means "this came from the CI system" — not "this is safe."

5. **npm audit coverage lag.** Zero-day advisories take hours to appear in audit feeds. For the first 24 hours after a new supply chain attack, manual detection (lockfile diff, behavior monitoring) is the only option.

6. **Don't rotate tokens before imaging.** If you rotate before forensics, you lose the trail. Image the host, then rotate.

7. **Agent-based cron jobs fail silently for scriptable checks.** If a Hermes cron job loads skills and uses tools to run deterministic commands (`npm audit`, `du`, `find`), it can timeout in the cron session's short-lived environment — and the error won't persist in LCM for debugging. For any cron job that only runs shell commands and reports output, use **no_agent mode** with a shell script (`script=` field). Reserve agent-based cron jobs for tasks that genuinely need LLM reasoning (summarizing web results, synthesizing research). The two patterns have different reliability profiles: scripts always run, agents sometimes don't.

8. **no_agent jobs silently succeed when script file is missing.** When a `no_agent` cron job's `script` file doesn't exist, the cron system reports `last_status: ok` with empty output. Since empty stdout = silent delivery (no message), the job appears healthy but does nothing. The daily advisory cron (`supply-chain-scan.sh`) was silently empty for an unknown period before being caught on 2026-05-28. **Detection:** A `no_agent` job that should report findings but never delivers anything to its channel is suspect. Verify script existence manually: `ls -la ~/.hermes/profiles/senna/scripts/supply-chain-scan.sh`. **Prevention:** After `hermes update`, profile migration, or `~/.hermes` cleanup, verify all no_agent scripts exist. See `cron-pipeline` skill for the full audit command and reconstruction workflow.

---

## Integration With Other Skills

Use after:
- `safe-web-research` — when researching a new package or advisory
- `github-code-review` — when reviewing a PR that changes dependencies or workflows
- `hermes-security-audit` — as part of periodic security reviews
- `requesting-code-review` — when approving dependency updates

References:
- TanStack postmortem: https://tanstack.com/blog/npm-supply-chain-compromise-postmortem
- Socket.dev analysis: https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack
- CVE-2026-45321 / GHSA-g7cv-rxg3-hmpx

---

## Change Log

- **2026-05-28 (v1.3.2)** — Added npm `overrides` technique for transitive dependency vulnerabilities (Layer 1). When `npm audit fix --force` would downgrade a major parent (e.g., Next.js 16→9), use `overrides` in package.json to force the transitive dep to a patched version. Added `references/2026-05-28-supply-chain-fix.md` documenting the HermesMirror + hermes-office fix session. Updated supply-chain-scan.sh to also detect postinstall scripts.
- **2026-05-28 (v1.3.1)** — Added pitfall #8: no_agent cron jobs silently succeed when script file is missing. The daily advisory cron was silently empty until scripts were reconstructed from session history. Cross-references `cron-pipeline` skill for reconstruction workflow.
- **2026-05-14 (v1.3.0)** — Cron job reliability fix: converted daily advisory cron from agent-based (repeatedly errored) to no_agent + shell script mode. Added pitfall #7 (agent-based cron jobs fail silently for scriptable checks). Updated `references/system-automation.md` with new cron setup. Updated `references/2026-05-14-supply-chain-scan.md` with HermesMirror vuln fix.
- **2026-05-12 (v1.2.0)** — Added Layer 0 (Pre-Install Dependency Risk Assessment) with risk category system, presentation methodology, and worked example. Added `references/magicmirror-dependency-analysis.md` as a session-derived worked example. Updated related_skills to include `smart-mirror`. Added `pre-install risk assessment` to trigger patterns.
- **2026-05-12 (v1.1.0)** — Added System-Specific Automation Layer documenting shell wrapper, git hooks, and cron advisory check. Added `references/system-automation.md` and `scripts/verify-guards.sh`. Codified enforcement-over-documentation principle from user setup.
- **2026-05-12 (v1.0.0)** — Initial version. Based on Mini Shai-Hulud (TeamPCP) supply chain attack analysis. Covers install-time guards, CI/CD hardening, IDE poison detection, egress blocking, and full incident response procedure.
