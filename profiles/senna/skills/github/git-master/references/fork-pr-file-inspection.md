# Reading Files from a Fork PR (Before Merge)

When reviewing a PR from a **fork** (not a branch on the same repo), the PR's
files don't exist on the base repo yet. You can't just `git show` them.

## Step 1: Get the fork's owner and branch name

```bash
gh pr view <PR_NUMBER> --repo <OWNER>/<REPO> --json headRefName,headRepositoryOwner
```

Output:
```json
{
  "headRefName": "contrib/my-branch",
  "headRepositoryOwner": {
    "login": "forkuser"
  }
}
```

## Step 2: Fetch the file from the fork's repo via the API

```bash
# Pattern: GET repos/{FORK_OWNER}/{REPO_NAME}/contents/{PATH}?ref={BRANCH}
gh api repos/forkuser/<REPO>/contents/path/to/file.md?ref=contrib/my-branch \
  --jq '.content' | base64 -d
```

The `/contents/` API returns base64-encoded file content. Pipe through
`--jq '.content' | base64 -d` to get the raw text.

## Pitfalls

**Do NOT use `owner:branch` as the ref on the base repo.**
The intuitive `gh api repos/owner/repo/contents/file?ref=forkuser:branch`
returns 404 because the fork's ref doesn't exist on the base repo.
You must query the **fork's** repo directly.

**`gh pr diff` may miss large new files.**
When a PR adds many files (2000+ lines), `gh pr diff` output can be truncated
or the file you need may not appear in a grep. Use the `/contents/` API
approach above for reliable per-file access.

**Large files (>1MB) won't return content in the `/contents/` response.**
GitHub's Contents API has a 1MB limit. For larger files, use the raw URL:
```bash
curl -sL "https://raw.githubusercontent.com/<FORK_OWNER>/<REPO>/<BRANCH>/path/to/file.md"
```

## Alternative: Check out the PR branch locally

If you need to inspect many files, it's faster to fetch the PR branch:
```bash
gh pr checkout <PR_NUMBER> --repo <OWNER>/<REPO>
# Now browse files locally
cat path/to/file.md
```

This creates a local branch tracking the fork's branch. Clean up with:
```bash
git checkout main
git branch -D <branch-name>
```
