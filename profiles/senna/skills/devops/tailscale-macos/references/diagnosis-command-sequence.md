# Tailscale macOS diagnosis — command sequence & findings

Reproduction recipe for the dual-install "daemon won't connect" failure. Commands
run on the user's Mac (macOS 15.7.7, host `<user>`).

## Sequence actually run
```
# 1. Is it installed / what's the error?
which tailscale                 # -> /usr/local/bin/tailscale
tailscale status                # -> failed to connect to local Tailscale service; is Tailscale running?

# 2. What's installed?
ls -d "/Applications/Tailscale.app"   # -> present (native app)
brew list tailscale                  # -> /usr/local/Cellar/tailscale/1.96.4 (Homebrew ALSO present)
launchctl list | grep -i tailscale   # -> empty (no brew daemon registered)

# 3. Start the app
open -a Tailscale
sleep 4
tailscale status   # -> failed to connect to local tailscaled (IPNExtension, pid ...) dial unix /var/run/tailscaled.socket: no such file or directory

# 4. The two installs fight: Homebrew CLI -> global socket; app -> network extension
find "/Applications/Tailscale.app" -name tailscale   # -> none (app has no CLI)
ls /var/run/tailscaled.socket                        # -> absent (no global socket)

# 5. Extension approval gate
systemextensionsctl list
# -> only ch.protonvpn.mac.* entries; Tailscale NOT in activated list  <-- ROOT BLOCKER

# 6. State checks
ifconfig | grep -i tailscale   # -> no tailscale interface
ifconfig | grep -A1 "inet 100" # -> no 100.x address
pgrep -fl IPNExtension         # -> (later) NOT running
```

## Root cause
Two installs: native `Tailscale.app` (network extension daemon) AND Homebrew
(`/usr/local/bin/tailscale` CLI). The Homebrew CLI is hardcoded to
`/var/run/tailscaled.socket`, which the native app never creates — so every CLI
call dies even when the app's `IPNExtension` is alive. Separately, Tailscale's
**system network extension was never approved** in System Settings, which is a
GUI-only gate no agent can click.

## Resolution handed to user
1. Choose one install; neutralize the other (recommended: keep native app).
2. User approves the network extension (System Settings → General → Login Items &
   Extensions → Network Extensions) and signs in to the tailnet.
3. Verify with `tailscale status` / `tailscale ip` / `ifconfig`.

## Gotcha captured
`security find-generic-password` returned a `hermes` usage dump — `security`
was shadowed by an alias/function. Use `/usr/bin/security` by absolute path.
