# Integration Test Protocol: HermesMirror Headless Server

> Full end-to-end test procedure for verifying Hermes modules load and communicate in headless/server-only mode.

## Pre-requisites

- Hermes gateway running (port 8643 for kanban API plugin)
- Project cloned at `~/projects/HermesMirror`
- Node.js 22+ installed

## Test Steps

### 1. Verify gateway is live

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8643/api/kanban/board
# Expected: 200

curl -s http://127.0.0.1:8643/api/kanban/board | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d.get(\"tasks\",[]))} tasks')"
# Expected: N tasks (any positive number)
```

### 2. Kill any stale server on port 8080

```bash
lsof -i :8080 -P -n | grep LISTEN | awk '{print $2}' | xargs kill 2>/dev/null
sleep 2
lsof -i :8080 -P -n
# Expected: no output (port free)
```

### 3. Start headless server with log capture

```bash
node serveronly/index.js > /tmp/mm-server.log 2>&1 &
```

Or via npm script:
```bash
npm run server
```

### 4. Wait for module loading (5-10 seconds)

```bash
sleep 8
cat /tmp/mm-server.log
```

Expected output includes:
- `All module helpers loaded.`
- No errors, no `Module helper 'hermes-bridge' not found`
- No `ECONNREFUSED` or connection errors

### 5. Verify server is serving HTTP

```bash
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:8080/
# Expected: HTTP 200
```

On IPv6-only servers:
```bash
curl -s -o /dev/null -w "HTTP %{http_code}" "http://[::1]:8080/"
# Expected: HTTP 200
```

### 6. Verify Socket.IO endpoint

```bash
curl -s "http://localhost:8080/socket.io/?EIO=4&transport=polling"
# Expected: starts with "0{" (Socket.IO handshake)
```

### 7. Wait for bridge polling cycles (30+ seconds)

The bridge polls every 30s by default. For a thorough test, wait 35s and check for multiple poll cycles:

```bash
sleep 35
wc -l /tmp/mm-server.log
grep -c "Gateway fetch" /tmp/mm-server.log
# Expected: 2+ fetch events (first at ~0s, second at ~30s)
grep -c "ERROR\|error\|Error\|ECONNREFUSED" /tmp/mm-server.log
# Expected: 0 errors
```

### 8. Run config validation

```bash
npm run config:check
# Expected: Clean exit (no errors)
```

### 9. Run test suite

```bash
npm test 2>&1 | grep -E "(Tests|PASS|FAIL|✓|✗)" | tail -5
# Expected: ~357/358 tests pass (1 pre-existing macOS systeminfo check)
```

### 10. Cleanup

```bash
SERVER_PID=$(lsof -i :8080 -P -n | grep LISTEN | awk '{print $2}')
if [ -n "$SERVER_PID" ]; then kill "$SERVER_PID"; fi
rm -f /tmp/mm-server.log
```

## Troubleshooting

### Server won't start (port 8080 in use)

```bash
lsof -i :8080 -P -n | head -10
# Identify the process, kill it, retry
```

### Bridge not polling

Check the node_helper.js `start()` method — it must self-start with defaults in headless mode:

```js
start() {
    const config = this.config && this.config.gatewayUrl ? this.config : {
        gatewayUrl: "http://127.0.0.1:8643",
        refreshInterval: 30
    };
    this._initPolling(config);
}
```

Without this, the bridge waits for a `CONFIG` notification from a browser client that never comes in headless mode.

### Wrong gateway URL

The default URL must match the kanban API plugin port (8643), not the main Hermes gateway (8642). Check both `hermes-bridge.js` (client defaults) and `node_helper.js` (fallback defaults).
