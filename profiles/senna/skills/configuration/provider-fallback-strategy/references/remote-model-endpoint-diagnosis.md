# Remote Self-Hosted Model Endpoint Diagnosis

## Scenario

User reports: "the model we set up didn't connect correctly"

The model is a self-hosted endpoint on another machine (e.g., llama.cpp on a Windows PC with a local GPU, Ollama on a home server, vLLM on a remote box). Connection is via Tailscale or LAN.

## Diagnostic Flow

### Step 1: Check what's currently configured

```bash
# What does the profile config say about this endpoint?
grep -A8 "fallback_providers" ~/.hermes/profiles/<profile>/config.yaml
```

**What happened here:** The fallback_providers only had a DeepSeek entry — the custom endpoint (`stewart.tail3bf242.ts.net/v1`) was missing entirely. The config from an earlier setup attempt had been lost. The STEWART_API_KEY env var still existed in the profile's `.env`, but no config was referencing it.

**Lesson:** A `key_env` in `.env` with no corresponding entry in `fallback_providers` or `providers:` = dead config. The key exists, nothing uses it.

### Step 2: Test raw endpoint reachability

```bash
# Try the known endpoint
curl -s --connect-timeout 5 https://<hostname>/v1/models
# Fallback: try the direct Tailscale IP
curl -s --connect-timeout 5 http://<tailscale-ip>:8001/v1/models
```

Expected outcomes:

| Result | Meaning | Next step |
|--------|---------|-----------|
| HTTP 200 + model list | Server reachable, auth passing | Check model name match between config and `/v1/models` response |
| `curl: (6)` DNS fail | Hostname doesn't resolve | Check tailnet membership (Step 3) |
| `curl: (7)` conn refused | Server not running or wrong port | Check the host machine; verify llama.cpp/Ollama/vLLM is started |
| `curl: (28)` timeout | Firewall or network block | Check ports and firewall rules |

**What happened here:** Both the MagicDNS hostname (`stewart.tail3bf242.ts.net`) and the direct Tailscale IP (`100.121.222.33:8001`) returned `curl: (28)` — the target machine didn't respond at all.

### Step 3: Check tailnet membership

```bash
tailscale status
```

This shows every device currently connected to your tailnet, with IPs and online/offline status.

- If the target machine is **not listed** at all → it has never joined the tailnet
- If the target machine is listed as **offline** → it was once connected but is currently offline
- If the target machine is listed with a **different IP** than expected → the IP address changed

**What happened here:** `tailscale status` showed only the Mac and iPhone. The Windows PC was not listed at all — it had never been connected to Tailscale.

### Step 4: Check your own Tailscale IP (confirm active)

```bash
tailscale ip -4
```

If this returns a `100.x.x.x` address, Tailscale is active on the diagnostic machine. If it fails (`failed to connect to local tailscaled`), Tailscale may be installed via the Mac App Store (IPNExtension mode) — the tunnel is active but the CLI can't talk to the daemon. See `references/tailscale-connectivity-pitfalls.md` for the IPNExtension workaround.

### Step 5: Confirm the host machine details

Ask the user to check on the target machine:

```
1. Is Tailscale installed? (tailscale status)
2. Is the model server running? (llama-server, ollama serve, etc.)
3. What port is it listening on? (default: 8001 for llama.cpp, 11434 for Ollama)
4. What's its Tailscale IP? (tailscale ip -4)
5. Does the server expose the model? (curl localhost:<port>/v1/models)
```

### Step 6: Re-establish the provider config

Once the target machine is online and reachable, add it as a provider entry:

```yaml
# Option A: Named provider in providers: block (switchable, visible in /model)
providers:
  windows-llm:
    name: Windows PC LLM
    base_url: http://100.121.222.33:8001/v1
    key_env: STEWART_API_KEY
    model: darwin-36b-opus-apex-i-mini
    discover_models: true

# Option B: Fallback provider (auto-tried when primary fails)
fallback_providers:
  - provider: custom
    model: darwin-36b-opus-apex-i-mini
    base_url: http://100.121.222.33:8001/v1
    api_key: $STEWART_API_KEY
```

**Important:** Use the **direct Tailscale IP** (`100.x.x.x`) not the MagicDNS hostname (`*.ts.net`) when you want maximum reliability. MagicDNS depends on the tailnet DNS resolver being reachable; the direct IP works even when DNS is degraded. Use MagicDNS only when the IP is dynamic or you want human-readable names.

## Root Cause Summary

| Symptom | Most likely cause |
|---------|------------------|
| `curl: (6)` on `*.ts.net` | Not on same tailnet, or share not accepted |
| `curl: (6)` on `100.x.x.x` | IP doesn't belong to a device on your tailnet |
| `curl: (7)` on known-good IP | Server process not running on host |
| `curl: (28)` on known-good IP | Host is offline or firewall blocking port |
| HTTP 200 but model name mismatch | Config says one name, server exposes another |
| HTTP 401/403 | API key expired or wrong |
| Config exists but model never used | Entry was in old config that got overwritten |
