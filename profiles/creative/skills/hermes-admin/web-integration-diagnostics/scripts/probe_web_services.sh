#!/usr/bin/env bash
# probe_web_services.sh — one-shot health check for Firecrawl + Browserbase API keys.
# Usage: probe_web_services.sh [path/to/.env]
#   default: ~/.hermes/profiles/creative/.env
# Exit code 0 if both services respond; 1 otherwise.
# Never prints full keys — masked prefixes only.
set -uo pipefail

ENV_FILE="${1:-$HOME/.hermes/profiles/creative/.env}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found" >&2
  exit 1
fi

get() { grep -E "^$1=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '\r'; }

FC_KEY="$(get FIRECRAWL_API_KEY)"
BB_KEY="$(get BROWSERBASE_API_KEY)"
BB_PROJ="$(get BROWSERBASE_PROJECT_ID)"

mask() { local s="$1"; if [ "${#s}" -le 9 ]; then echo "****"; else echo "${s:0:9}****"; fi; }

FAIL=0

echo "== Firecrawl (Authorization: Bearer) =="
if [ -n "$FC_KEY" ]; then
  CODE=$(curl -s -o "$TMP/fc.json" -w "%{http_code}" --max-time 40 \
    -X POST https://api.firecrawl.dev/v1/scrape \
    -H "Authorization: Bearer $FC_KEY" -H "Content-Type: application/json" \
    -d '{"url":"https://example.com","formats":["markdown"]}')
  OK=$(python3 -c "import json;print(json.load(open('$TMP/fc.json')).get('success'))" 2>/dev/null)
  echo "  scrape example.com: HTTP $CODE success=$OK  (key $(mask "$FC_KEY"))"
  { [ "$CODE" = "200" ] && [ "$OK" = "True" ]; } || FAIL=1
else
  echo "  missing FIRECRAWL_API_KEY"
  FAIL=1
fi

echo "== Browserbase (X-BB-API-Key) =="
if [ -n "$BB_KEY" ] && [ -n "$BB_PROJ" ]; then
  curl -s -o "$TMP/bb.json" --max-time 30 \
    -X POST https://api.browserbase.com/v1/sessions \
    -H "X-BB-API-Key: $BB_KEY" -H "Content-Type: application/json" \
    -d "{\"projectId\":\"$BB_PROJ\"}"
  SID=$(python3 -c "import json;print(json.load(open('$TMP/bb.json')).get('id',''))" 2>/dev/null)
  if [ -n "$SID" ]; then
    echo "  session create: OK ($SID)  (key $(mask "$BB_KEY"))"
    sleep 3
    curl -s -o "$TMP/bb2.json" --max-time 20 \
      "https://api.browserbase.com/v1/sessions/$SID" -H "X-BB-API-Key: $BB_KEY"
    python3 -c "import json;d=json.load(open('$TMP/bb2.json'));print('  status:',d.get('status'),'| proxy:',d.get('proxy'),'| region:',d.get('region'))" 2>/dev/null
    # cleanup; a 404 here is fine (session may already auto-expire)
    curl -s -o /dev/null --max-time 20 -X DELETE \
      "https://api.browserbase.com/v1/sessions/$SID" -H "X-BB-API-Key: $BB_KEY"
  else
    echo "  session create FAILED: $(head -c 200 "$TMP/bb.json")"
    FAIL=1
  fi
else
  echo "  missing BROWSERBASE_API_KEY or BROWSERBASE_PROJECT_ID"
  FAIL=1
fi

echo
if [ "$FAIL" = "0" ]; then
  echo "RESULT: both services OK"
else
  echo "RESULT: one or more checks FAILED"
fi
exit "$FAIL"
