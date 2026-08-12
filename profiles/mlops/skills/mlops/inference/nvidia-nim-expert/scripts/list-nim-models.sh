#!/bin/bash
# Usage: ./list-nim-models.sh
# Requires NVIDIA_API_KEY or OPENAI_API_KEY environment variable

API_KEY="${NVIDIA_API_KEY:-${OPENAI_API_KEY:-}}"
if [ -z "$API_KEY" ]; then
  echo "Error: NVIDIA API key not set. Export NVIDIA_API_KEY or OPENAI_API_KEY"
  exit 1
fi

curl -sL -H "Authorization: Bearer $API_KEY" \
  "https://integrate.api.nvidia.com/v1/models" | python3 -m json.tool
