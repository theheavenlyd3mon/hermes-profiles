## Description: <br>
Builds, ships, and debugs native iOS apps across lifecycle, permissions, entitlements, push, widgets, StoreKit, App Store review, device-only failures, privacy manifests, accessibility, and platform-release regressions. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[ivangdavila](https://clawhub.ai/user/ivangdavila) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and engineers use this skill to diagnose, build, and ship native iOS applications at the platform level, including lifecycle, permissions, entitlements, background execution, StoreKit, review, privacy, performance, and device-only failures. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Local project memory may accumulate app identifiers, device UDIDs, client names, release history, review notes, and renewal dates. <br>
Mitigation: Review the configured Clawic data folders periodically and keep credentials out of those files; store only pointers to secret material. <br>
Risk: Generated shell commands or migration guidance can affect simulator, device, keychain, or project state. <br>
Mitigation: Review commands before execution and require explicit confirmation for destructive actions such as simulator erases, keychain wipes, and lossy migrations. <br>
Risk: Platform guidance may propose changes that affect privacy manifests, permissions, entitlements, payments, or App Store review outcomes. <br>
Mitigation: Validate changes against the relevant iOS review, privacy, entitlement, and StoreKit requirements and test on physical devices before release. <br>


## Reference(s): <br>
- [ClawHub iOS skill page](https://clawhub.ai/ivangdavila/skills/ios) <br>
- [Clawic iOS skill homepage](https://clawic.com/skills/ios) <br>
- [Clawic skill library](https://clawic.com) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration] <br>
**Output Format:** [Markdown guidance with inline code and shell commands] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires macOS with xcodebuild for command execution; may update local Clawic project-memory files when durable project facts are produced.] <br>

## Skill Version(s): <br>
1.0.2 (source: SKILL.md frontmatter and server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
