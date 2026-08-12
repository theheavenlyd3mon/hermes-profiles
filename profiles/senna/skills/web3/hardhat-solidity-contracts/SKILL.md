---
name: hardhat-solidity-contracts
description: Build, test (TDD red→green), and deploy Solidity smart contracts with Hardhat 2 on Ethereum/Monad/L2 testnets. Covers the hardhat-toolbox version trap, the ts-node/TypeScript-7 crash, devDependency-omitting installs, and secret-safe config (never write private keys to .env).
trigger: When setting up a Hardhat project, writing Solidity (.sol), running `npx hardhat test`, doing TDD red→green for contracts, extracting an ABI to TypeScript, or deploying to Monad testnet/mainnet.
---

# Hardhat + Solidity contract development

Use this for any Hardhat 2 (NOT Hardhat 3) Solidity workflow: scaffold, TDD, compile, deploy.

## Environment pitfall: npm silently omits devDependencies
In some shells `npm config get omit` returns `dev`, so `npm install` installs only 2 packages and `hardhat` is MISSING. ALWAYS install with:
```
npm install --include=dev
```
(See `frontend-scaffold` skill — it documents this same trap for app scaffolding.)

## Pitfall 1: hardhat-toolbox version tag
- `@nomicfoundation/hardhat-toolbox@latest` is **v7**, which only works with Hardhat 3. With Hardhat 2 it prints a warning and then a confusing ts-node error.
- For Hardhat 2, install the `hh2` tag: `"@nomicfoundation/hardhat-toolbox": "hh2"` (resolves to ~6.1.2).
- Also decide ethers vs viem: the **`-viem`** variant (`hardhat-toolbox-viem`) does NOT provide ethers/chai, which most test files (`import { ethers } from "hardhat"`; `chai`) need. If your tests use ethers+chai, use the plain ethers toolbox and drop the viem packages.
- Clean installs: after changing toolbox deps, `rm -rf node_modules package-lock.json` then `npm install --include=dev` to avoid stale peer-dep resolution.

## Pitfall 2: ts-node crashes on TypeScript 7
Symptom:
```
TypeError: Cannot read properties of undefined (reading 'fileExists')
    at readConfig (.../ts-node/src/configuration.ts:161:25)
```
Cause: a transitive/mismatched TypeScript **7.x (preview)** breaks ts-node 10.9.2 when loading `hardhat.config.ts`.
Fix: pin TypeScript to 5.x:
```
npm install --save-dev "typescript@5.8.3"
```

## Pitfall 3: secret-safe hardhat.config (never write keys)
An empty `PRIVATE_KEY` crashes config load with `HH8: Invalid account ... private key too short`. Do NOT create a `.env` with real keys. Guard the accounts instead:
```ts
const PRIVATE_KEY = process.env.PRIVATE_KEY || "";
const ACCOUNTS = PRIVATE_KEY ? [PRIVATE_KEY] : [];
// networks.monadTestnet.accounts = ACCOUNTS;  (not [PRIVATE_KEY])
```
Keep `import "dotenv/config"` so a deployer can supply their own `.env` locally; `.gitignore` already ignores `.env`.

## TDD red→green flow (real checkpoint discipline)
1. Write `test/ContractName.test.ts` referencing a contract that does NOT exist yet.
2. Run `npx hardhat test` → expect RED: `HH700: Artifact for contract "X" not found`, `0 passing / 2 failing`. Capture this output as the red checkpoint.
3. Create `contracts/ContractName.sol`, then `npx hardhat test` → expect GREEN: `Compiled N Solidity file(s) successfully`, `2 passing`.
4. Commit red separately from green (separate commits, 3–4s apart, no push unless asked).

## Monad specifics
- Solidity `0.8.28`; set `evmVersion: "prague"` in `hardhat.config.ts` solidity settings (Monad supports it).
- Networks: `monadTestnet` (chainId 10143, `https://testnet-rpc.monad.xyz`), `monadMainnet` (chainId 143, `https://rpc.monad.xyz`).
- Sourcify/Etherscan blocks are fine; just keep the accounts guard above.

## Extract ABI to TypeScript (for a viem/frontend consumer)
After `npx hardhat compile`, the artifact JSON lives at
`artifacts/contracts/ContractName.sol/ContractName.json`. Emit a typed const:
```bash
node -e "const a=require('./artifacts/contracts/CommitmentLedger.sol/CommitmentLedger.json').abi; const fs=require('fs'); fs.writeFileSync('../src/lib/abi.ts','export const CommitmentLedgerAbi = '+JSON.stringify(a,null,2)+' as const;\n');"
```
The file should start `export const CommitmentLedgerAbi = [` and end `] as const;`. A valid file → `npx hardhat compile` reports "Nothing to compile" (artifact unchanged).

See `references/pitfalls.md` for exact error transcripts + the verification commands used in the reference session.
