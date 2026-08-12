#!/usr/bin/env python3
"""NVIDIA NIM quick test — verifies API key, lists models, runs a sample completion."""
import os
import sys
import json
from pathlib import Path

# Check configured key sources
sources = [
    ("env var", os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")),
    ("~/.config/nim/.env", None),
    ("Hermes skill scripts", None),
]

# Try ~/.config/nim/.env if env var not set
if not sources[0][1]:
    env_path = Path.home() / ".config" / "nim" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("NVIDIA_API_KEY="):
                os.environ["NVIDIA_API_KEY"] = line.split("=", 1)[1].strip()
                sources[1] = (f".env file ({env_path})", os.environ["NVIDIA_API_KEY"])
                break

api_key = sources[0][1] or (sources[1][1] if len(sources) > 1 and sources[1] else None)

print("=" * 55)
print("  NVIDIA NIM Quick Test")
print("=" * 55)

if not api_key:
    print("\n✗ NVIDIA API key not found.")
    print("\nSet it via one of these methods:")
    print("  1. Export in shell: export NVIDIA_API_KEY=\"nv-xxxxx\"")
    print("  2. Add to ~/.config/nim/.env:")
    print("     NVIDIA_API_KEY=nv-xxxxx")
    print("  3. Use the key directly inline: NVIDIA_API_KEY=nv-xxxxx python3 test_nim.py")
    print("\nGet your key at: https://build.nvidia.com/models")
    print("  (Sign in → Get API Key)")
    sys.exit(1)

print(f"✓ API key found: {api_key[:12]}...")

try:
    from openai import OpenAI
except ImportError:
    print("✗ OpenAI SDK not installed.")
    print("  Install with: pip install openai")
    sys.exit(1)

base_url = os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")
client = OpenAI(base_url=base_url, api_key=api_key)

print(f"✓ Endpoint: {base_url}")

# 1. Fetch and list models
print("\nFetching available models...")
try:
    resp = client.models.list()
    models = list(resp.data)
    print(f"✓ Success! {len(models)} models available.")

    if models:
        print("\nFirst 5 models:")
        for m in models[:5]:
            ctx = getattr(m, "context_length", "?")
            print(f"  • {m.id}  (ctx: {ctx})")
        if len(models) > 5:
            print(f"  ... and {len(models) - 5} more")
except Exception as e:
    print(f"✗ Failed to fetch models: {e}")
    print("  Check your API key and network connectivity.")
    sys.exit(1)

# 2. Quick test completion
if models:
    test_model = models[0].id
    print(f"\nRunning quick test on: {test_model}")
    try:
        completion = client.chat.completions.create(
            model=test_model,
            messages=[{"role": "user", "content": "Say 'NIM ready' in 2 words"}],
            max_tokens=10,
            temperature=0.3
        )
        msg = completion.choices[0].message.content.strip()
        print(f"  → {msg}")
        print("\n✓ NVIDIA NIM is working!")
    except Exception as e:
        print(f"✗ Completion failed: {e}")

print("\n" + "=" * 55)
print("  Done. For directory:")
print("  source ~/.config/nim/env.sh  (or add exports to ~/.zshrc)")
print("=" * 55)
