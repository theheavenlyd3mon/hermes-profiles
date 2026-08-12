# Onboarding Docs via `educate`

Use when the user asks for a beginner guide, repo orientation, or docs that explain Hermes profiles/fleet concepts to a newcomer.

## Trigger signals
- "create a guide for new users"
- "explain PersRubric / token-compression"
- "explain what each profile does"
- "explain educate in the fleet"

## Pattern
1. Delegate the doc work to `educate` if available.
2. Provide the exact source material/facts to use: current profile list, specializations, fleet roles.
3. Ask `educate` to produce a beginner guide plus any composition examples.
4. Review for drift against the actual `profiles/` directory; fix dead links and missing new profiles.
5. Link the guide from the top-level README.

## Anti-pattern
- Don't write the beginner prose yourself in-context if `educate` is available; route it.

## Example
Input: tutorial + profile set + `educate` skills
Output: `guides/getting-started-with-hermes-profiles.md` covering fleet map, profile tables, model-selection guidance, `educate` compositions, `PersRubric`, and `token-compression`.
