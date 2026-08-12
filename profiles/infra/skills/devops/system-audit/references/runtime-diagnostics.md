# macOS Runtime Diagnostics

Quick reference for "my Mac is hot / slow / what's running" investigations.
Complementary to the update-focused main audit workflow.

## CPU Hog Identification

```bash
# Top 20 processes by CPU (macOS BSD ps syntax)
ps -eo pid,pcpu,pmem,rss,etime,args -r | head -25

# System overview: load averages, CPU breakdown, memory
top -l 1 -n 15 -o cpu -s 0 | head -20

# Find a specific runaway process
ps -o pid,pcpu,pmem,etime,args -p <PID>
```

**Key signals:**
- `%CPU > 100` = multi-core usage, often a stuck daemon
- High accumulated TIME but low current %CPU = past spike, now idle
- Low accumulated TIME but high current %CPU = actively burning right now

## Memory Pressure

```bash
# Full memory report
memory_pressure

# Quick swap check
sysctl vm.swapusage
```

**Key signals:**
- "System-wide memory free percentage" < 50% = under pressure
- Swap used > 500MB = heavy paging, will slow everything down
- `Pages purged` count high = macOS is aggressively reclaiming memory

## Process Tree Tracing

```bash
# Find parent-child relationships (who spawned whom)
ps -eo pid,ppid,pcpu,etime,args | grep <process-name>

# Find all processes matching a pattern
pgrep -fl <pattern>

# What files/sockets a process has open
lsof -p <PID> | grep -i "pipe\|socket\|tcp" | head -10
```

## Daemon Management

```bash
# Check for launchd auto-start plists
ls ~/Library/LaunchAgents/*<name>* 2>/dev/null
ls /Library/LaunchDaemons/*<name>* 2>/dev/null

# Kill a runaway daemon
pkill -f "<process-name>"

# Kill and prevent respawn
launchctl unload ~/Library/LaunchAgents/<plist-name>.plist
```

## Quick Health Snapshot

```bash
echo "=== CPU ===" ; top -l 1 -s 0 | grep -E "CPU usage|Load Avg"
echo "=== MEMORY ===" ; top -l 1 -s 0 | grep "PhysMem"
echo "=== SWAP ===" ; sysctl vm.swapusage
echo "=== TOP 5 CPU ===" ; ps -eo pid,pcpu,args -r | head -6
```

## Pitfalls

- **macOS `ps` uses BSD syntax** — `ps aux` works but `ps aux --sort=-%cpu` does NOT.
  Use `ps -eo pid,pcpu,args -r` (the `-r` flag sorts by CPU).
- **`top` output differs from Linux** — `-l 1` for one sample, `-o cpu` for sort field,
  `-s 0` for no delay. Linux uses `top -bn1`.
- **Accumulated CPU time is misleading** — a process running for 11 days with 16 minutes
  of CPU time is fine. A process running for 6 seconds with 110% CPU is a problem.
- **`pgrep` on macOS doesn't support `-a` (show args)** — use `pgrep -fl` for full
  command line, or `ps -o args -p $(pgrep -f pattern)`.
