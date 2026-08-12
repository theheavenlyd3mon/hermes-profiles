#!/usr/bin/env python3
"""Rebuild context_length_cache.yaml from models_dev_cache.json.

Usage: python3 rebuild_context_cache.py [profile_dir]
  profile_dir defaults to ~/.hermes/profiles/senna

Reads models_dev_cache.json for authoritative context lengths (limit.context),
maps providers to base URLs from config.yaml, and writes the full cache file.
"""
import json
import sys
import os

def main():
    profile = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.hermes/profiles/senna")
    dev_path = os.path.join(profile, "models_dev_cache.json")
    out_path = os.path.join(profile, "context_length_cache.yaml")

    with open(dev_path) as f:
        dev_cache = json.load(f)

    # Provider -> base URL mapping.
    # ponytail: hardcoded for senna; extend when adding providers
    URL_MAP = {
        "alibaba": "https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1",
        "alibaba-coding-plan": "https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1",
        "openrouter": "https://openrouter.ai/api/v1",
        "deepseek": "https://api.deepseek.com",
        "anthropic": "https://api.anthropic.com",
        "kimi-coding": "https://api.kimi.com/coding",
        "kimi-coding-cn": "https://api.kimi.com/coding",
        "minimax": "https://api.minimax.chat/v1",
        "minimax-cn": "https://api.minimax.chat/v1",
        "zai": "https://open.bigmodel.cn/api/paas/v4",
        "xiaomi": "https://api.xiaomimimo.com/v1",
        "nvidia": "https://integrate.api.nvidia.com/v1",
        "xai-oauth": "https://api.x.ai/v1",
        "arcee": "https://api.arcee.ai/v1",
        "copilot": "https://api.githubcopilot.com",
        "opencode-zen": "https://opencode.ai/api/v1",
        "huggingface": "https://api-inference.huggingface.co/v1",
    }
    # Nous inference API serves OpenRouter-style model IDs
    NOUS_URL = "https://inference-api.nousresearch.com/v1"

    entries = {}

    for prov, pdata in dev_cache.items():
        base_url = URL_MAP.get(prov)
        if not base_url:
            continue
        models = pdata.get("models", {})
        for mid, mdata in models.items():
            lim = mdata.get("limit", {})
            ctx = lim.get("context") if isinstance(lim, dict) else None
            if ctx and ctx > 0:
                entries[f"{mid}@{base_url}"] = ctx
                entries[f"{mid}@{base_url}/"] = ctx

    # Also add Nous inference API entries for openrouter models
    if "openrouter" in dev_cache:
        models = dev_cache["openrouter"].get("models", {})
        for mid, mdata in models.items():
            lim = mdata.get("limit", {})
            ctx = lim.get("context") if isinstance(lim, dict) else None
            if ctx and ctx > 0:
                entries[f"{mid}@{NOUS_URL}"] = ctx
                entries[f"{mid}@{NOUS_URL}/"] = ctx

    # Write sorted YAML
    lines = ["context_lengths:"]
    for key in sorted(entries.keys()):
        lines.append(f"  {key}: {entries[key]}")

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(entries)} entries to {out_path}")

if __name__ == "__main__":
    main()
