# Kimi for Coding — model slugs, context tiers, quota (as of 2026-07)

Source: https://www.kimi.com/code/docs/en/kimi-code/models + platform.kimi.ai K3 quickstart.

## Model IDs (endpoint: https://api.kimi.com/coding)

| Model ID | Context | Availability | Notes |
|---|---|---|---|
| `k3` | up to 1M | Moderato+ (256K); **Allegretto+ unlocks 1M** | Flagship, 2.8T params. Thinking effort low/high/max. |
| `k3-256k` | fixed 256K | Moderato+ | Same results within 256K; ~half the quota of k3@1M. |
| `kimi-for-coding` | 256K | all members | Routine completion/dev tasks. |
| `kimi-for-coding-highspeed` | 256K | Allegretto+ | ~5-6x faster output. |

## Failure signature

Hermes resolves `kimi-k3` @ api.kimi.com/coding → 1M context via
`_endpoint_scoped_context_length` (agent/model_metadata.py) without knowing
the plan tier. On a Moderato plan the API enforces 262144 and rejects the
first oversized request: "Your request exceeded model token limit: 262144".
Hermes then falls back to the configured fallback provider mid-session.

## Fixes

- Moderato plan: `hermes config set model.context_length 262144` so LCM
  compresses before the API rejects — or switch slug to `k3-256k`.
- Allegretto+ plan: prefer slug `k3`; the `kimi-k3` alias has been observed
  defaulting to the 256K limit server-side.
- Third-party tools may default to a smaller window — set the context-window
  field to 1048576 explicitly where supported.

## Quirk

`k3` (1M) consumes ~2x quota vs `k3-256k`. temperature/top_p/n/penalties are
fixed server-side on K3 — omit them from requests.
