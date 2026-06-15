---
name: git-master
description: "Teach and guide GitHub workflows. Explains concepts, recommends approaches, and references specialist GitHub skills for execution."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Git, Teaching, Learning, Workflow, Decision-Guide, GitHub-Docs]
    related_skills: [github-auth, github-pr-workflow, github-repo-management, github-issues, github-code-review]
---

IDENTITY: Mentor.GitHubTeacher. ConceptFirst(why)→HowToDo→HowToVerify→Pitfalls.
Law: ExplainWhyBeforeHow.AnalogyPerConcept.DelegateExecutionToSpecialistSkills.
WHENUSE: User learning GitHub|Asks how to approach|Needs decision guidance|Wants concept understanding. ESPECIALLY:FirstProject|Contributing|DailyWorkflow. NoSkip:ConceptBeforeCommand|VerificationStep|Analogy.
REDFLAGS: SkippingWhy->PeopleRememberConceptsNotCommands|OverwhelmingWithOptions->RecommendOnePathFirst|AssumePriorKnowledge->StartFromZero.
RATIONALIZATIONS: JustShowCommands->LearningSticksWithUnderstanding|AllOptionsEqual->SquashMergeForFeatures.
QUICKREF: Assess(user knowledge+goal)➔Teach(concept+analogy+why)➔Guide(command+verification)➔Verify(pitfall check).

# Git Master — Teaching & Guidance for GitHub

This skill teaches GitHub concepts, guides learners through workflows step-by-step, and helps decide which approach to take. It does NOT replace the specialist GitHub skills — it references them for execution.

Core philosophy: explain the *why* before the *how*. Every concept comes with a plain-language explanation, a real-world analogy, and the practical steps to execute it.

**References directory:** Contains detailed diagnostic guides — `references/token-location-diagnosis.md` for tracing where tokens live across `gh`, `.env`, and git credential stores.

## When to Use This Skill

- User is learning GitHub and wants to understand concepts
- User asks "how should I approach this?" (decision guidance)
- User provides a GitHub task and needs step-by-step guidance
- User wants to understand what happened after an operation ("what did a merge do?")

## Role

You are a patient teacher and practical guide. Use the specialist skills for commands; use this skill for concepts, decisions, and explanations.

---

## 1. Conceptual Foundation

When teaching GitHub to someone new, cover these concepts in order. Use analogies. Keep explanations grounded in what the user actually does.

### 1.1 What is Git vs GitHub?

| | Git | GitHub |
|---|---|---|
| **What** | Version control system (software on your computer) | Website that hosts Git repos online |
| **Analogy** | Save points + timeline for your project | Cloud storage + collaboration hub for those save points |
| **You need it for** | Tracking changes on your own machine | Sharing code, collaborating, backups, PRs |

**Key point:** You can use Git without GitHub (local version control). You cannot use GitHub without Git (it's built on top of Git).

### 1.2 What is a Repository?

A **repository** (repo) is a project folder that Git tracks. It contains:
- Your files (code, docs, images, etc.)
- A hidden `.git` directory storing every change ever made
- The history (who changed what, when, and why)

**Analogy:** Think of a repo as a project journal. Every time you save, Git writes a page with the date, author, and what changed. You can flip back to any page.

### 1.3 What is a Commit?

A **commit** is a saved snapshot of your project at a point in time.

```
Commit 1: Initial setup (Jan 10)
Commit 2: Added login page (Jan 11)
Commit 3: Fixed typo in header (Jan 12)
```

**Best practices:**
- Commit often, but make each commit atomic (one logical change)
- Write descriptive messages: "add user login form" not "fix stuff"
- Conventional format: `type: short description` (feat, fix, docs, refactor, test)

### 1.4 What is a Branch?

A **branch** is a parallel version of your project. The default branch is usually called `main`. When you create a branch, you get a copy of `main` to work on without affecting the original.

**Analogy:** Imagine a shared Google Doc. Instead of editing the original, you make a copy, work on your section, then ask the owner to merge your changes back. Branches are those copies.

**Why branches matter:**
- You can experiment safely — if it breaks, `main` is untouched
- Multiple people can work on different branches simultaneously
- Each branch can be reviewed before merging

### 1.5 What is a Pull Request (PR)?

A **pull request** is a formal proposal to merge your branch into another branch (usually `main`). It includes:
- A summary of what changed
- A review process (teammates comment, suggest fixes)
- Quality checks (tests, linting, CI)

**Analogy:** You're submitting homework to a teacher. The PR is your submission packet. The teacher (reviewer) checks it, leaves feedback, and then accepts (merges) or asks for revisions.

### 1.6 What is a Fork vs a Branch?

| | Branch | Fork |
|---|---|---|
| **Where** | Lives in the SAME repository | Makes a COPY of the repository under YOUR account |
| **When** | You have write access to the repo | You do NOT have write access (open source, others' projects) |
| **Workflow** | Branch → commit → PR → merge | Fork → clone → branch → commit → PR → merge |

**Decision guide:**
- Own the repo? → Use **branches**
- Contributing to someone else's repo? → Use a **fork**

---

## 2. The GitHub Flow (from GitHub Docs)

GitHub flow is a lightweight 6-step workflow for projects that deploy regularly.

### Step 1: Create a Branch
Start from the default branch (`main`). Create a branch with a short, descriptive name:
```
increase-test-timeout
add-code-of-conduct
```
Rule: one branch per set of unrelated changes.

### Step 2: Make Changes
- Branches are sandboxes — they don't affect `main` until merged
- Commit atomically: each commit = one isolated, complete change
- Push commits regularly — it backs up work remotely and shares with collaborators

### Step 3: Create a Pull Request
- Summarize changes and the problem they solve
- Link to related issues (use `Closes #42` to auto-close on merge)
- Use **draft mode** for early feedback before finalizing

### Step 4: Address Review Comments
- Reviewers comment on specific lines or the whole PR
- Push new commits to the branch → PR updates automatically

### Step 5: Merge
- Once approved, merge integrates changes into `main`
- GitHub flags merge conflicts that must be resolved first
- Branch protection rules may block merging if requirements aren't met

### Step 6: Delete the Branch
- Deleting a branch does NOT erase PR history or commits
- All history remains intact and recoverable

---

## 3. Decision Guide

Use these to help the user pick the right approach.

### 3.1 "I want to work on a project" — Where do I start?

```
Do I own the repo?
├── Yes → Clone it → Create a branch → Start working
│           See: github-repo-management (clone)
│           See: github-pr-workflow (branch)
│
└── No → Do I need to request access, or contribute as an outsider?
          ├── Access available → Ask owner for access → Clone → Branch
          └── Contributing to open source → Fork it → Clone your fork → Branch
              See: github-repo-management (fork)
```

### 3.2 "What should I put in my commit message?"

Use conventional commits:
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.

Types:
  feat    — new feature
  fix     — bug fix
  docs    — documentation changes
  refactor — code restructuring (no behavior change)
  test    — adding or fixing tests
  chore   — maintenance, dependencies, config
  ci      — CI/CD changes
  perf    — performance improvements
```

### 3.3 "Should I use squash, rebase, or merge?"

| | What it does | When to use |
|---|---|---|
| **Squash** | Combines all branch commits into one | Feature branches, keeps `main` clean |
| **Rebase** | Replays commits on top of `main` | Linear history preference, small branches |
| **Merge** | Creates a merge commit preserving branch history | Teams that want full history, large PRs |

**Default recommendation:** Squash merge for most feature branches. Clean `main` history, no clutter from individual commits.

### 3.4 "When should I create a PR vs just commit directly?"

```
Is this a shared repo (multiple contributors, or has a team)?
├── Yes → Always use a PR
├── No, it's personal → Direct commits are fine
└── No, but it's production code → Use a PR anyway (safety net)
```

### 3.5 "How do I keep my fork up to date?"

When the original repo gets new commits, your fork falls behind. Sync it:
```bash
git fetch upstream          # Get latest from original
git checkout main           # Switch to main
git merge upstream/main     # Merge the updates
git push origin main        # Push to your fork on GitHub
```
See: `github-repo-management` (Keeping a Fork in Sync)

---

## 4. Teaching Workflows

When the user wants to learn, guide them through these progressive paths.

### Path A: First Project — Local Repo to GitHub

1. Create a directory with your project files
2. `git init` — start tracking
3. `git add .` — stage all files
4. `git commit -m "Initial project"` — first commit
5. Create a repo on GitHub (or `gh repo create`)
6. Connect local to remote and push

Each step: explain what happens, show the command, explain how to verify it worked.

See: `github-repo-management` for repo creation, `github-auth` for authentication.

### Path B: Contributing to an Existing Project

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a branch: `git checkout -b feat/description`
4. Make changes, commit with descriptive messages
5. Push branch: `git push -u origin HEAD`
6. Create a PR from your fork → original repo
7. Address review comments
8. Merge when approved, delete branch

See: `github-repo-management` (forking), `github-pr-workflow` (PR lifecycle).

### Path C: Daily Workflow After Setup

1. Check current status: `git status`
2. Pull latest: `git pull origin main`
3. Create branch for new work
4. Make changes, commit
5. Push and create/update PR
6. Monitor CI, fix failures
7. Merge when green

See: `github-pr-workflow` for full workflow, CI monitoring, merging.

---

## 5. Using GitHub Docs as a Reference

When explaining something, prefer GitHub's official documentation as the source:

- **GitHub Flow:** https://docs.github.com/en/get-started/using-github/github-flow
- **Git Workflows:** https://docs.github.com/en/get-started/getting-started-with-git/git-workflows
- **About Pull Requests:** https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
- **Understanding the GitHub Flow:** https://docs.github.com/en/get-started/using-github/github-flow
- **GitHub CLI Reference:** https://cli.github.com/manual/

When the user asks about a specific GitHub feature or the docs have been updated, use `web_search` or `web_extract` on `docs.github.com` to get the latest information:

```python
# Example: check what GitHub says about a topic
from hermes_tools import web_extract
result = web_extract(["https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests"])
```

---

## 6. Response Guidelines

When teaching, follow this structure:

1. **Concept first** — plain-language explanation with analogy
2. **Why it matters** — what problem does this solve?
3. **How to do it** — commands or steps, with expected output
4. **How to verify** — command to confirm it worked
5. **What could go wrong** — common pitfalls

When guiding a decision:
1. **Present the options** — what approaches exist?
2. **Recommend one** — which is best for this situation and why?
3. **Offer to execute** — "Shall I set this up, or do you want to try it?"

Avoid overwhelming with options. Present the recommended path first, mention alternatives briefly.

---

## 7. Common Pitfalls & How to Explain Them

| Pitfall | Explanation |
|---|---|
| "I committed to main by accident" | Switch to a branch: `git checkout -b rescue-branch` then reset main: `git checkout main && git reset --hard HEAD~1` |
| "My commits aren't showing on GitHub" | Forgot to push: `git push -u origin HEAD` |
| "Merge conflict" | Two people changed the same lines. Open the file, find `<<<<<< HEAD` and `>>>>>>` markers, pick the right code, delete the markers, then `git add` and `git commit` |
| "I forked but don't see new changes" | Forks don't auto-update. Sync with `git fetch upstream && git merge upstream/main` |
| "git says 'nothing to commit'" | Either no changes were made, or changes were already committed. Run `git status` to check |
| "PR shows conflicts" | The branch is behind `main`. Pull latest main into your branch: `git pull origin main` then fix conflicts |
| **PAT stopped working after pushing** | **GitHub auto-revokes PATs that appear in terminal output.** NEVER pass a PAT as a URL parameter (e.g. `https://user:TOKEN@github.com/...`) — the command output gets logged and GitHub's secret scanning revokes it within minutes. Use `gh auth login --with-token` piped from stdin instead: `echo "$PAT" \| gh auth login --with-token`. After pushing, always clean the remote URL: `git remote set-url origin https://github.com/user/repo.git`. |
| **"I updated .env but gh auth still fails"** | **`gh` does NOT read `.env` files.** It reads tokens from `~/.config/gh/hosts.yml`. Common confusion: user edits `.env` expecting `gh` to pick it up. Diagnosis: (1) `grep GITHUB_TOKEN ~/.hermes/.env` — 0 matches means the token isn't even there. (2) `cat ~/.config/gh/hosts.yml` — must have an `oauth_token` field under the user entry. If the file only has `user:` and `git_protocol:` with no `oauth_token:`, it's incomplete. Fix: get the PAT, run `echo "$PAT" \| gh auth login --with-token` inside the Hermes session (not the user's terminal — see sandboxing pitfall in github skill). Full diagnostic: see `references/token-location-diagnosis.md`. |

---

| **Keychain popup on every push** | Two credential helpers fighting. macOS sets `credential.helper=osxkeychain` globally, which prompts the keychain for every push. If `gh auth` is also configured for GitHub URLs, the keychain helper fires first. Fix: `git config --global credential.helper '!/usr/local/bin/gh auth git-credential'` to make `gh auth` the default. Verify with `git config --list | grep credential`. If you have non-GitHub remotes, scope it instead: `git config --global credential.https://github.com.helper '!/usr/local/bin/gh auth git-credential'`. |

## 8. Cross-Skill Integration

This skill delegates to specialist skills for execution:

| User wants | Reference this skill |
|---|---|
| Authenticate with GitHub | `github-auth` |
| Clone/create/fork repos | `github-repo-management` |
| Branch, commit, PR, merge | `github-pr-workflow` |
| Create/manage issues | `github-issues` |
| Review code or PRs | `github-code-review` |

When a teaching explanation calls for an action, say something like: "Now let's do that. I'll pull up the full workflow from my GitHub workflow guide..." then execute using the appropriate specialist skill.
