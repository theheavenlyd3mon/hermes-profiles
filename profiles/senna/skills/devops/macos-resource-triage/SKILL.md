---
name: macos-resource-triage
description: >
  Use when diagnosing macOS CPU/GPU usage or a hot, slow Mac.
---

# macOS Resource Triage

## Trigger
- "what's using our CPU", "why is the Mac slow/hot", "check system processes"
- "do we have a GPU", hardware capability questions
- Performance review before deciding what to kill/stop

## Golden rule: don't trust a single `ps` snapshot
On a busy Mac, instantaneous `ps -o pcpu` **races**: short-lived processes
(Spotlight bursts, transient spawns, restarting gateways) appear and vanish
between samples. One sample can name a different top-3 than the next. Load
average (`uptime`) is the ground truth for oversubscription; the process list
must be read with a stable delta sample.

## Steps

### 1. Load + aggregate first
```bash
uptime
ps -Ao pcpu | awk '{s+=$1} END {printf "total %CPU: %.0f (%.1f cores of 12)\n", s, s/100}'
```
Load 50+ / 20 / 13 on a 12-thread i7-9750H = ~4x run-queue oversubscription.
A `ps` aggregate of 2% while load is 50 means the churn is between samples —
see step 2, don't conclude "nothing is running".

### 2. Stable per-process CPU (delta sample)
```bash
top -l 2 -n 15 -o cpu -stats pid,command,cpu 2>/dev/null | awk '/^PID/{c++} c==2' | head -16
```
- `-l 2` = two samples; the **second** is delta-based and stable (first is cumulative since boot).
- Add `-stats pid,command,cpu,time` for CPU-seconds (TIME) to distinguish a
  hot process from a long-lived one.
- For more stability under heavy churn use `-l 3` and take the last sample.

### 3. Family aggregates (app + all helpers)
```bash
ps -Ao pcpu,comm | grep -i discord | awk '{s+=$1} END {printf "discord total: %.0f%% CPU\n", s}'
```
Discord is typically multiple processes (renderer, GPU helper, VTDecoderXPCService
for video decode) — the family sum is what matters, not the biggest single PID.

### 4. Identify suspicious/known-culprit daemons
- `coreaudiod` sustained 50%+ CPU with no audio clients = known spin bug.
  Fix: `sudo killall coreaudiod` (respawns automatically). Elapsed time of
  days (`ps -o etime -p <pid>`) confirms it's chronic, not transient.
- `kernel_task` high %CPU on Intel Macs = thermal/IO pressure signal, not literal compute.
- `WindowServer` 50%+ is usually a symptom of heavy rendering (video calls,
  GPU switching), not a standalone problem.
- `VTDecoderXPCService` / `VTEncoderXPCService` = video decode/encode in progress
  (stream, call, screenshare) — trace back to the app using it.

### 5. Fleet footprint (Hermes multi-profile hosts)
```bash
for p in $(pgrep -f 'hermes_cli.main'); do ps -o pcpu= -p $p; done | awk '{s+=$1} END {printf "fleet CPU: %.0f%%\n", s}'
ps -Ao rss,args | grep 'hermes_cli.main' | grep -v grep | awk '{s+=$1} END {printf "fleet RAM: %.1f GB\n", s/1048576}'
pgrep -f 'hermes_cli.main' | wc -l
```
- Full inventory: `pgrep -fl 'hermes_cli.main'` (shows every profile gateway).
- Churning PIDs between samples = gateways restarting/cycling — worth
  flagging as a finding, not just noise.

### 6. GPU / hardware identification
```bash
system_profiler SPDisplaysDataType
sysctl -n machdep.cpu.brand_string hw.model hw.ncpu
```
- `hw.model` decodes the machine: MacBookPro15,1 = 2019 15" MBP (i7-9750H, 12 threads).
- Dual-GPU Macs show both: Intel UHD 630 (iGPU, dynamic VRAM) + AMD Radeon
  Pro 555X (dGPU, 4 GB) with Automatic Graphics Switching + gMux.
- Metal support line matters for "can it do X" answers: Metal 3 = modern
  graphics OK; **no CUDA** = no NVIDIA compute. A 2019 Polaris dGPU is fine
  for display/video, not a compute workhorse — say so plainly.

## Report shape
Table of top consumers (PID | %CPU | what it is | why it's high), one line per
finding, then cheapest fixes first (kill daemon with auto-respawn, close the
video-streaming app, pause idle services). Offer to execute; don't kill
user-facing apps unprompted.

## Pitfalls
- BSD `ps` ≠ GNU `ps`: use `ps -Ao pid,pcpu,comm` (macOS), not `ps aux --no-headers`.
- `lsof -c coreaudiod` may return empty even when the daemon is hot — no
  clients listed doesn't mean it's idle; trust the %CPU + etime.
- A transient 15% process (Calculator, secinitd, rtk) in one sample is churn,
  not a finding. Cross-check two samples before naming it.
- Don't sum `ps` %CPU into "cores used" on a churning system — the sum can
  read 2% while load is 50. Use `uptime` for the real oversubscription number.
