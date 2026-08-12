#!/usr/bin/env python3
"""
Hermes NVIDIA NIM runner — use from any agent to call NVIDIA cloud models.
Provides a simple function interface and a CLI test mode.
"""
import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

# Try OpenAI SDK
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    OpenAI = None
    HAS_OPENAI = False

from typing import Optional, Dict, Any, List

def _load_api_key() -> Optional[str]:
    """Find NVIDIA API key from common sources."""
    # 1. Check env vars
    key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    # 2. Check ~/.config/nim/.env (try multiple home locations)
    # Hermes may remap HOME, so check common real-user locations
    possible_homes = [
        Path("~"),
        Path.home(),  # fallback to whatever Python thinks home is
    ]
    env_path = None
    for home in possible_homes:
        candidate = home / ".config" / "nim" / ".env"
        if candidate.exists():
            env_path = candidate
            break
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("NVIDIA_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")

    # 3. Check key stored in skill dir (optional)
    key_path = Path("~") / ".hermes" / "profiles" / "senna" / "skills" / "mlops" / "inference" / "nvidia-nim-expert" / ".api_key"
    if key_path.exists():
        return key_path.read_text().strip()

    return None

def get_client() -> Optional[OpenAI]:
    """Return a configured OpenAI-compatible client for NVIDIA NIM."""
    if not HAS_OPENAI:
        print("Error: openai package not installed. Run: pip install openai")
        return None

    api_key = _load_api_key()
    if not api_key:
        print("Error: NVIDIA API key not found.")
        print("Set NVIDIA_API_KEY environment variable or add to ~/.config/nim/.env")
        return None

    base_url = os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")
    return OpenAI(base_url=base_url, api_key=api_key)

def list_models() -> List[Dict[str, Any]]:
    """Return list of available NIM models as dicts."""
    client = get_client()
    if not client:
        return []

    try:
        resp = client.models.list()
        return [{"id": m.id, "context_length": getattr(m, "context_length", None)} for m in resp.data]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

def chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 1024,
    **kwargs
) -> Optional[str]:
    """Run a chat completion and return the assistant's response text."""
    client = get_client()
    if not client:
        return None

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"Completion error: {e}")
        return None

# CLI mode for quick testing
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"

    if mode == "test":
        print("NVIDIA NIM quick test\n")
        models = list_models()
        if not models:
            sys.exit(1)

        print(f"✅ Connected — {len(models)} models available.")
        print("\nTop models:")
        for m in models[:8]:
            print(f"  {m['id']}")

        # Prefer known-working active models; fallback to first that responds
        preferred = ["google/gemma-3-12b-it", "meta/llama-3.3-70b-instruct"]
        test_model = None
        for p in preferred:
            if any(m['id'] == p for m in models):
                test_model = p
                break
        if not test_model:
            # Try first few until one works
            for m in models[:5]:
                test_resp = chat_completion(
                    model=m['id'],
                    messages=[{"role": "user", "content": "OK"}],
                    max_tokens=3, temperature=0.1
                )
                if test_resp:
                    test_model = m['id']
                    break
        if not test_model:
            print("✗ No responding model found")
            sys.exit(1)
        
        print(f"\nTest completion with: {test_model}")
        result = chat_completion(
            model=test_model,
            messages=[{"role": "user", "content": "Say: OK"}],
            max_tokens=5,
            temperature=0.1
        )
        if result:
            print(f"  → {result.strip()}")
            print("\n✓ NVIDIA NIM is working!")
        else:
            print("✗ Completion failed")
            sys.exit(1)

    elif mode == "models":
        models = list_models()
        print(json.dumps(models, indent=2))

    elif mode == "chat":
        # Simple stdin chat
        print("Enter your message (Ctrl+D to send):")
        user_msg = sys.stdin.read().strip()
        if not user_msg:
            print("No input provided")
            sys.exit(1)

        models = list_models()
        if not models:
            sys.exit(1)

        reply = chat_completion(
            model=models[0]["id"],
            messages=[{"role": "user", "content": user_msg}],
            max_tokens=500
        )
        if reply:
            print(reply)
        else:
            sys.exit(1)
