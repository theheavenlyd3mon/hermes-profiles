## Description: <br>
Auto-learns when to plan vs execute directly. Adapts planning depth to task type. Improves strategy through outcome tracking. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[ivangdavila](https://clawhub.ai/user/ivangdavila) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Agents use this skill to decide when a task needs planning, choose an appropriate planning depth, and improve future plans through outcome tracking. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill's broad planning guidance may activate more often than users expect. <br>
Mitigation: Use narrower activation wording or disable the skill in workflows where minimal planning overhead is preferred. <br>
Risk: Plans and learned adjustments can introduce incorrect or misleading task guidance. <br>
Mitigation: Review plans and outcome-derived adjustments before relying on them for high-stakes, novel, or hard-to-reverse work. <br>


## Reference(s): <br>
- [Plan on ClawHub](https://clawhub.ai/ivangdavila/plan) <br>
- [Planning Strategies](artifact/strategies.md) <br>
- [Outcome Tracking](artifact/outcomes.md) <br>


## Skill Output: <br>
**Output Type(s):** [Guidance, Markdown, Text] <br>
**Output Format:** [Markdown planning guidance and outcome notes] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May recommend different planning depth levels and human validation for higher-risk tasks.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
