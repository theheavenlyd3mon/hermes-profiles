#!/bin/bash
# Usage: ./test-nim-connection.sh
# Verifies your NVIDIA API key can access the NIM models endpoint

API_KEY="${NVIDIA_API_KEY:-${OPENAI_API_KEY:-}}"
if [ -z "$API_KEY" ]; then
  echo "Error: NVIDIA API key not set (NVIDIA_API_KEY or OPENAI_API_KEY)"
  exit 1
fi

response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -H "Authorization: Bearer $API_KEY" \
  "https://integrate.api.nvidia.com/v1/models")

body=$(echo "$response" | grep -v "HTTP_CODE")
code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)

if [ "$code" = "200" ]; then
  echo "✓ Connection successful. Models received:"
  count=$(echo "$body" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['data']))" 2>/dev/null)
  if [ -n "$count" ]; then
    echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'\n  {len(d["data"])} models available\n'); [print(f'  - {m["id"]} (ctx:{m.get("context_length","?")} tokens)') for m in d['data'][:5]]; print('  ...')"
  else
    echo "$body"
  fi
else
  echo "✗ Connection failed (HTTP $code):"
  echo "$body"
  exit 1
fi
