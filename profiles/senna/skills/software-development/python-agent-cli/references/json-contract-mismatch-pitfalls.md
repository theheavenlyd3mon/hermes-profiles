# JSON Contract Mismatch Pitfalls

When frontend and backend are built in parallel, field name mismatches and port drift
cause integration failures that unit tests cannot catch (they test one side only).

## Common Mismatches Observed

### Port Drift
Frontend Vite proxy targets `localhost:7822`, backend defaults to `8000`.
Fix: hard-code the port in both places and document it in a shared contract file.

### Field Name Mismatches
Frontend expects `{prompt}`, backend accepts `{task}`.
Frontend expects `{id}` in POST response, backend returns `{run_id}`.
Fix: Generate types from a shared schema, or run frontend `npm run build` against
the actual `/api/run` endpoint and assert the response parses.

## Prevention Checklist

1. Define the JSON contract in a shared `types.ts` (frontend) and `contract.py` (backend).
2. Verify contract at build time: `scripts/verify_contract.py` fetches a sample response.
3. Document port and endpoints in the skill's README, not just code comments.
4. Test integration before claiming "done" — both sides must agree on the shape.

The frontend's `types.ts` is the source of truth for the RunState contract:
```ts
interface RunState {
  id: string;
  prompt: string;   // NOT 'task'
  status: 'idle'|'plan'|'run'|'build'|'done'|'error';
  bridge: string;
  memory: boolean;
  provider: string;
  model: string;
  buildAttempt: number;
  buildMax: number;
  events: HarnessEvent[];
}
```