"""Config-file env fallback for the edu-agent skill scripts (standalone mirror of
src/shared/env.py).

These scripts run detached (invoked as subprocesses by precheck.py / postcheck.py, or directly
like generate_voice.py) and can't import `shared`, so this replicates env.py's
`environment > ~/.qwen-mm-plugins/config > default` precedence — the ONE config file shared by
every capability. This lets GUI-launched harnesses (Claude desktop / Codex GUI), which don't
inherit a shell's exported vars, still find DASHSCOPE_API_KEY etc.

Import-only: `from env_config import get_env`. Each consumer reads the value it needs INSIDE the
script (see generate_voice.py), so a secret is never dumped to stdout for the calling agent to
read. There is deliberately no `__main__` KEY=VALUE export here — that shell-eval path exists only
in the video-memory build pipeline, where build_memory.sh consumes it straight into `export`.
"""

from __future__ import annotations

import os


def _config_file() -> str:
    """Config file path (mirrors shared.env): QWEN_MM_CONFIG, else QWEN_MM_CONFIG_DIR/config,
    else ~/.qwen-mm-plugins/config."""
    override = os.environ.get("QWEN_MM_CONFIG")
    if override:
        return os.path.expanduser(override)
    base = os.environ.get("QWEN_MM_CONFIG_DIR") or "~/.qwen-mm-plugins"
    return os.path.join(os.path.expanduser(base), "config")


def _parse_config(text: str) -> dict[str, str]:
    """KEY=VALUE per line; skip blank/# lines; strip `export ` and surrounding quotes."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip().removeprefix("export ").lstrip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            val = val[1:-1]
        key = key.strip()
        if key:
            out[key] = val
    return out


_config_cache: dict[str, str] | None = None


def _config() -> dict[str, str]:
    global _config_cache
    if _config_cache is None:
        try:
            _config_cache = _parse_config(open(_config_file(), encoding="utf-8").read())
        except (OSError, UnicodeDecodeError):
            _config_cache = {}
    return _config_cache


def get_env(name: str, default: str | None = None) -> str | None:
    """Env config read at CALL time. Precedence: environment > user config file > default."""
    val = os.environ.get(name)
    return val if val is not None else _config().get(name, default)
