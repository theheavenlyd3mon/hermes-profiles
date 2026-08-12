#!/usr/bin/env python3

"""Quick start: Test NVIDIA NIM connection and list models."""
import os
import json
from openai import OpenAI

def main():
    api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: Set NVIDIA_API_KEY or OPENAI_API_KEY")
        return
    
    base_url = "https://integrate.api.nvidia.com/v1"
    client = OpenAI(base_url=base_url, api_key=api_key)
    
    try:
        # Fetch models
        resp = client.models.list()
        models = list(resp.data)
        print(f"✓ Connected! {len(models)} models available:\n")
        for m in models[:5]:
            print(f"  {m.id}")
        if len(models) > 5:
            print(f"  ... and {len(models) - 5} more")
        
        # Quick test completion
        print("\nRunning a quick test completion...")
        completion = client.chat.completions.create(
            model=models[0].id,
            messages=[{"role": "user", "content": "Say 'NIM is working' in 3 words"}],
            max_tokens=20
        )
        print(f"  Response: {completion.choices[0].message.content.strip()}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()
