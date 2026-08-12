# Verify Leaf Subagent Output (Orchestrator-as-Verifier)

Use when you (the top-level orchestrator) dispatch fresh leaf subagents per task
and will verify their output yourself with direct tool calls, instead of spawning
separate reviewer subagents. Independence comes from context separation from the
*implementer*, not from being a different subagent — your read of `git log` /
`tsc` / `read_file` is genuine independent review.

## Verify-then-advance checklist (per task)

1. **Re-run the subagent's green command yourself.** Do not accept "built fine /
   2 passing / tsc clean" without your own tool-run.
   - Type-check: `npx tsc --noEmit -p tsconfig.app.json` (or project's app config).
   - Test: `npx hardhat test`, `pytest`, etc. — read the tail for PASS count.
   - Build: `npm run build` — note the `terminal` guard false-fires on `vite`/
     `build`/`dev`/`serve` substrings (even inside `echo`); run it as
     `background=true, notify_on_complete=true` with `> /tmp/x.log 2>&1`, then
     `process(action="wait")` and read the log for `EXIT=` + the build summary.
2. **Read back the actual files.** `read_file` head + `search_files` for required
   tokens (palette hexes, hook line, ABI `export const ... = [` wrapper, mood
   union, etc.). Confirm verbatim-match requirements from the plan are met.
3. **Diff against hard constraints.** Cloned scaffolds (hardhat-monad, create-vite)
   routinely violate project rules — check: no mainnet network in config,
   `.gitignore` covers `.env` + `contracts/.env` BEFORE any key exists,
   `contracts/.git` removed, no keys/`.env` tracked (`git ls-files | grep -i env`).
4. **Confirm commit span, not just HEAD.** After a parallel batch, use
   `git log -N` and check every expected commit message is present; `git log -1`
   right after a batch is unreliable (another subagent's commit may be HEAD).
   Confirm timestamps are post-window and non-clustered (judging-agent rule).
5. **Only then mark complete and proceed** to the next task.

## Two real catches from a build session

- **False root-cause:** A subagent claimed `~/.npmrc` had `omit[]=dev` active and
  that it had to run `npm install --include=dev`. The npmrc was fully commented
  out; dev deps were already present. The end-state was fine but the *explanation*
  was wrong. Any subagent-stated *cause* (missing binary, config quirk, env fix)
  must be independently confirmed before recording into memory/skills — else you
  poison future sessions with a false durable fact.
- **Scaffold-injected mainnet:** `git clone hardhat-monad contracts/` pulled in a
  `monadMainnet` (chainId 143) network, violating the plan's "no mainnet network
  in config" hard rule. Caught in review, fixed by removing the network block from
  `hardhat.config.ts` and re-compiling. Always diff cloned configs against the
  plan's hard constraints.

## When to still spawn reviewer subagents

Reserve spawned reviewers for cases the orchestrator cannot verify directly:
subjective UX/visual review, deep security audit needing its own sandbox, or
large integration review where context cost of doing it inline is too high.
