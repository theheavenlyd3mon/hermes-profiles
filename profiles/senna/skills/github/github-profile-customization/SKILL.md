---
name: github-profile-customization
description: "Customize a GitHub user *profile* — bio, profile README, pinned repos, and repo metadata (description/topics). Covers the API limits that bite: bio needs the 'user' scope, pinned repos are web-UI-only (no API), and gh repo edit has no --json flag. Use when the user asks to 'tidy my GitHub page', 'update my profile', 'pin repos', or 'set my bio/README'."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Profile, README, Pinned-Repos, Bio, Topics]
    related_skills: [github]
---

# GitHub Profile Customization

Managing the *user profile* surface (bio, profile README, pinned repos) is a different problem from repos/PRs. Two of the three operations are API-limited. This skill captures the working commands + the traps.

## Workflow: present drafts, then push

**This user reviews drafts before public changes go live.** When asked to update a bio, README, or pin set, first show the exact text/list, get explicit approval, then execute. Do not push public-facing profile changes blind.

## 1. Bio / name / company / location (the `user` object)

- Patch via REST:
  ```bash
  gh api user -X PATCH -f bio="Aspiring solo dev — UE5 game development, AI tooling, and agent-assisted workflows."
  ```
- **GOTCHA — `user` scope required.** A token carrying only `repo`/`gist`/`read:org`/`workflow` returns:
  `404 Not Found` + `"This API operation needs the \"user\" scope. To request it, run: gh auth refresh -h github.com -s user"`
  Fix: `gh auth refresh -h github.com -s user` (opens browser for scope grant), then retry. Anticipate this whenever the token was created repo-only.
- Web fallback (no scope needed): github.com/settings/profile → Bio field.

## 2. Profile README (`<username>/<username>` repo)

The profile README is the `README.md` inside a repo named *exactly* after the account (e.g. `<your-github-username>/<your-github-username>`). It renders on the profile page above the pinned grid.

- Read the current blob SHA first (required for the PUT update):
  ```bash
  gh api repos/<user>/<user>/contents/README.md --jq '.sha'
  ```
- Write the new content (base64-encoded):
  ```bash
  B64=$(base64 < /tmp/rm.md | tr -d '\n')   # macOS base64; Linux may need `base64 -w0`
  gh api repos/<user>/<user>/contents/README.md -X PUT \
    -f message="Update profile README" \
    -f sha=<SHA_FROM_ABOVE> \
    -f content="$B64"
  ```
- Replace (not append) the whole file — it's a full content PUT keyed by SHA.

## 3. Pinned repositories — WEB UI ONLY (no API)

- **There is no API to set pinned repos.** GitHub's GraphQL schema exposes no `updatePinnedRepositories` or `pinRepository` mutation — introspection confirms only `pinIssue`/`pinIssueComment`/`unpinIssue` (those pin *issues*, not repos). No REST endpoint exists either.
- Any attempt like `gh api graphql -f query='mutation { updatePinnedRepositories(...) }'` fails with:
  `Field 'updatePinnedRepositories' doesn't exist on type 'Mutation'`.
- **Do it in the web UI:** Profile page → pin/gear icon ("Customize your pins") → select 3–6 repos → Save.
- When the user asks to pin repos: give the exact list, flag it as a manual web step, and do NOT waste an API call attempting it.
- Verifier (if a mutation name is ever suspected wrong):
  ```bash
  gh api graphql -f query='{ __schema { mutationType { fields { name } } } }' \
    | tr -d ' {}[]",' | tr ',' '\n' | grep -i pin
  ```

## 4. Repo metadata (description + topics) — the easy one

- ```bash
  gh repo edit <owner>/<repo> --description "..." --add-topic ue5 --add-topic game-development
  ```
- **GOTCHA — `gh repo edit` has NO `--json` flag.** Chaining `--json` for verification errors out before applying. Verify separately:
  ```bash
  gh repo view <owner>/<repo> --json description,repositoryTopics
  ```
- Topics are lowercase-hyphenated; malformed ones are silently dropped (no error).
- Useful for making pinned/starred repos discoverable: add `description` + 5–7 topics.

## Quick decision table

| Task | Method | Blocker |
|------|--------|---------|
| Set bio | `gh api user -X PATCH` | needs `user` scope |
| Edit profile README | `gh api .../contents/README.md -X PUT` | needs current SHA |
| Pin repos | Web UI only | no API exists |
| Repo description/topics | `gh repo edit` | verify with `gh repo view`, not `--json` |

## Overlap note
This skill is a focused companion to the broader `github` skill (which covers auth, PRs, issues, repo lifecycle). The `github` skill's SKILL.md currently lacks a profile-customization section; the curator should fold this content into `github` and retire this standalone skill once `skill_manage` can patch the nested `github/github-auth` entry.
