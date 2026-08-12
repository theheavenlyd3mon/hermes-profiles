---
name: python-dotenv-secrets
description: "Wire secrets into a Python project via a gitignored .env + committed .env.example + python-dotenv load_dotenv(), and avoid the pytest tests/ collection footgun."
version: 1.0.0
author: Hermes Agent (Senna)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [secrets, dotenv, env, python, config, gitignore, pytest]
    related_skills: [project-workspace, frontend-scaffold]
---

IDENTITY: SecretsInDotenv{CommittedTemplate, GitignoredReal, LoadAtImport}. CoreRole: Add local-secret loading to a Python repo the standard, fork-proven way — never commit keys, never hand-set env vars per shell.
Law: `.env` is for secrets only (API keys, tokens, passwords). All behavioral settings stay in `config.yaml`. A `.env.example` with only commented placeholders is committed; the real `.env` is gitignored.
WHENUSE: Project needs API keys/tokens read from env; user says "store keys hidden", "add .env", "where do secrets go", or `api_key_env` in config resolves to an unset env var (crashes with "Could not resolve authentication method").
REDFLAGS: Committing .env -> leak | Hardcoding key in source -> leak | Putting behavior flags in .env -> fork rule violation | Trusting `pytest tests/` 0-collected as "tests pass" -> false negative.

# Python .env Secrets Pattern

## The pattern (4 parts, all required)

1. **`.env.example`** — committed. Only commented placeholders + a one-line "copy to `.env` and fill in" header. No real values, ever.
2. **`.env`** — gitignored. Real keys. Never committed. (Add `.env` to `.gitignore`.)
3. **`python-dotenv`** — add to `requirements.txt`. Call `load_dotenv()` at the TOP of the module that reads secrets (before any client is constructed), so the keys land in `os.environ`.
4. **Config reads the env var by name** — the config's `api_key_env` (or equivalent) must name the exact key in `.env` (e.g. `ANTHROPIC_API_KEY`). `llm.py` does `os.getenv(config.llm_api_key_env)`.

### Minimal load_dotenv wiring (llm.py-style)
```python
import os
from dotenv import load_dotenv

load_dotenv()  # pull .env secrets into os.environ before any client init

class LLM:
    def __init__(self, config):
        self.api_key = os.getenv(config.llm_api_key_env) or ""
```

`load_dotenv()` is idempotent and a no-op if `.env` is absent — safe to call unconditionally.

## Secrets-vs-behavior split (fork rule, load-bearing)
The reference fork's `AGENTS.md` is explicit: **`.env` is for secrets only.** Do NOT tell users to set behavioral flags (timeouts, thresholds, feature flags, model names) in `.env`. Those go in `config.yaml`. Reject any PR that says "set X in your .env" unless X is a credential. Bridge a credential to an internal env var if a mechanism needs one, but user docs point at `config.yaml`.

## Verification (prove the wiring, don't assert it)
After adding the pattern, prove a key in `.env` reaches the client WITHOUT a real key:
```bash
printf 'ANTHROPIC_API_KEY=test_key_123\n' > .env
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; from llm import LLM; from agent import Config; c=Config(...); l=LLM(c); print('wired =', l.api_key=='test_key_123')"
# then restore: printf 'ANTHROPIC_API_KEY=\n' > .env
```
And confirm `.env` is NOT tracked: `git ls-files | grep -E '^\.env$' && echo LEAK || echo OK`.

## Pitfall — pytest `tests/` collects 0 but bare `pytest` passes (silent false negative)
If tests use repo-root-relative imports (`from agent import ...`) and you run `python3 -m pytest tests/` (or `pytest tests/`), pytest sets **rootdir to `tests/`**, so the repo root is NOT on `sys.path` → `ModuleNotFoundError: No module named 'agent'` → **0 tests collected**. No error, just "No tests collected" — looks like a failure but isn't; the same tests pass under bare `pytest` / `pytest .`.
Fix: add a root `conftest.py` (see `templates/conftest.py`) so the repo root is importable under ANY invocation. After adding it, verify all three collect+pass: `pytest .`, `pytest tests/`, `pytest -q`.
Do NOT "fix" the tests by removing the root-relative import — the import is correct; only the collection path was wrong.

## Pitfall — Pyright flags `dotenv` unresolved until install
`from dotenv import load_dotenv` shows `reportMissingImports` in the LSP until `python-dotenv` is installed in the active venv. It's not a code error — `pip install python-dotenv` clears it. Confirm with `python3 -c "import dotenv"`.

## Pitfall — `load_dotenv()` crashes under `python3 - <<'PY'` heredocs
`load_dotenv()` with no args calls `find_dotenv()`, which walks the call-stack frames expecting a real `__main__` file. Under stdin-exec (`python3 - <<'PY' ...`) there is no file frame, so it raises `AssertionError: frame.f_back is not None` — even though the identical code works fine under `python3 -m agent`. Fix: pass the path explicitly in any verification snippet that loads secrets from a heredoc: `load_dotenv(dotenv_path=".env")`.

## Pitfall — swapping providers = change TWO fields, not one
`config.yaml`'s `llm.api_key_env` and the key NAME in `.env` must move together. If the user has an OpenRouter key (not Anthropic), flipping only `provider: openrouter` is not enough — the agent still reads `ANTHROPIC_API_KEY` (unset) and crashes with an auth error. Required pair:
```yaml
llm:
  provider: "openrouter"
  model: "anthropic/claude-sonnet-4"   # OpenRouter uses its own slug, not the bare Anthropic name
  api_key_env: "OPENROUTER_API_KEY"
  base_url: ""                          # empty → client defaults to https://openrouter.ai/api/v1
```
and `.env` holds `OPENROUTER_API_KEY=***`. For OpenAI-direct use `api_key_env: OPENAI_API_KEY` + `base_url` empty. For Ollama/local no key is needed. The OpenAI-style client path (which OpenRouter shares) sets the base URL itself when `base_url` is empty, so leave it blank rather than guessing.

## Pitfall — don't burn a generation to prove a key works
Before wiring a provider, confirm the key is valid AND reaches the client WITHOUT spending an inference token. Most providers expose a tokenless auth endpoint:
- OpenRouter: `GET https://openrouter.ai/api/v1/auth/key` with `Authorization: Bearer <key>` returns the key `id`/`label`. A 401 means the key is bad/unset; a 200 means it's accepted (no generation cost).
- Anthropic/OpenAI: no equivalent free endpoint — for those, use the `os.getenv(...)` wiring check above; the cheapest safe live probe is one short completion.
This catches "key unset / wrong env-var name / provider mismatch" before the agent burns a real call. Pair it with the swap-providers pitfall: flipping `provider` alone is not enough — `api_key_env` and the `.env` key name must move together.

## When NOT to use .env
- A single-shot script you run once with `export KEY=...` inline — YAGNI.
- Secrets that must come from a real secret manager (Vault, cloud IAM) in prod — `.env` is for local dev. In that case still keep `.env.example` as the local-dev contract.

## Files in this skill
- `templates/env.example` — copy to your repo as `.env.example` (rename on copy).
- `templates/conftest.py` — root conftest that fixes the pytest `tests/` collection footgun. Copy to repo root.
