# Hardhat pitfalls — exact transcripts & verification (reference session)

From a session building `CommitmentLedger.sol` on Monad via flattened `hardhat-monad` in `contracts/`.

## 1. Dev-deps omitted despite "no omit" note
```
$ npm config get omit
dev
$ npm install
added 1 package, and audited 2 packages in 2s
$ test -d node_modules/hardhat && echo OK || echo MISSING
MISSING
```
Fix: `npm install --include=dev`. After toolbox change: `rm -rf node_modules package-lock.json && npm install --include=dev`.

## 2. Toolbox v7 vs Hardhat 2
Plain `npx hardhat test` after installing `@latest`:
```
Warning: You installed the `latest` version of @nomicfoundation/hardhat-toolbox,
which does not work with Hardhat 2 nor 3.
```
Install `hh2` tag. If you see ERESOLVE on `hardhat-gas-reporter@^2.3.0` peer conflict after adding viem packages, remove `hardhat-toolbox-viem` and `hardhat-ignition-viem` from package.json (use ethers toolbox), then clean reinstall.

## 3. ts-node / TypeScript 7 crash
```
An unexpected error occurred:
TypeError: Cannot read properties of undefined (reading 'fileExists')
    at readConfig (.../ts-node/src/configuration.ts:161:25)
```
Root cause: `typescript@7.0.2` (preview) shipped transitively. Pin:
`npm install --save-dev "typescript@5.8.3"`. Then `npx hardhat test` proceeds past config load.

## 4. Empty PRIVATE_KEY -> HH8
```
Error HH8: There's one or more errors in your config file:
  * Invalid account: #0 for network: monadTestnet - private key too short, expected 32 bytes
```
Fix: `const ACCOUNTS = PRIVATE_KEY ? [PRIVATE_KEY] : [];` and use `ACCOUNTS` in both networks. Never write a `.env` with keys.

## 5. RED checkpoint (contract not yet written)
```
CommitmentLedger
    1) increments streak only on a new day
    2) rejects empty message
  0 passing (2s)
  2 failing
  HardhatError: HH700: Artifact for contract "CommitmentLedger" not found.
```

## 6. GREEN checkpoint (after CommitmentLedger.sol)
```
Compiled 1 Solidity file successfully (evm target: prague).
  CommitmentLedger
    ✔ increments streak only on a new day (446ms)
    ✔ rejects empty message
  2 passing (466ms)
```

## 7. ABI extraction verification
`artifacts/contracts/CommitmentLedger.sol/CommitmentLedger.json` -> `../src/lib/abi.ts`.
Valid file: starts `export const CommitmentLedgerAbi = [`, ends `] as const;`, 109 lines.
Recompile to confirm: `npx hardhat compile` -> `Nothing to compile / No need to generate any newer typings.`

## Commit discipline used
Separate commits, 3–4s apart, local only:
- `chore: add hardhat-monad (flattened, no nested git)`
- `test: add failing CommitmentLedger test (TDD red)`
- `feat: CommitmentLedger with real-day streak + empty guard`
- `feat: commit contract ABI for frontend`
Verify `test -d contracts/.git` is false after flatten (no nested git).
