# Image Generation Setup & Troubleshooting Reference

## Plugin Provider Structure

```
$HERMES_HOME/plugins/image_gen/    (NOT the hermes-agent install dir)
  ├── fal/         plugin.yaml + __init__.py  (requires FAL_KEY)
  ├── krea/        plugin.yaml + __init__.py  (requires KREA_API_KEY)
  ├── openai/      plugin.yaml + __init__.py  (requires OPENAI_API_KEY)
  ├── openai-codex/ plugin.yaml + __init__.py  (requires hermes auth codex)
  └── xai/         plugin.yaml + __init__.py  (requires XAI_API_KEY)
```

Source tree also has: `tools/image_generation_tool.py` (in-tree FAL backend + tool registration).

## Tool Registration Flow

1. `toolsets.py` defines `_HERMES_CORE_TOOLS` which includes `"image_generate"`
2. `image_generation_tool.py` registers with `check_fn=check_image_generation_requirements`
3. That function checks:
   - First: `FAL_KEY` env var + `fal_client` SDK importable → True
   - Fallback: any plugin-registered provider with `is_available()` → True
   - Otherwise → False (tool not registered)
4. Even if registered, the tool only loads if `image_gen` is in the active platform's `platform_toolsets` list

## Diagnostic Commands

```bash
# 1. Verify keys are loaded
hermes config show 2>&1 | grep -E "FAL|Krea|image"
hermes status 2>&1 | grep -iE "fal|krea|image"

# 2. Check config gates
grep -A20 'platform_toolsets:' ~/.hermes/profiles/<profile>/config.yaml
grep -A10 'plugins:' ~/.hermes/profiles/<profile>/config.yaml | head -20

# 3. Test requirement function (from hermes-agent dir with venv)
cd ~/.hermes/hermes-agent && HERMES_HOME=~/.hermes/profiles/<profile> venv/bin/python -c "
from hermes_cli.env_loader import load_hermes_dotenv
from hermes_constants import get_hermes_home
load_hermes_dotenv(hermes_home=get_hermes_home())
import os
print('FAL_KEY set:', bool(os.getenv('FAL_KEY')))
print('KREA_API_KEY set:', bool(os.getenv('KREA_API_KEY')))
from tools.image_generation_tool import check_image_generation_requirements
print('check passes:', check_image_generation_requirements())
"

# 4. List available providers
cd ~/.hermes/hermes-agent && venv/bin/python -c "
from agent.image_gen_registry import list_providers
from hermes_cli.plugins import _ensure_plugins_discovered
_ensure_plugins_discovered()
for p in list_providers():
    try: print(f'{p.name}: available={p.is_available()}')
    except Exception as e: print(f'{p.name}: error={e}')
"

# 5. Fix missing toolset (add image_gen to CLI)
hermes config set platform_toolsets.cli '[...,"image_gen",...]'

# 6. Fix missing plugins (add fal + krea)
hermes config set plugins.enabled '[...,"image_gen/fal","image_gen/krea",...]'
```

## .env Loading Chain

```
cli.py / run_agent.py
  → import time calls load_hermes_dotenv(hermes_home=get_hermes_home())
  → loads $HERMES_HOME/.env with override=True
  → FAL_KEY, KREA_API_KEY etc. become available in os.environ
```

If `Path.home()` resolves to a profile-specific home (e.g. `~/.hermes/profiles/senna/home`), the .env path doubles up. Always use `get_hermes_home()` from `hermes_constants.py`.
