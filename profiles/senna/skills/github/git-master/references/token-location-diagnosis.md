# Token Location Diagnosis

When `gh auth status` reports "invalid token" or "The token in default is invalid," the token is either missing, stale, or in the wrong place. This reference covers every location a GitHub token can live and how to check each one.

## Where `gh` reads tokens

`gh` reads tokens from **one place only**: `~/.config/gh/hosts.yml` (or `$GH_CONFIG_DIR/hosts.yml`).

A valid `hosts.yml` looks like:
```yaml
github.com:
    git_protocol: https
    users:
        <your-github-username>:
            oauth_token: ghp_XXXXXXXXXXXXXXXXXXXX
            oauth_token_cmd: ""
    user: <your-github-username>
    oauth_token: ghp_XXXXXXXXXXXXXXXXXXXX
```

**Minimum required fields:** `user`, `users.<username>.oauth_token`, and top-level `oauth_token`. If ANY of these is missing, `gh auth status` will report the token as invalid.

### Common broken states

1. **No `oauth_token` at all** — file only has `user:` and `git_protocol:`. Happens when user runs `gh auth login` but closes the browser before completing auth.
2. **Top-level `oauth_token` present but `users.<name>.oauth_token` missing** (or vice versa). Both must exist.
3. **Token is the literal string `""`** — placeholder, not a real token.

## Where `.env` tokens live (NOT read by `gh`)

These are read by **Hermes and scripts**, NOT by `gh` CLI:
- `~/.hermes/.env` (root)
- `~/.hermes/profiles/<name>/.env` (per-profile, often symlinked to root)

Check if a token exists:
```bash
grep -n 'GITHUB_TOKEN' ~/.hermes/.env ~/.hermes/profiles/*/.env 2>/dev/null
```

**If 0 matches:** The token was never added, or was added under a different key name (e.g. `GH_TOKEN`, `GITHUB_PAT`).

## Where git reads tokens

Git uses its own credential system, separate from `gh`:
- `~/.git-credentials` (if `credential.helper = store`)
- In-memory cache (if `credential.helper = cache`)
- Embedded in remote URLs: `https://user:token@github.com/...`

Check:
```bash
git config --global credential.helper
cat ~/.git-credentials 2>/dev/null | grep github
git remote -v  # in each repo
```

## Diagnostic flowchart

```
gh auth status → "invalid token" or "not logged in"
│
├─ cat ~/.config/gh/hosts.yml
│  ├─ File missing → gh was never authenticated. Run: echo "$PAT" | gh auth login --with-token
│  ├─ No oauth_token field → Incomplete auth. Re-run: echo "$PAT" | gh auth login --with-token
│  └─ oauth_token exists but still fails → Token was revoked or expired. Get a new PAT.
│
├─ grep GITHUB_TOKEN ~/.hermes/.env
│  ├─ 0 matches → Token not in .env (user may have edited wrong file)
│  └─ Line exists → Extract and re-inject: grep "^GITHUB_TOKEN=" ~/.hermes/.env | cut -d= -f2 | gh auth login --with-token
│
└─ git push still fails after gh auth OK?
   ├─ Check embedded tokens: git remote -v | grep "@"
   └─ Run: gh auth setup-git
```

## Hermes profile sandboxing

When running inside a Hermes profile, `$HOME` is remapped to `~/.hermes/profiles/<name>/home/`. This means:
- `gh` inside Hermes reads from `~/.hermes/profiles/<name>/home/.config/gh/hosts.yml`
- `gh` on the user's terminal reads from `~/.config/gh/hosts.yml`

These are **different files**. A token authenticated in one context is invisible to the other.

**Fix:** After authenticating in one context, sync to the other:
```bash
# From Hermes → user's terminal
cp ~/.hermes/profiles/<name>/home/.config/gh/hosts.yml ~/.config/gh/hosts.yml

# From user's terminal → Hermes
cp ~/.config/gh/hosts.yml ~/.hermes/profiles/<name>/home/.config/gh/hosts.yml
```

**Better fix:** Always authenticate from within the Hermes session so the token lands in the right sandboxed path.
